# 我的 AI 工程工作流

这是一个面向个人开发习惯的 AI 工程工作流仓库。它把 Trellis、ECC、
Matt Pocock Skills 和 Ponytail 中适合自己的部分组合起来，用于提高需求质量、
代码质量、验证质量，以及不同 AI 会话之间的上下文连续性。

本仓库不是上述项目的完整替代品，也不复制它们的源码。它是一个轻量编排层，
负责规定：谁保存任务状态、需求和方案写到哪里、何时使用 TDD、需要执行哪些验证，
以及任务结束后要为后续 AI 会话保留什么证据。

## 这个仓库是做什么的

这个工作流主要解决以下问题：

- AI 没有充分理解需求就开始实现。
- 需求、方案和实现过程只存在于聊天记录中，后续难以追踪。
- 切换 Codex、Claude Code 或新的 AI 会话后，需要重新解释项目背景。
- 代码虽然能运行，但缺少 TDD、回归测试、类型检查、安全检查等证据。
- AI 容易增加不必要的抽象、依赖、配置和文件。
- 计划中的方案和最终实际实现存在偏差，但没有被记录。

四个上游项目在本工作流中的职责如下：

| 组件 | 职责 | 本仓库如何使用 |
| --- | --- | --- |
| Trellis | 任务状态、需求、设计、项目规范、会话记忆 | 作为唯一记录系统和工作流内核 |
| ECC | TDD、验证、安全和专业 review | 作为工程质量能力库 |
| Matt Pocock Skills | 需求追问、领域建模、模块边界设计 | 选择性吸收和调用 |
| Ponytail | YAGNI、复用、stdlib/native 优先 | 只用于复杂度控制，不降低质量要求 |

本仓库目前提供五个 skill：

| Skill | 用途 |
| --- | --- |
| `$run-engineering-workflow` | 根据 Trellis 当前任务状态和风险等级路由整个开发流程 |
| `$clarify-requirements` | 澄清需求，并把可验证的验收标准写入 Trellis `prd.md` |
| `$plan-solution` | 设计技术方案，并把决策与执行步骤分别写入 `design.md` 和 `implement.md` |
| `$review-implementation` | 使用独立上下文复核需求覆盖、正确性、测试、安全和复杂度 |
| `$finish-with-evidence` | 执行最终检查，并把实际实现和验证证据写入 `outcome.md` |

## 核心产物

在使用本工作流的项目中，Trellis 是任务记录的唯一来源：

| 文件 | 内容 |
| --- | --- |
| `.trellis/tasks/<task>/prd.md` | 需求、范围、非目标、假设和验收标准 |
| `.trellis/tasks/<task>/design.md` | 技术方案、接口、数据流、兼容性和取舍 |
| `.trellis/tasks/<task>/implement.md` | 实施顺序、测试计划、验证命令和回滚点 |
| `.trellis/tasks/<task>/outcome.md` | 实际实现、AC 结果、RED/GREEN、独立复核、验证结果和剩余风险 |
| `.trellis/spec/` | 跨任务长期有效的规范、约定和踩坑经验 |
| `.trellis/workspace/` | 开发者会话摘要和任务指针 |
| `CONTEXT.md` | 可选的领域词汇表，不存放技术方案 |
| `docs/adr/` | 少量难以逆转且存在真实权衡的架构决策 |

详细约定随主路由一起打包在
[workflow-governance.md](skills/run-engineering-workflow/references/workflow-governance.md)，
复制或安装 skill 后仍然可见。

## 需要安装什么

### 基础环境

- Git
- Node.js 18 或更高版本
- Python 3.9 或更高版本
- Codex App / Codex CLI、Claude Code 2.1 或更高版本，按实际使用的平台安装
- 需要供应商无关的多模型角色映射时，可选 OMP 17.3.3 或更高版本

### 必须安装：Trellis

Trellis 提供任务目录、Spec、状态机、会话日志和跨会话恢复能力：

```bash
npm install -g @mindfoldhq/trellis@latest
```

在每个需要使用本工作流的代码仓库中初始化：

```bash
trellis init --codex -u your-name
```

如果同时使用多个平台，可以一次初始化：

```bash
trellis init --codex --omp --claude --cursor --opencode -u your-name
```

### 推荐安装：ECC

ECC 是本工作流的主要质量能力来源。Codex 原生插件安装方式：

