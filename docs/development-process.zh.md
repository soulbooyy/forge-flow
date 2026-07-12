# ForgeFlow 开发流程

## 1. 目的

本文档定义 ForgeFlow 的工程开发流程。

它的目的是：

* 定义 ForgeFlow 如何从愿景演进到 RFC、OpenSpec 变更、实现、测试、评估和复盘
* 明确什么时候使用 RFC、OpenSpec、ADR、Grill-Me 审查和复盘
* 防止在架构边界尚未清晰前过早编码
* 保持文档、代码、测试和评估同步演进

ForgeFlow 是一个基于 DeerFlow 和 LangGraph 构建的企业级自主软件工程 Agent 平台。它不应该变成一个玩具级代码助手。它的开发流程应该从一开始就保留治理、可观测性、评估和人工批准边界。

## 2. 开发原则

ForgeFlow 开发遵循以下原则：

* 先有愿景，再有架构。
* 重大架构变更前先写 RFC。
* 功能实现前先写 OpenSpec。
* 生产行为前先写测试。
* 从第一天开始评估。
* 自动化之前先有安全与治理。
* 高风险操作需要人工批准。
* 仓库事实来自确定性服务。
* 结构化契约优先于自由形式输出。
* Git 历史是项目演进的事实来源。

这些原则尤其适用于项目仍处于基础阶段和 pre-MVP 阶段时。

## 3. 文档类型与职责

| 文档                                    | 职责                                                                                                                                   |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `docs/vision.md`                      | 项目愿景、目标用户、长期方向、MVP 边界、Milestone 1 边界和核心原则。                                                                                           |
| `docs/milestones.md`                  | 阶段规划。定义 Milestone 1、MVP、后续阶段、范围排除项和退出标准。                                                                                             |
| `docs/project-foundation-proposal.md` | RFC 前的基础设计提案。它是早期设计输入，而不是最终架构规范。                                                                                                     |
| `rfcs/`                               | 重大架构决策，例如 Agent Architecture、State Model、Tool/MCP Integration、Sandbox Governance、Evaluation Framework 和 DeerFlow Extension Strategy。 |
| `openspec/` 或 `specs/changes/`        | 功能级规格，例如 Repository Context Service、PatchProposal 生成、Validation 工作流、ReviewResult 生成和 Draft PR 创建。                                    |
| `adr/`                                | 已接受的架构决策记录，通常在 RFC 讨论达成决策后创建。                                                                                                        |
| `docs/implementation-plans/`          | Canonical implementation sequence、文件级工作、依赖、TDD 步骤和 Phase 验收条件。                                                                              |
| `docs/milestones/<milestone-slug>/`   | Milestone 状态索引和正式的 Phase Completion Record。                                                                                                      |
| `retrospectives/`                     | 里程碑复盘，记录哪些有效、哪些失败、返工原因和后续改进。                                                                                                         |
| `README.md`                           | 项目入口。它应该只包含稳定的高层信息，以及指向当前文档的导航。                                                                                                      |

文档应该被视为产品的一部分，而不是可选的说明文字。

## 4. ForgeFlow Engineering Workflow

ForgeFlow 遵循分阶段的工程工作流：

```text
Vision
-> Architecture
-> Specification
-> Planning
-> Implementation
-> Verification
```

该工作流适用于每一个 Milestone。以下章节共同定义一条连续流程；后续章节提供各阶段的详细规则。

### 4.1 Architecture

Architecture 以项目 Vision 为输入，并产出 RFC 和 ADR。RFC 定义 architecture boundaries、system responsibilities、trade-offs 和 long-term technical direction。ADR 记录已接受的架构决策、被否决的替代方案和重要 trade-offs。

在必要的架构决策尚未明确前，不得开始 Implementation。

### 4.2 Specification

Specification 以相关 RFC 和已接受 ADR 为输入，并产出 OpenSpec change。OpenSpec 是 feature contract 的权威来源，必须包括 proposal、design、tasks 和 feature specifications。每个 change 必须明确 scope、acceptance criteria、non-goals 和 constraints。

### 4.3 Grill-Me Design Review

