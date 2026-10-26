# 交付验证

## 交付
- 状态：complete（awaiting-acceptance，2026-10-26T11:59:47+08:00）
- 概述：六个 workflow skills 统一发布到 `~/.agents/skills`，Claude 使用链接，旧副本先备份再清理，适配按 Scope 保留。

## 验收标准
| 标准 | 结果 | 证据 |
| --- | --- | --- |
| AC-001 | PASS | test_all_installs_one_shared_copy_with_adapters_and_is_idempotent；test_default_scope_is_user_and_both_preserves_codex_plus_omp |
| AC-002 | PASS | All / Project 产物、Claude resolve、适配文件、PI override 与 Both 测试 |
| AC-003 | PASS | test_project_migrates_old_user_and_project_copies_with_local_edits；test_shared_local_edits_are_backed_up_on_update；WhatIf、未知链接和 adapter parent 预检测试 |
| AC-004 | PASS | doctor 健康 / 遮蔽 / helper 缺失 / Claude 副本 / 错链 / 断链 / junction 测试，以及真实 gate 的 Project All doctor CLI |
| AC-005 | PASS | README / ARCHITECTURE 已更新；Node / Python / OpenSpec 检查及修复后相关测试通过；独立 full 1 + focused 1，REVIEW_STATUS: CLEAN |

## 实现
- scripts/install.ps1：一次共享发布，内容哈希幂等，备份、全入口预检、Claude 链接、适配保留；Scope 默认 User。
- scripts/doctor.py / doctor.ps1：共享路径、helper、Claude 链接和旧入口检查；默认 User；修正 Pi 可选扩展警告异常。
- tests/test_shared_installation.py：16 个测试，15 PASS / 1 Unix-only SKIP；实际 pwsh 和临时 HOME / 项目验证公开行为，补充 Unix 比较分支回归；tests/contracts.test.js 更新固定旧路径断言。
- README.md / ARCHITECTURE.md：安装更新、Scope、备份恢复、会话刷新及版本共享影响。
- 偏差：无新增依赖；Windows junction 诊断采用 lstat 属性，避免依赖 Python 3.12 才有的 Path.is_junction。
- 工作区存在无关未跟踪 openspec/changes/chinese-change-titles/，未读取或修改，不在审核范围内。

## TDD 证据
- 初始 RED：`python -m unittest discover -s tests -p test_shared_installation.py`，旧安装器缺失共享 SKILL.md，FileNotFoundError。
- doctor RED：相同命令，Claude 普通副本错误返回 healthy；Pi 无扩展时 `TypeError: list.append() takes exactly one argument (2 given)`。
- 预检 RED：test_linked_adapter_parent_is_rejected_before_any_publication，发布之后才拒绝 adapter 链接父目录；修复为发布前预检。
- junction RED：test_doctor_recognizes_windows_junction_without_new_pathlib_api，旧实现依赖 is_symlink / is_junction；改为 lstat 之后通过。
- WhatIf 最初观察到 AppData；单独 `pwsh -NoProfile -Command 'exit 0'` 证明为 PowerShell 自身缓存，测试先建立宿主基线再断言安装器无写入。
- GREEN：Python 全套 28 / 28，其中共享安装 12 条通过，无 skip。

## 验证
- `npm test`：PASS，41 / 41。
- `python -m unittest discover -s tests`：PASS，28 / 28；Windows，PowerShell 7，Python 3.14。
- tests/test_shared_installation.py 的 doctor CLI：临时 Project All，实际 sibling gate 复制到临时源码，执行 gate Node 合同；仅 harness 可执行发现使用临时占位命令，不启动真实 harness。
- OpenSpec 通过 scripts/openspec_compat.py 的 _executable / _check_version / _run 边界执行 `validate unify-shared-skill-installation --strict`：PASS，1.14.1。
- `git --no-pager diff --check`：初次发现一处尾部空格，已修复；复验 PASS，仅换行转换提示。

