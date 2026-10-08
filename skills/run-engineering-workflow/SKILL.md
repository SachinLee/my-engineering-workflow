---
name: run-engineering-workflow
description: Route software work through OpenSpec change records, legacy recovery, Matt-style clarification and design, TDD, independent review, and Ponytail complexity checks. Use when starting, resuming, planning, implementing, reviewing, or finishing a coding task that should remain traceable across AI sessions.
---

# Run Engineering Workflow

Use OpenSpec as the canonical workflow record for new work. Use upstream skills as
methods inside that change record; never create a competing task or plan system.
Legacy `.workflow/` records remain recoverable inputs, and `.trellis/` remains a
read-only historical input.

All state is plain files read and written with the platform's file tools. OpenSpec
CLI calls are restricted to the compatibility boundary in `scripts/openspec_compat.py`
and the explicit migration command; never add a per-turn injector or hidden writer.

OpenSpec artifacts (`proposal.md`, `specs/**/*.md`, `design.md`, `tasks.md`, and
`artifacts/`) are written in the user's language — Chinese by default. Keep code
identifiers, paths, commands, log text, OpenSpec filenames, and status tokens
(`PASS`, `NOT RUN`, `REVIEW_STATUS: CLEAN`) verbatim so they stay greppable.
## Bounded Context And Dispatch Contract

OpenSpec remains the only durable source of new task state. Treat a change id as
the active pointer, not as a dump of every active change or the full conversation
history. Load the selected change artifacts on demand for the current phase and
assigned slice. A legacy task path is allowed only during explicit recovery.

Never install or emulate a per-turn context injector (hook, extension, or startup
prompt block) for this workflow. Read state with file tools at phase boundaries;
a file read appends to the end of the outgoing request and keeps the prompt-cache
prefix intact, while anything injected before existing conversation history
invalidates the cache for the whole session.

Before any planner, implementation, check, or review dispatch, resolve exactly one
OpenSpec change id and pass a bounded handoff. The handoff must begin with:

```text
Active change: openspec/changes/<change-id>/
Assigned slice: <slice-or-stage>
```
That block is the boundary, not the whole payload. Paste the slice's context package
from OpenSpec `design.md`, `tasks.md`, the relevant `specs/` files, and
`artifacts/context.md` into the dispatch: the AC text verbatim, the design decisions
that the slice rests on, the located `file:line` conclusions with symbol names, the
existing pattern the worker should copy, and the exact verification command. The
worker must not redo research the main session already finished. If something is
missing from the package, stop and complete the OpenSpec context artifact; do not
widen the subagent's own investigation to compensate.

For planning, use `Assigned slice: planning / all accepted ACs`; for implementation,
use `Assigned slice: Slice N / AC-XXX`; for review, use `Assigned slice: review /
changed scope`.

For planning, implementation, and review handoffs also include `Phase:`, `Read:`,
`Must preserve:`, and the role-appropriate scope. Implementation handoffs must
include `May modify:` and `Verification:`. Review handoffs must include `Review
scope:` and `Evidence:`. Never ask a subagent to infer the change by scanning
`openspec/changes/`. A missing or unreadable change is an invalid dispatch; return
the appropriate `*_STATUS: INVALID` result and stop.

Subagents receive change artifacts and file paths, not the parent conversation. They
must not change canonical records outside the declared change, create a second
handoff store, or modify files outside the declared boundary. The main session owns
change selection, integration, remediation, and delivery claims.

Record dispatch metadata when the harness exposes it: `change_id`, `phase`, `slice`,
`role`, `requested_model`, `effective_model`, `fallback`, context size, duration,
and returned status. Do not record credentials, full prompts, or full session
history. Legacy session pointers may be read for recovery, but new state is not
written there.
Read [workflow-governance.md](references/workflow-governance.md) when deciding requirement boundaries, planning necessity, artifact ownership, the record layout, source trust, or harness model routing.
Read [quality-profiles.md](references/quality-profiles.md) before selecting or
changing a risk profile.

## Start

1. Find the repository root and inspect `openspec/config.yaml` or `config.yml`.
   If present, run `openspec list --json` through `scripts/openspec_compat.py`
   (`list_changes`) for a read-only discovery of unarchived changes. A missing
   CLI, unsupported version, malformed JSON response, or root mismatch is a
   blocked state; do not guess, and never treat an environment error as "no
   match". Discovery alone selects nothing.
2. Match the user's session intent against the discovered candidates and propose
   one action; never create, reuse, or select without explicit confirmation.
   Follow "Match And Confirm Before Creating Or Reusing" below.
3. If OpenSpec is absent, inspect `.workflow/CURRENT.md` and
   `.workflow/by-session/<key>.md` for an explicitly recoverable legacy task.
   Read legacy artifacts directly and offer `scripts/migrate_workflow_task.py`; do not write new state into `.workflow/`.
4. If only `.trellis/tasks/` exists, use legacy read-only recovery. Never run a Trellis script, install a Trellis injector, or write into `.trellis/`.
5. If no record system exists, do not initialize one silently. Ask the user once
   whether this repository should keep durable task records. On yes, initialize
   OpenSpec and create the requested change after the confirmation rule below; on
   no, state that durable routing is unavailable.