```bash
codex plugin marketplace add affaan-m/ECC
codex plugin add ecc@ecc
codex plugin list --json
```

安装后重启 Codex，检查并信任需要启用的 hooks，然后调用
`$configure-ecc` 完成配置。至少保留：

- `tdd-workflow`
- `verification-loop`
- `intent-driven-development`
- 与项目技术栈匹配的测试或 reviewer skill
- 涉及认证、输入、密钥、支付或数据安全时使用 `security-review`

Claude Code 中在会话内分别执行：

```text
/plugin marketplace add https://github.com/affaan-m/ECC
/plugin install ecc@ecc
```

同一个平台只选一种 ECC 安装方式，不要叠加 plugin 和完整手工复制，否则会出现重复
skill、command 或 hook。

不需要把 ECC 的全部 skill、agent 和 rules 都设置成日常加载项。建议按项目使用
`agent-sort` 分成 `DAILY` 和 `LIBRARY`。

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

建议只选择：

- `grilling`
- `domain-modeling`
- `codebase-design`

Matt 的 `code-review` 只在当前 harness 没有同名 reviewer 时安装。使用 ECC 和本仓库的
`review-implementation` 时不要全局安装它，否则 Claude Code 会同时看到两个
`code-review` 来源，增加命名冲突和误路由。

不要使用 Matt 的 `to-spec`、`to-tickets` 和 `implement` 作为主入口，否则会和
Trellis 的任务、方案和提交流程重复。也不要让其 setup 创建第二套 issue/task 记录。

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
调用 `ponytail-review` / `ponytail-audit`。不要用 Ponytail 的最小测试规则替代
ECC 或项目自身的测试要求。

Windows 可以在 `%APPDATA%\ponytail\config.json` 中设置：

```json
{
  "defaultMode": "off"
}
```

## 安装本仓库的 Skill

仅克隆本仓库不会自动让 Codex、Claude Code 或 OMP 发现这五个 skill。使用安装器
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

这会安装五个 skill、`workflow-planner` / `workflow-reviewer` 和
`/engineering-workflow`，不会安装或覆盖 Trellis agent。重新启动 Claude Code 后生效。

### 安装到项目，同时支持三个平台

先用 Trellis 初始化目标项目的 Codex、OMP 和 Claude 资产，再运行：

```powershell
trellis init --codex --omp --claude -u your-name
.\scripts\install.ps1 -Scope Project -Harness All -ProjectPath "D:\path\to\project"
.\scripts\doctor.ps1 -Scope Project -Harness All -ProjectPath "D:\path\to\project"
```

安装器会同步：

- 五个 canonical skill 到 `.agents/skills/`、`.omp/skills/` 和
  `.claude/skills/`。
- 两个本仓库 OMP agent 到 `.omp/agents/`；Trellis 自己提供
  `trellis-implement` 和 `trellis-check`。
- OMP skill 白名单 overlay 和启动脚本到项目 `.omp/`。
- 两个本仓库 Claude agent 和 `/engineering-workflow` 到项目 `.claude/`；安装器不会
  复制、修改或替换 Trellis 的 Claude agent 和 hooks。

只需要一个平台时使用 `Codex`、`OMP` 或 `Claude`。为兼容旧用法，`Both` 仍只表示
Codex + OMP；`All` 才表示三个平台。先用 `-WhatIf` 可以预览安装器将替换的受管目录
和文件。

个人电脑推荐使用全局安装。项目级安装只用于团队需要把适配文件固定在仓库中，或某个
项目需要隔离版本的情况。无论采用哪种方式，Trellis 的 `.trellis/` 都必须保留在项目
内，因为它保存该项目自己的任务状态和工程记录。

## 完整使用指南

### 一次性全局准备

Codex 和 Claude Code 的全局安装命令见上一节。需要经常使用 OMP 时，再全局安装一次
OMP adapter：

```powershell
.\scripts\install.ps1 -Scope User -Harness OMP
.\scripts\doctor.ps1 -Scope User -Harness OMP
```

全局安装后，不要再为每个项目复制本仓库的 skill。只有以下内容仍是项目级的：

- `.trellis/` 任务、Spec、workspace 和工作流状态。
- Trellis 为客户端生成的原生 agent、hook 或 extension。
- 项目自己的 `AGENTS.md`、测试命令、质量标准和模型配置。

