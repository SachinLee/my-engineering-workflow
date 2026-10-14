# 验证证据

状态：awaiting-acceptance

## 已执行检查

- RED：先修改契约测试；目标六个测试中三个失败，分别覆盖原有时间终止规则、缺失 OMP 显式无限时限和缺失 Pi agent 最大时限。
- GREEN：`node --test --test-name-pattern='router selects|OMP.*|Pi adapter' tests/contracts.test.js`，6/6 PASS。
- `npm test`：26/26 PASS。
- `scripts/install.ps1 -Scope User -Harness All`：PASS。
- `scripts/install.ps1 -Scope Project -Harness All -ProjectPath <repo>`：PASS。
- `python scripts/doctor.py --scope User --harness All`：PASS，Workflow installation is healthy。
- `python scripts/doctor.py --scope Project --harness All --project-path <repo>`：PASS，Workflow installation is healthy。
- 安装后 SHA256/字节比对：七个 skill 根目录全部管理源文件、两个 OMP overlay、三个 Pi agent，共 103 项 PASS；结果见 `installation-smoke.json`。
- 本机 OMP `task.maxRuntimeMs: 0`、Pi 默认 `timeoutMs: 2147483647`、Pi `httpIdleTimeoutMs: 0`：PASS。
- `git diff --check`：PASS。
- `openspec validate remove-subagent-time-limits --json`：PASS，valid=true，issues=[]。

## 验收追溯

- [x] AC-001：时间终止与 call-level deadline 契约测试 PASS；所有安装 skill 与源文件一致。
- [x] AC-002：OMP 零时限、三个 Pi 最大时限契约测试 PASS。
- [x] AC-003：User/Project installer、安装诊断、103 项文件比对及本机 runtime 配置断言 PASS。

## 验证边界

没有启动新的计费 subagent 长时间运行，也没有重启现有客户端。这里只证明规则、平台文档/实现语义及安装配置，不能证明当前会话已重新加载。Pi 仍有约 24.9 天的平台上限；调用方显式传递的超时参数及供应商请求限制仍可能终止执行。

Project doctor 提示本项目未找到可选上游 skill `ponytail-review`，并提示存在三个未归档 change；这两项不阻塞安装健康检查，也不属于本切片执行时限变更。

## 独立审查

`review_runtime_limits` 在独立上下文返回 `REVIEW_STATUS: CLEAN`，无 CRITICAL / HIGH / MEDIUM / LOW findings。reviewer 独立重跑目标测试 6/6 和完整测试 26/26，并重新核对 103 项安装文件一致。验收和归档仍由用户决定。
