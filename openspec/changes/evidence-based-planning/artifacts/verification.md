# 交付验证

## 交付

- 状态：complete；交接：`awaiting-acceptance`。
- 时间：2026-10-08T11:09:12+08:00。
- 行为变化：设计前先判断必要性；拟新增兜底、降级、重试、恢复、兼容分支或扩展点必须有当前需求、适用契约或正确性依据。没有依据不进入方案和任务；未知事实留作风险或针对性澄清，不自动视作生产环境。
- 保留必要的权限、事务、唯一性、并发一致性及其他适用保障。没有新增运行时框架、依赖、配置或强制插件安装。

## 验收标准

下列 PASS 是本次真实模型演练与人工审阅的结果，不是所有未来模型输出的保证。

| 标准 | 结果 | 已观察证据及复验步骤 |
| --- | --- | --- |
| AC-001 开发阶段不扩展恢复需求 | PASS | `planning-before.json` 的 `planning-development-logs` 擅自增加“暂时失败可恢复”验收、持久化重试和补偿扫描任务；`planning-after-complete.json` 同一场景只规划终态日志、联合唯一约束与定向冲突处理，正常/异常出口覆盖，显式排除历史回填、重试队列和补偿扫描。对照两个产物的场景输出。 |
| AC-002 简单化不删除必要保障 | PASS | `planning-after-complete.json` 的 `planning-required-safeguards` 拒绝删除权限校验、事务、幂等约束，说明越权、半完成和重复扣减后果，复用单体数据库保障，不新增分布式恢复。检查该场景输出。 |
| AC-003 未知事实与模板不扩需求 | PASS | `planning-unknown-stage` 先澄清部署阶段、保留数据和真实兼容对象，不提前定迁移/双写；`planning-template-pressure` 沿用现有鉴权、错误处理、开发期交付，明确无兼容迁移义务，不增加监控平台或灰度机制。检查这两个输出。 |
| AC-004 失败处理不伪装成功 | PASS | `planning-error-contract` 拒绝无依据自动重试、空列表或缓存旧结果成功兜底，保持既有 API 错误契约及页面失败反馈；`npm test` 26/26，doctor healthy，OpenSpec strict valid。检查场景输出并执行下方命令。 |

## 实现与设计取舍

- 共享规则：`skills/run-engineering-workflow/references/workflow-governance.md` 的 `Evidence-Based Planning` 是单一规则 owner。
- 调用点：`skills/clarify-requirements/SKILL.md`、`skills/plan-solution/SKILL.md`、`skills/run-engineering-workflow/SKILL.md` 显式读取/执行该规则。
- 契约：`evals/workflow-cases.json` 增加 5 个规划场景及判断标准；删除 `tests/contracts.test.js` 中两个只检查澄清/规划源措辞的测试，没有重钉文本或新增关键词评分器。
- 使用说明：`README.md`；项目安装副本通过现有安装器同步，安装器、agent 定义、quality profile、上游 lock 均未修改。
- 举证只要求拟新增机制的简短依据，不创建额外 checklist 或强制记账产物。模板章节允许省略或注明不适用。
- 与 design.md 的验证细化：日志 fixture 明确既有终态裁决和并发重复通知等价，避免把冲突结果仲裁混入测试；旧规则以修正后的同一请求重跑，初始输入/输出和修正原因保留在 `planning-before.json`。最终演练补齐实际 quality profile，初轮输出仍保留，未覆盖历史证据。

## RED / GREEN 行为证据

- 工具：`completion`，`model="default"`，`max_output_tokens=1800`。实际 provider/model 标识未返回，记为 `NOT CAPTURED`，不声称具体模型或 OMP 的 `@advisor` 已用于规划演练。
- RED：读取修改前真实澄清、规划、共享治理正文；在 `planning-before.json` 保存完整 system、5 个 prompt/output。日志场景将未要求的数据库恢复提升为 AC 与任务，构成实际 scope 扩张。其余 4 个场景基线已有相关正确行为，不制造“全部失败”。
- GREEN：`planning-after.json` 读取安装后的三份规则；`planning-after-complete.json` 再加入实际 quality profile，5 场景均按 AC 人工对照通过。每个产物保留完整 system、prompt、output；最终输入是四份文件，不是完整主路由正文。请求明确 change 已确认，不测试路由创建/复用。
- fixture 是场景定义，不是执行证据；Node 测试也不替代模型行为结果。

### 复跑规划演练

