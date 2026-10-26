// @workflow-review-gate
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import {
  closeSync,
  lstatSync,
  mkdirSync,
  openSync,
  readlinkSync,
  readFileSync,
  readSync,
  readdirSync,
  renameSync,
  writeFileSync,
} from "node:fs";
import { join, relative } from "node:path";
import core from "./lib/review-gate-core.js";

const RUNTIME_RELATIVE_PATH = ".omp/.runtime/workflow-review-gate.json";
const MAX_REPOSITORY_SCAN_DEPTH = 4;
const MAX_GIT_OUTPUT_BYTES = 64 * 1024 * 1024;
const HASH_BUFFER_BYTES = 64 * 1024;
const SKIPPED_DIRECTORIES = new Set([
  ".agents",
  ".claude",
  ".codex",
  ".git",
  ".gradle",
  ".omp",
  ".pi",
  ".trellis",
  "build",
  "dist",
  "node_modules",
  "target",
]);

function git(cwd: string, args: string[]): Buffer {
  return execFileSync("git", args, {
    cwd,
    encoding: "buffer",
    maxBuffer: MAX_GIT_OUTPUT_BYTES,
    stdio: ["ignore", "pipe", "ignore"],
  });
}

function repositoryRoot(cwd: string): string | null {
  try {
    return git(cwd, ["rev-parse", "--show-toplevel"]).toString("utf8").trim() || null;
  } catch {
    return null;
  }
}

function findRepositoryRoots(cwd: string): string[] {
  const directRoot = repositoryRoot(cwd);
  if (directRoot) return [directRoot];

  const roots: string[] = [];
  function visit(directory: string, depth: number): void {
    let entries;
    try {
      entries = readdirSync(directory, { withFileTypes: true });
    } catch {
      return;
    }
    if (entries.some((entry) => entry.name === ".git")) {
      roots.push(directory);
      return;
    }
    if (depth >= MAX_REPOSITORY_SCAN_DEPTH) return;
    for (const entry of entries) {
      if (!entry.isDirectory() || SKIPPED_DIRECTORIES.has(entry.name)) continue;
      visit(join(directory, entry.name), depth + 1);
    }
  }
  visit(cwd, 0);
  return roots.sort((left, right) => left.localeCompare(right));
}

function updateFromFile(digest: ReturnType<typeof createHash>, path: string): void {
  const stats = lstatSync(path);
  if (stats.isSymbolicLink()) {
    digest.update("symlink\0");
    digest.update(readlinkSync(path));
    return;
  }
  if (!stats.isFile()) {
    digest.update(`special:${stats.mode}:${stats.size}`);
    return;
  }
  digest.update(`file:${stats.size}\0`);
  const descriptor = openSync(path, "r");
  const buffer = Buffer.allocUnsafe(HASH_BUFFER_BYTES);
  try {
    let bytesRead;
    while ((bytesRead = readSync(descriptor, buffer, 0, buffer.length, null)) > 0) {
      digest.update(buffer.subarray(0, bytesRead));
    }
  } finally {
    closeSync(descriptor);
  }
}

function headRevision(repository: string): string | null {
  try {
    return git(repository, ["rev-parse", "--verify", "HEAD"]).toString("utf8").trim() || null;
  } catch {
    return null;
  }
}

type SnapshotResult = {
  hash: string | null;
  failed: boolean;
};

