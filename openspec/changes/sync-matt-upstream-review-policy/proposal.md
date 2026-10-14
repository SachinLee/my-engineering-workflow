# 同步 Matt 上游约定并统一审查策略

## 目标

在不替换自有工程工作流的前提下，适配已安装的 Matt `1.3.1`：用一套按风险分级的审查合同替代重复审查链，完整覆盖提交前工作区，明确领域词汇与任务上下文的不同归属，并记录经审阅的上游版本。

## 设计时基线与问题

- Matt 仓库当前提交为 `49dd158d1076134a641b33efb035946536778336`，插件版本为 `1.3.1`；自有 `manifests/upstreams.lock.json` 仍记录 `8b78b531ab965735c5dc74f6f7a219e1e37326df` / `1.2.3`。
- 主路由的 Standard 审查是二选一，但质量配置、交付技能、命令入口与部分 README 路径会要求先 `code-review` 再独立复核。
- 上游 `code-review` 原生合同是两个并行子代理、固定点到 `HEAD` 的三点 diff。把它称为“主会话执行、不派 agent”不符合真实行为；该 diff 也不包含未提交改动。
- `workflow-reviewer` 已具备正确性、测试、安全和复杂度检查能力，但尚未显式承担分开的 Standards / Spec 报告；OMP 自动加载 `code-review` 可能引入嵌套审查。
- 上游 `domain-modeling` 使用 `GLOSSARY.md`；本仓库仍把领域词汇表写成 `CONTEXT.md`。这不涉及 OpenSpec `artifacts/context.md` 的重命名。
- 现有 26 个 Node 契约测试通过，但大多检查关键词和用例存在，不能证明模型执行了完整审查链。

## 范围内

1. 在现有 `quality-profiles.md` 中集中定义分级审查合同，主路由、交付技能、审查技能、代理、入口和活跃文档引用它。
2. 默认工作区审查覆盖相关 staged、unstaged、显式列出的 untracked 文件；以已选 OpenSpec change 为 Spec 来源。
3. 保留 Matt 原生审查作为用户显式调用的独立模式，不自动触发、不修改或复制上游正文。
4. 领域词汇默认对齐 `GLOSSARY.md`，为旧 `CONTEXT.md` 明确只读兼容与人工选择规则，避免双写。
5. 更新已审阅的 Matt 版本记录，补充契约断言、行为演练及安装验证方案。

## 范围外

- 最初阶段仅设计；用户随后明确批准“开始实施”，目前允许按 design/tasks 修改技能、代理、版本锁及测试并运行隔离 Project 安装。生产 User 安装仍不在本 change 的验证范围。
- 不修改 Matt/Ponytail 源码，不扩大默认启用的技能集合，不自动接入 `implement-spec`、`pr`、`retro` 或新版 Matt `handoff`。
- 不全局替换 `context`，不批量迁移用户项目，不修改已归档 change 或 `.workflow/`、`.trellis/`。
- 不新增运行时审查框架、快照服务、模型路由器或强制跨模型依赖。
- 不修复另一个项目 `omp-extensions/workflow-review-gate` 的旧指针解析；该缺口作为后续独立工作记录。
- 不自动提交、推送、验收或归档。

## 角色与受影响系统

- 主会话：选择 change、执行实现与检查、组装审查材料、修复 findings、记录交付。
- `workflow-reviewer`：在独立上下文执行一轮合并范围的只读复核，分开报告 Standards / Spec。
- Codex、OMP、Claude Code、Pi：继续使用现有安装器及角色边界；Pi reviewer 不增加 shell 或写权限。

## 假设与约束

- 用户先确认新建 change 并编写方案，随后在当前会话明确批准“开始实施”；方案审批与实现授权均为 approved。验收与归档仍未授权。
- 本次为 `standard` 工作，默认主会话设计和实现，最终审查用一个 fresh-context reviewer；不可为了扩大代理预算把任务虚报为 `critical`。
- 方案审批后才允许实现；本仓库已有未提交修改，特别是执行时限和任务路由改动，不能清除或覆盖。
- 独立上下文优先；不同模型可用时使用，不把同模型的新上下文冒称为跨模型复核。
- OMP 去重扩展源代码在 `../omp-extensions/workflow-review-gate`，当前解析 `Active task:` 而非 `Active change:`。本方案提供可检查的流程合同，不声称运行时去重全面生效。
- 模型执行结果有非确定性；静态契约通过不等于模型行为已验证。

## 验收标准

- [ ] AC-001: 按风险分级的审查合同一致且无重复派发
  - 场景：从主路由、命令入口或交付技能处理同一 change 的最终审查。
  - 动作：分别按 `lightweight`、`standard`、`critical` 路径执行。
  - 期望：Lightweight 仅主会话范围检查和最小可运行检查；Standard 默认主会话实现、一个独立 reviewer；Critical 在完整验证后同样只有一个最终 reviewer，必要的专项检查有明确风险依据。
  - 不得：默认执行 Matt 双代理后再追加最终 reviewer；通过隐藏嵌套 dispatch 绕过预算；降低独立复核要求。
  - 验证方法：跨入口契约检查和三类路径演练，记录实际审查次数。

