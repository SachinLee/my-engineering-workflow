# 上下文包

## 切片 1
- AC：specs/project-standards/spec.md 的 AC-001..005 为完整验收条款。
- 已定位：scripts/install.ps1:33 的 skillNames、scripts/doctor.py:20 的 SKILLS 均硬编码六项；OMP includeSkills 白名单需要同步。
- 现有模式：README.md:300 共享安装；.pi/agents/workflow-implementer.md:24 限定 handoff 读取；skills/plan-solution/SKILL.md:118 上下文包范例；skills/review-implementation/SKILL.md:41 审查 handoff。
- 约束：不复制内部项目代码；不写用户模型配置；不增加注入或审查轮次。共享规范优先采用项目版本、范围条件及真实检查。
- 实现与测试：修改范围为本仓库规范、文档、安装脚本、doctor、各代理/命令及契约测试。不改 openspec 其他 change，不操作用户安装目录。
- 定向验证：根据测试组织选取 node --test 的相关文件和 Python 安装测试；完整 npm test 由父会话整合后执行一次。
