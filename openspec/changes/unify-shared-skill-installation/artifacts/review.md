# 独立审核记录

## 范围与预算
- 角色：workflow-reviewer，独立会话 a6ac1890-2d7b-4d5b-a05a-ccadfc53b9bd。
- full 1 / focused 1；base HEAD，含指定 tracked 工作区 diff 和明确命名 untracked tests/test_shared_installation.py 及本 change。
- tracked：scripts/install.ps1、scripts/doctor.py、scripts/doctor.ps1、tests/contracts.test.js、README.md、ARCHITECTURE.md。
- 未审核无关 openspec/changes/chinese-change-titles/。审核者只读，未修改、提交、归档或嵌套委派。

## Full 结果
REVIEW_STATUS: FINDINGS

| ID | 严重性 | Blocking | 位置 | 合同与场景 | 修复 |
| --- | --- | --- | --- | --- | --- |
| R1 | MEDIUM | yes | scripts/doctor.py:105 | AC-004：PI_CODING_AGENT_DIR=HOME/.agents 或 ProjectPath=HOME 时，legacy root 等于 shared，健康安装被报 Legacy skill entry | resolve legacy roots、去重并排除 shared.resolve() |
| R2 | MEDIUM | yes | scripts/install.ps1:122 | AC-002 / AC-003：PowerShell -eq 忽略大小写，Unix PLAN-SOLUTION 错链被认为指向 plan-solution，跳过未知链接拒绝 | 平台选择 OrdinalIgnoreCase / Ordinal，通过 string.Equals 比较 |

- Standards：未发现额外项目规则违规；canonical skills、上游隔离、无状态注入、Both、provider 配置、用户验收归档所有权保持。
- Spec：AC-001 与共享发布符合；AC-002/003/004 受上述问题影响；AC-005 等待修复审核。
- 数据保护：审核者临时验证未知断开的 junction 与旧目录内嵌套 junction 在发布前拒绝，外部目标保持；先复制备份再移除顺序合理。
- Tests：原 Node 41 / Python 28 / OpenSpec strict 证据有行为证明；缺少路径重合与 Unix 大小写边界。
- Complexity（Ponytail）：未发现不必要依赖或抽象，无其他必要修复。

## Focused 结果
REVIEW_STATUS: CLEAN

- R1 resolved：scripts/doctor.py:105 排除规范化后的共享根；tests/test_shared_installation.py:129、tests/test_shared_installation.py:137 以实际隔离安装覆盖 override 和 HOME 项目两种场景，doctor 返回成功且无误报。
- R2 resolved：scripts/install.ps1:122 采用平台相关比较；tests/test_shared_installation.py:145 在 Windows 直接执行 Unix 比较分支，tests/test_shared_installation.py:162 是真实 Unix 错链/断链集成场景。
- 修复验证：共享安装测试 16 条中 15 PASS / 1 Unix-only SKIP；git diff --check PASS；两项均有先 RED 后 GREEN 记录。
- Standards / Spec：无新增问题，AC-002/003/004 阻断解除，AC-005 审核环节完成。
- Correctness / Security / Tests / Complexity：修复命中根因，未扩大管理范围，无新阻断，无剩余建议。
- 最终覆盖链：原 full + 原 Node 41/41、Python 28/28、OpenSpec strict PASS + 修复后的相关测试 + focused。无剩余阻断，主会话记录 awaiting-acceptance；不是用户验收。

## 限制
NOT RUN：macOS / Linux 实际链接集成、真实用户安装和迁移、四种 harness 新会话发现、Windows PowerShell 5.1。Windows 执行 Unix 比较分支只证明比较语义。harness 可执行发现占位不能证明真实 harness 自动发现。
