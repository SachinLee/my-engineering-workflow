# 共享安装方案

## 背景与现状
`scripts/install.ps1:215` 起按 harness 复制技能，Project All 三份，User All 四份。`Sync-SkillDirectory` 当前拒绝 reparse point，不能用旧同步逻辑更新 Claude 链接。doctor 沿用旧路径。Codex / Pi 官方文档及本机 OMP 18.12.6 的 agents discovery 支持用户级 `.agents/skills`；Claude 官方支持 skill 目录 symlink。

## 方案与改动边界
- 保留仓库 `skills/` 为源码；安装器循环一次发布到 `$HOME/.agents/skills`，并装配 `openspec_compat.py`。默认 Scope 改为 User，与共享安装习惯一致；Harness 默认 Both 和其语义保持。
- User / Project 的 harness 适配目录沿用现有逻辑，`PI_CODING_AGENT_DIR` 只影响 Pi / OMP 的适配及旧目录发现，不改变 skills 根。
- Claude 每个 skill 目录使用 Windows junction / 其他平台 SymbolicLink，正确目标幂等保留。
- 所选 harness 的 user 旧路径总被检查；Project 同时检查当前项目入口（包括 Codex / Pi 的 `.agents/skills` 和旧 `.pi/skills`）。只处理六个受管名称。用户级项目级 Claude 旧副本一起迁移，所需入口重建链接，消除遮蔽。
- 旧普通目录移入 `~/.agents/backups/my-engineering-workflow/<unique-run>/`，输出源与备份路径；共享内容发生变化时也先保留旧安装。备份不位于 skills 扫描目录。
- 通过比较完整文件列表和 SHA256 判断共享安装是否已匹配源码及额外 helper；相同则跳过。旧版本与本地修改均可保留，无需引入额外 receipt 系统。

## 公开接口与不变量
公开边界为 `install.ps1` 和 `doctor.py` 命令；测试在临时 HOME / 项目调用实际安装器，不修改真实全局安装。保留 `-WhatIf`、All / Both、路径空格及已有 provider 配置。检查目标、父目录的 reparse point，拒绝未知链接；只有已指向对应共享 skill 的目录链接可作为兼容入口处理。链接操作只移除链接本身，不递归目标。

## 错误处理与兼容性
所有受管路径在写入前预检，未知链接显式报错。备份先于删除/发布；安装失败保留备份并允许用户重跑，不把半完成状态报告为成功。无需对任意项目做全盘扫描，其他项目的项目级旧副本由用户在该项目再执行安装。共享安装会让各项目一起升级，文档明确不再提供 Project skills 版本隔离。

## 诊断
doctor 统一检查 home `.agents/skills` 及 helper；Claude 额外比较入口的解析路径并要求目录链接；所选 harness 的旧入口必须不存在或为正确共享链接。已有适配检查保持，修正受影响的 Pi 警告追加调用以使 All 诊断能运行。

## 发布与回滚
此次只执行隔离安装。真实切换使用 `install.ps1 -Scope User -Harness All`，必要时对既有项目运行 Project All 清理其旧入口。恢复旧副本前先移除对应新链接，仅恢复输出中列明的备份；回滚旧安装器须恢复旧目录布局。Windows / 非 Windows 链接实际验证分别如实记录。

## 验收追溯
AC-001 / AC-002 对应共享发布和适配链接；AC-003 对应预检、备份、幂等及预览；AC-004 对应 doctor；AC-005 对应文档、测试及独立复核。实施在主会话，最终审核为唯一 dispatch。
