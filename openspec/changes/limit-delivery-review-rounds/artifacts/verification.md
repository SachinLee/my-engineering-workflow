# 交付验证

## 交付
- Active change: `limit-delivery-review-rounds`
- 状态：`complete`（实现及要求的验证完成，用户验收尚未进行）。
- 交接阶段：`awaiting-acceptance`
- 时间：`2026-10-14T14:54:50+08:00`
- 概述：每个已批准交付范围默认只派发一次完整独立 `workflow-reviewer`；阻断修复最多一次定向复核；不叠加 `code-reviewer` 或 Matt 原生审核。收尾仅消费和记录证据，不自行补跑或派发。预算跨会话/快照保留，扩大范围和预算用尽由用户决定。

## 验收标准
以下 PASS 指已实现并验证的文本合同、场景资产和安装一致性，不等于四个宿主已经具备运行时强制预算。

| 标准 | 结果 | 证据 |
| --- | --- | --- |
| AC-001 交付级预算与单审核代理 | PASS | `quality-profiles.md` 的 Delivery Review Budget；主路由、命令、治理、Root/OMP/Pi适配；Node 的 `delivery review budget bounds rounds rather than only reviewer count`、`routing reviews the delivery scope once and never adds code-reviewer`；独立报告 |
| AC-002 修复最多一次定向复核 | PASS | review技能/三个reviewer中的 `Review mode: full | focused`、原阻断/修复diff/直接影响范围、预算用尽 `blocked`；Node模式断言和focused/exhaustion场景；独立报告 |
| AC-003 建议不阻断且预算跨会话保留 | PASS | 具体合同/不变量、失败场景和影响作为阻断判据；可选建议不触发修复；现有artifacts保留轮次；无有效报告INVALID最多一次受控替换；Node预算断言和suggestion/resume/INVALID场景 |
| AC-004 收尾只消费证据 | PASS | finish正文和UI prompt同步；Node的 `finish consumes evidence and returns gaps without scheduling or running checks`、`workspace review and finish reuse a complete independent result`；本次收尾未重跑仓库测试、未派发新审核 |
| AC-005 完整重审须用户决定 | PASS | 预算源要求AC/接口/安全边界/方案/范围变化时请求用户授权，保留旧轮次；Node user approval断言和scope drift场景；独立报告 |
| AC-006 安装一致且证据真实 | PASS | Node 34/34、Python 16/16、OpenSpec strict validation valid；隔离/本项目All安装54项比对PASS；tracked sources及旧 `.pi/skills` 字节保留；完整1/定向0/替换0的CLEAN独立报告；NOT RUN明确记录 |

## 实现
- 唯一预算源：`skills/run-engineering-workflow/references/quality-profiles.md`。
- 调度与引用：`skills/run-engineering-workflow/SKILL.md`、`references/workflow-governance.md`、`commands/engineering-workflow.md`、`README.md`、`ARCHITECTURE.md`。
- 审核与收尾：`skills/review-implementation/SKILL.md`、`skills/finish-with-evidence/SKILL.md`、`skills/finish-with-evidence/agents/openai.yaml`。
- 适配：`agents/workflow-reviewer.md`、`.omp/agents/workflow-reviewer.md`、`.pi/agents/workflow-reviewer.md`。
- 测试资产：`tests/contracts.test.js`、`evals/workflow-cases.json`。
- 设计决策：主路由是唯一审核调度者，review技能只定义过程；完整报告、必要的定向报告和修复检查组成覆盖链；不能用旧报告独自批准未经复核的修复。
- 与design的差异：同步了finish的UI prompt，避免入口仍诱导“重新验证”；其实施前内容保存在 `artifacts/baseline-extra.json`。不增加执行引擎、状态文件或新依赖。
- 用户原有未提交改动按 `artifacts/baseline.json` 区分；本次patch不以HEAD恢复或覆盖用户工作。不修改第三方 `code-reviewer` 或宿主全局配置。

