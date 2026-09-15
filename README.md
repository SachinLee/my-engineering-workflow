# 我的 AI 工程工作流

这是一个面向个人开发习惯的 AI 工程工作流仓库。它把 `.workflow/` 文件约定、Matt Pocock
Skills 和 Ponytail 中适合自己的部分组合起来，用于提高需求质量、
代码质量、验证质量，以及不同 AI 会话之间的上下文连续性。

本仓库不是上述项目的完整替代品，也不复制它们的源码。它是一个轻量编排层，
负责规定：任务状态保存在哪里（纯文件，无 CLI 和注入）、需求和方案写到哪里、何时使用
TDD、需要执行哪些验证，以及任务结束后要为后续 AI 会话保留什么证据。

## 这个仓库是做什么的

这个工作流主要解决以下问题：

- AI 没有充分理解需求就开始实现。
- 需求、方案和实现过程只存在于聊天记录中，后续难以追踪。
- 切换 Codex、Claude Code 或新的 AI 会话后，需要重新解释项目背景。
- 代码虽然能运行，但缺少 TDD、回归测试、类型检查、安全检查等证据。
- AI 容易增加不必要的抽象、依赖、配置和文件。
- 计划中的方案和最终实际实现存在偏差，但没有被记录。

各部分在本工作流中的职责如下：

| 组件 | 职责 | 本仓库如何使用 |
| --- | --- | --- |
| `.workflow/` 约定 | 任务状态、需求、设计、上下文清单、证据、日志 | 唯一记录系统；纯文件，由 skill 用读写工具维护，无 CLI、无 hook、无每轮注入 |
| Matt Pocock Skills | 需求追问、领域建模、TDD、模块边界、双轴 review | 作为默认工程方法 |
| Ponytail | YAGNI、复用、stdlib/native 优先 | 只用于复杂度控制，不降低质量要求 |

本仓库目前提供五个 skill：

| Skill | 用途 |
| --- | --- |
| `$run-engineering-workflow` | 读取 `.workflow/` 中的当前任务状态，按风险等级路由整个开发流程 |
| `$clarify-requirements` | 澄清需求，并把可验证的验收标准写入当前任务的 `prd.md` |
| `$plan-solution` | 设计技术方案，把决策与执行步骤写入 `design.md` 和 `implement.md`，并给出 `context.md` 读取清单 |
| `$review-implementation` | 使用独立上下文复核需求覆盖、正确性、测试、安全和复杂度 |
| `$finish-with-evidence` | 执行最终检查，并把实际实现和验证证据写入 `outcome.md` |

## 核心产物

在使用本工作流的项目中，`.workflow/` 是任务记录的唯一来源：

| 文件 | 内容 |
| --- | --- |
| `.workflow/tasks/<task>/prd.md` | 需求、范围、非目标、假设和带复选框的验收标准 |
| `.workflow/tasks/<task>/design.md` | 技术方案、接口、数据流、兼容性和取舍 |
| `.workflow/tasks/<task>/implement.md` | 实施顺序、测试计划、验证命令和回滚点 |
| `.workflow/tasks/<task>/tickets/NN-<slug>.md` | 跨会话或多 writer 时的工单：covers、blocked_by、state、writer |
| `.workflow/tasks/<task>/context.md` | 本任务必须读取的规范、代码和研究文件清单（含一句理由） |
| `.workflow/tasks/<task>/STATUS` | 当前阶段（planning / in_progress / review / done）和时间戳 |
| `.workflow/tasks/<task>/outcome.md` | 实际实现、逐条 AC 结果、RED/GREEN、独立复核、验证结果和剩余风险 |
| `.workflow/CURRENT.md`、`.workflow/by-session/` | 任务指针：人可读的当前任务，以及每个会话自己的绑定 |
| `.workflow/spec/` | 跨任务长期有效的规范、约定和踩坑经验 |
| `.workflow/journal.md`、`.workflow/archive/` | 一行一次收口记录，以及已归档任务的只读历史 |
| `CONTEXT.md` | 可选的领域词汇表，不存放技术方案 |
| `docs/adr/` | 少量难以逆转且存在真实权衡的架构决策 |

旧项目里已有的 `.trellis/` 仍可作为只读历史被读取（同名产物），但本工作流不再调用
Trellis 脚本、不再安装它的注入扩展，新状态一律写入 `.workflow/`。

## 产物用什么语言

所有面向人的产物（`prd.md`、`design.md`、`implement.md`、`context.md`、`outcome.md`、
`journal.md`、工单正文）用中文书写，包括小标题和字段名；代码标识符、文件路径、
命令、日志原文，以及状态记号（`PASS`、`NOT RUN`、`REVIEW_STATUS: CLEAN`）和 `STATUS`
的键名保持英文原样，方便 grep 与脚本解析。

## 为什么不自动注入任务上下文

旧做法是每轮把状态块塞到请求最前面。实测代价：一次状态变更会让整条历史前缀失效，
长会话里连续 20 个请求的 `cached_input_tokens` 死钉在 instructions + tools 的静态前缀
（18,944），约 40 分钟内 132 万 token 按全价输入计费。

本工作流改为按需读取：文件读取的结果追加在请求尾部，前缀保持稳定，阶段变化只多一次
读。因此约定是——不装 hook、不加 extension、不写启动注入块；主路由把“读指针 →
读 `STATUS` → 读产物”作为入口动作，并由硬性前置检查保证它真的发生（读不到任务路径就是
INVALID 派发，不允许进入实现）。