重要 feature 在 Planning 前必须通过 Grill-Me 设计质询。Grill-Me 用于发现 hidden assumptions、unclear boundaries、scope creep 和 architecture violations。它不修改架构决策；最终决策仍由 RFC、ADR 和 OpenSpec 记录。

### 4.4 Planning

Planning 以已接受的 OpenSpec change 为输入，并产出 canonical Implementation Plan。该 plan 是执行顺序的唯一权威来源，必须定义 milestone scope、phase ordering、dependencies、expected file changes、TDD strategy 和 phase acceptance criteria。

每个即将进入 Implementation 的 Milestone，必须先使用 Superpowers 或等价的 AI-assisted workflow 生成 draft implementation plan。写入 canonical plan 前，必须将该 draft 与已接受 OpenSpec、相关 RFC 和已接受 ADR 对照审查。审查必须协调 phase boundaries、dependencies、scope exclusions、TDD strategy 和 acceptance criteria；当 draft 与仓库权威文档冲突时，以仓库权威文档为准，并在 canonical plan 中解决冲突。

最终的 canonical plan 可以吸收 draft 中有价值的执行细节，但它是后续 Phase 唯一可视为权威的 plan。draft 可以作为 non-canonical planning evidence 保留，但不得形成第二份需要同步的 plan。

Implementation Phase 必须来自 canonical plan。聊天提示词不得重新定义 Phase 的 scope、interface、file list 或 acceptance criteria。

### 4.5 Implementation

Implementation 使用 Lightweight Implementation Execution，并对每个 Phase 遵循以下顺序：

```text
Read Phase Requirement
-> Write Tests (RED)
-> Implement Minimal Solution (GREEN)
-> Refactor
-> Run Verification
-> Commit
-> Create Phase Completion Record
-> Update Milestone Progress
```

### 4.6 Verification

每个完成的 Phase 都必须验证 tests passed、scope respected、Git diff 已审查且 documentation 已更新。提交前至少运行 targeted tests、cumulative implemented tests、`git diff --check` 和 `git status`。

### 4.7 Documentation Authority Hierarchy

```text
Vision
-> RFC
-> ADR
-> OpenSpec
-> Implementation Plan
-> Phase Completion Record
-> Milestone Progress
```

- Vision 说明为什么做。
- RFC 定义架构。
- ADR 记录已确定的架构选择。
- OpenSpec 定义 feature contract。
- Implementation Plan 定义如何实施。
- Phase Completion Record 记录一个 Phase 实际完成什么。
- Milestone Progress 记录 Milestone 当前在哪里。

### 4.8 AI-assisted Development Tools

Superpowers 和其他 AI-assisted development tools 是执行辅助工具。它们可以用于 task decomposition、implementation planning 或 review assistance，但不是权威来源。它们不得定义 architecture、requirements 或 acceptance criteria。仓库文档仍是 source of truth。

AI 生成的 draft plan 是 Planning 输入，不替代 canonical Implementation Plan。它的作用是在 canonical plan 编写和审查前提高完整性与可执行性。

### 4.9 推荐开发流程

### Phase 0：Project Foundation

活动：

* 创建项目结构
* 保留初始架构草案
* 编写 Project Foundation Proposal
* 编写 `vision.md`
* 编写 `milestones.md`
* 编写 `development-process.md`

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

## 5. 什么时候使用 Grill-Me

Grill-Me 是一种设计审查机制。它应该用于压力测试假设、暴露范围蔓延，并强化架构边界。

使用 Grill-Me 的场景：

* Project Foundation Proposal 起草后
* 每个重大 RFC 草案准备好后
* OpenSpec 功能范围不清晰时
* 出现范围蔓延或架构边界混乱时

不要使用 Grill-Me 的场景：

* 每个小函数
* 范围已经清晰的简单实现任务
* 替代测试
* 替代 RFC 或 OpenSpec 文档

模式：

* Report mode：生成一次性架构审查报告，包含关键问题、风险、范围削减和就绪检查。
* Interactive mode：一次只问一个问题，并在继续前等待回答。

Grill-Me 反馈应该被整合进相关文档，而不是只留在聊天记录中。

## 6. 什么时候使用 RFC

