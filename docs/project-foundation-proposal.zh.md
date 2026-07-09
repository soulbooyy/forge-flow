# ForgeFlow 项目基础方案

状态：草稿  
类型：项目基础设计产物  
最后更新：2026-07-09

本文档记录 ForgeFlow 在正式 RFC 编写前的项目基础设计。

它不是最终架构规范。  
最终架构决策以后将以 `rfcs/` 目录下的 RFC 文档为准。

相关文档：
- `docs/vision.md`
- `docs/milestones.md`
- `docs/development-process.md`
- `rfcs/`

## 1. 定位

ForgeFlow 是一个基于 DeerFlow 和 LangGraph 构建的企业级自主软件工程 Agent 平台。

长期目标工作流：

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

这个长期工作流是产品方向，而不是第一步实现内容。

ForgeFlow 不应该变成一个通用代码聊天机器人、一个浅层改名版 DeerFlow，或者一个玩具级 LangChain demo。它的产品边界是自动化软件维护，并且输出必须可观测、可审查、可回滚。长期核心交付产物是一份草稿 Pull Request，并且该 PR 需要由证据、测试、追踪数据、明确的风险审查和人工批准门控支撑。

核心原则：

* Agent 负责判断，工具负责执行，确定性服务负责提供仓库事实。
* Repository Context 和 Code Intelligence 是基础设施，而不是 Agent 角色。
* 跨角色交接必须使用结构化契约。
* 高风险操作需要人工批准。
* 验证必须有重试边界和成本边界。
* Memory 只存储稳定的工程知识。
* 可观测性和评估从第一天起就是产品能力。
* 安全护栏必须在 MVP 垂直切片之前存在，而不是之后再补。

## 2. Milestone 1 与 MVP

最重要的范围修正，是将第一个基础切片与后续 MVP 垂直切片分离。

### Milestone 1：Repository Context Service / 基础切片

Milestone 1 构建最小但有用的仓库上下文能力，后续的 `PatchProposal` 和自主修复工作流都可以依赖它。

Milestone 1 不是完整 MVP。它不应该创建补丁、修改代码、创建 Pull Request，或运行自主修复循环。

Milestone 1 的职责：

* 接收 repo workspace
* 接收 query
* 接收可选 issue text
* 返回相关文件
* 返回证据引用
* 返回简单的文件/文本搜索结果
* 从配置或约定中返回候选测试命令提示
* 输出结构化的 `RepositoryContextResult`

Milestone 1 不包含：

* 补丁生成
* 代码修改
* Pull Request 创建
* 自动修复
* 复杂 issue 历史检索
* 完整依赖图
* 完整 CI 集成
* memory 写入
* 多仓库上下文
* 大规模 embedding 索引
* 语言特定的深度静态分析

### MVP：从 GitHub Issue 到草稿 PR 的垂直切片

MVP 是后续的垂直切片：

```text
GitHub Issue
  -> Sandbox
  -> Repository Context
  -> PatchProposal
  -> Validation
  -> Review
  -> Draft PR
```

这个 MVP 只应在基础 RFC 决策和 Repository Context Service spec 明确后开始。它仍然刻意保持狭窄范围：

* 单仓库
* 优先支持 GitHub Issue 输入
* 沙箱执行
* 优先支持本地验证
* 只输出草稿 PR
* 不自动 merge
* 不自动部署
* 不支持 Jira
* 不支持 Slack 审批
* 不支持多仓库编排
* 不支持 IDE 插件

## 3. 推荐仓库结构

推荐的初始结构：

```text
forge-flow/
  docs/
    vision.md
    project-foundation-proposal.md
    initial-architecture-draft.md
  rfcs/
    README.md
    rfc-001-agent-architecture.md
    rfc-002-state-model-and-structured-contracts.md
    rfc-003-tool-and-mcp-integration.md
    rfc-004-sandbox-and-security-governance.md
    rfc-005-observability-and-trace-model.md
    rfc-006-evaluation-framework.md
    rfc-007-deerflow-extension-strategy.md
  specs/
    README.md
    repository-context-service/
      proposal.md
      design.md
      tasks.md
  adr/
    README.md
  retrospectives/
    README.md
  scripts/
    README.md
  third_party/
    README.md
```

