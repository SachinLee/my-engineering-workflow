# 实现上下文与交接包

## 使用边界

- 方案审批与实现授权均已批准；四个切片、13 项任务已完成，当前状态 `awaiting-acceptance`。下一步由用户验收；不重新派发或执行已完成任务。
- 工作目录：`D:/my-works/claude-skills/my-engineering-workflow`。
- Active change: `openspec/changes/sync-matt-upstream-review-policy/`
- 当前默认主会话一个 writer；首轮独立 findings 已处理，最终独立复核 `REVIEW_STATUS: CLEAN`。完整结果、15 个模型判断场景和未执行边界见 `artifacts/verification.md`。
- 新鲜上下文先核对当前 diff，不重做上游大范围调查。若内联结论与磁盘不符，停止报告差异。
- `artifacts/planning-baseline.json` 保存设计前 189 个文件的 SHA-256。排除 `.git`、`.runtime`、`__pycache__` 和当前 change；用于证明设计阶段没有改技能/代理，不是运行时 review snapshot。

## 共用已知结论与现成模式

- Matt 提交 `49dd158d1076134a641b33efb035946536778336`，插件 `1.3.1`；lock 已更新为同一 revision/version。
- 上游 `code-review` 的核心是两个并行代理和 `git diff <fixed-point>...HEAD`，不包含未提交文件；默认 issue/track 寻源不应覆盖已选 OpenSpec 需求。本地整合不修改、复制上游正文。
- 设计前路由曾是“Standard 二选一”，实现已统一预算：主会话实现、一个独立 reviewer、收尾复用有效报告。切片正文保留原设计线索，不能当作仍待实施的状态。
- 现有测试用 `node:test`、`node:assert/strict` 和 helper `read(relativePath)`。可以添加同风格针对段落的正反断言，不增加依赖；禁止为逃避旧合同整段删除测试。示例结构：

```js
test("review policy covers the declared entry points", () => {
  const router = read("skills/run-engineering-workflow/SKILL.md");
  // 对声明的合同位置、引用及禁止路径做正反断言；按实际实现写准确断言。
});
```

- `evals/workflow-cases.json` 使用 `schema_version: 3` 和 `cases`，条目已有 `name`、`state`、`expected_stage`、`forbidden`。条目存在不能证明实际 agent 行为。现有 `duplicate-final-review-same-snapshot` 禁止重复派发，`remediated-diff-needs-fresh-final-review` 要求修复后重审，可直接扩展场景覆盖。
- 主会话保留 existing 未提交改动，不得改 Pi 最大 timeout、OMP 角色别名、只读权限、模型继承和 `Both`/`All` 意义。
- `../omp-extensions/workflow-review-gate/lib/review-gate-core.js:18-19` 仍解析 `Active task:`；`scripts/install.ps1:14-15,260-263` 从该源安装扩展。不修改安装副本，本 change 不解决运行时去重。依赖合同与调用记录，不宣传机械保证。
- 所有切片共用返回格式：实际改动文件；RED/GREEN 命令、退出码与断言数；验证输入/观察；未运行检查；风险与下一片前置状态。缺工具记 `NOT RUN`，未独立审查记 `UNVERIFIED`，不能生成 `CLEAN`。

## 切片 1 上下文包

```text
Assigned slice: 切片 1 / AC-001, AC-007
Phase: complete
Read: 本片允许文件的当前版本及差异
Review scope: 分级合同、主路由、命令入口与活跃说明
```

### 已内联验收与设计

- AC-001: 按风险分级的审查合同一致且无重复派发
  - 场景：从主路由、命令入口或交付技能处理同一 change 的最终审查。
  - 动作：分别按 `lightweight`、`standard`、`critical` 路径执行。
  - 期望：Lightweight 仅主会话范围检查和最小可运行检查；Standard 默认主会话实现、一个独立 reviewer；Critical 在完整验证后同样只有一个最终 reviewer，必要的专项检查有明确风险依据。
  - 不得：默认执行 Matt 双代理后再追加最终 reviewer；通过隐藏嵌套 dispatch 绕过预算；降低独立复核要求。
  - 验证方法：跨入口契约检查和三类路径演练，记录实际审查次数。
