# 执行计划

- Active change: `allow-simple-work-without-change`
- 阶段：`in_progress`
- 风险档位：`standard`
- 创建与实施授权：用户本轮明确选择“先覆盖非行为性小改动”及“创建并实施”。
- 当前执行前沿：完整审核 + 一次定向复核均完成（full FINDINGS → 修复 → focused CLEAN），实现、验证与审核完成，等待验收；不归档。
- 审核预算：一次 full + 一次 focused 已消耗，轮次证据由 `artifacts/review.md` 持有。

## 切片1：AC-001 / AC-002 / AC-004 / AC-005 - 前置快速分流
- 行为：资格先于 discovery；合格工作免记录，不合格及显式正式请求保留旧合同。
- 边界：主路由、共享质量/治理、命令、README、ARCHITECTURE、router UI prompt、tests/evals。
- 测试接缝：公开安装内容的文本合同与静态路由场景；不是宿主E2E。
- RED：`node --test tests/contracts.test.js`，资格/前置顺序的新断言在旧规则上失败。
- GREEN：同命令；保留现有全部审核和确认约束。
- 依赖：已批准范围；无外部依赖。
- 回滚：只撤本次对应文件增量，参考baseline，不恢复整个用户工作区。
- [x] 1.1 补路由边界测试与静态场景，保留RED。
- [x] 1.2 落地共享资格、主路由和说明入口，保留GREEN。

## 切片2：AC-003 / AC-004 / AC-005 - 规划及收尾不反向强制建档
- 行为：消费主路由快速选择，直接返回主会话验证与报告；扩大范围先停再升级。
- 边界：plan-solution、finish-with-evidence及UI prompt、tests/evals；必要的共享资格澄清。
- 测试接缝：入口早返回与快/正式分支隔离。
- RED / GREEN：`node --test tests/contracts.test.js`。
- 验证：`npm test`、Python unittest、OpenSpec strict validate、隔离和本项目All安装比对。
- 依赖：切片1。
- 回滚：撤该片增量，不移除正式模式的原有验证和审核规则。
- [x] 2.1 补后续入口合同断言并保留RED。
- [x] 2.2 实现入口守卫、对话收尾和升级防护，保留GREEN及相关全套验证。

## 交付：AC-006
- [x] 3.1 一次完整独立workflow-reviewer；有阻断才修复并最多一次定向复核。
- [x] 3.2 逐条AC和剩余风险记录验证，交接awaiting-acceptance，不提交、不归档。

## 状态：awaiting-acceptance

- 实现与验证：12 源 + 合同/evals 完成；Node 41/41、基线 Node 39/39、Python 16/16、OpenSpec strict、安装 54 项通过。
- 审核：full 第1轮 FINDINGS（F1 README 旧指南 legacy 建档、F2 Assess Profile First 先于快/正式分流）→ 修复 + 回归断言 → focused 第2轮 CLEAN。
- 剩余风险：四宿主新会话端到端、默认 LSP（biome 不可用）、全局安装与外部 gate 行为 NOT RUN；静态合同不证明运行时分类。
- 待用户：验收通过后明确要求，才归档（不自动归档、不推送）。