因此，`install.ps1 -Scope User` 只需在本机执行一次；Python OMP launcher 可以从任意已
初始化 Trellis 的项目启动。新项目仍需执行一次 `trellis init`，但不需要再次安装本仓库的
skill。已有 `.trellis/` 的项目无需重复初始化；升级 Trellis 时使用 `trellis update`。

### 每个项目只需初始化一次

同时使用 Codex、Claude Code 和 OMP 时，在项目根目录运行：

```powershell
trellis init --codex --claude --omp -u your-name
```

这一步不是重复安装本工作流。它只为当前项目创建 `.trellis/`，并生成三个客户端需要的
Trellis agent、hook 和 extension。已经初始化的项目不要重新 init；升级 Trellis 后使用
`trellis update`，并先检查项目中的自定义文件。

只使用部分客户端时，仅传对应 flag。例如：

```powershell
trellis init --codex --claude -u your-name
```

### 各客户端入口

| 客户端 | 启动方式 | 新需求入口 | 继续已有任务 |
| --- | --- | --- | --- |
| Codex App / CLI | 从项目根目录打开 Codex | `使用 $run-engineering-workflow 处理这个需求：...` | `使用 $run-engineering-workflow 继续当前 Trellis 任务。` |
| Claude Code | 从项目根目录运行 `claude --model sonnet` | `/engineering-workflow 处理这个需求：...` | `/engineering-workflow 继续当前 Trellis 任务` |
| OMP | 使用下面的全局 launcher | `使用 run-engineering-workflow 处理这个需求：...` | `使用 run-engineering-workflow 继续当前 Trellis 任务。` |
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

launcher 会直接执行并启动 OMP，它不是启动 OMP 之前的额外准备命令。每次需要带本工作流
启动一个新的 OMP 会话时使用 launcher，不要在它之后再运行一次 `omp`。

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
例如 `ompw --continue` 或 `ompw --model opus`。

完成用户级安装后，普通 `omp` 也会读取 `~/.omp/agent/config.yml` 中的本工作流默认设置，加载 skill 白名单、`prewalk` 设置和 `@plan` / `@task` / `@advisor` 角色映射。重新启动 OMP 会话后直接运行：

```powershell
omp
```

`ompw` 仍然保留，适合在未安装用户级默认配置的机器上，或需要显式指定项目 overlay 时使用：

```powershell
ompw --continue
```

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
  -> Trellis check -> @advisor 独立复核 -> 修复并复验 -> 证据交付
