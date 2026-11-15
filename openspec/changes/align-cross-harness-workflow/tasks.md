# 执行清单

用户授权：本会话明确要求按前述分析更新本地安装及工作流，覆盖本方案和可逆安装操作。

- [x] 切片 A：安装器/doctor 支持 OpenCode、Claude/OMP 漂移检测及旧副本迁移；F-001/F-002 已修复并回归通过。
- [x] 切片 B：共享规则、轻量边界、Slim 协作说明、合同测试（AC-002、AC-003）。
- [x] 主会话：审核上游并更新锁定记录、同步本地 Matt/Ponytail/工作流、完整验证（AC-005）。
- [x] 一次独立完整审查，结果见 artifacts/review-full.md。
- [x] 修复阻断问题，补充完整差异证据，执行唯一一次修复后聚焦复核；审查 CLEAN。
- [x] 第一轮证据已记录；当时状态 awaiting-acceptance（2026-10-27）。归档及 journal 由用户验收后决定。
- [x] 复验轮次 2：OpenCode 适配已明确正式实现走 Slim `fixer`、独立审查走 Slim `oracle`，并加入静态合同回归（tests/contracts.test.js、evals/workflow-cases.json）；静态回归、完整检查、差异证据及 focused review 已完成，状态回到 awaiting-acceptance。实际角色调度仍属运行时未验证项。

## 复验轮次 3 执行前沿
- [x] 切片 C / AC-007、AC-008：共享按需专长路由和 Pi/Codex 调用规则；契约测试 RED→GREEN；见本轮 focused test 证据。
- [x] 切片 D / AC-009、AC-010：Codex 原生角色、Pi skill 入口、安装诊断；临时 home 隔离测试 RED→GREEN；实际安装及烟测证据见 artifacts/verification.md。
- [x] 主会话：依赖 C/D，核对产物、更新 README/ARCHITECTURE、最终完整检查、安装及真实最小运行验证。Pi output 参数通路真实通过；Codex 正常结束与完整回传仍 UNVERIFIED。
- [x] 本轮唯一独立完整审查及必要聚焦复核，记录证据并停在 awaiting-acceptance；focused CLEAN，未提交/推送/归档。
- [x] full review F-004/F-005 修复与负向回归；最终 Node 64/64，Python 共 86 项、2 skipped；同一 reviewer 唯一 focused 确认两项 resolved，无剩余 blocking findings。
