# 设计

采用共享 skill + 按需 references + 项目入口 + 有界 handoff。正文发布到 ~/.agents/skills/project-standards；客户端仅管理既有链接和代理入口。主路由在代码修改/审查前选取适用规范，在上下文包中内联已判断的条目；必要新读取给出绝对路径。缺少可读取规范时报告缺口，不假称已加载。

基础/Java/MyBatis-Plus 为本次交付，其他语言使用项目工具和约定。规范不新增模型选择、调度系统、全局覆盖率或独立审查轮次。已有六个 workflow skill 的计数说明需同步，正文治理保持单一来源。项目模板只陈述可验证事实，示例采用泛化名称。

来源为已审阅 ECC 25278e7d7b6cf6e6a4e7a6c8e10f14ff22f0eb5b 的相关语言规则和 MyBatis-Plus 官方文档；保留改编部分许可与来源。csgops 仅用于验证习惯的适配性，不复制源码和内部标识。

验证顺序：先契约 RED，再实现与定向 GREEN，父会话执行完整 npm test、diff 检查与所有客户端安装 doctor，最后一次独立审查。真实客户端试运行若未执行，明确 UNVERIFIED。
