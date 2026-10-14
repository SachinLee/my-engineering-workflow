# 执行任务与审批边界

## 当前状态

- Active change: `sync-matt-upstream-review-policy`
- 阶段：`awaiting-acceptance`
- 交接时间：`2026-10-12T03:19:30+00:00`
- 风险级别：`standard`
- 方案审批：`approved`（用户在当前会话明确“开始实施”）
- 实现授权：`approved`
- 当前执行前沿：实施与交付任务 `13/13` 已完成；等待用户验收，存在验证限制见 `artifacts/verification.md`。
- 默认 writer：主会话；修复后最终独立复核已完成，`REVIEW_STATUS: CLEAN`。
- 本文件的 checkbox 只标记实现与交付，不用于表示“已经写好方案”。

## 切片 1：AC-001 / AC-007 - 统一审查预算和入口

- 行为：风险档只在现有质量配置定义；入口和主路由不再追加默认 Matt 双代理阶段。
- 代码边界：`skills/run-engineering-workflow/SKILL.md`、`skills/run-engineering-workflow/references/quality-profiles.md`、`skills/run-engineering-workflow/references/workflow-governance.md`、`commands/engineering-workflow.md`、`README.md`、`ARCHITECTURE.md`、`tests/contracts.test.js`、`evals/workflow-cases.json`。
- 测试接缝：不同入口引用同一合同、分级预算和独立性边界；不是仅检查 `code-review` 名称还存在。
- RED：先补跨入口正反断言，执行 `npm test`；当前默认双代理前置和不一致入口必须使目标断言失败。
- 实现：集中风险表，入口按 profile 路由；Standard 默认唯一 worker 是 reviewer，委派例外需明确授权。
- GREEN：`npm test`，检查新增断言实际执行且旧测试未为逃避合同被删除。
- 验证：人工演练三个风险档，从主路由/命令/收尾分别进入，记录默认审查数量和判断依据。
- 依赖：用户批准方案。
- 回滚：仅撤销本片实际规则和测试 patch，不覆盖既有主路由与执行时限改动。

- [x] 1.1 添加合同断言与分级用例，记录 RED。
- [x] 1.2 修改分级合同、路由、入口和相关活跃说明。
- [x] 1.3 记录 GREEN 与三类路径演练证据。

## 切片 2：AC-002 / AC-003 / AC-006 / AC-007 - 完整范围、单次独立审查和证据复用

- 行为：一个本地 reviewer 完整审查相关工作区，分开 Standards / Spec；交付消费同快照有效结果，不嵌套调度原生 Matt。
- 代码边界：`skills/review-implementation/SKILL.md`、`skills/finish-with-evidence/SKILL.md`、`agents/workflow-reviewer.md`、`.omp/agents/workflow-reviewer.md`、`.pi/agents/workflow-reviewer.md`、`tests/contracts.test.js`、`evals/workflow-cases.json`。若前片合同需补齐，修改仍限其原声明文件。
- 测试接缝：报告、handoff、只读能力、OMP autoload、交付前置条件和失效规则。
- RED：先添加禁止原生 autoload/嵌套 dispatch、分维度报告、独立缺失不通过、证据追加不自失效等断言；`npm test` 应因现有规则失败。
- 实现：工作区与显式原生模式分开；Root/OMP 支持 Standard，Pi 不扩权限；复用记录，修复后复验，沿用现有 INVALID 替换规则。
- GREEN：`npm test`。
- 验证：临时 Git 仓库中制造 staged、unstaged、untracked 测试和空提交 diff；记录采集与范围差异。再演练有效复用、修复失效、INVALID、独立上下文不可用、仅追加交付说明。原生模式演练记录需用户显式调用和实际代理次数，未执行注明 `NOT RUN`。
- 依赖：切片 1。
- 回滚：撤销本片 reviewer/收尾 patch，保留 Pi `timeoutMs: 2147483647`、只读工具和现有模型路由。

