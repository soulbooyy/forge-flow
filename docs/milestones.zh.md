# ForgeFlow 里程碑

## 1. 目的

本文档定义 ForgeFlow 的分阶段开发路线图。

它的目的是：

* 定义 ForgeFlow 的分阶段开发路径
* 区分项目基础、基础切片、垂直 MVP 和后续扩展
* 防止范围蔓延
* 明确每个里程碑的目标、范围、排除项和退出标准
* 为 RFC、OpenSpec 变更、实现工作和评估提供清晰的阶段边界

这不是一份实现设计文档。它不定义 API、类或具体服务实现。

## 2. 里程碑理念

ForgeFlow 应该通过有意设计、可审查的阶段逐步推进。

里程碑原则：

* 先打基础，再做自动化。
* 先构建横向能力，再做完整垂直自动化。
* 刻意保持 Milestone 1 足够小。
* 将完整 Draft PR 工作流视为后续 MVP，而不是第一个功能。
* 使用 RFC 做架构决策。
* 使用 OpenSpec 做功能级实现规格。
* 从一开始就纳入安全和评估。
* 对仓库事实，优先使用确定性服务。
* 优先使用结构化契约，而不是自由形式的 Agent 输出。

长期愿景是自主软件维护。第一批实现步骤必须小于这个愿景。

## 3. 里程碑概览

| 里程碑         | 名称                                     | 目标                                           | 主要交付物                                                            | 状态  | 依赖                                                 |
| ----------- | -------------------------------------- | -------------------------------------------- | ---------------------------------------------------------------- | --- | -------------------------------------------------- |
| Milestone 0 | Project Foundation                     | 建立项目边界、文档体系、RFC 路线图和范围修正。                    | 基础文档和 RFC 路线图。                                                   | 进行中 | 初始架构草案                                             |
| Milestone 1 | Repository Context Foundation Slice    | 构建第一个确定性的仓库上下文能力。                            | Repository Context Service OpenSpec 和 `RepositoryContextResult`。 | 已完成 | Milestone 0，RFC-001/002/004/007 skeleton decisions |
| Milestone 2 | Structured PatchProposal Slice         | 从仓库上下文中产生有证据支撑的补丁意图。                         | `PatchProposal` 契约和受治理的补丁方案流程。                                   | 计划中 | Milestone 1，RFC-002/003/004                        |
| Milestone 3 | Validation and Review Slice            | 验证补丁并产生阻塞级审查结果。                              | `ValidationResult`、`ReviewResult`、有边界的重试策略。                      | 计划中 | Milestone 2，RFC-004/005/006                        |
| Milestone 4 | Draft PR MVP Vertical Slice            | 完成第一个从 GitHub Issue 到 Draft PR 的 MVP 路径。     | 从 fixture 或测试仓库中生成受控草稿 PR。                                       | 计划中 | Milestone 3，GitHub/tool policy decisions           |
| Milestone 5 | Evaluation and Observability Hardening | 强化 trace、run summary、redaction 和 evaluation。 | 可靠的评估指标和产品级 run summaries。                                       | 计划中 | Milestone 4                                        |
| Milestone 6 | Enterprise Integrations and Scaling    | 在核心循环稳定后，添加可选企业集成。                           | 策略门控的集成和可扩展部署方向。                                                 | 未来  | Milestone 5                                        |

## 4. Milestone 0：Project Foundation

目标：建立项目边界、文档工作流、开发流程和 RFC 路线图。

范围：

* 初始化仓库结构
* 保留初始架构草案
* 创建 Project Foundation Proposal
* 创建 `vision.md`
* 创建 `milestones.md`
* 创建 `development-process.md`
* 定义 RFC 路线图
* 明确 DeerFlow 集成策略
* 运行 Grill-Me 架构审查
* 记录第一轮范围修正

排除项：

* 生产实现
* Agent 类
* OpenSpec 功能实现
* Repository Context Service 代码
* 沙箱执行代码
* PR 自动化

退出标准：

* Project Foundation Proposal 已存在
* `vision.md` 已存在
* `milestones.md` 已存在
* `development-process.md` 已存在
* 初始架构草案已保留
* RFC 路线图已记录
* Milestone 1 和 MVP 已清晰分离
* 当前文档已提交到 Git

## 5. Milestone 1：Repository Context Foundation Slice

Milestone 1 不是完整 MVP。

状态：已完成。实现和 closure 证据见 [Milestone 1 进度索引](milestones/m1-repository-context-foundation/progress.md)
和 [复盘](../retrospectives/milestone-1-repository-context-foundation.md)。

目标：实现 ForgeFlow 的第一个确定性基础能力：Repository Context Service。

