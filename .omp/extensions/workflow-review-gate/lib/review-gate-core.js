"use strict";

const REVIEW_AGENTS = new Set(["workflow-reviewer", "code-reviewer", "reviewer"]);
const SPECIALIST_PROFILES = new Set(["security", "data-integrity"]);

function stringValue(value) {
  return typeof value === "string" ? value.trim() : "";
}

function extractReviewRequest(input) {
  const agent = [input.agent, input.agentName, input.subagent_type, input.name]
    .map(stringValue)
    .find(Boolean);
  if (!REVIEW_AGENTS.has(agent)) return null;

  const prompt = [input.task, input.prompt, input.description, input.context]
    .map(stringValue).filter(Boolean).join("\n");
  const taskMatch = prompt.match(/^Active task:\s*(\S+)/mi);
  if (!taskMatch) return null;

  const profileMatch = prompt.match(/^Review profile:\s*([\w-]+)/mi);
  const requestedProfile = profileMatch?.[1]?.toLowerCase();
  const retry = /^Review retry:\s*invalid\s*$/mi.test(prompt);
  const profile = retry ? "final-retry" : SPECIALIST_PROFILES.has(requestedProfile)
    ? requestedProfile
    : "final";
  return {
    taskPath: taskMatch[1],
    profile,
    retry,
  };
}

function extractReviewRequests(input) {
  const tasks = Array.isArray(input.tasks) ? input.tasks : [input];
  return tasks.map((task) => extractReviewRequest({ ...task, context: input.context })).filter(Boolean);
}

function makeKey(request, diffHash) {
  return `${request.taskPath}\u0000${request.profile}\u0000${diffHash}`;
}

function newLedger() {
  return { version: 1, entries: {} };
}

function normalizeLedger(candidate) {
  if (!candidate || candidate.version !== 1 || typeof candidate.entries !== "object") {
    return newLedger();
  }
  return candidate;
}

function reserveReview(ledger, request, diffHash, now) {
  const key = makeKey(request, diffHash);
  const existing = ledger.entries[key];
  if (request.retry) {
    const initialKey = makeKey({ ...request, profile: "final" }, diffHash);
    const initial = ledger.entries[initialKey];
    if (initial?.status !== "failed" || initial.result !== "invalid") {
      return { allow: false, key, reason: "An invalid-review retry requires an earlier INVALID final review for this task and snapshot." };
    }
    if (existing) {
      return { allow: false, key, reason: "The single invalid-review replacement slot for this task and snapshot was already used." };
    }
  }
  if (existing?.status === "running") {
    return { allow: false, key, reason: "A final review is already running for this task and snapshot." };
  }
  if (existing?.status === "complete") {
    return { allow: false, key, reason: "A final review already completed for this task and snapshot. Remediate first; a changed snapshot will be reviewed again." };
  }
  if (existing?.result === "invalid") {
    return { allow: false, key, reason: "The final review was INVALID. Its single replacement must include Review retry: invalid." };
  }
  if (existing?.status === "failed" && existing.attempts >= 2) {
    return { allow: false, key, reason: "The single allowed replacement review already failed for this task and snapshot. Escalate instead of dispatching another duplicate review." };
  }
  ledger.entries[key] = {
    taskPath: request.taskPath,
    profile: request.profile,
    diffHash,
    status: "running",
    attempts: (existing?.attempts || 0) + 1,
    updatedAt: now,
  };
  return { allow: true, key, retry: existing?.status === "failed" };
}

function finishReview(ledger, key, result, now) {
  const entry = ledger.entries[key];
  if (!entry) return false;
  entry.status = result === "invalid" || result === "failed" ? "failed" : "complete";
  entry.result = result;
  entry.updatedAt = now;
  return true;
}

function classifyReviewResult({ isError, text }) {
  if (isError) return "failed";
  if (/REVIEW_STATUS:\s*INVALID\b/i.test(text)) return "invalid";
  if (/\b(?:could not|cannot|unable to)\s+(?:confirm|find|determine).{0,80}\btask\b/i.test(text)) {
    return "invalid";
  }
  return "complete";
}

module.exports = {
  classifyReviewResult,
  extractReviewRequest,
  extractReviewRequests,
  finishReview,
  makeKey,
  newLedger,
  normalizeLedger,
  reserveReview,
};
