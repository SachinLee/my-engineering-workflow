# 实施过程证据

## 切片 1：分级预算与入口

- 基线 `npm test`：退出码 0，26/26（`logs/implementation-baseline.log`）。
- RED `npm test`：退出码 1，26 通过、1 失败；新断言失败于 Lightweight 原文没有禁止默认 reviewer（`logs/slice-1-red.log`）。
- GREEN `npm test`：退出码 0，27/27（`logs/slice-1-green.log`）。
- 修改：统一 quality-profiles 预算、主路由、命令、共享独立性约束、README 和 ARCHITECTURE；增加跨入口正反合同断言和三个 eval 场景。

### 人工路径演练（静态推演，不是模型 eval）

| 输入 | 主路由/命令观察 | 默认逻辑审查预算 | 实际代理调用 |
| --- | --- | --- | --- |
| Lightweight 非行为说明改动 | 主会话范围检查和最小 runnable check | 0 | 0，人工阅读 |
| Standard 行为修改且原生检查通过 | 主会话实现，review-implementation 调用一个 workflow-reviewer | 1 独立 reviewer | 0，人工阅读 |
| Critical 安全/数据修改且检查通过 | 增加必要集成/安全/回滚检查后调用同一个最终 reviewer | 1 最终 reviewer | 0，人工阅读 |

收尾入口目前仍有旧的追加审查步骤，按切片 2 修正，不宣称完整流程已完成。这里的数量是合同预算，不是实际执行的模型调用次数。正式模型演练和最终 reviewer 放在切片 4；缺少时记 NOT RUN / UNVERIFIED。

## 切片 2：范围、复用与代理合同

- RED：`npm test` 退出 1，27/28，通过现有 27 项，新断言失败于缺少 Standards 维度（`logs/slice-2-red.log`）。
- GREEN：`npm test` 退出 0，28/28（`logs/slice-2-green.log`）。
- 三种 reviewer 描述和正文一致支持 Standard / Critical；OMP autoload 移除原生 code-review；Pi 只读工具、模型继承和 `timeoutMs: 2147483647` 未改变。
- `workspace-scope-experiment.json`：在任务创建的临时 Git 仓库真实验证提交范围为空，但 staged/unstaged diff 和明确读取的 untracked 测试非空；assert 成功，临时仓库已自动清理。

### 收尾路径静态演练

| 输入 | 逐条阅读收尾规则后观察 | 模型执行 |
| --- | --- | --- |
| 同 change / scope / requirements / checks，已有真实完整独立结果 | 消费原报告，不重复派发 | NOT RUN |
| material findings 修复或审查材料实质改变 | 复验后新审查，不复用旧签字 | NOT RUN |
| INVALID 且 handoff 已修复 | 只允许一次受控 replacement，带 Review retry: invalid | NOT RUN |
| 独立上下文不可用 | UNVERIFIED，缺口交接，不 CLEAN 或正常完成 | NOT RUN |
| 只追加 review/delivery evidence，没有改变审查输入 | 结果不自失效、不重复派发 | NOT RUN |


## 切片 3：词汇归属

- RED `npm test`：退出码 1，28/29；新断言暴露 eval JSON 中 `Review retry: invalid` 被错误建模为 handoff 字段（`logs/slice-3-red.log`）。修正为 `required_behavior` 后重新 GREEN。
- GREEN：`node -e "JSON.parse(...)"` 通过；`npm test` 退出码 0，29/29（`logs/slice-3-green.log`）。
- 五类场景：新项目无词汇文件时惰性创建 `GLOSSARY.md`；已有 `CONTEXT.md` 时保留并先确认；两者共存时询问并遵循 `GLOSSARY-MAP.md`；无稳定术语时不创建；`artifacts/context.md` 始终是 OpenSpec 派发包。均为规则演练，未执行真实用户文件迁移，代理调用 NOT RUN。
- 未创建迁移脚本、空词汇文件或重复词汇来源；历史 `CONTEXT.md` 引用保留为兼容说明。
主路由、命令和 finish 现在遵循同一预算，三档最终审查逻辑次数为 0 / 1 / 1；以上是合同推演，非实际 agent 调用。新增 eval 场景只是输入定义，未把其存在当作模型行为通过。
