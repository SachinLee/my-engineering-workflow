# 技术方案

## 方案结论

采用“OpenSpec canonical + 旧记录兼容读取 + 本仓库质量治理”的架构。

OpenSpec 接管新任务的规格、变更目录、设计和实现清单；本仓库不再为新任务创建 `.workflow/tasks/`。本仓库继续提供风险分级、TDD 约束、bounded dispatch、独立 review、验证证据和用户验收规则，但这些记录必须落在当前 OpenSpec change 内，不能另起一套新任务状态机。

旧 `.workflow/` 不迁移即不改写；旧 `.trellis/` 永远只读。迁移必须由用户明确触发，并采用“复制到新 change + 校验 + 建立来源映射”的方式，失败时不修改来源目录。

## 新任务目录约定

推荐结构：

```text
openspec/
  config.yaml
  specs/                         # 已合并的当前系统规格
  changes/<change-id>/
    proposal.md                  # 目标、范围、非目标、验收意图
    specs/<domain>.md             # ADDED / MODIFIED / REMOVED requirements
    design.md                    # 技术方案、接口、数据流、兼容性
    tasks.md                     # 可勾选实现任务和依赖顺序
    context.md                   # 本仓库的 bounded dispatch 上下文包
    verification.md              # 检查、review、RED/GREEN、剩余风险
    migration-report.md          # 仅迁移产生，记录旧来源与校验结果
  changes/archive/               # OpenSpec 归档变更
```

`context.md` 和 `verification.md` 是本仓库的自定义 change artifacts。实现前先确认 OpenSpec 是否允许未知 artifact；如果 CLI 会拒绝未知文件，则把它们放入 `openspec/changes/<id>/artifacts/` 或通过项目配置声明，不能退回 `.workflow/` 双写。

## 事实源与状态映射

| 现有产物 | 新 OpenSpec 产物 | 规则 |
| --- | --- | --- |
| `.workflow/tasks/<id>/prd.md` | `proposal.md` + `specs/*.md` | 需求意图进入 proposal；可验证行为进入 delta spec |
| `design.md` | `design.md` | 保持核心内容，统一为 OpenSpec change 内的设计文档 |
| `implement.md` 的切片 | `tasks.md` | 切片成为任务项；依赖和 writer 约束写入任务说明或自定义元数据 |
| `context.md` | change 根目录 `context.md` | 仅放已定位文件、关键结论、必须保持的不变量和精确验证命令 |
| `outcome.md` | `verification.md` | 保存每条 AC、真实命令、RED/GREEN、review findings、修复和剩余风险 |
| `STATUS` / `CURRENT.md` | OpenSpec CLI status + 当前 change 目录 | 不再新增 `.workflow` 状态指针；旧指针仅用于 legacy 恢复 |
| `tickets/*.md` | `tasks.md` 的依赖图 | 只有跨 writer 的任务才保留单独的自定义 ticket artifact |
| `.workflow/journal.md` | OpenSpec archive + `verification.md` | 旧 journal 保留；新任务不追加新 journal，除非用户明确要求兼容报告 |

OpenSpec CLI 的 status 输出必须成为活动 change 的唯一选择依据。主路由不能通过扫描所有目录猜当前任务；如果 CLI 返回多个活动 change，必须返回 `BLOCKED` 并要求用户选择。

## 路由状态机

```text
request
  -> detect OpenSpec capability and project state
  -> openspec status --json
  -> no active change
       -> clarify/propose -> proposal + specs + design + tasks
  -> active change with incomplete artifacts
       -> update/continue/ff according to missing artifact
  -> tasks ready and user approved
       -> apply -> TDD implementation
  -> implementation complete
       -> verify + repository checks + independent review
  -> review clean
       -> write verification.md, stop at awaiting-acceptance
  -> user accepts
       -> archive -> merge delta specs and archive change
```

