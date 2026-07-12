# ForgeFlow 开发生命周期

### 4.9 推荐开发流程

### Phase 0：Project Foundation

活动：

* 创建项目结构
* 保留初始架构草案
* 编写 Project Foundation Proposal
* 编写产品愿景文档
* 编写里程碑路线图文档
* 编写工程流程文档

产出：

* 项目方向清晰
* Milestone 1 和 MVP 已分离
* RFC 路线图已准备好
* 实现没有过早开始

### Phase 1：RFC 驱动的架构

活动：

* 编写 RFC-001 Agent Architecture
* 编写 RFC-002 State Model and Structured Contracts
* 编写 RFC-004 Sandbox and Security Governance
* 编写 RFC-007 DeerFlow Extension Strategy
* 在有用时并行起草 RFC-003 Tool and MCP Integration
* 在有用时并行起草 RFC-005 Observability and Trace Model
* 在有用时并行起草 RFC-006 Evaluation Framework

产出：

* 跨领域架构决策被明确记录
* 角色边界、state 边界、安全约束和 DeerFlow 集成策略被记录

### Phase 2：OpenSpec 功能规划

活动：

* 只为已有 RFC skeleton decisions 支撑的功能创建 OpenSpec 变更
* 从 Repository Context Service 作为第一个推荐功能开始
* 每个功能至少包含 `proposal.md`、`design.md` 和 `tasks.md`

产出：

* 功能范围已经准备好进入实现
* include / exclude 边界明确
* 编码前已经知道评估和安全预期

### Phase 3：实现

活动：

* 先写测试或测试计划
* 实现 OpenSpec 描述的最小功能
* 实现过程中避免扩大范围
* 随着工作推进更新 OpenSpec tasks

产出：

* 实现与已同意的功能范围一致
* 代码、测试和文档仍然可以追溯到 spec

### Phase 4：评估与审查

活动：

* 使用受控 fixtures 进行第一版评估
* 记录结果、失败模式、范围蔓延和安全问题
* 必要时更新 RFC、ADR 或 retrospectives

产出：

* 行为被测量，而不是被假设
* 风险和失败可见
* 学习结果反馈到架构和流程中

### Phase 5：复盘与迭代

活动：

* 每个完成的里程碑之后编写 retrospective
* 不要把临时实现细节写回 `vision.md`
* 通过 RFC 或 ADR 记录重大方向变化

产出：

* 项目有意识地改进
* 未来贡献者能够理解为什么发生了这些变化
## 11. Definition of Ready

一个功能只有在以下条件满足时，才准备好实现：

* `vision.md` 清晰定义当前阶段边界
* `milestones.md` 标识当前里程碑
* 影响架构的设计已经有 RFC
* 该功能已经有 OpenSpec 变更
* includes 和 excludes 明确
* 安全约束明确
* 评估方法明确
* 没有阻塞实现的重大未解架构问题

对于 Milestone 1，这意味着 Repository Context Service 必须保持为确定性基础切片，而不是补丁生成或 PR 自动化工作流。

## 12. Definition of Done

一个功能在以下条件满足时才算完成：

* 实现满足 OpenSpec tasks
* 测试通过
* evaluation fixture 已更新或已执行
* trace / run summary 要求已满足
* 文档已更新
* 新的架构决策已记录在 ADR 中，或通过 RFC 更新记录
* 如果里程碑完成，已创建 milestone retrospective

Done 意味着该功能已经实现、测试、评估、记录，并且可以追溯。

## 13. 范围控制规则

这些规则适用于 ForgeFlow 早期开发：

* 不要将 Milestone 1 扩展成完整 MVP。
* Repository Context Service v1 不生成补丁。
* 第一版不包含 Jira、Slack、自动 merge、多仓库支持或复杂权限系统。
* 第一版评估不从 SWE-bench 开始。
* 安全护栏不能完全推迟到 Phase 2。
* 在早期版本中，Memory 不会自动写入，除非人类明确确认这些内容是稳定的工程知识。

如果某个拟议变更违反其中一条规则，应推迟该变更，或要求先编写 RFC 再继续。
