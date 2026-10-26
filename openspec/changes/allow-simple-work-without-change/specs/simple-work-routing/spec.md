# 简单工作路由增量规格

## ADDED Requirements

### Requirement: 非行为性简单工作先判定快速通道
系统 SHALL 在运行 OpenSpec discovery 之前依据共享质量参考判定当前请求。仅当需求明确、非行为性、局部低风险、当前主会话可完成，且无更严格项目记录要求、显式 OpenSpec/选定 change 续接或正式交接需要时，使用无需 change 的快速通道。

#### Scenario: 有 OpenSpec 的项目修正文档错别字
- **WHEN** 用户请求局部文档纠错，符合全部资格，即使仓库已有未归档 change
- **THEN** 主路由直接执行，不列出候选，不要求新建/复用，不修改任何任务状态文件

#### Scenario: CLI 不可用但请求独立符合资格
- **WHEN** 用户请求符合资格的格式/文案修正，未安装 OpenSpec CLI
- **THEN** 主路由无需调用 CLI，不要求初始化项目，执行后报告相关验证

### Requirement: 快速通道保留真实验证和对话收尾
系统 SHALL 保留范围/diff 检查和项目要求的最小相关检查，在对话中报告执行事实。系统 SHALL NOT 为快速工作创建正式 artifacts、替代任务记录、委派或默认独立审核。

#### Scenario: 已选快速通道进入规划或收尾入口
- **WHEN** 模型随后调用 plan-solution 或 finish-with-evidence
- **THEN** 入口消费主路由的快速判定并返回主路由/对话交付，不强迫创建 proposal、tasks 或 verification，不冒称独立审核 CLEAN

#### Scenario: 快速检查没有通过
- **WHEN** 最小相关验证失败或无法执行
- **THEN** 报告失败/NOT RUN 及原因，不声称已验证通过；若处理需要扩大范围，先停止并升级

### Requirement: 不合格工作保留正式合同
系统 SHALL 对行为修复、功能/重构、高风险或依赖变更、显式 OpenSpec/已选 change 续接、正式计划/跨会话交接/委派要求及更严格项目规则使用正式流程。系统 SHALL 保留当前的发现、创建/复用确认、TDD、审核预算和用户验收归档规则。

#### Scenario: 看似很小的权限或行为修复
- **WHEN** 用户称为“简单”，但改动影响权限或可观察行为
- **THEN** 系统不按文件数或用户的“简单”措辞跳过正式流程；CLI 故障仍是阻塞而不是快速资格

#### Scenario: 快速执行中发现范围扩大
- **WHEN** 局部文案工作实际需要接口或行为变更、跨会话交接或委派
- **THEN** 系统停止扩大实现，保留现有 diff 和已执行检查，再按原确认规则进入正式流程；不自动建 change、不自动清理已有修改

#### Scenario: 用户明确继续已选 change
- **WHEN** 当前请求是已有选定 change 的小型收尾工作
- **THEN** 沿用该 change 的正式记录及其既有确认状态，不因改动小而丢弃任务链路或重置审核预算
