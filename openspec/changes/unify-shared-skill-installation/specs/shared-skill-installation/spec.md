## ADDED Requirements

### Requirement: 单一用户级 Skills 安装
安装器 SHALL 对 User 和 Project 范围都使用 `~/.agents/skills`，六个 skills 及其辅助脚本只发布一次。Scope SHALL 仅决定各 harness 适配文件的位置；Both SHALL 保持 Codex + OMP。

#### Scenario: 四种 harness 共用安装内容
- **WHEN** 用户执行 `install.ps1 -Scope User -Harness All` 或 Project All
- **THEN** 六个 skill 存于用户级共享目录，Claude 的入口链接到对应共享 skill，其他 harness 使用原生发现，适配文件按 Scope 安装

#### Scenario: 更新与预览
- **WHEN** 用户重复执行安装，或使用 `-WhatIf`
- **THEN** 未变化内容和正确链接不产生重复迁移，预览不写磁盘，辅助脚本随共享 skill 更新

### Requirement: 保留已有内容并消除旧入口
安装器 MUST 先备份再移除所选 harness 在已知旧目录的 workflow skill 内容；Project 范围还应处理当前项目的旧入口。不得覆盖其他 skills，未知链接或链接父目录 MUST 显式失败。备份位于不被 harness 自动发现的 `~/.agents/backups/my-engineering-workflow`。

#### Scenario: 旧副本有本地修改
- **WHEN** 用户首次运行新版安装器，旧 skill 包含自定义文件或修改
- **THEN** 完整内容保留到输出的备份目录，旧入口不再遮蔽共享版本，非 workflow skill 保持原样

#### Scenario: 旧路径是未知链接
- **WHEN** 入口或其受管父路径指向未授权目录
- **THEN** 安装失败并报告具体路径，不遍历、修改或删除链接目标

### Requirement: 共享安装诊断
Doctor SHALL 验证共享 skills、辅助脚本、Claude 链接解析目标和所选 harness 的适配文件，并报告已知旧入口的遮蔽。不得把旧独立正文副本或错误链接当作健康共享安装。

#### Scenario: 文件存在但 Claude 指向旧版本
- **WHEN** Claude skill 是普通目录、断链或链接至其他目录
- **THEN** doctor 返回非零并输出对应错误
