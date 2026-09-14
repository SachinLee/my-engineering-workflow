---
name: finish-with-evidence
description: Verify a completed software task and record factual implementation evidence in the active Trellis task. Use after code changes, before archival or handoff, and whenever future AI sessions must know what was actually implemented and validated.
---

# Finish With Evidence

Close the gap between the planned solution and the implementation that actually
shipped. Write results to the active task's `outcome.md`.

## Verify

1. Read `prd.md`, optional `design.md`, optional `implement.md`, applicable
   `.trellis/spec/`, and the selected quality profile.
2. Inspect `git status` and `git diff`. Identify unrelated changes and leave
   them untouched.
3. Run `trellis-check` for spec compliance and repository checks.
4. Run relevant repository verification: targeted tests, type checking, lint, build,
   security review, migration checks, or E2E based on risk and available tools.
5. Confirm that `review-implementation` ran from an independent context for
   standard behavior changes and critical work. In OMP, use
   `workflow-reviewer` on `@advisor`; do not substitute the `@task`
   implementer's self-review. In Claude Code, use this repository's read-only
   `workflow-reviewer` on Opus after the native Trellis `trellis-check`.
   Resolve material findings and re-run affected checks before continuing.
6. For behavior changes, capture real RED and GREEN evidence from the relevant
   test target when available. Mark missing RED evidence explicitly.
7. Apply `ponytail-review` after correctness checks to find deletable complexity.
   Re-run affected checks after simplification.
8. Review whether `trellis-update-spec` should promote a reusable convention,
   prevention rule, or non-obvious lesson into `.trellis/spec/`.

Do not invent commands, output, coverage, commits, or PASS results. Use `NOT RUN`,
`UNVERIFIED`, or `NOT APPLICABLE` when evidence is unavailable.

## Write Outcome

Create or update `outcome.md` with:

```markdown
# Outcome

## Delivery
- Status: complete | partial | blocked
- Summary: what changed in observable terms

## Acceptance Criteria
| Criterion | Result | Evidence |
| --- | --- | --- |
| AC-001 | PASS | test name or manual evidence |

## Implementation
- Main code paths changed
- Important design decisions
- Deviations from design.md and why

## TDD Evidence
- RED: command and relevant failure, or NOT CAPTURED
- GREEN: command and relevant passing result

## Verification
- Exact commands and results

## Independent Review
- Reviewer role or model context
- Findings resolved
- Checks repeated after remediation

## Commits
- Work commit hashes, or NOT COMMITTED

## Remaining Risk
- Known gaps, deferred work, and explicit upgrade triggers
```

Keep `outcome.md` factual and concise. Link to code, tests, ADRs, or commits
instead of copying their content.

## Hand Off

If work is incomplete, record the blocker and next executable step rather than
claiming completion. Archive and journal only through the local Trellis finish
workflow and only after its permission and clean-worktree requirements are met.
