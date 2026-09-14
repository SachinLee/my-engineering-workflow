---
name: finish-with-evidence
description: Verify a completed software task and record factual implementation evidence in its outcome.md under .workflow/. Use after code changes, before closing or handoff, and whenever future AI sessions must know what was actually implemented and validated.
---

# Finish With Evidence

Close the gap between the planned solution and the implementation that actually
shipped. Write results to the active task's `outcome.md`.

## Verify

1. Read `prd.md`, `STATUS`, `context.md`, optional `design.md`, optional
   `implement.md`, applicable
   specifications, and the selected quality profile.
2. Inspect `git status` and `git diff`. Identify unrelated changes and leave
   them untouched.
3. Run Matt `code-review` as the Standards-versus-Spec axis: does the diff follow
   the project's documented standards, and does it deliver what `prd.md` asked?
4. Run relevant repository verification: targeted tests, type checking, lint, build,
   security review, migration checks, or E2E based on risk and available tools.
5. Confirm that `review-implementation` ran from an independent context for
   standard behavior changes and critical work. In OMP, use
   `workflow-reviewer` on `@advisor`; do not substitute the `@task`
   implementer's self-review. In Claude Code, use this repository's read-only
   `workflow-reviewer` on Opus after `code-review` and the repository checks.
   Resolve material findings and re-run affected checks before continuing.
6. For behavior changes, capture real RED and GREEN evidence from the relevant
   test target when available. Mark missing RED evidence explicitly.
7. Apply `ponytail-review` after correctness checks to find deletable complexity.
   Re-run affected checks after simplification.
8. Decide whether a reusable convention, prevention rule, or non-obvious lesson
   belongs in `.workflow/spec/`. Write it there, or route it to `CONTEXT.md` or
   `docs/adr/` when it is vocabulary or a hard-to-reverse decision. Record a
   pointer to it in `journal.md` rather than repeating the text.

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

Make the acceptance-criteria table exhaustive: one row for every `- [ ] AC-NNN`
in `prd.md`, none omitted, and any criterion left unchecked carries an explicit
reason and an upgrade trigger. Then tick the checkbox in `prd.md` only for rows
that show PASS with executed evidence. Keep `outcome.md` factual and concise.
Link to code, tests, ADRs, or commits instead of copying their content.

## Hand Off

If work is incomplete, record the blocker and next executable step rather than
claiming completion.

## Close The Record

Only after `outcome.md` is complete, every required check has executed evidence or
an explicit `NOT RUN`, and the repository's commit permission is satisfied:

1. Set `STATUS` to `phase: done` with the current timestamp.
2. Append one line to `.workflow/journal.md`: date, task path, one-sentence
   outcome, and the commit or branch that carries it.
3. Move the task directory to `.workflow/archive/`, then delete this session's
   pointer file. Point `CURRENT.md` at the next real task, or clear it.
4. Confirm `.workflow/tasks/` no longer lists the closed task.

Never delete an archived task or rewrite its artifacts afterwards. A corrected
conclusion belongs in a new task that references the archive.
