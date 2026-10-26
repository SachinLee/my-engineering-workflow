# Context：让 OpenSpec 任务以中文标题出现在列表与路由确认中

## 目标（AC 摘要，逐字）

- AC-001：新 change 的 `proposal.md` 第一行是 `# 提案：<中文短标题>`，且含 `## Why` 与 `## What Changes` 两个英文段名；标题读取直接取该 H1（不依赖 `openspec show`）。
- AC-002：只写中文段名（`## 目标`、`## 范围内`）而没有 `## Why` / `## What Changes` 的 proposal 判定为不合规形式，不得作为约定形式推广。
- AC-003：`openspec instructions proposal --change <name> --json` 返回的 `rules` 数组含"proposal H1 写 `# 提案：<中文短标题>` 且保留 `## Why` / `## What Changes` 英文段名"这条规则。
- AC-004：`.pi/skills/openspec-propose/SKILL.md` 与 `.agents`/`.claude`/`.omp` 三份 harness 副本含同一指引，且四份内容一致（除已知的 apply 提示差异）。
- AC-005：`list_changes` 返回的 `available_changes` 仍是 id 字符串列表（语义不变），并新增 `change_titles`（id → 标题）；有可读 H1 时映射为中文标题。
- AC-006：标题缺失或不可读时 `change_titles[id] == id`，`status` 仍为 `ready`/`unselected`，不进入 blocked。
- AC-007：`proposal.md` 缺失、不可读或 H1 为 `# Proposal`/空时**不阻塞**，`change_titles` 该 id 回退为 id 本身。
- AC-008：`tests/contracts.test.js` 断言 config rule 与 skill 指引存在，`node --test tests/contracts.test.js` 全绿。
- AC-009：`tests/test_openspec_compat.py` 含"标题映射 / 缺失回退 / 子命令不可用不阻塞"三类用例，`python -m unittest tests.test_openspec_compat` 全绿。

## 关键事实（file:line，各切片依赖）

### 切片 1 依赖

- `openspec/config.yaml:10-21`：`rules:` 下 `proposal:` 目前只有一条 `- State the motivation, scope, non-goals, assumptions, and acceptance criteria in Chinese.`（第 12 行）。新增规则追加在其后，保持 YAML 列表缩进 4 空格。
- `.pi/skills/openspec-propose/SKILL.md:42`：`**Input**: The user's request should include a change name (kebab-case) OR a description ...`；`:51`：`From their description, derive a kebab-case name (e.g., "add user authentication" → \`add-user-auth\`).`。指引加在此处，紧接 kebab-case 派生之后。
- harness 副本路径：`.agents/skills/openspec-propose/SKILL.md`、`.claude/skills/openspec-propose/SKILL.md`、`.omp/skills/openspec-propose/SKILL.md`。`.pi` 与 `.agents` 当前仅第 155 行 apply 提示不同（`/opsx-apply` vs `$openspec-apply-change`），其余一致。
- `openspec instructions proposal --json` 的 `rules` 字段来自 `config.yaml` 的 `rules.proposal`；改完立即生效，无需重装。

### 切片 2 依赖

- `scripts/openspec_compat.py:21` `MIN_OPENSPEC_VERSION = (1, 14, 0)`；`:23` `CHANGE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")`。
- `scripts/openspec_compat.py:73-100` `_json_command(executable, project, args, timeout)`：内部已追加 `--json` 并解析 stdout，JSON 解析失败抛 `CompatibilityError(f"OpenSpec returned invalid JSON...")`。**标题读取不走它**（见切片 2 第一条），它只服务于 `openspec list` 与 `openspec status`。
- `scripts/openspec_compat.py:192-207` `_open_spec_names(...) -> Tuple[str, List[str], Dict[str, str]]`：返回 `(version, names, titles)`，`names` 来自 `listing["changes"][i]["name"]`，`titles` 来自 `_change_titles`。
- `scripts/openspec_compat.py:174-200` `_change_titles(root, names) -> Dict[str, str]`：**直接读** `openspec/changes/<id>/proposal.md`，用 `TITLE_RE = re.compile(r"^#\s+(?:Change:\s+)?(.+)$")`（镜像 OpenSpec 自身 `extractTitle`）取第一条 H1；`OSError` 吞掉，标题为空/等于 `proposal`/等于 id 时回退为 id。不再调 `openspec show`（见切片 2 首条），也不调 deprecated 的 `openspec change list`。
- `scripts/openspec_compat.py:213-238` `list_changes(...)`：`return _result("openspec", "ready", "openspec", openspec_version=version, available_changes=names, change_titles=titles)`。
- `scripts/openspec_compat.py:280-300` `detect_project_mode(...)`：`version, names, titles = _open_spec_names(...)`；`unselected` 分支同时带 `available_changes=names` 与 `change_titles=titles`；`not listed` 分支保持只带 `available_changes`。
- `scripts/openspec_compat.py:150-166` `_result(mode, status, source, change=None, reason=None, **details)`：`**details` 直接并入 payload，新增字段无需改 `_result`。
- 真实 CLI 事实（本机 1.14.1，仓库内 8 个真实 change 实测）：`openspec show <id> --json` 对 6 个中文段名的 change 一律失败 `Change must have a Why section`，且每次约 1 秒进程开销 —— 所以标题改为读磁盘上的 `proposal.md`。`openspec show` 在写对英文段名的 change 上仍返回 `title`（临时目录演练：写 `# 提案：中文演练标题` 后 `title` 即该中文串）。`openspec change list --json` 也能读 title，但会打 deprecated 警告。
- 判断"不可读/回退"的口径：`proposal.md` 读不到（`OSError`）、H1 文本为空、等于 `proposal`（大小写不敏感）、或等于 id 时，一律用 id 填充 `change_titles[id]`。