在第一个被接受的 OpenSpec 功能准备实现之前，先不要创建 `src/` 和 `tests/`。过早创建源码目录会诱导虚假抽象、过早 API，以及在工作流边界尚未稳定前就创建 Agent 类。

目录设计理由：

| 目录                | 用途                                         |
| ----------------- | ------------------------------------------ |
| `docs/`           | 稳定的项目级文档：愿景、基础方案、架构概览、术语表、里程碑计划。           |
| `rfcs/`           | 实现前的跨领域设计决策。RFC 用于比较选项，并在 ADR 固化决策前记录当前建议。 |
| `specs/`          | OpenSpec 风格的功能变更。每个功能应包含具体范围、设计、任务和验收标准。   |
| `adr/`            | 决策做出后的不可变架构决策记录。RFC 负责讨论；ADR 负责记录。         |
| `retrospectives/` | 来自实现、评估、事故和流程缺口的里程碑后复盘。                    |
| `scripts/`        | 项目自动化辅助工具，例如文档检查、评估运行器或安装命令。初期只保留 README。  |
| `third_party/`    | 上游依赖的元数据和引用，例如 DeerFlow。初期避免复制上游源码。        |

后续只在需要时再添加：

| 未来目录        | 添加时机                       |
| ----------- | -------------------------- |
| `src/`      | 某个功能 spec 被接受并开始实现时。       |
| `tests/`    | 已经有可执行代码或基于 spec 的验证需要测试时。 |
| `examples/` | 已经有值得展示的可运行垂直切片时。          |
| `evals/`    | 评估 fixtures 和运行器成为具体产物时。   |
| `infra/`    | 沙箱、部署或可观测性基础设施真正落地时。       |

## 4. DeerFlow 与 ForgeFlow 的边界

DeerFlow 是上游框架/参考。ForgeFlow 是围绕它构建的企业软件维护应用层/平台层。

### DeerFlow 职责

DeerFlow 应该拥有或提供以下基础能力：

* graph / runtime / thread 原语
* tool orchestration 原语
* checkpoint 和 state persistence 原语
* middleware hook 原语
* tracing hook 原语

### ForgeFlow 职责

ForgeFlow 应该拥有：

* 软件工程领域 state
* 结构化契约
* `RepositoryContextResult`
* `PatchProposal`
* `ValidationResult`
* `ReviewResult`
* `PRResult`
* Repository Context Service
* 沙箱治理
* 安全策略
* 补丁边界策略
* PR 工作流
* 评估框架
* 产品级 run summary

### 集成策略

选项：

| 选项               | 优点                                  | 缺点                                   | 当前适配度         |
| ---------------- | ----------------------------------- | ------------------------------------ | ------------- |
| Git submodule    | 可以锁定精确上游版本；保持 ForgeFlow 独立；支持可复现引用。 | 增加 submodule 工作流负担；在扩展点明确前过早。        | RFC-007 之后适合。 |
| 单独的本地参考仓库        | 零耦合；最适合早期探索；在架构稳定前避免 vendoring 决策。  | 项目本身不是完全自包含；贡献者需要单独获取 DeerFlow。      | 最适合当前基础阶段。    |
| 直接 fork DeerFlow | 容易修改内部实现；完全可控。                      | 容易漂移成改名版 fork；削弱 ForgeFlow 的产品/平台边界。 | 当前不推荐。        |
| 复制 DeerFlow 源码   | 本地快速 hack。                          | 维护成本高；来源不清晰；难以同步上游。                  | 避免。           |

当前建议：将 DeerFlow 保持为单独的本地参考仓库，并在项目结构初始化时，在 `third_party/README.md` 中记录该引用。

