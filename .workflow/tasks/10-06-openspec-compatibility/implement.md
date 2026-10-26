# 实施规划

## 执行门槛

本任务为 `critical`。在用户批准本方案前不得修改实现文件。

实现顺序遵循：合同测试先行 → 外部 OpenSpec 契约确认 → canonical 路由 → legacy 兼容/迁移 → 适配四个平台 → 文档和回归验证 → 独立 review。

每个切片完成后必须运行该切片的验证命令，并把真实结果写入对应 OpenSpec change 的 `verification.md`。一个切片只能有一个 writer。

## 切片 0：冻结外部 OpenSpec 契约

**目标**：在改路由前确认 CLI 版本、JSON 输出、artifact 行为和四个平台的命令生成方式。

**上下文包**

- 验收标准：AC-002、AC-008、AC-009。
- 设计决策：OpenSpec 是新任务 canonical；本仓库不 vendor CLI；缺失依赖必须 BLOCKED，不能静默创建新 `.workflow`。
- 已定位：`README.md` 的“基础环境”“各客户端入口”“OMP 多模型工作流”“Pi 工作流”章节；OpenSpec 官方 README 的 Quick Start、OPSX workflow、supported tools 和 Node.js 20.19.0 要求。
- 现成模式：`scripts/doctor.py` 的环境检查；`scripts/doctor.ps1` 的平台包装；`tests/contracts.test.js` 的合同检查。
- 不变量：不执行生产迁移，不写 `.trellis/`，不改用户已有 `.workflow/`。
- 验证命令：`openspec --version`、`openspec status --json`、`openspec instructions --json`、`openspec --help`；结果和版本写入 `verification.md`。
- 需要打开：`README.md`、`scripts/doctor.py`、`tests/contracts.test.js`、OpenSpec 官方 `docs/cli.md`、`docs/opsx.md`、`docs/supported-tools.md`。

**产出**

- 明确支持的 OpenSpec CLI 版本范围。
- 固定 status/instructions JSON 的最小字段契约。
- 确定自定义 `context.md`、`verification.md` 的保存位置和 archive 行为。
- 若外部契约不稳定，设计一个版本化 adapter，不直接解析人类可读输出。

## 切片 1：先加 canonical/legacy 合同测试

**目标**：在改变路由之前，锁定四种项目状态和禁止行为。

**上下文包**

- 验收标准：AC-001、AC-003、AC-004、AC-005、AC-006、AC-009、AC-010。
- 设计决策：优先级为 `OpenSpec canonical > .workflow legacy recovery > .trellis read-only`；多个活动 change 返回 BLOCKED。
- 已定位：`tests/contracts.test.js`；相关受测文本为 `skills/run-engineering-workflow/SKILL.md`、`skills/run-engineering-workflow/references/workflow-governance.md`、`scripts/install.ps1`、`scripts/doctor.py`。
- 现成模式：当前合同测试对安装器、入口 skill、旧 Trellis 禁止项和跨平台资源做静态断言。
- 不变量：测试不得依赖真实用户目录；所有 fixture 使用临时目录；迁移失败后来源字节必须相同。
- 验证命令：`npm test`；新增的迁移/状态 fixture 测试必须可单独运行。
- 需要打开：`tests/contracts.test.js` 全文和 `package.json` 的 test script。

**产出**

- canonical OpenSpec fixture。
- 旧 `.workflow` fixture。
- 旧 `.trellis` fixture。
- 缺 CLI、未初始化、多个活动 change、迁移失败和成功迁移 fixture。
- 对 `.trellis` 写入/脚本执行和新建 `.workflow/tasks` 的禁止断言。

## 切片 2：实现 OpenSpec 状态适配与显式迁移

**目标**：用结构化 OpenSpec CLI 输出解析当前 change，并提供不修改来源的旧 `.workflow` 迁移。

**建议文件边界**

