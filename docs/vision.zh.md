# ForgeFlow 愿景

## 1. 项目概览

ForgeFlow 是一个基于 DeerFlow 和 LangGraph 构建的企业级自主软件工程 Agent 平台。

它不是一个简单的代码助手、聊天机器人，也不是一个玩具级 Agent demo。ForgeFlow 旨在以受控、可观测、可审查的方式，自动化软件维护生命周期中的部分环节。

这个平台围绕一个核心产品理念设计：AI Agent 系统不应该只是 在聊天窗口里给出代码建议。它应该帮助准备有证据支撑、可测试、可审计的工程变更，并交由人类审查和批准。

## 2. 问题陈述

企业软件维护成本很高，因为这项工作很少只是写几行代码那么简单。

常见问题包括：

* Bug 诊断需要阅读分散的代码、历史上下文、日志、测试和 issue 描述。
* 大型代码仓库让相关上下文难以快速定位。
* 验证需要知道应该运行哪些测试，以及如何解释失败。
* 准备高质量 Pull Request 需要根因分析、聚焦的 diff、测试证据和风险说明。
* 审查周期会因为理由不清、缺少验证和变更过大而变慢。
* 现有自动化工具通常缺乏治理能力、可观测性、可复现性和可解释性。

ForgeFlow 的存在，是为了在不移除人类对高风险工程决策控制权的前提下，降低软件维护负担。

## 3. 目标用户

ForgeFlow 面向负责维护生产软件系统的团队：

* 软件工程师
* 平台工程团队
* QA / 测试团队
* 工程效率团队
* DevOps / CI 维护者

第一批用户应该是需要针对低到中风险维护工作获得可靠自动化能力的工程师和平台团队，而不是需要完全自主生产部署的团队。

## 4. 产品愿景

ForgeFlow 的长期工作流是：

```text
GitHub Issue / 失败的 CI / 错误日志
  -> 任务分析
  -> 仓库理解
  -> Bug 诊断
  -> 代码补丁
  -> 验证
  -> 审查
  -> 草稿 Pull Request
  -> 人工批准
  -> 评估 / 记忆更新
```

长期目标是支持自主软件维护运行，并生成草稿 Pull Request，该 PR 应包含：

* 清晰的任务理解
* 仓库证据
* 根因分析
* 最小化代码变更
* 验证结果
* 风险审查
* 可追踪的运行摘要
* 人工批准门控
* 评估反馈
* 在适当情况下进行稳定的记忆更新

ForgeFlow 应该让 Agent 创建的 Pull Request 更容易被信任、检查、测试、拒绝或改进。

## 5. MVP 范围

完整的 MVP 垂直切片是：

```text
GitHub Issue
  -> Sandbox
  -> Repository Context
  -> PatchProposal
  -> Validation
  -> Review
  -> Draft PR
```

这个 MVP 被刻意限定在较窄范围内：

* 单仓库
* 优先支持 GitHub Issue 输入
* 沙箱执行
* 基于确定性服务的仓库上下文
* 结构化 `PatchProposal`
* 有边界的验证和重试行为
* 审查和风险标记
* 只输出草稿 PR

MVP 不是第一步实现内容。ForgeFlow 必须先建立一个基础切片，使仓库上下文可靠、可观测、可评估。

## 6. Milestone 1 范围

Milestone 1 是 Repository Context 基础切片。

它只聚焦于 Repository Context Service：一种确定性能力，用于为后续 Agent 工作流提供有证据支撑的仓库上下文。

Milestone 1 包含：

* repo workspace 输入
* issue text / query 输入
* 文件搜索
* 文本搜索
* 证据引用
* 简单测试命令提示
* 结构化 `RepositoryContextResult`

Milestone 1 不包含：

* 补丁生成
* 代码编辑
* PR 创建
* 相似 issue 检索
* 依赖图
* 自动 memory 写入

这个切片应该证明：在尝试自动补丁生成之前，ForgeFlow 能够将未来的 Agent 决策建立在可检查的仓库事实之上。

## 7. 核心原则

ForgeFlow 遵循以下原则：

* Agent 负责决策，工具负责执行。
* 仓库事实来自确定性服务，而不是自由形式的 Agent memory。
* 优先使用结构化契约，而不是自由形式输出。
* 执行优先在沙箱中进行。
* 高风险操作需要人工批准。
* 可观测性是产品能力，而不仅是内部日志。
* 评估从第一天开始。
* Memory 只存储稳定的工程知识。

这些原则是约束，而不是口号。它们的存在是为了在系统能力变强时，仍然保持系统可治理。

## 8. 非目标

第一阶段不包含：

* Jira 集成
* Slack 审批
* 自动 merge
* 自动部署
* 多仓库编排
* IDE 插件
* 复杂企业权限系统
* 将 SWE-bench 作为第一个评估目标

这些内容之后可能会变得相关，但它们不应该影响第一批实现里程碑的设计。

## 9. 成功标准

早期 ForgeFlow 的成功应该通过基础质量来衡量，而不是通过 demo 范围来衡量。

Milestone 1 成功的标准是 ForgeFlow 能够产出：

* 清晰的仓库上下文结果
* 有证据支撑的输出
* 有边界且可检查的范围
* 可追踪的运行摘要
* 受控沙箱和安全策略方向
* 小型受控评估 fixtures
* 通向后续 Draft PR MVP 的可信路径

MVP 成功的标准是：一个 GitHub Issue 能够产生一个草稿 Pull Request，并包含最小补丁、验证证据、审查结果、风险说明和人工批准边界。

## 10. 与 DeerFlow 的关系

DeerFlow 是 ForgeFlow 的上游框架和参考实现。

DeerFlow 预期提供以下基础能力：

* runtime 原语
* graph 执行
* thread state 原语
* tool orchestration
* checkpointing
* middleware hooks
* tracing hooks

ForgeFlow 拥有软件工程平台层：

* 软件工程领域 state
* 结构化契约
* 仓库上下文
* 沙箱治理
* 安全策略
* 补丁边界策略
* PR 工作流
* 评估框架
* 产品级运行摘要

ForgeFlow 应该基于 DeerFlow 构建，但不能变成一个浅层 fork 或简单改名版本。该平台应该保持自己的应用边界，并在合适的地方将 DeerFlow 作为运行时基础。
