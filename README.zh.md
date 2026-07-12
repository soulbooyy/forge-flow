# ForgeFlow

ForgeFlow 是一个基于 DeerFlow 和 LangGraph 构建的企业级自主软件工程 Agent 平台。

长期目标是支持受治理、可观测、可评估的软件维护工作流，例如：

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

ForgeFlow 不是一个通用代码助手、聊天机器人或玩具级 Agent demo。它旨在成为一个面向生产的平台，用于准备有证据支撑、可测试、可审查的工程变更。

## 当前状态

ForgeFlow 目前处于：

```text
Milestone 1：closure 已完成
下一阶段：准备 Milestone 2 的架构与规格
```

项目基础文档、已接受的架构基线、DeerFlow 扩展评估和初始 ADR 已就绪。
Milestone 1 已完成确定性的 Repository Context Foundation Slice，包括契约、
fixtures、验收覆盖和 hardening 验证。

Milestone 1 是 Repository Context Foundation Slice，不是完整 MVP。它仅包含
确定性的 Repository Context Service，用于提供相关文件、证据引用、文件/文本
搜索结果和描述性的测试命令提示；没有生成补丁、编辑代码、创建 Pull Request 或
运行自主修复循环。详见 [Milestone 1 进度索引](docs/milestones/m1-repository-context-foundation/progress.md)
和 [复盘](retrospectives/milestone-1-repository-context-foundation.md)。

后续 MVP 是从 GitHub Issue 到 Draft PR 的垂直切片：

```text
GitHub Issue
  -> Sandbox
  -> Repository Context
  -> PatchProposal
  -> Validation
  -> Review
  -> Draft PR
```

## 文档

* [文档总导航](docs/index.zh.md)
* [愿景](docs/product/vision.zh.md)
* [里程碑](docs/product/roadmap/milestones.zh.md)
* [开发流程](docs/process/index.zh.md)
* [项目基础方案](docs/architecture/foundation/project-foundation-proposal.zh.md)
* [初始架构草案](docs/_history/architecture/initial-architecture-draft.md)

## 方法论

ForgeFlow 使用分阶段、文档驱动的开发流程：

* RFC 驱动的架构
* OpenSpec 功能规格
* Grill-Me 架构审查
* 测试驱动实现
* 从第一天开始评估

在相关 RFC 决策、功能规格、安全约束和评估方法明确之前，项目不应从架构阶段进入实现阶段。

## 下一步

1. 审阅 Milestone 1 复盘和 closure 证据。
2. 为 Milestone 2 建立架构和 OpenSpec 范围。
3. 在相应契约和治理决策被接受前，不实现补丁生成、验证执行或 PR 行为。
