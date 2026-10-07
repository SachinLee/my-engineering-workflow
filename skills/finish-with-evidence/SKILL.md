---
name: finish-with-evidence
description: Verify a completed software task and record factual implementation evidence in the active OpenSpec change's artifacts/verification.md. Use after code changes, before closing or handoff, and whenever future AI sessions need to know what was implemented and validated.
---

# Finish With Evidence

Close the gap between the planned solution and the implementation that actually
shipped. Write results to the active OpenSpec change's `artifacts/verification.md`,
in the user's language (Chinese by default); keep code identifiers, paths, commands,
and log text verbatim. Status tokens (`PASS`, `NOT RUN`, `UNVERIFIED`,
`NOT APPLICABLE`, `NOT CAPTURED`, `NOT COMMITTED`) stay in English so they remain
greppable.

## Verify

1. Read the active OpenSpec change's `proposal.md`, `specs/`, `design.md`,
   `tasks.md`, `artifacts/context.md`, and the selected quality profile.
2. Inspect `git status` and `git diff`. Identify unrelated changes and leave them
   untouched.
3. Run Matt `code-review` as the Standards-versus-Spec axis: does the diff follow
   the project's documented standards, and does it deliver what `proposal.md` and
   the change specs asked?
4. Run relevant repository verification: targeted tests, type checking, lint, build,
   security review, migration checks, or E2E based on risk and available tools.
5. Confirm that `review-implementation` ran from an independent context for
   standard behavior changes and critical work. In OMP, use `workflow-reviewer` on
   `@advisor`; do not substitute the `@task` implementer's self-review. In Claude
   Code, use this repository's read-only `workflow-reviewer` on Opus after
   `code-review` and repository checks. Resolve material findings and re-run
   affected checks before continuing.
6. For behavior changes, capture real RED and GREEN evidence from the relevant test
   target when available. Mark missing RED evidence explicitly.
7. Apply `ponytail-review` after correctness checks to find deletable complexity.
   Re-run affected checks after simplification.
8. Confirm every task marked `done` in `tasks.md` matches the diff and evidence, and
   state which tasks remain on the frontier.
9. Decide whether a reusable convention, prevention rule, or non-obvious lesson
   belongs in `openspec/specs/`, `CONTEXT.md`, or `docs/adr/`. Record a pointer in
   the verification artifact instead of copying the text.

Do not invent commands, output, coverage, commits, or PASS results. Use `NOT RUN`,
`UNVERIFIED`, or `NOT APPLICABLE` when evidence is unavailable.

## Write Verification

Create or update `artifacts/verification.md` in the active OpenSpec change:

```markdown
# 交付验证

## 交付
- 状态：complete | partial | blocked
- 概述：用可观测的语言说明改了什么

## 验收标准
| 标准 | 结果 | 证据 |
| --- | --- | --- |
| AC-001 | PASS | 测试名或可复现的手工证据 |

## 实现
- 主要改动路径
- 关键设计决策
- 与 design.md 的偏差及原因

## TDD 证据
- RED：命令与相关失败，或 NOT CAPTURED
- GREEN：命令与相关通过结果

## 验证
- 确切命令与结果

## 独立复核
- 复核者角色或模型上下文
- 已解决的 findings
- 修复后重复执行的检查

## 提交
- 工作提交哈希，或 NOT COMMITTED

## 剩余风险
- 已知缺口、延后事项，以及明确的升级触发条件

## 验收
- 状态：待用户验收
- 验证清单：每条 AC 对应的命令或手工步骤
- 未运行的检查：NOT RUN 项及其原因
```

Make the acceptance-criteria table exhaustive: one row for every AC in the active
The verification table has one row for every `- [ ] AC-NNN` acceptance criterion in the active OpenSpec proposal/specs.
OpenSpec proposal/specs, none omitted. Any criterion left unchecked carries an
explicit reason and an upgrade trigger. Keep the verification artifact factual and
concise. Link to code, tests, ADRs, or commits instead of copying their content.

## Hand Off For Acceptance

If work is incomplete, record the blocker and next executable step rather than
claiming completion.

You do not accept the work, and you do not archive the OpenSpec change. Once the
evidence above is recorded:

1. Set the change handoff status to `awaiting-acceptance` in `tasks.md` or the
   repository's approved OpenSpec status mechanism, with the current timestamp.
2. In your reply, give the verification list: every AC with the exact command or
   manual step that proves it, every check left `NOT RUN`, and the residual risks.
3. Print the archival command from
   [workflow-governance.md](../run-engineering-workflow/references/workflow-governance.md)
   so the user can run it, or say that you will run it on request.

Do not move the OpenSpec change into `openspec/changes/archive/`, do not append a
journal line, do not delete compatibility pointers, and do not archive the change.

If the user verifies and finds a problem, treat that as a normal transition: update
`tasks.md`, fix the implementation, re-run the affected checks, and append a new
round to `artifacts/verification.md` under `## 复验轮次 N`. Leave earlier rounds
untouched, so what was claimed and when it was corrected stays visible.

When the user has accepted and explicitly asks to archive, invoke `archive-task`
instead of doing it inline here; that skill owns the archive move and compatibility
cleanup.
