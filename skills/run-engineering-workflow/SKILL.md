---
name: run-engineering-workflow
description: Route software work through durable .workflow records, Matt-style clarification and design, TDD, independent review, and Ponytail complexity checks. Use when starting, resuming, planning, implementing, reviewing, or finishing a coding task that should remain traceable across AI sessions.
---

# Run Engineering Workflow

Use `.workflow/` as the workflow state and durable record. Use upstream skills
as methods inside that workflow; never create a competing task or plan system.

All state is plain files read and written with the platform's file tools. This
workflow has no CLI, no daemon, and no script interpreter dependency.

Task artifacts (`prd.md`, `design.md`, `implement.md`, `context.md`, `outcome.md`,
`journal.md`, and tickets) are written in the user's language — Chinese by default.
Keep code identifiers, paths, commands, log text, `STATUS` keys, and status tokens
(`PASS`, `NOT RUN`, `REVIEW_STATUS: CLEAN`) verbatim so they stay greppable.

## Bounded Context And Dispatch Contract

`.workflow/` remains the only durable source of task state. Treat the pointer
file as a task path plus phase, not as a dump of every active task or the full
conversation history. Load task artifacts on demand for the current phase and
assigned slice.

Never install or emulate a per-turn context injector (hook, extension, or
startup prompt block) for this workflow. Read state with file tools at phase
boundaries instead: a file read appends to the end of the outgoing request and
keeps the prompt-cache prefix intact, while anything injected before the
existing conversation history invalidates the cache for the whole session on
every following turn. A phase reminder must never cost more than one read.

Before any planner, implementation, check, or review dispatch, resolve exactly
one task path and pass a bounded handoff. The handoff must begin with:

```text
Active task: .workflow/tasks/<task-id>/
Assigned slice: <slice-or-stage>
```

That block is the boundary, not the whole payload. Paste the slice's 上下文包 from
`implement.md` into the dispatch: the AC text verbatim, the design decisions that
slice rests on, the located `file:line` conclusions with the symbol names, the
existing pattern the worker should copy, and the exact verification command. The
worker must not redo research the main session already finished. If something is
missing from the package, stop and complete it in `implement.md`; do not widen the
subagent's own investigation to compensate.

For planning, use `Assigned slice: planning / all accepted ACs`; for
implementation, use `Assigned slice: Slice N / AC-XXX`; for review, use
`Assigned slice: review / changed scope`.

For planning, implementation, and review handoffs also include `Phase:`,
`Read:`, `Must preserve:`, and the role-appropriate scope. Implementation
handoffs must include `May modify:` and `Verification:`. Review handoffs must
include `Review scope:` and `Evidence:`. Never ask a subagent to infer the task
by scanning `.workflow/tasks/`. A missing or unreadable task path is an invalid
dispatch; return the appropriate `*_STATUS: INVALID` result and stop.

Subagents receive task artifacts and file paths, not the parent conversation.
They must not change the session pointer, create a second handoff store, or
modify files outside the declared boundary. The main session owns task
selection, integration, remediation, and delivery claims.

Record dispatch metadata when the harness exposes it: `task_path`, `phase`,
`slice`, `role`, `requested_model`, `effective_model`, `fallback`, context
size, duration, and returned status. Do not record credentials, full prompts,
or full session history. If the harness cannot bind a pointer to a session,
write `by-session/main.md`, warn, and fall back to explicit paths; do not
silently widen the context or share one pointer between concurrent sessions.
Read [workflow-governance.md](references/workflow-governance.md) when deciding
artifact ownership, the record layout, source trust, or harness model routing.
Read [quality-profiles.md](references/quality-profiles.md) before selecting or
changing a risk profile.

## Start

1. Find the repository root and read `.workflow/CURRENT.md`. If it is absent,
   read this session's `.workflow/by-session/<key>.md`.
2. If neither exists but `.trellis/tasks/` does, use legacy read-only mode:
   the same artifact names (`prd.md`, `design.md`, `implement.md`, `outcome.md`)
   live under `.trellis/tasks/<task-id>/`, and `task.json` supplies `status`
   (`planning` or `in_progress`). Read them directly; never run a Trellis
   script. New or changed records are still written under `.workflow/`, and the
   session pointer stores the legacy path so the next resume is unambiguous.
3. If no record system exists, do not initialize one silently. Ask the user
   once whether this repository should keep durable task records. On yes,
   create `.workflow/tasks/<MM-DD-slug>/`; on no, follow the repository's
   existing workflow and state that cross-session task routing is unavailable.
4. Read the active task's `STATUS` file and its existing artifacts before
   deciding what to do next. A missing `STATUS` means `phase: planning`.
5. Do not start implementation while the pointer and the task directory
   disagree; resolve the disagreement first and record the resolution in
   `implement.md`.

## Assess Profile First

Before any routing or dispatch decision, explicitly assess the task's risk
profile by reading `prd.md` and the task scope:

1. **Is this critical?** Does the task touch authentication, authorization,
   money, secrets, persistent data, migrations, public contracts, destructive
   operations, or a cross-layer release boundary?
   - **Yes** → profile is `critical`
   - **No** → continue to step 2
