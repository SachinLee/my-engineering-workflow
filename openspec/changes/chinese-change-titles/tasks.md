# Tasks：让 OpenSpec 任务以中文标题出现在列表与路由确认中

## 切片 1：规则落地（config + skill）

- [x] 1.1 `openspec/config.yaml`：`rules.proposal` 新增一条 "Title (H1) 写成 `# 提案：<中文短标题>`，并保留 `## Why` 与 `## What Changes` 英文段名"（blocked_by: 无）
- [x] 1.2 `.pi/skills/openspec-propose/SKILL.md` 第 1 步（derive kebab-case name 附近）补"H1 写中文标题 + 保留英文 section 名"指引（blocked_by: 无）
- [x] 1.3 同步 `.agents/skills/openspec-propose/SKILL.md`、`.claude/skills/openspec-propose/SKILL.md`、`.omp/skills/openspec-propose/SKILL.md`（blocked_by: 1.2）
- [x] 1.4 验证：`openspec instructions proposal --change chinese-change-titles --json` 的 `rules` 含新规则（blocked_by: 1.1）

## 切片 2：compat 脚本回传标题（测试先行）

- [x] 2.1 `tests/test_openspec_compat.py`：用临时目录写 `proposal.md` 覆盖七种情形（中文 H1 / `# Proposal` 占位 / `Change:` 前缀 / 空 H1 / 文件缺失 / 非标题 `#` 行 / 代码围栏内 `#` 行）；新增用例：`change_titles` 正确映射、不可读时回退为 id、`available_changes` 仍是 id 列表、`openspec show` 失败不阻塞（blocked_by: 无）
- [x] 2.2 `scripts/openspec_compat.py`：新增 `TITLE_RE` 与 `_change_titles(root, names)`（直接读 `proposal.md` 的 H1）；`_open_spec_names` 返回 `(version, names, titles)`；`list_changes` 与 `detect_project_mode` 的 unselected 分支新增 `change_titles` 字段，不可读/缺字段回退为 id，blocked/unselected 语义不变（blocked_by: 2.1）
- [x] 2.3 跑 `python -m unittest tests.test_openspec_compat` 全绿（blocked_by: 2.2）

## 切片 3：doctor 与路由展示

- [x] 3.1 `scripts/doctor.py:198` 附近：unselected 候选提示用 `change_titles` 拼 `id（中文标题）`，无标题时退回 id（blocked_by: 2.2）
- [x] 3.2 `skills/run-engineering-workflow/SKILL.md` 的匹配确认段落：推荐与确认提示使用 `id（中文标题）` 形式（blocked_by: 2.2）
- [x] 3.3 同步 `skills/run-engineering-workflow/` 的 harness 副本（`.agents`/`.claude`/`.omp`）（blocked_by: 3.1, 3.2）

## 切片 4：契约测试与分发

- [x] 4.1 `tests/contracts.test.js`：断言 `openspec/config.yaml` 的 `rules.proposal` 含中文 H1 规则；断言 `.pi/skills/openspec-propose/SKILL.md` 含"H1 写中文标题 + 保留 Why/What Changes"（blocked_by: 1.1, 1.2）
- [x] 4.2 跑 `node --test tests/contracts.test.js` 全绿（blocked_by: 4.1）
- [x] 4.3 若 `scripts/openspec_compat.py` 的 harness 副本由 `scripts/install.ps1` 复制，临时目录验证分发后 `list_changes` 仍返回 `change_titles`（blocked_by: 2.2）

## 切片 5：真实 CLI 演练

- [x] 5.1 临时目录 `openspec new change demo-title` → 写 `# 提案：中文演练标题` + `## Why` / `## What Changes` → `_change_titles` 读出中文标题；本仓库 8 个真实 change 的 `change_titles` 均非空（blocked_by: 1.1）
- [x] 5.2 `python scripts/openspec_compat.py` 路径下的 `list_changes` 对真实项目返回 `change_titles`，实测本仓库 8 个 change 中 7 个读出中文标题，1 个按设计回退 id（blocked_by: 2.2）

## 切片 6：文档与验收

- [x] 6.1 `README.md:204` 附近关于"确认提示会包含中文任务名"的表述与实际行为对齐（blocked_by: 2.2）
- [x] 6.2 `artifacts/verification.md`：逐条记录 AC-001..AC-009 的证据（blocked_by: 全部实现任务）
- [x] 6.3 自查复核（同一上下文）：查出并修掉 4 处真实缺陷（`detect_project_mode` "not listed" 分支缺 `change_titles`、`_change_titles` 缺 id 守卫、H1 正则误吃缩进/`#hashtag` 行、`utf-8-sig` 读取），每条都补了回归用例（blocked_by: 6.2）
- [x] 6.4 独立模型复核：第一次派发（`del_mvorsscl_9sns`）30 分钟无结论被 watchdog 杀掉，作废；重派窄范围限时复核（`del_mvosxonn_ilph`）返回 `VERDICT: 通过`，无 BLOCKER，并指出 1 个 LOW 瑕疵（代码围栏内 `# 注释` 会被当标题），已修 + 补用例 `test_fenced_code_hash_lines_are_not_titles`（blocked_by: 6.3）

