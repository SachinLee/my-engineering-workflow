# 上下文包

## 切片 1/2：行为契约与规划规则

- 目标：禁止无依据兜底、降级、恢复进入方案，必要保障不可删除；只优化已有规则。
- AC-001：开发期无历史数据节点日志，覆盖唯一性/正常异常保存查询，不增历史恢复/所有权状态机/提交查证/降级。
- AC-002：有明确授权/原子性/唯一性要求，保留已有校验、事务和约束，不扩恢复子系统。
- AC-003：阶段/兼容事实未知只做实质性澄清，模板章节不触发新系统。
- AC-004：既有错误契约要求失败可见，无依据空值/缓存 fallback 不伪装成功。
- 已定位现状：`skills/plan-solution/SKILL.md:30-42` 从复用开始；`:190-202` 只有末尾 Ponytail 提醒。`skills/clarify-requirements/SKILL.md:15-24` 已区分技术事实/产品假设，追加阶段范围即可。`skills/run-engineering-workflow/references/workflow-governance.md` 为可安装的共享规则 owner。路由 `skills/run-engineering-workflow/SKILL.md:71-73` 已引用治理，需要将规划列入读取条件。
- 验证现状：`tests/contracts.test.js:252-279` 只检查措辞，删除；`evals/workflow-cases.json` schema_version 3 支持扩展真实场景，不增加语义词匹配器。
- 不可破坏：既有 source trust、risk profile、用户确认/验收/归档、上游不 vendoring、多 harness 安装模式。错误传播与安全/数据完整性不因精简移除。
- 不做：插件安装、评分器、新框架、业务恢复功能、其他 change 修改。
- 验证命令：`npm test`；`pwsh -NoProfile -File scripts/install.ps1 -Scope Project -Harness All -ProjectPath .`；`python scripts/doctor.py --scope Project --harness All --project-path .`；`openspec validate evidence-based-planning --strict`。模型行为通过 `completion` 读取同一 fixture 和真实三份 skill 文件，保存修改前后输出并按场景人工判定。

## 切片 3：独立复核包

- Active change: `openspec/changes/evidence-based-planning/`
- Assigned slice: 切片 3；只读独立复核。
- Phase: verification
- Read: 本 change 的 proposal、spec、design、tasks；前述 4 个治理/skill 文件；`evals/workflow-cases.json` 的 planning 场景；`artifacts/planning-before.json`、`artifacts/planning-after.json`、`artifacts/planning-after-complete.json`、`artifacts/installation-smoke.json`、`artifacts/verification.md`；README 新增使用说明。
- Must preserve: 以上四条 AC 和范围外边界，且没有伪造模型/命令结果。
- Review scope: 是否将安全/必要正确性误判成过度设计；未知事实是否默认生产；文件读取路径能否随安装保留；是否规则重复/过度记账；模型演练是否真的支持判定。
- Evidence: `npm test` 26/26；Project All doctor healthy（保留可选 Ponytail 缺失告警）；OpenSpec strict valid；安装后三根 helper 真实 import/API `ready`、不选择 change，四份规则哈希匹配；5 个实际模型规划场景人工判定 PASS。输入与输出保存在上述 JSON，独立复核 `REVIEW_STATUS: CLEAN`；全部证据及未验证边界见 `artifacts/verification.md`。
- reviewer 不修改生产或治理文件，不运行构建/lint/tests/formatter；主会话已负责单次最终验证，只有可疑具体缺陷需给复验建议。