OpenSpec 的 `/opsx:propose`、`/opsx:apply`、`/opsx:verify`、`/opsx:archive` 作为默认入口；实际命令名称以 `openspec init` 针对当前客户端生成的适配为准。当前仓库的 `run-engineering-workflow` 负责在这些动作前后施加风险和验收约束，不复制 OpenSpec 的命令实现。

## 旧记录恢复与迁移

### `.workflow/`

1. 如果没有 OpenSpec canonical project，读取 `.workflow/CURRENT.md` 或 `.workflow/by-session/`。
2. 如果存在旧任务，显示 `LEGACY_WORKFLOW`，读取其 `STATUS`、`prd.md`、`design.md`、`implement.md`、`outcome.md`。
3. 允许用户选择“继续旧任务”或“迁移到 OpenSpec”；不自动猜测。
4. 迁移时创建确定性的 change id，复制并转换字段，写入 `migration-report.md`，逐条校验 AC 和来源 hash。
5. 迁移成功后，后续新记录只写 OpenSpec；旧任务目录保持不变，报告中记录 `source_of_truth: openspec`。
6. 如果迁移失败，删除未完成的新 change 或标记失败的迁移目录，但绝不修改旧任务。

### `.trellis/`

继续使用现有的只读同名产物映射。任何 Trellis 脚本执行、注入器安装、`.trellis/` 写入都应被合同测试拒绝。

## 多平台边界

- Codex / Claude Code / OMP / Pi 仍由当前安装器管理本仓库的 skill、agent 和入口。
- OpenSpec CLI 与生成的 commands/skills 是外部依赖，不 vendor 到本仓库。
- 安装器只负责检测、提示和同步本仓库适配；不在每个项目静默执行 `openspec init`，初始化必须由用户确认。
- doctor 检查 Node.js、OpenSpec CLI、项目 `openspec/config.yaml`、支持的客户端适配和版本兼容性。
- OpenSpec 缺失或版本不满足时：新任务返回 `OPENSPEC_STATUS: BLOCKED`，legacy 任务仍可按旧记录读取；不得把新任务降级成新的 `.workflow` 记录。
- OMP 的 `config/omp-workflow.yml`、Claude agent、Pi agent 都只引用 capability 名称和 OpenSpec artifact 路径，不固定 provider-specific model。

## 关键不变量

- 新任务只有一个 canonical change。
- OpenSpec 规格、change 任务、verification 证据与代码状态必须可从同一 change 目录关联。
- 用户批准前不能进入 implementation。
- reviewer 不得使用实现会话的自我复述代替独立上下文。
- 代码或任务快照发生实质变化后必须重新验证和 review。
- `archive` 只能在用户验收后执行。
- 不使用自动注入来传递易变任务状态。
- 不因为迁移或 OpenSpec 适配而降低安全、可访问性、正确性或验证要求。

## 回滚策略

- OpenSpec CLI 升级失败：锁定并恢复已验证的 CLI 版本，项目记录不改写。
- 路由回归：只回滚本仓库 adapter/skill/installer 变更；旧 `.workflow` 和 `.trellis` 原样可读。
- 单个迁移失败：删除迁移生成的未归档 change，保留来源目录，重新生成新的迁移 id 或修复映射后重试。
- 已归档 change 不回写旧 `.workflow`；如需恢复，使用 OpenSpec 的 change/规格历史重新创建新 change。

## 需要在实现前验证的外部事实

- 当前 OpenSpec CLI 的最低 Node.js 和 CLI 版本要求。
- `openspec status --json`、`instructions --json` 的稳定字段。
- 自定义 artifact 是否被 CLI、archive、update、verify 保留。
- 30+ 客户端适配中 Codex、Claude Code、OMP、Pi 的实际命令生成路径。
- OpenSpec 是否提供可供本仓库调用的迁移/导出 API；若没有，使用结构化 Markdown/JSON 解析，不解析人类可变的命令输出。