## 独立复核
- profile：standard；full 1 / focused 1；独立 workflow-reviewer 会话 a6ac1890-2d7b-4d5b-a05a-ccadfc53b9bd。full 发现 R1/R2，focused 确认两项 resolved、无新增阻断；最终 REVIEW_STATUS: CLEAN。摘要见 artifacts/review.md。
- Standards 无额外问题；Spec AC-002/003/004 受 R1/R2 阻断：R1 doctor 未排除共享目录自身，R2 非 Windows 链接判定忽略大小写。正确性/数据保护/测试/复杂度均覆盖；full 审核另用临时目录确认未知断链及目录内嵌套 junction 在发布前拒绝，外部目标保持。
- R1 最小复现：PI_CODING_AGENT_DIR=HOME/.agents，Pi 安装成功但 doctor 把六个共享 skill 报为 Legacy skill entry；ProjectPath=HOME 同类问题。修复为规范化 legacy roots 后排除 shared.resolve()。
- R2 场景：Unix Claude 链接指向 PLAN-SOLUTION，正确目录为 plan-solution，PowerShell -eq 会误认为相同。修复为 Windows OrdinalIgnoreCase / 非 Windows Ordinal。
- 审核范围：本任务六个 tracked 修改、tests/test_shared_installation.py 和本 change artifacts；base HEAD，staged / unstaged / 明确命名 untracked。

## 审核修复验证
- R1 RED：`python -m unittest discover -s tests -p test_shared_installation.py -k does_not_report_shared`，两条测试均失败，doctor 把共享目录自身报告为旧副本。
- R2 RED：`python -m unittest discover -s tests -p test_shared_installation.py -k unix_link_comparison`，实际 PowerShell Unix 比较分支将大小写不同的链接当作正确链接，退出码 1。
- 修复 GREEN：`python -m unittest discover -s tests -p test_shared_installation.py`，16 条中 15 PASS、1 SKIP（Unix 文件系统集成需要非 Windows）；Windows 上直接执行相同 Unix 比较函数的测试 PASS。
- 最终覆盖链：原 Node 41 / Python 28 全套证据 + 两项局部修复后的完整共享安装测试 + 同一独立 reviewer focused CLEAN。未重复无关检查。

## 用户环境执行
- 用户后续明确要求执行脚本；已执行 `pwsh -NoProfile -File ./scripts/install.ps1 -Scope User -Harness All`，成功安装六个共享 skills 及四种 harness 适配。
- Claude / Codex / OMP / Pi 共 24 个旧 skill 副本已备份至 `~/.agents/backups/my-engineering-workflow/7c3ec305697349a19673024797fdc320/`。
- 首次 `pwsh -NoProfile -File ./scripts/doctor.ps1 -Scope User -Harness All` 返回 1，唯一错误 `ERROR: claude was not found on PATH.`；检查确认 `~/.local/bin/claude.exe` 存在。
- 仅在子进程 PATH 前置 `~/.local/bin` 后重跑同一 doctor 命令，返回 0，`Workflow installation is healthy.`；未修改持久 PATH。
- 本次为 User 安装，未迁移任何项目级旧副本，未启动四种 harness 验证新会话发现；不代表用户验收或归档。

## 提交
- NOT COMMITTED

## 剩余风险
- NOT RUN：Codex / Claude / OMP / Pi 新会话自动发现验收，macOS / Linux symlink 实机测试，Windows PowerShell 5.1 实机安装。真实用户安装 / 迁移已按用户后续指令执行，见下。
- 用户级共享升级影响所有项目；未指定项目及祖先项目中的旧副本不自动迁移。
- `PI_CODING_AGENT_DIR` 同时影响 Pi / OMP 是既有语义；两者指向同一目录时同名 agents 的覆盖是原有行为，未扩展此任务处理。
- 非 Windows 分支按现有跨平台 PowerShell 约定保留，未宣称实机验证。

## 验收
- 状态：awaiting-acceptance，2026-10-26T11:59:47+08:00；尚未用户验收或归档。
- AC-001 / AC-002：运行 `./scripts/install.ps1 -Scope User -Harness All`，确认六个 skill 仅在 `~/.agents/skills`，Claude 入口指向对应共享目录；重启 harness / Pi `/reload` 验证发现。
- AC-003：先用相同命令加 `-WhatIf` 预览；实际迁移后按 `Backup:` 输出确认旧内容保留，重跑不产生未变化内容的重复备份。已有项目旧副本另执行 `./scripts/install.ps1 -Scope Project -Harness All -ProjectPath <实际项目路径>`。
- AC-004：对应运行 `./scripts/doctor.ps1 -Scope User -Harness All` 或 Project 参数，确认共享安装、链接、旧遮蔽及适配诊断。
- AC-005：阅读 README 安装章节及本验证记录；可复现 `npm test`、`python -m unittest discover -s tests`。未运行项和跨平台限制见剩余风险。
- 验收通过并明确要求后，主会话可使用 archive-task 归档；本次不执行。
