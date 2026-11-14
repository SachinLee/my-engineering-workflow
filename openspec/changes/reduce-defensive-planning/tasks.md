# 任务

## 1. 规划规则与行为合同

- [x] 1.1 在 `tests/planning-simplicity.test.js` 先增加 `node:test` 回归合同，要求共享规划指导和 `plan-solution` 都含有反事实准则且明确保留必要保护、不生成普通错误逐行清单；运行 `node --test tests/planning-simplicity.test.js` 确认新增断言因缺少准则而失败。（证据：RED 5 项失败——反事实准则、plan-solution 引用、案例/协议/verification 缺失）
- [x] 1.2 在 canonical `skills/run-engineering-workflow/references/workflow-governance.md` 增加最短反事实准则，并让 `skills/plan-solution/SKILL.md` 的既有方案审查步骤指向它；运行 `node --test tests/planning-simplicity.test.js` 和 `npm test` 验证通过。（证据：GREEN，`npm test` 59 项通过）

### 切片 1 上下文包

- 行为：正式方案只保留能关联明确 AC/必要不变量及可达失败的非平凡防御机制；必要保护不因简化而删除，普通错误处理不要求逐行论证。
- 验收标准：AC-001 要求每个非平凡 fallback、retry、compensation、recovery、兼容分支、开关或扩展点有明确 AC/不变量、可达失败场景、现有保护不足和省略后果；无证据时不得列为功能。AC-002 要求保留安全、数据完整性、并发、资源清理保障，不为普通错误处理新增逐项清单。
- 相关设计：只改 canonical 共享规则及 `plan-solution` 的现有审查步骤，不复制到宿主 agent 模板；以一个新增 node:test 文件隔离测试，避免改动已有大而且当前被用户修改的 `tests/contracts.test.js`。
- 已定位：`skills/run-engineering-workflow/references/workflow-governance.md:82-108` 已有 Evidence-Based Planning，新增内容只显式化反事实判断；`skills/plan-solution/SKILL.md:222-223` 已检查额外机制，沿用该位置。
- 不变量：不得弱化授权、安全、数据完整性、并发一致性、资源清理和现存错误传播；未知事实记录为风险，不自动扩展成生产需求。
- 验证：`node --test tests/planning-simplicity.test.js`；`npm test`。
- 需要新打开：`package.json` 确认测试脚本；上述两个 canonical skill 文件及 OpenSpec spec。
- 允许修改：上述两个 canonical skill 文件、`tests/planning-simplicity.test.js`、本 change 的 `tasks.md` 与 verification artifact。
- 禁止修改：OMP 代码/配置、`.agents/skills` 旧副本、其他 harness agent 配置、其他 OpenSpec change、既有用户未提交修改。
- 升级条件：如需改共享规则以外的 agent/config，或发现 AC 与现行安全不变量冲突，停止并回报，不扩大范围。
- 返回证据：RED/GREEN 命令及结果、修改文件、未运行检查及剩余风险。

## 2. 消融材料与试点

- [x] 2.1 新增 10 个脱敏合成规划案例及手工 A/B 盲评协议；新增测试验证 JSON 可解析、案例数和风险类别覆盖，并运行 `node --test tests/planning-simplicity.test.js` 与 `npm test`。（证据：`evals/planning-ablation-cases.json` 10 例、`evals/planning-ablation-protocol.md`；JSON/schema/风险覆盖测试通过）
- [x] 2.2 已完成条件检查与逐例状态记录；实际模型试点为 `NOT RUN`。原执行约定：对冻结的 10 个案例执行一次配对试点：两组只差新增准则，固定可确认的模型、上下文与工具，使用独立会话并盲评；将案例级结果、无依据机制变化、必要 AC/不变量覆盖、可验证性、实现工作量和限制记录到 `openspec/changes/reduce-defensive-planning/artifacts/verification.md`。若无法确认相同有效模型或隔离条件，记录 `NOT RUN` 及具体原因，不得模拟或声称有效；核对报告对 10 个案例均有成对状态，且必要 AC/不变量无遗漏。（证据：verification.md 逐案例 A/B 均记录 `NOT RUN` 及阻碍原因——执行子代理未具备可核对有效模型的独立会话与盲评条件；未模拟输出或评分）

### 切片 2 上下文包

- 行为：为提示策略变化提供可选的一次性、方向性消融，不引入常驻运行器；简化只能在必要 AC/不变量零回退时得到正向信号。
- 验收标准：AC-003 要比较无依据机制数量、AC/必要不变量覆盖、可验证性和实现工作量；多数案例无依据机制减少且必要覆盖零回退才为正向信号，篇幅/token 下降不算成功。AC-004 要求同模型、同输入条件、独立 A/B 会话和盲评；高风险保护只可推演/隔离验证。AC-005 要求有可核对材料，未运行标 `NOT RUN`。
- 相关设计：新增 10 个合成案例和手工协议；一次配对试点才是可选经验评估，不加自动 runner、agent 或 MCP。若当前 harness 不能确认执行条件，报告 `NOT RUN`，不从规则文本或合同测试推断模型行为改善。
- 不变量：试点不操作生产数据或用户授权；不能为了得出简化结果而删除保护；小样本只作方向性证据，不宣称统计显著。
- 验证：`node --test tests/planning-simplicity.test.js`；`npm test`；人工检查 verification artifact 覆盖 10 对输出和盲评状态。
- 需要新打开：`evals/workflow-cases.json` 了解现有案例格式；`openspec/changes/reduce-defensive-planning/specs/planning-simplicity-evaluation/spec.md`。
- 允许修改：`evals/planning-ablation-cases.json`、`evals/planning-ablation-protocol.md`、新增测试及本 change 的 `artifacts/verification.md`。
- 禁止修改：生产提示、用户全局模型/API设置、OMP和其他 harness 配置、无关评测 runner 或其他 change。
- 升级条件：模型条件、独立会话或盲评无法满足时，停止实际试验并记录 `NOT RUN` 原因；遇到高风险机制时只做反事实，不在生产验证。
- 返回证据：JSON/协议合同测试、10 例的 A/B 状态与评分或 `NOT RUN` 说明、实际模型与限制。
