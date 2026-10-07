# Spec Delta

## Purpose

让工作流按会话意图与未归档 OpenSpec changes 语义匹配后推荐新建或复用，并强制用户确认后执行，消除手动创建命令，同时保留任务归属决定权。归档合并时，本能力的要求并入 `workflow-compatibility` 的 "Resolve one canonical task mode"。

## ADDED Requirements

### Requirement: 匹配结果必须先征得用户确认
The system SHALL 按会话意图与当前项目未归档 changes 语义匹配后，仅向用户提出建议；创建 change 与选择 active change 都 SHALL 在用户明确确认后执行。

#### Scenario: 无同义任务时建议创建
- **WHEN** 会话目标与所有未归档 changes 都不同义
- **THEN** 系统给出含中文名、change id、目标摘要与理由的创建建议，等待确认；确认前不创建目录、不写入任何记录

#### Scenario: 有同义任务时建议复用
- **WHEN** 某个未归档 change 与会话目标同义（同一工作目标、范围兼容）
- **THEN** 系统给出复用建议并说明该 change 的当前状态；确认后复用，不重复创建

#### Scenario: 仅一个候选也不自动选中
- **WHEN** 当前项目只有一个未归档 change 且用户未确认
- **THEN** 系统不自动选中它；目标一致时仍须确认复用，目标不同时建议新建

### Requirement: 多候选由用户决定
The system SHALL 在多个合理候选时展示各候选的差异，由用户选择复用其一、新建或取消；SHALL NOT 按时间顺序、名称顺序或模型偏好自动执行。

#### Scenario: 多个未归档 change
- **WHEN** 只读发现返回多个未归档 change 且其中不止一个可能相关
- **THEN** 系统列出候选及各自状态与范围差异，等待用户选择

### Requirement: 候选范围限定当前项目未归档 changes
The system SHALL 仅把当前项目 `openspec/changes/` 下未归档的 changes 作为匹配候选；归档目录、`.workflow/`、`.trellis/` 与其他项目的记录 SHALL NOT 进入复用推荐；未归档不等于未完成，推荐复用 SHALL 说明已有状态。

#### Scenario: 归档与其他项目记录被排除
- **WHEN** 匹配候选中存在已归档 change 或其他项目的记录
- **THEN** 它们不参与推荐；已完成但未归档的 change 仍参与并标注状态

### Requirement: 确认语义与失效
The system SHALL 把用户确认限定为对当前建议的一次性授权：拒绝复用不等于同意新建；调整名称或范围后重新确认；候选消失、被归档或目标实质变化后原确认失效并停止；确认创建或复用不等于批准实现方案、验收或归档。

#### Scenario: 过期确认停止执行
- **WHEN** 用户确认后、执行前候选被归档或目标已实质变化
- **THEN** 系统停止本次执行，重新匹配并再次征求确认，不沿用旧确认

### Requirement: 错误不伪装成无匹配
The system SHALL 在 CLI 缺失、版本过旧、JSON 无效、根目录不符或候选读取失败时报告阻塞；SHALL NOT 把环境故障当作"无同义任务"而建议创建。

#### Scenario: 环境故障与无匹配区分
- **WHEN** OpenSpec CLI 缺失或返回无效输出
- **THEN** 系统报告阻塞与可操作的修复信息，不提出创建建议
