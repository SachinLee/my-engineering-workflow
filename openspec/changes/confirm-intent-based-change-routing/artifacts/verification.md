# 交付验证

## 验证轮次 1

| AC | 状态 | 证据 |
|---|---|---|
| AC-001 无同义建议创建 | PASS | `python -m unittest tests.test_openspec_compat.test_create_change_runs_explicit_cli_command`：FAKE_CLI 记录 argv 含 `new change <id> --description --goal --schema --json`；真实 CLI 演练步骤 2 create_change 返回 `created intent-routing`。SKILL.md "Match And Confirm Before Creating Or Reusing" 规定确认前不创建 |
| AC-002 同义建议复用 | PASS | tests/contracts.test.js "routing recommends and requires confirmation before creating or reusing"：SKILL.md 含 `已经存在 XXX 任务，是否复用`；evals case `same-goal-match-proposes-reuse` 禁止 `create a duplicate change` |
| AC-003 单任务不自动选中 | PASS | `test_single_open_spec_change_is_not_auto_selected`：单 change 返回 `unselected` + `available_changes=["alpha"]`，`change=None`；真实 CLI 演练步骤 6 `detect no id: unselected ['intent-routing']` |
| AC-004 多候选用户决定 | PASS | `test_multiple_open_spec_changes_wait_for_user_decision`：多 change 返回 `unselected` + 两个候选；evals case `multi-candidate-user-decides` 禁止按最新/名称顺序/模型偏好执行 |
| AC-005 拒绝/取消/调整不越权 | PASS | SKILL.md 确认规则 "A confirmation authorizes exactly the current proposal, once. Rejecting reuse is not consent to create"；evals case `expired-confirmation-stops` 禁止执行过期确认 |
| AC-006 确认不产生循环 | PASS | SKILL.md "Clarification answers and sub-steps of an already-confirmed request do not re-trigger the loop; a genuinely new request re-runs it" |
| AC-007 候选范围正确 | PASS | SKILL.md 候选范围条款：归档、`.workflow/`、`.trellis/`、其他项目记录不进入复用推荐；未归档说明状态（`detect_project_mode(project, change=<id>)`） |
| AC-008 相关≠同义 | PASS | SKILL.md "Related but different goals are not a match; if the goal is unclear, clarify first"；evals case `related-but-not-same-goal` 禁止把相关 change 当同义推荐 |
| AC-009 错误≠无匹配 | PASS | `test_lists_changes_reports_blocked_environments`：malformed JSON 返回 `blocked` + "invalid JSON" 原因；evals case `environment-error-not-no-match` 禁止把错误当无匹配而建议创建 |
| AC-010 同名不覆盖；过期确认停止 | PASS | `test_create_change_never_overwrites_existing_name`：重复创建抛 `CompatibilityError("Change 'intent-routing' already exists at ...")`，真实 CLI 演练步骤 4 相同；`test_create_change_rejects_invalid_id_before_cli` 非法 id 在 CLI 前拒绝 |
| AC-011 复用保留已有工作 | PASS | SKILL.md 复用条款 "keep its existing work — never clear requirements, execution state, or prior verification evidence when reusing"；`test_explicit_change_reads_status` 复用路径只读状态 |
| AC-012 安装后可用、诊断无副作用 | PASS | 临时项目 `install.ps1 -Harness All -Scope Project` 实装：helper 落地 `.agents/skills`、`.omp/skills`、`.claude/skills` 的 `run-engineering-workflow/scripts/openspec_compat.py`（Pi Project 模式与 Codex 共用 `.agents/skills`，四条 Copy-ManagedFile 目标全部覆盖）；`python <helper> --help` 可执行；真实 CLI 演练步骤 8-9 doctor 只产 warning（列出候选），errors 为空 |

## 全量检查

- `python -m unittest discover -s tests -p "test_*.py"`：16/16 OK（含 discover/create/只读/冲突/诊断新覆盖）
- `node --test tests/contracts.test.js`：28/28 pass（含新契约 "routing recommends and requires confirmation before creating or reusing"）
- `openspec validate confirm-intent-based-change-routing`：valid

## 真实 CLI 临时目录演练（scripts/openspec_compat.py + doctor.py，演练目录已清理）