当决策影响架构、项目边界、安全、state、契约、运行时集成或评估时，使用 RFC。

RFC 适用于：

* 跨模块架构变更
* Agent 角色或工作流变更
* state 和 contract 设计
* 工具权限模型
* 沙箱安全模型
* 可观测性和评估设计
* DeerFlow 扩展策略

RFC 不适用于：

* 小型 bug fix
* 单个测试变更
* 文档措辞修改
* 不影响架构边界的本地实现细节

推荐 RFC 结构：

* Title
* Status
* Context
* Problem Statement
* Goals
* Non-goals
* Proposed Design
* Alternatives Considered
* Trade-offs
* Risks
* Open Questions
* Decision Summary

RFC 可以是 accepted、rejected、superseded 或 deferred。

## 7. 什么时候使用 OpenSpec

在实现前使用 OpenSpec 进行功能级规划。

适合 OpenSpec 的候选功能：

* Repository Context Service
* PatchProposal generation
* Validation workflow
* ReviewResult generation
* Draft PR creation

每个 OpenSpec 变更至少应包含：

* `proposal.md`
* `design.md`
* `tasks.md`

OpenSpec 不应用于：

* 替代 `vision.md`
* 替代 RFC
* 讨论尚未解决的大型架构问题
* 用一个变更覆盖整个 GitHub Issue 到 Draft PR MVP

第一个 OpenSpec 变更应该是 Repository Context Service，并且只应在相关 RFC skeleton decisions 已存在后开始。

## 8. 什么时候使用 ADR

使用 ADR 记录已接受的技术决策。

ADR 主题示例：

* 使用 DeerFlow 作为上游参考。
* 在早期阶段将 agents 视为 workflow roles。
* 使用确定性的 Repository Context Service。
* 高风险操作需要人工批准。
* 从受控 fixtures 开始评估，而不是从 SWE-bench 开始。

ADR 应该简短且持久。

推荐 ADR 结构：

* Context
* Decision
* Consequences
* Related RFCs

ADR 不应该重新打开完整讨论。完整讨论应该放在 RFC 中。

## 9. Git 工作流

使用清晰、具体的提交信息。

推荐示例：

```text
docs: add project vision
docs: define milestones and development process
docs(rfc): add agent architecture proposal
docs(rfc): refine state model after review
docs(openspec): add repository context service proposal
feat(context): implement repository file search
test(context): add repository context fixtures
chore: add DeerFlow upstream reference
```

指南：

* 文档变更必须提交
* RFC、OpenSpec 和 ADR 变更应该能够追溯到相关代码变更
* 避免使用 `update`、`fix stuff` 或 `misc changes` 这类模糊提交信息
* 保持提交足够聚焦，使项目演进能够从 Git 历史中被理解

## 10. 分支建议

使用适合个人项目、并且未来可能开源的轻量级分支策略。

建议：

* 保持 `main` 稳定
* 为文档、RFC、spec、feature 和 fix 使用短生命周期分支
* 除非项目规模之后需要，否则避免重量级 Git Flow

分支名称示例：

```text
docs/rfc-001-agent-architecture
docs/openspec-repository-context
feature/repository-context-service
fix/...
```

只有在相关文档、spec、实现、测试或审查预期满足后才合并。

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

## 14. 轻量实现执行

该模式适用于 ForgeFlow 每个 Milestone 中范围明确、已接受的实现阶段。它保留 TDD、范围控制、聚焦提交、正式完成记录和持久进度，但不将 AI 执行过程产物视为长期工程文档。

### 14.1 权威输入

开始一个阶段前，必须阅读当前 feature specification、相关 RFC、已接受 ADR、canonical implementation plan 和 milestone `progress.md`。聊天提示词可以提供上下文，但不能定义本阶段的接口、文件清单、验收标准或范围。

发生冲突时，权威顺序为：

1. OpenSpec 或已接受 feature specification：需求、验收标准和排除项。
2. 已接受 ADR：有约束力的架构决策。
3. RFC：架构边界和延期决策。
4. Canonical implementation plan：实施顺序和任务细节。
5. Milestone progress：仅记录执行状态。

