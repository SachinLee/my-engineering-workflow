# 验证记录

## 安装与回归

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| 隔离安装 | `PASS` | 无同级 gate 源码时，`OMP`、`Both` 和 `All` 均可安装。`-WhatIf` 未在安装目标写入文件，重复安装后文件内容不变，升级保留已有 gate。 |
| 静态诊断 | `PASS` | doctor 在可选组件缺失时通过静态检查并报告派发 `UNVERIFIED`。白名单缺项时报告技能名和配置路径。诊断沿用现有块状白名单格式。 |
| Python 回归 | `PASS` | `python -m unittest tests.test_shared_installation tests.test_openspec_compat` 共 93 项，92 项通过，1 项因需要区分大小写的 Unix 文件系统跳过。集成结束后复跑受影响的 4 项安装与诊断测试，全部通过。 |
| 仓库合同与启动器 | `PASS` | `npm test` 64 项通过，`python scripts/test_start_omp.py` 4 项通过。仓库内旧 gate 的 14 项单独测试通过。 |
| OpenSpec 校验 | `PASS` | `openspec validate repair-cross-harness-runtime --strict` 通过。 |

## OMP 运行探针

使用 `omp/19.0.0`，将 OMP 适配装入临时项目，使用隔离的安装目录。会话沿用本机模型角色配置，禁用扩展，默认入口探针不传 `--config`。

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| 技能发现 | `PASS` | 普通入口实际读取 `.agents/skills/run-engineering-workflow/SKILL.md` 与 `.agents/skills/project-standards/SKILL.md`。 |
| 只读探查 | `PASS` | 两个原生 `scout` 在 `@smol` 下分别返回实现与测试覆盖信息。 |
| 有界实现 | `PASS` | 原生 `task` 在 `@task` 下仅修改允许的 `calc.py`。`python -B -m unittest -v` 先因两条断言失败退出 `1`，修改后两条测试通过，退出 `0`。项目快照只记录到 `calc.py` 的变更。 |
| `prewalk` | `PASS` | 同一临时项目的有效配置为 `prewalk.enabled: false`、`prewalk.auto: off`，`task.agentPrewalk` 无覆盖。实现派发日志记录 `modelRole: task`。 |
| 本机默认 `@advisor` | `UNVERIFIED` | `workflow-reviewer` 被任务截止时间取消，未返回 `REVIEW_STATUS`。 |
| 临时覆盖 `@advisor` | `PASS` | 只在隔离探针中将 `@advisor` 指向可用模型。OMP 从临时项目加载 `workflow-reviewer` 并返回 `REVIEW_STATUS: CLEAN`，探针未修改项目文件。 |

有界实现优先使用原生 `task` 的条件由路由保留，包括关闭 `prewalk`、约束写入范围以及返回已执行的检查。条件尚未验证的会话使用 `workflow-implementer`。旧扩展未参与运行探针。

## 交付审查

独立审查 `UNVERIFIED`。本次全量 `workflow-reviewer` 派发因模型服务返回 `502`（`Upstream access forbidden`）退出，未生成有效 `REVIEW_STATUS`。临时项目的审查探针只验证了 OMP 的派发协议。

主会话接管集成核对，检查了安装和诊断调用路径、验收标准、技能副本一致性以及回归结果。核对发现白名单诊断遗漏配置路径，已补上测试及报错路径。`2.2` 保持待完成，等待独立审查证据。