### 切片 3 依赖

- `scripts/doctor.py:189-206` `check_record_layout`：`:198` `candidates = result.get("available_changes") or []`，`:202` `f"{', '.join(candidates)}. The routing flow recommends one and asks for confirmation; nothing is auto-selected."`。改为用 `result.get("change_titles") or {}` 拼 `f"{cid}（{title}）"`，`title` 缺省或等于 `cid` 时只显示 `cid`。
- `skills/run-engineering-workflow/SKILL.md`：匹配确认段落在 `## Match And Confirm Before Creating Or Reusing`（`:113` 起）。契约测试强制保留短语：`openspec list --json`、`Active change: openspec/changes`、`do not initialize one silently`、`at most one live writer`、`Do not automatically re-dispatch`——改动不得删除这些短语。
- `scripts/install.ps1` 用 `Copy-ManagedFile` 把 `scripts/openspec_compat.py` 与 `skills/run-engineering-workflow/` 分发到各 harness；切片 3.3 也可直接跑一次安装器而不手抄副本。

### 切片 4 依赖

- `tests/contracts.test.js:12-14` `read(relativePath)` 基于 `path.resolve(__dirname, "..")` 读仓库相对路径，可直接 `read("openspec/config.yaml")` 与 `read(".pi/skills/openspec-propose/SKILL.md")`。
- `tests/contracts.test.js:367` 现有 `test("workflow policies define one owner for every durable artifact", ...)` 之后可追加新 test；文件共 1005 行、50 个 test。
- `tests/test_openspec_compat.py:21-63` `FAKE_CLI` 脚本：`sys.argv[1:2]` 分支处理 `--version` / `list` / `status` / `new change`。新增 `sys.argv[1:3] == ["change", "list"]` 分支，受 `FAKE_OPENSPEC_MODE` 控制（例如 `titled` / `untitled` / `no-change-list`）。
- 现有断言必须保持不变：`self.assertEqual(result["available_changes"], ["alpha"])`（`:99`、`:107`、`:152`）。

### 切片 5/6 依赖

- `README.md:204` 现有表述："确认提示会包含中文任务名、change id、目标摘要和推荐理由"；实现后该表述才真正成立，若实现范围不足需回写。
- `openspec/changes/chinese-change-titles/artifacts/verification.md` 尚不存在，切片 6.2 创建。

## 复用模式

- 新返回值沿用 `_result(**details)`，不新增返回结构；错误统一 `CompatibilityError`，由 `list_changes`/`detect_project_mode` 捕获转 `blocked`。
- 新增的标题读取必须容错：`_change_titles` 内部逐个 `try/except OSError`，单个 id 失败只回退为自身，绝不让它冒泡成 `blocked`（AC-007）。
- 契约测试沿用 `read()` + `assert.match`；Python 测试沿用 `unittest` + `FAKE_CLI` 子进程边界，不 mock 函数。
- OpenSpec 产物语言：中文正文 + 英文标识符/路径/状态 token（`AGENTS.md` 规则）。

## 验证命令

```
openspec validate chinese-change-titles --type change --strict
openspec instructions proposal --change chinese-change-titles --json | python -c "import sys,json;print(json.load(sys.stdin)['rules'])"
python -m unittest tests.test_openspec_compat -v
node --test tests/contracts.test.js
head -1 openspec/changes/<id>/proposal.md
pwsh -File scripts/install.ps1 -Harness All -Scope Project -ProjectPath <tmp> -WhatIf
```