# 验证证据

## 实施范围

本轮完成了 OpenSpec canonical 路由、legacy `.workflow` 恢复边界、Trellis 只读边界、迁移适配器、四平台安装/诊断入口、agent/skill 文档、行为 fixture 与合同测试更新。

新任务记录归属 `openspec/changes/<change-id>/`；旧 `.workflow/` 仅用于恢复或显式迁移，`.trellis/` 只读且不执行脚本。未执行 OpenSpec archive，等待用户验收。

## 验证命令与结果

- `openspec status --change openspec-compatibility --json`：PASS；proposal、specs、design、tasks 均为 `done`，规划产物完整。
- `openspec validate openspec-compatibility --json`：PASS；1 个 change 通过，0 个 issue。
- `node --test tests/contracts.test.js`：PASS；27 tests passed，0 failed。
- `python -m unittest discover -s tests -p 'test_*.py'`：PASS；9 tests passed。
- `python scripts/test_start_omp.py`：PASS；4 tests passed。
- `python -m py_compile scripts/openspec_compat.py scripts/migrate_workflow_task.py scripts/doctor.py`：PASS。
- `git diff --check`：PASS；仅报告 Windows 工作树的 CRLF 转换提示，无 whitespace error。

## 修正记录

最终合同测试首次收尾时发现 README 断言仍要求旧的 `.workflow/tasks/<task>/context.md` 路径。已将合同改为检查 `openspec/changes/<change-id>/` canonical 路由，并重跑合同测试通过。

曾尝试执行 `python tests/test_start_omp.py`，该路径不存在；按上下文清单更正为 `python scripts/test_start_omp.py` 后通过。该失败是命令路径错误，不是实现失败。

## 复核与剩余风险

- 当前变更尚未由独立 reviewer 在新上下文完成最终复核；这是交付前仍需保留的风险。
- 真实外部目标项目的 OpenSpec CLI 初始化/迁移演练未在本仓库内执行；本轮覆盖的是 fake executable/temporary root 单测和本仓库 change 校验。
- 未执行归档、提交或推送；这些动作均等待用户验收或明确指令。

## 追加验证

- `python scripts/doctor.py --scope Project --harness All --project-path .`：PASS；报告 `Workflow installation is healthy.`，同时给出既有环境提示 `Recommended upstream skill was not found: ponytail-review`。该提示不影响本仓库 OpenSpec 路由测试，但表示完整 Ponytail review 能力未安装。
- `openspec instructions apply --change openspec-compatibility --json`：PASS；10/10 implementation tasks complete，状态为 `all_done`。

## 独立复核状态

- 独立 reviewer 两次在规定时间内超时，输出为空；因此不能声称 `REVIEW_STATUS: CLEAN`。
- 主会话已完成静态 diff、OpenSpec validate、Node/Python/OMP/compile/doctor 检查；独立 fresh-context review 保留为 `UNVERIFIED`，等待用户决定是否补装 `ponytail-review` 或再次运行独立审查。

## 验收清单

- [ ] 用户检查 OpenSpec change 目录与合同测试结果。
- [ ] 用户确认旧 `.workflow`/`.trellis` 兼容边界满足预期。
- [ ] 用户确认后再运行 `openspec archive openspec-compatibility`，不得在此之前归档。
