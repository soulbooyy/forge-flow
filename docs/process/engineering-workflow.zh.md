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
| `docs/product/vision.md`                      | 项目愿景、目标用户、长期方向、MVP 边界、Milestone 1 边界和核心原则。                                                                                           |
| `docs/product/roadmap/milestones.md`                  | 阶段规划。定义 Milestone 1、MVP、后续阶段、范围排除项和退出标准。                                                                                             |
| `docs/architecture/foundation/project-foundation-proposal.md` | RFC 前的基础设计提案。它是早期设计输入，而不是最终架构规范。                                                                                                     |
| `rfcs/`                               | 重大架构决策，例如 Agent Architecture、State Model、Tool/MCP Integration、Sandbox Governance、Evaluation Framework 和 DeerFlow Extension Strategy。 |
| `openspec/` 或 `specs/changes/`        | 功能级规格，例如 Repository Context Service、PatchProposal 生成、Validation 工作流、ReviewResult 生成和 Draft PR 创建。                                    |
| `adr/`                                | 已接受的架构决策记录，通常在 RFC 讨论达成决策后创建。                                                                                                        |
| `docs/milestones/<milestone-slug>/implementation-plan.md` | Canonical implementation sequence、文件级工作、依赖、TDD 步骤和 Phase 验收条件。                                                                              |
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
