# 上下文包

## 切片 1（主会话执行）
- 验收标准：proposal 中 AC-001、AC-003、AC-005。
- 已定位：`skills/run-engineering-workflow/references/quality-profiles.md:21-31` 只限制一个 reviewer，仍要求修复后审核新快照；`skills/run-engineering-workflow/SKILL.md:210-226` 每次 Code changed 容易触发完整审查；`commands/engineering-workflow.md:39-44` 同样要求修复后再审核。
- 决策：交付级完整审核一次、必要时定向最多一次，预算不被新快照/会话重置；默认不追加 `code-reviewer`。
- 现成模式：`tests/contracts.test.js:25-75` 跨文件文本合同断言；`evals/workflow-cases.json` 是场景资产，不是运行时调度实现。
- 验证：`node --test tests/contracts.test.js`，预期 RED 命中新断言，GREEN 保持旧合同不回退。

## 切片 2（主会话执行）
- 验收标准：proposal 中 AC-002、AC-004、AC-006。
- 已定位：`skills/finish-with-evidence/SKILL.md:17-42` 重新跑检查、修改后新审查；`skills/review-implementation/SKILL.md:50-59` 材料变化即新审核；Root/OMP/Pi reviewer 定义同样要求 fresh review。
- 决策：`Review mode: full | focused`，focused 只核对原阻断项和修复影响；finish 检查证据关联，不直接运行验证/派发。
- 不变量：完整相关工作区，包括 staged/unstaged/显式 untracked；独立性、Standard/Critical 分类、Pi 只读工具、OMP `@advisor`、用户归档权限保持。
- 安装：`scripts/install.ps1` 的 All 同步 Codex/OMP/Claude/Pi；Pi 项目技能目标 `.agents/skills`，Root agents 安装到 `.claude/agents`，OMP/Pi agents 已是仓库源，保持同步合同。
- 验证：`npm test`；`python -m unittest discover -s tests -p 'test_*.py'`；PowerShell 隔离 All 安装与源内容比对。本项目同步不更新 legacy `.pi/skills`。

## 最终独立审核派发包
Active change: openspec/changes/limit-delivery-review-rounds/
Assigned slice: review / AC-001～AC-006
Phase: review
Review mode: full
Read: 本包、proposal.md、specs/delivery-review-budget/spec.md、design.md、tasks.md；先读取 artifacts/review-inputs.json 与 artifacts/review-input.patch，再按 diff 定位明确声明的源/测试和直接影响安装文件。
Must preserve: 用户既有未提交修改；Root/OMP/Pi 模型与工具限制（OMP @advisor、Pi 无 model 且只读）；无 injector；legacy 只读；用户验收归档权限。主会话单 writer，reviewer 只读，不嵌套派发，不运行外部 gate，不提交或归档。
Review scope: artifacts/baseline.json + artifacts/baseline-extra.json 到最终当前内容的增量，不把 HEAD 上的其他工作混入本 change。14 个声明输入的 SHA-256 在 artifacts/review-inputs.json；patch 为便于阅读统一 EOL，哈希以实际字节为准。覆盖 staged/unstaged 和显式当前材料，不仅 committed diff。安装副本仅核对声明技能及 reviewer 适配。
Evidence: npm test → 34/34 PASS（artifacts/node-test.log）；python -m unittest discover -s tests -p 'test_*.py' → 16/16 PASS（artifacts/python-test.log）；openspec validate limit-delivery-review-rounds --strict → valid；隔离和本项目 All 安装源/产物比对54项 PASS（artifacts/installation-smoke.json）。两切片 RED 与 GREEN 日志已经保存。可选 LSP NOT RUN：biome LSP command not found；实际四宿主端到端自动派发、外部 OMP gate 运行 NOT RUN，禁止推断运行时强制预算已实现。

### 已知验收标准与测试接缝
- AC-001：Standard/Critical 交付范围完成且检查通过后一次完整 workflow-reviewer，切片只做检查；不追加 code-reviewer / Matt 原生审核。接缝：delivery review budget bounds rounds rather than only reviewer count；routing reviews the delivery scope once and never adds code-reviewer。
- AC-002：集中修复后最多一次 focused，只查原阻断项、修复 diff 和直接影响；预算用尽或仍有/新增阻断则 blocked，不能 CLEAN。接缝：review procedure and all reviewer adapters distinguish full and focused modes；focused/exhaustion fixtures。
- AC-003：阻断需具体违反合同/不变量和失败影响；可选简化/风格不阻断；跨会话/快照保留预算；仅无有效报告 INVALID 可受控替换一次。接缝：delivery budget 断言及 suggestion/resume/INVALID fixtures。
- AC-004：finish 核对和记录既有证据，不派发、不直接补跑；缺口返回主路由；追加记录不自失效。接缝：finish consumes evidence and returns gaps without scheduling or running checks；workspace review and finish reuse a complete independent result；UI prompt 同步检查。
- AC-005：AC、接口、安全边界、方案或范围扩大导致原覆盖失效，须请求用户决定重新完整审核/拆分，不自行重置。接缝：shared budget 的 user approval 断言及 scope drift fixture。
- AC-006：四 harness 安装一致、模型/工具限制不变、Pi project 使用 .agents/skills 不改旧 .pi/skills、真实记录 RED/GREEN 与 NOT RUN。接缝：现有安装合同与54项 smoke；tracked sources 和 legacy Pi mirror 字节保留证明。

### 设计与审查重点
- quality-profiles.md 是唯一预算源；主路由唯一调度，review-implementation 是过程而非第二个 reviewer，finish 不调度。
- 本次是薄编排层规则优化，不创建执行引擎或状态机模拟测试。静态合同/场景证明文本和安装一致，不证明所有模型必然遵循。
- prior full + focused + affected checks 覆盖最终内容；不能仅凭旧报告批准未经复核的修复。任何有效 FINDINGS 不能改称 INVALID 以重试。
- 输出用中文，将 Standards 和 Spec 分开；每条 finding 标注 severity、Blocking: yes | no、具体路径行号、违反的 AC/不变量、失败场景和最小修复。
- 返回一个 REVIEW_STATUS: CLEAN | FINDINGS | INVALID；CLEAN 意味着有足够证据且没有阻断问题，可保留非阻断建议。你不改实现、不做用户验收、不追加 code-reviewer。

## 外部边界
`D:/my-works/claude-skills/omp-extensions/workflow-review-gate` 是独立仓库；本次不修改或运行其行为验证。安装同步来自它的受管副本不代表其 `Active change` 识别已经修复。
