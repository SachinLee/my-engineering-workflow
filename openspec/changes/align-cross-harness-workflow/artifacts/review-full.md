# 完整审查

- 模式：full；REVIEW_STATUS: FINDINGS。
- 独立上下文：workflow-reviewer，session `ses_e847ac7abffe56FqOiNMD1SuBP`。
- 前一次仅因缺少 `Review mode` 返回 INVALID，按规则受控替换；未消耗有效实现审查轮次。

## Spec
- F-001 / MEDIUM / Blocking：`scripts/doctor.py` 的 Claude、OMP 检查未调用受管内容漂移比较；需覆盖 OMP 三代理、Claude 三代理和两命令，对应 User/Project 根。
- F-002 / MEDIUM / Blocking：OpenCode Project 旧入口检测漏掉项目 `.agents/skills`；应与安装器保持一致。
- AC-002、AC-003 规则与目标一致；AC-001、AC-004 上述缺口阻断。AC-005 有记录证据支持，未重新执行。

## Standards、安全与复杂度
- 无另列阻断规范或安全问题；模型所有权、只读 reviewer、单审查预算与用户验收权保留。
- 安装器先备份后删除、批量预检、未知链接拒绝、幂等性有实现与测试支持。
- 非阻断：All CLI 集成测试 stub 漏掉 `opencode`，应补齐以消除环境依赖。

## 证据限制
- reviewer 未执行命令，消费父会话检查记录。
- 初次完整审查缺少 Git 工具及完整 diff/status 附件，对完整差异覆盖标为 UNVERIFIED。父会话补充 `workspace.diff` / `workspace-status.txt`，聚焦复核须核对该边界后才能完成。
- 原始规则 RED 输出 NOT CAPTURED；真实跨客户端模型对话 NOT RUN。
