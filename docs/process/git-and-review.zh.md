# ForgeFlow Git 与审查实践

## 1. 什么时候使用 Grill-Me

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

## 2. 什么时候使用 RFC

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

## 3. 什么时候使用 OpenSpec

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

## 4. 什么时候使用 ADR

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

## 5. Git 工作流

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

## 6. 分支建议

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

对于属于某个 Milestone 的 implementation work，必须使用
`implementation-execution.md` 定义的更具体的 Milestone 范围命名：

```text
feature/m<NUMBER>-<milestone-topic-slug>
```

该 branch 在 Milestone closure 前持续分配给同一个 worktree；单个 Phase 使用
focused commit，而不是创建新的 branch。

只有在相关文档、spec、实现、测试或审查预期满足后才合并。