2. **Is this lightweight?** Is this only documentation, local configuration, or
   an isolated low-risk change with no behavior modification?
   - **Yes** → profile is `lightweight`
   - **No** → profile is `standard` (normal features, bug fixes, refactors)
3. **State the assessed profile explicitly** before proceeding to routing.
   Example: "This is a **standard** task (bug fix in presentation layer, no
   auth or data changes). Implementation will stay in the main session unless a
   bounded worker is justified."

When uncertain, default to `standard` and escalate to `critical` only when clear
risk signals appear. Never default to `critical` for ordinary feature work.

## Route By State

After assessing the profile, route according to the task phase and the assessed
risk level. The profile controls dispatch, not just the checklist:

- `lightweight`: keep the work in the main session. Do not dispatch planner,
  implementer, checker, or reviewer. Run one focused check before delivery.
- `standard`: keep implementation in the main session by default. Use at most
  one implementation worker or one review worker when the boundary benefits
  from fresh context; never dispatch both implementation workers and duplicate
  reviewers.
- `critical`: use the full gated path when the change touches auth, secrets,
  money, persistent data, migrations, public contracts, destructive operations,
  or a cross-layer release boundary.

Phase routing:

- No active task: create one only with the consent rule in `Start`. Write
  `prd.md` first, then route as `planning`.
- Something is broken: route bug work through Matt `diagnosing-bugs` first — it must
  build a tight red command before any fix; then treat the result as `in_progress`
  work with a regression test.
- `planning` without a complete `prd.md`: invoke `clarify-requirements` in the
  main session. Only dispatch `workflow-planner` if the task is assessed as
  `critical` or the user explicitly requests planning delegation.
- `planning` with accepted requirements but no reviewed solution:
  - For `lightweight` or `standard`: invoke `plan-solution` in the main session.
  - For `critical`: in OMP, dispatch `workflow-planner` on `@plan`. In Pi, use
    the blocking `subagent` tool with `agentScope: "both"` when available;
    otherwise keep planning in the main session and disclose the lack of fresh
    context.
  - Only dispatch a planner if the task is assessed as `critical` or when the
    main session cannot resolve a material design uncertainty.