```

常用操作如下：

| 目的 | 在 OMP 主会话中输入 |
| --- | --- |
| 开始新需求 | `使用 run-engineering-workflow 处理这个需求：...` |
| 只澄清需求 | `使用 clarify-requirements 澄清当前需求，不要写代码。` |
| 只规划方案 | `使用 plan-solution 为当前 Trellis 任务生成 design.md 和 implement.md，不要实现。` |
| 批准后继续实现 | `继续当前 Trellis 任务，按已批准的 implement.md 使用 TDD 实现。` |
| 继续已有任务 | `使用 run-engineering-workflow 继续当前 Trellis 任务。` |
| 方案仍有争议 | `使用 grilling 逐项追问当前方案，并把结论写回当前任务。` |
| 需要领域建模 | `使用 domain-modeling 统一当前任务的领域术语和实体关系。` |
| 完成前单独复核 | `使用 review-implementation 从独立上下文复核当前实现。` |
| 最终交付 | `使用 finish-with-evidence 记录验证证据并完成当前 Trellis 任务。` |

通常只使用第一条主路由即可；表中的单阶段调用只用于补做或强化某一阶段。实现模型、
复核模型和角色由 OMP overlay 自动分配：方案规划使用 `@plan`，TDD 实现使用 `@task`，
Trellis 检查和独立复核使用 `@advisor`。用户不需要手动切换这些角色。

如果关闭 OMP 后重新打开，可使用 `ompw --continue` 恢复 OMP 会话；跨 Codex、Claude Code
或其他客户端时，优先输入“继续当前 Trellis 任务”，让新会话重新读取 `.trellis/` 中的
任务产物。Trellis 文件才是共享记录的事实来源，OMP 聊天记录只是辅助上下文。

Windows 上如果 Trellis 命令显示无输出并以 `Exit: 49` 结束，通常是 `python` / `python3`
解析到了 Microsoft Store 的 WindowsApps 占位程序，并不表示 Trellis 与当前 Python 版本
不兼容。使用 `py -3` 运行 Trellis 脚本；不要改用 OMP `eval` 内核导入 `task.py`，也不要
绕过 hooks 手工创建任务文件。主路由已包含该选择规则。可用以下命令确认：

```powershell
Get-Command python, python3, py | Select-Object Name, Source
py -3 .\.trellis\scripts\get_context.py --mode phase
```

### 一次完整任务的阶段

1. **进入主路由**：读取 `.trellis/workflow.md` 和当前 task，确认是否需要创建任务。
2. **需求澄清**：把目标、范围、非目标、假设和可验证 AC 写入 `prd.md`。
3. **方案规划**：把技术决策写入 `design.md`，把 vertical slice、RED/GREEN 和验证命令
   写入 `implement.md`。
4. **批准执行**：按项目 Trellis gate 从 `planning` 进入 `in_progress`，不能由 AI 默认为
   已批准。
5. **TDD 实现**：先 RED，再最小 GREEN，然后重构；实现不得创建第二套计划记录。
6. **检查和复核**：先运行 Trellis check，再从独立上下文运行
   `review-implementation`，修复 findings 后重新验证。
7. **证据交付**：将 AC 结果、实际改动、RED/GREEN、命令输出和剩余风险写入
   `outcome.md`，再按 Trellis 流程完成任务。

通常只需要调用主路由。只有需要重新执行或单独强化某一阶段时，才直接调用
`clarify-requirements`、`plan-solution`、`review-implementation` 或
`finish-with-evidence`。

### 扩展能力怎么调用

| 场景 | 使用能力 | 结果写到哪里 |
| --- | --- | --- |
| 需求或方案仍含模糊决策 | Matt `grilling` | 结论整理回 `prd.md` 或 `design.md` |
| 统一业务术语和实体关系 | Matt `domain-modeling` | 稳定词汇写入 `CONTEXT.md`，真实架构决策写 ADR |
| 设计模块边界和测试 seam | Matt `codebase-design` | 方案写入当前 task 的 `design.md` |
| 功能或 bug fix | ECC `tdd-workflow` | 测试和代码；证据最终写 `outcome.md` |
| 发布前综合验证 | ECC `verification-loop` | 实际命令结果写 `outcome.md` |
| 安全敏感改动 | ECC security/reviewer 能力 | findings 返回主会话，修复后记录结果 |
| 正确性检查完成后压缩复杂度 | Ponytail review/audit | 修改代码并重新运行受影响检查 |

扩展只提供方法，不拥有任务状态。不要让 Matt、ECC 或 Ponytail 另建与 Trellis 重复的
PRD、ticket、plan 或 outcome。

### 跨客户端和新会话续接

Codex、Claude Code、OMP 和其他客户端通过同一个工作树和 `.trellis/` 共享上下文，不
通过复制聊天记录共享。切换前确保本阶段结论已经写入正确产物；切换后从同一项目根目录
启动新客户端，然后要求继续当前 Trellis 任务。

新会话必须重新读取：

1. `.trellis/workflow.md` 和当前 task 状态。
2. 当前 task 的 `prd.md`、`design.md`、`implement.md` 和已有 `outcome.md`。
3. 适用的 `.trellis/spec/`、代码、测试和 `git status` / `git diff`。

聊天摘要、自动 memory 和旧会话只可作为线索。它们与任务文件或代码冲突时，以任务
文件、Spec、代码和测试为准。未提交修改会通过同一工作树保留，但新客户端必须先区分
当前任务改动与用户已有改动。

### 其他客户端

Trellis 还支持 Cursor、OpenCode、Gemini CLI、Kiro、GitHub Copilot、Pi Agent、Qoder、
CodeBuddy、Kimi Code 等平台。先查看当前 Trellis 版本支持的 flag：

```powershell
trellis init --help
```

然后只初始化实际使用的平台，例如：

```powershell
trellis init --cursor --opencode --gemini -u your-name
```

本仓库安装器目前原生管理 Codex、Claude Code 和 OMP。其他支持 agentskills.io 的客户端
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
不支持 skill，直接要求它读取 `.trellis/workflow.md` 和当前 task，按其中阶段执行；此时
本仓库的自动路由和质量加固不能视为已加载。

## OMP 多模型工作流

OMP 默认会扫描 Codex、Claude、Agents 和 Pi/OMP 的用户级及项目级 skill。被发现的
主要是 skill 的 `name` 和 `description`；正文通常在触发后才加载。不过候选过多仍会
增加误触发和选择冲突，因此本仓库不依赖“让模型从全部 skill 中自行挑选”。

项目安装后从目标项目运行：

```bash
python ./.omp/start-engineering-workflow.py --project-path .
```

该脚本显式加载 `.omp/engineering-workflow.yml`，其中
`skills.includeSkills` 只保留本工作流、Trellis 和选定的 ECC/Matt/Ponytail 能力。
OMP 17.3.3 的项目 `.omp/config.yml` 只自动接管 `modelRoles`；把白名单仅写进该文件并
不能保证生效，所以不要绕过启动脚本。临时启动也可以使用：

```powershell
omp --cwd "D:\path\to\project" --config "D:\path\to\project\.omp\engineering-workflow.yml"
```

### OMP 升级后的检查

只更新 OMP 程序通常不会改动本仓库的 skill、launcher 或 overlay，因此不需要重新执行
`trellis init`。升级后从本仓库根目录执行一次：

```powershell
omp --version
.\scripts\doctor.ps1 -Scope User -Harness OMP
ompw --help
```

`doctor` 会验证 overlay 是否仍能被 OMP 读取，并检查 `includeSkills`、`@plan`、`@task`、
`@advisor` 和 `modelRoles`。检查通过就不需要修改其他文件。

如果 OMP 发布说明明确修改了配置键或 agent/skill API，再按以下顺序处理：

1. 用 `omp config list --json` 确认新版本实际支持的配置键。
2. 更新本仓库的 `config/omp-workflow.yml` 和相关测试。
3. 重新运行 `install.ps1 -Scope User -Harness OMP` 同步全局 overlay。
4. 再运行 `doctor.ps1 -Scope User -Harness OMP`，并用 `ompw --help` 做启动冒烟测试。

如果使用的是项目级安装，还要对每个项目重新运行一次项目级安装器；全局安装不需要这一步。
OMP 更新和 Trellis 更新是两件事：只有 Trellis 更新时才运行项目内的 `trellis update`，
不要重复执行 `trellis init`。

### 模型角色分工

| 阶段 | OMP 执行者 | 模型角色 |
| --- | --- | --- |
| 主路由、需求追问、最终决策 | 主会话 | `@default` |
| 方案规划 | `workflow-planner` | `@plan` |
| TDD 实现 | Trellis `trellis-implement` | `@task` |
| Trellis 质量检查 | Trellis `trellis-check` | `@advisor` |
| 最终只读复核 | `workflow-reviewer` | `@advisor` |
| 高风险或失败升级 | 主会话/专项 agent | `@default` 或 `@slow` |

自定义规划和复核 agent 用 `autoloadSkills` 强制加载阶段 skill 正文。实现继续使用
Trellis 原生 `trellis-implement`，保留 Trellis 的 `implement.jsonl` context injection；主路由
会要求它先读取 `skill://tdd-workflow`。实现使用 `@task` 不代表降低标准；遇到认证、资金、
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
| TDD 实现 | Trellis 原生 `trellis-implement` | Trellis/Claude 当前配置 |
| Trellis 质量检查 | Trellis 原生 `trellis-check` | Trellis/Claude 当前配置 |
| 最终只读复核 | `workflow-reviewer` | `opus` |

