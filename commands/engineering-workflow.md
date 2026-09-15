---
description: Run or resume the five-stage engineering workflow for a software request.
argument-hint: "[request or continuation instruction]"
---

# Engineering Workflow

Use the `run-engineering-workflow` skill to process:

`$ARGUMENTS`

Keep the interactive main session responsible for requirement questions,
scope, approvals, risk escalation, remediation, and the final delivery claim.
`.workflow/` remains the only task and durable-record system.

Route work by the active task phase:

1. Clarify incomplete requirements in the main session and persist them in
   `prd.md`.
2. After requirements are accepted, dispatch `workflow-planner` to create or
   update `design.md`, `implement.md`, and the `context.md` read list. Do not
   start implementation until the user approves the plan and `STATUS` moves to
   `in_progress`.
3. For implementation, dispatch `workflow-implementer` only for a `critical`
   task or an explicitly justified fresh-context need. Its prompt must begin
   `Active task: .workflow/tasks/<task-id>/` and must carry the assigned slice,
   the `Read:` paths from `context.md`, `May modify:`, and `Verification:`.
   Require it to follow the approved RED/GREEN slices in `implement.md`.
   Ordinary work is implemented in the main session.
4. Run the repository's own checks, then Matt `code-review` for the
   Standards-versus-Spec axis.
5. After checks complete and the worktree is stable, dispatch exactly one
   `workflow-reviewer` for independent final review. Do not append generic
   `reviewer` or `code-reviewer` tasks for the same snapshot. The main session
   fixes findings, reruns affected checks, and dispatches a new final review
   only after the diff changes. An `INVALID` review has one controlled retry;
   its prompt must contain `Review retry: invalid`.
6. Use `finish-with-evidence` to record actual results in `outcome.md` and set
   `STATUS` to `awaiting-acceptance`, then stop and hand the user the verification
   list. Do not move the task, write the journal line, clear pointers, or set
   `phase: done`. Only `/archive-task`, invoked by the user after they accept,
   performs those steps.

Claude Code has no OMP `@task` or `@advisor` role aliases. The planning and
review agents use Opus; the implementer inherits the configured worker model.
A fresh context is independent, but it is not necessarily a different model.