RFC-007 必须在实现前定义实际扩展映射：graph nodes、thread state extension、tool registry、checkpointing、middleware hooks、trace hooks，以及 ForgeFlow 可能需要的任何上游变更。

## 5. Agent 角色与工作流边界

Planner、Software Engineer、Validation、Review 和 PR 在当前阶段是工作流角色。它们还不应该被实现为独立类、服务或长期存在的 Agent。

第一个架构决策是角色边界，而不是代码结构。

| 角色                       | 当前边界                                                                                                        |
| ------------------------ | ----------------------------------------------------------------------------------------------------------- |
| Planner                  | 生成并修订结构化计划、成功标准、风险假设和停止条件。它不负责运行时调度。                                                                        |
| Workflow Graph / Runtime | 执行 graph、进行 dispatch、应用 middleware、强制执行停止条件，并控制 retry transitions。                                          |
| Software Engineer        | 产生补丁意图，并且在后续 MVP 中，可以使用受控的沙箱编辑工具生成 diff。它不能直接写文件，也不能绕过补丁/安全策略。                                              |
| Validation               | 运行验证命令并解释失败。它不直接修复失败。                                                                                       |
| Repair Loop              | 工作流层面的 transition，当重试策略允许时，可以回到 Software Engineer 生成修订后的 `PatchProposal`。                                   |
| Review                   | 产生 `ReviewResult`、风险标记和 blocking issues。它不执行人工批准。                                                           |
| Human Approval           | 针对敏感操作、高风险变更、验证耗尽、非草稿 PR 创建、merge 或策略升级的独立门控。                                                               |
| PR                       | 只有在 `ReviewResult` 通过且策略允许后，才创建 branch / commit / draft PR。Commit message 和 PR body 必须来自契约和证据，而不是自由形式的重新总结。 |

这可以防止 Planner 变成超级 Agent，也可以防止 Validation、Review 和 PR 职责重叠。

## 6. 结构化契约

ForgeFlow 的工作流必须由契约驱动。契约应该在生产代码之前定义，但基础方案中不要求完整 JSON schema。

RFC-002 中需要定义的契约：

* `RepositoryContextResult`
* `PatchProposal`
* `ValidationResult`
* `ReviewResult`
* `PRResult`

每个契约都应考虑以下字段类别：

* `schema_version`
* `run_id`
* source evidence references
* artifact IDs
* risk flags
* policy decisions
* retry lineage
* stop reason
* `created_at`
* `updated_at`
* immutable fields
* mutable fields

最低方向：

| 契约                        | 用途                                                                               |
| ------------------------- | -------------------------------------------------------------------------------- |
| `RepositoryContextResult` | 有证据支撑的仓库上下文：相关文件、搜索结果、低成本 symbol hints，以及测试命令提示。                                 |
| `PatchProposal`           | 根因、修复策略、变更文件、diff artifact reference、验证命令、风险标记和限制。                               |
| `ValidationResult`        | 执行过的命令、结果状态、解析后的失败、失败分析、重试次数、重试 lineage 和停止原因。                                   |
| `ReviewResult`            | Blocking issues、风险等级、敏感文件发现、测试充分性、是否建议批准 draft PR，以及所需人工门控。                      |
| `PRResult`                | Branch、commit、draft PR URL、关联 issue、PR body artifact、可用的 CI/check 状态，以及使用过的策略决策。 |

契约应引用 artifacts，而不是嵌入大型源码文件、完整日志或大型 diff。

## 7. State 模型

State 必须拆成三类。

### Runtime State

Runtime State 是当前工作流执行过程中的可变、短生命周期工作状态。

示例：

* 当前计划步骤
* 当前重试次数
* 当前 repository workspace path
* 临时工具结果
* 激活的停止条件
* 临时验证输出
* 中间失败的 patch 尝试

Runtime State 可以扩展 DeerFlow thread/run state，但不应被视为持久审计历史。

### Durable Run Summary / Audit Record

