# 交付验证

## 交付
- 状态：awaiting-acceptance；前三轮静态交付与独立复核完成，轮次 3 focused CLEAN。最新运行边界以本文件“复验轮次 3”为准；历史未执行项保留原记录，不应解释为当前已验证。
- 范围：共享技能、跨客户端安装与诊断、宿主调度边界、低风险修复流程、上游安装核对。
- 提交：NOT COMMITTED。

## 验收标准
| 标准 | 结果 | 证据 |
| --- | --- | --- |
| AC-001 | PASS | 用户级 All 安装及复跑幂等；临时 home 迁移测试，含 OpenCode 项目 `.agents/skills` 检查；完整 Python suite 60 tests，1 个 Unix 专用测试在 Windows 跳过 |
| AC-002 | PASS | `npm test`：51 / 51；OpenCode agent 由 Slim 唯一调度；focused review CLEAN |
| AC-003 | PASS | `npm test`：快速通道、风险升级、回归检查合同；review Standards/Spec CLEAN |
| AC-004 | PASS | All doctor PASS，比较 Claude/OMP/Pi/OpenCode 内容并报告别名、Pi overrides、Codex 能力；模型配置 SHA256 不变；回归包含 Claude/OMP 漂移 |
| AC-005 | PASS | upstream-installation.md + 用户目录真实安装、15 项旧文件备份、幂等、配置 hash 保留、Node 及 Python 验证 |
| AC-006 | UNVERIFIED | 静态合同已通过：OpenCode 正式实现走 Slim `fixer`、唯一独立复核走 Slim `oracle`，不固化模型 ID；真实 Slim 会话中的角色调用及最终模型仍未运行核实 |

## TDD 证据
- 规则切片：实施者报告新断言先失败后通过；原始 RED 输出未归档：NOT CAPTURED；GREEN=`npm test`，51 / 51。
- 诊断修复：独立 worktree 基线 `f8d8636` 上两条新回归用例 `Ran 2 tests, FAILED (failures=1, errors=1)`；修复后 `Ran 2 tests, OK`。完整文件 `python -m unittest tests.test_shared_installation`：28 tests，OK (skipped=1)。

## 验证
- `npm test`：最终 PASS，52 / 52（包含 OMO-Slim `fixer` / `oracle` 静态路由合同）。
- `python -m unittest discover -s scripts -p 'test_*.py'`：PASS，4 / 4。
- `python -m unittest discover -s tests -v`：最终 PASS，Ran 62 tests in 151.360s，OK (skipped=1)。跳过项要求区分大小写的 Unix 文件系统，本机 Windows 不适用。
- `scripts/install.ps1 -Scope User -Harness All -WhatIf`：PASS；随后真实安装 PASS，重跑没有新备份，验证幂等。
- `scripts/doctor.ps1 -Scope User -Harness OpenCode`：PASS。
- `python scripts/doctor.py --scope User --harness All`：当前进程 PATH 未包含 Claude 时报告缺少 `claude`；将既有 `~/.local/bin` 加入该进程 PATH 后 PASS。没有永久改 PATH。
- Claude/Pi/OpenCode/Slim/Codex 五份配置与 `config-hashes-before-install.json` 逐一比对：全部保持相同 SHA256。
- 旧技能及手写 OpenCode 代理/命令共 15 项备份：`~/.agents/backups/my-engineering-workflow/418c59a7d9ad4962b23c1bbab0850ad7/`。
- 仓库 `.claude/skills` 原有 junction 指向共享安装；安装后相应 Git 可见内容一起更新，逐文件核对与规范 skills/ 一致，不是第二套实现。
- `openspec validate align-cross-harness-workflow --strict`：PASS。
- `git diff --check`：PASS，末尾空行已修正；Git 换行风格提示不构成检查失败。

## 独立复核
- 完整复核：REVIEW_STATUS: FINDINGS，见 review-full.md；F-001/F-002 已修复。
- 修复后 `python -m unittest tests.test_shared_installation`：28 项，OK (skipped=1)；新增两个回归用例单独运行 2 / 2 PASS。修复仅影响 doctor 与该测试文件，先前其余完整检查继续有效。
- 修复后本机 All doctor：PASS；`git diff --check`：PASS。
- workspace.diff 与 workspace-status.txt 已重新导出最终 HEAD 到工作区差异，用于补齐 reviewer 无 Git 工具的覆盖缺口。
- 修复后聚焦复核：前一轮 F-001/F-002 的 `REVIEW_STATUS: CLEAN` 已保留；复验轮次 2 首次因 handoff 缺少显式 `Review mode: focused` 返回 `REVIEW_STATUS: INVALID`，随后一次受控 replacement retry 返回 `REVIEW_STATUS: FINDINGS`（F-003：旧差异附件），补齐附件后证据续审返回 `REVIEW_STATUS: CLEAN`，F-003 resolved。

