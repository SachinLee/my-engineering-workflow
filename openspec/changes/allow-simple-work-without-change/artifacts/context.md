# 上下文包

## 共用边界
- Active change: `openspec/changes/allow-simple-work-without-change/`
- 用户已选非行为性小改动，明确允许创建并实施。本次不扩大到小型行为bug修复。
- 原有归档移动、legacy、全局harness、外部gate及上游内容禁止修改；只在本change写持久交付状态。
- 唯一资格源：`skills/run-engineering-workflow/references/quality-profiles.md`。
- 可修改12源：`skills/run-engineering-workflow/SKILL.md`、其 `references/quality-profiles.md`、`references/workflow-governance.md`、`agents/openai.yaml`；`commands/engineering-workflow.md`；`README.md`；`ARCHITECTURE.md`；`skills/plan-solution/SKILL.md`；`skills/finish-with-evidence/SKILL.md` 及其 `agents/openai.yaml`；`tests/contracts.test.js`；`evals/workflow-cases.json`。

## 切片1：前置分流（主会话实现）
- AC-001：资格先于任何discovery/建档，合格请求不因CLI或无关change进入正式分支。
- AC-002：不创建/修改任务记录，无建档确认、正式规划、委派或默认独立审核。
- AC-004：行为/高风险/依赖、项目更严格规则、显式OpenSpec、选定change续接及正式计划/交接/委派需求保留正式模式；扩大实现前先停。
- AC-005相关部分：命令和流程图采用同样次序。
- 已定位：主路由 `Locate Canonical State` 第一步先读config并调用list_changes；命令Steps第1步为discovery；governance `Record Layout` 的routing invariant将所有new work视作OpenSpec。
- 现成模式：Node测试使用 `read(relativePath)` 读取公开技能，再用assert.match/assert.doesNotMatch核对合同；evals是 `schema_version:3`、`cases`，包含 `name/state/expected_stage/forbidden`。
- 设计：先读项目规则与共享资格；命中则主会话一条快路径，未命中才执行旧discovery/确认。治理把持久记录限定到正式模式，不增加新配置/脚本。
- 不变量：不得改变Standard/Critical审核预算和原有创建/复用确认语义；不得将CLI故障伪装成no-match或降级理由。
- 新读：上述源/测试当前相关段；proposal/spec/design不必再调查。
- 返回：`node --test tests/contracts.test.js` 的RED/GREEN、路径和风险。

## 切片2：后续入口（主会话实现）
- AC-003：检查diff与项目要求的最小验证，在对话报告真实结果及NOT RUN，不伪称独立CLEAN。
- AC-004升级：发现行为/风险/正式交接要求时，停止扩大实现，保留diff/check，再按原规则确认正式任务。
- AC-005：plan和finish若消费到主路由已选fast，先返回快路径；未选fast或已选change不能自行降级。
- 已定位：plan `Confirm Readiness` 第一步假定proposal已存在；`Lightweight Planning`要求proposal-only；finish开头要求写verification且Consume第一步读取change。README `1.直接说明需求` 和 `3.规划技术方案`仍有强制legacy/proposal示例，需限定为正式路径。
- 设计：入口早返回只引用共享资格，不复制资格清单；finish快路径只报告已有检查，不自行补跑或建档。router执行最小检查，finish消费。
- 不变量：正式模式原有检查与待验收归档不变；失败不能声称通过；scope升级不能自动建档或丢弃现有修改。
- 新读：plan/finish及其prompt、tests/evals的相关段。
- 返回：同Node RED/GREEN；`npm test`、`python -m unittest discover -s tests -p 'test_*.py'`、`openspec validate allow-simple-work-without-change --strict`、隔离和本项目 `pwsh -NoProfile -File scripts/install.ps1 -Scope Project -Harness All -ProjectPath <path>` 比对证据。

## 完整审核交接（仅交付范围完成后派发一次）
- Review mode: full
- 已批准范围：12源和本change规划/证据；不得把已有其他归档移动当作本次实现。
- 必须读取：本change proposal/spec/design/tasks，`artifacts/review-inputs.json`、`artifacts/review-input.patch` 和最终验证日志；再查必要源，不能只用HEAD差异认证工作区。
- 覆盖AC-001～006的Standards/Spec、边界、检查完整性、快速分支和正式分支是否冲突。此fixture不是四宿主runtime执行证明。
- 禁止派子reviewer或要求额外generic/code-reviewer；仅报告真实阻断，风格建议不阻断。
- 返回：可识别 `REVIEW_STATUS: CLEAN|FINDINGS|INVALID`，findings带合同/失败场景/影响和源路径；没有报告或执行失败不能冒充CLEAN。