## 子代理拿到的上下文包

规划阶段每写一个切片，就同时把它对应的 **上下文包** 写进 `implement.md`。派发给
`workflow-implementer` / `workflow-planner` / `workflow-reviewer` 时整段贴进去：

```text
已内联上下文（子代理不需要再读原文）：
- 验收标准：本片 AC 整条原文
- 相关设计决策：design.md 对应小节的关键原文
- 已定位：file:line + 符号 + 结论
- 现成模式：可直接照抄结构的实现或测试文件，附关键片段
- 不变量：本片必须保持的行为
- 验证命令：确切命令（含 JDK、离线、模块参数）与预期输出要点

需要新打开（只列真正要读的）：
- 它将要编辑的那两三个文件
```

原则是：**主会话读过并据此做过判断的内容，一律内联**，只给路径就等于让子代理把
调研重做一遍。预算约每片 1500 token；超了就摘录决定性的那几行并标注出处，不要贴
整份文件。上下文包缺字段时，正确做法是回 `implement.md` 补全再派发，而不是放任子
代理自己扩大搜索——reviewer 会把这种情况作为流程问题报出来。

## 任务怎么拆

拆分的粒度由“实际怎么执行”决定，不按文档好看程度决定。三档从小到大：

| 档位 | 用在什么时候 | 写在哪里 |
| --- | --- | --- |
| 切片 | 同一会话内顺序完成、共享模块、只有一个 writer | `implement.md` 的 `### 切片 N` |
| 工单 | 每片能独立验收、需要跨会话续接、或多 writer 并行 | `tickets/NN-<slug>.md` |
| 多任务 | 不同发布单元、不同仓库、可各自独立收口 | 多个 task 目录 + 一个总控 task |

工单文件头部固定字段：

```text
---
id: T2
标题：摄像头状态 CAS 更新
covers: [AC-001]
blocked_by: [T1]
state: ready          # ready | in_progress | done | blocked
writer: main          # main | workflow-implementer
---
```

调度规则：frontier = 全部 `blocked_by` 已 `done` 的 `ready` 工单；一次工单只给一个
writer；验证命令真正跑过并把证据写进 `outcome.md` 后，才能把 `state` 改成 `done`。
换会话或换客户端续接时，重新读 `tickets/` 算 frontier，不靠上一段聊天回忆进度。
工单正文不重写切片计划，直接引用 `implement.md#切片-N` 和它的上下文包。

不要拆的情形：`lightweight` 任务、单一测试接缝、改动集中在一两个文件。拆分本身有
记账成本，不会自动带来质量。需要更大范围探路时，先走 Matt `wayfinder` 出决策地图，
再回到 `to-spec` / `to-tickets` 收拢成工单。


详细约定随主路由一起打包在
[workflow-governance.md](skills/run-engineering-workflow/references/workflow-governance.md)，
复制或安装 skill 后仍然可见。

## 需要安装什么

### 基础环境

- Git
- Node.js 18 或更高版本
- Python 3.9 或更高版本（只用于 `doctor.py` 和 OMP 启动脚本；工作流本身不执行任何脚本）
- Codex App / Codex CLI、Claude Code 2.1、Pi 0.84 或更高版本，按实际使用的平台安装
- 需要供应商无关的多模型角色映射时，可选 OMP 17.3.3 或更高版本

### 不需要安装：记录系统

任务状态就是 `.workflow/` 目录约定，由 skill 用平台自带的读写工具维护，不需要安装
CLI、插件或 hook。第一次在某个项目使用时，主路由会先征求同意再创建最小骨架：

```text
.workflow/
  CURRENT.md
  journal.md
  tasks/<MM-DD-slug>/
    prd.md
    STATUS
    context.md
```

如果项目里已有旧的 `.trellis/`，主路由会以只读方式接着使用它的任务产物，但不会执行
Trellis 脚本，也不会继续保留它的每轮上下文注入扩展。

### 可选安装：Matt Pocock Skills

本仓库已经吸收了基础需求澄清方法，因此不安装 Matt Skills 也能运行。需要更深入的
领域建模、模块边界和双轴 review 时再安装：

```bash
npx skills@latest add mattpocock/skills
```

Claude Code 也可以只选一种方式安装完整 plugin：

```bash
claude plugins install mattpocock-skills
```

建议选择：

- `grill-with-docs`
- `grilling`
- `domain-modeling`
- `codebase-design`

另外默认启用 `tdd`、`diagnosing-bugs` 和 `code-review`：`tdd` 是实现的默认方法，`code-review`
承担去掉 Trellis 之后的规范符合性与需求覆盖双轴检查。本仓库的 `review-implementation`
负责需要 fresh context 的任务级独立复核，两者不重复调用。

Matt 的 `to-spec`、`to-tickets`、`implement` 只作为方法使用，产物必须落在当前任务目录里
（例如票写到 `.workflow/tasks/<task-id>/tickets/`），不要让它们在 `.scratch/` 另起一套记录。

### 可选安装：Ponytail

Ponytail 适合检查过度设计，但不负责 correctness、安全和完整验证：

```bash
codex plugin marketplace add DietrichGebert/ponytail
codex plugin add ponytail@ponytail
```

Claude Code 中在会话内分别执行：

```text
/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail
```

