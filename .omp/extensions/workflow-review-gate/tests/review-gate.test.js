const assert = require("node:assert/strict");
const { execFileSync } = require("node:child_process");
const { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } = require("node:fs");
const { tmpdir } = require("node:os");
const { join } = require("node:path");
const test = require("node:test");
const { pathToFileURL } = require("node:url");
const gate = require("../lib/review-gate-core.js");

const finalInput = {
  agent: "workflow-reviewer",
  prompt: "Active task: tasks/123\nReview profile: final\nReview the current patch.",
};

function git(cwd, ...args) {
  return execFileSync("git", args, { cwd, encoding: "utf8" });
}

function createRepository() {
  const cwd = mkdtempSync(join(tmpdir(), "workflow-review-gate-"));
  git(cwd, "init", "--quiet");
  git(cwd, "config", "user.name", "Workflow Review Gate Tests");
  git(cwd, "config", "user.email", "workflow-review-gate@example.invalid");
  writeFileSync(join(cwd, ".gitignore"), "*.ignored\n.omp/.runtime/\n", "utf8");
  writeFileSync(join(cwd, "tracked.txt"), "tracked\n", "utf8");
  git(cwd, "add", ".gitignore", "tracked.txt");
  git(cwd, "commit", "--quiet", "-m", "test fixture");
  return cwd;
}

async function loadExtensionHandlers() {
  const handlers = new Map();
  const extensionUrl = pathToFileURL(join(__dirname, "..", "index.ts")).href;
  const extension = (await import(extensionUrl)).default;
  extension({
    on(eventName, handler) {
      handlers.set(eventName, handler);
    },
  });
  return handlers;
}

function readOnlyLedgerEntry(cwd) {
  const ledgerPath = join(cwd, ".omp", ".runtime", "workflow-review-gate.json");
  const ledger = JSON.parse(readFileSync(ledgerPath, "utf8"));
  return Object.values(ledger.entries)[0];
}

async function dispatchReview(handlers, cwd, toolCallId) {
  return handlers.get("tool_call")({
    toolName: "task",
    toolCallId,
    input: finalInput,
  }, { cwd });
}

test("only an explicit final reviewer with an active task is gated", () => {
  assert.equal(gate.extractReviewRequest({ agent: "trellis-check", prompt: finalInput.prompt }), null);
  assert.equal(gate.extractReviewRequest({ agent: "workflow-reviewer", prompt: "Review it" }), null);
  assert.deepEqual(gate.extractReviewRequest(finalInput), {
    taskPath: "tasks/123", profile: "final", retry: false,
  });
});

test("OMP task batches use each nested task with shared active context", () => {
  assert.deepEqual(gate.extractReviewRequests({
    context: "Active task: tasks/123",
    tasks: [{ agent: "workflow-reviewer", task: "Review the patch." }],
  }), [{ taskPath: "tasks/123", profile: "final", retry: false }]);
});

test("same task, profile, and snapshot is allowed once then blocked", () => {
  const ledger = gate.newLedger();
  const request = gate.extractReviewRequest(finalInput);
  const first = gate.reserveReview(ledger, request, "first", "2026-08-20T00:00:00Z");
  assert.equal(first.allow, true);
  assert.match(gate.reserveReview(ledger, request, "first", "2026-08-20T00:00:01Z").reason, /already running/i);
  gate.finishReview(ledger, first.key, "complete", "2026-08-20T00:00:02Z");
  assert.match(gate.reserveReview(ledger, request, "first", "2026-08-20T00:00:03Z").reason, /already completed/i);
});

test("a changed snapshot requires a fresh review", () => {
  const ledger = gate.newLedger();
  const request = gate.extractReviewRequest(finalInput);
  const first = gate.reserveReview(ledger, request, "before-fix", "now");
  gate.finishReview(ledger, first.key, "complete", "later");
  assert.equal(gate.reserveReview(ledger, request, "after-fix", "later").allow, true);
});

test("invalid review requires the explicit single replacement slot", () => {
  const ledger = gate.newLedger();
  const request = gate.extractReviewRequest(finalInput);
  const first = gate.reserveReview(ledger, request, "snapshot", "now");
  gate.finishReview(ledger, first.key, "invalid", "later");

  assert.equal(gate.reserveReview(ledger, request, "snapshot", "later").allow, false);
  const retry = gate.extractReviewRequest({
    agent: "workflow-reviewer",
    prompt: "Active task: tasks/123\nReview retry: invalid",
  });
  const replacement = gate.reserveReview(ledger, retry, "snapshot", "later");
  assert.equal(replacement.allow, true);
  gate.finishReview(ledger, replacement.key, "failed", "later");
  assert.equal(gate.reserveReview(ledger, retry, "snapshot", "later").allow, false);
});

test("an invalid retry requires an earlier INVALID final review", () => {
  const ledger = gate.newLedger();
  const retry = gate.extractReviewRequest({
    agent: "workflow-reviewer",
    prompt: "Active task: tasks/123\nReview retry: invalid",
  });
  assert.equal(gate.reserveReview(ledger, retry, "snapshot", "now").allow, false);
  const final = gate.reserveReview(ledger, gate.extractReviewRequest(finalInput), "snapshot", "now");
  assert.equal(final.allow, true);
  assert.equal(gate.reserveReview(ledger, retry, "snapshot", "later").allow, false);
  gate.finishReview(ledger, final.key, "complete", "later");
  assert.equal(gate.reserveReview(ledger, retry, "snapshot", "later").allow, false);
});

