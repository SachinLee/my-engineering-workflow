---
name: run-engineering-workflow
description: Route software work through Trellis records, Matt-style clarification and design, TDD, independent review, and Ponytail complexity checks. Use when starting, resuming, planning, implementing, reviewing, or finishing a coding task that should remain traceable across AI sessions.
---

# Run Engineering Workflow

Use Trellis as the workflow state and durable record. Use upstream skills as
methods inside that workflow; never create a competing task or plan system.


## Bounded Context And Dispatch Contract

Trellis remains the only durable source of task state. Treat startup context as a
small project summary plus a task pointer, not as a dump of every active task or
the full conversation history. Load dynamic task artifacts on demand for the
current phase and assigned slice.

Before any OMP planner, implementation, check, or review dispatch, resolve exactly
one task path from Trellis and pass a bounded handoff. The handoff must begin with:
```text
Active task: .trellis/tasks/<task-id>/
Assigned slice: <slice-or-stage>
```

For planning, use `Assigned slice: planning / all accepted ACs`; for implementation,
use `Assigned slice: Slice N / AC-XXX`; for review, use `Assigned slice: review /
changed scope`.

For planning, implementation, and review handoffs also include `Phase:`, `Read:`,
`Must preserve:`, and the role-appropriate scope. Implementation handoffs must
include `May modify:` and `Verification:`. Review handoffs must include
`Review scope:` and `Evidence:`. Never ask a subagent to infer the task by
scanning `.trellis/tasks/`. A missing or unreadable task path is an invalid
dispatch; return the appropriate `*_STATUS: INVALID` result and stop.

Subagents receive task artifacts and file paths, not the parent conversation. They
must not change global `CURRENT TASK`, create a second handoff store, or modify
files outside the declared boundary. The main session owns task selection,
integration, remediation, and delivery claims.

Record dispatch metadata when the harness exposes it: `task_path`, `phase`,
`slice`, `role`, `requested_model`, `effective_model`, `fallback`, context size,
duration, and returned status. Do not record credentials, full prompts, or full
session history. If named-task context resolution is unavailable, warn and fall
back to explicit paths and artifact sections; do not silently widen the context.
Read [workflow-governance.md](references/workflow-governance.md) when deciding
artifact ownership, source trust, extension precedence, or harness model routing.
Read [quality-profiles.md](references/quality-profiles.md) before selecting or
changing a risk profile.

## Start

1. Find the repository root and `.trellis/workflow.md`.
2. If Trellis is absent, do not initialize it silently. Follow the repository's
   existing workflow and tell the user that durable task routing is unavailable.
3. Resolve one working external Python command before invoking any Trellis
   script, then reuse it for the whole turn. On Windows, prefer `py -3`; do not
   use bare `python` or `python3` when it resolves to a WindowsApps alias or its
   `--version` probe exits nonzero. On macOS/Linux, prefer `python3`, then a
   successfully probed `python`. A documented command name may be translated
   to the working platform launcher without changing the Trellis arguments.
4. Load Trellis context with that command, for example
   `py -3 ./.trellis/scripts/get_context.py` on Windows, then request
   `--mode phase`.
5. In OMP, run Trellis CLI scripts only as external processes through the
   terminal/bash tool. Never use the `eval` Python kernel to import or execute
   Trellis modules. Never mutate `sys.platform`, monkeypatch Git or hooks, or
   manually synthesize task artifacts to bypass a failed CLI call. If no
   interpreter works or a Trellis command still fails, preserve the error,
   stop Trellis mutations, and report the blocker.
6. Read the active task status and its existing artifacts before deciding what
   to do next.

## Assess Profile First

Before any routing or dispatch decision, explicitly assess the task's risk profile
by reading `prd.md` and the task scope:

1. **Is this critical?** Does the task touch authentication, authorization, money,
   secrets, persistent data, migrations, public contracts, destructive operations,
   or a cross-layer release boundary?
   - **Yes** → profile is `critical`
   - **No** → continue to step 2

2. **Is this lightweight?** Is this only documentation, local configuration, or an
   isolated low-risk change with no behavior modification?
   - **Yes** → profile is `lightweight`
   - **No** → profile is `standard` (normal features, bug fixes, refactors)

