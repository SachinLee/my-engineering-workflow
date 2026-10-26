# 上下文包

实施由主会话顺序完成，不委派 writer；最终审核使用本包。

Active change: openspec/changes/unify-shared-skill-installation/
Assigned slice: review / changed scope
Phase: review

## 已内联结论
- AC-001：六个 skills 及 helper 只发布到用户级 `~/.agents/skills` 一次，其他 skill 保持。
- AC-002：Claude 使用逐 skill 链接，三种原生宿主发现共享目录；适配、Both 语义不变。
- AC-003：已知旧副本备份，正确链接幂等，未知链接及链接父目录拒绝，WhatIf 无写入。
- AC-004：doctor 检查共享 helper、Claude 链接、遮蔽和适配，不把旧正文当作共享成功。
- AC-005：文档、RED/GREEN、全套验证和一次独立审核，awaiting-acceptance。
- 设计：User / Project 均使用用户级共享目录；Scope 只控制适配；不隔离版本。备份在共享 skills 树外；不迁移未指定项目。
- 已定位：scripts/install.ps1:76 Assert-NotReparsePoint 拒绝链接；scripts/install.ps1:215 起四分支重复复制；scripts/doctor.py:219 起使用旧目录；tests/contracts.test.js:485 断言四份 helper，需要改为一份。
- 模式：沿用 SupportsShouldProcess、skillNames、Copy-ManagedFile、OMP 白名单与 review gate；新增测试调用实际 pwsh，临时覆盖 HOME，不访问真实用户安装。
- 保持：skills/ 源码所有权、上游隔离、PI override 适配、角色定义、OpenSpec 记录、不提交不归档。
- 验证：python -m unittest discover -s tests；npm test；兼容边界严格校验。

## 需打开
- openspec/changes/unify-shared-skill-installation/proposal.md — 完整验收标准。
- openspec/changes/unify-shared-skill-installation/specs/shared-skill-installation/spec.md — 增量合同。
- scripts/install.ps1 — 安装 / 备份 / 链接和适配。
- scripts/doctor.py、scripts/doctor.ps1 — 诊断命令。
- tests/test_shared_installation.py、tests/contracts.test.js — 行为与静态合同。
- README.md、ARCHITECTURE.md — 用户接口与版本影响。
- artifacts/verification.md — 执行证据（审核前由主会话补齐）。

## 审核边界
Read-only；不修改生产文件、不做嵌套 dispatch。不读取其他 change、legacy 记录或真实用户凭据。当前 AC 和设计已内联，审核时核对磁盘实现及证据即可。报告 Standards / Spec、正确性、安全、测试、复杂度和 NOT RUN。
