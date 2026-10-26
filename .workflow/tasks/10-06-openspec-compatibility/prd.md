# OpenSpec 兼容改造

## 状态

- STATUS: planning
- PROFILE: critical
- 目标：让 OpenSpec 成为新任务、规格和变更生命周期的唯一事实源，同时保留旧 `.workflow/` 的恢复能力和 `.trellis/` 的只读兼容能力。

## 背景

本仓库当前以 `.workflow/` 作为任务状态和长期记录系统，并通过 `run-engineering-workflow` 路由需求澄清、方案设计、TDD、独立复核、验证证据和用户验收。当前设计明确不使用 Trellis CLI、hooks、extension 或每轮上下文注入。

用户已选择：

1. 以 OpenSpec 完整替换当前新任务记录系统，而不是只做格式导入导出。
2. 保留旧 `.workflow/` 记录的可恢复能力。
3. 保留旧 `.trellis/` 的只读读取能力。

## 目标

- 新任务在 `openspec/` 下创建、推进、归档。
- OpenSpec 的 `specs/` 和 `changes/` 成为新任务的规格与变更事实源。
- 当前仓库保留自己的风险路由、TDD 约束、独立 review、验证证据和用户验收边界。
- 新会话能够只通过 OpenSpec 状态和变更目录恢复当前任务。
- 旧 `.workflow/` 可以被识别、读取并显式迁移到 OpenSpec；迁移不能静默发生，也不能产生双写。
- 旧 `.trellis/` 只读，不调用其脚本，不安装其注入器，不修改其内容。
- Codex、Claude Code、OMP、Pi 的安装和入口保持可用，并增加 OpenSpec 前置检查。

## 非目标

- 不实现 OpenSpec CLI 本身。
- 不维护一套与 OpenSpec 平行的 `.workflow/` 新任务状态机。
- 不恢复每轮 head-of-input 状态注入。
- 不把 OpenSpec 的命令、skill 或内部源码 vendor 到本仓库。
- 不在本次改造中自动迁移所有历史 `.workflow/` 任务。
- 不自动归档任务；用户验收仍然是完成条件。

## 兼容规则

- 存在 `openspec/` 时，新任务路由到 OpenSpec canonical mode。
- 只有不存在 OpenSpec 新任务且发现旧 `.workflow/` 指针或任务目录时，才进入 legacy workflow mode。
- `.workflow/` legacy mode 只允许读取和恢复；要继续产生新任务记录，必须执行显式迁移，生成一个 OpenSpec change。
- `.trellis/` 只允许读取同名历史产物；禁止执行 Trellis 脚本、写入 `.trellis/` 或重新安装 Trellis injector。
- 同一个事实只能有一个权威来源；迁移后 OpenSpec change 是权威来源，旧任务仅作为迁移来源和历史证据。

## 验收标准

- [ ] AC-001 新任务默认创建 OpenSpec change，不创建新的 `.workflow/tasks/<id>/` 任务记录。
- [ ] AC-002 OpenSpec change 至少覆盖 proposal、spec delta、design、tasks、上下文包和验证证据的完整生命周期。
- [ ] AC-003 主路由可以从 OpenSpec 状态恢复当前任务，且不依赖聊天摘要、hook 注入或隐式扫描多个任务目录。
- [ ] AC-004 旧 `.workflow/` 任务可以被识别并以 legacy mode 恢复；系统不会把它误当成 OpenSpec 新任务。
- [ ] AC-005 旧 `.workflow/` 到 OpenSpec 的迁移必须显式触发、可验证、幂等，并在失败时保留原记录不变。
- [ ] AC-006 旧 `.trellis/` 可以读取 `prd.md`、`design.md`、`implement.md` 和 `outcome.md` 等同名产物，但不会调用脚本或写入目录。
- [ ] AC-007 现有 critical/standard/lightweight 风险路由、TDD、独立 review、验证证据和用户验收边界继续有效。
- [ ] AC-008 Codex、Claude Code、OMP、Pi 的安装器、doctor、入口 skill 和 agents 都能识别 OpenSpec 依赖与项目初始化状态。
- [ ] AC-009 OpenSpec CLI 缺失、版本不满足或项目未初始化时，系统给出可操作的 INVALID/BLOCKED 结果，不静默退回旧新混合模式。
- [ ] AC-010 合同测试覆盖 canonical、legacy workflow、legacy Trellis、迁移失败和安装检查路径。
- [ ] AC-011 文档明确新的事实源、旧记录策略、迁移命令、回滚方式和各客户端入口。
- [ ] AC-012 完成实现后，独立 review、仓库检查和真实验证命令结果都写入 OpenSpec change 的验证证据文件，任务停在 `awaiting-acceptance`，不自动归档。

## 验收者需要确认

- OpenSpec CLI 的最低版本和 Node.js 版本要求是否固定在项目规范中。
- 是否接受在 OpenSpec change 根目录增加项目自定义的 `context.md` 和 `verification.md` 产物。
- 迁移后的旧 `.workflow` 任务是否保留原目录不动，并通过迁移报告建立来源映射。