- 新增：`scripts/openspec_compat.py` 或等价的最小适配模块。
- 修改：`scripts/doctor.py`、`tests/contracts.test.js`。
- 不修改：用户的 `.workflow/`、`.trellis/` 和任何未声明 fixture。

**上下文包**

- 验收标准：AC-003、AC-004、AC-005、AC-006、AC-009、AC-010。
- 设计决策：迁移采用 copy-transform-verify；来源不可变；迁移报告写入目标 change；不允许双写。
- 已定位：`scripts/doctor.py` 的环境检查入口、`tests/contracts.test.js` 的临时目录工具；旧产物映射见 `design.md` 的“事实源与状态映射”。
- 现成模式：Python 负责环境和文件系统检查，Node 合同测试负责跨平台契约；不要引入第三套运行时。
- 不变量：路径必须限定在项目根目录；禁止命令拼接注入；CLI 返回非零或 JSON 不符合契约时返回 `OPENSPEC_STATUS: BLOCKED`；迁移重复执行必须幂等。
- 验证命令：`python -m unittest` 或项目选定的 Python 测试命令；`npm test`；使用临时 fixture 做两次相同迁移并比较结果。
- 需要打开：`scripts/doctor.py`、`scripts/doctor.ps1`、`tests/contracts.test.js`、`package.json`。

**产出**

- `detect_project_mode()`：canonical / legacy-workflow / legacy-trellis / unconfigured / blocked。
- `read_active_change()`：只消费 JSON/结构化文件，不扫描目录猜测 active change。
- `migrate_workflow_task()`：生成 proposal/spec/design/tasks/context/verification/migration-report。
- 来源 hash、映射版本、迁移时间和结果状态。

## 切片 3：重写主路由和治理规则

**目标**：让入口 skill 以 OpenSpec 为新任务主路径，并保留显式 legacy 恢复分支。

**建议文件边界**

- 修改：`skills/run-engineering-workflow/SKILL.md`。
- 修改：`skills/run-engineering-workflow/references/workflow-governance.md`。
- 修改：`skills/run-engineering-workflow/references/quality-profiles.md`（仅当 artifact/状态规则需要）。
- 修改：`commands/engineering-workflow.md`、`commands/archive-task.md`。
- 修改：`tests/contracts.test.js`。

**上下文包**

- 验收标准：AC-001、AC-002、AC-003、AC-004、AC-006、AC-007、AC-009、AC-011、AC-012。
- 设计决策：OpenSpec CLI status 是活动任务选择依据；当前 skill 只负责路由和质量门，不复制 OpenSpec workflow 实现。
- 已定位：`skills/run-engineering-workflow/SKILL.md` 的 Start、Route By State、Bounded Context And Dispatch Contract、archive 边界；`ARCHITECTURE.md` 的 Workflow 与 Design Rules。
- 现成模式：当前入口按 profile 路由 `lightweight`/`standard`/`critical`，并要求 dispatch 显式携带 task path、slice、Read、Must preserve 和 Verification。
- 不变量：不再把 `.workflow/CURRENT.md` 当成新任务入口；用户批准前不能 apply；review clean 后仍然停在 awaiting-acceptance；不自动 archive。
- 验证命令：`npm test`；逐段检查 skill 中不存在“新建 `.workflow/tasks`”和“恢复 Trellis 注入器”的表述。
- 需要打开：上述 skill、references、commands、`ARCHITECTURE.md`、`AGENTS.md`。

**产出**

- canonical OpenSpec 路由正文。
- legacy workflow 恢复和显式迁移说明。
- Trellis 只读兼容说明。
- 新的 OpenSpec dispatch contract 和失败状态格式。

## 切片 4：适配上下文包、TDD、review 和验证证据

**目标**：保留当前项目的质量治理，但把产物写到 OpenSpec change 内。

**建议文件边界**