这些来源发生冲突或无法识别安全的下一阶段时，必须停止实现并报告冲突。不得自行创造架构决策或静默修改权威来源。

### 14.2 阶段识别

根据 canonical implementation plan 和 milestone `progress.md` 最后完成状态识别下一阶段。执行编号与 canonical plan 不一致时，必须在实现开始前完成 reconciliation。

### 14.3 测试驱动开发

每个阶段遵循 RED -> GREEN -> REFACTOR：

- 先增加或修改测试；
- 确认测试因为能力缺失或行为错误而失败；
- 实现满足当前阶段的最小代码；
- 运行 targeted tests，再运行完整已实现 suite；
- 仅在 GREEN 后进行小范围、阶段内重构。

在完整实现之后才补测试，不能替代上述顺序。

### 14.4 范围控制

每次只执行一个 canonical-plan phase。禁止为未来阶段增加抽象、修改无关模块或扩大功能范围。权威文档缺失或冲突是停止条件，不是自行补齐缺口的许可。

### 14.5 Git 和提交策略

使用该 Milestone 指定的 branch 和 worktree。除非 canonical plan 或已接受的 workflow decision 明确要求，否则不得为每个 Phase 创建新的 branch 或 worktree。

每个 Phase 创建一个聚焦 commit。提交前至少运行 targeted tests、完整已实现 test suite、`git diff --check` 和 `git status --short`，并检查生成文件与无关修改。

### 14.6 审查策略

默认轻量审查为当前 diff、通过的测试和范围边界的 self-review。默认不生成 subagent brief、review diff、rereview diff 或长篇 checkpoint report。

当修改 feature contract、安全边界、canonical identity algorithm、外部依赖或跨平台安全行为；偏离 canonical plan；或用户明确要求 review 时，必须升级为独立审查。

### 14.7 Phase Completion Record 和进度索引

每个 Milestone 的每一个实现 Phase 都必须在
`docs/milestones/<milestone-slug>/phase-<number>-<phase-name>.md`
保留一份正式的 Phase Completion Record。文件名必须从已完成 reconciliation 的
canonical implementation plan Phase 名称转换为稳定的 kebab-case；已存在的
Completion Record 文件名应保持不变。不得根据聊天提示词为后续 Phase 命名。

所有 Phase Completion Record 必须使用完全相同的模板。任何后续 Phase 都不得使用
简化版或不同结构：

```text
# Phase X: <Phase Name>

## 1. Goal
## 2. Scope
### Included
### Excluded
## 3. Changed Files
## 4. Implementation
## 5. Design Decisions
## 6. TDD and Tests
## 7. Important Fixes and Edge Cases
## 8. Commit
## 9. Acceptance
## 10. Scope Boundary Confirmation
## 11. Follow-up
```

`Changed Files` 使用 `File | Change | Purpose` 表格。`TDD and Tests` 必须
记录 RED、GREEN、必要的重构或修复迭代、命令、targeted result 和 cumulative-suite
result。该记录只保留已经完成的工程事实，不包含 agent dispatch、review diff 正文或
临时调试叙述。

每个 Phase commit 后，必须同时创建或更新对应的 Phase Completion Record 和
milestone `progress.md`。Completion Record 承担该 Phase 的详细记录；`progress.md`
是简洁的 Milestone 索引，只记录 Phase 状态、commit、文档链接、当前阶段、下一个
未完成 Phase 和 Milestone 级 reconciliation item。两者都不得重新定义需求、架构或
实施顺序。

`progress.md` 不替代 Phase Completion Record，不记录详细 implementation，也不定义
requirements 或 architecture。

默认不生成 Superpowers brief、review diff、rereview diff 或 agent execution report。
新的架构决策进入 ADR，需求变化进入 OpenSpec，实施顺序变化进入 canonical
implementation plan。

完成 Completion Record 和 progress 索引更新后，输出简短总结并停止等待用户确认。
不得自动进入下一阶段。

### 14.8 翻译策略

英文流程文档是 canonical。既有 `.zh.md` 流程文档是稳定、持久流程规则的维护性翻译。滚动 progress 和临时执行产物默认不创建翻译。
