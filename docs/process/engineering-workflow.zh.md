# ForgeFlow 工程工作流

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

## 3. ForgeFlow Engineering Workflow

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

### 3.1 Architecture

Architecture 以项目 Vision 为输入，并产出 RFC 和 ADR。RFC 定义 architecture boundaries、system responsibilities、trade-offs 和 long-term technical direction。ADR 记录已接受的架构决策、被否决的替代方案和重要 trade-offs。

在必要的架构决策尚未明确前，不得开始 Implementation。

### 3.2 Specification

Specification 以相关 RFC 和已接受 ADR 为输入，并产出 OpenSpec change。OpenSpec 是 feature contract 的权威来源，必须包括 proposal、design、tasks 和 feature specifications。每个 change 必须明确 scope、acceptance criteria、non-goals 和 constraints。

### 3.3 Grill-Me Design Review

重要 feature 在 Planning 前必须通过 Grill-Me 设计质询。Grill-Me 用于发现 hidden assumptions、unclear boundaries、scope creep 和 architecture violations。它不修改架构决策；最终决策仍由 RFC、ADR 和 OpenSpec 记录。

### 3.4 Planning

Planning 以已接受的 OpenSpec change 为输入，并产出 canonical Implementation Plan。该 plan 是执行顺序的唯一权威来源，必须定义 milestone scope、phase ordering、dependencies、expected file changes、TDD strategy 和 phase acceptance criteria。

每个即将进入 Implementation 的 Milestone，在 OpenSpec、相关 RFC 和已接受 ADR
完备后，必须先使用 Superpowers 的 `writing-plans` skill 生成详细的 draft
implementation plan。draft 必须保存为
`docs/_history/ai-assisted/implementation-plans/YYYY-MM-DD-<milestone-topic-slug>.md`，
其中 topic slug 不含目录使用的 `m<NUMBER>-` 前缀，
并明确 phase order、dependencies、expected file changes、TDD steps、verification
和 phase acceptance conditions。

写入 canonical plan 前，必须将该 draft 与已接受 OpenSpec、相关 RFC 和已接受 ADR
对照审查。审查必须协调 phase boundaries、dependencies、scope exclusions、TDD
strategy 和 acceptance criteria；当 draft 与仓库权威文档冲突时，以仓库权威文档
为准，并在 canonical plan 中解决冲突。

draft 与 canonical plan 都必须以 Phase 作为一级执行结构；Task 或 step 只能是
Phase 内部的工作项。最终的 canonical plan 可以吸收 draft 中有价值的执行细节，但它是后续 Phase
唯一可视为权威的 plan。AI-assisted draft 作为 `_history` 中的 non-canonical
planning evidence 保留，但不得形成第二份需要同步的 plan。

Implementation Phase 必须来自 canonical plan。聊天提示词不得重新定义 Phase 的 scope、interface、file list 或 acceptance criteria。

### 3.5 Implementation

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

### 3.6 Verification

每个完成的 Phase 都必须验证 tests passed、scope respected、Git diff 已审查且 documentation 已更新。提交前至少运行 targeted tests、cumulative implemented tests、`git diff --check` 和 `git status`。

### 3.7 AI-assisted Development Tools

Superpowers 和其他 AI-assisted development tools 是执行辅助工具。它们可以用于 task decomposition、implementation planning 或 review assistance，但不是权威来源。它们不得定义 architecture、requirements 或 acceptance criteria。仓库文档仍是 source of truth。

AI 生成的 draft plan 是 Planning 输入，不替代 canonical Implementation Plan。它的作用是在 canonical plan 编写和审查前提高完整性与可执行性。