Durable Run Summary 会被持久化，用于可追踪性、审查、PR 说明和评估。

持久化内容：

* run ID 和 trace ID
* task source 和 normalized task summary
* plan 和 plan revisions
* evidence references
* contract artifacts
* changed file list
* root cause summary
* validation commands 和 summarized results
* review result 和 risk flags
* policy decisions
* retry count 和 stop reason
* token/cost/time metrics
* PR result
* human feedback

默认不要持久化原始克隆仓库内容、完整源码文件、不必要的完整日志、secrets，或未脱敏的 prompts/responses。

### Long-Term Memory

Long-Term Memory 只存储稳定的工程知识。

允许的例子：

* 仓库测试命令约定
* 稳定的架构说明
* 重要路径
* 已接受的工程约定
* 已验证的重复失败模式

不允许：

* 源码
* secrets
* 临时日志
* 未验证推理
* 大型 diff
* 失败的中间尝试
* 客户敏感数据

第一版 Memory 默认不自动写入。如果存在 memory 写入，也必须要求人工确认，并且只应存储稳定的仓库约定或已验证的工程知识。

## 8. 安全与治理护栏

安全治理不能完全推迟到 Phase 2。MVP 垂直切片会编辑代码、运行命令并创建草稿 PR，因此在该切片之前必须存在最低限度的护栏。

MVP 前置护栏：

* command policy
* path policy
* network policy
* resource limits
* diff threshold
* secret scan hook
* sensitive file policy
* cost and retry caps
* human approval gates

敏感文件和区域至少必须包括：

* `.github/workflows`
* deployment configuration
* infrastructure files
* auth code
* crypto code
* permission code
* production configuration

人工批准门控应在以下事件之前或之后触发：

* 高风险命令执行
* 敏感文件修改
* diff size 或 changed file count 超过阈值
* validation retry exhaustion
* `ReviewResult` 包含阻塞或高风险发现
* 非草稿 PR 创建
* merge
* deployment-related change

危险命令保护不应只依赖字符串黑名单。RFC-004 应一起定义 allowlists、denylists、path policy、diff policy、resource limits、network policy、secret scanning 和 approval escalation。

## 9. Repository Context Service 范围

Repository Context Service 是第一个 OpenSpec 候选，也是 Milestone 1 的基础切片。

它必须是一个确定性服务，而不是 Repository Context Agent。

### 第一版包含

* repo workspace input
* query input
* optional issue text input
* file search
* text search
* 如果成本低且已有工具支持，则包含 simple symbol search
* 基于配置和约定的 test command hints
* evidence references
* 结构化 `RepositoryContextResult`
* trace hooks：记录 summary 和 evidence references，而不是完整源码快照

### 第一版排除

* patch generation
* code modification
* automatic repair
* similar issue retrieval
* full dependency graph
* large-scale embedding index
* GitHub issue 或 PR history ingestion
* multi-repo context
* language-specific deep static analysis
* full CI integration
* memory write

Spec 的开放问题：

* 第一版服务是否语言无关？
* 它是否读取 git history，还是只读取当前 workspace？
* 测试提示是否完全基于约定/配置？
* 索引是每次运行临时生成，还是持久化？
* 什么才算 evidence reference？
* 哪些 trace data 可以安全持久化？

## 10. 文档策略

ForgeFlow 应该使用五种文档类型，每种承担不同职责。

| 文档类型                  | 作用                                                          |
| --------------------- | ----------------------------------------------------------- |
| Vision document       | 解释 ForgeFlow 为什么存在、服务谁、目标工作流、MVP 边界和非目标。                    |
| RFC                   | 跨领域架构的预决策设计提案。RFC 比较选项并形成建议。                                |
| OpenSpec feature spec | 具体且可实现的功能变更，包含 proposal、design、tasks 和 acceptance criteria。 |
| ADR                   | 已接受架构决策的简短持久记录，通常链接到某个 RFC。                                 |
| Retrospective         | 里程碑后的学习记录，说明哪些有效、哪些失败、哪些需要调整。                               |