function sourceSnapshot(cwd: string): SnapshotResult {
  try {
    const repositories = findRepositoryRoots(cwd);
    if (!repositories.length) return { hash: null, failed: false };
    const digest = createHash("sha256");
    for (const repository of repositories) {
      digest.update(relative(cwd, repository).replaceAll("\\", "/") || ".");
      digest.update("\0");
      const head = headRevision(repository);
      digest.update("HEAD\0");
      digest.update(head || "unborn");
      digest.update("\0");
      const cachedArgs = ["diff", "--binary", "--no-ext-diff", "--no-textconv", "--cached"];
      if (head) cachedArgs.push("HEAD");
      digest.update(git(repository, cachedArgs));
      digest.update("\0");
      digest.update(git(repository, ["diff", "--binary", "--no-ext-diff", "--no-textconv"]));
      digest.update("\0");
      const untracked = git(repository, ["ls-files", "--others", "--exclude-standard", "-z"])
        .toString("utf8").split("\0").filter(Boolean)
        .filter((relativePath) => !relativePath.startsWith(".omp/.runtime/"))
        .sort();
      for (const relativePath of untracked) {
        digest.update(relativePath);
        digest.update("\0");
        updateFromFile(digest, join(repository, relativePath));
        digest.update("\0");
      }
    }
    return { hash: digest.digest("hex"), failed: false };
  } catch {
    return { hash: null, failed: true };
  }
}

function ledgerPath(cwd: string): string {
  return join(cwd, RUNTIME_RELATIVE_PATH);
}

function readLedger(cwd: string): ReturnType<typeof core.normalizeLedger> {
  const path = ledgerPath(cwd);
  try {
    return core.normalizeLedger(JSON.parse(readFileSync(path, "utf8")));
  } catch {
    return core.newLedger();
  }
}

function saveLedger(cwd: string, ledger: unknown): void {
  const path = ledgerPath(cwd);
  const directory = join(cwd, ".omp", ".runtime");
  mkdirSync(directory, { recursive: true });
  const temporary = `${path}.${process.pid}.tmp`;
  writeFileSync(temporary, `${JSON.stringify(ledger, null, 2)}\n`, "utf8");
  renameSync(temporary, path);
}

function trySaveLedger(cwd: string, ledger: unknown): boolean {
  try {
    saveLedger(cwd, ledger);
    return true;
  } catch {
    return false;
  }
}

function textFromContent(content: unknown): string {
  if (!Array.isArray(content)) return "";
  return content
    .filter((part) => part && typeof part === "object" && part.type === "text")
    .map((part) => typeof part.text === "string" ? part.text : "")
    .join("\n");
}

export default function (pi: any) {
  const pending = new Map<string, string[]>();

  pi.on("tool_call", (event: any, ctx: any) => {
    if (event.toolName !== "task") return;
    const requests = core.extractReviewRequests(event.input || {});
    if (!requests.length) return;
    const snapshot = sourceSnapshot(ctx.cwd);
    if (snapshot.failed) {
      return {
        block: true,
        reason: "[workflow-review-gate] The Git source snapshot could not be computed; review dispatch was blocked because duplicate-review state would be unreliable.",
      };
    }
    if (!snapshot.hash) return;
    const diffHash = snapshot.hash;

    const ledger = readLedger(ctx.cwd);
    const candidateLedger = JSON.parse(JSON.stringify(ledger));
    const reservations = requests.map((request: any) =>
      core.reserveReview(candidateLedger, request, diffHash, new Date().toISOString()));
    const denied = reservations.find((reservation: any) => !reservation.allow);
    if (denied) return { block: true, reason: `[workflow-review-gate] ${denied.reason}` };
    if (!trySaveLedger(ctx.cwd, candidateLedger)) {
      return {
        block: true,
        reason: "[workflow-review-gate] Review state could not persist; dispatch was blocked to avoid an untracked duplicate review.",
      };
    }
    pending.set(event.toolCallId, reservations.map((reservation: any) => reservation.key));
  });

  pi.on("tool_result", (event: any, ctx: any) => {
    if (event.toolName !== "task") return;
    const keys = pending.get(event.toolCallId);
    if (!keys) return;
    pending.delete(event.toolCallId);
    const ledger = JSON.parse(JSON.stringify(readLedger(ctx.cwd)));
    const result = core.classifyReviewResult({
      isError: Boolean(event.isError),
      text: textFromContent(event.content ?? event.result?.content),
    });
    for (const key of keys) {
      core.finishReview(ledger, key, result, new Date().toISOString());
    }
    trySaveLedger(ctx.cwd, ledger);
  });
}
