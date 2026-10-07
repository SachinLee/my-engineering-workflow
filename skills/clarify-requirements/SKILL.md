---
name: clarify-requirements
description: Convert an ambiguous software request into scoped, observable acceptance criteria in the active OpenSpec change's proposal.md and specs/. Use before planning complex work, when business intent is unclear, or when another AI session needs a reliable requirement handoff.
---

# Clarify Requirements

Improve the active OpenSpec change's `proposal.md` and `specs/`; do not create a second specification.
Combine codebase discovery, Matt-style grilling, and observable acceptance
criteria. Write the artifact in the user's language (Chinese by default); keep
code identifiers, paths, commands, and log text verbatim.

## Clarify

1. Read the current request, active OpenSpec change, related code, tests, specs, and prior
   decisions before asking technical questions.
2. Separate discovered technical facts from product assumptions. Never infer a
   business rule only from code or naming.
3. Ask one question at a time. Ask only when the answer materially changes
   behavior, scope, risk, compatibility, or verification.
4. Challenge overloaded domain terms. If a stable glossary exists, use it; if
   a term is newly resolved, propose a focused `CONTEXT.md` update.
5. Stop questioning when the requested outcome is observable and the remaining
   assumptions are safe to record.

## Write OpenSpec Requirements

Keep the requirement sections in `proposal.md`, with Chinese headings; put normative behavior in `specs/<capability>.md`:

- 目标
- 现状与问题
- 范围内
- 范围外
- 角色与受影响系统
- 假设与约束
- 领域术语（相关时）
- 验收标准
- 未决与阻塞决策

Write acceptance criteria as `AC-001`, `AC-002`, and so on, each with a
checkbox title line — `- [ ] AC-001: <标题>` — with its details indented below, so
`artifacts/verification.md` can close them one by one. Every criterion names the 场景,
动作, expected 可观测结果, 禁止副作用 when meaningful, and 验证方法. A criterion
without a checkbox cannot be verified or reported as delivered.
After clarification, record the accepted execution boundary and verification checkpoints in `tasks.md`; keep the dispatch file map in `artifacts/context.md`.

Example:

```markdown
- [ ] AC-001: 拒绝越权导出
  - 场景：已登录用户请求导出属于其他账号的数据
  - 动作：提交导出请求
  - 期望：返回仓库既有的标准禁止响应
  - 不得：泄露该账号是否存在
  - 验证方法：API 集成测试
```

## Escalate By Risk

- Use proposal-only planning for a small, well-understood change.
- Add `design.md` when interfaces, data flow, compatibility, security, rollout,
  or meaningful alternatives need an explicit decision.
- Use `tasks.md` and `artifacts/context.md` when ordering, checkpoints, validation
  commands, bounded dispatch, or rollback steps matter.
- Add an ADR only for a hard-to-reverse, surprising decision made through a real
  tradeoff. Link it from `design.md`; do not duplicate its rationale.

## Finish

Report confirmed requirements, recorded assumptions, and any blockers. Do not
start risky or irreversible implementation while a blocking decision remains.
When this clarification creates a change, ensure `proposal.md`, relevant `specs/`,
`design.md` when required, and `artifacts/context.md` are present and the change's
OpenSpec status is discoverable. Legacy `.workflow` pointers may be updated only for
explicit recovery metadata; new requirements and state belong in OpenSpec.
