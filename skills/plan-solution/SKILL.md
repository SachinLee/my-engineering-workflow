---
name: plan-solution
description: Design a traceable technical solution and execution plan for an active .workflow task. Use after requirements are clarified and before implementation, especially for behavior changes, multi-file work, public interfaces, data flow, migrations, security-sensitive work, or tasks another AI session must execute.
---

# Plan Solution

Turn an accepted `prd.md` into an implementation-ready solution. Keep
technical decisions in `design.md`, ordered execution in `implement.md`, and the
dispatch context in `context.md`. Do not implement production code while using
this skill. Write the artifacts in the user's language (Chinese by default);
keep code identifiers, paths, commands, and log text verbatim.

When OMP is available, run this skill in the `workflow-planner` agent on the
`@plan` role. In Claude Code, use this repository's `workflow-planner` agent on
Opus. Requirement questions still return to the interactive main session; the
planning agent must not guess product intent.

## Confirm Readiness

1. Read `prd.md`, related code and tests, applicable project specs
   (`.workflow/spec/`, or `.trellis/spec/` in a legacy repository), and prior
   ADRs before designing.
2. Verify that 目标, 范围内, 范围外, 假设, and 验收标准 are explicit.
3. If a decision still changes required behavior or scope, return to
   `clarify-requirements`. Do not hide a requirement question inside a technical
   plan.
4. Select the `lightweight`, `standard`, or `critical` quality profile.

## Find The Smallest Sound Design

Before proposing new code, check in order:

1. Existing project behavior, helpers, modules, and conventions.
2. Standard library and native platform capabilities.
3. Already-installed dependencies.
4. The smallest new module or interface that owns the behavior correctly.

Use Matt-style deep-module reasoning when a boundary is changing: identify the
public interface, invariants, error modes, and test seam. Prefer one deep module
over multiple pass-through layers. Simplicity cannot remove required security,
data integrity, compatibility, observability, accessibility, or rollback.

## Write design.md

For standard work, create `design.md` when the task changes an interface, data
flow, module boundary, persistence model, or meaningful technical decision.
For critical work, `design.md` is required. Use Chinese headings and keep only
the sections that apply:

- 背景与现状
- 方案与改动边界
- 组件与职责
- 公开接口与不变量
- 数据流与状态迁移
- 错误处理与失败模式
- 安全与隐私
- 兼容性与迁移
- 可观测性
- 备选方案与否决理由
- 发布与回滚
- 未决技术风险
- 验收追溯（AC → 设计点）

Do not copy acceptance criteria into `design.md`; reference their IDs. Create an
ADR only for a hard-to-reverse and surprising decision produced by a real
tradeoff, then link it instead of duplicating its rationale.

## Write implement.md

For standard and critical work, create an ordered `implement.md`. Organize work
as vertical slices that leave the repository verifiable after each slice. Use
this shape per slice:

```markdown
### 切片 N：AC-XXX - <标题>

- 行为：本片交付的可观测结果
- 代码边界：预期会改动的模块或接口
- 测试接缝：用来证明行为的公开边界
- RED：目标测试与预期失败
- 实现：最小生产改动
- GREEN：目标通过命令
- 验证：lint、typecheck、集成、构建或手工检查
- 依赖：前置切片或外部决策
- 回滚：如何安全移除或关闭本片
```

Map every required acceptance criterion to at least one slice or an explicit
non-code verification step. Do not use `AC-001` as a placeholder when the PRD
has different IDs.

## Write The Context Package

Every slice that can be dispatched must carry a 上下文包 written at planning
time, so a fresh subagent starts from conclusions instead of repeating the
main session's investigation. The rule is simple: **what the main session has
already read and reasoned about gets inlined; only files the worker must newly
open stay as paths.**