test("specialist reviews are separate only when profile is explicit", () => {
  const security = gate.extractReviewRequest({
    agent: "workflow-reviewer",
    prompt: "Active task: tasks/123\nReview profile: security",
  });
  assert.equal(security.profile, "security");
  assert.equal(gate.classifyReviewResult({ isError: false, text: "REVIEW_STATUS: INVALID" }), "invalid");
});

test("successful task results complete the reserved review", async () => {
  const cwd = createRepository();
  try {
    const handlers = await loadExtensionHandlers();
    await dispatchReview(handlers, cwd, "review-1");

    await handlers.get("tool_result")({
      toolName: "task",
      toolCallId: "review-1",
      isError: false,
      content: [{ type: "text", text: "Review completed." }],
    }, { cwd });

    assert.equal(readOnlyLedgerEntry(cwd).status, "complete");
  } finally {
    rmSync(cwd, { recursive: true, force: true });
  }
});

test("ignored files do not change the review snapshot", async () => {
  const cwd = createRepository();
  try {
    const handlers = await loadExtensionHandlers();
    const ignoredPath = join(cwd, "scratch.ignored");
    writeFileSync(ignoredPath, "first\n", "utf8");
    await dispatchReview(handlers, cwd, "review-1");
    await handlers.get("tool_result")({
      toolName: "task",
      toolCallId: "review-1",
      isError: false,
      content: [{ type: "text", text: "Review completed." }],
    }, { cwd });

    writeFileSync(ignoredPath, "second\n", "utf8");
    const result = await dispatchReview(handlers, cwd, "review-2");

    assert.equal(result.block, true);
    assert.match(result.reason, /already completed/i);
  } finally {
    rmSync(cwd, { recursive: true, force: true });
  }
});

test("a nested repository produces a workspace snapshot", async () => {
  const cwd = mkdtempSync(join(tmpdir(), "workflow-review-gate-workspace-"));
  try {
    const repository = join(cwd, "codes", "service");
    mkdirSync(repository, { recursive: true });
    git(repository, "init", "--quiet");
    git(repository, "config", "user.name", "Workflow Review Gate Tests");
    git(repository, "config", "user.email", "workflow-review-gate@example.invalid");
    writeFileSync(join(repository, "tracked.txt"), "before\n", "utf8");
    git(repository, "add", "tracked.txt");
    git(repository, "commit", "--quiet", "-m", "test fixture");
    writeFileSync(join(repository, "tracked.txt"), "after\n", "utf8");

    const handlers = await loadExtensionHandlers();
    await dispatchReview(handlers, cwd, "review-1");

    assert.equal(readOnlyLedgerEntry(cwd).status, "running");
  } finally {
    rmSync(cwd, { recursive: true, force: true });
  }
});

test("an unborn nested repository produces a workspace snapshot", async () => {
  const cwd = mkdtempSync(join(tmpdir(), "workflow-review-gate-unborn-"));
  try {
    const repository = join(cwd, "codes", "new-service");
    mkdirSync(repository, { recursive: true });
    git(repository, "init", "--quiet");
    writeFileSync(join(repository, "untracked.txt"), "new repository\n", "utf8");

    const handlers = await loadExtensionHandlers();
    await dispatchReview(handlers, cwd, "review-1");

    assert.equal(readOnlyLedgerEntry(cwd).status, "running");
  } finally {
    rmSync(cwd, { recursive: true, force: true });
  }
});

test("a new commit changes an otherwise clean repository snapshot", async () => {
  const cwd = createRepository();
  try {
    const handlers = await loadExtensionHandlers();
    await dispatchReview(handlers, cwd, "review-1");
    await handlers.get("tool_result")({
      toolName: "task",
      toolCallId: "review-1",
      isError: false,
      content: [{ type: "text", text: "Review completed." }],
    }, { cwd });

    writeFileSync(join(cwd, "tracked.txt"), "committed change\n", "utf8");
    git(cwd, "add", "tracked.txt");
    git(cwd, "commit", "--quiet", "-m", "change snapshot");
    const result = await dispatchReview(handlers, cwd, "review-2");

    assert.equal(result, undefined);
    const ledger = JSON.parse(readFileSync(
      join(cwd, ".omp", ".runtime", "workflow-review-gate.json"),
      "utf8",
    ));
    assert.equal(Object.keys(ledger.entries).length, 2);
  } finally {
    rmSync(cwd, { recursive: true, force: true });
  }
});

test("staged content remains part of the snapshot when the worktree is reverted", async () => {
  const cwd = createRepository();
  try {
    const handlers = await loadExtensionHandlers();
    await dispatchReview(handlers, cwd, "review-1");
    await handlers.get("tool_result")({
      toolName: "task",
      toolCallId: "review-1",
      isError: false,
      content: [{ type: "text", text: "Review completed." }],
    }, { cwd });

    writeFileSync(join(cwd, "tracked.txt"), "staged change\n", "utf8");
    git(cwd, "add", "tracked.txt");
    writeFileSync(join(cwd, "tracked.txt"), "tracked\n", "utf8");
    const result = await dispatchReview(handlers, cwd, "review-2");

    assert.equal(result, undefined);
  } finally {
    rmSync(cwd, { recursive: true, force: true });
  }
});

test("ledger persistence failures block dispatch instead of throwing", async () => {
  const cwd = createRepository();
  try {
    writeFileSync(join(cwd, ".omp"), "not a directory\n", "utf8");
    const handlers = await loadExtensionHandlers();

    const result = await dispatchReview(handlers, cwd, "review-1");

    assert.equal(result.block, true);
    assert.match(result.reason, /could not persist/i);
  } finally {
    rmSync(cwd, { recursive: true, force: true });
  }
});