RFC 负责讨论。ADR 负责记录。OpenSpec 在足够的 RFC 决策存在后，为一个具体变更限定范围。

## 11. 更新后的 RFC 路线图

### RFC-001 Agent Architecture

目的：定义最小工作流角色，并避免过早设计 agent/service/class。

关键问题：

* Planner、Software Engineer、Validation、Review 和 PR 是概念性工作流角色，还是 runtime components？
* 每个角色负责什么？
* workflow graph/runtime 负责什么？
* repair loop ownership 如何与 Validation 分离？
* Planner 如何避免变成超级 Agent？

预期决策：

* 在基础阶段和第一批 specs 中，将五个 agents 视为工作流角色。
* Planner 只生成/修订 plan 和 stop conditions。
* Runtime/workflow graph 执行 scheduling、retries、middleware 和 stop enforcement。
* Validation 解释失败，但不修复。
* Review 产生风险标记，但不批准高风险操作。

为什么重要：过早的 agent 实体设计会造成职责重叠、行为难测试和策略绕过。

当前建议：在 MVP 垂直切片证明哪些边界值得实现为具体 artifact 之前，保持角色概念化。

### RFC-002 State Model and Structured Contracts

目的：定义 runtime state、durable run summary、long-term memory，以及所需结构化契约。

关键问题：

* 什么扩展 DeerFlow thread/run state？
* 什么是 runtime-only？
* 什么会成为 durable audit record？
* 什么允许进入 long-term memory？
* `RepositoryContextResult`、`PatchProposal`、`ValidationResult`、`ReviewResult` 和 `PRResult` 需要哪些字段？
* schema versions、evidence refs、artifact IDs、risk flags、policy decisions、retry lineage、stop reasons、mutable/immutable fields 如何表示？

预期决策：

* 将 state 拆分为 Runtime State、Durable Run Summary / Audit Record 和 Long-term Memory。
* 持久化 contract artifacts 和 summaries，而不是原始仓库内容或未脱敏日志。
* 第一版 memory 不自动写入，除非经过人工确认。

为什么重要：契约和 state 边界决定审计能力、评估能力、重试安全性和 PR 可信度。

当前建议：在写实现代码前定义最小契约字段类别，但完整 JSON schema 细节推迟到 RFC 中。

### RFC-003 Tool and MCP Integration

目的：定义 agents 和 workflow roles 如何访问 GitHub、沙箱、仓库搜索、测试执行、diff 和安全能力。

关键问题：

* 哪些工具是 read-only、sandbox-write、external-write 或 approval-gated？
* 每个工具必须返回什么证据？
* 工具错误如何表示？
* 工具调用如何被追踪，并如何与契约关联？
* 哪些 MCP 集成是 Milestone 1 必需的，哪些属于 MVP？

预期决策：

* 仓库事实必须来自确定性服务/工具。
* 工具必须返回结构化证据。
* 外部写操作需要策略调解。
* 沙箱编辑工具受控，并且不能被 Agent 角色绕过。

为什么重要：只有当仓库事实声明和副作用都能追溯到工具时，平台才可信。

当前建议：Milestone 1 只需要 repository workspace/search 风格工具；GitHub 写操作属于后续 MVP 垂直切片。

### RFC-004 Sandbox and Security Governance

目的：在任何代码修改或测试执行工作流之前，定义最低安全策略。

关键问题：

* network access 是否默认禁用？
* dependency installation 和 package downloads 如何处理？
* 哪些命令被 allowlist 或 deny？
* 哪些文件路径是敏感的？
* 适用哪些 resource limits？
* 哪些 diff thresholds 触发升级？
* secret scanning 如何运行？
* 何时需要 human approval gates？
* logs 和 traces 如何脱敏？

预期决策：

* 定义 command、path、network、resource、diff、secret、sensitive file、cost、retry 和 approval policies。
* 敏感文件包括 `.github/workflows`、deployment config、infrastructure files、auth、crypto、permission 和 production config。
* 安全护栏是 MVP 前置条件，而不是 Phase 2 的奢侈品。

