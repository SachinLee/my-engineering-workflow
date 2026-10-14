## ADDED Requirements

### Requirement: 风险分级决定唯一的默认审查路径
工作流 MUST 在现有质量配置中集中定义审查预算，各入口 SHALL 引用同一合同。`lightweight` 使用主会话范围检查和最小验证；`standard` 默认主会话实现后执行一个 fresh-context 最终 reviewer；`critical` 增加适用的安全、集成、数据、回滚与 E2E 验证，但不默认追加重复最终 reviewer。Standards、Spec、正确性、测试、安全和复杂度 SHALL 纳入该 reviewer 的同一范围。实现代理和审查代理的总预算例外 MUST 经用户明确授权并记录，不能通过虚报风险或嵌套 dispatch 获得。

#### Scenario: Standard 从不同入口进入最终审查
- **WHEN** 主路由、命令入口或交付技能处理同一 Standard change 的稳定工作区
- **THEN** 它们采用同一质量配置，默认只派发一个最终 reviewer，不调用 Matt 原生双代理审查作为前置步骤

#### Scenario: Lightweight 与 Critical 路径
- **WHEN** 非行为性 Lightweight 或有真实关键风险的 Critical change 进入检查
- **THEN** 前者不默认派代理；后者完成适用完整验证后只执行一个最终 reviewer，专项检查说明触发风险，不隐藏增加审查层

### Requirement: 默认审查覆盖完整相关工作区
工作流 SHALL 以已明确选中的 OpenSpec change 的 proposal、specs 和适用设计为需求来源。Reviewer MUST 读取相关 staged、unstaged diff 及被显式列入范围的 untracked 文件内容，保留无关用户改动与敏感文件边界。报告 SHALL 分开提供 Standards 和 Spec，并列出实际证据、剩余风险及未运行检查。

#### Scenario: 未跟踪测试不被提交 diff 漏掉
- **WHEN** 提交间 diff 为空，但工作区含 staged、unstaged 和 untracked 测试改动
- **THEN** 默认审查仍检查所有相关改动，不把空提交 diff 视为已完成工作区审查，不另行寻找 issue 覆盖已选 change

### Requirement: 原生 Matt 审查保持显式且独立的模式
工作流 MUST 区分本地工作区审查和用户显式调用的 Matt 原生 `code-review`。原生模式 SHALL 保持上游双代理、有效固定点及非空 `git diff <fixed-point>...HEAD` 的合同；不得把只含提交的结果当作对未提交工作区的独立复核。默认 reviewer MUST NOT 自动加载或嵌套启动该模式。

#### Scenario: 用户显式审查提交范围
- **WHEN** 用户调用原生 Matt `code-review` 并提供固定点
- **THEN** 先验证固定点和非空提交 diff，再按上游合同执行；报告明确未覆盖的工作区内容，默认本地工作流不自动再派第三名 reviewer

### Requirement: 交付检查复用审查结果而不是新增审查链
`finish-with-evidence` SHALL 检查并复用同 change、同相关快照、同需求合同的有效独立审查记录。缺少审查时 SHALL 返回主路由选定的审查阶段；审查对象、需求或支撑证据实质变化后 MUST 使旧结果失效并重新验证。仅追加审查结果或交付说明 SHALL 不使审查自身失效。沿用现有一次受控 `INVALID` 替换规则。独立上下文不可用、审查材料不完整或仍有 material findings 时 MUST 保留 `UNVERIFIED` 或缺口说明，不生成虚假的 `CLEAN`、`PASS` 或普通完成状态。

#### Scenario: 无变化的交付不重派
- **WHEN** 已有有效最终审查且相关材料未变
- **THEN** 交付技能引用记录，不重复执行原生 Matt 或独立 reviewer，不因调用 Ponytail 方法自动新增审查代理

#### Scenario: 修复后需要重新复核
- **WHEN** 当前 findings 已修复或需求、相关文件、验证证据改变
- **THEN** 旧审查记录失效，主会话重新检查并派发新一轮最终审查；未知结果不等于通过

### Requirement: 领域术语与上下文分离且不自动迁移
工作流 SHALL 优先遵循项目明确的术语文件约定和 `GLOSSARY-MAP.md`。新项目在首次解析出稳定术语时才使用 `GLOSSARY.md`；仅有旧 `CONTEXT.md` 或两者冲突时 SHALL 先只读，写入前确认唯一目标及必要迁移。规范、设计决策和派发上下文 MUST 继续使用各自 OpenSpec 文件，不自动改名、双写或空建术语文件。

#### Scenario: 新项目、旧词汇表与多上下文
- **WHEN** 项目只有新词汇表、只有旧词汇表、两者并存、存在 map 或无术语文件
- **THEN** 采用唯一且明确的术语归属；`artifacts/context.md` 不改名、不变为词汇表；旧内容的迁移需用户授权

### Requirement: 版本追踪与跨 harness 适配保持可审计
在对应适配及验证完成后，工作流 SHALL 将 Matt 锁定为提交 `49dd158d1076134a641b33efb035946536778336` / `1.3.1`，记录实际审阅日期；保持 Ponytail、retired_sources 和默认候选技能集合不变。Root、OMP、Pi reviewer SHALL 语义一致并保持只读、OMP 角色别名、Pi 模型继承与最大时限。安装副本 MUST 由现有安装器生成，`Both` 和 `All` 的含义不变。

#### Scenario: 隔离安装与字段对比
- **WHEN** 在临时 Project 目录安装四种 harness 的自有工作流并核对锁文件
- **THEN** 新规则和三个 reviewer 源定义正确分发，无权写文件或启动嵌套审查的 reviewer 没有新增权限，无关技能与配置不变

### Requirement: 测试证据不能代替模型行为证据
规则修改 MUST 先增加相关契约测试并取得 RED，再做最小修改并取得 GREEN。行为演练 SHALL 记录真实输入、输出及实际代理次数；仅验证 eval 条目存在不构成模型行为通过。现有用户修改、legacy 只读边界、按需读取状态、用户批准实现和验收归档门禁 MUST 保持。

#### Scenario: 方案阶段与实现阶段分离
- **WHEN** 用户只授权设计
- **THEN** 只修改当前 change 的方案记录，所有实现任务保持未完成，不运行安装、不改技能正文、不接受或归档 change

#### Scenario: 行为执行工具不可用
- **WHEN** 缺少授权或实际 harness，无法执行模型行为演练
- **THEN** 对应结果记 `NOT RUN` 或 `UNVERIFIED`，保留人工演练证据与限制，不将静态测试通过写成模型兼容已验证
