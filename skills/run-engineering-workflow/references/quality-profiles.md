# Quality Profiles

Risk may add checks. It never excuses an available check that directly proves
changed behavior.

## Lightweight

Use for documentation, local configuration, or an isolated low-risk change.

- Review scope and `git diff`.
- Run the smallest relevant runnable check.
- Add a regression test for any behavior change when a suitable seam exists.
- Independent review is optional for non-behavioral changes.

## Standard

Use for normal features, bug fixes, and refactors.

- Capture RED/GREEN evidence.
- Run targeted tests, lint, typecheck, and the relevant build.
- Review project specs and the final diff, with Matt `code-review` for the
  Standards-versus-Spec axis.
- Run one independent correctness and complexity review through
  `review-implementation` or `workflow-reviewer`. Do not run both by default.
- Re-run affected checks after fixes or simplification.

## Critical

Use for authentication, authorization, money, secrets, persistent data,
migrations, public contracts, or destructive operations.

- Run all standard checks.
- Add integration coverage and the full relevant suite.
- Run security and data/migration review as applicable.
- Verify rollback and affected critical-path E2E behavior.
- Use an independent reviewer and escalate uncertain implementation work from
  `@task` to `@default` or `@slow` in OMP.

Coverage percentages are diagnostic evidence, not a substitute for testing the
right behavior through a stable public seam.