- 修改：`agents/workflow-planner.md`、`agents/workflow-implementer.md`、`agents/workflow-reviewer.md`。
- 修改：`skills/plan-solution/SKILL.md`、`skills/review-implementation/SKILL.md`、`skills/finish-with-evidence/SKILL.md`、`skills/archive-task/SKILL.md`。
- 同步检查：`skills/*/agents/openai.yaml`、`.omp`/`.pi`/Claude 安装生成源。
- 修改：`tests/contracts.test.js`、必要的 `evals/workflow-cases.json`。

**上下文包**

- 验收标准：AC-002、AC-007、AC-012。
- 设计决策：OpenSpec `tasks.md` 是实施清单；自定义 `context.md` 是 bounded dispatch 包；`verification.md` 是唯一新验证证据；不生成平行 `.workflow/outcome.md`。
- 已定位：`skills/plan-solution/SKILL.md` 的 design/implement/context 产物规则；`skills/finish-with-evidence/SKILL.md` 的 outcome/awaiting-acceptance 规则；三个 root agent 定义。
- 现成模式：当前 agent 只接收显式 task path 和已内联上下文，不允许扫描 `.workflow/tasks/` 猜任务。
- 不变量：实现 worker 不修改 proposal/spec/design；reviewer 只读；主会话拥有整合、修复、证据和用户验收；OpenSpec archive 只在用户验收后调用。
- 验证命令：`npm test`；对一个 fixture change 做 planner → implementer → reviewer → evidence 的静态契约检查。
- 需要打开：上述五个 skill、三个 agent、相关 `openai.yaml` 和 `evals/workflow-cases.json`。

**产出**

- OpenSpec change artifact 模板。
- agent dispatch 的新字段和范围约束。
- verification.md 的 AC、命令、结果、review、剩余风险格式。
- 旧 `.workflow` 恢复任务的只读提示。

## 切片 5：更新四平台安装器和 doctor

**目标**：让 Codex、Claude Code、OMP、Pi 都能发现并使用 OpenSpec 适配，同时不安装 Trellis injector。

**建议文件边界**

- 修改：`scripts/install.ps1`、`scripts/doctor.py`、`scripts/doctor.ps1`、`scripts/start-omp.py`。
- 修改：`config/omp-workflow.yml`。
- 修改：`README.md` 的基础环境、安装、客户端入口、升级检查章节。
- 修改：`tests/contracts.test.js`、`scripts/test_start_omp.py`。

**上下文包**

- 验收标准：AC-008、AC-009、AC-011。
- 设计决策：安装器管理本仓库的 skill/agent/command，OpenSpec CLI 由用户或项目工具链安装；不静默 `openspec init`；项目级初始化必须有明确命令和确认。
- 已定位：`scripts/install.ps1` 的 Harness/Scope 分支和受管文件复制；`scripts/doctor.py` 的诊断报告；`config/omp-workflow.yml` 的 includeSkills/modelRoles；`README.md` 的四平台安装章节。
- 现成模式：当前安装器通过 `-Harness Codex|OMP|Claude|Pi|All` 分发，且已有 `.trellis` 不创建、不修改的断言。
- 不变量：保持 `Both` 与 `All` 兼容语义；不写项目 `.pi/settings.json`；不把 OpenSpec provider-specific model 写进 agent 定义；doctor 失败必须可定位。
- 验证命令：`npm test`；`python scripts/test_start_omp.py`；`scripts\doctor.ps1 -Scope User -Harness <Harness>` 的 WhatIf/diagnostic smoke；在无 OpenSpec CLI fixture 下检查 BLOCKED 文本。
- 需要打开：上述安装器、doctor、OMP 配置和测试文件。

**产出**

- OpenSpec 依赖检查和可操作提示。
- `openspec init/update` 的用户确认说明。
- 四个平台的 OpenSpec command/skill 路径说明。
- OpenSpec 版本升级后的 doctor 检查项。

## 切片 6：迁移文档、评估和回归验证

**目标**：让用户可以从旧项目安全迁移，并证明新旧模式不会混写。