- AC-007: 验证覆盖实际兼容风险并保留现有工作
  - 场景：完成上述行为和文档适配。
  - 动作：先补目标契约测试，再修改规则，并执行针对性验证。
  - 期望：新增测试先 RED 后 GREEN，原 Node/Python 检查保持通过；行为演练记录实际输入、输出、代理次数或明确的 `NOT RUN`；不以 eval 用例存在冒称模型行为通过。工作区基线保留，不写 legacy，不自动验收归档。
  - 不得：为了测试改写无关文件、用单个关键词匹配代替跨入口合同检查、虚构独立 reviewer 结果。
  - 验证方法：目标与完整测试、行为记录、文件哈希基线比对。

设计：`quality-profiles.md` 是唯一预算；Standard 默认 reviewer 占唯一 worker，必要实现委派例外先授权，不改成主会话自查。Critical 以验证深度区别。Lightweight 不默认 dispatch，发现行为变化重新分级。

定位：`skills/run-engineering-workflow/SKILL.md:161-164,212-220` 的二选一和 Matt 前置；`quality-profiles.md:21-24` 分开的审查条目；`workflow-governance.md:262-268` 的独立性不变量；`commands/engineering-workflow.md:25-42` 的无条件派发。文档只改当前说明，不改 archived 记录。

### 允许修改与验证

允许且需新打开：`skills/run-engineering-workflow/SKILL.md`、`skills/run-engineering-workflow/references/quality-profiles.md`、`skills/run-engineering-workflow/references/workflow-governance.md`、`commands/engineering-workflow.md`、`README.md`、`ARCHITECTURE.md`、`tests/contracts.test.js`、`evals/workflow-cases.json`。

命令：在工作目录运行 `npm test`。先新增目标断言得到真实 RED，再改规则得到 GREEN；原 26 项覆盖继续有效，新增项实际执行。人工按三个档逐入口推演并记录结果；真实代理次数只能来自获授权实际执行，不能由文本推演推断。

禁止修改：所有未声明文件、上游源、另一个 change、legacy 状态、安装副本。发现接口范围扩大或预算与独立性仍冲突时停止报告。

## 切片 2 上下文包

```text
Assigned slice: 切片 2 / AC-002, AC-003, AC-006, AC-007
Phase: complete
Read: 本片允许文件的当前版本、切片 1 已实现质量合同
Review scope: 审查材料范围、报告合同、交付复用和 reviewer 权限
```

### 已内联验收与设计

- AC-002: 审查范围与需求来源准确
  - 场景：change 包含 staged、unstaged 和未跟踪测试，或用户显式请求审查提交区间。
  - 动作：默认审核完整相关工作区；原生 Matt 模式审核合法固定点到 `HEAD` 的提交差异。
  - 期望：工作区模式传递完整相关 diff、未跟踪文件内容及选定 change 的 proposal/specs；报告同时有 Standards / Spec。原生模式明确需用户调用、有效固定点及非空提交 diff，且不能替代对未提交代码的审查。
  - 不得：把空的提交 diff 视为完整工作区已经干净；搜寻另一个 issue 或 `.scratch/` 来覆盖已选 OpenSpec 需求；读取无关或敏感未跟踪文件。
  - 验证方法：临时 Git 仓库混合改动演练及静态合同检查。
- AC-003: 交付复用有效审查证据并诚实处理缺失
  - 场景：已有完整独立审查结果、发生修复、审查输入无效或独立上下文不可用。
  - 动作：进入 `finish-with-evidence`。
  - 期望：同 change、同相关快照、同需求合同的有效结果被复用；审查对象、需求或支撑证据实质改变或有 findings 时先修复、复验并重新审查；仅追加审查结果或交付说明不使自身失效；沿用现有一次受控 `INVALID` 替换规则。独立审查不可用记 `UNVERIFIED` 并停在缺口交接，不宣称正常交付完成。
  - 不得：无变化重复派发、把主会话自查冒称独立复核、缺失证据写成 `PASS` 或 `REVIEW_STATUS: CLEAN`。
  - 验证方法：有效复用、修复失效、INVALID、不可用四类行为演练。