1. 空项目 `list_changes` → `ready []`
2. `create_change` → `created intent-routing`（真实 `openspec new change` 调用）
3. 创建后 `list_changes` → `['intent-routing']`
4. 同名重复创建 → `CompatibilityError: Change 'intent-routing' already exists at ...`
5. 非法 id `Bad_Id` → CLI 前拒绝
6. `detect_project_mode` 无 id → `unselected ['intent-routing']`（单 change 也不自动选中）
7. 显式 change → `incomplete intent-routing`
8. `check_record_layout` → warning 列出候选 + "nothing is auto-selected"，errors 为空

## 独立复核状态

- 独立 reviewer（fresh context）尚未执行，因此不能声称 `REVIEW_STATUS: CLEAN`；保留为 `UNVERIFIED`。
- 主会话已完成行为覆盖（unittest + Node contracts）、OpenSpec validate、真实 CLI 演练与实装演练；全部 PASS。

## 验收清单

- [ ] 用户检查 OpenSpec change 目录、行为测试与真实 CLI 演练结果。
- [ ] 用户确认"推荐 + 强制确认"的路由语义满足预期（无同义建议创建、同义建议复用、多候选用户决定）。
- [ ] 用户确认后运行归档命令；不得在此之前归档本 change。

## 交付状态

- OpenSpec change handoff：`awaiting-acceptance`。验收与归档归用户；未执行归档、提交或推送。

TASK AS OF THIS ROUND: 全部 AC 已验证 PASS，停在 awaiting-acceptance；独立复核 UNVERIFIED，验收与归档归用户。

## 复验轮次 2：用户请求验收修改内容

本轮是检查，不是用户接受或归档授权。保留第 1 轮历史记录，但本轮纠正“全部 AC 已验证 PASS”的结论。

### 结论

- `REVIEW_STATUS: CHANGES_REQUIRED`。现有回归检查通过，但存在可复现的边界缺陷；语义匹配与多轮确认没有端到端证据，当前不满足全量验收条件。
- 仅更新本 change 的验收证据与修复前沿，未修改实现或测试，未提交、推送或归档。

### 已确认发现

| 严重性 | 位置 | 场景、结果与修复方向 |
|---|---|---|
| HIGH | `scripts/openspec_compat.py:178-181` | CLI 返回合法 JSON，但 `changes=[{}]` 时，缺失 name 的记录被静默过滤；`list_changes()` 返回 `ready` 和空候选，调用方可能把读取故障当作无匹配而推荐新建，违反 AC-009。应拒绝无有效名称的候选记录并报告 blocked。 |
| MEDIUM | `scripts/openspec_compat.py:228-245` | 创建路径未检查版本，未校验响应 root 与 change id。模拟 CLI 返回 `root.path=/different-project`、`change.id=different-id` 时，函数仍报告 `created approved-id`；同一模拟 CLI 的 `--version=1.0.0` 在 discovery 被拒绝，在 create 不被检查。应在创建前执行适用的兼容性校验，成功响应必须对应当前项目和已确认 id；校验响应不能回滚 CLI 已产生的写入。 |
| HIGH | 本文件第 1 轮 AC 表；`tests/contracts.test.js:174-208` | Node 契约新增项只检查源文件短语、函数名和安装路径；eval case 是数据，不是执行记录。它们不能证明同义推荐、拒绝/取消、调整后重确认、确认不循环或过期确认停止。第 1 轮将这些规则存在性标为行为 PASS，证据过度声明。应完成真实路由与多轮确认演练后再判定这些 AC。 |

### 本轮执行证据