安装后检查并信任它的 hooks。建议把默认模式设为 `off` 或 `lite`，只在需要时显式
调用 `ponytail-review` / `ponytail-audit`。不要用 Ponytail 的最小化规则替代项目自身的
测试要求。

Windows 可以在 `%APPDATA%\ponytail\config.json` 中设置：

```json
{
  "defaultMode": "off"
}
```

## 安装本仓库的 Skill

仅克隆本仓库不会自动让 Codex、Claude Code、OMP 或 Pi 发现这五个 skill。使用安装器
同步，避免升级后残留旧文件。

### 全局安装到 Codex

在本仓库根目录运行 PowerShell（Windows 使用 PowerShell，macOS / Linux 使用
PowerShell 7 `pwsh`）：

```powershell
.\scripts\install.ps1 -Scope User -Harness Codex
```

安装完成后重启 Codex App 或重新启动 Codex CLI。

### 全局安装到 Claude Code

```powershell
.\scripts\install.ps1 -Scope User -Harness Claude
.\scripts\doctor.ps1 -Scope User -Harness Claude
```

这会安装五个 skill、`workflow-planner` / `workflow-implementer` / `workflow-reviewer` 三个
agent 和 `/engineering-workflow`。重新启动 Claude Code 后生效。

### 全局安装到 Pi

```powershell
.\scripts\install.ps1 -Scope User -Harness Pi
.\scripts\doctor.ps1 -Scope User -Harness Pi
```

这会把五个 skill 安装到 `~/.pi/agent/skills/`，把 provider-independent 的
`workflow-planner` / `workflow-implementer` / `workflow-reviewer` 安装到 `~/.pi/agent/agents/`。Pi agent 默认省略
`model`，因此继承当前 Pi 模型；需要真正跨模型时，可以在安装副本或可信项目的同名
`.pi/agents/*.md` 中配置具体模型。设置了 `PI_CODING_AGENT_DIR` 时，安装器和 doctor 会改用
该用户目录。Pi 会在 `/reload` 或新会话后刷新 agent catalog。

方案规划、有界实现和独立复核需要 Pi subagents 扩展；没有它时主路由会在主会话内执行并记录缺少
独立上下文：

```powershell
pi install npm:@narumitw/pi-subagents
```

### 安装到项目，同时支持四个平台

目标项目不需要任何外部记录系统，直接安装即可：

```powershell
.\scripts\install.ps1 -Scope Project -Harness All -ProjectPath "D:\path\to\project"
.\scripts\doctor.ps1 -Scope Project -Harness All -ProjectPath "D:\path\to\project"
```

安装器会同步：

- 五个 canonical skill 到共享 `.agents/skills/`、`.omp/skills/` 和
  `.claude/skills/`；Pi 与 Codex 共用项目 `.agents/skills/`，不制造重复副本。
- 三个 OMP agent 到 `.omp/agents/`。
- OMP skill 白名单 overlay 和启动脚本到项目 `.omp/`。
- 三个 Claude agent 和 `/engineering-workflow` 到项目 `.claude/`。
- 三个 Pi agent 到 `.pi/agents/`。

安装器不会创建 `.trellis/`，也不会写入项目的 hook、extension 或 `.pi/settings.json`；
任务记录目录 `.workflow/` 由主路由在获得同意后按需创建。

只需要一个平台时使用 `Codex`、`OMP`、`Claude` 或 `Pi`。为兼容旧用法，`Both` 仍只表示
Codex + OMP；`All` 表示 Codex + OMP + Claude Code + Pi。先用 `-WhatIf` 可以预览安装器将替换的受管目录
和文件。

个人电脑推荐使用全局安装。项目级安装只用于团队需要把适配文件固定在仓库中，或某个
项目需要隔离版本的情况。无论采用哪种方式，任务记录 `.workflow/` 都必须留在项目仓库内
（并纳入版本控制），因为它保存该项目自己的任务状态和工程记录。

## 完整使用指南

### 一次性全局准备

Codex、Claude Code 和 Pi 的全局安装命令见上一节。需要经常使用 OMP 时，再全局安装一次
OMP adapter。也可以一次安装全部四个平台：

```powershell
.\scripts\install.ps1 -Scope User -Harness OMP
.\scripts\doctor.ps1 -Scope User -Harness OMP
.\scripts\install.ps1 -Scope User -Harness All
.\scripts\doctor.ps1 -Scope User -Harness All
```

全局安装后，不要再为每个项目复制本仓库的 skill。只有以下内容仍是项目级的：

- 项目自己的 `.workflow/` 任务记录（需要时由主路由创建）。
- 项目自己的 `AGENTS.md`、`CONTEXT.md`、`docs/adr/` 和 `.workflow/spec/`。
- 项目自己的测试命令、质量标准和模型配置。

因此，`install.ps1 -Scope User` 只需在本机执行一次；OMP launcher 可以从任意项目目录
启动。新项目不需要安装任何记录系统：第一次让主路由接手时，它会先询问是否创建
`.workflow/`。已有 `.trellis/` 的旧项目保持原样即可，本工作流只读取、不改动。

### 每个项目不需要初始化

本工作流没有 per-project 初始化命令。第一次在某个仓库使用时，主路由会先读取
`.workflow/CURRENT.md`；没有记录时先征求同意，再创建最小骨架：

```text
.workflow/
  CURRENT.md
  journal.md
  tasks/
```

