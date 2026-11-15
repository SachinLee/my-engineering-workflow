# 复验轮次 3 独立审查

## 授权及轮次
- 范围：AC-007–AC-010；Standard。用户批准复用本 change，新增本轮交付范围。保留前两轮结论；本轮一次 full，最多一次 focused。
- reviewer：`ses_e2641fa44ffeM8RQOUf5QjgyQs`，独立 `workflow-reviewer`。
- 首次交接缺少 Phase、完整 workspace 基线、标准 brief 和轮次信息，返回 `REVIEW_STATUS: INVALID`；未开展有效审查。
- 已补齐交接，并以 `Review retry: invalid` 作唯一受控 replacement；形成以下有效 full 报告。尚未消耗 focused。
- 基线：`53e4dcfccc94425a62eabdfa9ccc3e445abe9646`，staged 为空；审查指定当前内容及相关未提交修改，不覆盖其他 change。

## 完整审查结果
`REVIEW_STATUS: FINDINGS`；F-004、F-005 均为 MEDIUM、blocking=yes。

### F-004：Pi output 层级错误
- 位置：修复前 `skills/run-engineering-workflow/SKILL.md:418-420`、`references/specialist-routing.md:49-51`。
- 错误：文档将 `output` 列为 `options` 成员，实际 pi-subagents 会拒绝，错误为 `'output' is a top-level field, not an option.`。
- 影响：遵循文档配置受限输出会在派发前失败，阻断 AC-008。成功 reviewer 烟测未覆盖错误层级。
- 修复要求：顶层 `output`；`context`、`agentScope`、`timeoutMs` 在 `options`；增加完整示例及结构回归，并同步安装。
- reviewer 核对版本 v0.88.0 上游 schema；实施者后续另核对本机 v0.88.1 bundle，层级结论相同。

### F-005：Codex 静态可发现性假阳性
- 位置：修复前 `scripts/doctor.py:563-582`。
- 错误：仅按三个 TOML 文件存在就输出 `Statically discoverable: yes`，没有校验语法、必需字符串字段或角色 name。
- 影响：文件截断、无效 TOML、缺字段、错误 name 仍可能误报可发现，阻断 AC-010。runtime UNVERIFIED 不能补救静态层错误。
- 修复要求：分别报告文件存在与有效角色；检查 `name`、`description`、`developer_instructions` 及预期名称，不能校验时静态状态未知；保持 Python 兼容且不添依赖；补负向回归。

## Standards / Spec
- 除 F-004/F-005，未发现额外阻断的标准、安全或复杂度问题。未新增调度器、注入器或影子状态。
- AC-007 静态合同覆盖；AC-008 受 F-004 阻断；AC-009 当前三个原生角色无固定模型、保留用户配置，但完整 Codex 运行仍 UNVERIFIED；AC-010 受 F-005 阻断。

## 证据与限制
- reviewer 只读检查指定当前文件、相关 Pi agents、标准、工件及一手接口资料，未运行检查、安装或修改。
- 消费主会话证据：Node 63/63；Python 共 81 项、2 skipped；OpenSpec strict PASS；diff check exit 0。
- Pi fresh async reviewer 实际完成且原生通知回传；Codex 启动 reviewer 后 180 秒超时，exit 1，不计完整运行通过。
- 主会话四份配置 SHA256 比对均不变。reviewer 未读取私人配置，也未独立执行 Git 覆盖检查。旧 workspace 附件需更新为本轮范围以补足差异证据。
- 本轮 RED 输出由实施者报告并给出失败点，原始 RED 全量日志未归档，不能声称已独立核对原始日志。

## 修复与唯一 focused
- 主会话分派两个无重叠 repair lane；最终修复、检查、证据补齐后复用同一 reviewer，仅检验 F-004/F-005 及直接影响。
- 同一 reviewer 已完成本轮唯一 focused，`REVIEW_STATUS: CLEAN`；F-004/F-005 均 resolved，剩余 blocking findings 为 none。

## 聚焦复核结论（2026-11-14）
- F-004：复读实际 SKILL/reference 与结构测试，核对顶层 output 和 options 中的 scope/context/timeout；消费 `pi-smoke-round3.json` 的实际派发、无错误和 marker 回传，确认参数通路。resolved。
- F-005：复读 tomllib 校验、字段类型、角色名、文件数与有效数分离、无 parser 时 unknown，以及负向用例和既有诊断。无自制 parser 或依赖；resolved。
- Standards：未发现剩余阻断性标准、正确性、安全或复杂度问题。
- Spec：AC-007–AC-010 在本轮静态及明确烟测边界内无 findings；未将 Codex runtime 升级为已验证。
- 消费修复后证据：Node 64/64；Python 86 项含 2 skipped（84 passed）；Codex doctor exit 0；OpenSpec strict PASS；diff check exit 0；现代 Python focused 9 通过、Python 3.10 5 通过和 4 skipped。
- 复核只读，未执行测试、安装或 Git；检查结果归属主会话。差异附件在全部代码修复后生成，其他 change 的路径仅为工作区状态而非本轮覆盖。
- 本轮预算已使用：一次有效 full（此前 INVALID 的唯一受控 replacement）和一次 focused。没有额外审查或自动授权。
- 状态保持 awaiting-acceptance；NOT COMMITTED；Codex 完整 runtime 和既有 OpenCode/Slim 端到端选模仍 UNVERIFIED。