为什么重要：没有清晰策略的沙箱执行会在表面安全的同时制造风险。

当前建议：在这些护栏被明确前，不实现 repair/PR MVP；Milestone 1 可以在受限本地 workspace access 下推进以读取为主的 repository context。

### RFC-005 Observability and Trace Model

目的：定义产品级 trace、run summary、redaction、retention 和 PR-facing trace excerpts。

关键问题：

* 标准 run summary 是什么？
* 哪些 spans 是必需的？
* 哪些数据可以记录、总结、脱敏或禁止记录？
* LLM calls、tool calls、contract artifacts、validation、review、policy decisions、cost 和 feedback 如何关联？
* 哪些内容进入 PR body，哪些进入 internal audit record？

预期决策：

* 每次运行都有 trace ID 和 durable run summary。
* 可观测性是产品 UX 和审计基础设施，而不仅是日志。
* 在存储 prompts、tool results、logs 或 diffs 之前，需要 redaction 和 retention rules。

为什么重要：企业不会信任无法检查证据的自主 PR；没有可靠 traces，平台也无法改进。

当前建议：第一版 trace 默认存储 summaries 和 evidence references，而不是完整源码快照或未脱敏日志。

### RFC-006 Evaluation Framework

目的：定义第一版评估，使其小型、可重复，并且连接到产品 traces。

关键问题：

* 第一批 evaluation dataset 是什么？
* Milestone 1 哪些指标是必需的？
* MVP 垂直切片哪些指标是必需的？
* evaluation results 如何链接到 run summaries 和 contract artifacts？
* 哪些失败应该阻止进入下一里程碑？

预期决策：

* 从 5-10 个小型受控 repo fixtures 或精选历史 issue fixtures 开始。
* 对 Milestone 1，衡量 context retrieval precision、evidence quality、test recommendation usefulness 和 run summary completeness。
* 对 MVP，增加 patch changed files count、validation determinism、test pass rate、retry count、token/cost、execution time 和 failure rate。
* 将 SWE-bench 和 SWE-bench Verified 作为长期目标，而不是第一版前置条件。

为什么重要：评估必须避免进展依赖轶事经验，也要避免过早承诺大型 benchmark。

当前建议：在尝试大规模 benchmarks 前，先创建一小组受控 fixtures。

### RFC-007 DeerFlow Extension Strategy

目的：定义 ForgeFlow 如何基于 DeerFlow 构建，而不是变成 fork 或依赖不稳定内部实现。

关键问题：

* ForgeFlow 将扩展 DeerFlow 的哪些抽象？
* ForgeFlow 如何挂接 domain state？
* ForgeFlow 如何注册 tools？
* checkpointing、middleware hooks 和 trace hooks 如何映射到 ForgeFlow 的需求？
* DeerFlow 应该作为本地参考仓库、submodule、package dependency 还是 fork？
* 哪些变更可能贡献给上游？

预期决策：

* 在基础阶段将 DeerFlow 保持为单独的本地参考。
* 在依赖机制之前先定义扩展点。
* 只有在扩展点已知后，才重新考虑固定版本 submodule 或 package dependency。

为什么重要：不清晰的集成会导致脆弱 fork，或导致平台无法有效使用 runtime。

当前建议：在编写 runtime integration code 之前，先在 RFC-007 中记录 extension map。

## 12. OpenSpec 就绪计划

当前状态：

* 尚未准备好为完整的 GitHub Issue 到 Draft PR 工作流生成 OpenSpec。
* 在几个 RFC skeleton 决策完成后，可以准备一个狭窄的 Repository Context Service OpenSpec 草案。

在 Repository Context Service OpenSpec 之前，需要的 RFC skeleton 决策：

* RFC-001 Agent Architecture
* RFC-002 State Model and Structured Contracts
* RFC-004 Sandbox and Security Governance
* RFC-007 DeerFlow Extension Strategy

