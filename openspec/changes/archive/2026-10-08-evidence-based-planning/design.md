# 方案

## 背景与边界

对应 AC-001 至 AC-004，优化已有规则而非增加执行框架。skill 是模型解释的行为契约，源文本匹配不能证明模型规划结果。

## 方案与职责

1. `skills/run-engineering-workflow/references/workflow-governance.md` 新增单一「Evidence-Based Planning」规则：先判断是否需要、额外机制举证、未知事实澄清、必要保障保留、模板不扩 scope。规则只要求争议机制的一句依据，不创建独立 checklist 或产物。
2. `skills/clarify-requirements/SKILL.md` 明确读取该章节，需求中记录影响行为的项目阶段/兼容/恢复范围，避免固定问题表。
3. `skills/plan-solution/SKILL.md` readiness 读取规则；复用阶梯前加必要性；设计模板不生成需求；交付复查无依据机制没有混入任务。已有上下文包保留实际不变量与事实。
4. 路由 skill 的治理读取说明纳入需求边界与规划，不修改路由状态机或 agent 定义。

## 验证接缝

先在 `evals/workflow-cases.json` 添加 5 个真实用户场景及判断标准，删除两个只检查规划/澄清措辞的契约测试。其余无关测试不重写。修改规则前，使用工具 `completion` 加载真实的澄清、规划、共享治理文件，输出完整方案作为基线；修改后在相同输入上演练。按行为人工审阅，不按关键词自动打分，也不以 fixture 存在性冒充语义 PASS。模型输入、输出与判定写入 change 的验证产物，便于用户复验。

Node 测试只证明现有仓库契约未破坏。实际运行安装器同步项目内 Codex/OMP/Claude/Pi 副本，再运行诊断与 OpenSpec 严格校验。独立 reviewer 从新上下文审阅规则、场景结果和遗漏边界。

## 否决方案

- 强制加载/安装 Ponytail：需要额外上游前置条件，不能保证必要性规则已经执行；本次只引用能力，不复制其正文。
- 复杂度评分、关键词分类器、运行时 gate：新增机制比待修问题更复杂。
- 为所有错误处理增加逐项举证文档：会制造新的规划负担，只对拟新增的额外机制要求简短依据。

## 兼容与回退

不变更公开 API、文件布局和 quality profile。不需要迁移业务数据；回退恢复规则文件并重新运行既有安装器即可，不设计兼容层。

## 验收追溯

| 验收 | 设计点 | 场景 |
| --- | --- | --- |
| AC-001 | 必要性优先、按实际阶段 | planning-development-logs |
| AC-002 | 必要保障与复用 | planning-required-safeguards |
| AC-003 | 有条件澄清、模板不扩 scope | planning-unknown-stage、planning-template-pressure |
| AC-004 | 无依据 fallback 排除、错误契约保留 | planning-error-contract |

## 风险

模型执行仍具有非确定性。修改前若已符合场景，不伪造 RED；修改后通过只作为本次演练证据。不适用上游插件缺失须保持真实报告，不修改安装器来掩盖告警。
