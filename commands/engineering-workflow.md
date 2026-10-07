---
description: Run or resume the five-stage engineering workflow for a software request.
argument-hint: "[request or continuation instruction]"
---

# Engineering Workflow

Use the `run-engineering-workflow` skill to process:

`$ARGUMENTS`

Keep the interactive main session responsible for requirement questions, scope,
approvals, risk escalation, remediation, and the final delivery claim.
OpenSpec owns new changes and durable records; `.workflow/` is legacy recovery only.

Route work by the active change phase:

1. For a new request, run read-only discovery of unarchived changes
   (`scripts/openspec_compat.py` `list_changes`) and match the session intent
   against the candidates. Propose create or reuse and stop for an explicit user
   confirmation; never create, reuse, or select without it. Multiple candidates
   are a waiting state, not an environment failure.
2. Clarify incomplete requirements in the main session and persist them in
   `proposal.md` and relevant `specs/`.
3. After requirements are accepted, dispatch `workflow-planner` to create or
   update `design.md`, `tasks.md`, and `artifacts/context.md`. Do not start
   implementation until the user approves the plan and the OpenSpec change is
   ready for implementation.
4. For implementation, dispatch `workflow-implementer` only for a `critical`
   change or an explicitly justified fresh-context need. Its prompt must begin
   `Active change: openspec/changes/<change-id>/` and must carry the assigned slice,
   the `Read:` paths from `artifacts/context.md`, `May modify:`, and `Verification:`.
   Require it to follow the approved RED/GREEN slices in `tasks.md`. Ordinary work
   is implemented in the main session.
5. Run the repository's own checks, then Matt `code-review` for the
   Standards-versus-Spec axis.
6. After checks complete and the worktree is stable, dispatch exactly one
   `workflow-reviewer` for independent final review. Do not append generic
   `reviewer` or `code-reviewer` tasks for the same snapshot. The main session
   fixes findings, reruns affected checks, and dispatches a new final review only
   after the diff changes. An `INVALID` review has one controlled retry; its prompt
   must contain `Review retry: invalid`.
7. Use `finish-with-evidence` to record actual results in
   `artifacts/verification.md`, set the OpenSpec change to `awaiting-acceptance`,
   then stop and hand the user the verification list. Do not archive the change.
   Only `/archive-task`, invoked by the user after acceptance, performs archival.

Claude Code has no OMP `@task` or `@advisor` role aliases. The planning and review
agents use Opus; the implementer inherits the configured worker model. A fresh
context is independent, but it is not necessarily a different model.
