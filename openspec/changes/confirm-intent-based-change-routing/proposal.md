# Proposal：会话意图匹配与确认式任务路由

## Why

当前 `run-engineering-workflow` 要求每次新工作都手动确认 change 归属：单 change 自动选中，多 change 直接 BLOCKED。用户要消除"手动敲 `openspec new change`"的负担，但保留任务归属与创建决定权——系统按会话意图与未归档 changes 语义匹配后**推荐**新建或复用，**必须经用户确认**才执行创建或选择。

取代 `openspec-compatibility` 中"多 change 未显式选择即 BLOCKED"的交互：多候选不再是环境故障，而是等待用户决定的正常状态。

## What Changes

- **主路由（SKILL.md）**：每次任务路由请求触发"只读发现 → 语义匹配 → 推荐 → 等确认"流程；无同义建议创建，有同义建议复用，多候选展示差异；新建与复用都强制确认。
- **兼容模块（scripts/openspec_compat.py）**：新增只读 `list_changes()`、显式 `create_change()`；`detect_project_mode()` 不再按数量自动选中（单 change 也不自动选中，改为 unselected + 候选列表），显式 change 路径保持不变。
- **诊断（scripts/doctor.py）**：unselected 且有候选时报告候选清单，不算环境不可用。
- **安装（scripts/install.ps1）**：把 `openspec_compat.py` 随 skill 分发到各 harness 的 `run-engineering-workflow/scripts/`，保持单一源实现。
- **行为契约（tests、evals）**：先补发现/创建/冲突/确认行为覆盖，再改实现。

## Impact

- 受影响 specs：`workflow-compatibility`（本 change 以新能力 `task-routing` 表达增量；归档合并时并入 `openspec-compatibility` 的 "Resolve one canonical task mode" 要求）。
- 行为变化：单 change 不再自动选中；多 change 不再 BLOCKED。显式指定 change 的行为不变。
- 不修改 OpenSpec 上游；不引入关键词分类器、向量库或相似度阈值；语义判断留在主会话。
