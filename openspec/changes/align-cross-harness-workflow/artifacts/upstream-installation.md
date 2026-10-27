# 上游安装核对

日期：2026-10-27。

- Matt 源码：`5beb35b040e3de97e54fa9e386d7e42d15c295c2`（1.3.1）。对共享技能、Codex、Claude、OpenCode、Pi 的已存在同名技能进行逐文件 SHA256 对比，57 处对应安装没有差异，无需覆盖。
- 同名例外：共享和 Claude 的 `handoff` 属于 agentmemory（恢复最近会话），Matt 的 `handoff` 用于输出交接文档；保留既有 agentmemory 技能，避免静默改变用途。
- Claude：通过原生 `claude.exe plugin update ponytail@ponytail --scope user --json` 从 4.9.0 更新到 5.3.2。更新后 hooks/ 和 skills/ 所有源码文件的 SHA256 均相同。CLI 明确要求重启生效。
- Codex：原缓存虽标为 5.3.2，但 hooks/ 有六处缺失或差异；通过原生 `codex plugin add ponytail@ponytail --json` 刷新，hooks/ 和 skills/ 全部相同。未改写模型/供应商/信任决策。`codex plugin list` 曾在 30 秒超时，改用安装结果和文件散列核实。
- Ponytail 源码：`09c434ab73ca43761c5d8b0c5d341926c2fba710`（5.3.2）。使用同目录 `sync-ponytail.ps1`，预检目标不存在后，将六个技能发布到 `~/.agents/skills`，逐一验证 SHA256。该操作只增加共享技能，不新增每轮注入插件。
- 未整套引入 ECC；未替换 Slim 的 PowerShell 补丁；未新增 Pi/OMP 每轮注入；模型、供应商和 Pi overrides 均保留。

静态安装一致性不能证明各客户端实际运行表现。原生插件或代理由下次新会话加载；本次不宣称已执行各客户端端到端对话。
