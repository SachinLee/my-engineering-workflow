## ADDED Requirements

### Requirement: 共享技能与客户端原生安装
安装器 SHALL 从规范 skills/ 发布六个工作流技能，并支持 OpenCode。Both SHALL 继续表示 Codex + OMP；All SHALL 包含 OpenCode。已知旧副本迁移 SHALL 先备份，未知链接 SHALL 拒绝覆盖。

#### Scenario: OpenCode 旧副本迁移
- **WHEN** OpenCode 技能目录存在已知工作流旧副本
- **THEN** 安装器保存旧副本后建立受管理的技能入口，并可检测再次安装是否幂等

### Requirement: 宿主调度与共享质量规则
工作流 SHALL 定义验收、证据和审查预算，宿主 SHALL 管理调度与模型。OpenCode SHALL 使用 Slim 作为唯一主调度器；正式交付 SHALL 最多一次完整审查和一次针对修正的聚焦审查。

#### Scenario: Slim 委派已授权工作
- **WHEN** 用户已授权明确范围且 Slim 可以调用对应 specialist
- **THEN** 工作流允许按宿主能力委派，不要求重复授权或另起总控

### Requirement: 风险决定执行重量
范围明确、低风险、可验证的小行为修复 MAY 使用轻量流程，且 SHALL 执行有效回归检查。公共契约、认证、持久数据迁移等高风险变更 SHALL 使用正式流程。

#### Scenario: 小行为修复
- **WHEN** 任务范围明确且没有高风险、正式续接或持久交接要求
- **THEN** 可直接修改并运行回归检查，不以文件数量作为唯一判断条件

### Requirement: 诊断保留用户配置所有权
doctor SHALL 比较受管理代理和命令内容，报告 Claude 模型别名折叠、Pi overrides 和 Codex 能力边界；SHALL 不输出凭据或重写模型配置。

#### Scenario: 本地模型配置不同
- **WHEN** 本地 Pi 配置模型覆盖或 Claude 多个别名指向相同模型
- **THEN** doctor 报告相关事实，保留原有配置

### Requirement: OpenCode 工作角色使用 Slim 模型路由
在 OMO-Slim 管理 OpenCode 调度的会话中，正式实现 SHALL 通过 Slim `fixer` 角色调度，独立审查 SHALL 通过 Slim `oracle` 角色调度，使各自遵从当前激活 preset 的模型配置。工作流安装器 SHALL NOT 将某个 preset 的模型 ID 静态写入受管 OpenCode agents；仅当实际通过相应角色调用时，方可报告使用了角色配置模型。角色不可用、模型上下文相同或运行时路由无法核实时，交付记录 SHALL 如实标注 `UNVERIFIED` 或独立性限制。

#### Scenario: Slim active preset supplies implementation and review models
- **WHEN** 正式工作从启用 OMO-Slim 的 OpenCode 主会话执行
- **THEN** 实施任务委派给 Slim `fixer`、独立审查委派给 Slim `oracle`，由当前 preset 决定其模型；受管 workflow agent 不固定具体模型 ID

#### Scenario: Slim specialist role unavailable
- **WHEN** 当前会话未由 OMO-Slim 调度或对应 specialist 角色不可调用
- **THEN** 工作流不得声称角色模型路由已生效；须标注 `UNVERIFIED`，并说明直接 OpenCode agent 会继承当前会话模型

### Requirement: 按任务形状选择专长
主代理 SHALL 负责调度、整合和证据，按需选择 explore、research、implement、consult 和 review；SHALL NOT 强制每个任务经过全部角色。已掌握上下文的小改动和上下文密集文档 MAY 直接完成。正式实施及最终独立审查 SHALL 保留 OpenSpec 上下文包与共享质量门槛。

#### Scenario: 先探索再决定实施
- **WHEN** 用户仍在调查且尚未授权正式实施
- **THEN** 可进行范围受限的只读探索，不强制创建 change，不把探索授权扩大为实施授权

### Requirement: Pi 激活与独立审查边界
Pi 适配 SHALL 区分工具激活、角色发现和实际委派，以当前 runtime schema 为准，使用 fresh context 和受限输出；异步任务 SHALL 通过完成事件续接而非模型轮询。独立 reviewer 不可用时 SHALL 记录 `UNVERIFIED`，不得用主代理自审冒充。

#### Scenario: 仅存在 loader
- **WHEN** 当前仅有 `subagents_enable` 可调用
- **THEN** 激活后在下一轮检查工具，不把 loader 成功当作子代理完成

### Requirement: 原生角色安装不等于运行证明
安装器 SHALL 提供无固定模型的 Codex workflow TOML 角色和 Pi 原生共享 skill 入口，并保留用户自定义角色、模型及插件配置。doctor SHALL 区分已安装、静态发现条件和运行验证未知；SHALL NOT 以文件存在证明实际独立调用或跨模型。

#### Scenario: 静态安装通过但未运行
- **WHEN** 受管文件一致但尚无真实角色调用证据
- **THEN** 报告静态状态及运行 `UNVERIFIED`，不宣称端到端验证成功