## 剩余风险与验收
- 客户端实际端到端对话：NOT RUN；文件一致性和静态合同不能替代真实模型对话。
- 模型和供应商设置保留；不保证别名背后是不同模型。
- Codex 是否能在当前版本提供满足该流程要求的独立 subagent/reviewer 尚未端到端验证；doctor 会明确报告该能力边界。需升级独立审查时可先在 Codex 中验证 native subagent，否则将此审查记为 UNVERIFIED。
- 待用户验收；本次不提交、不推送、不归档。

## 复验轮次 2
- 范围：OpenCode / OMO-Slim 的实现与独立审查模型路由；保留第一轮证据，不改全局 Slim 配置和模型配置。
- 状态：已完成本轮静态交付，待用户验收；静态回归、完整检查、差异证据和 focused review 均完成。真实 OpenCode/Slim 端到端角色调用仍为 `UNVERIFIED`。
- 2026-10-27：真实 OpenCode 用户级安装已同步；`python scripts/doctor.py --scope User --harness OpenCode` PASS；OpenCode/Slim 两份配置安装前后 SHA256 不变。备份位于 `~/.agents/backups/my-engineering-workflow/ecbad68e94204a84b2043dbabea32621/`。
- focused reviewer `ses_e843208d5ffeTeLygizEY549OO` 证据续审：F-003 resolved；Standards / Spec 静态合同覆盖无剩余阻断，`REVIEW_STATUS: CLEAN`。此状态仅适用于静态合同及差异证据，不覆盖真实运行时选模。
- 最终证据更新后 `node --test tests/contracts.test.js` 再次 PASS 52/52；完整 Python 结果为 62 项中 61 通过、1 skipped，不是 62 通过再加 1 跳过。

## 复验轮次 3（2026-11-14）
- 批准范围：AC-007–AC-010，按需专长协作与 Pi/Codex 原生适配；不开发新调度插件、不改用户模型或 toolActivation，不提交/推送/归档。
- 当前状态：独立 full review 两项阻断均修复，唯一 focused 已返回 CLEAN；本轮实现与验证结束、待用户验收。前两轮记录保留，不代表用户已验收。
- 原生角色：新增三个无模型 Codex TOML，保留用户自定义 roles/config；Pi 安装七个指向共享技能的受管理入口。Both 仍为 Codex + OMP。

### 完整检查（阻断修复前）
- `node --test tests/*.test.js`：exit 0，63/63；README 七技能示例已包含 project-standards。
- `python -m unittest discover -s tests`：exit 0，共 81 项，其中 2 skipped（即 79 通过）。
- `openspec validate align-cross-harness-workflow --strict`：exit 0。
- `git diff --check`：exit 0，仅 LF/CRLF 提示。
- 安装前快照 `C:/Users/shuan/AppData/Local/Temp/opencode/workflow-round3-config-before.json` 与安装后 SHA256 归一化比对：Pi settings、Pi subagent config、Pi models、Codex config 共四份全部 UNCHANGED；首次检查的列表索引错误及大小写误报不构成实际配置变化。

### 本地安装与运行证据
- 已实际执行 User / Pi、User / Codex 安装，返回成功；静态 doctor 报告 Pi 7/7 入口，Codex 3/3 角色。doctor 不执行模型会话，runtime 提示继续 UNVERIFIED。
- F-004 修复后再次 `scripts/install.ps1 -Scope User -Harness Pi` 成功，备份共享 workflow skill 至 `~/.agents/backups/my-engineering-workflow/291cba6653f746e39c0c1d0d67248317/001-run-engineering-workflow`；Pi doctor exit 0、7/7，agentOverrides 未改。
- Pi 裸启动真实会话实际发现 `subagent` 和 project `workflow-reviewer`，fresh context、async 派发，返回 terminal complete，并以原生 subagent-notify 回传 README 事实。此为加载扩展/发现/派发/回传证据，不是对本轮代码的完整审查。
- 该 Pi 会话先前工具记录已由主会话读取；临时 shell 日志后续重读路径不存在，故原始全量日志未作为持久附件保存。不能把临时日志路径当作永久证据。
- Codex 真实 `codex exec --json --ephemeral -s read-only -C . ...` 已启动 workflow-reviewer 并返回一项 README 发现，但父命令 180 秒超时、exit 1；完整结果回传与正常终止仍 UNVERIFIED，不算成功端到端烟测。README 漏列技能的问题已修复。
- `pi-subagents` 最初调查为 0.88.0；F-004 修复时实施者读到本机版本 0.88.1，层级合同相同。未授权升级/重配插件，不能将版本变化归因于本安装器。