3. **State the assessed profile explicitly** before proceeding to routing.
   Example: "This is a **standard** task (bug fix in presentation layer, no auth
   or data changes). Implementation will stay in the main session unless a bounded
   worker is justified."

When uncertain, default to `standard` and escalate to `critical` only when clear
risk signals appear. Never default to `critical` for ordinary feature work.

## Route By State

After assessing the profile, route according to the task state and the assessed
risk level. The profile controls dispatch, not just the checklist:

- `lightweight`: keep the work in the main session. Do not dispatch planner,
  implementer, checker, or reviewer. Run one focused check before delivery.
- `standard`: keep implementation in the main session by default. Use at most one
  implementation worker or one check worker when the boundary benefits from fresh
  context; never dispatch both implementation workers or duplicate reviewers.
- `critical`: use the full gated path when the change touches auth, secrets, money,
  persistent data, migrations, public contracts, destructive operations, or a
  cross-layer release boundary.

- No active task: follow the local Trellis consent and task-creation rules.
- `planning` without a complete `prd.md`: invoke `clarify-requirements` in the main
  session. Only dispatch `workflow-planner` if the task is assessed as `critical`
  or the user explicitly requests planning delegation.
- `planning` with accepted requirements but no reviewed solution:
  - For `lightweight` or `standard`: invoke `plan-solution` in the main session.
  - For `critical`: In OMP, dispatch `workflow-planner` on `@plan`. In Pi, use the
    blocking `subagent` tool with `agentScope: "both"` when available; otherwise
    keep planning in the main session and disclose the lack of fresh context.
  - Only dispatch a planner if the task is assessed as `critical` or when the main
    session cannot resolve a material design uncertainty.
- `planning` with complete artifacts: follow the local Trellis gate for entering
  `in_progress`; planning completion is not permission to start implicitly.
- `in_progress`: read `prd.md`, optional `design.md`, optional `implement.md`,
  and relevant `.trellis/spec/` files through `trellis-before-dev`. Use ECC
  `tdd-workflow` for behavior changes and regression fixes.
  - For `lightweight` or `standard`: implement in the main session. Only use a
    single bounded worker if explicitly justified by the need for fresh context.
  - For `critical`: dispatch `trellis-implement` on `@task` and require it to read
    `skill://tdd-workflow` before editing. In Pi, use the project's native
    `trellis_subagent` with `trellis-implement` so Trellis keeps task-context
    injection; do not replace it with a generic subagent.
- Code changed: run the smallest check that proves the changed behavior.
  - For `lightweight`: run one focused check before delivery.
  - For `standard`: use either `trellis-check` or `workflow-reviewer`, not both.
    In a project with native Trellis check, prefer `trellis-check`; otherwise use
    `review-implementation` in a fresh context.
  - For `critical`: run `trellis-check` and then `workflow-reviewer` from a fresh
    context. In OMP, run exactly one `workflow-reviewer` final review after checks
    finish, against a stable worktree snapshot; do not append duplicate reviewer
    tasks. In Claude Code, first run the native Trellis `trellis-check`, then this
    repository's `workflow-reviewer`. In Pi, first use native `trellis-check`, then
    the blocking `subagent` reviewer when available.
  - The main session fixes findings and repeats affected checks; a changed snapshot
    requires a new review. The implementation model does not approve its own work.
- Ready to finish: invoke `finish-with-evidence` before Trellis archival or
  journal recording.

### OMP Dispatch Limits

These limits enforce the profile-based routing rules:

- **Prefer the main session for `lightweight` and `standard` work.** Only dispatch
  when the assessed profile is `critical` or when fresh context is explicitly
  justified for a bounded slice.
- Allow at most one live writer and one review/check worker for a task.
- Treat a worker as making progress only when it edits a declared file, runs a
  relevant check, reports a concrete result, or states a reproducible blocker.
- After 10 minutes without progress, request one status update. After 15 minutes
  without progress, interrupt or terminate the worker and let the main session
  take over. Do not automatically re-dispatch a similar worker.
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
- Optional solution planning: `workflow-planner` on `@plan` **only for `critical`
  tasks** or explicitly requested planning.
