# 验证记录：让 OpenSpec 任务以中文标题出现在列表与路由确认中

状态：`awaiting-acceptance`（等待用户验收；未归档）

复核情况：
- 同上下文自查：修掉 4 处缺陷并补回归用例（见「计划外发现与处理」4-6）。
- 独立模型复核（`del_mvosxonn_ilph`）：`VERDICT: 通过`。逐条回答：① 无崩溃路径，IO 由 `except OSError` 覆盖；② `##` 二级标题正确排除，但代码围栏内 `# 注释` 会被误抓（LOW）；③ `utf-8-sig` + `errors="replace"` 组合正确，BOM 剥离后 `^#` 锚点不受影响；④ `doctor.py:211` 三态判断安全，无 `foo（foo）` 冗余；⑤ 无 BLOCKER。
- 该 LOW 瑕疵已修：`_change_titles` 增加围栏状态跟踪（`line.lstrip().startswith("```")` 翻转 `in_fence`），并补用例 `test_fenced_code_hash_lines_are_not_titles`。
- 第一次派发的复核（`del_mvorsscl_9sns`）跑满 30 分钟被 watchdog 终止、无结论，已作废并用窄范围限时任务重派。

## 证据逐条

| AC | 结论 | 证据 |
| --- | --- | --- |
| AC-001 | 通过 | `openspec/config.yaml` 的 `rules.proposal` 新增 H1 规则；四份 `openspec-propose/SKILL.md` 同步指引；`_change_titles` 从 H1 取值（不依赖 `openspec show`）。用例 `test_unselected_routing_carries_readable_titles`。 |
| AC-002 | 通过 | `design.md` 决策 2 明确中文段名只作为 `## Why` / `## What Changes` 之内子段；`proposal.md` / `specs/change-title/spec.md` 同步该口径。 |
| AC-003 | 通过 | `openspec instructions proposal --change chinese-change-titles --json` 的 `rules` 含新增条目（下方命令可复现）。 |
| AC-004 | 通过 | `.pi` / `.agents` / `.claude` / `.omp` 四份 `openspec-propose/SKILL.md` 指引文本一致，仅既有 apply 提示差异保留。 |
| AC-005 | 通过 | `list_changes(Path('.'))` 返回 `available_changes` 为 id 字符串列表 + `change_titles` 映射；实测 8 个真实 change 中 7 个读出中文标题。 |
| AC-006 | 通过 | 用例 `test_placeholder_title_falls_back_to_change_id`、`test_bare_heading_without_text_falls_back_to_change_id`；`status` 保持 `ready`/`unselected`。 |
| AC-007 | 通过 | 用例 `test_missing_proposal_falls_back_to_change_id`、`test_show_failure_never_blocks_routing`（fake CLI 的 `show` 恒失败，路由仍 `unselected` 且 `reason is None`）。 |
| AC-008 | 通过 | `node --test tests/contracts.test.js` → `pass 44 / fail 0`，含用例 `OpenSpec changes carry a readable Chinese title in listings and routing`。 |
| AC-009 | 通过 | `python -m unittest discover -s tests` → `Ran 50 tests ... OK (skipped=1)`；`tests/test_openspec_compat.py` 新增 7 个标题用例（含 `test_non_heading_hash_lines_are_not_titles`、`test_fenced_code_hash_lines_are_not_titles`）。 |
| AC-010 | 通过 | 切片 7：`ensure_proposal_title_rule` 幂等补规则，`create_change` 回传 `title_rule`，`doctor.py` 对老项目告警。真实 CLI 端到端演练见「缺口归因与修复」。用例 6 个 + 契约测试 1 个。 |
| AC-011 | 通过 | 切片 8：`_main` + `list` 子命令（只读）与 `_safe_print` 编码降级。实测本仓库 8 个 change 中 7 个打印中文标题、`openspec-compatibility` 按设计只打 id；`PYTHONIOENCODING=ascii` 下降级为 `?` 且退出码 0；未初始化目录打印 `blocked: OpenSpec is not initialized in this project.` 且退出码 1。用例 4 个 + 契约测试 1 个。 |

## 复现命令

```bash
node --test tests/contracts.test.js
python -m unittest discover -s tests
python scripts/doctor.py
openspec instructions proposal --change chinese-change-titles --json
python scripts/openspec_compat.py list
# 切片 7 端到端（在干净目录里跑）：
#   openspec init --language Chinese --tools none
#   python -c "from pathlib import Path; from openspec_compat import create_change; print(create_change(Path('.'), 'demo', description='d', goal='g'))"
#   openspec instructions proposal --change demo --json   # rules 应含 H1 规则
```