该服务为后续 `PatchProposal`、Validation、Review 和 Draft PR 工作流提供有证据支撑的仓库上下文。

范围：

* 接收 repo workspace 输入
* 接收 query 和可选 issue text
* 执行文件搜索
* 执行文本搜索
* 返回证据引用
* 返回相关文件
* 从项目配置或约定中返回简单测试命令提示
* 生成 `RepositoryContextResult`
* 记录最小 trace / run summary
* 支持小型受控评估 fixtures

排除项：

* 补丁生成
* 代码编辑
* 测试执行
* draft PR 创建
* 相似 issue 检索
* 完整依赖图
* GitHub issue / PR 历史摄取
* 大规模 embedding 索引
* 多仓库支持
* 自动 memory 写入
* 语言特定的深度静态分析

退出标准：

* `RepositoryContextResult` 契约已指定
* Repository Context Service 的 OpenSpec 变更已存在
* 最小文件/文本搜索可以工作
* 返回证据引用
* 受控评估 fixtures 已存在
* 范围排除项已记录
* 安全假设已记录
* 该里程碑中没有引入补丁生成

## 6. Milestone 2：Structured PatchProposal Slice

目标：使用 Repository Context 生成结构化 `PatchProposal`，表示后续自动修复工作流中的最小代码变更意图。

范围：

* 定义 `PatchProposal` 契约
* 使用 `RepositoryContextResult` 作为输入
* 生成根因假设
* 生成修复策略
* 识别候选变更文件
* 生成结构化补丁意图
* 可选：通过受治理工具在沙箱中生成 diff
* 强制执行补丁边界策略
* 记录风险标记和证据引用

排除项：

* 完整自主修复循环
* PR 创建
* 自动 merge
* 多轮验证修复
* 大规模重构
* 未经批准修改敏感文件

退出标准：

* `PatchProposal` 契约已记录
* 补丁方案有证据支撑
* 变更文件有边界
* 已产生风险标记
* 已强制执行补丁边界策略
* 存在基础测试或 fixtures

## 7. Milestone 3：Validation and Review Slice

目标：引入 `ValidationResult` 和 `ReviewResult`，使 ForgeFlow 能够测试补丁、解释失败，并执行阻塞级审查。

范围：

* 定义 `ValidationResult` 契约
* 定义 `ReviewResult` 契约
* 运行用户指定或推荐的测试命令
* 解析测试结果
* 解释验证失败
* 产生风险标记
* 检测阻塞级审查问题
* 强制执行有边界的重试策略
* 在达到重试限制时升级给人工审查

排除项：

* 无限修复循环
* 完整 CI 集成
* 自动生产部署
* 自动 merge
* 广泛的纯风格代码审查评论

退出标准：

* `ValidationResult` 和 `ReviewResult` 已记录
* Validation 不直接修复失败
* repair loop 由 workflow graph 控制
* 已强制执行重试限制
* Review 只执行阻塞级审查
* 人工批准门控已记录

## 8. Milestone 4：Draft PR MVP Vertical Slice

目标：完成第一个真正的垂直 MVP：

```text
GitHub Issue
  -> Sandbox
  -> Repository Context
  -> PatchProposal
  -> Validation
  -> Review
  -> Draft PR
```

范围：

* GitHub Issue 输入
* 沙箱 workspace 设置
* 仓库上下文检索
* `PatchProposal` 生成
* 受治理的代码修改
* 测试验证
* 阻塞级审查
* draft PR 创建
* PR body 从结构化契约生成
* 针对高风险操作的人工批准门控
* 可追踪的 run summary

排除项：

* 自动 merge
* 自动部署
* Jira 集成
* Slack 审批
* 多仓库编排
* 复杂企业权限系统
* 完整 SWE-bench 支持

退出标准：

* 一个 GitHub Issue 可以在受控 fixture 或测试仓库中生成 draft PR
* PR body 包含根因、变更、验证、风险和 trace summary
* 高风险操作被阻止或需要批准
* 验证重试有边界
* run summary 被持久化
* evaluation result 被记录

## 9. Milestone 5：Evaluation and Observability Hardening

目标：强化 evaluation、trace、run summary、安全脱敏和审计能力。

范围：

* 扩展受控 fixtures
* 跟踪 context retrieval precision
* 跟踪 test recommendation usefulness
* 跟踪 patch size 和 changed files
* 跟踪 validation determinism
* 跟踪 run summary completeness
* 为 prompts、tool outputs、logs 和 diffs 添加 redaction policy
* 改进 observability dashboard 或 trace format
* 添加 cost 和 retry metrics

排除项：

