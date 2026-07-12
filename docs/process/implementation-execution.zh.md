# ForgeFlow 实现执行

## 1. 轻量实现执行

该模式适用于 ForgeFlow 每个 Milestone 中范围明确、已接受的实现阶段。它保留 TDD、范围控制、聚焦提交、正式完成记录和持久进度，但不将 AI 执行过程产物视为长期工程文档。

### 1.1 权威输入

开始一个 Phase 前，必须阅读当前 feature specification、相关 RFC、已接受 ADR、canonical implementation plan 和 milestone `progress.md`。聊天提示词可以提供上下文，但不能定义本 Phase 的接口、文件清单、验收标准或范围。

发生冲突时，权威顺序为：

1. OpenSpec 或已接受 feature specification：需求、验收标准和排除项。
2. 已接受 ADR：有约束力的架构决策。
3. RFC：架构边界和延期决策。
4. Canonical implementation plan：实施顺序和任务细节。
5. Milestone progress：仅记录执行状态。

这些来源发生冲突或无法识别安全的下一阶段时，必须停止实现并报告冲突。不得自行创造架构决策或静默修改权威来源。

### 1.2 阶段识别

根据 canonical implementation plan 和 milestone `progress.md` 最后完成状态识别下一阶段。执行编号与 canonical plan 不一致时，必须在实现开始前完成 reconciliation。

### 1.3 测试驱动开发

每个阶段遵循 RED -> GREEN -> REFACTOR：

- 先增加或修改测试；
- 确认测试因为能力缺失或行为错误而失败；
- 实现满足当前阶段的最小代码；
- 运行 targeted tests，再运行完整已实现 suite；
- 仅在 GREEN 后进行小范围、阶段内重构。

在完整实现之后才补测试，不能替代上述顺序。

### 1.4 范围控制

每次只执行一个 canonical-plan phase。禁止为未来阶段增加抽象、修改无关模块或扩大功能范围。权威文档缺失或冲突是停止条件，不是自行补齐缺口的许可。

### 1.5 Git 和提交策略

使用该 Milestone 指定的 branch 和 worktree。除非 canonical plan 或已接受的 workflow decision 明确要求，否则不得为每个 Phase 创建新的 branch 或 worktree。

每个 Phase 创建一个聚焦 commit。提交前至少运行 targeted tests、完整已实现 test suite、`git diff --check` 和 `git status --short`，并检查生成文件与无关修改。

### 1.6 审查策略

默认轻量审查为当前 diff、通过的测试和范围边界的 self-review。默认不生成 subagent brief、review diff、rereview diff 或长篇 checkpoint report。

当修改 feature contract、安全边界、canonical identity algorithm、外部依赖或跨平台安全行为；偏离 canonical plan；或用户明确要求 review 时，必须升级为独立审查。
