# 上下文包

## 安装与诊断

- 范围与验收 — `proposal.md` 的 AC-001 至 AC-003，及 `design.md` 的安装和诊断部分。
- 现状 — `scripts/install.ps1` 从仓库同级 `omp-extensions` 读取 gate 并复制至目标，`scripts/doctor.py` 以静态 gate 检查作为 OMP 必需项。`config/omp-workflow.yml` 已列出 `project-standards`，项目副本漏项。
- 可写 — `scripts/install.ps1`、`scripts/doctor.py`、`.omp/engineering-workflow.yml`、这些行为的现有测试。技能正文及 README 由主会话负责。
- 保持 — 兼容入口、角色及已有扩展，其他宿主、用户模型配置、权限、历史变更。先编写并运行契约测试，再改行为。
- 验证 — `npm test`、Python 安装和 doctor 测试。隔离测试 `OMP`、`Both`、`All` 及 `-WhatIf`。

## OMP 角色路由与交付

- 范围与验收 — AC-004，普通入口和角色路由由主会话验证，独立审查覆盖所有本 change 改动。
- 现状 — 原生 `scout`、`task` 可用，`workflow-reviewer` 提供当前交付协议。角色切换依赖实际运行证据。
- 可写 — 主会话负责 `README.md`、canonical 工作流技能和相应合同。独立审查只读。
- 验证 — 仓库测试、隔离会话工具结果及角色证据、独立审查结果。