RFC-003、RFC-005 和 RFC-006 可以并行起草。它们不需要在小型 Repository Context Service 功能 spec 开始前完全接受，但其中的开放问题应被引用。

Repository Context Service OpenSpec 必须包含：

* `proposal.md`：用户价值、范围、非目标、验收标准。
* `design.md`：确定性服务边界、输入、输出、evidence references、trace behavior、failure modes。
* `tasks.md`：在允许实现后，用于文档、测试和实现的 checklist。

该 OpenSpec 必须明确排除 patch generation、code modification、PR creation、memory write、deep issue history、full dependency graph 和 multi-repo support。

## 13. 更新后的里程碑计划

### Milestone 0：基础文档

产出：

* project vision
* revised foundation proposal
* RFC index 和七个 RFC drafts
* ADR index
* retrospective index
* documented DeerFlow upstream reference strategy

退出标准：

* Milestone 1 和 MVP 被清晰分离。
* Agent roles 被定义为 workflow roles。
* DeerFlow 和 ForgeFlow responsibilities 被分离。
* Security 和 evaluation 没有被推迟到 MVP 前置条件之外。

### Milestone 1：Repository Context Service / 基础切片

产出：

* accepted Repository Context Service OpenSpec
* `RepositoryContextResult` contract direction
* deterministic file/text search behavior
* evidence references
* candidate test command hints
* context queries 的 trace summary

非目标：

* 不生成 patch
* 不修改代码
* 不创建 PR
* 不自动修复
* 不写 memory

退出标准：

* 给定一个 repo workspace 和 query，该服务返回相关文件、evidence references 和 test hints。
* 行为可以在小型受控 fixtures 上被检查和评估。
* 没有 Agent persona 拥有仓库事实。

### Milestone 2：PatchProposal and Validation Slice

产出：

* controlled sandbox edit path
* `PatchProposal`
* local validation command execution
* `ValidationResult`
* bounded retry policy

非目标：

* 不自动 merge
* 不部署
* 不做广泛 CI 集成

### Milestone 3：Review and Draft PR Slice

产出：

* `ReviewResult`
* sensitive file 和 diff risk checks
* draft PR creation
* `PRResult`
* PR body 从 contracts 和 evidence 生成

退出标准：

* 只有当 review 和 policy 允许时，才能创建 draft PR。
* 高风险变更在 PR 创建前需要人工批准。

### Milestone 4：MVP 垂直切片

目标：

```text
GitHub Issue -> Sandbox -> Repository Context -> PatchProposal -> Validation -> Review -> Draft PR
```

退出标准：

* 单仓库 GitHub Issue 输入
* 受控沙箱执行
* 有边界的 repair loop
* 产品级 run summary
* 小型受控评估集
* 不自动 merge 或部署

## 14. 评估计划

第一版评估必须从小规模开始。

不要把 SWE-bench 作为第一个评估目标。SWE-bench 和 SWE-bench Verified 应作为长期目标，等平台能够可靠运行受控 fixtures 后再考虑。

### Milestone 1 Evaluation

使用 5-10 个小型受控 repository fixtures。

衡量：

* context retrieval precision
* evidence reference quality
* test recommendation usefulness
* run summary completeness
* repeated runs 的 determinism

### MVP Evaluation

增加：

* patch changed files count
* patch size
* validation determinism
* test pass rate
* retry count
* token cost
* execution time
* failure rate
* draft PR completeness

评估结果应该链接到 run summaries、contract artifacts 和 trace IDs。

## 15. 更新后的 MVP 就绪检查清单

在第一个 MVP 实现工作开始前：

