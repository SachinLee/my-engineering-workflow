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

## 复验轮次 3：共用结论
- 用户要 omo-slim 风格按需专家协作，不是 planner→implementer→reviewer 全阶段强制流水线；授权实施且复用本 change。
- Pi 已装 nicobailon/pi-subagents 0.88.0（非 README 旧 @narumitw scope）；auto 模式可能只暴露 subagents_enable，调用后下一轮出现工具；旧会话两者均可能缺失。安装不等于调用能力。
- Pi options.context=fresh，options.agentScope=both，async 默认开启，以实际 schema 为准。oracle 默认 fork，必须覆盖；scout 含 bash/write，不能宣称硬只读；researcher 需 web provider。禁止默认写 context.md/plan.md/research.md 等影子状态，限定输出到主会话或 active change 授权产物。
- Codex CLI 0.169.0；用户 ~/.codex/agents 有 explorer/fixer/designer/oracle.toml，不属于本仓库，必须保留。config multi_agent 已开启但命名角色运行未证实。没有 codex exec --agent。官方 role.rs 支持角色配置，当前目录发现与注册格式须查当前官方文档或源码验证，不能猜。
- scripts/install.ps1 与 scripts/doctor.py 已有其他 change 的七个技能支持增量；tests/contracts.test.js、tests/test_shared_installation.py 亦已改。保留全部现状。根 agents/、.omp/、.pi/、.opencode/ 定义同步规则不变。

### 上下文包 C（可派发）
Active change: openspec/changes/align-cross-harness-workflow/
Assigned slice: C / AC-007、AC-008
Phase: implement
- 验收：按需选择 explore/research/implement/consult/review；协调器持有上下文的小修改与文档直接做；咨询不是额外审核门。Pi loader 激活、fresh context、受限输出、事件完成，缺 reviewer 为 UNVERIFIED。
- 设计：共享 reference 只写一份；宿主调度和质量规则分离；可探索后建 change，但正式实施/最终审查 handoff 不削弱；保留一次审查预算及 OpenCode Slim 路由。
- 已定位：skills/run-engineering-workflow/SKILL.md Pi Roles 当前是 blocking 示例、缺激活且允许自审 fallback；references/quality-profiles.md 已要求缺独立 review UNVERIFIED；tests/contracts.test.js 有 Codex skills-only 旧假设，需条件化而非全局宣称支持。
- 需要新打开：skills/run-engineering-workflow/SKILL.md、references/quality-profiles.md、tests/contracts.test.js、evals/workflow-cases.json；必要 Pi 文档位于 C:/Users/shuan/.pi/agent/npm/node_modules/pi-subagents/docs/。
- 允许修改：skills/run-engineering-workflow/SKILL.md、skills/run-engineering-workflow/references/specialist-routing.md、tests/contracts.test.js、evals/workflow-cases.json。不修改 README/ARCHITECTURE、安装器、agent 模板或其他 change。
- RED/GREEN：node --test tests/contracts.test.js；按任务契约先失败后通过；只跑本 lane 聚焦测试，不跑完整 suite。
- 返回证据：确切命令、exit code、RED 失败点、GREEN 计数、文件范围和未验证运行限制。越界停报；不提交、不安装。

### 上下文包 D（可派发）
Active change: openspec/changes/align-cross-harness-workflow/
Assigned slice: D / AC-009、AC-010
Phase: implement
- 验收：Codex 无 model 的原生三个 workflow TOML；Pi 原生 skill 入口指向共享源；安全安装、备份、未知链接保护和幂等；doctor 区分安装/发现/运行未知。不覆写用户角色、模型/provider 或插件配置，Both 兼容。
- 设计：沿用安装器现有 helper 和 Python 测试临时 home；不再创建调度服务。不把 TOML 存在当 runtime verified。若角色原生目录格式依赖版本，必须核实官方当前格式，不猜 CLI --agent；无法安全注册时说明限制。
- 已定位：scripts/install.ps1 Codex 当前只备份旧 md；scripts/doctor.py 仍总报告 skills-only；现有 tests/test_shared_installation.py 临时 home 安装回归及七技能增量必须保留。
- 需要新打开：scripts/install.ps1、scripts/doctor.py、tests/test_shared_installation.py；agents/workflow-*.md 与 .pi/agents/workflow-*.md 用于迁移原有标准/权限/handoff 合同；Codex 当前官方文档或源码。
- 允许修改：scripts/install.ps1、scripts/doctor.py、tests/test_shared_installation.py、.codex/agents/workflow-*.toml（新增），必要独立 tests/test_codex*.py。不可写 shared SKILL、tests/contracts.test.js、README/ARCHITECTURE 或用户 home。
- RED/GREEN：python -m unittest tests.test_shared_installation（可选择新增用例先跑）；新回归覆盖无模型原生格式、幂等/保护与诊断分层，先 RED 后 GREEN。只跑聚焦测试，不跑所有 Python discovery。
- 返回证据：官方依据、命令及 exit code/计数、改动文件、未验证限制。需要越界先报；不提交、不实际安装用户目录。实施者负责聚焦验证，主会话负责最终整合/真实安装/运行验证。