## 切片 7：让规则真正到达新项目（安装到本地时发现的缺口，用户要求在本 change 内修）
- [x] 7.1 `scripts/openspec_compat.py` 新增 `TITLE_RULE_ANCHOR`、`_config_file(project)`、`ensure_proposal_title_rule(project)`：纯文本插入，只在锚点文本缺失时写入，保留模板注释块与用户已有规则，幂等（blocked_by: 无）
- [x] 7.2 `create_change` 在 `openspec new change` 成功后调用 `ensure_proposal_title_rule(root)`，并把结果作为 `title_rule` 随返回值回传——规则必须在 agent 读 `openspec instructions proposal` 之前就位（blocked_by: 7.1）
- [x] 7.3 `scripts/doctor.py` 新增 `_check_proposal_title_rule`：已初始化项目缺 H1 规则时给出 WARNING（覆盖规则引入前就存在的老项目），并复用 compat 的 `TITLE_RULE_ANCHOR` 常量避免两处漂移（blocked_by: 7.1）
- [x] 7.4 测试先行：`tests/test_openspec_compat.py` 新增 6 个用例（create_change 补规则、幂等、保留注释与用户规则、无 rules 块时插到注释示例之后、缺 config 时 skipped、CRLF 不被改写），`tests/contracts.test.js` 新增 1 个契约测试（blocked_by: 7.1）
- [x] 7.5 真实 CLI 端到端演练：干净目录 `openspec init --language Chinese` → `create_change` → `openspec instructions proposal --json` 的 `rules` 出现 H1 规则；再次 `create_change` 时 `title_rule.status == "unchanged"` 且 config 逐字节不变（blocked_by: 7.2）
- [x] 7.6 测试抓到的真实缺陷并修复：`read_text` 会做换行转换，导致 CRLF 项目被误判并改写为 LF；改为 `read_bytes().decode("utf-8-sig")`（blocked_by: 7.4）
- [x] 7.7 把 `proposal.md` / `spec.md` 中「经 `scripts/install.ps1` 分发」的错误表述改为「手工同步 + 不由 install.ps1 分发 + 会被 `openspec update --force` 重写」（实测修正）（blocked_by: 7.1）

## 切片 8：让用户不靠 agent 也能查任务（用户 m01556 追问「加这个 cli 的作用是什么」）
- [x] 8.1 `scripts/openspec_compat.py` 新增只读 CLI `_main(argv)` + `list` 子命令，输出 `id  中文标题`；无子命令打印 help 并返回 2，project 不存在或未初始化时把 `reason` 打到 stderr 并返回 1（blocked_by: 无）
- [x] 8.2 新增 `_safe_print`：控制台编码无法表示中文时降级为替换字符，绝不让 `UnicodeEncodeError` 丢掉 id——id 才是所有 openspec 命令的入参（blocked_by: 8.1）
- [x] 8.3 测试先行：`tests/test_openspec_compat.py` 新增 4 个用例（输出 id+标题、标题等于 id 时不重复打印、blocked 时返回 1 并报因、无子命令返回 2 且打印 usage），用 `contextlib.redirect_stdout` 捕获（blocked_by: 8.1）
- [x] 8.4 `tests/contracts.test.js` 新增契约测试：CLI 入口必须存在、必须保持只读（断言不出现 `create`/`update`/`archive`/`apply` 子命令）、旧的无入口 `SystemExit("Import this module...")` 必须消失、skill 必须告知用户这条命令（blocked_by: 8.1）
- [x] 8.5 `skills/run-engineering-workflow/SKILL.md`（+ `.agents`/`.claude`/`.omp` 三副本）补指引：用户想自己查任务时用 `python scripts/openspec_compat.py list`，并说明为何比 `openspec change list --long` 可靠（后者对中文段名的 proposal 打印 `(unable to read)`）（blocked_by: 无）
- [x] 8.6 实测：本仓库 8 个 change 中 7 个打印出中文标题，`openspec-compatibility` 按设计只打印 id；`PYTHONIOENCODING=ascii` 下降级为 `?` 且不崩（blocked_by: 8.1）
