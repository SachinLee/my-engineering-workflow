# 交付验证：reduce-defensive-planning

## 交付

- 状态：`awaiting-acceptance`；实现、验证和独立复核完成，待用户验收。
- 日期：2026-11-14。
- 范围：共享规划指导、10 个合成案例、手工 A/B 协议和合同测试。OMP 暂停；未发布到用户级 skills，未修改宿主模型、权限或插件配置。
- 模型试点：`NOT RUN`；材料交付不构成模型行为改善证据。

## 验收标准

| 标准 | 结果 | 证据与边界 |
| --- | --- | --- |
| AC-001 | PASS | `workflow-governance.md` 的 Evidence-Based Planning 新增反事实删除判据，沿用现有证据门槛；`plan-solution` 的既有审查步骤引用它；合同测试 1、3 通过。 |
| AC-002 | PASS | 必要安全、数据完整性、并发和资源清理保护保留，普通错误不增加逐行清单；合同测试 2 通过。 |
| AC-003 | 合同 PASS；试点 NOT RUN | 协议包含四个评价维度、机制计数方式和多数案例减少且必要覆盖零回退的判定；合同测试 5 通过。实际效果尚未评估。 |
| AC-004 | 合同 PASS；试点 NOT RUN | 协议固定变更前基线、有效模型/上下文/工具条件、独立会话与盲评；评分参考不交给生成器；高风险仅推演或隔离。合同测试 5、6 通过；实际试点 `NOT RUN`。 |
| AC-005 | 合同 PASS；试点 NOT RUN | 6 项合同测试通过；10 例均有成对 `NOT RUN` 记录并如实说明原因，不从文本检查推断模型改善。 |

## 实现

- 修改：`skills/run-engineering-workflow/references/workflow-governance.md`、`skills/plan-solution/SKILL.md`。
- 新增：`tests/planning-simplicity.test.js`、`evals/planning-ablation-cases.json`、`evals/planning-ablation-protocol.md`。
- 保留：原有 `plan-solution` 项目规范/上下文包改动及其他用户未提交改动；不手工同步旧宿主副本。
- 设计保持不变。审查修复收紧了协议的 A 组基线与生成/评分隔离；移除常驻测试对当前 change 路径的依赖，归档后无需保留该路径。

## TDD 证据

- 执行代理报告的原始 RED：`node --test tests/planning-simplicity.test.js`，5 项失败、1 项通过；缺失反事实规则、引用和新增材料。主线程未独立复跑这一历史状态。
- 主线程修复 RED：新增“变更前基线与评分提示隔离”合同后运行同一命令，5 项通过、1 项失败，错误为 `A must be frozen before the candidate rule is introduced`。
- 修复 GREEN：同一命令 6/6 PASS；`npm test` 59/59 PASS。

## 已执行验证

以下修复后结果由主线程于 2026-11-14 实际执行：

- `node --test tests/planning-simplicity.test.js`：exit 0，tests 6 / pass 6 / fail 0。
- `npm test`：exit 0，tests 59 / pass 59 / fail 0；已修正任务记录中误写的 63。包含既有合同测试和用户已有 project-standards 测试。
- `openspec validate reduce-defensive-planning --type change --strict --json`：exit 0，valid true，issues []。
- `git diff --check -- skills/run-engineering-workflow/references/workflow-governance.md skills/plan-solution/SKILL.md`：exit 0，无空白错误；Git 仅提示将来 checkout 时可能转换 LF/CRLF。
- 使用 hashline `read` 读取案例和本记录并逐项核对：10 个唯一案例、10 行状态，A/B 均为 `NOT RUN`，无缺项。此核对不是常驻测试，不依赖当前 change 路径继续存在。
- `pwsh -NoProfile -File scripts/install.ps1 -Scope User -Harness Codex -WhatIf`：exit 0。
- `pwsh -NoProfile -File scripts/install.ps1 -Scope User -Harness Claude -WhatIf`：exit 0。
- `pwsh -NoProfile -File scripts/install.ps1 -Scope User -Harness Pi -WhatIf`：exit 0。
- `pwsh -NoProfile -File scripts/install.ps1 -Scope User -Harness OpenCode -WhatIf`：exit 0。
- 上述仅为非 OMP 安装预演，不是实际安装或宿主运行时效果验证。
- lint、typecheck、build：不适用；`package.json` 仅定义 `test`，本切片为 Markdown/JSON 及直接由 Node 执行的 `.test.js`，没有对应编译或独立静态检查脚本。未额外引入检查工具。

## 独立复核

