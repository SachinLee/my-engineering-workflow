---
name: review-implementation
description: Independently review a completed implementation against the active task's requirements, project rules, tests, security constraints, and complexity budget. Use after implementation and before final evidence, especially when a different AI model or fresh context should challenge correctness claims.
---

# Review Implementation

Review from a fresh context when the platform supports it. Do not implement the
change under review and then approve it in the same pass.

Write your findings in the user's language (Chinese by default); keep identifiers,
paths, commands, and severity tokens verbatim.

## Establish The Contract

1. Read the declared change artifacts and `Review mode: full | focused` from the
   handoff. Missing mode, scope, or evidence is `REVIEW_STATUS: INVALID`.
2. For full mode, inspect the complete relevant workspace, adjacent code and tests;
   map every required acceptance criterion to implementation and executed evidence.
3. For focused mode, consume the prior full report and original blocking findings,
   inspect the repair diff and directly affected paths/tests, and confirm the repair
   checks. Preserve original coverage for unchanged inputs; do not redo the full survey.
4. Keep current-task changes separate from unrelated user or concurrent changes.

## One Workspace Review

Follow `../run-engineering-workflow/references/quality-profiles.md`, the sole
Delivery Review Budget. The main router schedules the full review and any focused
follow-up; this skill is its review procedure, not a second scheduler. Standard and
Critical use `workflow-reviewer` only, never default `code-reviewer` or nested
native Matt `code-review`. Lightweight has no default review dispatch. Ponytail
is a complexity lens in the same report.

Capture the complete relevant workspace: committed changes from the declared
base, staged (`git diff --cached`), unstaged (`git diff`), and explicitly named
untracked test/file contents. An empty base-to-HEAD diff proves nothing about
uncommitted work. Use `git status` to enumerate candidates, but inspect only the
approved relevant files, never unrelated or sensitive untracked files. Keep
unrelated user changes identifiable and untouched.

The handoff carries `Active change:`, `Assigned slice:`, `Phase:`, `Read:`,
`Must preserve:`, `Review mode:`, `Review scope:`, and `Evidence:`. Inline the known ACs, design
and verification conclusions; identify the base, file list, diff/current contents,
requirements and actual check results. The selected proposal/specs own Spec;
do not seek another issue or `.scratch/` requirement to override them. A Pi
read-only reviewer consumes recorded check evidence, not shell privileges.

Only an explicit user request enables native Matt review: require a valid fixed
point and nonempty committed diff to HEAD plus delegation authorization for its
two agents. It is not a certification of staged/unstaged/untracked work. Do not
silently add a third review; report missing workspace coverage instead.

Reuse only real same-change/same-material independent evidence with complete
coverage. After local blocking repairs, combine the prior full report with the
budgeted focused follow-up and affected check results to cover the final contents;
never treat the old report alone as approval of unaudited repairs. Expanded inputs
return to the main router for a user decision under the shared budget, not an
automatic full review. Appending the report or delivery evidence does not invalidate
coverage unless substantive reviewed inputs change. Allow one controlled replacement
for `INVALID` with no valid report as the shared budget specifies, using
`Review retry: invalid`. Missing independent context, round history or coverage
stays `UNVERIFIED`, not `CLEAN` or normal completion.

## Full Review In Order

1. Correctness: find missed ACs, regressions, boundary errors, concurrency
   hazards, failure-path defects, and incorrect assumptions.
2. Tests: check that assertions prove public behavior, include meaningful
   negative paths, and would fail for the defect they claim to prevent.
3. Security and data integrity: inspect input boundaries, authorization,
   secrets, injection, destructive behavior, persistence, migrations, and
   rollback when applicable.
4. Project compliance: compare the change with `AGENTS.md`, project specs,
   established local patterns, and public contracts.
5. Maintainability and complexity: identify unnecessary abstraction,
   duplication, dependencies, configuration, compatibility paths, and dead code
   without weakening required safeguards.
6. Evidence: run the smallest commands needed to confirm or reject material
   findings. Never turn an unexecuted check into a PASS.

## Focused Follow-Up

Check original blocking findings, the repair diff, and directly affected behavior
only. Report each original finding as resolved or remaining with evidence; report
new blocking regressions caused by the repairs. Record optional observations
separately without widening into a whole-scope optimization review. Return the
combined coverage and any gap to the main router; it owns the budget and next step.

## Report Findings

Lead with actionable findings ordered by severity. For each finding include:
Report **Standards** (project rules and conventions) and **Spec** (every selected
change AC and evidence) separately, including an explicit no-findings statement
for each when appropriate. Then summarize correctness, security, tests,
complexity, residual risk, and unexecuted checks in the same report.

- Severity: `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`.
- Blocking: `yes | no`, justified by the concrete violated contract/invariant,
  failure scenario and impact; severity or preference alone does not block.
- File and tight line reference.
- Violated requirement, invariant, or project rule.
- Concrete failure scenario and impact.
- Smallest sound remediation and verification command.

Distinguish confirmed defects from questions. Do not report style preferences
without a project rule or maintainability consequence. If no findings remain,
say so and list any checks not run or residual risk.

When a dispatched slice had to redo research the plan should have carried, report
the thin 上下文包 as a process finding: naming the missing field is enough to fix
the next plan.

Return one closing status: `REVIEW_STATUS: FINDINGS` for blocking defects;
`REVIEW_STATUS: CLEAN` for no blocking defects with sufficient evidence and
coverage (non-blocking suggestions may remain); `REVIEW_STATUS: INVALID` only
when no valid review was possible. State the full/focused mode, prior report,
reviewed inputs, resolved/remaining finding IDs, checks and coverage gaps.

Return findings to the main session. The main session applies fixes, re-runs
affected checks, and records the final review result in `artifacts/verification.md`.
A reviewer must not commit, push, archive the change, or claim final delivery.
