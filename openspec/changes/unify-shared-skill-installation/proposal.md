# 统一共享 Skills 安装

## 目标
六个 workflow skills 统一发布到 `~/.agents/skills`，更新一次供 Codex、OMP、Claude Code 和 Pi 使用；各 harness 继续保留必需的适配文件。

## 范围内
- User / Project 均使用用户级共享 skills；Scope 只决定 agents、commands、OMP 配置和扩展的位置。
- Codex、OMP、Pi 原生发现共享目录；Claude 使用逐 skill 的目录链接。
- 迁移所选 harness 的已知旧入口；保留旧内容和本地修改的备份，不触碰其他 skill。
- 安装器、doctor、README、架构说明及测试同步更新；支持重复执行、路径含空格和 `-WhatIf`。

## 范围外
- 修改第三方 harness、Matt/Ponytail 内容、OpenSpec CLI 或其他 change。
- 自动迁移其他项目、修改真实用户全局安装、提交、发布、验收或归档。
- 项目级隔离 skills 版本；本方案明确让同一用户的项目共享安装版本。

## 假设与授权
- 用户已确认统一路径为 `~/.agents/skills`，并确认创建和按上一轮列出的范围直接实施。
- profile: standard；主会话实施，一次独立最终审核。
- 测试接缝沿用已确认的安装器、doctor、契约测试和隔离安装验证；以公开命令的退出码及磁盘产物证明行为。
- 验证使用临时 HOME 和临时项目，真实用户目录的切换留给用户执行安装命令。

## 验收标准
- [ ] AC-001：任何 Harness、User / Project 安装只把六个 skill 的正文、references 和 `openspec_compat.py` 发布到 `~/.agents/skills` 一次；不新增 native skill 正文副本，其他 skill 保持不变。
- [ ] AC-002：Claude 在 Scope 对应目录建立逐 skill 链接；Codex / OMP / Pi 原生使用共享目录；各 harness 的 agent、command、OMP overlay / extension / launcher 和白名单保持有效，Both 仍为 Codex + OMP。
- [ ] AC-003：迁移所选 harness 的已知用户级旧副本及 Project 范围下目标项目旧副本，先备份再移除，保留本地修改；重复执行不重建正确链接或重复备份未变内容；拒绝管理未知链接和链接父目录；`-WhatIf` 不产生写入。
- [ ] AC-004：doctor 检查共享目录和辅助脚本、Claude 链接目标、所选 harness 旧入口遮蔽及适配文件，并准确报告缺失、断链、错误目标和旧正文副本。
- [ ] AC-005：文档说明共享安装/更新命令、Scope 语义、备份恢复、全局版本影响和会话刷新；先 RED 后 GREEN，Node / Python 测试及隔离 All 安装通过，一次独立审核后停在 awaiting-acceptance。
