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
| `docs/_history/ai-assisted/implementation-plans/` | 在 architecture 和 specification 输入完备后创建、受版本控制的非 canonical 详细 AI-assisted draft plan。推荐 Superpowers `writing-plans`，但不强制使用。 |
| `docs/templates/` | 可复用的生命周期文档模板。它们固定文档职责和必需结构，不固定 Milestone 的具体结论。 |
| `openspec/templates/change/` | OpenSpec proposal、design、tasks 和 specification 文档的可复用 feature-change 模板。 |
| `docs/milestones/<milestone-directory-slug>/implementation-plan.md` | Canonical implementation sequence、文件级工作、依赖、TDD 步骤和 Phase 验收条件。                                                                              |
| `docs/milestones/<milestone-directory-slug>/`   | Milestone 状态索引和正式的 Phase Completion Record。                                                                                                      |
| `retrospectives/`                     | 里程碑复盘，记录哪些有效、哪些失败、返工原因和后续改进。                                                                                                         |
| `README.md`                           | 项目入口。它应该只包含稳定的高层信息，以及指向当前文档的导航。                                                                                                      |

文档应该被视为产品的一部分，而不是可选的说明文字。

## 2. 文档权威层级

```text
Vision
-> RFC（需要重大架构探索时）
-> ADR（架构决策被接受时）
-> OpenSpec
-> Canonical Implementation Plan
-> Implementation
-> Phase Completion Record
-> Milestone Progress
```

- Vision 说明为什么做。
- RFC 在重大架构问题需要探索时定义架构；它不是例行的 Milestone 文书。
- ADR 记录已接受的架构选择；没有此类决策时不要求创建。
- OpenSpec 定义 feature contract。
- canonical Implementation Plan 定义如何实施。
- Implementation 服从已接受的 OpenSpec、ADR 和 canonical plan；它是活动，不是与文档竞争的权威来源。
- Phase Completion Record 记录一个 Phase 实际完成什么。
- Milestone Progress 记录 Milestone 当前在哪里。

AI-assisted draft 不属于该权威链路。它是非权威 planning evidence，只能在与
已接受仓库权威记录完成明确 reconciliation 后为 canonical plan 提供输入。


## 3. Milestone 文档结构

每个 Milestone 必须使用相同的文档结构。在该 Milestone 的 canonical
implementation plan 建立后创建对应目录：

命名中，`<milestone-topic-slug>` 是不含 Milestone 编号的稳定 kebab-case 主题名
（例如 `structured-patchproposal`）。`<milestone-directory-slug>` 是
`m<NUMBER>-<milestone-topic-slug>`（例如 `m2-structured-patchproposal`）。两者
有意区分：目录用编号标识 Milestone，历史 draft 文件名只使用主题名。

