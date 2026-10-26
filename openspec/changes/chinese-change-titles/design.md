# Design：让 OpenSpec 任务以中文标题出现在列表与路由确认中

## 决策

1. **标题的唯一来源是 `proposal.md` 的 H1，不改目录名**：OpenSpec CLI 的 `isKebabId` 把 change id 锁死在 `[a-z0-9-]`（`dist/utils/change-utils.js:42-66`），`openspec new change <中文>` 直接报 `Change name can only contain lowercase letters, numbers, and hyphens`。因此中文只能进 H1，`dist/commands/change.js:505-510` 的 `extractTitle` 正是读它，且 `title.toLowerCase() !== 'proposal'` 才不回退 id。
2. **保留 `## Why` / `## What Changes` 英文段名**：`dist/core/parsers/markdown-parser.js:40-47` 缺任一 section 就抛 `Change must have a Why section` / `... What Changes section`，`show --json` 与 `change list --long` 随之失败，`archive` 也会打警告。中文段名（`## 目标`、`## 范围内`）必须作为 Why/What Changes **之内**的子段，而不是替换它们。这是本方案与既有 `clarify-requirements` 中文段名约定的调和点：段名保留英文，内容与子段标题保持中文。
3. **规则下沉到 config + skill，而非只写文档**：`openspec/config.yaml` 的 `rules.proposal` 会经 `openspec instructions proposal --json` 的 `rules` 字段直接进入模型上下文，比 README 约定更硬；`openspec-propose` skill 覆盖不走 instructions 的 harness。两处都写，规则才在所有入口生效。
4. **compat 脚本直接读 `proposal.md` 的 H1 取 title，不调 `openspec show`**：`openspec list --json` 的键只有 `name/completedTasks/totalTasks/lastModified/status`（无 title）；`openspec change list --json` 返回 title 但整组 `openspec change ...` 已 deprecated（1.14.1 每次调用向 stderr 打两行警告）。原本计划用 `openspec show <id> --json`，实测本仓库 8 个真实 change 有 6 个直接失败 `Change must have a Why section`（中文段名不满足 markdown 解析器），且每次调用约 1 秒进程开销。因此改为 `_change_titles(root, names)` 直接读 `openspec/changes/<id>/proposal.md`，用与上游 `extractTitle` 同形的正则 `^#\s+(?:Change:\s+)?(.+)$` 取第一条 H1：零进程、不受段名影响、单次失败只让该 id 回退为自身，绝不冒泡成 `blocked`。
5. **向后兼容的 `available_changes` 结构**：当前 `available_changes` 是 `List[str]`，被 `scripts/doctor.py:198`（`', '.join(candidates)`）与既有测试（`assertEqual(result["available_changes"], ["alpha"])`）依赖。改为 `List[Dict]` 会破坏这两处。折中：保留 `available_changes: List[str]`（id 列表）不变，**新增** `change_titles: Dict[str, str]`（id → 标题）。doctor 用 `change_titles` 拼展示串，无标题时退回 id。这样零破坏、零迁移。
6. **标题回读失败不回退语义**：`title` 缺失/不可读时用 id 填充（与 OpenSpec 自身 `extractTitle` 的回退一致），`list_changes` 仍返回 `ready`，`detect_project_mode` 仍返回 `unselected`。标题是展示层增强，不参与 blocked 判定。
7. **不改上游 OpenSpec**：让 `openspec list` 原生显示 title 属于上游 feature，本地不 patch `node_modules`（不可复现、升级即失效）。

## 备选方案

- **给 `openspec` 包打补丁让 `list` 显示 title**：被否——`node_modules` 修改不随仓库分发，`openspec update` 会覆盖。
- **用 `openspec/changes/INDEX.md` 维护 id↔中文标题映射**：被否——多一份需要人工同步的持久状态，违反"OpenSpec 是唯一持有者"；且标题已在 `proposal.md` 里，属重复数据。
- **把 `available_changes` 直接改成 `[{id,title}]`**：被否——破坏 doctor 与现有 2 个测试，且没有任何外部收益；新增并列字段即可。
- **让 skill 要求把中文标题写进 `.openspec.yaml` 的 `goal`**：被否——实测 `title` 不读 `goal`，`openspec validate` 还会对未知键告警；`goal` 保留原用途。

## 数据流

新建 change：`openspec new change <kebab-id>` → agent 按 config `rules.proposal` + skill 指引写 `# 提案：<中文短标题>` + `## Why` / `## What Changes` → `_change_titles` 从该 H1 读到中文标题。

路由发现：`list_changes()` → `openspec list --json`（校验 root/版本/候选 id）→ `_change_titles(root, names)` 读每个 `proposal.md` 的 H1 → 返回 `available_changes`（id 列表）+ `change_titles`（id→title）→ 主会话用 `id（中文标题）` 组装推荐与确认提示 → `doctor.py` 同样拼展示串。

## 测试接缝

- `tests/test_openspec_compat.py`：用临时目录写 `proposal.md`（中文 H1、`# Proposal` 占位、`Change:` 前缀、空 H1、文件缺失、非标题 `#` 行、代码围栏内 `#` 行七种），断言 `available_changes` 仍是 id 列表、`change_titles` 正确映射、不可读时回退为 id、且 `openspec show` 失败不影响路由。
- `tests/contracts.test.js`：断言 `openspec/config.yaml` 的 `rules.proposal` 含中文 H1 规则；断言 `.pi/skills/openspec-propose/SKILL.md` 含"H1 写中文标题 + 保留 Why/What Changes"指引；断言 compat 的标题读取不依赖 `openspec show`、也不再调 deprecated 的 `change list`。
- 真实 CLI 演练：本仓库 `list_changes` 对 8 个真实 change 全部返回非空 `change_titles`（中文 H1 的 change 读出中文标题，其余回退 id）；临时目录新建 change 写中文 H1 后，`_change_titles` 读到中文标题。

## 回滚

纯增量：删掉 config 里新增的那条 rule、skill 里新增的那段指引、`change_titles` 字段与 doctor 的展示改动，即可完全回到当前行为。无数据迁移、无持久状态、无破坏性接口变更（`available_changes` 语义不变）。

## AC 映射

AC-001/002 → spec "proposal H1 必须是中文标题"；AC-003/004 → spec "标题规则进入机器可读来源"；AC-005/006/007 → spec "compat 脚本回传中文标题"；AC-008/009 → spec "契约测试覆盖标题规则" + 本文件测试接缝。