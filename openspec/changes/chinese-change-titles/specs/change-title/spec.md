# Spec Delta

## Purpose

定义"change 各工件中可由 OpenSpec 读取和展示的中文标题"这一能力：约束 `proposal.md` 的 H1 写法与 section 结构，使其能被 OpenSpec 的 title 提取与校验机制读取；约束配置与 skill 中的标题规则来源；并为 compat/doctor 提供对标题的回读与回退展示。目的是让未归档 OpenSpec 任务以可辨认的中文标题出现在列表与路由确认中。

## ADDED Requirements

### Requirement: proposal H1 必须是中文标题
每个新 change 的 `proposal.md` 第一行 H1 SHALL 写成 `# 提案：<中文短标题>`，且 MUST 保留英文 section 名 `## Why` 与 `## What Changes`（中文说明可放在这两个 section 内或其他子段），以保证 OpenSpec 的 title 提取（`/^#\s+(?:Change:\s+)?(.+)$/`）与本仓库 markdown 解析器对 Why/What Changes 的识别始终成立。

#### Scenario: 新提案带中文 H1
- **WHEN** 为一个新 change 编写 `proposal.md`
- **THEN** 其第一行是 `# 提案：<中文短标题>`，并包含 `## Why` 与 `## What Changes` 两个英文段名
- **AND** `scripts/openspec_compat.py` 的 `_change_titles` 从该 H1 读出的标题等于该中文标题

#### Scenario: 缺少英文 section 名导致标题不可读
- **WHEN** 某 change 的 `proposal.md` 只有中文段名（如 `## 目标`、`## 范围内`）而没有 `## Why` / `## What Changes`
- **THEN** 该 change 的 `title` 无法被 OpenSpec 回读（表现为 `(unable to read)` 或校验报错），因此不得作为标题来源的约定形式

### Requirement: 标题规则进入机器可读来源
标题写作规则 SHALL 出现在 `openspec/config.yaml` 的 `rules.proposal` 与 `.pi/skills/openspec-propose/SKILL.md`（及其手工同步的 `.agents`/`.claude`/`.omp` 副本；这些副本不由 `install.ps1` 分发，且会被 `openspec update --force` 重写）中，使 `openspec instructions proposal` 与各 harness 的新建流程默认采用该约定。

#### Scenario: config 规则生效
- **WHEN** 运行 `openspec instructions proposal --change <name> --json`
- **THEN** 返回的 `rules` 数组包含一条要求"proposal H1 写为 `# 提案：<中文短标题>` 且保留 `## Why` / `## What Changes` 英文段名"的规则

### Requirement: 规则随创建流程落到项目

由于新项目的 `openspec/config.yaml` 里 `rules:` 整块是注释示例，且 `openspec new change` 不生成 `proposal.md`（由 agent 依据 `openspec instructions proposal` 现场编写），工作流 SHALL 在创建 change 时幂等地把 H1 规则写入项目配置，使规则在 agent 读取 instructions 之前就位；对规则引入前已存在的项目，`doctor.py` SHALL 在缺该规则时告警。

写入 MUST 为纯文本插入并保持幂等：仅在规则缺失时追加，保留模板注释块与用户已有规则，不改写既有配置。

#### Scenario: 创建 change 时补齐规则
- **WHEN** 在一个 config 尚无生效 `rules` 的项目里通过 `create_change` 创建 change
- **THEN** `create_change` 返回的 `title_rule.status` 为 `updated`，且随后 `openspec instructions proposal --change <name> --json` 的 `rules` 包含 H1 规则

#### Scenario: 重复创建不重复写入
- **WHEN** 在已有该规则的项目里再次调用 `create_change` 或 `ensure_proposal_title_rule`
- **THEN** 返回 `title_rule.status` 为 `unchanged`，且 `config.yaml` 内容逐字节不变

#### Scenario: 保留用户配置与模板注释
- **WHEN** 项目 config 中已有 `rules.proposal` 条目或 init 留下的注释示例
- **THEN** 插入后这些内容全部保留，新规则追加进既有 `rules.proposal` 列表而非替换它

#### Scenario: 老项目缺规则时可见
- **WHEN** 对已初始化但缺 H1 规则的项目运行 `python scripts/doctor.py`
- **THEN** 输出一条指出该 config 缺 proposal H1 规则的 WARNING，且不修改任何文件

### Requirement: compat 脚本回传中文标题
`scripts/openspec_compat.py` 的 `list_changes` 回传的每个 change SHALL 携带 `id` 与 `title`（`title` 为可回读的中文标题；回读失败或缺失时回退为 `id`），使路由确认与 `doctor.py` 的 unselected 提示能展示 `id（中文标题）`，且不得因标题回读失败改变现有的 blocked/unselected 语义。

#### Scenario: 回传带中文标题的候选
- **WHEN** 调用 `list_changes` 且存在 `proposal.md` H1 为中文的 change
- **THEN** 返回的 `available_changes` 中该 change 包含 `title` 等于其中文 H1，且 `id` 保持不变

#### Scenario: 标题缺失时回退为 id
- **WHEN** 某 change 没有可回读的 `proposal.md` 标题
- **THEN** 其 `title` 等于其 `id`，返回仍为 `ready`/`unselected` 语义，不进入 blocked

### Requirement: 契约测试覆盖标题规则
本仓库的仓库级契约测试 SHALL 断言标题规则确实落入 `openspec/config.yaml` 的 `rules.proposal` 与 `openspec-propose` skill，且 compat 脚本的标题回读/回退有对应的单元测试。

#### Scenario: 契约测试断言规则存在
- **WHEN** 运行 `tests/contracts.test.js`
- **THEN** 断言 `openspec/config.yaml` 的 `rules.proposal` 与 `.pi/skills/openspec-propose/SKILL.md` 包含中文 H1 标题规则

#### Scenario: compat 标题单元测试通过
- **WHEN** 运行 `tests/test_openspec_compat.py`

### Requirement: 用户可脱离 agent 自查任务

`scripts/openspec_compat.py` SHALL 提供一个只读的命令行入口，使人类不依赖 agent 也能列出未归档 change 的 `id` 与其可读中文标题。该入口 SHALL 只读：不得包含创建、更新、归档等任何写子命令。当终端编码无法表示中文标题时，SHALL 降级输出而不是因 `UnicodeEncodeError` 终止，以保证 `id` 始终可见。

#### Scenario: 列出 id 与中文标题
- **WHEN** 在已初始化 OpenSpec 的项目中运行 `python scripts/openspec_compat.py list`
- **THEN** 每个未归档 change 打印一行 `id` 与其中文标题，退出码为 0

#### Scenario: 无标题时不重复打印 id
- **WHEN** 某 change 没有可读标题（回读结果等于其 `id`）
- **THEN** 该行只打印一次 `id`，不打印 `id  id`

#### Scenario: 环境异常时报因而非乱猜
- **WHEN** 目标目录不是 OpenSpec 项目或根目录不存在
- **THEN** 向 stderr 打印 `blocked: <原因>`，退出码为 1，不输出任何候选

#### Scenario: 控制台无法表示中文
- **WHEN** 标准输出编码为 `ascii` 等无法表示中文的编码
- **THEN** 标题降级为替换字符且进程正常退出，`id` 仍完整可见

#### Scenario: 命令行入口保持只读
- **WHEN** 检查该入口注册的子命令
- **THEN** 只存在 `list`（以及隐式的 `--help`），不存在任何写子命令
- **THEN** 包含"标题回读"与"标题缺失回退为 id"两个测试用例，且全部通过