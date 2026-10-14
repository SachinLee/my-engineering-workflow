# 移除子代理执行时间限制

## 目标与范围

用户已明确要求修改仓库并同步本地 harness，不再按执行时间终止子代理。
范围为 workflow 调度规则、OMP runtime cap、三个 Pi workflow agent 及本机 User/Project 安装副本。

## 假设与约束

- OMP 的 `maxRuntimeMs: 0` 关闭执行时限。
- Pi 不接受无限时长；`timeoutMs: 2147483647` 是平台上限，约 24.9 天。
- 保留显式失败、用户取消、权限边界和验证门禁；工具请求时限与 OMP 已完成 agent 的 idle TTL 不属于执行总时限。
- 不修改第三方 harness 源码、凭据或已有运行中进程。

## 验收标准

- [x] AC-001: workflow 不再因时长或无进展时间阈值终止 worker，也不添加 call-level runtime deadline；通过契约测试验证。
- [x] AC-002: 仓库 OMP overlay 为 `maxRuntimeMs: 0`，三个 Pi workflow agent 使用平台最大时限；通过契约测试验证。
- [x] AC-003: 本地 Codex、OMP、Claude、Pi 的 User/Project 安装副本与源文件一致，OMP 全局 runtime cap 为零，Pi 全局默认最大时限保持有效；通过安装和文件比对验证。

## 范围外

远程发布、提交、自动归档，以及声称 Pi 平台时限已真正无限化。