**上下文包**

- 验收标准：AC-005、AC-006、AC-010、AC-011、AC-012。
- 设计决策：迁移是显式、可重复、来源不变的操作；旧 `.trellis` 永不升级为可写；完成后由用户验收再 archive。
- 已定位：`README.md` 的“旧 Trellis 只读”“一次完整任务的阶段”“验收和归档由你执行”“跨客户端和新会话续接”；`evals/workflow-cases.json`。
- 现成模式：当前文档将聊天和 memory 降级为线索，磁盘产物为事实；验收后由用户触发 archive。
- 不变量：不删除旧记录；不把迁移成功等同于用户验收；所有失败路径都保留可读报告。
- 验证命令：`npm test`、`python scripts/test_start_omp.py`、完整 fixture migration smoke、文档链接检查。
- 需要打开：`README.md`、`evals/workflow-cases.json`、所有新增/修改的 contract tests。

**产出**

- 迁移指南和回滚指南。
- 新旧目录对照表。
- OpenSpec 缺失、版本不兼容、多个 active change、迁移失败的故障排查说明。
- eval cases：新任务、legacy resume、explicit migration、Trellis read-only、OpenSpec blocked。

## 切片 7：独立审查和收口

**目标**：在稳定快照上进行独立 review，修复 findings 后完成真实验证，但不归档。

**上下文包**

- 验收标准：AC-001 至 AC-012 全部。
- 设计决策：implementation 与 final review 使用独立上下文；任何实质修复后重新验证并重新 review。
- 已定位：当前 `review-implementation`、`finish-with-evidence`、`archive-task` 的职责边界，以及 `AGENTS.md` 对 acceptance/archival 的限制。
- 现成模式：critical 任务执行仓库检查、规范/需求 review、独立 reviewer、修复、复验，最终状态为 `awaiting-acceptance`。
- 不变量：不把测试通过冒充用户验收；不自动移动到 archive；不清理旧兼容目录。
- 验证命令：完整 `npm test`、Python 测试、OpenSpec fixture smoke、安装器 WhatIf/doctor、独立 reviewer 报告。
- 需要打开：最终 diff、所有 OpenSpec 适配代码、skill/agent 文本、合同测试和文档。

## 风险与控制

| 风险 | 控制 |
| --- | --- |
| OpenSpec CLI 输出或 artifact 规则变化 | 锁定最低版本、只读 JSON、doctor 早失败、adapter contract tests |
| `.workflow` 与 OpenSpec 双写 | canonical mode 明确禁止新 `.workflow/tasks`，合同测试拒绝 |
| 迁移损坏历史 | copy-transform-verify、来源 hash、来源目录只读、失败自动保留来源 |
| 多个 active change 无法判断 | 返回 BLOCKED，要求用户选择，不猜测 |
| 自定义 verification/context 被 archive 丢失 | 切片 0 先验证 artifact 规则，并为 archive 添加回归测试 |
| 四个平台行为漂移 | 根定义单一来源、安装器同步、逐平台 smoke test |
| 旧 Trellis 规则被重新引入 | 保留禁止项合同测试，不安装 hooks/extensions |

## 完成定义

- 所有 AC 有真实验证结果。
- 新任务路径只写 OpenSpec。
- `.workflow` 和 `.trellis` 兼容路径通过 fixture 验证。
- OpenSpec 缺失或不满足版本时能清晰阻断。
- 独立 review 无未解决高严重度 finding。
- `verification.md` 写明实际命令、结果和剩余风险。
- STATUS 置为 `awaiting-acceptance`，等待用户验收；不自动 archive。

## 实施批准

用户在当前会话明确要求“开始实施”，批准按本任务的 critical 方案执行。OpenSpec change：`openspec/changes/openspec-compatibility/`；新任务 canonical，旧 `.workflow` 仅恢复/迁移来源，`.trellis` 只读。
