---
name: finish-with-evidence
description: Consume existing verification and independent review evidence, report simple fast-path work directly or record formal delivery in the active OpenSpec change's artifacts/verification.md. Use after code changes, before closing or handoff, and whenever future AI sessions need to know what was implemented and validated.
---

# Finish With Evidence

## Fast Path Exit

If the main router has already selected [Simple Work Fast Path](../run-engineering-workflow/references/quality-profiles.md#simple-work-fast-path),
return existing changes/checks, `NOT RUN` items and risks to the main router for a
conversational handoff. Do not create task records or verification artifacts, run
checks, dispatch reviewers, or backfill a change just to close this request.
Formal work is not silently downgraded here; a missing fast-path decision returns
to router selection rather than implying eligibility. The formal steps below
require a selected change and do not apply to eligible fast work.

Close the gap between the planned solution and the implementation that actually
shipped. Write results to the active OpenSpec change's `artifacts/verification.md`,
in the user's language (Chinese by default); keep code identifiers, paths, commands,
and log text verbatim. Status tokens (`PASS`, `NOT RUN`, `UNVERIFIED`,
`NOT APPLICABLE`, `NOT CAPTURED`, `NOT COMMITTED`) stay in English so they remain
greppable.

## Consume Evidence

The main router is the only scheduler. Do not dispatch reviewers and do not run
repository verification directly from this skill; consume recorded evidence.

1. Read the selected change's proposal/specs, tasks and verification/review records
   with the shared `quality-profiles.md` budget. Read design/context only as needed
   to resolve a traceability gap, not to repeat the design or implementation review.
2. Inspect `git status` and the relevant `git diff` to identify final input changes and
   unrelated user work. Match the evidence's staged, unstaged and explicitly named
   untracked scope to final contents; do not perform a second full code review.
3. Consume same-change/same-material executed tests, lint, typecheck, build and
   risk-specific evidence. For Standard / Critical require the independent
   `workflow-reviewer` report with Standards / Spec, correctness/security/tests/
   complexity coverage; local repairs also require the budgeted focused follow-up
   and affected checks. The prior full report alone cannot approve unaudited repairs.
   Lightweight consumes its host-native focused check, without a formal reviewer.
4. Check full/focused rounds, unresolved blockers and the final coverage chain.
   Missing or stale evidence, unavailable independent review, incomplete scope or
   conflicting round history: record `UNVERIFIED` and return the precise gap to
   the main router for affected checks or a budgeted/user-authorized next step.
   Do not claim `CLEAN` or normal completion while a required gate is unsatisfied.
   Appending the report or delivery evidence does not invalidate matching evidence
   unless a substantive reviewed input changes. Entering finish adds no review.
5. Record existing RED/GREEN evidence, commands/results and all AC outcomes; mark
   missing RED evidence `NOT CAPTURED`, not an invented execution.
6. Confirm completed tasks match evidence and identify the remaining frontier.
   Record reusable conventions by pointer in `openspec/specs/`, `GLOSSARY.md` (or
   a user-confirmed existing `CONTEXT.md`) or `docs/adr/` only when warranted.

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
- 已批准交付范围、完整/定向审核轮数及模式
- 复核者角色或模型上下文、报告与最终材料的覆盖关系
- 阻断 findings 的解决情况与非阻断建议
- 修复检查的既有执行证据；缺口返回主路由，不在收尾补跑

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

You do not accept the work, and you do not archive the OpenSpec change. Only when the
required checks and review gate are satisfied and evidence is recorded:

1. Set the change handoff status to `awaiting-acceptance` in `tasks.md` or the
   repository's approved OpenSpec status mechanism, with the current timestamp.
2. In your reply, give the verification list: every AC with the exact command or
   manual step that proves it, every check left `NOT RUN`, and the residual risks.
3. Print the archival command from
   [workflow-governance.md](../run-engineering-workflow/references/workflow-governance.md)
   so the user can run it, or say that you will run it on request.

Do not move the OpenSpec change into `openspec/changes/archive/`, do not append a
journal line, do not delete compatibility pointers, and do not archive the change.

If the user verifies and finds a problem, return it to the main router: preserve
prior rounds, update `tasks.md`, apply fixes and affected checks through that router,
and follow the shared budget's focused/reauthorization rules rather than resetting
rounds. Record the new evidence under `## 复验轮次 N` in
`artifacts/verification.md`; leave earlier rounds untouched.

When the user has accepted and explicitly asks to archive, invoke `archive-task`
instead of doing it inline here; that skill owns the archive move and compatibility
cleanup.