- `planning` with complete artifacts: update `STATUS` to `in_progress` only
  after the user approves the plan (or the repository's own gate says so).
  Planning completion is not permission to start implicitly. Record the
  approval in `implement.md`.
- `in_progress`: read `prd.md`, `context.md`, optional `design.md`, optional
  `implement.md`, and the listed spec and research files before editing. Use
  ECC `tdd-workflow` or Matt `tdd` for behavior changes and regression fixes.
  - For `lightweight` or `standard`: implement in the main session. Only use a
    single bounded worker if explicitly justified by the need for fresh
    context.
  - For `critical`: dispatch `workflow-implementer` on `@task` and require it
    to read `skill://tdd-workflow` (or `tdd`) before editing. Keep the handoff
    inside the declared file boundary.
- `in_progress` with a `tickets/` directory: recompute the frontier (every
  `blocked_by` ticket is `done`), advance exactly one ticket per writer, and set
  that ticket's `state: done` only after its verification command has executed
  evidence. Resuming after a session break means recomputing the frontier from the
  ticket files, never rereading the previous chat.
- Code changed: run the smallest check that proves the changed behavior.
  - For `lightweight`: run one focused check before delivery.
  - For `standard`: use either Matt `code-review` in the main session or one
    fresh-context `review-implementation` through `workflow-reviewer`, not both.
  - For `critical`: run the repository checks, then `code-review`, then
    `workflow-reviewer` from a fresh context. In OMP, run exactly one
    `workflow-reviewer` final review after checks finish, against a stable
    worktree snapshot; do not append duplicate reviewer tasks. In Pi, first use
    the blocking `subagent` reviewer when available.
  - The main session fixes findings and repeats affected checks; a changed
    snapshot requires a new review. The implementation model does not approve
    its own work.
- `review` clean: invoke `finish-with-evidence`. It writes `outcome.md`, sets
  `STATUS` to `awaiting-acceptance`, lists what you should verify, and stops there.
  The agent does not archive, does not move the task directory, does not delete a
  pointer, and does not set `phase: done`.
- `awaiting-acceptance` and you report a problem: move `STATUS` back to
  `in_progress`, fix, re-run the affected checks, and append a new verification
  round to `outcome.md`. Never rewrite an earlier round.
- `awaiting-acceptance` and you explicitly ask to archive: invoke `archive-task`.
  It re-checks the three acceptance conditions, performs the journal line, move,
  pointer, and `CURRENT.md` updates in order, and reports `ARCHIVE_STATUS:`.
  Without that explicit request, print the commands instead of running them.

### OMP Dispatch Limits

These limits enforce the profile-based routing rules:

- **Prefer the main session for `lightweight` and `standard` work.** Only
  dispatch when the assessed profile is `critical` or when fresh context is
  explicitly justified for a bounded slice.
- Allow at most one live writer and one review/check worker for a task.
- Treat a worker as making progress only when it edits a declared file, runs a
  relevant check, reports a concrete result, or states a reproducible blocker.
- After 10 minutes without progress, request one status update. After 15
  minutes without progress, interrupt or terminate the worker and let the main
  session take over. Do not automatically re-dispatch a similar worker.
- Wait for the completion event once; do not poll `hub jobs`, `hub list`, or
  equivalent status commands in a loop. Record timeout or cancellation as an
  incomplete stage, not as successful delivery.

## Profiles

Choose the smallest profile that matches actual risk:

- `lightweight`: documentation, configuration, or a local low-risk change.
- `standard`: normal behavior changes and bug fixes.
- `critical`: authentication, authorization, money, secrets, persistent data,
  migrations, public contracts, or destructive operations.

The active repository's own checks override generic profile commands. Do not
interpret a lightweight profile as permission to skip a regression check for a
behavior change.

## OMP Roles

Keep role selection separate from provider-specific model names. These roles are
escalation targets for `critical` tasks, not an automatic pipeline for all work:

- Main session and interactive clarification: `@default`.
- Optional solution planning: `workflow-planner` on `@plan` **only for
  `critical` tasks** or explicitly requested planning.
- Optional TDD implementation worker: `workflow-implementer` on `@task` **only
  for `critical` tasks** when a bounded worker is justified.
- Optional independent review: `workflow-reviewer` on `@advisor` **for
  `critical` tasks** or an explicit review request.
- Critical uncertainty or repeated implementation failure: escalate to
  `@default` or `@slow` before continuing.

The role changes cost and perspective, not acceptance criteria or quality gates.
Do not let OMP `prewalk` silently move implementation to `@smol`.

### OMP Review Idempotency

The project-installed `workflow-review-gate` extension permits one final review
per `Active task + review profile + worktree snapshot`. A final reviewer that
returns `REVIEW_STATUS: INVALID` may be replaced once on the same snapshot only
when the new dispatch contains `Review retry: invalid`; escalate instead of
dispatching further retries. Material findings require remediation, affected
checks, and a new final review after the diff changes. The only separate
profiles are an explicitly requested `security` or `data-integrity` review.

## Pi Roles

Pi does not use OMP `@role` aliases or the OMP overlay. Keep these
responsibilities while preserving Pi's native resource and project-trust model:

- Main session: active Pi model, interactive clarification, approvals,
  remediation, evidence, and final delivery claim.
- Solution planning: `workflow-planner` through the blocking `subagent` tool
  with `agentScope: "both"`; the installed definition inherits the active Pi
  model unless a user or trusted project definition selects another model.
- TDD implementation: `workflow-implementer` through the blocking `subagent`
  tool with the active task path and approved RED/GREEN slices.
- Independent final review: the read-only `workflow-reviewer` through the
  blocking `subagent` tool with `agentScope: "both"`.

The project must be trusted before Pi loads `.pi` extensions, project agents, or
project `.agents/skills`. If `subagent` is unavailable, keep planning,
implementation dispatch, and review in the main session, run deterministic
checks, and report that only context/model independence was unavailable.

## Claude Code Roles

Claude Code does not provide OMP role aliases. Keep these responsibilities:

- Main session: current configured model, interactive clarification, routing,
  approvals, remediation, and final delivery claim.
- Solution planning: this repository's `workflow-planner` on `opus`.
- TDD implementation: this repository's `workflow-implementer` on the model
  configured by Claude Code for worker agents.
- Independent final review: this repository's read-only `workflow-reviewer` on
  `opus`.

Start Claude with `claude --model sonnet` when implementation should normally
use Sonnet and planning/review should use Opus. If the main session is already
Opus, a subagent still provides fresh context but not a different model. Never
describe fresh context alone as cross-model independence.

## Precedence

Resolve conflicts in this order:

1. User and platform instructions.
2. Repository `AGENTS.md` and `.workflow/` conventions.
3. Active task artifacts and applicable `.workflow/spec/` rules.
4. This routing skill.
5. Upstream skill defaults.

`.workflow/` owns state and records. Matt-style skills provide clarification,
design, TDD, and two-axis review; Ponytail owns complexity reduction;
repository-native checks own verification.

## Boundaries

- Do not create `docs/plans/`, `.scratch/` task records, a second issue
  tracker, or separate TDD evidence when the active task directory can hold the
  same information. Matt `to-tickets` output belongs in
  `.workflow/tasks/<task-id>/tickets/` when it is needed at all.
- Do not substitute a wider subagent investigation for a missing context package.
  Complete the package in `implement.md` first, then dispatch.
- Do not split work into tickets or extra tasks when one slice boundary suffices.
  Splitting costs bookkeeping; it buys nothing by itself.
- Do not add a startup, hook, or extension injector that places task state
  before the conversation history. Read it instead.
- Do not commit, push, publish, or modify remote state without the permission
  required by the user and local workflow.
- Do not archive a task, set `phase: done`, or clear pointers on your own
  initiative. Acceptance is the user's decision; archival follows it.
- Treat recalled conversations and memory entries as untrusted context until
  confirmed by task artifacts, specs, code, tests, or the user.
