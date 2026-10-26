# 设计

## 现状与最小方案
主路由 `Locate Canonical State` 的第一步和命令入口均要求所有请求先发现 change；Lightweight 仅减少审核，没有省记录。规划和收尾又假定已存在 change，README 的使用示例仍有 `.workflow/` 新建措辞。必须同时修正入口和后续触发，不能仅增加一条例外。

以现有 `lightweight` 为风险档位，在 `quality-profiles.md` 增加唯一 `Simple Work Fast Path` 资格与执行合同。它是路由分支，不增加配置文件、状态机或新 profile。主路由只保留引用和执行次序；命令、治理、说明及规划/收尾只引用同一资格源。

## 分支与升级
1. 当前请求先检查项目规则和实际影响，再按共享资格判定；不为判断而调用 OpenSpec。
2. 合格：用一句话说明本次是快速执行及范围；主会话完成局部修改、检查 diff、最小相关验证并报告。无需再次询问建档，不运行正式阶段或制造正式记录。
3. 不合格：进入现有 discovery → 匹配 → 一次确认 → 正式生命周期。既有选定 change 续接保留已有确认；存在无关 change 本身不强制正式模式。
4. 中途扩大：停止进一步实现，保留当前修改和检查，说明升级原因再走正式选择确认；不自动建档，不擅自撤销用户改动。

## 入口职责
- `run-engineering-workflow`：唯一分支判定和调度者；前置快速段必须出现在 `Locate Canonical State` 前。
- `quality-profiles.md`：全部资格、排除、执行/退出条件的唯一来源；正常行为变更仍是 Standard/Critical。
- `workflow-governance.md`：正式模式拥有持久状态；快速模式没有任务状态。原 discovery 与归档规则限定到正式分支。
- `engineering-workflow` 命令、README、ARCHITECTURE：先展示分流，再讲正式生命周期；替换与本分支冲突的旧示例。
- `plan-solution`、`finish-with-evidence`：若主路由已选择快速通道，先返回该路径；不自行降级已选正式 change，不要求创建 artifacts 来满足入口。
- UI prompt：提示先遵循路由分流，不强化“每次记录”。

## 验证接缝与限制
沿用仓库现有 Node 文本合同 seam 和 `evals/workflow-cases.json`，用户已授权先测试后实施该路由边界。切片1断言资格边界、前置顺序及命令/治理/文档引用；切片2断言规划/收尾早返回、最小检查和升级防护。增补快路径、无CLI、严格项目、行为变更、续接、升级和验证失败的静态场景。它们验证安装后技能合同，不构建虚假分类器，也不把 fixture 当作真实宿主执行结果。

相关验证使用 `npm test`、Python unittest、OpenSpec strict validate、现有安装器隔离及本项目 `All` 安装内容比对。只运行一次完整独立 reviewer，若无阻断则直接收尾，若有阻断最多一次 focused。

## 边界与回滚
只改 context 包列出的12个源/测试文件和本 change。用户原有归档移动、旧镜像、全局安装及外部 gate 不在范围。需要回滚时恢复 `artifacts/baseline.json` 对应增量并重新安装受影响项目副本；不恢复整个 HEAD，不删除用户工作。

## 验收追溯
- AC-001/002/004：共享资格、前置分流、正式模式边界与升级。
- AC-003/005：入口早返回、直接验证报告和使用说明。
- AC-006：两切片 RED/GREEN、现有完整检查、安装比对与独立审核。
