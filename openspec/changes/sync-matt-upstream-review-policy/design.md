# 修改方案设计

## 背景与现状

本次是薄编排层的兼容性修正，不是上游技能移植。规范行为见 `specs/upstream-review-integration/spec.md`；验收定义见 `proposal.md`。

关键证据：

| 位置 | 当前事实 | 设计影响 |
| --- | --- | --- |
| `skills/run-engineering-workflow/SKILL.md:161-164,212-220` | Standard 一名实现或审查 worker；审查二选一；Critical 先 Matt 再最终 reviewer | 统一预算，移除默认原生 Matt 步骤 |
| `skills/run-engineering-workflow/references/quality-profiles.md:21-24` | 双轴与独立复核分开要求 | 该文件成为审查预算的唯一来源 |
| `skills/run-engineering-workflow/references/workflow-governance.md:262-268` | Standard 行为变更和 Critical 要求 fresh-context 最终复核 | 保留独立性，不能用主会话自查解决预算冲突 |
| `skills/finish-with-evidence/SKILL.md:21-35` | 收尾再调用 Matt、独立复核和 Ponytail | 改为验证已有审查记录，不新增审查链 |
| `commands/engineering-workflow.md:25-42` | 无条件规划 dispatch，先 Matt 再 reviewer | 入口服从 profile，不覆盖主路由 |
| `../mattpocock-skills/skills/engineering/code-review/SKILL.md:6-13,23-25,73-93` | 两个并行代理；提交 diff；默认 issue 寻源 | 工作区默认采用本地 reviewer；原生模式显式保留 |
| `.omp/agents/workflow-reviewer.md:8,20-24` | autoload 原生 `code-review`；已经要求完整工作区 | 移除 autoload 的原生技能，保留只读和范围 |
| `agents/workflow-reviewer.md:3`、`.omp/agents/workflow-reviewer.md:3` | 描述仅允许 Critical 或显式审查 | 文案允许质量配置要求的 Standard 审查 |
| `skills/clarify-requirements/SKILL.md:27-28`、`skills/finish-with-evidence/SKILL.md:38-40` | 领域词汇指向旧 `CONTEXT.md` | 术语归属统一，不动任务上下文 |
| `manifests/upstreams.lock.json:3-9` | 旧日期、旧 Matt revision/version_hint | 适配验证后只更新已审阅字段 |
| `scripts/install.ps1:14-15,260-263` | OMP 去重扩展来自兄弟目录 | 禁止修改 `.omp/extensions/` 安装副本 |
| `../omp-extensions/workflow-review-gate/lib/review-gate-core.js:18-19` | 只解析 `Active task:` | 运行时去重缺口明确记录，另立任务处理 |

## 方案与改动边界

### 决策一：合并审查责任，而不是削减检查

复用已有 `workflow-reviewer`，不新建适配器程序或另一个 reviewer。将风险表和审查模式放在现有 `quality-profiles.md`；其余技能与代理通过指针读取同一合同。

| Profile | 默认实现与派发 | 最终审查 | 仓库验证 |
| --- | --- | --- | --- |
| `lightweight` | 主会话，无默认子代理 | 主会话范围检查 | 一项最小相关检查；发现行为改动重新评估 profile |
| `standard` | 主会话；默认唯一 worker 留给最终 review | 一个独立 `workflow-reviewer`，不嵌套 dispatch | RED/GREEN、目标测试和适用 lint/type/build |
| `critical` | 既有 gated 实现路径，始终一个 writer | 一个最终 reviewer；必要专项检查由真实风险触发 | 全相关套件、安全、数据/迁移、回滚、关键路径 E2E |

Standard 若确需实现委派，先说明独立复核如何满足；默认不同时增加实现 worker。需要超过默认预算时由用户显式批准并记录例外，不能降低独立性或伪造 Critical 风险。

Reviewer 在一次结果中分开输出 `Standards` 与 `Spec`，另列正确性、安全、测试、复杂度及证据缺口；保留现有 severity 和 `REVIEW_STATUS: CLEAN|FINDINGS|INVALID`，三个 agent 定义语义统一。Ponytail 是审查方法，不额外增加一名 agent。Root/OMP reviewer 可执行既有只读验证；Pi reviewer 没有 shell 权限，只核对主会话已执行证据并报告缺口。

这里的“一个 reviewer”指同一稳定审查材料的一轮最终复核，不是整个 change 永远只能调用一次。修复 material findings 或实质改变需求/证据后必须重新复核；这不是对同快照的重复叠加。仍沿用现有受控替换与授权边界，不允许以重审名义并行增加 reviewer。