- [ ] AC-002: 审查范围与需求来源准确
  - 场景：change 包含 staged、unstaged 和未跟踪测试，或用户显式请求审查提交区间。
  - 动作：默认审核完整相关工作区；原生 Matt 模式审核合法固定点到 `HEAD` 的提交差异。
  - 期望：工作区模式传递完整相关 diff、未跟踪文件内容及选定 change 的 proposal/specs；报告同时有 Standards / Spec。原生模式明确需用户调用、有效固定点及非空提交 diff，且不能替代对未提交代码的审查。
  - 不得：把空的提交 diff 视为完整工作区已经干净；搜寻另一个 issue 或 `.scratch/` 来覆盖已选 OpenSpec 需求；读取无关或敏感未跟踪文件。
  - 验证方法：临时 Git 仓库混合改动演练及静态合同检查。

- [ ] AC-003: 交付复用有效审查证据并诚实处理缺失
  - 场景：已有完整独立审查结果、发生修复、审查输入无效或独立上下文不可用。
  - 动作：进入 `finish-with-evidence`。
  - 期望：同 change、同相关快照、同需求合同的有效结果被复用；审查对象、需求或支撑证据实质改变或有 findings 时先修复、复验并重新审查；仅追加审查结果或交付说明不使自身失效；沿用现有一次受控 `INVALID` 替换规则。独立审查不可用记 `UNVERIFIED` 并停在缺口交接，不宣称正常交付完成。
  - 不得：无变化重复派发、把主会话自查冒称独立复核、缺失证据写成 `PASS` 或 `REVIEW_STATUS: CLEAN`。
  - 验证方法：有效复用、修复失效、INVALID、不可用四类行为演练。

- [ ] AC-004: 领域词汇与任务上下文各有唯一归属
  - 场景：项目有 `GLOSSARY.md`、只有旧 `CONTEXT.md`、两者共存、存在 `GLOSSARY-MAP.md` 或尚无术语文件。
  - 动作：澄清领域术语并保存结论。
  - 期望：优先服从项目明确约定；新项目首次形成稳定术语时才建 `GLOSSARY.md`；旧文件先只读，写入前确认唯一目标和必要迁移；多上下文遵循 map。规范写 OpenSpec，技术决策写 design 或合适 ADR，派发上下文仍写 `artifacts/context.md`。
  - 不得：自动重命名旧文件、双写词汇表、空建文件，或修改 `artifacts/context.md` 的用途。
  - 验证方法：五类术语文件场景演练、活跃文档引用检查。

- [ ] AC-005: 上游版本记录反映已审阅版本
  - 场景：本次适配实现及验证完成。
  - 动作：更新 `manifests/upstreams.lock.json`。
  - 期望：Matt revision 为 `49dd158d1076134a641b33efb035946536778336`，version_hint 为 `1.3.1`，生成日期为实际审阅日期，审阅范围和未采用行为可追溯。
  - 不得：改动 Ponytail 或 retired_sources 的版本、扩大安装技能集合，或把锁文件称为自动安装器。
  - 验证方法：JSON 解析、源版本核对及字段差异断言。

- [ ] AC-006: 三种代理定义与安装副本保持边界一致
  - 场景：通过现有安装器部署新版自有工作流到隔离测试目录。
  - 动作：检查 root、OMP、Pi reviewer 定义及 Codex/OMP/Claude/Pi 安装产物。
  - 期望：Reviewer 清楚支持 Standard/Critical、禁止嵌套 dispatch；OMP reviewer 不自动加载原生 `code-review`；只读权限、OMP `@advisor`、Pi 模型继承及最大 timeout、现有 `Both`/`All` 含义保持。
  - 不得：手改生成副本、修改无关本机配置、恢复执行时限、覆盖 agentmemory `handoff`。
  - 验证方法：契约测试、隔离安装、源文件与安装产物哈希比较。

- [ ] AC-007: 验证覆盖实际兼容风险并保留现有工作
  - 场景：完成上述行为和文档适配。
  - 动作：先补目标契约测试，再修改规则，并执行针对性验证。
  - 期望：新增测试先 RED 后 GREEN，原 Node/Python 检查保持通过；行为演练记录实际输入、输出、代理次数或明确的 `NOT RUN`；不以 eval 用例存在冒称模型行为通过。工作区基线保留，不写 legacy，不自动验收归档。
  - 不得：为了测试改写无关文件、用单个关键词匹配代替跨入口合同检查、虚构独立 reviewer 结果。
  - 验证方法：目标与完整测试、行为记录、文件哈希基线比对。

## 未决与阻塞决策

- 方案审批与实现授权已批准。依照 tasks.md 完成已批准范围；用户验收与归档仍待用户决定。
- 独立复核在某个 harness 不可用时，默认停在 `UNVERIFIED` 缺口交接；若用户选择例外交付，必须单独记录授权和风险，不能标为普通 `PASS`。
- OMP 运行时门禁解析缺口不在本 change 的实现范围，后续应单独修复并验证。
