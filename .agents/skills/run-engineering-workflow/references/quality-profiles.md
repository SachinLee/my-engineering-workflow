# Quality Profiles

This file is the shared quality contract: it owns acceptance criteria, evidence
requirements, risk profiles and the review budget for every workflow entry point.
It does not own which agent runs, which model serves a role, or which tools a
client exposes — the host owns scheduling, model choice and tool availability.
Risk adds relevant checks, never duplicate final reviewers or permission to skip
an available check that directly proves changed behavior.

## Simple Work Fast Path

This is the single source of eligibility for work without an OpenSpec change.
Use it only when **all** conditions hold: the request is clear, local and
low-risk, and it does not need a formal continuation or an explicit durable
handoff; the user has not explicitly requested OpenSpec and is not continuing a
selected change; no stricter project record rule applies.

Two work shapes qualify:

- Non-behavioral edits: typo/copy/formatting fixes, local configuration, or code
  cleanup proven not to alter behavior.
- A small behavior fix confined to a bounded seam, where the change is clearly
  scoped, the affected caller graph is visible, and a regression check proves the
  fixed behavior. Keep the fix and its regression test in the same change.

File count is never sufficient, and it never disqualifies either: a one-line
change can be high risk and a five-file change can be trivial. Behavior includes
workflow/agent instructions, not only executable code. A behavior fix that needs
a migration, a public contract change, or a design decision is formal work.

Escalate to the formal branch — regardless of how small the diff is — when the
work touches authentication/authorization, money, secrets, persistent data,
migrations, public contracts, dependencies or destructive operations, or when
risk is unknown or cannot be bounded. Behavior changes that fit none of the two
shapes above, and all refactors, remain Standard or Critical. Ambiguous scope must
be resolved before eligibility is claimed. CLI errors or failures do not qualify
otherwise ineligible work for this path.

Fast-path work needs a meaningful regression check for any behavior change, and
no formal record: report the check in the conversation. Absence of a record is not
absence of evidence.

- Decide before discovery: an existing `openspec/` directory or unrelated changes
  do not require task matching, CLI access or initialization for eligible work.
- State the fast-path scope briefly, then execute without a create/reuse
  confirmation, on the main session or the host's preferred bounded worker. Skip
  formal clarification/planning dispatch and default independent review; do not
  create or update OpenSpec, `.workflow/`, `.trellis/`, or replacement task/status
  records, including retroactive artifacts.
- Inspect the relevant diff and run the smallest relevant checks required by the
  project. Report actual changes, commands/results, `NOT RUN` items and risks in
  the conversation. A failed/unavailable check is not a verified success or an
  independent `REVIEW_STATUS: CLEAN`; entering finish adds no checks or records.
- If behavior, risk, scope or formal handoff needs emerge, stop expanding the
  implementation. Preserve current diffs and executed checks, explain the change,
  then follow formal discovery and confirmation before creating/reusing a change.
  Do not auto-create a record or discard edits during escalation. A selected
  change continuation keeps its existing confirmation and review history.

## Change Completeness

A lazy solution is lazy about code, never about the change. Before calling a change
complete, list every place it must reach: callers, tests, fixtures, config, and
exports. A shortcut that leaves a caller, fixture or exported signature broken is
unfinished work, not a smaller change.

- Keep validation and error paths when you move or merge code; deletion is not a
  simplification when it removes a trust boundary or failure handling.
- Non-trivial new logic (a branch, a loop, a parser, money or security handling)
  leaves one small test or assert-based self-check behind. Trivial edits need none.
- Ponytail supplies this lens; it never lowers correctness, security,
  accessibility or required verification.

## Lightweight

Use only for non-behavioral documentation, local configuration, or isolated
low-risk changes. Reclassify behavior changes as Standard or Critical.

- No mandatory formal planner, implementer, or independent reviewer. Keep
  scheduling host-native: the main session, or a bounded worker the host prefers.
- Review scope and `git diff`, then run the smallest relevant runnable check.

## Standard

Use for normal features, bug fixes, and refactors.

- Implement on the host's preferred writer — the main session only when the host
  has no specialist policy — and capture RED/GREEN evidence.
- Run targeted tests, relevant lint, typecheck, and build.
- Prefer Matt `tdd` for behavior changes and regression fixes. ECC
  `tdd-workflow` is an optional named alternative when it is installed and the
  user or project chooses it; it is never a default dependency, and its absence
  changes nothing here.
