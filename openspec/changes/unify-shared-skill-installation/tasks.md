# 实施任务

- 状态：awaiting-acceptance
- 更新时间：2026-10-26T11:59:47+08:00
- profile：standard
- 授权：用户在确认“创建并按上述范围直接实施”的问题后回复“创建”；按已确认边界执行，无需再次审批相同方案。
- 执行前沿：等待用户验收；writer: main；独立审核 full 1 / focused 1，REVIEW_STATUS: CLEAN，R1/R2 resolved。

### 切片 1：AC-001 / AC-002 / AC-003 — 共享发布和迁移
- [x] 1.1 在安装器公开命令边界新增隔离 HOME 的 All / Project / 幂等 / 迁移 / WhatIf 测试，捕获 RED。
- [x] 1.2 实现一次共享发布、Claude 链接、旧副本备份和路径保护，保留适配行为。
- 行为：所有 scopes / harnesses 共用用户级 skills，旧正文退出发现路径。
- 代码边界：scripts/install.ps1、tests/test_shared_installation.py、tests/contracts.test.js。
- RED / GREEN：`python -m unittest discover -s tests -p test_shared_installation.py`。
- 验证：隔离 HOME / 项目、正确链接重跑、空间路径、旧修改备份和未知链接拒绝。
- 依赖：无；回滚：还原本片源码，安装产物从输出备份恢复。

### 切片 2：AC-004 — 共享诊断
- [x] 2.1 新增 doctor 行为测试捕获 RED，再调整路径和链接/遮蔽检查。
- 行为：旧副本、错链、断链、缺失 helper 有明确非零诊断。
- 代码边界：scripts/doctor.py、scripts/doctor.ps1、tests/test_shared_installation.py。
- RED / GREEN：同切片 1；验证同时覆盖适配目录和 PI_CODING_AGENT_DIR。
- 依赖：切片 1；回滚：还原 doctor。

### 切片 3：AC-005 — 文档及交付
- [x] 3.1 更新 README / ARCHITECTURE、合同断言，执行 Node / Python 全套和 OpenSpec 校验。
- [x] 3.2 一次独立 workflow-reviewer full 审核；有阻断时集中修复并最多一次 focused 复核。
- [x] 3.3 消费验证与审核证据，更新 artifacts/verification.md，停在 awaiting-acceptance。
- 代码边界：README.md、ARCHITECTURE.md、tests/contracts.test.js、本 change artifacts。
- 验证：`npm test`；`python -m unittest discover -s tests`；通过兼容边界运行本 change 严格校验。
- 依赖：切片 1、2；回滚：还原本次文档，不删除验证记录。