Claude Code 没有 OMP 的 `@task` / `@advisor` 角色别名。若希望实现与复核真正跨模型，
通常用以下方式让主会话运行 Sonnet，而 planner/reviewer 固定使用 Opus：

```powershell
claude --model sonnet
```

如果主会话也使用 Opus，reviewer 仍然是新的上下文，但不能称为跨模型复核。

本仓库刻意不覆盖 Trellis 的 `trellis-implement` / `trellis-check`。它们负责 Claude hook
注入、`implement.jsonl` / `check.jsonl` 和无 hook 时的 fallback context loading。Claude
实现 agent 的 tools 不含 `Skill`，因此不能宣称它会自动加载 ECC `tdd-workflow`；TDD
由 `implement.md` 中的 RED/GREEN vertical slice、主会话 dispatch prompt、Trellis check
和最终独立 review 共同约束。

## 使用方法

### 1. 第一次在项目中使用

确认项目已经执行过 `trellis init`，然后在 Codex 中输入以下内容，或在 Claude Code 中
执行 `/engineering-workflow` 后附带同一需求：

```text
使用 $run-engineering-workflow 处理这个需求：为订单列表增加按状态筛选。
```

该 skill 会读取 `.trellis/workflow.md` 和当前任务状态，再决定进入需求澄清、方案规划、
实现、独立复核、验证还是收尾阶段。