- AC-006: 三种代理定义与安装副本保持边界一致
  - 场景：通过现有安装器部署新版自有工作流到隔离测试目录。
  - 动作：检查 root、OMP、Pi reviewer 定义及 Codex/OMP/Claude/Pi 安装产物。
  - 期望：Reviewer 清楚支持 Standard/Critical、禁止嵌套 dispatch；OMP reviewer 不自动加载原生 `code-review`；只读权限、OMP `@advisor`、Pi 模型继承及最大 timeout、现有 `Both`/`All` 含义保持。
  - 不得：手改生成副本、修改无关本机配置、恢复执行时限、覆盖 agentmemory `handoff`。
  - 验证方法：契约测试、隔离安装、源文件与安装产物哈希比较。
- AC-007: 验证覆盖实际兼容风险并保留现有工作
  - 场景：完成上述行为和文档适配。
  - 动作：先补目标契约测试，再修改规则，并执行针对性验证。
  - 期望：新增测试先 RED 后 GREEN，原 Node/Python 检查保持通过；行为演练记录实际输入、输出、代理次数或明确的 `NOT RUN`；不以 eval 用例存在冒称模型行为通过。工作区基线保留，不写 legacy，不自动验收归档。
  - 不得：为了测试改写无关文件、用单个关键词匹配代替跨入口合同检查、虚构独立 reviewer 结果。
  - 验证方法：目标与完整测试、行为记录、文件哈希基线比对。

设计：单个 reviewer 分别报告 Standards / Spec，再报告正确性、安全、测试和复杂度；Ponytail 是方法，不自动派代理。默认完整相关范围包含已提交部分、staged、unstaged、显式未跟踪内容；原生 Matt 模式不替代工作区。保留现有 handoff 字段，在 Review scope/Evidence 中写 base、文件清单、diff/内容和执行证据。收尾检查有效记录，不自动派发；仅追加报告不触发自失效。

定位：`skills/finish-with-evidence/SKILL.md:21-35` 默认追加审查；`.omp/agents/workflow-reviewer.md:8,20-24` 的原生 autoload 与已有完整范围；Root/OMP reviewer 描述过窄。Pi reviewer 没有 shell，沿用主会话验证材料，不能扩权限。

### 允许修改与验证

允许且需新打开：`skills/review-implementation/SKILL.md`、`skills/finish-with-evidence/SKILL.md`、`agents/workflow-reviewer.md`、`.omp/agents/workflow-reviewer.md`、`.pi/agents/workflow-reviewer.md`、`tests/contracts.test.js`、`evals/workflow-cases.json`；为补齐前片合同可读改切片 1 的原声明文件。读取 proposal/spec 的目标 AC，不需重新调查上游。

命令：`npm test` 先 RED 再 GREEN；临时 Git 仓库用 `git diff --cached`、`git diff` 和显式读取未跟踪测试证明提交 diff 的范围差异。演练有效复用/修复/INVALID/不可用/纯报告追加，明确观察依据。安装验证在切片 4。

不变量与升级条件：不调用未经授权的代理；不扩大 Pi 权限；不改变已有最大时限和 OMP 别名；缺独立审查不放行；敏感文件不进入包。需要修改 OMP 运行时 gate 或安装器则停下请求范围扩展。

## 切片 3 上下文包

```text
Assigned slice: 切片 3 / AC-004, AC-007
Phase: complete
Read: 术语调用处和共享治理当前版本
Review scope: 词汇文件所有权与任务上下文兼容
```

### 已内联验收与设计

