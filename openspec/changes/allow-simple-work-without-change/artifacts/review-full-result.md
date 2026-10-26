## 审核结论

Review mode: full。无前序有效报告（`artifacts/review.md` 仍是第 1 轮待返回）。Blocking: yes。

本轮只读了声明的 12 个源/测试文件和本 change 的 proposal、spec、design、tasks、context 与证据日志，没有改文件，也没有重跑仓库检查。

### F1 — HIGH，Blocking: yes

`README.md:355`、`README.md:386-406`、`README.md:519`、`README.md:554-556`、`README.md:593`、`README.md:612`、`README.md:887`。否定断言窄到没抓住这些句子：`tests/contracts.test.js:62`。

违反 AC-005，并让面向人的流程重新要求 AC-002 禁止的 `.workflow/` 建档。设计要求替换与本分支冲突的旧示例。`AGENTS.md` 也规定新工作不得把 `.workflow/` 当新状态。

「使用方法」和「记录系统」已经先走快速通道，但「完整使用指南」仍是当前流程：

- `README.md:386-392`：第一次接手先询问是否创建 `.workflow/`，并先读 `.workflow/CURRENT.md`，没有记录就建骨架。
- `README.md:406`：新状态一律写入 `.workflow/`。
- `README.md:355`：任务目录由主路由同意后按需创建。
- `README.md:556`、`README.md:593`、`README.md:612`：完整任务、默认调用和跨会话续接都从 `.workflow/` 阶段开始。
- `README.md:519`：OMP 调度从需求澄清一路到归档，没有快速分支。
- `README.md:887`：收尾示例无条件要求写入 `artifacts/verification.md`。

失败场景：合格的局部文案修正若按「完整使用指南」执行，会在共享资格判定前征求同意并创建 `.workflow/`，或按旧阶段进入澄清/规划。`tests/contracts.test.js:62` 只排除「主路由会先询问是否创建 `.workflow/`」这一句；`README.md:386` 的「它会先询问是否创建」仍能通过。

影响：人读流程图，或后续会话把 README 当路由说明时，会绕过 `quality-profiles.md` 的快速通道，重新建禁止的任务状态。

最小修复：这些当前流程段改为先引用 `#simple-work-fast-path`；`.workflow/CURRENT.md` 只保留显式 legacy 恢复。收尾示例只在已选正式 change 时写 verification。把否定断言扩到「先询问是否创建 `.workflow/`」和「进入主路由先读 `.workflow/CURRENT.md`」。验证：`node --test tests/contracts.test.js`。

### F2 — HIGH，Blocking: yes

`skills/run-engineering-workflow/SKILL.md:154-155`。位置守卫只比较到 `## Start`：`tests/contracts.test.js:41-43`。

违反 AC-001。`SKILL.md:77-91` 要求在 discovery 前判定，合格则返回并跳过后面的正式阶段，`## Start` 也标了 formal-only。但 `## Assess Profile First` 仍写：在任何 routing 或 dispatch 决策之前，先读选定 OpenSpec `proposal.md`。这句没有 formal-only 限定。

失败场景：局部文档纠错。执行者按「Assess Profile First / Before any routing」先找选定 proposal。仓库里已有无关未归档 change 时，就会先 `list_changes` 并匹配候选，然后才做快速资格判断。即使最后不建档，AC-001 禁止的「先匹配任务」已经发生。

影响：主路由的可执行合同自身把 discovery 放回分流之前，快速通道可以被旧的风险判断顺序抵消。

最小修复：该节改为快速判定之后、仅正式分支；删掉「Before any routing」。合同测试断言读取 `proposal.md` 的档位评估不能先于 `## Choose Fast Or Formal`，且必须标成 formal-only。验证：`node --test tests/contracts.test.js`。

非阻断：

- `skills/plan-solution/agents/openai.yaml` 的 default prompt 未提示已选快速通道。技能正文已有早返回，不反向建档。
- `## Bounded Context And Dispatch Contract` 在分流前要求 dispatch 前解析一个 change id。语义限于派发；快速通道不派发。若实现时把 implementation 读成必须先有 change，再把该句收进正式分支。

## Standards

有阻断。F1 违反 `AGENTS.md`：新工作只把 OpenSpec 当正式持久状态，不得创建或更新 `.workflow/`。其余核对通过：资格源只在 `skills/run-engineering-workflow/references/quality-profiles.md`，没有新配置、状态机或依赖；正式确认、TDD 和 Delivery Review Budget 没有被放宽；本 change 的人读产物是中文。生成镜像不是源，未当规范审查。

## Spec

- AC-001：不满足。早返回段落在，但 F2 仍要求先读选定 proposal。
- AC-002：技能与命令文本满足；F1 的人读流程仍要求创建 `.workflow/`，整体不满足。
- AC-003：满足。共享资格源要求 diff、项目要求的最小检查、对话报告 `NOT RUN`，并禁止把失败写成 `CLEAN` 或回补 artifacts。finish 早返回不补跑、不建档。
- AC-004：满足。行为、显式 OpenSpec、选定 change 续接、更严项目规则和 CLI 故障都留在正式分支；升级时停止扩大、保留 diff/检查、不自动建档或不丢改动。静态场景覆盖了这些边界。
- AC-005：不满足。命令、`ARCHITECTURE.md:29-34`、plan/finish 早返回与主路由一致；F1 的 README 流程图不一致。正式 lightweight 仍要求 proposal 草图，原正式要求还在。
- AC-006：证据满足到本审核之前。切片 1 RED 为 3 失败，切片 2 RED 为 2 失败；随后 GREEN，`npm test` 39/39，Python unittest 16/16，OpenSpec strict valid，Project All 安装 54 项及 helper/commands/overlay 为 PASS。本报告是那一次独立 full review。`tasks.md` 3.1/3.2 仍待父会话记录，不构成实现缺陷。

正确性：除 F1/F2 外，资格、执行、验证和升级都集中在共享源；plan/finish 只消费已选快速通道，不自行降级。安全：无密钥、权限或持久数据扩大；CLI 错误不能授予资格。测试：新增断言能锁住已写进技能的句子，但锁不住 F1 的改写句和 F2 的优先级句；按已批准设计，它们是文本合同，不是运行时分类器。复杂度：单一资格源合适；README 两套流程是多余且冲突的政策，不是该再加一层抽象。

## 剩余风险与未跑检查

- 四宿主新会话端到端、默认 LSP（biome 不可用）、全局安装、外部 OMP gate：记录为 NOT RUN。静态 fixture 不证明运行时分类。
- 本审核未重跑 `npm test`、Python unittest、OpenSpec validate、安装脚本、`git diff --check`，也未重算 `review-inputs.json` 的 SHA256。
- 未逐字节比对 `.agents/`、`.claude/`、`.omp/` 镜像；安装日志称与 canonical 一致。
- 无关归档移动、legacy 与生成目录按范围排除。

Reviewed inputs：`review-inputs.json` 的 12 个路径，以及本 change 的 proposal、spec、design、tasks、context、`review-input.patch`、RED/GREEN 与 node/python/openspec/installation 日志。

REVIEW_STATUS: FINDINGS