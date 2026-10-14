# 执行任务

状态：awaiting-acceptance
质量档位：lightweight

- [x] 1. AC-001 / AC-002：先更新契约测试并确认 RED，再修改 workflow、OMP overlay 和三个 Pi agent；针对性测试 GREEN（6/6）。
- [x] 2. AC-003：执行 `scripts/install.ps1` 的 User/Project `All` 同步，显式关闭本地 OMP 全局 runtime cap，核对源文件与安装副本。
- [x] 3. 运行完整测试、安装诊断及独立审查，记录证据并停在 awaiting-acceptance。

执行边界：主会话负责上述单个本地配置切片；独立 reviewer 只读核对最终改动和证据。
回滚：恢复本切片的源文件后重装；本地 OMP 全局配置恢复原字段状态，保留其余自定义项。
