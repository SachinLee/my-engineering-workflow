# 技术方案

六个 skills 仍以 skills/ 为唯一源码，发布到 ~/.agents/skills。客户端入口采用原生发现或受管理链接；OpenCode 支持与旧副本迁移由安装器显式管理。代理权限按客户端原生格式发布，模型保持用户配置所有权。Codex 优先共享技能与如实能力声明，避免把旧 Markdown 当作原生运行代理。

执行规则：工作流管理范围、验收、审查及证据；宿主管理调度、模型与工具。OpenCode 中 Slim Orchestrator 调度 explorer/designer/fixer/oracle 和必要的 workflow agents，不增加总控。正式实现使用 Slim `fixer` 角色，独立审查使用 Slim `oracle` 角色，让当前激活 preset 负责选模；不把某个 preset 模型 ID 写死进 workflow agent 模板，也不把直接 agent 继承的主会话模型说成 Slim 角色模型。不可用或路由未验证时报告 `UNVERIFIED`。Ponytail 5 的完整修改与有效检查整合到方法说明。

验证：先补相应合同/安装回归用例并证明失败，再实现；各实施 lane 只运行聚焦检查，主会话汇总后运行完整仓库测试一次。安装先备份已知受管理文件，保留未知文件、模型配置及插件补丁。独立 reviewer 仅审查本次范围一次。实际客户端对话与 UI 测试不能以静态检查替代。