* 大规模企业部署
* 将完整 SWE-bench 自动化作为强制基线
* 生产 SRE 级监控
* 复杂分析平台

退出标准：

* 评估指标被稳定记录
* redaction policy 已记录并应用
* run summaries 对 PR review 和 retrospectives 有用
* cost、retry 和 failure metrics 可用
* 已记录已知失败模式

## 10. Milestone 6：Enterprise Integrations and Scaling

目标：只有在核心循环稳定后，才扩展企业集成和规模化能力。

可能范围：

* Jira 集成
* Slack 或 IM 审批
* 更深入的 GitHub Actions 集成
* 相似 issue 检索
* Git / PR 历史检索
* 多仓库支持
* 需要人工批准的 repository memory
* 基于角色的权限模型
* 部署在隔离 worker 基础设施中
* 可选 SWE-bench / SWE-bench Verified 评估

排除项：

* 任何破坏安全边界的内容
* 没有明确批准策略的自动 merge
* 将源码或 secrets 存入 memory
* 无边界的自主修复

退出标准：

* 企业集成是可选的，并由策略门控
* 安全模型可以随集成规模扩展
* 评估覆盖离线 fixtures 和在线使用
* memory 写入需要清晰的批准策略
* 系统仍然可审计、可治理

## 11. 里程碑与 RFC 的关系

Milestones 和 RFC 承担不同职责。

* Milestones 定义交付阶段。
* RFC 定义架构决策。
* OpenSpec 变更定义功能实现细节。

Milestone 0 产出 RFC 路线图。

必需 RFC：

* RFC-001 支持 Agent Architecture。
* RFC-002 支持 State Model and Structured Contracts。
* RFC-003 支持 Tool and MCP Integration。
* RFC-004 支持 Sandbox and Security Governance。
* RFC-005 支持 Observability and Trace Model。
* RFC-006 支持 Evaluation Framework。
* RFC-007 支持 DeerFlow Extension Strategy。

当某个决策影响多个里程碑、契约、安全姿态、运行时集成或评估时，应在实现前编写 RFC。

## 12. 里程碑与 OpenSpec 的关系

OpenSpec 不应该一次性用于整个 MVP。

每个里程碑可以包含一个或多个 OpenSpec 变更。每个 OpenSpec 变更都应该描述一个聚焦功能，并包含：

* `proposal.md`
* `design.md`
* `tasks.md`

第一个 OpenSpec 变更应该是 Repository Context Service。

只有在相关 RFC skeleton decisions 已存在后，才应该创建 OpenSpec。对于 Repository Context Service，相关 skeleton decisions 是：

* RFC-001 Agent Architecture
* RFC-002 State Model and Structured Contracts
* RFC-004 Sandbox and Security Governance
* RFC-007 DeerFlow Extension Strategy

RFC-003、RFC-005 和 RFC-006 可以并行起草，并被第一个 OpenSpec 引用，但它们不需要在 Repository Context Service spec 开始前完全完成。

## 13. 范围控制规则

这些规则用于保护 ForgeFlow，防止将长期愿景变成第一步实现。

* Milestone 1 不得扩展为补丁生成。
* Repository Context Service 在 Milestone 1 中必须保持确定性。
* Draft PR 在 Milestone 4 之前不是必需项。
* 相似 issue 检索在 Milestone 6 之前不是必需项。
* SWE-bench 不是第一个评估里程碑所必需的。
* 自动 merge 不属于 MVP 范围。
* Jira 和 Slack 不属于 MVP 范围。
* Memory 自动写入不属于早期里程碑范围。
* 安全护栏不能完全推迟到后续阶段。

任何违反这些规则的提案都应该被拒绝、推迟，或者写成明确的 RFC，并包含清晰的权衡讨论。

## 14. 里程碑退出检查清单

在宣布任何里程碑完成前，使用以下检查清单：

* [ ] 范围已完成
* [ ] 排除项得到遵守
* [ ] 相关 RFC 已更新
* [ ] OpenSpec tasks 已更新
* [ ] 测试或评估 fixtures 已更新
* [ ] 安全影响已审查
* [ ] 可观测性要求已审查
* [ ] 文档已更新
* [ ] Git 历史包含有意义的提交
* [ ] 如果里程碑完成，已创建 retrospective

## 15. 当前状态

当前里程碑：

```text
Milestone 0: Project Foundation
Status: In progress
```

下一步：

* finalize `vision.md`
* finalize `milestones.md`
* finalize `development-process.md`
* create RFC-001 Agent Architecture
* run Grill-Me review on RFC-001
* proceed to RFC-002, RFC-004, and RFC-007
* only after that, create the first OpenSpec change for Repository Context Service