```text
docs/milestones/
├── index.md
└── m<NUMBER>-<milestone-topic-slug>/
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
`retrospectives/m<NUMBER>-<milestone-topic-slug>.md`。

创建 canonical implementation plan 前，必须先创建一份详细 AI-assisted draft plan，
并保存为
`docs/_history/ai-assisted/implementation-plans/YYYY-MM-DD-<milestone-topic-slug>.md`。
推荐使用 Superpowers `writing-plans`；等价 framework 也可以产出该 draft。它是历史
planning evidence，不是第二份 canonical plan。canonical plan 必须将该 draft 与
已接受 OpenSpec、相关 RFC 和已接受 ADR 明确完成 reconciliation。

draft 与 canonical plan 都必须以 `Phase 1`、`Phase 2` 等作为一级执行结构。
Phase 是授权、focused commit、Completion Record、progress 更新和验收的单位；
Task 或 checkbox step 只能在 Phase 内部表达 TDD 与 verification 工作。完成
reconciliation 后，以 canonical plan 为准确定 Phase 名称和边界；不得仅为套用
新格式而重写旧的历史 draft。

## 4. Phase Completion Record 和进度索引

每个 Milestone 的每一个实现 Phase 都必须在
`docs/milestones/<milestone-directory-slug>/phases/phase-<number>-<phase-name>.md`
保留一份正式的 Phase Completion Record。文件名必须从已完成 reconciliation 的
canonical implementation plan Phase 名称转换为稳定的 kebab-case；已存在的
Completion Record 文件名应保持不变。不得根据聊天提示词为后续 Phase 命名。

必须实例化
[`docs/templates/milestone/phase-completion-record.template.md`](../templates/milestone/phase-completion-record.template.md)，
且不得改变其必需章节结构。`Changed Files` 使用 `File | Change | Purpose` 表格。
`TDD and Tests` 必须记录 RED、GREEN、必要的重构或修复迭代、命令、targeted result
和 cumulative-suite result。该记录只保留已经完成的工程事实，不包含 agent dispatch、
review diff 正文或临时调试叙述。

每个 Phase commit 后，必须同时创建或更新对应的 Phase Completion Record 和 milestone `progress.md`。Completion Record 承担该 Phase 的详细记录；`progress.md` 是简洁的 Milestone 索引，只记录 Phase 状态、commit、文档链接、当前阶段、下一个未完成 Phase 和 Milestone 级 reconciliation item。两者都不得重新定义需求、架构或实施顺序。

`progress.md` 不替代 Phase Completion Record，不记录详细 implementation，也不定义 requirements 或 architecture。

默认不生成工具特定的 brief、review diff、rereview diff 或 agent execution report。新的架构决策进入 ADR，需求变化进入 OpenSpec，实施顺序变化进入 canonical implementation plan。

完成 Completion Record 和 progress 索引更新后，输出简短总结并停止等待用户确认。不得自动进入下一阶段。

## 5. 翻译策略

英文流程文档是 canonical。既有 `.zh.md` 流程文档是稳定、持久流程规则的维护性翻译。滚动 progress 和临时执行产物默认不创建翻译。

## 6. 模板生命周期治理

模板统一文档职责、生命周期和必需章节；它们不要求每个 Milestone 都创建每种
文档，也不预设 requirements、architecture decisions、scope 或 acceptance
criteria。实例化模板时必须替换所有尖括号占位符。

### 6.1 Milestone 生命周期模板

在满足相应生命周期条件时使用以下模板：

| 模板 | 生命周期条件 | 权威性与用途 |
|---|---|---|
| `docs/templates/milestone/index.template.md` | canonical plan 建立时创建。 | 仅作为 Milestone 入口和链接。 |
| `docs/templates/ai-assisted/implementation-draft.template.md` | OpenSpec 及相关已接受 RFC/ADR 完备后、canonical plan 前创建。 | 非权威 AI-assisted planning evidence，必须完成 reconciliation。 |
| `docs/templates/milestone/implementation-plan.template.md` | draft 审校与 reconciliation 后创建。 | 唯一 canonical 执行计划。 |
| `docs/templates/milestone/progress.template.md` | 与 canonical plan 一起创建；每个 Phase 被接受后更新。 | 仅记录执行状态。 |
| `docs/templates/milestone/phase-completion-record.template.md` | 一个 Phase commit 被接受后才创建。 | 记录该 Phase 已完成的工程事实。 |
| `docs/templates/milestone/retrospective.template.md` | Milestone closure 时创建。 | 结果、证据、经验和延期工作。 |

Milestone index、canonical plan 和 progress index 是进入 Implementation 的标准
生命周期文档。Phase Completion Record 只为已完成 Phase 创建，retrospective
只在 Milestone closure 后创建。

### 6.2 OpenSpec Change 模板

每个 OpenSpec change 都使用 `openspec/templates/change/` 下的模板创建必需的
`proposal.md`、`design.md`、`tasks.md` 和 feature
`specs/<capability>/spec.md`。当已接受 scope 确有需要时，change 可以增加范围
受限的 contract、policy profile、fixture 或其他支持性文档；这些支持性文档不应
成为空壳的强制样板。

### 6.3 条件性架构记录

仅当存在重大架构探索或未决的跨域边界时创建 RFC。仅当决策已被接受且需要持久
记录时创建 ADR。两者都不是逐 Milestone 的清单项。若 OpenSpec 依赖这些记录，
应链接已接受记录，不得复制内容到 Milestone 目录。

### 6.4 采用与工具化边界

在 M2 和 M3 中手动实例化模板，并且只在实际使用暴露出稳定缺口时改进模板。
在此验证期内不得增加文档生成脚本、scaffolding command 或自动同步。
Superpowers 是推荐且可替换的执行辅助工具，不是 ForgeFlow 的 architecture 或
governance dependency。未来若要工具化，必须保留权威链路，且不得使 AI-assisted
draft 变成权威来源；替换执行 framework 不得影响 RFC、ADR、OpenSpec、canonical
plan 或 milestone lifecycle record。