* [ ] Milestone 1 和 MVP 被明确分离。
* [ ] Repository Context Service 被定义为确定性服务，而不是 Agent。
* [ ] RFC-001 决定这五个 agents 是继续作为 workflow roles，还是之后成为 runtime components。
* [ ] RFC-001 将 Planner 限定为 plan revision 和 stop conditions。
* [ ] RFC-001 将 scheduling、retry transitions 和 stop enforcement 分配给 workflow graph/runtime。
* [ ] RFC-002 为 `RepositoryContextResult`、`PatchProposal`、`ValidationResult`、`ReviewResult` 和 `PRResult` 定义最小 contract fields。
* [ ] RFC-002 区分 Runtime State、Durable Run Summary / Audit Record 和 Long-Term Memory。
* [ ] RFC-002 说明第一版 Memory 不自动写入，除非经过人工确认。
* [ ] RFC-003 定义 tool permission levels 和 evidence-returning requirements。
* [ ] RFC-004 定义 command、path、network、resource、diff、secret scan、sensitive file、cost、retry 和 approval policies。
* [ ] RFC-004 列出 sensitive file categories，包括 workflows、deployment、infra、auth、crypto、permission 和 production config。
* [ ] RFC-005 定义 run summary fields、redaction 和 retention rules。
* [ ] RFC-006 定义 first-version controlled fixtures 和 metrics。
* [ ] RFC-007 定义 DeerFlow extension points 和 ForgeFlow-owned platform responsibilities。
* [ ] Repository Context Service OpenSpec 排除 patch generation、code modification、PR creation、memory write、deep issue history、full dependency graph 和 multi-repo support。
* [ ] Human approval gates 是明确节点，而不是泛泛地说“high risk”。
* [ ] Validation retry 对 rounds、token cost、tool calls、elapsed time、diff growth 和 repeated failure type 有硬性上限。
* [ ] Draft PR body 从 contracts、evidence、validation、review 和 trace summaries 生成。

## 16. 初始 Git 工作流

推荐的早期提交：

```text
chore: initialize project structure
docs: add project vision
docs: add project foundation proposal
docs(rfc): add agent architecture proposal
docs(rfc): add state model and structured contracts proposal
docs(rfc): add sandbox and security governance proposal
docs(rfc): add DeerFlow extension strategy
docs(spec): add repository context service proposal
docs(rfc): add tool, observability, and evaluation proposals
chore: document DeerFlow upstream reference
```

在 RFC-001、RFC-002、RFC-004 和 RFC-007 拥有足够 skeleton decisions 以支撑 Repository Context Service OpenSpec 之前，提交应保持文档导向。不要在基础提交中加入生产代码。

## 17. 已应用的具体文档修改

本次修订应用了 Grill-Me 架构审查，并通过以下具体方式修改了基础方案：

* 将 Milestone 1 与后续 MVP 垂直切片分离
* 将 Repository Context Service 定义为第一个基础切片
* 将 Repository Context Service 范围收窄为 file/text search、低成本 symbol hints、test hints、evidence references 和 `RepositoryContextResult`
* 说明 Planner、Software Engineer、Validation、Review 和 PR 是 workflow roles，而不是 implementation classes 或 services
* 将 Planner 限定为 structured plan revision 和 stop conditions
* 将 scheduling、retries 和 stop enforcement 移到 workflow graph/runtime
* 明确 Validation 不直接修复
* 将 Review Agent output 与 Human Approval gates 分离
* 定义 DeerFlow 和 ForgeFlow 的职责边界
* 强化 RFC-002 的 contract decision points
* 将 state 拆分为 Runtime State、Durable Run Summary / Audit Record 和 Long-Term Memory
* 将第一版 memory 设为非自动写入，除非经过人工确认
* 将最低安全护栏纳入 MVP 前置条件
* 收窄第一版 Code Intelligence / Repository Context 范围
* 更新 OpenSpec 就绪状态，说明完整 GitHub Issue 到 Draft PR 流程还未准备好进入 spec
* 使用每个 RFC 的当前建议更新 RFC roadmap
* 将第一版评估从 SWE-bench-first 改为小型受控 fixtures
* 使用 policy、state、contract、evaluation 和 approval gates 更新 MVP readiness checklist