之后每个任务一个目录，产物（`prd.md`、`STATUS`、`context.md`、收口后的
`outcome.md`）由 skill 直接用读写工具维护。需要把适配文件固定在仓库里的团队，改用
`-Scope Project -Harness All` 安装即可，记录目录本身仍然按需创建。

旧项目里已有的 `.trellis/` 不需要迁移或删除：主路由以只读方式接着使用它的任务产物，
新状态一律写入 `.workflow/`。

### 各客户端入口

| 客户端 | 启动方式 | 新需求入口 | 继续已有任务 |
| --- | --- | --- | --- |
| Codex App / CLI | 从项目根目录打开 Codex | `使用 $run-engineering-workflow 处理这个需求：...` | `使用 $run-engineering-workflow 继续当前任务。` |
| Claude Code | 从项目根目录运行 `claude --model sonnet` | `/engineering-workflow 处理这个需求：...` | `/engineering-workflow 继续当前任务` |
| OMP | 使用下面的全局 launcher | `使用 run-engineering-workflow 处理这个需求：...` | `使用 run-engineering-workflow 继续当前任务。` |
| Pi | 从受信任的项目根目录运行 `pi` | `/skill:run-engineering-workflow 处理这个需求：...` | `/skill:run-engineering-workflow 继续当前任务。` |
| 其他 skills-compatible 客户端 | 从项目根目录启动客户端 | 显式加载 `run-engineering-workflow` 并附带需求 | 显式加载同一 skill 并要求继续当前任务 |

OMP 全局安装后的启动方式：

```powershell
python "$HOME\.omp\agent\start-engineering-workflow.py" `
  --project-path "D:\path\to\project"
```

如果 Windows 没有启用 `python` 命令，使用 Python Launcher：

```powershell
py "$HOME\.omp\agent\start-engineering-workflow.py" `
  --project-path "D:\path\to\project"
```

macOS / Linux 使用：

```bash
python3 "$HOME/.omp/agent/start-engineering-workflow.py" \
  --project-path "/path/to/project"
```

launcher 会直接执行并启动 OMP，或在 `--web` 模式下启动/复用共享的 ompweb；它不是启动 OMP 之前的额外准备命令。
每次需要带本工作流启动一个新的 OMP 会话时使用 launcher，不要在它之后再运行一次 `omp`。

启动共享的 Web UI 使用 `--web`：

```powershell
ompw --web
```

`ompw --web` 只启动或复用一个 `ompweb` 服务，不会为每个项目目录创建新的 Web 服务。
Web UI 中的每个项目会按自己的 session cwd 启动 OMP RPC 子进程，但使用启动该 Web 服务时
解析出的同一个 workflow overlay。若服务已经运行，再从其他项目目录执行 `ompw --web` 时，
会复用已有服务；要切换 workflow 配置，先停止已有 ompweb 再重新启动。

PowerShell wrapper 会把参数放在 `--` 后转发，因此以下命令用于传递 Web 参数：

```powershell
ompw --web -- --no-open
ompw --web -- --port 30178
```


`--project-path` 默认是当前目录。因此从项目根目录启动时，可以省略该参数：

```powershell
py "$HOME\.omp\agent\start-engineering-workflow.py"
```

为了日常使用，推荐在 PowerShell `$PROFILE` 中定义一个用户级函数：

```powershell
function ompw {
  py "$HOME\.omp\agent\start-engineering-workflow.py" `
    --project-path "$PWD" -- @args
}
```

macOS / Linux 可在 `~/.zshrc` 或 `~/.bashrc` 中定义：

```bash
ompw() {
  python3 "$HOME/.omp/agent/start-engineering-workflow.py" \
    --project-path "$PWD" -- "$@"
}
```

重新加载 shell 配置后，从任意项目根目录只需运行 `ompw`。额外的 OMP 参数会原样转发，
例如 `ompw --continue` 或 `ompw --model opus`；`ompw --web` 则启动或复用共享的 Web UI。

完成用户级安装后，普通 `omp` 会读取 `~/.omp/agent/config.yml` 中的本工作流默认设置，加载 skill 白名单、`prewalk` 设置和 `@plan` / `@task` / `@advisor` 角色映射。重新启动 OMP 会话后直接运行：

```powershell
omp
```

`ompw` 仍然保留，适合在未安装用户级默认配置的机器上，或需要显式指定项目 overlay 时使用：

```powershell
ompw --continue
```

如果没有用户级默认配置，必须使用 Python launcher 或显式 `--config` 启动 OMP，普通 `omp` 不会自动加载本仓库的 workflow overlay。
### `ompw` 启动后怎么用

`ompw` 只负责打开已经配置好的 OMP。进入 OMP 后，直接把需求交给主路由：

```text
使用 run-engineering-workflow 处理这个需求：
为 Codex-Manager 增加一个导出项目配置的命令，要求支持 JSON 和 YAML，
保留现有配置格式，并补充单元测试和命令行验证。
```

正常情况下你只需要按主会话提示回答问题，并在方案完成后明确批准实现。主路由会自动按
以下顺序调度：

```text
需求澄清 -> 方案规划 -> 等待批准 -> @task TDD 实现
  -> code-review + 仓库检查 -> @advisor 独立复核 -> 修复并复验 -> 证据交付与归档
