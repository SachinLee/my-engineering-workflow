## 审核结论

Review mode: focused。前序报告 `artifacts/review-full-result.md` 为 `REVIEW_STATUS: FINDINGS`（F1、F2）。本轮只核对这两项、修复后的直接文本和已记录的合同测试日志，没有改文件，也没有重跑仓库检查。Blocking: no。

### F1 — Fixed

原阻断是当前流程在快速资格判定前创建或读取 `.workflow/`。现文不再这样做；`.workflow/` 只出现在恢复或迁移说明里。

- `README.md:355-356`：安装后先走快速通道，简单任务不建档；`.workflow/` 只作 legacy 恢复输入。
- `README.md:386-388`、`README.md:392-393`、`README.md:397-398`：完整指南先引用 `quality-profiles.md#simple-work-fast-path`；正式分支才做 OpenSpec discovery 和确认；`.workflow/CURRENT.md` 仅用于显式 legacy 恢复或用户要求的迁移。
- `README.md:506-510`：OMP 先分流，简单任务对话交付且不建档。
- `README.md:545-560`：`### 一次正式任务的阶段` 声明合格任务先返回；正式阶段从 OpenSpec discovery 开始，verification 写入该 change。
- `README.md:583-584`、`README.md:597-602`、`README.md:905`：默认顺序和跨会话续接先判快速通道；共享上下文是已选 `openspec/changes/<change-id>/`；旧指针只用于显式恢复。
- `README.md:259-260`：`to-spec` / ticket 产物放在已确认的 OpenSpec change，不写 legacy tasks。
- `README.md:868-869`：快速通道只在对话报告，不创建 `artifacts/verification.md`；只有已选正式 change 才记录。

已核对的旧句（先询问创建 `.workflow/`、先读 `CURRENT.md`、新状态一律写入、按 `.workflow/` 阶段、共享 `.workflow/` 上下文、任务目录由主路由创建、票写到 `.workflow/tasks/`、`AGENTS.md` 和 `.workflow/spec/`）在当前 `README.md` 中均不存在。

### F2 — Fixed

`skills/run-engineering-workflow/SKILL.md:77-86` 的 `## Choose Fast Or Formal` 仍在 discovery 之前。`SKILL.md:89-91` 的 `## Start` 标明 formal-only。`SKILL.md:152-155` 的 `## Assess Profile First` 现为 “Formal branch only, after the fast/formal selection and confirmed change selection.”，下一句是 “Before formal dispatch”，并读取已选 OpenSpec `proposal.md`。该节不再含 “Before any routing”，也不能先于快/正式选择去匹配 proposal。

## Standards

无阻断。当前指南不再把 `.workflow/` 当作新工作状态，符合 `AGENTS.md`。正式确认、TDD、Delivery Review Budget 和中文产物要求没有被这次文本修复放宽：`README.md:833` 仍要求正式 `lightweight` 在 `proposal.md` 保留方案草图；`README.md:553-557` 仍是一次完整复核加最多一次定向复核。

## Spec

- AC-001：满足。档位评估位于快/正式选择和已确认 change 之后，且仅正式分支。
- AC-002：满足。人读流程不再要求为新工作创建 `.workflow/`。
- AC-003：修复段未削弱。快速通道仍报告 diff、检查和未运行项，不回补 verification。
- AC-004：未削弱。正式确认、范围扩大先停止，以及 CLI 失败不伪装成无匹配，都还在。
- AC-005：满足。命令级早返回不在本轮重审范围内；本次 README 流程图已与主路由一致，正式要求仍保留。
- AC-006：不在本轮重开。修复前的全套证据继续覆盖未改输入。

正确性：F1/F2 的失败路径在已审源文本中已消失。安全：无新的权限或持久数据扩大。测试：`tests/contracts.test.js:67-87` 锁住上述旧句，并要求完整指南引用快速通道、`简单任务不建档`、`### 一次正式任务的阶段`、`显式 legacy 恢复`；收尾段须同时出现快速通道不写 verification 和仅正式 change 记录。`tests/contracts.test.js:90-98` 锁住评估节位于 `## Choose Fast Or Formal` 之后、含 “Formal branch only” 与 fast/formal selection、不含 “Before any routing”、仍读取 selected OpenSpec `proposal.md`。RED 日志证明这些断言曾经失败；当前源文本与断言一致。复杂度：只删除冲突说明，没有新抽象。

## 证据与未跑检查

- `artifacts/repair-red.log`：41 tests，39 pass，2 fail（README 旧句与 Assess 节 “Before any routing”）。
- `artifacts/repair-red-remaining-guide.log`：41 tests，40 pass，1 fail（仍有 ticket / `.workflow/spec/` 旧句）。
- `artifacts/repair-green.log` 与 `artifacts/repair-green-final.log`：41 tests，41 pass，0 fail。
- 本审核没有重跑 `node --test`、Python、OpenSpec validate、安装或 `git diff --check`。Python 与安装比对不需要为这次纯文本修复重跑；它们不证明 README/主路由句子，修复前的基线继续有效。
- 四宿主新会话、默认 LSP、全局安装和外部 gate 仍是既有 NOT RUN，不影响本次源文本结论。

## 非阻断

- `.agents/skills/run-engineering-workflow/SKILL.md:154`、`.claude/skills/run-engineering-workflow/SKILL.md:154`、`.omp/skills/run-engineering-workflow/SKILL.md:154` 仍是 “Before any routing or dispatch decision”。设计把旧镜像排除在本 change 之外，合同测试只读 canonical `skills/`。这不是本轮源文本阻断；在重新安装前，不能声称已安装副本与修复后的主路由一致。
- `SKILL.md:52-53` 仍要求派发前解析一个 OpenSpec change id。前次已判定其语义限于派发，快速通道不派发；本修复没有放宽或扩大它。
- 否定断言是精确旧句，不能防止将来换一种措辞再引入 legacy 建档。当前文本没有这种句子。

Reviewed inputs：`artifacts/review-full-result.md`、`artifacts/review.md`、`proposal.md`、`tasks.md`、`design.md`、`specs/simple-work-routing/spec.md`、`README.md` 的安装/完整指南/正式阶段/默认顺序/续接/收尾/冲突段、`skills/run-engineering-workflow/SKILL.md` 的 `## Choose Fast Or Formal` 与 `## Assess Profile First`、`tests/contracts.test.js:67-98`，以及四份 repair 日志。未重做全仓审查。

REVIEW_STATUS: CLEAN