```text
Active task: .workflow/tasks/<task-id>/
Assigned slice: 切片 N / AC-XXX
Phase: implement

已内联上下文（子代理不需要再读原文）：
- 验收标准：<把本片 AC 整条贴进来>
- 相关设计决策：<design.md 对应小节的关键原文>
- 已定位：<file:line> + 符号 + 结论（例：XxxServiceImpl.java:212 handleHeartbeat 用部分实体调用 dao.update(entity, wrapper)）
- 现成模式：可直接照抄结构的实现或测试文件，附关键片段
- 不变量：本片必须保持的行为
- 验证命令：确切命令，含 JDK、离线、模块参数，以及预期输出要点

需要新打开（只列真正要读的）：
- path/to/production-file
- path/to/test-file

允许修改：
- path/to/production-file
- path/to/test-file
禁止修改：
- 实体注解、mapper/XML、配置、数据库、其他 task 目录、STATUS 与指针文件
升级条件：
- 需要越出允许范围，或内联结论与磁盘不符时，停止并报告差异
返回证据：
- 改动文件、RED/GREEN 命令与结果、未运行的检查、剩余风险
```

Keep the package under roughly 1,500 tokens per slice. When the source material
is longer, inline the decisive lines and cite the file rather than pasting it.
A slice without a context package is planned for a main-session edit, not for
dispatch.

## Decompose The Work

Choose the smallest split level that matches how the work will actually be
executed:

| 级别 | 用在什么时候 | 落在哪里 |
| --- | --- | --- |
| 切片 | 同一会话内顺序完成，共享模块，一个 writer | `implement.md` 的 `### 切片 N` |
| 工单 | 每片可独立验收、需要跨会话续接、或多 writer 并行推进 | `.workflow/tasks/<task-id>/tickets/NN-<slug>.md` |
| 多任务 | 不同发布单元、不同仓库、或可独立交付收口的成果 | 各自 `.workflow/tasks/<id>/`，由一个总控 task 记 `prd.md` 与子任务清单 |

Do not split `lightweight` work, a single test seam, or a change confined to one
or two files. Splitting is a scheduling decision, not a documentation goal.

For the 工单 level, one file per ticket:

```markdown
---
id: T2
标题：摄像头状态 CAS 更新
covers: [AC-001]
blocked_by: [T1]
state: ready          # ready | in_progress | done | blocked
writer: main          # main | workflow-implementer
---

范围、入口文件、验收与验证命令；细节直接引用 `implement.md#切片-3` 与其上下文包。
```

The frontier is the set of `ready` tickets whose `blocked_by` are all `done`.
Advance one ticket per writer; on completion set `state: done`, then record the
evidence in `outcome.md`. Use Matt `to-tickets` to draft this list, but write the
result inside the task directory — never into `.scratch/` or a second tracker.

## Write context.md

Nothing is injected into a subagent automatically, so record the read list that
dispatch depends on. One row per file, with a one-line Chinese reason:

```text
- .workflow/spec/gateway/billing.md — 价格规则只增不改；迁移不重写历史
- docs/adr/0012-cost-source.md — provider 实际费用优先于本地估算
- crates/service/src/quota/model_pricing.rs — 当前价格解析入口
```

Keep paths and reasons only. Never paste file bodies into `context.md`: they go
stale, and a reader can read the source. When resuming a legacy task that has an
`implement.jsonl` or `check.jsonl` manifest, convert it here once.

## Lightweight Planning

For documentation, configuration, or an isolated low-risk change, the task may
remain PRD-only. Record an explicit solution sketch, affected files, runnable
check, and the reason `design.md` / `implement.md` are unnecessary in `prd.md`.
Skipping files is allowed; skipping the planning decision is not.

## Review The Plan

Before handing off:

- Confirm every required AC has implementation or verification coverage.
- Confirm expected changed files are inside the declared scope.
- Confirm test seams exercise public behavior rather than internals.
- Confirm dependency ordering, migration, rollout, and rollback where relevant.
- Confirm every dispatchable slice has a context package with inlined AC text,
  located code, and the exact verification command.
- Challenge speculative abstractions, dependencies, configuration, and fallback
  paths through Ponytail's simplicity ladder.
- Record unresolved technical risk instead of presenting guesses as decisions.

Finish by summarizing the selected profile, artifacts written, major decisions,
and whether the task is ready to enter `in_progress`. List `context.md` among the
artifacts written; a plan without a read list cannot be dispatched safely.