`list_changes` 实读结果（`PYTHONIOENCODING=utf-8`，本仓库）：

```
chinese-change-titles               => 提案：让 OpenSpec 任务以中文标题出现在列表与路由确认中
unify-shared-skill-installation     => 统一共享 Skills 安装
allow-simple-work-without-change    => 提案：简单工作免建 OpenSpec 任务
limit-delivery-review-rounds        => 限制交付审核轮数
sync-matt-upstream-review-policy    => 同步 Matt 上游约定并统一审查策略
remove-subagent-time-limits         => 移除子代理执行时间限制
confirm-intent-based-change-routing => Proposal：会话意图匹配与确认式任务路由
openspec-compatibility              => openspec-compatibility   ← H1 仍是 `# Proposal`，按设计回退为 id
```

## 计划外发现与处理

1. **`openspec show <id> --json` 在本仓库大面积失败**：8 个真实 change 有 6 个报 `Change must have a Why section`（中文段名不满足 OpenSpec markdown 解析器），每次调用约 1 秒。设计原定走 `show`，实测后改为直接读 `proposal.md` 的 H1（零进程、不受段名影响）。`design.md`、`tasks.md` 2.1/2.2/5.1、`specs/change-title/spec.md`、`proposal.md`、`README.md` 均已同步为新口径。
2. **`openspec-compatibility` 的 H1 仍是 `# Proposal`**：这是既有 change，按 AC-006 回退为 id，不修改它的历史记录。
3. **旧 change 的历史 H1 不回填**：本 change 只保证新 change 默认带中文标题；历史 change 需要时手工补 H1（属用户决定，不自动改写）。
4. **`detect_project_mode` 的 "not listed" 分支补了 `change_titles`**：原先只有 `available_changes`，同一 payload 的两个分支字段不一致会让调用方按需读 `change_titles` 时出现 `KeyError`；已对齐。
5. **`_change_titles` 加了 id 合法性守卫**：只处理匹配 `CHANGE_ID_RE`（`^[a-z0-9][a-z0-9-]*$`）的 id，避免未来上游返回异常名字时拼出越界路径。
6. **`utf-8-sig` 读取**：`proposal.md` 用 `encoding="utf-8-sig"` 读，避免带 BOM 的文件让 H1 行变成 BOM + `# ...` 而匹配失败。用例 `test_non_heading_hash_lines_are_not_titles` 同时锁定了「只有行首 `#` 才算 H1」（缩进注释、`#hashtag` 不算）。

## 未做（显式非目标）

- 不改上游 OpenSpec（`dist/` 不 patch），`openspec list` 原生仍只显示 id。
- 不改 change 目录名（`isKebabId` 锁死 `[a-z0-9-]`）。
- 不自动回填历史 change 的 H1。
- 不修「生成源」层（`openspec-propose/SKILL.md` 的指引仍会被 `openspec update --force` 重写）——规则已在 config 层独立成立，见下「缺口归因与修复」。

## 缺口归因与修复（安装到本地时暴露，已在本 change 内修）

**症状**：本 change 起初只在**本仓库**生效，新项目里新建的 change 仍落成 `# Proposal`，列表继续显示英文 id。

三层归因（干净目录 `openspec init --language Chinese --tools pi` 实测），**只有中间一层是断的**：

| 层 | 位置 | 修复前 | 修复后 |
| --- | --- | --- | --- |
| 读取侧 | `_change_titles` 读 `proposal.md` H1 | **通**（`list_changes` → `status: ready`） | 不变 |
| 写入侧 | agent 按 instructions 写 `proposal.md` H1 | **断**，落成 `# Proposal` | `create_change` 补规则 → **通** |
| 生成源 | `openspec-propose/SKILL.md` 指引 | 断且易失 | 断且易失（**刻意不再依赖**） |

断裂的直接证据：

- `openspec new change <id>` 只建 `openspec/changes/<id>/.openspec.yaml`（`schema` / `created`），**不建 `proposal.md`**；`proposal.md` 由 agent 依 `openspec instructions proposal` 现场编写。
- `openspec instructions proposal --change <id> --json` → `rules: None`，`template` 首行 `# Proposal`，`instruction` 不含「提案」。
- 根因：init 生成的 `config.yaml` 里 `rules:` **整块是注释示例**；`context` 只有「用中文」三行。
- 反证：往 `config.yaml` 加生效 `rules.proposal` 后，同一命令立刻返回该规则 → 机制没问题，缺的是规则落点。