### 决策二：默认完整工作区，原生 Matt 显式调用

工作区模式由主会话提供已选 change、明确文件边界和证据。使用现有 Git 能力，不写通用快照模块：

```text
git rev-parse HEAD
git status --short --untracked-files=all
git diff --cached -- <declared-paths>
git diff -- <declared-paths>
git ls-files --others --exclude-standard -- <declared-paths>
```

`<declared-paths>` 是实际文件数组，不是让执行者照抄的字符串；无初始 commit 的项目显式报告不能解析 HEAD，不悄悄空过。未跟踪内容用只读工具逐文件读取；显式需要的 ignored 测试可单独加入范围，无关文件和凭据不读取。完整相关范围含本次已提交变化时，另外加入批准的 base 到 HEAD diff，不能只审核当前未提交尾部。

Handoff 继续使用现有 `Active change:`、`Assigned slice:`、`Phase:`、`Read:`、`Must preserve:`、`Review scope:`、`Evidence:`，在 scope 中注明工作区或批准的提交范围，在 evidence 中给出 base、相关文件清单、diff、未跟踪内容和执行结果。不新增 required 字段，避免扩展不必要的公共协议。

Matt 原生模式只在用户显式请求时使用其上游合同；确认固定点、非空提交 diff 和适用 Spec 来源。已选 OpenSpec change 的路径应显式提供，不让 issue 或 `.scratch/` 搜索取代它。原生模式本身可能需要 tracker 配置，缺失时如实说明，不自动安装。两个原生子代理的结果不是本地工作区最终 reviewer 的同义词，不能自动消除本地交付缺口。

### 决策三：收尾消费审查结果，不再启动整套审查

`finish-with-evidence` 检查 review 是否针对同 change、同相关代码/需求/支撑证据，且 material findings 已解决；已有有效结果则记录引用。没有有效审查则回到主路由的审查阶段，不在交付技能里私自派代理。

审查快照是已声明的相关文件与需求材料，不是整个仓库所有文件。实现、需求或支撑证据实质改变会使旧结果失效；仅追加审查结果、交付说明或无关文件变动不使审查自身失效，避免“写证据导致永远重审”。沿用一次受控 `INVALID` 替换规则，不新增重试系统。

独立复核不可用时记录 `UNVERIFIED`，停在未完成缺口交接。用户若明确接受例外，需要单独说明授权及风险；不变成普通验证通过。对于未提供结尾状态的 reviewer，统一补齐报告合同，不从空输出推断 CLEAN。

### 决策四：GLOSSARY 管术语，OpenSpec 管需求和任务

- 项目明确约定优先；存在 `GLOSSARY-MAP.md` 时使用指向的上下文词汇表。
- 无现成约定的新项目：首次解决稳定术语后才写 `GLOSSARY.md`。
- 只有旧 `CONTEXT.md`：先读已有术语，写入前确认继续使用旧文件还是人工迁移至新文件；若选择旧目标，向 domain-modeling 明确该项目目标，不同时生成新文件。
- 两者共存且没有清楚分工：询问唯一术语所有者，不自动合并或双写。
- 可复用规范归 `openspec/specs/`，任务设计归 `design.md`，真正适用的架构决策归 ADR。`artifacts/context.md` 保留派发上下文；不把所有学习都塞进词汇表。

共享术语规则放在已有 governance 的 Artifact Ownership 附近；澄清、交付、归档技能仅调整相关指针。这里不创建本仓库的新词汇文件，也不改档案正文。

### 决策五：最小版本更新，不扩展默认技能清单

在本次兼容适配完成后更新 Matt revision/version_hint 和 manifest 实际生成日期。Ponytail、retired_sources、schema、默认候选集合不变。审阅证据保留本 change 的记录，不向 lock 添加自创 schema。锁文件表达已审阅来源，不驱动下载或安装。

## 预期修改文件