- Use exactly one independent `workflow-reviewer` in a fresh context, through
  `review-implementation`, for the complete relevant workspace. It reports both
  Standards and Spec, plus correctness, security, tests, and complexity.
- Do not run both by default: `review-implementation` is the review procedure,
  not another review added after `workflow-reviewer`.
- Inside an already approved scope, delegate with the host's native mechanism
  (subagent, task, or none) when fresh context or parallelism genuinely helps.
  The scope approval covers proportionate delegation; re-ask only when the scope,
  risk, or the reviewer's independence materially changes. Delegation never
  removes independent final review. One writer per bounded, non-overlapping slice;
  independent lanes may run in parallel only when they share no write files. Apply
  the Delivery Review Budget below across all entry points.
- If independent review is unavailable, record `UNVERIFIED` and hand off the
  gap; do not claim normal delivery completion or `REVIEW_STATUS: CLEAN`.

## Critical

Use for authentication, authorization, money, secrets, persistent data,
migrations, public contracts, or destructive operations.

- Run all Standard checks and use the same single final reviewer: no additional
  final reviewer by default. Add justified security/data checks, not a second
  generic or Matt native review stage.
- Add integration coverage, the full relevant suite, rollback verification,
  and affected critical-path E2E checks.
- Escalate uncertain implementation from `@task` to `@default` or `@slow` in OMP.

## Delivery Review Budget

The main router is the only review scheduler. For each approved delivery scope,
allow exactly one full review and at most one focused follow-up. Lightweight keeps
its focused check without default independent review. Standard and
Critical use `workflow-reviewer` only; do not append `code-reviewer`, a generic
reviewer, native Matt `code-review`, or nested review dispatch by default.

- Complete slices with targeted checks, not a full review per slice. Dispatch
  `Review mode: full` only after the delivery scope is complete and relevant
  repository checks pass; an independently shippable slice may be the approved scope.
- A blocking finding needs a violated AC, project rule, or correctness/security/data
  invariant, plus a concrete failure scenario and impact. Severity alone is not
  the gate. Optional simplification and preference suggestions are non-blocking;
  they do not trigger repairs or another review by default. `CLEAN` means no
  blocking findings with required coverage/evidence, not no suggestions at all.
- Batch blocking repairs on the implementer side and rerun affected checks. Use
  `Review mode: focused` for original blocking findings, the repair diff, and
  directly affected paths only, preferably in the original reviewer context.
  Do not solicit a new whole-scope optimization list during this follow-up.
- If blocking findings remain or new blocking defects appear after the follow-up,
  record `blocked` and let the user decide the next step. An exhausted budget
  never grants `CLEAN` or permission to skip required checks.
- Record the approved scope, full/focused rounds, reviewed inputs, reports,
  findings and repair checks in existing `artifacts/review.md` or
  `artifacts/verification.md`. On resume, reread that record; session changes and
  snapshot changes do not reset the budget. Missing round history is a gap to
  resolve, not permission to start again.
- Reuse a real same-change/same-material result. Appending the report or delivery
  evidence does not invalidate it unless substantive reviewed inputs change.
  Local blocking repairs use the focused follow-up, not another full review.
- Changed ACs, interfaces, security boundaries, implementation approach, or modules
  outside reviewed coverage require a user decision. Obtain explicit user approval
  for a new full review or restart with a newly approved delivery scope; preserve
  prior rounds and record the changed boundary. Never restart on snapshot change alone.
- Allow one controlled replacement for `INVALID` per approved scope, only when
  there is no valid report, after repairing the handoff with `Review retry: invalid`.
  It does not consume a valid full/focused round or reset their budget. A genuine
  findings report is not `INVALID`; another invalid result stops at `UNVERIFIED`.
- Finish consumes valid evidence; gaps return to the main router for affected
  checks or a budgeted review. Merely entering finish never adds verification or review.

## Explicit Native Review

Matt `code-review` is only a user-requested native mode, not the workflow default.
It needs a valid fixed point and nonempty committed diff to HEAD; it launches
its two reviewers only with explicit delegation authorization. It cannot certify
staged, unstaged, or untracked changes, and finish never automatically adds a
third review. If complete independent workspace coverage is still missing,
report the gap rather than silently treating committed review as sufficient.

Coverage percentages are diagnostic evidence, not a substitute for testing the
right behavior through a stable public seam.
