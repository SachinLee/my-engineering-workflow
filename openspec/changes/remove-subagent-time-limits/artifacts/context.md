# 上下文包

Active change: openspec/changes/remove-subagent-time-limits/
Assigned slice: review / changed scope
Phase: review

## 已内联结论

- 用户要求：仓库也修改，然后同步其他 harness；不希望限制执行时间。
- AC-001：取消经过时间或无进展时间阈值终止及 call-level runtime deadline。
- AC-002：OMP `maxRuntimeMs: 0`；三个 Pi workflow agent `timeoutMs: 2147483647`。
- AC-003：四个本地 harness 的 User/Project 文件与仓库一致；OMP 全局 runtime cap 为零，Pi 默认最大时限保持有效。
- 原规则：workflow 在 10 分钟无进展时查询状态，15 分钟时终止；原测试在 `tests/contracts.test.js` 强制保留该规则。
- 本机 OMP 源码 `src/task/settings.ts` 定义零表示 Unlimited，`src/task/executor.ts` 仅在 `maxRuntimeMs > 0` 时设置终止计时器。
- 本机 Pi `pi-subagents/docs/configuration.md` 说明 `timeoutMs` 必须是 1 到 `2147483647` 的整数；不能宣称真正无限。
- OMP idle TTL 只暂存已完成的 idle agent，不是执行中任务时限；保持既有 request budget 和验证门禁。
- 使用既有 `scripts/install.ps1`；不新增安装选项或修改第三方源码。
- 工作树里既有 evidence-based-planning 归档搬动和安装副本未跟踪状态，不属于本次修改。

Read: proposal.md、specs/subagent-runtime/spec.md、tasks.md、artifacts/verification.md。
Review scope: `skills/run-engineering-workflow/SKILL.md`、`config/omp-workflow.yml`、`.pi/agents/workflow-*.md`、`tests/contracts.test.js`，以及本切片安装证据。
Must preserve: 权限边界、显式取消、失败处理、并发规则、required verification、用户配置和已有工作树改动。
Evidence: RED 时目标六个测试中三个失败；GREEN 为六个通过。完整测试及安装验证见 verification.md。