| 边界 | 文件 | 修改内容 |
| --- | --- | --- |
| 分级合同 | `skills/run-engineering-workflow/references/quality-profiles.md` | 唯一风险表、审查预算和模式 |
| 共享治理 | `skills/run-engineering-workflow/references/workflow-governance.md` | 模式冲突优先级、术语归属、保持独立性 |
| 路由与审查 | `skills/run-engineering-workflow/SKILL.md`、`skills/review-implementation/SKILL.md` | 引用合同，准确工作区/提交范围和分维度报告 |
| 收尾与术语 | `skills/finish-with-evidence/SKILL.md`、`skills/clarify-requirements/SKILL.md`、`skills/archive-task/SKILL.md` | 消费 review 证据、术语目标指针 |
| 代理 | `agents/workflow-reviewer.md`、`.omp/agents/workflow-reviewer.md`、`.pi/agents/workflow-reviewer.md` | Standard 适用性、同一报告合同、无嵌套派发；OMP 去除原生审查 autoload |
| 入口与说明 | `commands/engineering-workflow.md`、`README.md`、`ARCHITECTURE.md` | 按 profile 引用，不保留“Matt 不派代理”等错误说明 |
| 来源记录 | `manifests/upstreams.lock.json` | Matt 已审阅版本与生成日期 |
| 验证 | `tests/contracts.test.js`、`evals/workflow-cases.json` | 跨入口正反断言与可执行/人工行为场景 |

不预期修改 `scripts/install.ps1`、`scripts/doctor.py`、其他 agent 或配置；安装器已经整目录分发 skill 引用。若隔离安装证明存在真实缺口，先记录差异并请求扩大文件范围。生成目录只经安装器写入，不手编辑。

## 验证与执行顺序

四个主会话切片见 `tasks.md`，可选派发上下文见 `artifacts/context.md`。每片先补准确契约再改规则，避免把测试弱化成保留技能名即可。规则合同使用针对段落和引用的正反断言；不新增运行时策略解析器来满足测试。

行为演练至少包括：三个风险档入口、混合 Git 工作区、空提交 diff、原生显式调用、同快照复用、修复后重审、INVALID、不可用、证据追加不自失效、五类词汇表。可先进行带输入/预期/观察的人工演练；实际模型执行只在平台可用且获得授权后进行，需记录工具调用次数，不把 JSON 用例存在算通过。

未来隔离安装命令：

```text
pwsh -NoProfile -File scripts/install.ps1 -Scope Project -Harness All -ProjectPath <sandbox>
python scripts/doctor.py --scope Project --harness All --project-path <sandbox>
```

Sandbox 先有最小 OpenSpec 配置；完整 doctor 如缺 harness/upstream，则原样记录，不掩盖错误。仅验证生成文件的 smoke 不等于完整运行环境健康。本机 User 安装在用户另行授权后才执行，本次不安装。

## 备选方案与否决理由

- 默认 Matt 双代理后再 reviewer：三层叠加、预算不实，且提交 diff 仍漏工作区，否决。
- 默认主会话自查以实现“二选一”：违背 Standard 行为变更的独立复核要求，否决。
- 修改或复制 Matt 审查正文：违反薄编排与上游所有权约束，否决。
- 新建动态 reviewer selector 或 snapshot service：既有技能和 Git 足够，没有当前需求依据，否决。
- 所有 CONTEXT 自动改名：混淆历史、任务与领域上下文，否决。

## 发布与回滚

设计阶段仅新增当前 change 的文件。实现阶段保留既有未提交修改，逐范围查看 diff；禁止 `git reset --hard`、`git clean` 或整仓回退。按本 change 的实际 patch 单独撤销规则、测试和 lock 更新，不能撤销此前执行时限修改。安装仅在隔离目录先验证；真实用户安装如获授权，先备份受管文件，用现有安装器重装，不触碰无关技能。

## 未决技术风险

- OMP 去重 gate 当前没有消费 `Active change:`。本 change 不改另一仓库的扩展；重复审查限制依赖合同执行及实际派发记录，不能宣传成全 harness 的机器硬门禁。
- Review snapshot 默认用现有材料描述而非新自动哈希服务；并发变更或需求变更时必须重新组装材料。
- 静态断言无法证明模型遵从性；未执行的模型演练和独立复核必须保留缺口。

## 验收追溯

| AC | 设计点 | 切片 |
| --- | --- | --- |
| AC-001 | 决策一、三；单一质量配置 | 1、2 |
| AC-002 | 决策二；完整相关范围和显式原生模式 | 2 |
| AC-003 | 决策三；复用与失效、不伪造结果 | 2 |
| AC-004 | 决策四；术语唯一归属 | 3 |
| AC-005 | 决策五；已审阅来源记录 | 4 |
| AC-006 | 三种 reviewer 与隔离安装 | 2、4 |
| AC-007 | 每片 RED/GREEN、行为演练、边界和回滚 | 1 至 4 |