**关键边界（实测，修正了先前的猜测）**：

- `openspec update --force` **不覆盖** `config.yaml`（放 `MARKER_ACTIVE_RULE_H1` 进去跑 update，标记仍在）→ config 里的规则**持久**。
- `openspec update --force` **覆盖** `openspec-propose/SKILL.md`（放入含 1 处「提案」的文件 → update 后变回 0）→ skill 文件的手工编辑**易失**。

### 采取的修法（切片 7）

因为规则在 config 里持久、且 `openspec instructions` 会自动把它喂给 agent，修法全部落在 config：

- `scripts/openspec_compat.py` 新增 `TITLE_RULE_ANCHOR`、`_config_file`、`ensure_proposal_title_rule`：**纯文本插入**（不做 YAML round-trip，否则会丢模板注释块与用户注释），只在锚点缺失时写入，幂等。
- `create_change` 在 `openspec new change` 成功后调用它并回传 `title_rule` —— 时机关键：规则必须在 agent 读 instructions **之前**就位。
- `scripts/doctor.py` 新增 `_check_proposal_title_rule`，对缺规则的**老项目**告警（只读，不改文件），并复用 compat 的常量避免两处漂移。
- 刻意**未**采用「让 `install.ps1` 分发 skill 副本」：那类改动会被 `openspec update --force` 抹掉。

### 修复验证（真实 CLI 端到端）

```
干净目录 openspec init --language Chinese
  → config.yaml 含 H1 规则: False，含生效 rules 块: False
create_change('.', 'add-user-auth', ...)
  → status: created, title_rule: {'status': 'updated'}
openspec instructions proposal --change add-user-auth --json
  → rules 条数: 1  ★ 含 `# 提案：<中文短标题>`
再次 create_change('.', 'add-logout', ...)
  → title_rule: {'status': 'unchanged'}，config 与首次逐字节相同（幂等）
写入 proposal.md 的 `# 提案：增加用户认证` 后 list_changes
  → add-user-auth => 提案：增加用户认证（完整读写闭环）
移除规则块模拟老项目 → doctor 输出缺规则的 WARNING
本仓库（已有规则）→ doctor 无该 WARNING
```

插入后 `config.yaml` 的模板注释块（`#   rules:` / `#     proposal:` 等）与用户已有 `rules.proposal` 条目均完整保留。

### 本 change 未做的部分

- 「生成源」层仍断：`openspec-propose/SKILL.md` 的 H1 指引仍会随 `openspec update --force` 丢失。这是**刻意接受**的——规则已在 config 层独立成立，不依赖该副本；不再把正确性押在易失文件上。

## 用户自查入口（切片 8）

**动因**：用户问「加这个 cli 的作用是什么」。此前标题只在 agent 的推荐/确认提示里可见，用户想自己找任务时**没有可用命令**：`openspec list` 只打印英文 id，而 `openspec change list --long` 对 8 个 change 里的 2 个打印 `(unable to read)`（中文段名让上游解析器吞掉整条），且该组命令已 deprecated。

**做法**：`scripts/openspec_compat.py` 增加只读 CLI（原先末尾是 `raise SystemExit("Import this module from doctor, migration commands, or tests.")`，无任何入口）：

```
python scripts/openspec_compat.py list [--project <dir>]
```

输出 `id` 左对齐 + 中文标题；无子命令打印 help 并返回 2；项目不存在或未初始化时把 `list_changes` 的 `reason` 作为 `blocked: <原因>` 打到 stderr 并返回 1。

**边界**：
- **只读**。只注册 `list` 一个子命令，写操作仍只能经 `create_change` / `migrate_workflow_task`，契约测试对此加了负向断言。
- **不改变 `openspec` 原生输出**。终端直接敲 `openspec list` 仍是英文 id，改它需要改上游，本 change 明确不做。
- **编码降级**：`_safe_print` 在控制台编码无法表示中文时用 replacement 字符输出，宁可丢标题也不能丢 id —— id 是所有 openspec 命令的入参。实测 `PYTHONIOENCODING=ascii` 时标题变 `????`，退出码仍为 0。

**实测（本仓库）**：8 个未归档 change 中 7 个打印出中文标题，`openspec-compatibility` 因 H1 仍是 `# Proposal` 按设计只打印 id。
