# 跨客户端项目规范

## 目标
按用户已批准的设计，提供一份按任务加载的基础、Java 和 Spring/MyBatis-Plus 规范，接入现有 Matt/Ponytail 工作流及 Pi、OpenCode、OMP、Claude、Codex 安装。

## 范围内
- 新增 project-standards skill，按需加载 references，项目约定优先于通用默认值。
- 安装器、doctor、OMP 白名单、代理上下文包与实现/审查读取入口同步。
- 提供项目 AGENTS 入口模板和来源记录；安全处理本地旧 ECC 流程规则。
- 执行仓库检查和本地安装验证；客户端实际模型与行为未观察时记录 UNVERIFIED。

## 范围外
- 不修改 csgops 业务代码、配置或数据库；不复制内部业务内容。
- 不更改用户模型配置，不新增注入 hook 或审查轮次。
- Go/Rust/Python/Vue 详细规范留待后续扩展，本次明确缺省行为。

## 授权与状态
用户已批准上一轮方案并要求开始实施。profile: standard。此变更独立于此前跨客户端工作流变更。完成后 awaiting-acceptance，不自动提交、推送或归档。
