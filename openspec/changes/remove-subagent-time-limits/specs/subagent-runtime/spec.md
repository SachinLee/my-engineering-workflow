## ADDED Requirements

### Requirement: 子代理执行时限策略

工作流 SHALL 禁止仅因经过时间或无进展时间阈值终止 worker，且 SHALL 不主动添加 call-level runtime deadline。出现疑似停滞时可以请求一次状态更新；显式失败、取消及用户指令仍可终止任务。

#### Scenario: 长时间执行

- **WHEN** worker 的执行时长超过原来的 15 分钟阈值
- **THEN** 主会话继续等待，不能仅因该时长终止 worker

### Requirement: harness 配置与同步

仓库 OMP overlay SHALL 使用 `maxRuntimeMs: 0`。三个 Pi workflow agent SHALL 使用 `timeoutMs: 2147483647`，并明确该值约为 24.9 天的有限平台上限。安装副本 SHALL 保持与仓库管理的源文件一致。

#### Scenario: 同步本机安装

- **WHEN** 安装更新到本机四个 harness
- **THEN** User/Project workflow skill 与源文件一致，OMP overlay 和 Pi workflow agent 的执行时限配置保持一致
