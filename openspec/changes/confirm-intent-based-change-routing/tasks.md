# Tasks：会话意图匹配与确认式任务路由

## 切片 1：OpenSpec 产物

- [x] 1.1 写 proposal.md、specs/task-routing 增量、design.md、tasks.md、artifacts/context.md

## 切片 2：兼容模块（测试先行）

- [x] 2.1 tests/test_openspec_compat.py：FAKE_CLI 支持 `new change`；补 list_changes / 单 change 不自动选中 / 多 change 不 BLOCKED / create_change 成功 / 同名冲突 / 非法 id 覆盖（blocked_by: 无）
- [x] 2.2 scripts/openspec_compat.py：新增 `list_changes()`、`create_change()`；`detect_project_mode()` 改为 `change=None` 一律 unselected + available_changes（blocked_by: 2.1）
- [x] 2.3 跑 `python -m unittest tests.test_openspec_compat` 全绿（blocked_by: 2.2）

## 切片 3：诊断与路由文本

- [x] 3.1 scripts/doctor.py：unselected 且有候选时报告候选清单，不再报环境不可用（blocked_by: 2.2）
- [x] 3.2 skills/run-engineering-workflow/SKILL.md：Start 步骤改为意图匹配 + 强制确认（blocked_by: 2.2）
- [x] 3.3 references/workflow-governance.md：路由不变量更新为"推荐 + 确认"；复用保留已有工作（blocked_by: 3.2）
- [x] 3.4 commands/engineering-workflow.md：同步入口行为（blocked_by: 3.2）
- [x] 3.5 tests/contracts.test.js 新增确认契约；evals/workflow-cases.json 增加语义匹配与确认 case（blocked_by: 3.2）

## 切片 4：安装分发

- [x] 4.1 scripts/install.ps1：分发 openspec_compat.py 到各 harness skill 目录（blocked_by: 2.2）
- [x] 4.2 临时目录验证安装后 helper 可执行、doctor 无副作用（blocked_by: 4.1）

## 切片 5：验证与文档

- [x] 5.1 真实 CLI 演练：创建成功 / 同名报错（blocked_by: 2.2）
- [x] 5.2 更新 README.md、ARCHITECTURE.md（blocked_by: 3.2）
- [x] 5.3 写 artifacts/verification.md，停在 awaiting-acceptance（blocked_by: 5.1, 5.2）

## 本轮验收与待修复前沿

- 状态：`awaiting-acceptance`；本轮 `REVIEW_STATUS: CHANGES_REQUIRED`，不能据第 1 轮全 PASS 归档。历史实施勾选保留，不表示本轮验收通过。
- [ ] 6.1 修复无 name / 非有效 name 的候选记录被当作空列表；添加可观察错误结果的回归覆盖（AC-009，blocked_by: 无）。
- [ ] 6.2 修复 create_change 未检查兼容版本与成功响应 root/id；补错误响应不得报告 created 的回归覆盖（blocked_by: 无）。
- [ ] 6.3 在真实主路由完成同义/相关区分、新建/复用建议、拒绝/取消/调整、确认不循环、过期确认与保留工作演练；验证安装 helper 定位与用户验收状态读取，按 AC 记录实际结果（blocked_by: 6.1, 6.2）。
- [ ] 6.4 完成修复后独立复核与复验；未经用户明确接受和归档请求不得归档（blocked_by: 6.3）。

本次用户请求为验收检查；6.1～6.4 是明确的后续修复前沿，尚未执行。具体复现与证据见 `artifacts/verification.md` 的“复验轮次 2”。
