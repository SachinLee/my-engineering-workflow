# 执行任务与审批边界

## 当前状态
- Active change: `limit-delivery-review-rounds`
- 阶段：`awaiting-acceptance`
- 风险级别：`standard`
- 交接时间：`2026-10-14T14:54:50+08:00`。
- 方案审批：`approved`（用户要求执行此前优化方案，并确认新建本 change；包含不追加 `code-reviewer`）
- 实现授权：`approved`
- 当前执行前沿：无待执行实现项；独立审核 `CLEAN`，证据见 `artifacts/review.md` 与 `artifacts/verification.md`，等待用户验收。

## 切片 1：AC-001 / AC-003 / AC-005 - 交付级预算与单审核身份
- 行为：完整审核一次、最多一次定向；恢复/快照不重置；扩大范围需用户授权。
- 代码边界：quality profiles、主路由、治理、命令、README、ARCHITECTURE、`tests/contracts.test.js`、`evals/workflow-cases.json`。
- 测试接缝：上述公开文本及 eval 场景。
- RED：`node --test tests/contracts.test.js`，新增预算断言在旧规则上失败。
- 实现：单源预算，入口只调用主路由；明确默认不追加 `code-reviewer`。
- GREEN：同 RED 命令。
- 依赖：用户已批准此前优化方案。
- 回滚：撤销相对 baseline 的本片增量。
- [x] 1.1 添加预算/身份/停止条件断言与场景并记录 RED。
- [x] 1.2 更新共享预算和入口规则，记录 GREEN。

## 切片 2：AC-002 / AC-004 / AC-006 - 定向复核与证据型收尾
- 行为：完整/定向模式可区分，findings 标注阻断性；finish 只核对和记录证据。
- 代码边界：review/finish 技能、Root/OMP/Pi reviewer 定义、同一合同测试；同步本项目受管技能。
- 测试接缝：技能/代理合同、安装产物内容比对。
- RED：同一 Node 合同命令，新增 finish 禁止补跑和 focused 模式断言失败。
- 实现：仅在主路由集中修复和定向复核，不扩大只读代理工具权限。
- GREEN/验证：`npm test`、`python -m unittest discover -s tests -p 'test_*.py'`、隔离与当前项目 All 安装比对。
- 依赖：切片 1。
- 回滚：撤销本片增量并按源重新安装。
- [x] 2.1 添加 reviewer/finish 断言并记录 RED。
- [x] 2.2 更新技能和三个 reviewer 源定义，记录 GREEN。
- [x] 2.3 完成全套测试、隔离安装验证和本项目安装同步。

## 交付阶段
- [x] 3.1 派发一次完整独立 `workflow-reviewer`，记录报告；若有阻断项只集中修复并最多一次定向复核。
- [x] 3.2 记录逐条 AC、运行限制和用户验证步骤，交接 `awaiting-acceptance`；不接受或归档。
