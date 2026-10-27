# 交付验证

## 交付
- 状态：awaiting-acceptance；第一轮实现与复核完成，复验轮次 2 的 AC-006 静态合同、差异证据和 focused review 已完成。
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
