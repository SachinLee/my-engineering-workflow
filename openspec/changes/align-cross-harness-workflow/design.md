# 技术方案

六个 skills 仍以 skills/ 为唯一源码，发布到 ~/.agents/skills。客户端入口采用原生发现或受管理链接；OpenCode 支持与旧副本迁移由安装器显式管理。代理权限按客户端原生格式发布，模型保持用户配置所有权。Codex 优先共享技能与如实能力声明，避免把旧 Markdown 当作原生运行代理。

执行规则：工作流管理范围、验收、审查及证据；宿主管理调度、模型与工具。OpenCode 中 Slim Orchestrator 调度 explorer/designer/fixer/oracle 和必要的 workflow agents，不增加总控。正式实现使用 Slim `fixer` 角色，独立审查使用 Slim `oracle` 角色，让当前激活 preset 负责选模；不把某个 preset 模型 ID 写死进 workflow agent 模板，也不把直接 agent 继承的主会话模型说成 Slim 角色模型。不可用或路由未验证时报告 `UNVERIFIED`。Ponytail 5 的完整修改与有效检查整合到方法说明。

验证：先补相应合同/安装回归用例并证明失败，再实现；各实施 lane 只运行聚焦检查，主会话汇总后运行完整仓库测试一次。安装先备份已知受管理文件，保留未知文件、模型配置及插件补丁。独立 reviewer 仅审查本次范围一次。实际客户端对话与 UI 测试不能以静态检查替代。

## 复验轮次 3 方案
- AC-007/008：新增共享 specialist-routing reference，主路由按需读取；不复制上游技能。探索不强制正式记录，进入正式实施才要求 active change。Pi 以运行时 schema 为准，options.context=fresh；loader 激活后下一轮重新检查工具，不把 loader 当委派。保留 workflow-reviewer 独立质量合同。
- AC-009/010：以 Codex 当前官方原生格式建立 .codex/agents/*.toml，不写 model/provider；安装仅管理三个 workflow 名称。优先原生目录发现，若当前版本需要注册且无法安全保留配置，则明确限制而非擅写 config。Pi 原生技能入口指向规范共享安装，沿用备份/未知链接保护。doctor 不以静态文件证明实际调用。
- 不变量：现有未提交改动不得回退；不触碰用户模型/插件设置；无注入器、无新状态机；Both 不变；独立角色新上下文不代表跨模型。
- 验证：两条不重叠 writer lane 各自拥有 RED/GREEN；主会话整合后一次 npm test、Python discovery 和 diff 检查。真实 Pi/Codex 最小调用只验证发现/委派/结果回传，不修改业务项目；不可用时如实保留运行限制。独立 reviewer 对本轮增量做一次完整审查。
- 回滚：恢复本轮增量及安装器记录的备份，不删除/覆盖用户未知角色，不回退其他 change 的现有改动。