```

常用操作如下：

| 目的 | 在 OMP 主会话中输入 |
| --- | --- |
| 开始新需求 | `使用 run-engineering-workflow 处理这个需求：...` |
| 只澄清需求 | `使用 clarify-requirements 澄清当前需求，不要写代码。` |
| 只规划方案 | `使用 plan-solution 为当前任务生成 design.md、implement.md 和 context.md，不要实现。` |
| 批准后继续实现 | `继续当前任务，按已批准的 implement.md 使用 TDD 实现。` |
| 继续已有任务 | `使用 run-engineering-workflow 继续当前任务。` |
| 方案仍有争议 | `使用 grilling 逐项追问当前方案，并把结论写回当前任务。` |
| 需要领域建模 | `使用 domain-modeling 统一当前任务的领域术语和实体关系。` |
| 完成前单独复核 | `使用 review-implementation 从独立上下文复核当前实现。` |
| 最终交付 | `使用 finish-with-evidence 记录验证证据并关闭当前任务。` |

通常只使用第一条主路由即可；表中的单阶段调用只用于补做或强化某一阶段。实现模型、
复核模型和角色由 OMP overlay 自动分配：方案规划使用 `@plan`，TDD 实现使用 `@task`，
质量检查在主会话执行，独立复核使用 `@advisor`。用户不需要手动切换这些角色。

如果关闭 OMP 后重新打开，可使用 `ompw --continue` 恢复 OMP 会话；跨 Codex、Claude Code
或其他客户端时，优先输入“继续当前任务”，让新会话重新读取 `.workflow/` 中的任务产物。
磁盘上的记录才是共享事实来源，OMP 聊天记录只是辅助上下文。

Windows 上如果 `python` 无输出并以 `Exit: 49` 结束，通常是它解析到了 Microsoft Store 的
WindowsApps 占位程序。这只影响 `doctor.py` 与 OMP 启动脚本，不影响工作流本身；改用
Python Launcher `py` 即可，可用以下命令确认解析结果：

```powershell
Get-Command python, python3, py | Select-Object Name, Source
```

### 一次完整任务的阶段

1. **进入主路由**：读取 `.workflow/CURRENT.md` 或本会话指针和当前 task，确认是否需要创建任务。
2. **需求澄清**：把目标、范围、非目标、假设和带复选框的 AC（`- [ ] AC-001`）写入 `prd.md`。
3. **方案规划**：把技术决策写入 `design.md`，把 vertical slice、RED/GREEN 和验证命令
   写入 `implement.md`，并把后续 dispatch 必须读取的规范与研究文件写进 `context.md`。
4. **批准执行**：用户批准后把 `STATUS` 从 `planning` 改为 `in_progress`，不能由 AI 默认为
   已批准。
5. **TDD 实现**：先 RED，再最小 GREEN，然后重构；实现不得创建第二套计划记录。
6. **检查和复核**：先运行仓库自身检查与 Matt `code-review`，再从独立上下文运行
   `review-implementation`，修复 findings 后重新验证。
7. **证据交付**：把逐条 AC 结果、实际改动、RED/GREEN、命令输出和剩余风险写入
   `outcome.md`，然后把 `STATUS` 置为 `done`、追加一行 `journal.md`，并归档到
   `.workflow/archive/`。

通常只需要调用主路由。只有需要重新执行或单独强化某一阶段时，才直接调用
`clarify-requirements`、`plan-solution`、`review-implementation` 或
`finish-with-evidence`。

### 扩展能力怎么调用

| 场景 | 使用能力 | 结果写到哪里 |
| --- | --- | --- |
| 需求或方案仍含模糊决策 | Matt `grilling` | 结论整理回 `prd.md` 或 `design.md` |
| 统一业务术语和实体关系 | Matt `domain-modeling` | 稳定词汇写入 `CONTEXT.md`，真实架构决策写 ADR |
| 设计模块边界和测试 seam | Matt `codebase-design` | 方案写入当前 task 的 `design.md` |
| 功能或 bug fix | Matt `tdd` / `diagnosing-bugs` | 测试和代码；证据最终写 `outcome.md` |
| 发布前综合验证 | 仓库自身测试、lint、typecheck、build | 实际命令结果写 `outcome.md` |
| 安全敏感改动 | 项目自身安全工具和检查 | findings 返回主会话，修复后记录结果 |
| 正确性检查完成后压缩复杂度 | Ponytail review/audit | 修改代码并重新运行受影响检查 |

扩展只提供方法，不拥有任务状态。不要让 Matt 或 Ponytail 另建与当前任务目录重复的
PRD、ticket、plan 或 outcome。

### 默认调用顺序

主入口是 `$run-engineering-workflow`。它按 `.workflow/` 中的任务阶段选择以下能力：

| 阶段 | 默认调用 | 说明 |
| --- | --- | --- |
| 需求模糊 | `clarify-requirements`；复杂需求先用 Matt `grill-with-docs` | `grill-with-docs` 内部调用 `grilling` + `domain-modeling`，结论写入当前任务 `prd.md` |
| 方案设计 | `plan-solution` + Matt `codebase-design` | 生成 `design.md`、`implement.md` 和 `context.md` 读取清单 |
| 实现/修 bug | Matt `tdd`；疑难 bug 用 `diagnosing-bugs` | 默认在主会话执行；`critical` 才 dispatch `workflow-implementer`，遵循 RED/GREEN slice |
| 质量检查 | Matt `code-review` + 仓库自身检查 | 双轴：规范符合性与需求覆盖；不替代项目自己的测试 |
| 独立复核 | `review-implementation` + `ponytail-review` | 通过 `workflow-reviewer` 在新上下文执行；主会话负责修复 |
| 收尾 | `finish-with-evidence` | 把真实命令和结果写入 `outcome.md`，逐条勾 AC，再置 `done` 并归档 |

### 跨客户端和新会话续接

Codex、Claude Code、OMP、Pi 和其他客户端通过同一个工作树和 `.workflow/` 共享上下文，
不通过复制聊天记录共享。切换前确保本阶段结论已经写入正确产物；切换后从同一项目根目录
启动新客户端，然后要求继续当前任务。

新会话必须重新读取：

1. `.workflow/CURRENT.md`（或本会话指针）与当前 task 的 `STATUS`。
2. 当前 task 的 `prd.md`、`context.md`、`design.md`、`implement.md` 和已有 `outcome.md`。
3. 适用的 `.workflow/spec/`、代码、测试和 `git status` / `git diff`。

聊天摘要、自动 memory 和旧会话只可作为线索。它们与任务文件或代码冲突时，以任务
文件、Spec、代码和测试为准。未提交修改会通过同一工作树保留，但新客户端必须先区分
当前任务改动与用户已有改动。

### 其他客户端

本工作流不依赖平台专属 hook，因此 Cursor、OpenCode、Gemini CLI、Kiro、GitHub Copilot、
Qoder、CodeBuddy、Kimi Code 等任何支持 agentskills.io 的客户端都能直接使用：安装五个
skill，再在项目 `AGENTS.md` 中写明任务记录位于 `.workflow/` 即可。

本仓库安装器目前原生管理 Codex、Claude Code、OMP 和 Pi。其他支持 agentskills.io 的客户端
可使用 `skills` CLI 从本地仓库安装五个 canonical skill：

```powershell
npx skills@latest add "D:\my-works\claude-skills\my-engineering-workflow" `
  --global `
  --agent <agent-id> `
  --skill run-engineering-workflow clarify-requirements plan-solution review-implementation finish-with-evidence `
  --yes --copy --full-depth