- `python -m unittest discover -s tests -p "test_*.py"`：16/16 OK。
- `node --test tests/contracts.test.js`：28/28 pass；其新增路由项是源文本契约，不能视为语义行为演练。
- `openspec validate confirm-intent-based-change-routing`：valid，仅证明 OpenSpec 格式有效。
- 临时 fake CLI 子进程边界演练：`changes=[{}]` → `ready, available_changes=[]`；创建响应 root/id 不符 → `created approved-id`；同一 CLI 的 1.0.0 版本在 discovery → blocked。这些是上述缺陷的可执行证据。
- 临时项目真实运行 `pwsh -NoProfile -File scripts/install.ps1 -Harness All -Scope Project -ProjectPath <tmp>`：exit 0。三个独立 skills root（Codex/Pi Project 共用 `.agents/skills`、OMP `.omp/skills`、Claude `.claude/skills`）的 helper 哈希均与单一源实现一致；逐个 import 后调用 `list_changes(<tmp>)` 均得到 `ready []`。
- 已安装 helper 的真实 OpenSpec 1.14.1 调用：创建 alpha 后目录存在；同名创建报 `already exists`，重复创建前后文件路径与内容哈希完全相同；两个候选时 `change=None, status=unselected`。
- 在新的临时项目完成剩余演练：将 alpha 移入该临时项目的 archive，`list_changes()` 只返回 beta；`check_record_layout()` errors 为空、warning 包含候选与确认提示，诊断前后文件路径与内容哈希完全相同。首次演练因 archive 已由 CLI 创建而中断，后续以 `exist_ok=True` 修正演练脚本完成该场景；不是实现失败。
- 源 helper 的 `python scripts/openspec_compat.py --help`：exit 1，stderr 为 `Import this module from doctor, migration commands, or tests.`。已安装副本与源文件哈希一致。第 1 轮“--help 可执行”不是可用性证据；本轮以真实 import/API 调用替代。
- 所有演练仅操作临时项目，目录已由 TemporaryDirectory 清理；未修改本项目的归档目录或用户全局 harness 配置。

### AC 复验矩阵

`PARTIAL` 表示该 AC 的确定性子路径已执行，但整个 AC 未验证通过。

| AC | 本轮状态 | 已执行证据与剩余缺口 |
|---|---|---|
| AC-001 | UNVERIFIED | 确认后的 create API 已执行；无同义推荐、建议字段与确认前不写入没有真实路由演练。 |
| AC-002 | UNVERIFIED | 未执行不同措辞同一目标的复用会话。 |
| AC-003 | PARTIAL | unittest 证明单候选不自动选择；目标不同时推荐新建未演练。 |
| AC-004 | PARTIAL | 真实两个候选返回 unselected；展示差异、等待用户决定未演练。 |
| AC-005 | UNVERIFIED | 未执行拒绝、取消及调整后的多轮会话。 |
| AC-006 | UNVERIFIED | 未执行确认回答不重新路由、独立请求重新路由的会话。 |
| AC-007 | PARTIAL | 真实 CLI 排除临时 archive；已完成未归档任务状态展示、跨项目路由会话未演练。 |
| AC-008 | UNVERIFIED | 未执行关键词相近但目标不同的真实推荐会话。 |
| AC-009 | FAIL | 缺失 name 的候选记录被报告为无候选；现有 malformed JSON 字符串测试没有覆盖该边界。 |
| AC-010 | PARTIAL | 真实同名创建失败且文件不变；过期确认停止未演练。 |
| AC-011 | UNVERIFIED | 显式状态读取 unittest 通过，但完整复用会话保留已有工作与验收门未演练。 |
| AC-012 | PARTIAL | Project All 安装副本 import/API 与诊断无副作用已证明；未启动各 harness 的实际主路由，User scope 未实装。 |

### 独立复核及剩余风险

- fresh-context `workflow-reviewer` 已调用，返回 `REVIEW_STATUS: CLEAN`，但将第 1 轮规则/fixture 证据当作执行证据，没有逐项提供可复现支持。主会话随后执行的边界演练直接反证其结论，因此不采用该 CLEAN 作为本轮最终状态。
- 主路由 `skills/run-engineering-workflow/SKILL.md:78-85,105-124` 只读发现输出仅有候选名称，需在真实演练核实会读取候选 proposal/specs/验证状态，再做同义判断；不能只根据 id 判断目标或以 CLI isComplete 代替用户验收状态。
- 安装后的 helper 是 import-only 模块，目标项目根目录没有 `scripts/openspec_compat.py`；实际 harness 应从已安装 skill 的 scripts 目录加载。真实路由演练需证明该路径定位，不应依靠开发仓库绝对路径。
- 当前仍待修复与复验，验收清单不勾选；用户未确认接受，不能归档。
