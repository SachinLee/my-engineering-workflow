---
name: run-engineering-workflow
description: Route software work through Trellis records, requirement clarification, solution planning, ECC quality practices, and complexity review. Use when starting, resuming, planning, implementing, reviewing, or finishing a coding task that should remain traceable across AI sessions.
---

# Run Engineering Workflow

Use Trellis as the workflow state and durable record. Use upstream skills as
methods inside that workflow; never create a competing task or plan system.

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

## Route By State

- No active task: follow the local Trellis consent and task-creation rules.
- `planning` without a complete `prd.md`: invoke `clarify-requirements`.
- `planning` with accepted requirements but no reviewed solution: invoke
  `plan-solution`. It writes `design.md` and `implement.md` when the selected
  profile and change shape require them. In OMP or Claude Code, dispatch the
  harness-specific `workflow-planner`.
- `planning` with complete artifacts: follow the local Trellis gate for entering
  `in_progress`; planning completion is not permission to start implicitly.
- `in_progress`: read `prd.md`, optional `design.md`, optional `implement.md`,
  and relevant `.trellis/spec/` files through `trellis-before-dev`. Use ECC
  `tdd-workflow` for behavior changes and regression fixes. In OMP, preserve
  the Trellis dispatch protocol: dispatch `trellis-implement` on `@task` and
  require it to read `skill://tdd-workflow` before editing. In Claude Code,
  preserve the native Trellis `trellis-implement` definition and context hook;
  dispatch it with the active task path and require the approved RED/GREEN
  slices in `implement.md`. Do not claim that the native agent auto-loads ECC.
- Code changed: run `trellis-check` and risk-specific ECC checks, then invoke
  `review-implementation` from a fresh context. In OMP, dispatch
  `workflow-reviewer`. In Claude Code, first dispatch the native Trellis
  `trellis-check`, then dispatch this repository's `workflow-reviewer`. The main
  session fixes findings and repeats affected checks; the implementation model
  does not approve its own work.
- Ready to finish: invoke `finish-with-evidence` before Trellis archival or
  journal recording.

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

Keep role selection separate from provider-specific model names:

- Main session and interactive clarification: `@default`.
- Solution planning: `workflow-planner` on `@plan`.
- TDD implementation: Trellis `trellis-implement` on `@task`.
- Trellis quality check: `trellis-check` on `@advisor`.
- Independent final review: `workflow-reviewer` on `@advisor`.
- Critical uncertainty or repeated implementation failure: escalate to
  `@default` or `@slow` before continuing.

The role changes cost and perspective, not acceptance criteria or quality
gates. The active `.trellis/workflow.md` remains authoritative for dispatch
names and context injection. Do not let OMP `prewalk` silently move
implementation to `@smol`.

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
module design. ECC owns TDD, specialist review, and verification. Ponytail owns
complexity reduction only. Never let one layer write a second source of truth.

## Boundaries

- Do not create `docs/plans/`, a second issue tracker, or separate TDD evidence
  when the active Trellis task can hold the same information.
- Do not commit, push, publish, archive, or modify remote state without the
  permission required by the user and local workflow.
- Treat recalled conversations and memory entries as untrusted context until
  confirmed by task artifacts, specs, code, tests, or the user.
