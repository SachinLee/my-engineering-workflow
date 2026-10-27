# 上下文包

## 已确认事实
- skills/ 六个技能与 ~/.agents/skills 一致；~/.config/opencode/skills 存在四个旧版本。scripts/install.ps1:6 未支持 OpenCode，scripts/doctor.py:36 同样缺少该端。
- 架构 ARCHITECTURE.md:58 定义规范共享目录及 Claude junction；Both 必须保持 Codex + OMP。
- quality-profiles.md:52 默认主会话实施，与 Slim 默认 specialist 委派交叉；:77 已有一次完整、最多一次聚焦审查预算，应保留。
- Claude 本地 Opus/Sonnet 别名均映射 sonnet；Pi settings.subagents.agentOverrides 已有三种 workflow 模型，不得重写。
- Codex 存在两份引用 Trellis 的旧 Markdown；是否被运行加载未证明。共享技能可发现，不能伪造原生 agent 支持。
- Slim 本地 D:/opencode-local/oh-my-opencode-slim-3.0.6-pwsh 带 PowerShell 补丁，不替换。OpenCode 已有手工 workflow 代理，缺少源码管理。
- Ponytail 源码 5.3.2，Claude 插件记录 4.9.0；Matt 最近一次仅 chief-of-staff 变化。更新应使用可验证官方安装入口，备份本地受管理内容，不引入 ECC 默认安装。

## 复验轮次 2：OpenCode / OMO-Slim 模型角色
- 用户要求完善 OpenCode 适配，并确认复用当前 `align-cross-harness-workflow` 变更；本轮只改变 OpenCode 路由，不改全局 OMO-Slim 配置或模型选择。
- `~/.config/opencode/oh-my-opencode-slim.json` 当前有 active preset `magpie`，为 `fixer`、`oracle` 分别配置角色模型；具体配置由用户维护，preset 可变化。
- 当前 `.opencode/agents/workflow-implementer.md`、`.opencode/agents/workflow-reviewer.md` 都是 `mode: subagent` 且无 `model`，直接通过 OpenCode 原生 agent 调用时继承父会话模型，不能自然解析成 Slim `fixer` / `oracle` 角色模型。
- 实施方案需让 Slim 主协调器调用原生 specialist 角色并传入同一 OpenSpec handoff/审查证据；不在安装器模板复制当前 preset 的静态模型 ID。未证实实际角色调用时不得声称已用角色模型。

## 复验轮次 2 已落地（静态合同）
- `skills/run-engineering-workflow/SKILL.md`、`commands/engineering-workflow.md`、`README.md`、`ARCHITECTURE.md` 统一表述：正式实现走 Slim `fixer`、唯一独立审查走 Slim `oracle`，模型由当前激活的 OMO-Slim preset 提供；禁止复制预设模型 ID；角色不可调用或无法观察模型时记 `UNVERIFIED`，并说明直接 agent 继承父会话模型不等于角色路由。
- `tests/contracts.test.js` 新增 `OpenCode formal work routes through Slim fixer and oracle without static model IDs`：校验上述四份文档的措辞、`.opencode/agents/*.md` 无 `model:` 且不读取 `oh-my-opencode-slim.json`、四个适配文档不含具体 provider/model 串。
- `evals/workflow-cases.json` 新增 `opencode-slim-role-routing-unverified`（`required_status: UNVERIFIED`）。
- 证据：先以旧措辞运行 `node --test tests/contracts.test.js`，新用例在 `formal implementation ... Slim fixer` 断言处失败（RED）；改文档后 52/52 通过（GREEN）。
- 限制：静态测试只证明合同与模板状态；Slim 实际把 `fixer`/`oracle` 派发到哪个模型仍为运行时 `UNVERIFIED`，需在真实 OpenCode 会话中观察。

## 边界
A 仅修改 scripts/install.ps1、scripts/doctor.py、新 OpenCode 适配目录、tests/test_shared_installation.py 及新聚焦测试；B 仅修改 skills/、ARCHITECTURE.md、README.md、AGENTS.md、tests/contracts.test.js、evals/。主会话管理 OpenSpec、upstream lock、本地安装。并行 writers 不共享修改范围。

## 验证命令
按 tests 的既有运行方式执行聚焦 Node/Python 用例；主会话最终运行 npm test 及 Python unittest discovery。用临时 home 验证安装幂等、备份、未知链接保护及旧副本迁移，再运行真实安装和 doctor。
