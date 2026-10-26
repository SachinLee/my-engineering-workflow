# Quality Profiles

This is the single source of review budgets for every workflow entry point.
Risk adds relevant checks, never duplicate final reviewers or permission to skip
an available check that directly proves changed behavior.

## Simple Work Fast Path

This is the single source of eligibility for work without an OpenSpec change.
Use it only when **all** conditions hold: the request is clear, non-behavioral,
local and low-risk; it can finish in the same main session with no formal plan,
handoff or delegation; the user has not explicitly requested OpenSpec and is not
continuing a selected change; no stricter project record rule applies.
Examples: typo/copy/formatting fixes and local configuration or code cleanup
proven not to alter behavior. File count or the word "simple" is not sufficient.

Behavior includes workflow/agent instructions, not only executable code.
Behavior changes, bug fixes and refactors remain Standard or Critical. Security,
authentication/authorization, money, secrets, persistent data, migrations, public
contracts, dependency changes and destructive operations are never fast-path work.
Ambiguous scope must be resolved before eligibility is claimed. CLI errors or
failures do not qualify otherwise ineligible work for this path.

- Decide before discovery: an existing `openspec/` directory or unrelated changes
  do not require task matching, CLI access or initialization for eligible work.
- State the fast-path scope briefly, then execute in the main session without a
  create/reuse confirmation. Skip formal clarification/planning, dispatch and
  default independent review; do not create or update OpenSpec, `.workflow/`,
  `.trellis/`, or replacement task/status records, including retroactive artifacts.
- Inspect the relevant diff and run the smallest relevant checks required by the
  project. Report actual changes, commands/results, `NOT RUN` items and risks in
  the conversation. A failed/unavailable check is not a verified success or an
  independent `REVIEW_STATUS: CLEAN`; entering finish adds no checks or records.
- If behavior, risk, scope or formal handoff needs emerge, stop expanding the
  implementation. Preserve current diffs and executed checks, explain the change,
  then follow formal discovery and confirmation before creating/reusing a change.
  Do not auto-create a record or discard edits during escalation. A selected
  change continuation keeps its existing confirmation and review history.

## Lightweight

Use only for non-behavioral documentation, local configuration, or isolated
low-risk changes. Reclassify behavior changes as Standard or Critical.

- Keep work in the main session: no default independent reviewer or dispatch.
- Review scope and `git diff`, then run the smallest relevant runnable check.

## Standard

Use for normal features, bug fixes, and refactors.

- Implement in the main session and capture RED/GREEN evidence.
- Run targeted tests, relevant lint, typecheck, and build.
- Use exactly one independent `workflow-reviewer` in a fresh context, through
  `review-implementation`, for the complete relevant workspace. It reports both
  Standards and Spec, plus correctness, security, tests, and complexity.
- Do not run both by default: `review-implementation` is the review procedure,
  not another review added after `workflow-reviewer`.
- The reviewer is the default sole worker. Any implementation delegation needs
  explicit justification and user authorization; it never removes independent
  final review. Apply the Delivery Review Budget below across all entry points.
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
allow exactly one full review and at most one focused follow-up. Lightweight
keeps its main-session check without default independent review. Standard and
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
- Batch blocking repairs in the main session and rerun affected checks. Use
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
