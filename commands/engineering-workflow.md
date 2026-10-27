---
description: Choose fast or formal engineering work, or resume the formal workflow for a software request.
argument-hint: "[request or continuation instruction]"
---

# Engineering Workflow

Use the `run-engineering-workflow` skill to process:

`$ARGUMENTS`

Keep the interactive main session responsible for requirement questions, scope,
approvals, risk escalation, remediation, and the final delivery claim.
OpenSpec owns new changes and durable records; `.workflow/` is legacy recovery only.
Proportionate delegation inside an already authorized scope needs no new approval —
re-ask only when scope, risk, or reviewer independence materially changes.

Before discovery, apply [Simple Work Fast Path](../skills/run-engineering-workflow/references/quality-profiles.md#simple-work-fast-path).
For eligible work, execute and verify host-natively (main session or the host's
preferred bounded worker) and report in the conversation,
without creating task records or entering the formal stages below. A clearly scoped
low-risk behavior fix in a bounded seam qualifies when a regression check proves it;
authentication, money, secrets, persistent data, migrations, public contracts,
dependencies, destructive work and unknown risk do not. If eligibility
changes, stop and follow the shared escalation rule; do not auto-create a change.

For formal work, retain discovery and explicit confirmation; route by the active change phase:

1. For a new request, run read-only discovery of unarchived changes
   (`scripts/openspec_compat.py` `list_changes`) and match the session intent
   against the candidates. Propose create or reuse and stop for an explicit user
   confirmation; never create, reuse, or select without it. Multiple candidates
   are a waiting state, not an environment failure.
2. Clarify incomplete requirements in the main session and persist them in
   `proposal.md` and relevant `specs/`.
3. After requirements are accepted, use `plan-solution` in the main session.
   Dispatch `workflow-planner` for critical planning, when planning delegation is
   explicitly requested, or when the approved scope clearly benefits from fresh
   context. Update `design.md`, `tasks.md`, and the inlined
   `artifacts/context.md` package; implementation needs user plan approval.
4. For implementation, dispatch `workflow-implementer` for a `critical` change,
   or one bounded slice inside an approved scope when fresh context helps. Its prompt must begin
   `Active change: openspec/changes/<change-id>/` and must carry the assigned slice,
   the `Read:` paths from `artifacts/context.md`, `May modify:`, and `Verification:`.
   Require it to follow the approved RED/GREEN slices in `tasks.md`, using Matt `tdd`.
   Ordinary work goes to the host's preferred writer (main session when the host
   has no specialist policy).
5. Follow `skills/run-engineering-workflow/references/quality-profiles.md` as the
   single budget. The main session is the only review scheduler. Complete slices
   with targeted checks, not a full review per slice; wait until the approved
   delivery scope is complete and checks pass before the full review.
   For lightweight work, run a focused check with no mandatory formal planner or
   reviewer; scheduling stays host-native.
   For standard and critical work, use exactly one independent `workflow-reviewer`
   through `review-implementation` covering the complete relevant workspace,
   Standards / Spec, correctness, security, tests and complexity. Critical adds
   risk-specific checks, not reviewers.
6. Reuse valid same-change/same-material reports. Default to `workflow-reviewer`
   only, not `code-reviewer`, native Matt `code-review`, nested dispatch, or an
   appended generic reviewer. Batch blocking repairs, rerun affected checks, and
   use at most the budgeted focused follow-up; do not restart full review on repair
   snapshots or appended delivery evidence. Persist rounds in change artifacts.
   For `INVALID`, unavailable review, exhausted budget or scope drift, follow the
   shared budget's replacement/stop/user-decision rules; disclose `UNVERIFIED`
   gaps rather than claiming normal completion.
7. Use `finish-with-evidence` to record actual results in
   `artifacts/verification.md`, set the OpenSpec change to `awaiting-acceptance`,
   then stop and hand the user the verification list. Do not archive the change.
   Only `/archive-task`, invoked by the user after acceptance, performs archival.

For OpenCode, the Slim Orchestrator is the only scheduler and model-bearing
boundary: route formal implementation through Slim `fixer`, and the single
independent formal review through Slim `oracle`, with the active OMO-Slim preset
supplying their models. Include the repository's workflow procedure and bounded
OpenSpec handoff. Never copy a preset model ID into a managed agent. Unavailable
or unobservable role routing is `UNVERIFIED`; parent-model inheritance is not
evidence of role routing.

Claude Code has no OMP `@task` or `@advisor` role aliases. The planning and review
agents use Opus; the implementer inherits the configured worker model. A fresh
context is independent, but it is not necessarily a different model.