- Optional TDD implementation worker: Trellis `trellis-implement` on `@task` **only
  for `critical` tasks** when a bounded worker is justified.
- Optional quality check: `trellis-check` on `@advisor`; use it once for `standard`
  work when fresh context is useful, and with the full critical gate when required.
- Optional independent final review: `workflow-reviewer` on `@advisor` **for
  `critical` tasks** or an explicit review request.
- Critical uncertainty or repeated implementation failure: escalate to `@default`
  or `@slow` before continuing.

The role changes cost and perspective, not acceptance criteria or quality gates. The
active `.trellis/workflow.md` remains authoritative for dispatch names and context
injection. Do not let OMP `prewalk` silently move implementation to `@smol`.

### OMP Review Idempotency

The project-installed `workflow-review-gate` extension permits one final review
per `Active task + review profile + worktree snapshot`. `trellis-check` remains
a separate quality gate and is never suppressed. A final reviewer that returns
`REVIEW_STATUS: INVALID` may be replaced once on the same snapshot only when the
new dispatch contains `Review retry: invalid`; escalate instead of dispatching
further retries. Material findings require remediation, affected checks, and a
new final review after the diff changes. The only separate profiles are an
explicitly requested `security` or `data-integrity` review.

## Pi Roles

Pi does not use OMP `@role` aliases or the OMP overlay. Keep these
responsibilities while preserving Pi's native resource and project-trust model:

- Main session: active Pi model, interactive clarification, approvals,
  remediation, evidence, and final delivery claim.
- Solution planning: `workflow-planner` through the blocking `subagent` tool
  with `agentScope: "both"`; the installed definition inherits the active Pi
  model unless a user or trusted project definition selects another model.
- TDD implementation: the project-owned Trellis `trellis-implement` through
  `trellis_subagent`, with the active task path and approved RED/GREEN slices.
- Trellis quality check: the project-owned `trellis-check` through
  `trellis_subagent` so Trellis keeps `check.jsonl` context injection.
- Independent final review: the read-only `workflow-reviewer` through the
  blocking `subagent` tool with `agentScope: "both"`.

The project must be trusted before Pi loads `.pi` extensions, project agents,
or project `.agents/skills`. If `subagent` is unavailable, keep planning and
review in the main session, run deterministic checks, and report that only
context/model independence was unavailable. Never substitute generic Pi
subagents for Trellis implementation or check agents.

## Claude Code Roles

Claude Code does not provide OMP role aliases. Keep these responsibilities:

- Main session: current configured model, interactive clarification, routing,
  approvals, remediation, and final delivery claim.
- Solution planning: this repository's `workflow-planner` on `opus`.
- TDD implementation: the native Trellis `trellis-implement`; do not replace
  its agent file or hook-driven `implement.jsonl` context injection.
- Trellis quality check: the native Trellis `trellis-check`; preserve its
  `check.jsonl` context injection and self-fix contract.
- Independent final review: this repository's read-only `workflow-reviewer` on
  `opus`.

Start Claude with `claude --model sonnet` when implementation should normally
use Sonnet and planning/review should use Opus. If the main session is already
Opus, a subagent still provides fresh context but not a different model. Never
describe fresh context alone as cross-model independence.

## Precedence

Resolve conflicts in this order:

1. User and platform instructions.
2. Repository `AGENTS.md` and `.trellis/workflow.md`.
3. Active task artifacts and applicable `.trellis/spec/` rules.
4. This routing skill.
5. Upstream skill defaults.

Trellis owns state and records. Matt-style skills improve clarification and
module design. Matt owns TDD and design discipline; Ponytail owns complexity
reduction; repository-native checks own verification.

## Boundaries

- Do not create `docs/plans/`, a second issue tracker, or separate TDD evidence
  when the active Trellis task can hold the same information.
- Do not commit, push, publish, archive, or modify remote state without the
  permission required by the user and local workflow.
- Treat recalled conversations and memory entries as untrusted context until
  confirmed by task artifacts, specs, code, tests, or the user.