- AC-004: 领域词汇与任务上下文各有唯一归属
  - 场景：项目有 `GLOSSARY.md`、只有旧 `CONTEXT.md`、两者共存、存在 `GLOSSARY-MAP.md` 或尚无术语文件。
  - 动作：澄清领域术语并保存结论。
  - 期望：优先服从项目明确约定；新项目首次形成稳定术语时才建 `GLOSSARY.md`；旧文件先只读，写入前确认唯一目标和必要迁移；多上下文遵循 map。规范写 OpenSpec，技术决策写 design 或合适 ADR，派发上下文仍写 `artifacts/context.md`。
  - 不得：自动重命名旧文件、双写词汇表、空建文件，或修改 `artifacts/context.md` 的用途。
  - 验证方法：五类术语文件场景演练、活跃文档引用检查。
- AC-007: 验证覆盖实际兼容风险并保留现有工作
  - 场景：完成上述行为和文档适配。
  - 动作：先补目标契约测试，再修改规则，并执行针对性验证。
  - 期望：新增测试先 RED 后 GREEN，原 Node/Python 检查保持通过；行为演练记录实际输入、输出、代理次数或明确的 `NOT RUN`；不以 eval 用例存在冒称模型行为通过。工作区基线保留，不写 legacy，不自动验收归档。
  - 不得：为了测试改写无关文件、用单个关键词匹配代替跨入口合同检查、虚构独立 reviewer 结果。
  - 验证方法：目标与完整测试、行为记录、文件哈希基线比对。

设计：共享 Artifact Ownership 处定义唯一规则；澄清/收尾/归档只引用。旧 CONTEXT 若由用户确认继续作为项目词汇目标，向 domain-modeling 明确该约定，不另外双写 GLOSSARY。共存冲突写前询问。没有稳定术语不空建文件。不新增迁移脚本，不全局改名。

定位：`skills/clarify-requirements/SKILL.md:27-28` 与 `skills/finish-with-evidence/SKILL.md:38-40` 使用旧词汇名；上游已经在 `domain-modeling` 使用 GLOSSARY / MAP，无需自写能力。

### 允许修改与验证

允许且需新打开：`skills/run-engineering-workflow/references/workflow-governance.md`、`skills/clarify-requirements/SKILL.md`、`skills/finish-with-evidence/SKILL.md`、`skills/archive-task/SKILL.md`、`README.md`、`tests/contracts.test.js`、`evals/workflow-cases.json`。

命令：`npm test` 先 RED 后 GREEN；针对新/旧/共存/MAP/无文件五类做带输入和观察的演练。保留历史文本、`artifacts/context.md` 及既有 context package 合同。遇到真实用户文件迁移需求先报告，不在本片迁移数据。

## 切片 4 上下文包

```text
Assigned slice: 切片 4 / AC-005, AC-006, AC-007
Phase: complete（awaiting-acceptance）
Read: lock、安装入口、前三片证据与当前受管源文件
Review scope: 已审阅来源、跨 harness 生成结果及交付门禁
```

### 已内联验收与设计

- AC-005: 上游版本记录反映已审阅版本
  - 场景：本次适配实现及验证完成。
  - 动作：更新 `manifests/upstreams.lock.json`。
  - 期望：Matt revision 为 `49dd158d1076134a641b33efb035946536778336`，version_hint 为 `1.3.1`，生成日期为实际审阅日期，审阅范围和未采用行为可追溯。
  - 不得：改动 Ponytail 或 retired_sources 的版本、扩大安装技能集合，或把锁文件称为自动安装器。
  - 验证方法：JSON 解析、源版本核对及字段差异断言。
- AC-006: 三种代理定义与安装副本保持边界一致
  - 场景：通过现有安装器部署新版自有工作流到隔离测试目录。
  - 动作：检查 root、OMP、Pi reviewer 定义及 Codex/OMP/Claude/Pi 安装产物。
  - 期望：Reviewer 清楚支持 Standard/Critical、禁止嵌套 dispatch；OMP reviewer 不自动加载原生 `code-review`；只读权限、OMP `@advisor`、Pi 模型继承及最大 timeout、现有 `Both`/`All` 含义保持。
  - 不得：手改生成副本、修改无关本机配置、恢复执行时限、覆盖 agentmemory `handoff`。
  - 验证方法：契约测试、隔离安装、源文件与安装产物哈希比较。