### 2. 单独澄清需求

需求复杂、模糊或涉及多个系统时使用：

```text
使用 $clarify-requirements 澄清这个需求，并把结果写入当前 Trellis 任务。
```

它会先读取代码和已有文档，再一次询问一个真正影响范围或行为的问题，并生成
`AC-001`、`AC-002` 等可验证验收标准。

### 3. 规划技术方案

需求确认后、写代码之前使用：

```text
使用 $plan-solution 为当前 Trellis 任务设计方案，生成 design.md 和 implement.md。
```

它会先分析现有代码、测试、Spec 和 ADR，再设计模块边界、接口、数据流、错误处理、
备选方案、迁移与回滚。`implement.md` 按 vertical slice 将每个 AC 映射到代码边界、
test seam、RED/GREEN 和验证命令。该阶段不写生产代码。

`lightweight` 任务可以保持 PRD-only，但必须在 `prd.md` 中记录方案草图、预计修改文件、
验证方法，以及不创建独立 `design.md` / `implement.md` 的原因。

### 4. 实现

需求确认后继续调用主路由：

```text
使用 $run-engineering-workflow 继续当前任务，按照 implement.md 和 ECC TDD 实现。
```

正常行为变更应经历：

```text
RED 测试 -> 最小实现 -> GREEN -> 重构 -> Trellis/ECC 验证
```

在 OMP 中，主路由会按 Trellis 原生协议把已批准的任务交给 `trellis-implement`，默认
使用 `@task`，并要求它加载 ECC `tdd-workflow`。在 Claude Code 中仍调用 Trellis 原生
`trellis-implement`，按已批准的 `implement.md` 执行 RED/GREEN slice。主会话继续负责
范围、升级和最终决策。

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
使用 $finish-with-evidence 检查当前任务，记录 outcome.md，然后按 Trellis 流程收尾。
```

没有执行的检查必须记录为 `NOT RUN` 或 `UNVERIFIED`，不能根据推测写成 `PASS`。

### 7. 新会话继续任务

在新的 Codex、Claude Code 或其他 AI 会话中输入：

```text
使用 $run-engineering-workflow 继续当前 Trellis 任务。
```

AI 应优先读取当前 task、Spec、代码和测试，而不是依赖上一段聊天摘要。确实需要找回
旧讨论时，再使用 Trellis `session-insight` / `trellis mem`。

## 质量等级

| 等级 | 适用场景 | 主要要求 |
| --- | --- | --- |
| `lightweight` | 文档、配置、低风险局部改动 | 范围检查、diff、最小可运行检查 |
| `standard` | 普通功能、bug fix、重构 | RED/GREEN、目标测试、必要的 lint/类型/构建、Spec；`trellis-check` 与独立 review 二选一 |
| `critical` | 认证、资金、密钥、迁移、公共接口、破坏性操作 | Standard 全部要求，加安全、集成、回滚和关键路径 E2E；必须独立 review |

详细配置随主路由打包在
[quality-profiles.md](skills/run-engineering-workflow/references/quality-profiles.md)。风险等级
不能覆盖项目自身更严格的要求。

## 冲突处理规则

当多个扩展给出不同指令时，按以下优先级处理：

1. 用户和 AI 平台的上级指令。
2. 项目 `AGENTS.md` 和 `.trellis/workflow.md`。
3. 当前 Trellis 任务与 `.trellis/spec/`。
4. 本仓库的路由和质量策略。
5. ECC、Matt Skills、Ponytail 的通用默认规则。

任何扩展都不能创建与 Trellis 重复的需求、方案或任务记录，也不能以“减少代码”为由
删除必要的正确性、安全、可访问性或验证措施。

## 开发和验证

修改本仓库后运行：

```bash
npm test
```

五个 skill 还应通过 Codex `skill-creator` 提供的 `quick_validate.py`。上游版本和本机
相对路径提示记录在 [`manifests/upstreams.lock.json`](manifests/upstreams.lock.json) 中。
升级后重新运行 `install.ps1`，再用 `doctor.ps1` 检查安装完整性、OMP 角色映射和
Claude Code agent 边界。