- [x] 2.1 增加范围、报告、复用、权限和 autoload 断言，记录 RED。
- [x] 2.2 修改审查/收尾技能和三个 reviewer 源定义。
- [x] 2.3 记录 GREEN、混合工作区实验及五类审查结果演练。

## 切片 3：AC-004 / AC-007 - 明确词汇表唯一归属

- 行为：新词汇使用 `GLOSSARY.md`；旧 `CONTEXT.md` 不自动迁移；规范、设计和派发上下文用途保持。
- 代码边界：`skills/run-engineering-workflow/references/workflow-governance.md`、`skills/clarify-requirements/SKILL.md`、`skills/finish-with-evidence/SKILL.md`、`skills/archive-task/SKILL.md`、`README.md`、`tests/contracts.test.js`、`evals/workflow-cases.json`。
- 测试接缝：活跃术语规则与指针；明确保留旧文件兼容提及及 `artifacts/context.md`，不能断言整个仓库不存在 `CONTEXT.md`。
- RED：添加新文件惰性创建、旧文件写前确认、共存选择、多上下文 map 和 OpenSpec 上下文保留断言；`npm test` 应因旧术语目标失败。
- 实现：在共享治理集中归属，调用处用能力指针，不复制上游正文。
- GREEN：`npm test`。
- 验证：五类词汇文件场景演练；检查没有新增空词汇文件、迁移脚本或双写路径。
- 依赖：切片 2，避免收尾文件并行写入。
- 回滚：撤销词汇归属相关 patch；没有数据迁移，无需改用户旧词汇文件。

- [x] 3.1 添加术语归属断言和场景，记录 RED。
- [x] 3.2 修改共享规则及活跃调用处，保留历史内容不变。
- [x] 3.3 记录 GREEN 和五类场景演练。

## 切片 4：AC-005 / AC-006 / AC-007 - 来源锁与隔离安装验证

- 行为：锁文件反映已适配的 Matt 版本，四种安装产物一致，最终证据完整。
- 代码边界：`manifests/upstreams.lock.json`、`tests/contracts.test.js`、`evals/workflow-cases.json`、当前 change 的 `artifacts/verification.md`；sandbox 生成文件仅由现有安装器写入。
- 测试接缝：JSON 字段差异、隔离安装文件哈希、完整测试与审查记录。
- RED：新增 Matt 精确版本和无关来源不变断言；`npm test` 应因旧锁文件失败。
- 实现：核对源提交/插件版本，修改允许字段；保持 schema 和候选技能集合。没有证据前不先把版本锁改成新值。
- GREEN 与回归：`npm test`；`python -m unittest discover -s tests -p 'test_*.py'`；`python scripts/test_start_omp.py`。
- 验证：先运行 `pwsh -NoProfile -File scripts/install.ps1 -Scope Project -Harness All -ProjectPath <sandbox> -WhatIf`；确认目标后在相同 sandbox 去掉 `-WhatIf`，核对三种 agent 及共享 references；执行 `python scripts/doctor.py --scope Project --harness All --project-path <sandbox>`，环境缺项如实记录。此命令不是本机 User 安装授权。
- 依赖：切片 1 至 3 通过；真实模型演练和最终独立 review 需要相应平台与授权。
- 回滚：恢复本 change 引入的 Matt 锁字段和测试 patch；清理仅本任务创建的 sandbox。真实安装如另获授权，先备份受管目标。

- [x] 4.1 添加版本字段断言，记录 RED 后更新锁文件。
- [x] 4.2 执行 GREEN、Python 回归、隔离安装与哈希 smoke。
- [x] 4.3 执行获授权的行为演练与一个独立最终 reviewer；没有执行则保留缺口，不写 CLEAN。
- [x] 4.4 逐条记录 AC 与证据；全部满足后停在 `awaiting-acceptance`，不自行归档。

## 上下文与续接

切片交接材料见 `artifacts/context.md`。实现续接时重新核对磁盘和当前未提交改动，不按会话时间猜测进度。任何范围扩展、独立性例外或跨仓修改都先报告并获得授权。
