# 统一跨客户端工程工作流与本地安装

## 目标与授权
用户已明确授权按本会话分析更新工作流及本地安装。以 Matt + Ponytail 为方法核心，保留各客户端模型与供应商配置；不增加 ECC 默认流水线。Standard 变更。

## 范围与验收标准
- [ ] AC-001：安装器及 doctor 正式支持 OpenCode，共享六个规范技能，检测并备份迁移已知旧副本；保留 Both = Codex + OMP。
- [ ] AC-002：各端适配区分共享交付规则与客户端调度；Slim 是 OpenCode 唯一主调度器，一次正式交付仅一套审查预算。
- [ ] AC-003：范围明确、低风险的小行为修复可采用轻量执行，必须有回归检查；高风险、公共契约、数据迁移继续正式流程。
- [ ] AC-004：doctor 比较已安装代理/命令内容并报告已知模型别名折叠、Pi overrides 与 Codex 能力差异，不泄露凭据、不擅自改模型。
- [ ] AC-005：本地 Matt / Ponytail 安装与已审核源码同步；工作流各客户端安装更新，记录备份、差异、执行证据和无法运行的检查。
- [ ] AC-006：OpenCode 正式实现和独立审查使用 OMO-Slim 当前 preset 的 `fixer` / `oracle` 角色路由，不静态复制模型 ID；角色不可用或路由未验证时明确报告 `UNVERIFIED`，不把继承协调器模型误报为角色模型。

## 范围外
不升级供应商或模型，不提交/推送，不自动归档，不替换 Slim 的 Windows 修补版本，不给其他项目强制安装，不整套引入 ECC。

## 复验轮次 3：Pi / Codex 按需专长协作（2026-11-14）
用户授权实施前述方案并明确复用本 change。本轮为新批准的交付范围，独立于前两轮材料；保留旧审查记录，本轮预算为一次完整审查、最多一次修复后聚焦复核。质量级别 Standard。
- AC-007：主代理负责协调、整合与证据，按任务形状选择 explore / research / implement / consult / review；已掌握上下文的小改动及上下文密集文档可直接完成，不强制全阶段流水线。只读探索可先于正式 change；正式实施及最终独立审查保留 OpenSpec 上下文包与质量门槛。
- AC-008：Pi 显式处理 subagents_enable 激活、发现和异步完成；复用 scout / researcher / oracle 时限定 fresh context、写入边界和可用工具；正式角色仍由 workflow agents 提供。缺失独立 reviewer 必须 UNVERIFIED，不允许主代理自审冒充。
- AC-009：Codex 安装原生、无固定模型的 workflow TOML 角色；保留已有自定义角色和用户配置。只有实际证明发现和调用才报告运行能力，不把安装成功或新上下文等同跨模型。
- AC-010：安装器提供 Pi 原生共享 skill 入口；doctor 区分已安装、静态可发现、运行验证未知，保持 Both 兼容。契约与安装回归先 RED 后 GREEN；真实运行烟测如受限须明确 UNVERIFIED。
- 本轮不安装新调度器、不更改 toolActivation 或模型配置、不引入默认 evidence-auditor / delegate，不更改其他任务状态。
