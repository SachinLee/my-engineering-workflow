## ADDED Requirements

### Requirement: 交付级有限审核预算
工作流 MUST 对 Standard / Critical 的一个已批准交付范围使用一次完整独立 `workflow-reviewer` 审核，存在具体阻断问题时最多一次定向复核。它 MUST 不默认叠加 `code-reviewer`、Matt 原生审核或另一个综合 reviewer。风险等级只改变相关验证深度。

#### Scenario: 正常交付
- **WHEN** 交付范围实现完成且相关检查通过
- **THEN** 主路由派发一次完整审核，满足门禁后记录证据并交给用户验收

#### Scenario: 切片完成
- **WHEN** 仅完成同一交付范围内一个实现切片
- **THEN** 运行该切片相关检查，不自动进行完整独立审核

### Requirement: 阻断发现与定向复核
审核 MUST 为阻断发现提供违反的 AC、项目规则或不变量、具体失败场景和影响。可选简化或偏好 MUST 作为非阻断建议。定向复核 MUST 只检查原阻断 findings、修复差异与直接受影响路径；未解决问题或新阻断问题在预算用尽时 MUST 报告 `blocked`，不得继续自动循环或伪造 `CLEAN`。

#### Scenario: 修复完成
- **WHEN** 一次完整审核的阻断问题已集中修复且受影响检查通过
- **THEN** 最多一次定向复核，不重新征集整套优化建议

#### Scenario: 预算用尽
- **WHEN** 定向复核后仍存在阻断发现
- **THEN** 主路由记录阻塞和下一步，交给用户决定后续，不继续自动派发

### Requirement: 复用与授权边界
工作流 MUST 将审核范围、有效轮数、报告、findings 和修复检查记录在现有 change artifacts；续接和 snapshot 变化 MUST 不自动重置预算。一次 `INVALID` 受控替换只适用于未形成有效审核报告的派发失败，不得绕过有效审核预算。材料重大变化使覆盖失效时 MUST 请求用户批准重新完整审核或拆分交付。

#### Scenario: 非阻断与证据追加
- **WHEN** 报告只有非阻断建议，或仅追加不改变实质输入的交付记录
- **THEN** 复用有效审核，不重新审核

#### Scenario: 覆盖失效
- **WHEN** 用户变更验收标准或实现改变接口、安全边界、方案以及未覆盖模块
- **THEN** 报告失效范围并等待用户决定，不自动完整重审

### Requirement: 收尾只核对并记录证据
`finish-with-evidence` MUST 消费同 change 同材料的完整相关验证和独立审核证据，核对 staged、unstaged、显式 untracked 范围以及 Standards / Spec 覆盖。它 MUST 不派发 reviewer 或直接重跑仓库验证。发现缺失或过期证据时 MUST 返回主路由补相关检查；只有门禁满足时才能交接 `awaiting-acceptance`。

#### Scenario: 有效证据
- **WHEN** 验证与审核证据对应最终交付内容且阻断问题已解决
- **THEN** 收尾记录事实、逐条 AC、剩余风险和用户验证步骤，不增加检查轮次

#### Scenario: 证据缺口
- **WHEN** 报告缺失、范围不全或输入实质变化
- **THEN** 报告 `UNVERIFIED` 和具体缺口，返回主路由，不假称正常完成
