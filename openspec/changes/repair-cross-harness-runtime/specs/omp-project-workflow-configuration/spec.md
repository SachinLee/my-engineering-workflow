# OMP 项目工作流配置

## Purpose

定义普通 OMP 会话的工作流安装、项目规范技能发现、静态诊断与正式交付审查角色行为。

## ADDED Requirements

### Requirement: OMP overlay 暴露项目规范技能

工作流随附的 OMP overlay SHALL 将 `project-standards` 纳入 `includeSkills`。安装器同步配置时 SHALL 保留该入口。

#### Scenario: 显式使用项目 overlay

- **WHEN** OMP 会话通过兼容启动器使用项目 overlay
- **THEN** 选中的 overlay 允许发现 `project-standards`

### Requirement: OMP 安装独立于旧审查扩展

`OMP`、`Both` 和 `All` 安装 SHALL 支持普通 `omp` 入口。安装 SHALL NOT 要求同级 `omp-extensions/workflow-review-gate` 或覆盖既有 gate。

#### Scenario: 缺少外部源码

- **WHEN** 用户在同级 gate 源码缺失时安装任一包含 OMP 的模式
- **THEN** 该模式安装共享技能及工作流角色

#### Scenario: 安装预演和已有扩展

- **WHEN** 用户预演安装或升级含既有 gate 的目标
- **THEN** 预演无写入，升级保留既有 gate

### Requirement: Doctor 诊断常规安装并报告运行证据边界

Doctor SHALL 检查共享技能、工作流角色和适用的技能白名单。Doctor SHALL 将实际角色派发标为 `UNVERIFIED`，可选 launcher、overlay 与 gate 的缺失 SHALL NOT 造成诊断失败。

#### Scenario: 白名单漏项

- **WHEN** 适用的非空技能白名单缺少 `project-standards`
- **THEN** doctor 报告缺少的技能及配置路径

#### Scenario: 普通安装

- **WHEN** 常规静态检查通过且可选组件缺失
- **THEN** doctor 通过静态检查并报告角色派发为 `UNVERIFIED`

### Requirement: 正式 OMP 交付使用工作流审查协议

主会话 SHALL 按 OpenSpec 质量配置控制正式评审轮次，并派发 `workflow-reviewer` 获取 `REVIEW_STATUS`。

#### Scenario: OMP 正式交付评审

- **WHEN** 工作流质量配置要求正式评审
- **THEN** 主会话派发带有 OpenSpec 变更与评审证据的 `workflow-reviewer` 请求