在本仓库及支持 `completion` 的 Eval 环境，先读取 `xd://eval/judge` 文档；然后以保存的 system 和 prompt 原样生成，不把评判规则额外塞入 prompt：

```python
import json
from pathlib import Path
p = Path("openspec/changes/evidence-based-planning/artifacts/planning-after-complete.json")
data = json.loads(p.read_text(encoding="utf-8"))
jobs = [(c["name"], completion(c["prompt"], system=data["system"],
          model=data["model_alias"], max_output_tokens=1800)) for c in data["cases"]]
for name, job in jobs:
    print(name, job.wait())
```

逐项对照上表及 `evals/workflow-cases.json` 中的 `required`/`forbidden`；不要按关键词自动判 PASS。该步骤用于用户复验，本报告没有把这段说明当作额外一次已执行结果。

## 仓库与安装验证

| 已执行命令/场景 | 结果 | 边界 |
| --- | --- | --- |
| `npm test` | PASS，26/26，fail 0 | 仅现有仓库契约；测试数减少来自删除两个源措辞测试。npm 同时报告现有 `sass_binary_site` 配置 warning，未为此修改全局配置。 |
| `pwsh -NoProfile -File scripts/install.ps1 -Scope Project -Harness All -ProjectPath .` | 已执行，安装后的规则实际用于 GREEN；另以下方 API/哈希 smoke 核实副本 | 无 User scope 写入，不修改插件依赖或 OMP 白名单策略。 |
| `python scripts/doctor.py --scope Project --harness All --project-path .` | `Workflow installation is healthy.` | 保留未归档 change 提醒及 `Recommended upstream skill was not found: ponytail-review`；healthy 不等于可选插件已安装。 |
| `openspec validate evidence-based-planning --strict` | `Change 'evidence-based-planning' is valid` | 格式检查，不代替语义演练。 |
| 实际 import 三个安装根的 `run-engineering-workflow/scripts/openspec_compat.py`，调用 `list_changes(project)`，计算四份规则的 SHA-256 对比 | 三根均 `ready`、`change=None`；4/4 规则匹配 canonical | `.agents/skills`（Codex/Pi Project 共用）、`.omp/skills`、`.claude/skills`；细节见 `installation-smoke.json`。没有启动全部 harness UI，未声称完整 harness 集成演练。 |

## 独立复核与简化检查

- 用户已授权独立复核；工具调用 `workflow-reviewer`，新上下文，输出 `REVIEW_STATUS: CLEAN`，无 material findings；复核读取规则、spec 与修改前后规划产物，未运行 build/lint/tests/formatter。
- 复核传入摘要中的历史测试计数存在误差；本报告以原始命令输出 **26/26** 为准，基线语义以保存的 JSON 为准。复核结论不作为命令结果来源。
- 复核的 effective model 和 fallback 元数据 `NOT CAPTURED`，不推断具体 provider 或 `@advisor` 实际解析结果。
- Standards/Spec：按仓库 thin orchestration、canonical ownership、中文 OpenSpec、用户验收以及四条 AC 检查；无上游正文 vendoring、无业务恢复实现、无额外 gate framework。
- 简化检查参考本地 Ponytail review 的删除/推测性功能原则；未安装或调用 `ponytail-review` 插件。没有必要再增加插件依赖，也没有可删的额外运行时机制。

## 未运行与剩余风险

- lint、typecheck、编译构建：`NOT APPLICABLE`，本次改动为 skill/Markdown、JSON fixture 及删除 JS 源措辞测试，无编译目标；现有 `npm test` 已运行。
- 全部 harness 实际交互、User scope 实装及所有模型组合：`NOT RUN`，本次安装验证限 Project All，语义演练限 `default` 抽样。
- 模型行为非确定性。若后续规划再次无依据扩展机制，保留具体输入输出，用相同场景复验并修正规则；不预先新增运行时分类器或重试系统。
- 可选 `ponytail-review` 缺失告警如实保留；本次核心规则不依赖它。
- 规范归属：本 change 的 `specs/evidence-based-planning/spec.md` 与共享治理；未提前合并主 specs 或自动归档。

## 提交与用户验收

- 提交：`NOT COMMITTED`；未推送、未归档、未改动其他 change 的记录。
- 用户验收：待确认，proposal 的用户验收复选框保持未勾选。
- 验证入口：上表四条 AC 对应的已保存场景，及三个可直接运行的仓库/诊断/格式命令。
- 用户验收后若明确要求，可执行 `openspec archive evidence-based-planning`；本轮不执行。
