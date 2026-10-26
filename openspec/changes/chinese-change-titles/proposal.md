# 提案：让 OpenSpec 任务以中文标题出现在列表与路由确认中

## Why

未归档的 OpenSpec change 目录名只能是 kebab-case 英文 id，而用户日常通过 `openspec list` 只看到英文 id，难以辨认对应任务。虽然 `proposal.md` 的 H1 可承载任意语言标题（`openspec change list --long` / `show --json` 会读它），但当前 `proposal.md` 的 H1 默认是模板自带的 `# Proposal` 或未落为中文，且本仓库约定用中文段名（`## 目标`、`## 范围内`）——而 OpenSpec 的 markdown 解析器只识别英文段名 `## Why` / `## What Changes`，导致多数现有 change 的 `title` 读不出来（显示 `(unable to read)`）。同时 `scripts/openspec_compat.py` 的 `list_changes` 只从 `openspec list --json` 拿 `name`（英文 id），路由确认提示里不会出现中文标题——这与 README 承诺的"确认提示会包含中文任务名"不符。

## What Changes

- 定一条可执行的写作约定：每个新 change 的 `proposal.md` 第一行 H1 写 `# 提案：<中文短标题>`，并保留英文段名 `## Why` / `## What Changes`（中文内容可继续放在 `## 目标` 等子段），使 OpenSpec 的 `title` 提取与解析始终成立。
- 把该约定下沉为机器可读的规则：在 `openspec/config.yaml` 的 `rules.proposal` 中新增一条 `Title (H1) 一行写成 提案：<中文短标题>，保留 ## Why 与 ## What Changes 英文段名`，让 `openspec instructions proposal` 把此规则喂给模型。
- 在 `.pi/skills/openspec-propose/SKILL.md`（以及手工保持一致的 `.agents`/`.claude`/`.omp` 副本；这些副本**不由** `scripts/install.ps1` 分发，见 verification 的"已知缺口"）的提案步骤里补一条"H1 写中文标题且保留英文 section 名"的指引，确保所有 harness 的新建 change 默认带中文标题。
- 扩展 `scripts/openspec_compat.py` 的 `list_changes`：新增 `_change_titles` 直接读每个 `proposal.md` 的 H1，回传 `change_titles`（id → 标题），使路由确认、`doctor.py` 的 unselected 提示能显示 `id（中文标题）`；读不到标题时优雅回退为 id，不改变现有 blocked/unselected 语义。
- 增加契约测试覆盖上述规则与回退行为。

## Capabilities

### New Capabilities
- `change-title`: 定义"change 各工件中可由 OpenSpec 读取和展示的中文标题"这一能力，约束 `proposal.md` H1 写法、配置与 skill 中的标题规则来源，以及 compat/doctor 对标题的回读与展示。

### Modified Capabilities

## Impact

- `openspec/config.yaml`：`rules.proposal` 增一条 H1 中文标题规则。
- `.pi/skills/openspec-propose/SKILL.md` 及其手工同步的 `.agents`/`.claude`/`.omp` 副本（**不由** `install.ps1` 分发；且会被 `openspec update --force` 按 CLI 模板重写而丢失）：新增标题写作指引。
- `scripts/openspec_compat.py`：`_open_spec_names` / `list_changes` 增加 `title` 回读与回退；`available_changes` 结构向后兼容（仍含 `id`，新增 `title`）。
- `scripts/doctor.py`：unselected 提示可显示中文标题（若该 change 有可回读标题）；已初始化项目缺 H1 规则时告警（只读）。
- `scripts/openspec_compat.py`（切片 7）：新增 `ensure_proposal_title_rule`，`create_change` 调用它把规则落到**项目**的 `openspec/config.yaml`，否则新项目的 change 仍写 `# Proposal`（规则原本只在配置里手工存在的项目生效）。
- 测试：`tests/test_openspec_compat.py` 增标题回读/回退用例（含切片 7 的 6 个规则注入用例），`tests/contracts.test.js` 增规则存在性与「规则随创建流程落到项目」断言。
- `scripts/openspec_compat.py`（切片 8）：新增只读 CLI 入口 `_main` + `list` 子命令与 `_safe_print`，让用户不依赖 agent 也能查 `id` + 中文标题；原先该模块无任何入口（末尾为拒绝运行的 `SystemExit`）。
- `skills/run-engineering-workflow/SKILL.md`（+ `.agents`/`.claude`/`.omp` 三副本，手工同步）：补充「用户想自己查任务时运行 `openspec_compat.py list`」的指引。