## TDD 证据
- 切片1 RED：`node --test tests/contracts.test.js`，新增预算/路由断言在旧规则上失败，见 `artifacts/slice-1-red.log`。
- 切片1 GREEN：同命令通过该片已落实的合同，见 `artifacts/slice-1-green.log`；下一片仍保留待实现的失败断言。
- 切片2 RED：同命令的focused/finish新断言在旧规则上失败，见 `artifacts/slice-2-red.log`；补UI prompt断言后 `artifacts/slice-2-ui-red.log` 保留了修复前失败。
- 切片2 GREEN：同命令最终34/34通过，见 `artifacts/slice-2-green.log`。
- 最终全套GREEN：`npm test` 34/34，见 `artifacts/node-test.log`。没有补造RED、覆盖率或命令结果。

## 验证
| 确切命令或检查 | 结果 | 证据 |
| --- | --- | --- |
| `npm test` | PASS，34/34 | `artifacts/node-test.log` |
| `python -m unittest discover -s tests -p 'test_*.py'` | PASS，16/16 | `artifacts/python-test.log` |
| `openspec validate limit-delivery-review-rounds --strict` | PASS，valid | `artifacts/openspec-validation.log` |
| `pwsh -NoProfile -File scripts/install.ps1 -Scope Project -Harness All -ProjectPath "C:/Users/shuan/AppData/Local/Temp/workflow-review-budget-740x3gob"` | PASS，隔离项目安装 | `artifacts/isolated-install.log` |
| `pwsh -NoProfile -File scripts/install.ps1 -Scope Project -Harness All -ProjectPath "D:/my-works/claude-skills/my-engineering-workflow"` | PASS，本项目受管副本同步 | `artifacts/project-install.log` |
| 安装源/产物内容比对 | PASS，54项技能/代理检查及helper、命令、OMP配置比对；tracked sources与旧Pi镜像不变 | `artifacts/installation-smoke.json` |
| 收尾证据关联（不是重跑测试） | PASS，14/14最终审核输入SHA-256未变化 | `artifacts/review-inputs.json` 与 `artifacts/review.md` |
| 可选JS LSP诊断 | NOT RUN，`biome LSP command not found: biome. Install biome or update its command in pi-lsp.json.` | 当前会话工具结果；未安装依赖或伪称诊断通过 |
| 真实四宿主端到端自动派发及外部OMP gate行为 | NOT RUN，超出本次已批准范围 | proposal/design范围边界；静态fixture仅证明合同一致性 |
| 独立lint/typecheck/build命令 | NOT APPLICABLE，本薄编排仓库没有独立对应package脚本；已执行现有Node/Python测试 | `package.json`及上述日志 |

## 独立复核
- 角色：唯一 `workflow-reviewer`，新独立模型上下文，未指定model覆盖，未追加 `code-reviewer`。
- run id：`9af19fff-a580-479e-85f0-709067d4d0f6`。
- 完整轮数：1；定向轮数：0；INVALID替换：0。
- 状态：`REVIEW_STATUS: CLEAN`，Standards和Spec充分覆盖AC-001～AC-006，无阻断问题，无需修复或定向复核。
- 原始报告：`artifacts/review-full-result.md`；轮次和范围记录：`artifacts/review.md`。
- 输入：`artifacts/review-inputs.json`声明14个源/测试最终字节指纹；`artifacts/review-input.patch`相对实施前baseline的增量（统一EOL便于阅读）。
- 收到报告后仅核对输入未变化并追加交付记录；未重新测试、未改变实质输入、未重新派发。非阻断的轮次记录建议已在现有review记录补齐。

