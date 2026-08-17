---
name: review-implementation
description: Independently review a completed implementation against the active Trellis requirements, project rules, tests, security constraints, and complexity budget. Use after implementation and before final evidence, especially when a different AI model or fresh context should challenge correctness claims.
---

# Review Implementation

Review from a fresh context when the platform supports it. Do not implement the
change under review and then approve it in the same pass.

## Establish The Contract

1. Read the active `prd.md`, optional `design.md`, optional `implement.md`, and
   applicable `.trellis/spec/` and ADRs.
2. Inspect `git status`, the complete relevant diff, adjacent code, and tests.
3. Separate current-task changes from unrelated user or concurrent changes.
4. Map every required acceptance criterion to code and executable evidence.

## Review In Order

1. Correctness: find missed ACs, regressions, boundary errors, concurrency
   hazards, failure-path defects, and incorrect assumptions.
2. Tests: check that assertions prove public behavior, include meaningful
   negative paths, and would fail for the defect they claim to prevent.
3. Security and data integrity: inspect input boundaries, authorization,
   secrets, injection, destructive behavior, persistence, migrations, and
   rollback when applicable.
4. Project compliance: compare the change with `AGENTS.md`, Trellis specs,
   established local patterns, and public contracts.
5. Maintainability and complexity: identify unnecessary abstraction,
   duplication, dependencies, configuration, compatibility paths, and dead code
   without weakening required safeguards.
6. Evidence: run the smallest commands needed to confirm or reject material
   findings. Never turn an unexecuted check into a PASS.

## Report Findings

Lead with actionable findings ordered by severity. For each finding include:

- Severity: `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`.
- File and tight line reference.
- Violated requirement, invariant, or project rule.
- Concrete failure scenario and impact.
- Smallest sound remediation and verification command.

Distinguish confirmed defects from questions. Do not report style preferences
without a project rule or maintainability consequence. If no findings remain,
say so and list any checks not run or residual risk.

Return findings to the main session. The main session applies fixes, re-runs
affected checks, and records the final review result in `outcome.md`. A reviewer
must not commit, push, archive the task, or claim final delivery.