- 预算：一次 full 与一次 focused 均已完成；最终 `REVIEW_STATUS: CLEAN`，无剩余阻断项。
- Full：独立 `workflow-reviewer`，运行 `24d9e656-ec6e-4d7e-b6b9-56a5fcb9cff0`，`REVIEW_STATUS: FINDINGS`。B1 为任务记录 63 与实现报告 59 不一致；S1 为试点勾选易误读；T1/T2/T3 为正则误匹配、缺少禁止语义和章节边界过宽。
- 主线程修复：测试数统一为 59；2.2 行明确实际试点 `NOT RUN`；测试使用 AC 词边界、反事实条款和章节范围，并匹配必要保护/禁止清单语义。另修复当前 change 路径耦合与 A/B 基线含候选条款的风险。
- Focused：原独立 reviewer 在运行 `42c5215e-eeca-4904-b945-8807194f6b13` 完整补读 AGENTS、审查 skill、质量档位和 design；确认 B1/S1/T1/T2/T3 全部 resolved，无阻断回归。结合原 full 覆盖 AC-001 至 AC-005；原 Standards 读取缺口已补齐。reviewer 无 shell，测试/diff 结果来自主线程实测，不声称独立复跑。
- Focused 的 N1/N2 建议已落实：AC-003/004/005 标明“合同 PASS；试点 NOT RUN”，并记录 lint/typecheck/build 的适用性。此后仅交付记录变化，不影响已通过的实现检查。
- Full 报告：`C:/Users/shuan/.pi/agent/sessions/--D--my-works-claude-skills-my-engineering-workflow--/subagent-artifacts/outputs/04228c59-f32d-41f5-b100-cce07d706770/planning-full-review.md`。
- Focused 报告：`C:/Users/shuan/.pi/agent/sessions/--D--my-works-claude-skills-my-engineering-workflow--/subagent-artifacts/outputs/42c5215e-eeca-4904-b945-8807194f6b13/planning-focused-review.md`。

## 模型试点逐案例状态

本次未建立可核对有效模型和提示注入的独立 A/B 会话，也未执行盲评；执行子代理未提供可用外部模型调用工具。按 AC-004/AC-005 记录 `NOT RUN`，不模拟输出或评分。

| 案例 | 风险类别 | A 臂 | B 臂 | 评分状态 | 说明 |
| --- | --- | --- | --- | --- | --- |
| ablation-simple-report-page | simple | NOT RUN | NOT RUN | 未评 | 有效模型与独立会话未建立 |
| ablation-simple-name-sort | simple | NOT RUN | NOT RUN | 未评 | 有效模型与独立会话未建立 |
| ablation-ordinary-log-save | ordinary | NOT RUN | NOT RUN | 未评 | 有效模型与独立会话未建立 |
| ablation-ordinary-query-error-contract | ordinary | NOT RUN | NOT RUN | 未评 | 有效模型与独立会话未建立 |
| ablation-ordinary-upload-validation | ordinary | NOT RUN | NOT RUN | 未评 | 有效模型与独立会话未建立 |
| ablation-ordinary-config-switch | ordinary | NOT RUN | NOT RUN | 未评 | 有效模型与独立会话未建立 |
| ablation-high-order-dedup | high | NOT RUN | NOT RUN | 未评 | 高风险：仅可反事实/隔离验证，未执行 |
| ablation-high-auth-boundary | high | NOT RUN | NOT RUN | 未评 | 高风险：仅可反事实/隔离验证，未执行 |
| ablation-high-display-name-migration | high | NOT RUN | NOT RUN | 未评 | 高风险：仅可反事实/隔离验证，未执行 |
| ablation-high-resource-cleanup | high | NOT RUN | NOT RUN | 未评 | 高风险：仅可反事实/隔离验证，未执行 |

10/10 案例均有成对状态；无依据机制变化、必要覆盖、可验证性及工作量没有实际试点数据，均未评。

## 提交与边界

- `NOT COMMITTED`；检查基点为 `620e1b169ffad92390ea0a244f742ccd19e32806`，暂存区为空。
- 本 change 以外的用户已有修改保留；未接受、归档任何 change，未写 `.workflow/` 或 `.trellis/`。

## 剩余风险与验收

- 模型行为效果 `NOT RUN`；10 例是合成数据，即使后续运行也仅作方向性证据。
- 实际安装/宿主发现新版本 `NOT RUN`；本次只交付 canonical 源码，旧项目级 skill 副本仍需后续安装流程处理。
- 已完成交付，当前为 `awaiting-acceptance`。用户验收及归档尚未执行；待用户明确要求后再处理归档。
