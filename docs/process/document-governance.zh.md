# ForgeFlow 文档治理

## 1. 文档类型与职责

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

## 2. 文档权威层级

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


## 3. Milestone 文档结构

每个 Milestone 必须使用相同的文档结构。在该 Milestone 的 canonical
implementation plan 建立后创建对应目录：

```text
docs/milestones/
├── index.md
└── m<NUMBER>-<milestone-slug>/
    ├── index.md
    ├── implementation-plan.md
    ├── progress.md
    └── phases/
        ├── phase-1-<canonical-phase-name>.md
        ├── phase-2-<canonical-phase-name>.md
        └── ...
```

Milestone `index.md` 是入口，包含简洁的范围摘要、权威来源链接，以及对
plan、progress 索引和 Completion Record 的导航。`implementation-plan.md`
是该 Milestone 唯一的 canonical plan。`progress.md` 是 Milestone 级状态
索引。`phases/` 只包含实际已完成 Phase 的正式 Completion Record。

不得在 Milestone 目录中复制 OpenSpec、RFC、ADR 或 retrospective；应链接至
它们各自的权威记录。Milestone closure 后，retrospective 创建在
`retrospectives/m<NUMBER>-<milestone-slug>.md`。

## 4. Phase Completion Record 和进度索引

每个 Milestone 的每一个实现 Phase 都必须在 `docs/milestones/<milestone-slug>/phases/phase-<number>-<phase-name>.md` 保留一份正式的 Phase Completion Record。文件名必须从已完成 reconciliation 的 canonical implementation plan Phase 名称转换为稳定的 kebab-case；已存在的 Completion Record 文件名应保持不变。不得根据聊天提示词为后续 Phase 命名。

所有 Phase Completion Record 必须使用完全相同的模板。任何后续 Phase 都不得使用简化版或不同结构：

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

`Changed Files` 使用 `File | Change | Purpose` 表格。`TDD and Tests` 必须记录 RED、GREEN、必要的重构或修复迭代、命令、targeted result 和 cumulative-suite result。该记录只保留已经完成的工程事实，不包含 agent dispatch、review diff 正文或临时调试叙述。

每个 Phase commit 后，必须同时创建或更新对应的 Phase Completion Record 和 milestone `progress.md`。Completion Record 承担该 Phase 的详细记录；`progress.md` 是简洁的 Milestone 索引，只记录 Phase 状态、commit、文档链接、当前阶段、下一个未完成 Phase 和 Milestone 级 reconciliation item。两者都不得重新定义需求、架构或实施顺序。

`progress.md` 不替代 Phase Completion Record，不记录详细 implementation，也不定义 requirements 或 architecture。

默认不生成 Superpowers brief、review diff、rereview diff 或 agent execution report。新的架构决策进入 ADR，需求变化进入 OpenSpec，实施顺序变化进入 canonical implementation plan。

完成 Completion Record 和 progress 索引更新后，输出简短总结并停止等待用户确认。不得自动进入下一阶段。

## 5. 翻译策略

英文流程文档是 canonical。既有 `.zh.md` 流程文档是稳定、持久流程规则的维护性翻译。滚动 progress 和临时执行产物默认不创建翻译。