### 审查及修复证据
- 本轮唯一 full reviewer `ses_e2641fa44ffeM8RQOUf5QjgyQs`；首次交接 INVALID，补齐后唯一受控 replacement 有效，F-004/F-005 为 blocking，见 `review-round3.md`。
- F-004 实施者先 RED 后 GREEN：`node --test --test-name-pattern "Pi launch params keep output top-level|Pi dispatch covers activation" tests/contracts.test.js` exit 0、2/2；后将 sample timeout 精确改为 2147483647，单用例 exit 0、1/1。主会话已读取实际示例与 reference；全套最终检查待 F-005 收敛后一并执行。
- F-005：已严格校验 TOML 语法、必需非空字符串与角色名称；旧 Python 缺 tomllib 时为 unknown / UNVERIFIED，不引入自写解析器或新依赖。现代 Python 聚焦 9 项通过；Python 3.10 共 9 项、4 skipped、其余 5 项通过；覆盖无 parser、空文件、无效 TOML、缺字段、错误 name 和既有诊断。RED 反例证明旧候选 fallback 将 description=42 误作字符串；该候选已删除。
- `workspace-round3.diff` 与 `workspace-round3-status.txt` 为本轮指定范围的 Git 覆盖附件，基线 HEAD `53e4dcfccc94425a62eabdfa9ccc3e445abe9646`，无 staged；主会话将在最终修复完成后刷新附件。既有其他 change 的修改不属于本轮。

### 阻断修复后的最终验证
- `node --test tests/*.test.js`：exit 0，64/64。
- `python -m unittest discover -s tests`：exit 0，共 86 项，2 skipped（84 通过），89.083s。
- `python scripts/doctor.py --scope User --harness Codex`：exit 0，3/3、静态可发现 yes；运行 discovery/delegation/review 仍 UNVERIFIED。
- `openspec validate align-cross-harness-workflow --strict`：exit 0；`git -c core.safecrlf=false diff --check`：exit 0。
- 修复后新真实 Pi 参数烟测：`pi -p --mode json --no-session <bounded runtime smoke prompt>` exit 0。主会话实际调用 read 打开已安装 workflow SKILL；以顶层 output=false、options.context=fresh、options.agentScope=both、options.timeoutMs=2147483647 启动单个 scout；run `56e0d9fa-42f8-4689-a81d-6455f22c5c11` 无参数错误，原生异步回传 `PI_OUTPUT_TOP_LEVEL_OK`，最终 `PI_SMOKE_OK`。仅参数通路烟测，不是新增交付审查。选定事件已落盘 `pi-smoke-round3.json`；不保存包含完整系统上下文的全量日志。
- 同一 reviewer `ses_e2641fa44ffeM8RQOUf5QjgyQs` 唯一 focused：F-004/F-005 resolved，Standards / Spec 无剩余阻断，`REVIEW_STATUS: CLEAN`；详见 `review-round3.md`。reviewer 消费主会话执行证据并独立阅读实际产物，未重跑测试。
- 本轮最终交付范围：按需 coordinator/specialist 路由、Pi 激活/fresh/异步/输出边界、三个无固定模型 Codex 角色、Pi 共享技能入口、分层 doctor 及负向回归；未开发新 Pi 调度器、未更改用户模型/provider/plugin 设置。
- 剩余边界：Codex 完整 runtime 正常退出与完整回传 UNVERIFIED；原 AC-006 OpenCode/Slim 真实运行选模 UNVERIFIED。Pi 参数通路和技能正文 read 已有实际证据，不等于所有角色在全部宿主均完成端到端验收。
- 用户验收前保持 awaiting-acceptance；不提交、不推送、不归档。
