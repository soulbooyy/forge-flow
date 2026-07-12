# ForgeFlow 文档注册表

本注册表说明 ForgeFlow 知识的位置，以及不同问题应由哪类文档作为权威来源。它是索引，不是第二份规格。

| 文档类别 | 位置 | 权威职责 | 更新触发条件 |
| --- | --- | --- | --- |
| 产品愿景 | `docs/product/` | 产品方向 | 意图或 MVP 边界变化 |
| 里程碑路线图 | `docs/product/roadmap/` | 里程碑范围和状态 | 里程碑规划或 closure |
| RFC | `rfcs/` | 架构边界和设计理由 | 架构提案或修订 |
| ADR | `adr/` | 已接受架构决策 | 决策接受或被替代 |
| OpenSpec | `openspec/` | 功能需求和验收标准 | 已接受功能变更 |
| 流程规则 | `docs/process/` | 工程工作流和文档治理 | 流程决策 |
| 实施计划 | `docs/milestones/<slug>/implementation-plan.md` | Phase 顺序和实施细节 | 已接受 planning reconciliation |
| Phase 记录 | `docs/milestones/<slug>/phases/` | 已完成 Phase 的工程事实 | 每个已接受 Phase |
| 里程碑进度 | `docs/milestones/<slug>/progress.md` | 当前执行状态 | 每个 Phase 或 closure |
| 复盘 | `retrospectives/` | 已完成里程碑的学习 | 里程碑 closure |
| 历史材料 | `docs/_history/` | 仅供非权威参考 | 归档迁移 |

稳定英文文档是 canonical。既有 `.zh.md` 文件是稳定产品、架构和流程规则的维护性翻译。滚动 progress、Phase record 和 retrospective 默认不翻译。

文档发生冲突时，按[工程工作流](process/engineering-workflow.zh.md)定义的权威顺序处理。
