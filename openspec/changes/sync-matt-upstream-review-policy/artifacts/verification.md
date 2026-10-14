# 交付验证

## 交付状态

- Active change: `sync-matt-upstream-review-policy`
- 状态：`complete`；交接阶段：`awaiting-acceptance`。
- 方案审批与实现授权：`approved`（用户明确“开始实施”）。用户验收：待确认；归档：未执行。
- 记录时间：`2026-10-12T03:19:30+00:00`。
- 实施任务：`13/13`。源规则、回归、安装分发、受限模型判断演练和独立复核已完成。验证范围包含下述明确限制，不能读成全 harness 端到端认证。
- 提交：`NOT COMMITTED`；未推送、未修改已归档记录或 legacy 状态。

## 实现

- `quality-profiles.md` 集中定义预算：Lightweight 主会话检查，Standard 一个独立 reviewer，Critical 增加必要验证并沿用一个最终 reviewer。主路由、命令和交付入口使用同一合同。
- 一个 `workflow-reviewer` 分开报告 Standards / Spec，同时检查正确性、安全、测试、复杂度和证据；OMP 不再自动加载 Matt 原生 `code-review`，禁止嵌套派发。
- 默认范围覆盖相关 committed、staged、unstaged 和显式列出的 untracked 内容；选定 change 的 proposal/specs 是需求来源。敏感及无关文件排除。原生 Matt 模式仅显式请求，不能证明未提交内容已审查。
- 收尾复用同 change、同材料、同需求和检查的有效独立报告。实质修复后复验并重新审查；仅追加交付或审查记录不自失效。`INVALID` 只允许一次受控 replacement，缺少独立性保留 `UNVERIFIED`。
- 新项目稳定术语使用 `GLOSSARY.md`；旧 `CONTEXT.md` 写前确认，不自动迁移或双写。`artifacts/context.md` 仍为 OpenSpec 上下文包。
- Matt 锁定为 `49dd158d1076134a641b33efb035946536778336` / `1.3.1`，`generated_at: 2026-10-12`。Ponytail、retired sources 和默认候选集合不变。
- 仓库自身 `Project / All` 副本经现有 `scripts/install.ps1` 生成，最终 dry-run 和刷新日志见 `logs/project-refresh-dry-run.log`、`logs/project-refresh.log`。后续用户请求本地使用时，已执行 `User / All` 安装；详见下方本机同步记录。

## 验收标准与复现入口

以下 PASS 指本 change 的规则、交付与所列验证范围；不包含未执行的运行时路径。

| AC | 结果 | 实际证据与复现入口 |
| --- | --- | --- |
| AC-001 | PASS | `npm test` 跨入口预算断言；`behavior-inputs.json`、`behavior-output.json`、`behavior-assessment.json` 的 lightweight/standard/critical 判断；最终独立报告。实际演练上下文 1、内部派发 0，0/1/1 是输出的计划预算，不是假称实际运行三个 reviewer。 |
| AC-002 | PASS | `workspace-scope-experiment.json` 真实 Git 混合工作区实验；模型 mixed_workspace 与 native_explicit 判断；相关完整工作区由最终独立 reviewer 审查。原生双代理实际运行 NOT RUN。 |
| AC-003 | PASS | 模型 reuse/append/remediation/invalid_first/invalid_second/unavailable 输出符合合同；真实首轮 findings 修复后重新独立 review，并在收尾复用 CLEAN 报告。受限演练不执行模拟动作。 |
| AC-004 | PASS | `npm test` 术语归属合同；五类人工文件场景见 `implementation-evidence.md`，模型验证 new_glossary/legacy_context/both_vocabularies/no_stable_term。旧项目无迁移，未创建空词汇表。 |
| AC-005 | PASS | `npm test` 锁字段及无关来源断言；源 revision/version 核对；`manifests/upstreams.lock.json`。 |
| AC-006 | PASS | source agent 合同断言；真实隔离 `Project / All` 安装；`installation-smoke.json` 的 56 对文件哈希全部匹配，覆盖技能、共享 references、三个代理角色及 Claude commands；各 harness 实际派发 NOT RUN。 |
| AC-007 | PASS | 各切片 RED/GREEN 日志、完整 Node/Python/启动器检查、模型实际输入输出和次数、最终独立 CLEAN 报告、189 文件基线对比；未执行项如实列出。 |

## TDD 与回归

工作目录：`D:/my-works/claude-skills/my-engineering-workflow`。

- 切片 1 RED：26 通过、1 失败；GREEN：27/27。
- 切片 2 RED：27 通过、1 失败；GREEN：28/28。
- 切片 3 RED：28 通过、1 失败；GREEN：29/29。首个失败暴露 eval marker 字段不合合同，修正后完成术语合同验证；不把它虚称为旧术语规则的唯一失败点。
- 切片 4 RED：上游精确锁字段断言失败；GREEN：29/29。
- 日志：`logs/slice-{1,2,3,4}-{red,green}.log`；过程说明：`implementation-evidence.md`。