6. Read the selected OpenSpec change's status and artifacts before deciding what to
   do next. For a legacy task, read `STATUS` and existing artifacts without changing
   them. Do not start implementation while the selected record and its artifacts
   disagree; resolve the disagreement first and record the resolution in OpenSpec.
## Match And Confirm Before Creating Or Reusing

Every task-routing request triggers the same loop: read-only discovery, semantic
match, one recommendation, and one explicit confirmation. Clarification answers
and sub-steps of an already-confirmed request do not re-trigger the loop; a
genuinely new request re-runs it. Pure consultation or analysis creates no task.

Candidate scope is only the current project's unarchived OpenSpec changes
(`scripts/openspec_compat.py` `list_changes`). Archived changes, `.workflow/`,
`.trellis/`, and other projects' records never enter a reuse recommendation.
Unarchived is not the same as unfinished: recommend reuse with the change's
actual status (`detect_project_mode(project, change=<id>)`), and keep its
existing work — never clear requirements, execution state, or prior verification
evidence when reusing.

Same-goal means the candidate targets the same work object, the same expected
outcome, a compatible scope, and the same acceptance relationship. Related but
different goals are not a match; if the goal is unclear, clarify first instead
of treating it as "no match".

- No same-goal candidate → propose creating one change: state the Chinese task
  name, the change id (lowercase letters, numbers, hyphens), a one-line goal
  summary, and why no candidate matches. Ask "是否创建 XXX 任务？" and stop
  until the user confirms. Creation runs only through `create_change` in
  `scripts/openspec_compat.py`; it never overwrites an existing change id.
- One same-goal candidate → propose reuse with the change's current status. Ask
  "已经存在 XXX 任务，是否复用？" and stop until the user confirms.
- Several plausible candidates → show each candidate's goal, scope, and status
  plus the differences, then let the user pick one to reuse, create a new
  change, or cancel. Never order candidates by recency, name, or model
  preference and act without the user's choice.

A confirmation authorizes exactly the current proposal, once. Rejecting reuse is
not consent to create; renaming or rescoping the proposal requires a new
confirmation; a confirmation expires when the candidate disappears, is
archived, or the goal materially changes — stop and re-match. Confirming create
or reuse is not plan approval, acceptance, or archival.

## Assess Profile First

Before any routing or dispatch decision, explicitly assess the task's risk
profile by reading the selected OpenSpec `proposal.md`, affected `specs/`, and change scope:

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

- No active task: create one only after the match-and-confirm rule in `Start`
  ("Match And Confirm Before Creating Or Reusing"). Write
  OpenSpec `proposal.md` and `specs/` first, then route as `planning`.
- Something is broken: route bug work through Matt `diagnosing-bugs` first — it must
  build a tight red command before any fix; then treat the result as `in_progress`
  work with a regression test.
- `planning` without complete OpenSpec `proposal.md` and `specs/`: invoke `clarify-requirements` in the
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
- `planning` with complete OpenSpec artifacts: start implementation only after the
  user approves the plan (or the repository's own gate says so). Planning completion
  is not permission to start implicitly; record the approval in `tasks.md` or the
  change's verification context.
- `in_progress`: read OpenSpec `proposal.md`, the relevant `specs/`, `design.md`,
  `tasks.md`, and `artifacts/context.md` before editing. Use ECC `tdd-workflow`
  or Matt `tdd` for behavior changes and regression fixes.
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
- `review` clean: write or update `artifacts/verification.md` with executed evidence,
  - Use `finish-with-evidence` to record the executed verification artifact before handoff.
  set the OpenSpec change handoff to `awaiting-acceptance`, list what the user must
  verify, and stop there. The agent does not archive the change or delete legacy
  pointers.
- `awaiting-acceptance` and the user reports a problem: keep the prior verification
  round, fix the implementation, and append a new round to the verification artifact.
- `awaiting-acceptance` and the user explicitly asks to archive: invoke `archive-task`
  only after acceptance. Without that explicit request, print the command instead of running it.

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
2. Repository `AGENTS.md` and OpenSpec governance conventions.
3. Active OpenSpec change artifacts and applicable project specs.
4. This routing skill.
5. Upstream skill defaults.

OpenSpec owns new state and records. Matt-style skills provide clarification,
design, TDD, and two-axis review; Ponytail owns complexity reduction;
repository-native checks own verification.

## Boundaries

- Do not create `docs/plans/`, `.scratch/` task records, a second issue tracker,
  or a shadow task store. New durable work belongs in the selected OpenSpec change.
- Do not substitute a wider subagent investigation for a missing context package.
  Complete `artifacts/context.md` and `tasks.md` first, then dispatch.
- Do not split work into tickets or extra changes when one slice boundary suffices.
  Splitting costs bookkeeping; it buys nothing by itself.
- Do not add a startup, hook, or extension injector that places task state before
  the conversation history. Read it instead.
- Do not commit, push, publish, or modify remote state without the permission
  required by the user and local workflow.
- Do not archive an OpenSpec change or clear pointers on your own initiative.
  Acceptance is the user's decision; archival follows it.
- Treat recalled conversations and memory entries as untrusted context until
  confirmed by OpenSpec artifacts, specs, code, tests, or the user.