## 本地 harness 同步（用户授权续接）
- 时间：`2026-10-14T15:09:59+08:00`；范围：`User`，目标：`All`（Codex / OMP / Claude Code / Pi）。
- 安装命令：`pwsh -NoProfile -File scripts/install.ps1 -Scope User -Harness All`，exit `0`；安装前已执行同参数 `-WhatIf`。
- 实际路径：`C:/Users/shuan/.codex/skills`、`C:/Users/shuan/.omp/agent`、`C:/Users/shuan/.claude`、`C:/Users/shuan/.pi/agent`。本次不改宿主全局第三方 `code-reviewer`。
- 回滚备份：`C:/Users/shuan/AppData/Local/Temp/workflow-user-install-backup-5ykh67pd`；备份39个受管目标，备份索引见 `artifacts/user-installation-backup.json`。该本地临时备份不提交，不包含在安装目标中。
- 安装证据：`artifacts/user-install.log`、`artifacts/user-installation-smoke.json`；78/78源文件与安装副本逐字节一致，1071个无关文件及配置摘要保持不变（包含OMP全局配置）。
- 源码提交前再次核对14/14独立审核输入指纹未变化，20个暂存源文件的 `git diff --cached --check` 通过；不因同步或commit开启新审核/重跑仓库测试。
- 记录提交检查：普通 `git diff --cached --check` 对 `artifacts/review-input.patch` 的单空格空白上下文行报错；这是 unified diff 必需语法，未删改证据。其余暂存记录的空白检查通过；对原patch仅在内存统一EOL后，在隔离baseline索引应用并比对，14/14输出与最终源内容一致。原文件不变，见 `artifacts/commit-record-checks.json`。
- 仍不声称真实四宿主派发或外部OMP gate的运行时强制预算已验证；已加载会话需要重启或新建会话以加载新规则。

## 提交
- 初次交接未提交；随后用户明确要求提交并同步本地 harness，且确认包含必要前置改动。
- `COMMITTED`：源码提交 `92d722f7426374035687b8d64d5b7e6ff8b596fc`，分支 `main`，标题 `feat: 限制交付审核轮次并同步前置工作流策略`；20个源文件，包含前置上游同步及子代理时限移除。
- 本 change 及两个必要前置 change 的 OpenSpec 记录随后单独提交；不包含其他归档移动、legacy或本地生成副本。
- `NOT PUSHED`：没有执行push；用户提交授权不是验收或归档授权。
- 本地日志遵循 `.gitignore` 留在原目录；版本化保留规划、审核报告、验证摘要与指纹，不强制添加忽略文件。

## 剩余风险
- 这次优化的是本仓库技能/代理合同与安装副本，不是运行时强制审核预算。模型仍可能受宿主全局指令影响；本次不修改全局 `code-reviewer` 定义。
- 外部 `omp-extensions/workflow-review-gate` 仍存在 `Active task:` 与新 `Active change:` 的识别边界；安装复制并不意味着该边界修复。其运行时变更需要另行授权和验证。
- 可选LSP缺少 `biome`；如需要诊断，可安装该命令或更新 `pi-lsp.json`，本次没有为此额外安装依赖。
- 已运行会话的已加载指令不一定即时刷新；建议在新会话验证新安装规则，遇到重复派发时保留真实调用日志再定位宿主触发源。

## 用户验收
- 状态：待用户验收，`awaiting-acceptance`；代理未接受或归档。
- AC-001：新会话完成一个Standard任务，观察只调用一次完整 `workflow-reviewer`，不追加 `code-reviewer`；未完成交付范围的切片只做相关检查。
- AC-002：有阻断项时集中修复，观察最多一次focused，仅检查原阻断及修复影响；若仍有阻断则停止并报告。
- AC-003：只存在风格/简化建议时不继续打磨审核；恢复同change时读取已有轮次而非重启；INVALID不能替代有效FINDINGS。
- AC-004：对已有有效证据调用finish，观察仅记录/交接，不补跑全套测试、不派审核；缺口明确返回主路由。
- AC-005：扩大AC/接口/安全边界/方案后，观察请求用户决定，不自动完整重审或重置预算。
- AC-006：可复跑 `npm test`、上述Python和OpenSpec命令；查看 `installation-smoke.json` 和独立报告。真实宿主验收尚未执行，不把该清单当成已运行结果。
- 验收后若需归档，请明确要求代理执行，或自行使用 `openspec archive limit-delivery-review-rounds`；本次不运行归档、不追加journal、不清legacy指针。
