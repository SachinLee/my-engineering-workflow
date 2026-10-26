# 上下文清单

本任务进入实现前，必须按切片读取下列文件。这里的清单只描述真实需要读取的文件，不代替切片上下文包。

## 项目规则与事实源

- `AGENTS.md`：仓库硬约束，尤其是 OpenSpec canonical、`.workflow` legacy、`.trellis` 只读和 acceptance/archival 边界。
- `ARCHITECTURE.md`：现有分层、路由、跨客户端和不变量，避免把 OpenSpec 适配做成第二套并行编排系统。
- `README.md`：用户可见安装、入口、任务阶段和兼容说明，需要同步更新。
- `.workflow/tasks/10-06-openspec-compatibility/prd.md`：本次改造的 AC、范围、非目标和兼容决策。
- `.workflow/tasks/10-06-openspec-compatibility/design.md`：OpenSpec canonical 结构、状态映射、路由和迁移设计。
- `.workflow/tasks/10-06-openspec-compatibility/implement.md`：当前切片的执行边界、上下文包和验证命令。

## 路由与治理

- `skills/run-engineering-workflow/SKILL.md`：修改主路由，使新任务走 OpenSpec，保留 legacy 恢复分支。
- `skills/run-engineering-workflow/references/workflow-governance.md`：核对事实源、任务所有权、迁移、验收和归档约束。
- `skills/run-engineering-workflow/references/quality-profiles.md`：确认 critical/standard/lightweight 仍覆盖 OpenSpec 新路径。
- `commands/engineering-workflow.md`：更新用户入口和恢复语义。
- `commands/archive-task.md`：决定旧命令是否变成 OpenSpec archive 的兼容包装。

## 质量能力与 agents

- `skills/clarify-requirements/SKILL.md`：把需求澄清结果写入 OpenSpec proposal/spec，而不是新的 `.workflow/prd.md`。
- `skills/plan-solution/SKILL.md`：把 design/tasks/context 写入 change。
- `skills/review-implementation/SKILL.md`：复核 OpenSpec change 和代码的一致性。
- `skills/finish-with-evidence/SKILL.md`：把结果写入 verification.md 并停在 awaiting-acceptance。
- `skills/archive-task/SKILL.md`：只在用户明确验收后调用 OpenSpec archive。
- `agents/workflow-planner.md`：规划 agent 的 change 边界和上下文包输入。
- `agents/workflow-implementer.md`：实现 agent 的 tasks、文件边界和 TDD 输入。
- `agents/workflow-reviewer.md`：独立 review 的只读边界和证据输入。
- `skills/*/agents/openai.yaml`：确认安装/触发元数据没有残留 `.workflow` canonical 假设。

## 安装、诊断与 OMP

- `scripts/install.ps1`：四平台受管文件和 Harness/Scope 分支。
- `scripts/doctor.py`：Node/OpenSpec/项目初始化检查和诊断结果。
- `scripts/doctor.ps1`：Windows 包装和参数转发。
- `scripts/start-omp.py`：OMP 启动和项目路径边界。
- `config/omp-workflow.yml`：OMP skill 白名单和 role 映射。
- `scripts/test_start_omp.py`：OMP 启动回归。

## 测试、评估与外部契约

- `tests/contracts.test.js`：安装器、路由、legacy 只读和迁移合同测试。
- `package.json`：Node 测试命令和最低运行时约定。
- `evals/workflow-cases.json`：新增 OpenSpec canonical、legacy resume、explicit migration、blocked 和 Trellis read-only 场景。
- OpenSpec 官方 `docs/cli.md`：CLI 和 JSON 输出契约。
- OpenSpec 官方 `docs/opsx.md`：OPSX artifact 生命周期和命令关系。
- OpenSpec 官方 `docs/supported-tools.md`：Codex、Claude Code、OMP、Pi 的适配命令。

## 旧记录 fixture

- `.workflow/CURRENT.md`、`.workflow/by-session/`、`.workflow/tasks/`：仅在存在旧项目记录时读取，用来验证 legacy 恢复和显式迁移。
- `.trellis/tasks/`：仅在存在旧 Trellis 项目时读取同名产物；禁止执行 `.trellis/scripts/`。
