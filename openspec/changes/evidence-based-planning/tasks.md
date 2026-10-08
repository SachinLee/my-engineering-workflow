# 执行计划

- 状态：awaiting-acceptance
- 交接时间：2026-10-08T11:09:12+08:00
- 档位：standard
- writer：main
- frontier：实现与验证完成；等待用户验收，无剩余实施切片
- 任务创建：用户已明确确认；本请求授权按此前分析实施。验收与归档仍属用户。

### 切片 1：AC-001 至 AC-004 — 先建立行为契约

- [x] 将 5 个实际规划场景及判断标准加入现有 eval fixture。
- [x] 删除规划/澄清两个源措辞测试，不重钉文本。
- [x] RED：加载修改前真实 skill，演练相同场景并如实记录通过或缺口。
- 行为接缝：模型对既定请求产出的澄清/方案，不是文件关键词。
- 代码边界：`evals/workflow-cases.json`、`tests/contracts.test.js`。
- 依赖：已确认 change。

### 切片 2：AC-001 至 AC-004 — 收紧规划边界

- [x] 更新共享治理、澄清、规划及路由读取说明。
- [x] GREEN：相同场景加载新规则，人工对照契约审阅结果。
- 验证：`npm test`；实际运行安装器与 doctor；`openspec validate evidence-based-planning --strict`。
- 代码边界：4 个现有 skill/治理文件；无 agent、安装逻辑或上游改动。
- 依赖：切片 1。

### 切片 3：AC-001 至 AC-004 — 独立复核与交付

- [x] 通过现有安装器同步项目副本，更新 README 使用说明。
- [x] 独立上下文复核全部 AC、规划输出与必要保障边界，修复 material findings。
- [x] 写事实验证证据，状态置为 `awaiting-acceptance`。
- 依赖：切片 2；不归档、不提交、不改变其他 change。