- AC-007: 验证覆盖实际兼容风险并保留现有工作
  - 场景：完成上述行为和文档适配。
  - 动作：先补目标契约测试，再修改规则，并执行针对性验证。
  - 期望：新增测试先 RED 后 GREEN，原 Node/Python 检查保持通过；行为演练记录实际输入、输出、代理次数或明确的 `NOT RUN`；不以 eval 用例存在冒称模型行为通过。工作区基线保留，不写 legacy，不自动验收归档。
  - 不得：为了测试改写无关文件、用单个关键词匹配代替跨入口合同检查、虚构独立 reviewer 结果。
  - 验证方法：目标与完整测试、行为记录、文件哈希基线比对。

设计：仅改 Matt revision/version_hint 与实际日期，不扩 lock schema；审阅说明放当前 change 的证据。现有安装器已递归分发 references，不预期改脚本。模型演练须授权且真的执行；一个最终独立 reviewer，material findings 修复后复验。同模型 fresh context 如实称独立上下文，不叫跨模型。

### 允许修改与验证

允许修改：`manifests/upstreams.lock.json`、`tests/contracts.test.js`、`evals/workflow-cases.json`、本 change 的 `artifacts/verification.md`。需新打开 `scripts/install.ps1`、`scripts/doctor.py` 来确认当前执行目标，当前 reviewer/skill 源用于哈希；只读上游 `.claude-plugin/plugin.json` 与 HEAD 核对锁字段。

确切命令：

```text
npm test
python -m unittest discover -s tests -p 'test_*.py'
python scripts/test_start_omp.py
pwsh -NoProfile -File scripts/install.ps1 -Scope Project -Harness All -ProjectPath <sandbox> -WhatIf
pwsh -NoProfile -File scripts/install.ps1 -Scope Project -Harness All -ProjectPath <sandbox>
python scripts/doctor.py --scope Project --harness All --project-path <sandbox>
```

`<sandbox>` 必须先解析为本任务创建的绝对临时目录，准备最小 OpenSpec 配置；禁止把占位符或实际用户目录直接作为目标。第二条安装命令只能在 dry-run 目标正确后执行。预期源/安装文件哈希一致，主测试成功；doctor 如有环境缺项如实记录，不把哈希 smoke 当完整健康。

返回所有 AC 的证据映射、未运行项和一个最终 reviewer 的真实报告。仅在门禁满足后停 `awaiting-acceptance`；不自行 archive、写 journal、清 legacy 指针、commit 或 push。真实 User 范围安装需要用户另行授权。

## 续接阅读列表

以下是角色确实需要重新确认的源，不替代上面已内联结论：

| 路径 | 原因 |
| --- | --- |
| `openspec/changes/sync-matt-upstream-review-policy/proposal.md` | AC 的权威原文与审批边界 |
| `openspec/changes/sync-matt-upstream-review-policy/specs/upstream-review-integration/spec.md` | 可验证 MUST/SHALL 合同 |
| `openspec/changes/sync-matt-upstream-review-policy/design.md` | 五个技术决策与范围 |
| `openspec/changes/sync-matt-upstream-review-policy/tasks.md` | 当前执行前沿和顺序 |
| `skills/run-engineering-workflow/references/quality-profiles.md` | 实现后唯一预算来源 |
| `tests/contracts.test.js` | 现有准确断言与测试风格，当前磁盘才是事实 |
| `scripts/install.ps1`、`scripts/doctor.py` | 隔离安装当前 CLI 与受管范围 |

## 设计阶段发现但不扩大范围的矛盾

`skills/plan-solution/SKILL.md` 的前段要求内联上下文包，后段仍写 context 只列路径；本仓库 AGENTS 明确要求 package。本 change 按较明确的治理约束保留内联已知结论，并给真正的新读源列表，不为此修改 plan-solution。若将来统一这一文案，另报范围，不夹带当前兼容任务。