```

`<agent-id>` 以 `npx skills@latest --help` 的当前输出为准。不要假设所有客户端都读取
`~/.agents/skills`；Claude Code 等平台仍有自己的目录和 agent/command 机制。

如果客户端只支持主会话 skill、不支持子 agent，仍按同一五阶段流程执行，但把实现、
检查和复核顺序放在主会话中，并明确记录未获得独立模型复核的剩余风险。若客户端完全
不支持 skill，直接要求它读取 `.workflow/CURRENT.md` 指向的任务产物，按五阶段执行；此时
本仓库的自动路由和质量加固不能视为已加载。

## Pi 工作流

Pi 原生扫描 `~/.pi/agent/skills/`、`~/.agents/skills/`、项目 `.pi/skills/` 和项目
`.agents/skills/`。使用 `-Harness Pi` 后无需 launcher；从已信任的项目根目录直接运行：

```powershell
pi
```

首次进入带 `.pi` 资源或项目 `.agents/skills` 的仓库时，Pi 会要求确认 project trust。
只有信任后，它才会加载项目 `.pi/` 资源、agents 和项目 skills。可在 Pi 中使用 `/trust`
管理决定，变更后重新启动或 `/reload`。

主入口是：

```text
/skill:run-engineering-workflow 处理这个需求：...
```

Pi 中的阶段分工如下：

| 阶段 | Pi 执行者 | 上下文/模型规则 |
| --- | --- | --- |
| 主路由、需求追问、批准、修复、交付 | 主会话 | 当前 Pi 模型 |
| 方案规划 | `workflow-planner` | blocking `subagent`；默认继承当前模型 |
| TDD 实现 | `workflow-implementer` | blocking `subagent`；默认继承当前模型 |
| 质量检查 | Matt `code-review` + 仓库自身检查 | 主会话执行，不派 agent |
| 最终只读复核 | `workflow-reviewer` | blocking `subagent`；默认继承当前模型 |

Pi 不读取 OMP 的 `engineering-workflow.yml`，也不识别 `@plan`、`@task`、`@advisor`。
本仓库的 Pi agents 因此不硬编码 `model`。若 planner/reviewer 没有配置不同模型，它们仍然
提供 fresh context，但不能称为跨模型复核。planner / implementer / reviewer 全部由本仓库
安装，任务上下文只通过 dispatch prompt 里的显式路径传递；缺少这些字段就是 INVALID 派发，
不允许靠扫描 `.workflow/tasks/` 猜测。

升级 Pi 或本仓库后检查：

```powershell
pi --version
.\scripts\doctor.ps1 -Scope User -Harness Pi
.\scripts\doctor.ps1 -Scope Project -Harness Pi -ProjectPath "D:\path\to\project"
```

## OMP 多模型工作流

OMP 默认会扫描 Codex、Claude、Agents 和 Pi/OMP 的用户级及项目级 skill。被发现的
主要是 skill 的 `name` 和 `description`；正文通常在触发后才加载。不过候选过多仍会
增加误触发和选择冲突，因此本仓库不依赖“让模型从全部 skill 中自行挑选”。

项目安装后从目标项目运行：

```bash
python ./.omp/start-engineering-workflow.py --project-path .
```

该脚本显式加载 `.omp/engineering-workflow.yml`，其中
`skills.includeSkills` 只保留本工作流、Matt 和 Ponytail 能力。
OMP 17.3.3 的项目 `.omp/config.yml` 只自动接管 `modelRoles`；把白名单仅写进该文件并
不能保证生效，所以不要绕过启动脚本。临时启动也可以使用：

```powershell
omp --cwd "D:\path\to\project" --config "D:\path\to\project\.omp\engineering-workflow.yml"
```

项目安装同时会从同级的
`D:\my-works\claude-skills\omp-extensions\workflow-review-gate` 同步 OMP extension 到
`.omp/extensions/workflow-review-gate`。它只阻止同一 `Active task + review profile +
worktree snapshot` 的重复最终审查；仓库检查和 `code-review` 不受它约束，修复产生新快照后仍
必须进行新的独立审查。扩展的短期状态写入 `.omp/.runtime/`，不替代 `.workflow/` 记录。

### OMP 升级后的检查

只更新 OMP 程序通常不会改动本仓库的 skill、launcher 或 overlay。升级后从本仓库根目录
执行一次：

```powershell
omp --version
.\scripts\doctor.ps1 -Scope User -Harness OMP
ompw --help
```

`doctor` 的主实现为 `scripts/doctor.py`，PowerShell 文件只负责转发参数。它会检查已安装
文件、overlay 的 skill 白名单、角色映射和 review gate；检查通过就不需要修改其他文件。

不要用 `omp --config <overlay> config list` 验证 overlay：OMP 17.3.8 的 `config`
子命令不会转发该参数，会错误地显示默认配置。Python doctor 因此不调用该接口；正常启动仍
由启动器传入 `--config`。

如果 OMP 发布说明明确修改了配置键或 agent/skill API，再按以下顺序处理：

1. 用 `omp config list --json` 确认新版本实际支持的配置键。
2. 更新本仓库的 `config/omp-workflow.yml` 和相关测试。
3. 重新运行 `install.ps1 -Scope User -Harness OMP` 同步全局 overlay。
4. 再运行 `doctor.ps1 -Scope User -Harness OMP`，并用 `ompw --help` 做启动冒烟测试。

OMP 更新和记录系统无关：如果使用的是项目级安装，还要对每个项目重新运行一次项目级安装
器；全局安装不需要这一步。OMP 升级只影响 overlay 与 agent 定义。

### 模型角色分工

| 阶段 | OMP 执行者 | 模型角色 |
| --- | --- | --- |
| 主路由、需求追问、最终决策 | 主会话 | `@default` |
| 方案规划 | `workflow-planner` | `@plan` |
| TDD 实现（仅 critical） | `workflow-implementer` | `@task` |
| 质量检查 | Matt `code-review` + 仓库自身检查 | 主会话 |
| 最终只读复核 | `workflow-reviewer` | `@advisor` |
| 高风险或失败升级 | 主会话/专项 agent | `@default` 或 `@slow` |

三个自定义 agent 都用 `autoloadSkills` 强制加载方法 skill 正文。实现由 `workflow-implementer`
承担，任务上下文通过 dispatch prompt 显式传递（含 `context.md` 的读取清单）；主路由会要求
它遵循 `implement.md` 中的 TDD 切片。实现使用 `@task` 不代表降低标准；遇到认证、资金、
迁移、公共接口等 `critical` 风险，或目标测试反复失败时，必须停止猜测并升级到
`@default` / `@slow`。overlay 同时关闭 `prewalk`，避免实现过程中意外切换到 `@smol`。

这些角色只引用 `@plan`、`@task`、`@advisor` 等别名，实际供应商和模型仍由你的 OMP
`modelRoles` 配置控制。为了获得真正的独立复核，`@advisor` 最好与 `@task` 使用不同
模型家族。

## Claude Code 工作流

仓库根目录包含可由 Claude Code 直接校验和加载的 plugin：

```powershell
claude plugin validate "D:\my-works\claude-skills\my-engineering-workflow" --strict
claude --plugin-dir "D:\my-works\claude-skills\my-engineering-workflow" --model sonnet
```

`--plugin-dir` 适合本地试用和开发，会得到 namespaced command
`/my-engineering-workflow:engineering-workflow`。使用 `-Harness Claude` 同步到用户或项目
目录后，入口是 `/engineering-workflow`。两种加载方法择一即可，避免同名 skill 和 agent
重复出现。

### Claude 模型与 agent 分工

| 阶段 | Claude Code 执行者 | 模型 |
| --- | --- | --- |
| 主路由、需求追问、批准、修复、交付 | 主会话 | 启动时选择的模型 |
| 方案规划 | `workflow-planner` | `opus` |
| TDD 实现（仅 critical） | `workflow-implementer` | `sonnet` |
| 质量检查 | Matt `code-review` + 仓库自身检查 | 主会话 |
| 最终只读复核 | `workflow-reviewer` | `opus` |

Claude Code 没有 OMP 的 `@task` / `@advisor` 角色别名。若希望实现与复核真正跨模型，
通常用以下方式让主会话运行 Sonnet，而 planner/reviewer 固定使用 Opus：

```powershell
claude --model sonnet
```

如果主会话也使用 Opus，reviewer 仍然是新的上下文，但不能称为跨模型复核。

`workflow-planner`、`workflow-implementer`、`workflow-reviewer` 都由本仓库安装，没有项目
hook 帮忙注入上下文。Claude 实现 agent 的 tools 不含 `Skill`，因此不能宣称它会自动加载
外部 skill；TDD 由 `implement.md` 中的 RED/GREEN vertical slice、主会话 dispatch prompt、
`code-review` 和最终独立 review 共同约束。

## 使用方法

### 1. 第一次在项目中使用

第一次使用时直接说明需求即可，主路由会先询问是否创建 `.workflow/`。在 Codex 中输入以下内容，或在 Claude Code 中
执行 `/engineering-workflow` 后附带同一需求：

```text
使用 $run-engineering-workflow 处理这个需求：为订单列表增加按状态筛选。
```

该 skill 会读取 `.workflow/` 指针和当前任务状态，再决定进入需求澄清、方案规划、
实现、独立复核、验证还是收尾阶段。

### 2. 单独澄清需求

需求复杂、模糊或涉及多个系统时使用：

```text
使用 $clarify-requirements 澄清这个需求，并把结果写入当前任务的 prd.md。
```

它会先读取代码和已有文档，再一次询问一个真正影响范围或行为的问题，并生成
`AC-001`、`AC-002` 等可验证验收标准。

### 3. 规划技术方案

需求确认后、写代码之前使用：

```text
使用 $plan-solution 为当前任务设计方案，生成 design.md、implement.md 和 context.md。
```

它会先分析现有代码、测试、Spec 和 ADR，再设计模块边界、接口、数据流、错误处理、
备选方案、迁移与回滚。`implement.md` 按 vertical slice 将每个 AC 映射到代码边界、
test seam、RED/GREEN 和验证命令。该阶段不写生产代码。

`lightweight` 任务可以保持 PRD-only，但必须在 `prd.md` 中记录方案草图、预计修改文件、
验证方法，以及不创建独立 `design.md` / `implement.md` 的原因。

### 4. 实现

需求确认后继续调用主路由：

```text
使用 $run-engineering-workflow 继续当前任务，按照 implement.md 和 Matt TDD 实现。
```

正常行为变更应经历：

```text
RED 测试 -> 最小实现 -> GREEN -> 重构 -> code-review + 仓库验证
```

在 OMP 中，只有 `critical` 任务才会把已批准的切片交给 `workflow-implementer`，默认使用
`@task`，并要求它遵循 `implement.md` 中的 TDD 切片；普通任务留在主会话实现。在 Claude
Code 中调用本仓库的 `workflow-implementer`，同样按已批准的 `implement.md` 执行 RED/GREEN
slice。主会话继续负责范围、升级和最终决策。

### 5. 独立复核
`lightweight` 默认不派独立 reviewer。`standard` 在项目原生检查不足或确实需要
fresh context 时执行一次 `review-implementation`；`critical` 任务必须执行：
```text
使用 $review-implementation 从独立上下文复核当前实现。
```

OMP 使用 `workflow-reviewer` 和 `@advisor`，先返回按严重度排序的 findings；主会话
修复后重新运行受影响的检查。Claude Code 使用只读 Opus `workflow-reviewer`。实现模型
不能仅靠自己的复述完成签字。

### 6. 完成和记录证据

代码和测试完成后使用：

```text
使用 $finish-with-evidence 检查当前任务，记录 outcome.md，然后关闭并归档任务记录。
```

没有执行的检查必须记录为 `NOT RUN` 或 `UNVERIFIED`，不能根据推测写成 `PASS`。

### 7. 新会话继续任务

在新的 Codex、Claude Code 或其他 AI 会话中输入：

```text
使用 $run-engineering-workflow 继续当前任务。
```

AI 应优先读取当前 task、Spec、代码和测试，而不是依赖上一段聊天摘要。确实需要找回
旧讨论时，再使用跨会话 memory 工具或 `.workflow/journal.md` 作为线索。

## 质量等级

| 等级 | 适用场景 | 主要要求 |
| --- | --- | --- |
| `lightweight` | 文档、配置、低风险局部改动 | 范围检查、diff、最小可运行检查 |
| `standard` | 普通功能、bug fix、重构 | RED/GREEN、目标测试、必要的 lint/类型/构建、Spec；`code-review` 与独立 review 二选一 |
| `critical` | 认证、资金、密钥、迁移、公共接口、破坏性操作 | Standard 全部要求，加安全、集成、回滚和关键路径 E2E；必须独立 review |

详细配置随主路由打包在
[quality-profiles.md](skills/run-engineering-workflow/references/quality-profiles.md)。风险等级
不能覆盖项目自身更严格的要求。

## 冲突处理规则

当多个扩展给出不同指令时，按以下优先级处理：

1. 用户和 AI 平台的上级指令。
2. 项目 `AGENTS.md` 和 `.workflow/spec/`。
3. 当前任务目录的 `prd.md`、`design.md`、`implement.md` 与 `outcome.md`。
4. 本仓库的路由和质量策略。
5. Matt Skills、Ponytail 的通用默认规则。

任何扩展都不能创建与 `.workflow/` 重复的需求、方案或任务记录，也不能以“减少代码”为由
删除必要的正确性、安全、可访问性或验证措施。

## 开发和验证

修改本仓库后运行：

```bash
npm test
```

五个 skill 还应通过 Codex `skill-creator` 提供的 `quick_validate.py`。上游版本和本机
相对路径提示记录在 [`manifests/upstreams.lock.json`](manifests/upstreams.lock.json) 中。
升级后重新运行 `install.ps1`，再用 `doctor.ps1` 检查安装完整性、OMP 角色映射、
Claude Code 与 Pi agent 契约。
