# 验证记录

## 当前状态

状态：awaiting-acceptance。实现、本地安装及独立审查已完成；尚未验收、提交、推送或归档。

## 已执行证据

- 实现代理记录初始 RED：Node 缺少 project-standards SKILL.md；Python doctor.SKILLS 缺少 project-standards。随后定向 GREEN；父会话检查了正文与 MyBatis-Plus reference。
- 父会话 `npm test`：53 tests，53 pass，0 fail。
- 父会话 `python -m unittest tests.test_shared_installation`：29 tests，116.662s，OK，skipped=1。
- 父会话 `git diff --check`：exit 0；仅提示 Windows 换行转换，无空白错误。
- `./scripts/install.ps1 -Scope User -Harness All`：PASS，七个共享 skill 已安装；OMP 白名单增加 project-standards；变更前受管文件自动备份到用户目录 `.agents/backups/my-engineering-workflow/fd3e792018f0459eb48ec88d65f67eb8`。
- `python scripts/doctor.py --scope User --harness OpenCode`：PASS，`Workflow installation is healthy.`
- 同一 Python doctor 分别检查 Pi、OMP：均 PASS。Pi 提示保留用户 agentOverrides。
- `./scripts/doctor.ps1 -Scope User -Harness All`：exit 1，`ERROR: claude was not found on PATH.`；不能记为整体 PASS。
- doctor 同时报告 Claude Opus/Sonnet 别名都解析为 es-claude/claude-sonnet-5-5，Pi 用户 agentOverrides 保留；本次未修改模型配置。
- 宿主已发现新增 project-standards skill。发现并不证明真实任务中已正确应用；Pi/Claude/Codex/OMP 实际子代理读取和 OpenCode fixer/oracle 实际模型执行仍为 UNVERIFIED。

## 旧 ECC 规则处理

九个现存 `.claude/rules` 文件与当前 ECC 上游均非字节相同，不据此覆盖内容。全部先备份到用户目录 `.agents/backups/project-standards/20261027-150959`，附 SHA256 清单。

逐项读过 agents.md 与 development-workflow.md：其中强制 planner/tdd-guide/code-reviewer、多视角拆分、额外文档和 80% 覆盖率与已批准共享流程冲突。在验证备份哈希一致后，仅将这两个活动文件移到同一备份目录的 `.disabled` 文件。其余七个旧规则保留，未整目录覆盖。恢复可从该目录复制对应原始 `.md` 回 `.claude/rules`。

## 边界

未修改 csgops、数据库或用户业务工程；未执行真实 SQL。引用 SQL 语义的业务修改仍需项目数据库证据。Go/Rust/Python/Vue 详细规则不在本阶段，沿用目标仓库约定。

## 审查过程

首次派发没有形成有效完整审查，返回 INVALID（要求显式完整 diff 和文件清单）。父会话已生成 review-input.txt，包含 HEAD 到工作区的完整受管 diff、文件清单以及批准的新 skill/test 内容；按共享预算进行一次 `Review retry: invalid`，由同一审查上下文完成。不能把 INVALID 当作通过。

重试报告为 CLEAN，Standards/Spec 无阻塞发现，完整报告见 review-full.md。唯一非阻塞 F-001 是字符串列名常量不保证编译期校验，主会话已区分 lambda 属性引用与数据库列名验证。修正后 `node --test tests/project-standards.test.js` PASS（1/1）；All 安装再次 PASS，OMP 白名单无重复，修订 skill 已同步。该文案修正由主会话验证，未声称经过额外独立复核。
