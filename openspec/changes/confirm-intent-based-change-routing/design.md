# Design：会话意图匹配与确认式任务路由

## 决策

1. **语义判断留在主会话**：主会话已有理解用户意图的能力；本设计只约束它依据哪些事实判断（proposal 目标、specs 预期行为、范围与验收关系）以及何时必须停止等确认。禁关键词分类器、向量库、相似度阈值——它们会把"同义"退化成词面相似，违背 AC-008。
2. **只读发现与写入分离**：`list_changes()` 只读（校验根目录、版本、`openspec list --json`），`create_change()` 显式创建（校验 id、执行 `openspec new change <id> --description --goal --schema --json`）。诊断路径（doctor）只走只读发现，无创建副作用。
3. **detect_project_mode 行为收敛**：单 change 不再自动选中，多 change 不再 BLOCKED；`change=None` 一律返回 `unselected` + `available_changes`。显式 change 路径（校验存在性、读状态）保持不变。resume/doctor 语义不变，但多候选不再算环境故障。
4. **单源分发**：`scripts/openspec_compat.py` 是唯一实现；install.ps1 用 `Copy-ManagedFile` 复制到各 harness 的 `<skills root>/run-engineering-workflow/scripts/openspec_compat.py`，Sync-SkillDirectory 之后执行。
5. **同义定义**：同一工作目标的不同表达——目标对象、预期结果、范围兼容、验收关系四维判断；相关≠同义；信息不足先澄清，不当作无匹配。

## 备选方案

- **自动执行 + 仅歧义时询问**（先前 agentmemory 建议）：被用户否决——用户要保留创建决定权。
- **把 confirm 提示词写进命令而非 skill**：命令是 Claude Code 专属入口，语义规则必须约束所有 harness，落在 SKILL.md。
- **在 detect_project_mode 中加 confirm 参数**：检测函数应无副作用、无交互；确认是主会话职责，兼容模块只提供确定性操作。

## 数据流

请求 → `list_changes()`（只读，含 blocked 结构化错误）→ 主会话读取候选 proposal/specs 匹配 → `ask` 建议（创建/复用/取消）→ 确认后 `create_change()`（新建）或 `detect_project_mode(project, change=<id>)`（复用校验）→ 进入现有工作流。取消 → 停止，无任何写入。

## 测试接缝

- `tests/test_openspec_compat.py`：FAKE_CLI 扩展支持 `new change` 子命令并记录 argv；覆盖 list_changes 只读、单 change 不自动选中、多 change 不 BLOCKED、create_change 成功/同名冲突/非法 id、显式 change 路径不回归。
- `tests/contracts.test.js`：新增"路由推荐并强制确认"契约；evals 增加语义匹配与确认场景 case。
- 真实 CLI 演练：临时目录创建成功、同名重复报错。

## 回滚

行为全部回退 = 恢复 detect_project_mode 的自动选中分支 + 删除 list_changes/create_change + SKILL.md 恢复旧 Start 步骤。无数据迁移，无持久状态。

## AC 映射

AC-001/002 → spec "匹配结果必须先征得用户确认"；AC-003 → 同上 Scenario 3 + detect unselected 测试；AC-004 → spec "多候选由用户决定"；AC-005/006 → spec "确认语义与失效" + 主路由触发规则；AC-007 → spec "候选范围"；AC-008 → design 决策 1/5 + eval case；AC-009 → spec "错误不伪装成无匹配"；AC-010 → spec "确认语义与失效" Scenario + create_change 冲突测试；AC-011 → 治理复用规则；AC-012 → install.ps1 分发 + 临时目录演练。
