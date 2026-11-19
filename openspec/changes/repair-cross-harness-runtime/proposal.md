# 提案：简化 OMP 工作流适配

## Why

OMP 项目 overlay 缺少 `project-standards`，默认安装又依赖同级的旧审查扩展。OpenSpec 已记录交付审查预算，OMP 可以通过原生角色和专用审查角色执行工作流。

## What Changes

- 普通 `omp` 成为默认入口，保留 `ompw` 和 overlay 供显式使用。
- `OMP`、`Both` 和 `All` 安装不再依赖外部 gate，保留用户已有的扩展。
- doctor 验证共享技能、适用的技能白名单及角色安装，并将 OMP 实际派发标为 `UNVERIFIED`。
- 探查优先使用原生 `scout`，专项规划和正式交付审查保留工作流角色。以真实派发结果决定有界实现是否默认使用原生 `task`。

## 验收标准

- AC-001 — 已有的项目和用户级 overlay 纳入 `project-standards`。doctor 对存在的白名单漏项给出诊断。
- AC-002 — 缺少同级外部 gate 时，`OMP`、`Both`、`All` 可安装，升级保留既有扩展，`-WhatIf` 无写入，重复安装保持幂等。
- AC-003 — 缺少可选启动器、overlay 或 gate 时，常规安装可通过 doctor。doctor 通过静态检查后明确报告实际派发为 `UNVERIFIED`。
- AC-004 — 隔离环境运行安装和仓库测试。实际运行 OMP 验证技能和审查角色，分别记录每项结果。验证原生 `task` 的文件边界、测试证据、模型与 prewalk 行为后再切换默认实现角色。

## Capabilities

### New Capabilities

- `omp-project-workflow-configuration` — OMP 的工作流安装、配置诊断及角色路由。

### Modified Capabilities

- 无。

## Impact

涉及安装与诊断脚本、OMP overlay、共享技能、测试及说明。外部 gate 由其所属仓库维护。真实运行探针使用隔离项目，沿用本机现有 OMP 模型配置。
