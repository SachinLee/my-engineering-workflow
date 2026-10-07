# Context：会话意图匹配与确认式任务路由

## 目标（AC 摘要，逐字）

- AC-001：无同义任务时建议创建——展示名称、change id、目标和理由；确认前没有新目录，确认后创建正确任务。
- AC-002：有同义任务时建议复用——不同措辞表达同一目标时能推荐已有任务；确认后复用，不重复创建。
- AC-003：仅有一个任务也不能自动选中——未确认前不激活；目标不同时建议新建。
- AC-004：多候选由用户决定——展示候选差异；不按最新、名称顺序或模型偏好直接执行。
- AC-005：拒绝、取消和调整不会越权执行。
- AC-006：确认不产生循环——确认回答直接处理当前建议；新独立请求重新匹配。
- AC-007：候选范围正确——排除归档和其他项目；保留已完成未归档并说明状态。
- AC-008：相关不等于同义——关键词相近但目标不同的任务不能直接推荐。
- AC-009：错误不能伪装成无匹配——环境故障报告阻塞。
- AC-010：同名创建不覆盖；过期确认停止。
- AC-011：复用保留已有工作——不清空需求、执行状态或旧验证证据。
- AC-012：安装后目标项目可用——各 harness 安装资源含 helper；诊断无副作用。

## 关键事实（file:line，切片 2/3 依赖）

- `scripts/openspec_compat.py:169-241` `detect_project_mode()`：现单 change 自动选中（:194-206），多 change BLOCKED "Multiple active OpenSpec changes require an explicit change id."。要改为 `change=None` 一律 `unselected` + `available_changes=names`；显式 change 路径（:207-226 校验 not listed / 读 status）保持不变。
- `scripts/openspec_compat.py` 工具函数：`_executable`/`_check_version`/`_json_command`（追加 `--json`）/`_has_openspec_root`/`_result`。`CHANGE_ID_RE = ^[a-z0-9][a-z0-9-]*$`；`MIN_OPENSPEC_VERSION = (1,14,0)`；`REQUIRED_STATUS_KEYS = {changeName, artifacts, isPlanningComplete, isComplete}`。模块 `__main__` raise SystemExit，只能 import。
- 真实 CLI 1.14.1：创建命令 `openspec new change <name> --description <text> --goal <text> --schema <name> --json`；重复创建同名 exit 1，错误含 "already exists"。
- `scripts/doctor.py:145-157` `check_record_layout`：blocked → error "OpenSpec record system is not usable"；unselected → warning "has no active change selected"。改为：unselected 且 `available_changes` 非空 → warning 列出候选（不算环境不可用）。
- `tests/test_openspec_compat.py:13-42` FAKE_CLI：支持 `--version`/`list`/`status`，`FAKE_OPENSPEC_MODE` ∈ single/multiple/empty/malformed。要加 `new change` 子命令：成功时写 argv JSON 到 cwd 的 `.new-change-args.json` 并输出创建 payload；`FAKE_OPENSPEC_NEW=duplicate` 时输出 `{"status":[{"message":"Change 'alpha' already exists at <path>"}]}` exit 1。现有 test_selects_single_open_spec_change 与 test_blocks_multiple_open_spec_changes 断言旧行为，随行为变更改写。
- `scripts/install.ps1`：分发 seam 在四个 harness 分支（Codex :211-221、OMP :222-256、Claude :258-285、Pi :287-311）。每个分支 `Sync-SkillDirectory` 之后追加 `Copy-ManagedFile -Source scripts\openspec_compat.py -Target <skills root>\run-engineering-workflow\scripts\openspec_compat.py`。`Assert-ManagedChild` 校验目标在 root 下；Codex/Pi Project 模式 skills root 是 `.agents\skills`。
- 契约测试必须保留的短语：SKILL.md 含 `openspec list --json`、`Active change: openspec/changes`、`do not initialize one silently`、`at most one live writer`、`Do not automatically re-dispatch`；governance 含 `## Acceptance And Archival`、`do not dual-write`；install.ps1 不匹配 Trellis forbidden 正则。

## 复用模式

- 新函数沿用 `_result()` 构造返回 dict、`CompatibilityError` 报错；`create_change` 失败时提取 `_json_error_message(payload)`。
- evals case 遵循 schema_version 3：`name`/`state`/`expected_stage`/`forbidden`/`required_*`；handoff 字段白名单不变。
- OpenSpec 产物语言：中文正文 + 英文标识符/路径/状态 token（AGENTS.md 规则）。

## 验证命令

```
python -m unittest tests.test_openspec_compat -v
node --test tests/contracts.test.js
pwsh -File scripts/install.ps1 -Harness All -Scope Project -ProjectPath <tmp> -WhatIf
```