| 命令或实验 | 结果 |
| --- | --- |
| `npm test` | PASS，29/29；最终 reviewer 也独立执行通过 |
| `python -m unittest discover -s tests -p 'test_*.py'` | PASS，16/16 |
| `python scripts/test_start_omp.py` | PASS，4/4；不是实际 OMP agent 启动 |
| `openspec validate sync-matt-upstream-review-policy --strict` | PASS |
| `git diff --check` | PASS；LF/CRLF 提示不影响检查 |
| 临时 Git 混合工作区实验 | PASS；空 committed diff 不掩盖 staged/unstaged/显式 untracked 内容 |
| 隔离 `Project / All` dry-run 与实际安装 | PASS；完整哈希 56 对，missing=0、mismatched=0；临时目录已清理 |
| 隔离 `doctor.py` | BLOCKED (environment)，exit 1：sandbox 缺少 ponytail-review，PATH 缺少 claude；另有无 durable records 的提示 |
| 基线保存与产物同步 | PASS；189 文件中 16 个源变化、23 个安装产物变化并匹配源、150 个未变、0 缺失；见 `reviewed-material.json` |

npm 有既有 `Unknown user config "sass_binary_site"` 提示，未改本机配置。

隔离安装 argv、退出码、源到产物 SHA-256 和日志位置完整保存于 `installation-smoke.json`。仓库自身 Project 安装的修改不再声称为“仅 sandbox 安装”；用户级安装后续已更新，见本机同步记录。

## 模型判断演练

- 输入：`behavior-inputs.json` 的 15 场景。
- 独立模型上下文：`del_mv4o8lkr_la1o`；输出：`behavior-output.json`。延迟进程通知记录 exit `SIGTERM`；结果 JSON 与保存的 15 场景输出完全一致，仅使用完整输出作为判断演练证据，不宣称子进程正常退出。
- 主会话按 proposal/specs 核对：15/15 符合判断合同，见 `behavior-assessment.json`。评估者是实现主会话，不能冒称独立 evaluator 或跨模型评估。
- 实际 exercise 子上下文 1，exercise 内部代理派发 0。输出中的 planned_reviewers 是模拟计划；没有执行模拟的审查、安装或词汇写入。
- 这证明一次受限模型决策输出，不能证明各 harness 运行时自动去重、长期一致性或端到端行为。

## 独立复核

- 首轮 `del_mv4nl42p_mt52` 留下有效 findings 报告后以 SIGTERM 结束；该报告不作为最终通过。保留 `initial-review-findings.md` 供追溯。
- 已修复：版本日期、当前 change 的过期状态、README 的额外 Ponytail 默认审查暗示；补齐隔离安装、真实判断演练和证据范围。首轮报告中的未完成项目逐项补齐或明确标为 NOT RUN。
- 修复后独立只读 reviewer：`del_mv4nw63p_yozv`。结论：`REVIEW_STATUS: CLEAN`，未发现 material 实现问题。完整报告：`independent-review.md`，含 Standards / Spec、检查与残余风险。延迟进程通知记录 exit `SIGTERM`；结果文件与已保存报告逐字节一致且包含上述完整结论，因此仅将报告作为复核证据，不宣称子进程正常退出。
- reviewer 与实现使用独立上下文，不宣称不同模型。受管源在报告后未实质变化；`reviewed-material.json` 的源哈希一致。后续仅追加和校正文档证据及安装生成副本，不重复派发 reviewer。

## 未运行、风险和升级触发条件

- 各 harness 的真实代理派发、原生 Matt 两代理实际执行：`NOT RUN`。需要在目标 harness 使用一个实际 change，分别验证风险档、复用/失效和 explicit native 模式；当前只证明安装分发与一次受限判断演练。
- `../omp-extensions/workflow-review-gate/lib/review-gate-core.js:18-19` 仍解析 `Active task:`，不能保证 `Active change:` 路径运行时去重。共享规则已明确此边界；需要另立跨仓 change 修复，不在本 change 偷改扩展或其安装副本。
- 完整 sandbox doctor 为环境阻塞。具备 ponytail-review 和 claude executable 后再运行该健康检查，不能用文件哈希替代。
- 本机 User 范围已刷新；当前运行会话不保证重新读取磁盘技能，重启目标 harness 后使用新版。其他项目已有 Project 副本需按该项目范围单独同步。
- 规则是提示词合同，存在模型非确定性；一次 15 场景演练不能证明所有后续会话都会遵守。

## 本机同步记录（后续请求）

- 用户要求本地 harness 使用修改后的工作流，已执行现有安装器 `pwsh -NoProfile -File scripts/install.ps1 -Scope User -Harness All`。先 dry-run，备份 39 个既有受管目标后正式安装；退出码 `0`。
- Codex：`C:/Users/shuan/.codex/skills`；OMP：`C:/Users/shuan/.omp/agent`；Claude：`C:/Users/shuan/.claude`；Pi：`C:/Users/shuan/.pi/agent`。
- 安装后 SHA-256：Codex 15、OMP 25、Claude 20、Pi 18，共 78 个源到产物文件均一致，缺失和不匹配为 0。包含六个技能、共享 references、compat 脚本、配套代理及安装器管理的命令/OMP 文件。没有真实启动四个 harness。
- 备份和安装校验：`C:/Users/shuan/.pi/agent/backups/workflow-user-20261012-113105/manifest.json`、同目录 `installation-verification.json`。
- OMP 白名单已包含六个技能，本次无需改配置白名单。源规则未变化，用户验收和归档状态不变。

## 用户验收

状态：`awaiting-acceptance`，尚未接受或归档。用户可按上方 AC 表检查规则、报告与命令结果。确认接受后，如明确要求归档，再由 `archive-task` 执行；当前没有触发归档或 journal 写入。
