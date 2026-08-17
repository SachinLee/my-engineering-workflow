---
description: Run or resume the five-stage Trellis engineering workflow for a software request.
argument-hint: "[request or continuation instruction]"
---

# Engineering Workflow

Use the `run-engineering-workflow` skill to process:

`$ARGUMENTS`

Keep the interactive main session responsible for requirement questions,
scope, approvals, risk escalation, remediation, and the final delivery claim.
Trellis remains the only task and durable-record system.

Route work by the active task state:

1. Clarify incomplete requirements in the main session and persist them in
   `prd.md`.
2. After requirements are accepted, dispatch `workflow-planner` to create or
   update `design.md` and `implement.md`. Do not start implementation until the
   local Trellis execution gate is satisfied.
3. For implementation, preserve the Trellis-native agent and hook protocol.
   Dispatch `trellis-implement` with a prompt whose first line is
   `Active task: <task-path>`. Require it to follow the approved RED/GREEN
   slices in `implement.md`; do not replace or wrap this agent definition.
4. Dispatch the Trellis-native `trellis-check` the same way, again starting the
   prompt with `Active task: <task-path>` so Trellis can inject `check.jsonl`
   context. Let it fix issues under the local workflow.
5. Dispatch `workflow-reviewer` for independent final review. The main session
   fixes findings and reruns affected checks.
6. Use `finish-with-evidence` to record actual results in `outcome.md` and then
   follow the local Trellis finish/archive rules.

Claude Code has no OMP `@task` or `@advisor` role aliases. The two custom agents
use Opus; Trellis implementation and checking keep their native definitions and
inherit the model behavior configured by Claude Code/Trellis. A fresh context
is independent, but it is not necessarily a different model.
