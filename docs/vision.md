# ForgeFlow Vision

## 1. Project Overview

ForgeFlow is an enterprise autonomous software engineering agent platform built on DeerFlow and LangGraph.

It is not a simple coding assistant, chatbot, or toy agent demo. ForgeFlow is intended to automate selected parts of the software maintenance lifecycle in a controlled, observable, and reviewable way.

The platform is designed around one core product idea: an AI agent system should not merely suggest code in a chat window. It should help prepare evidence-backed, testable, auditable engineering changes that humans can review and approve.

## 2. Problem Statement

Enterprise software maintenance is expensive because the work is rarely limited to writing a few lines of code.

Common problems include:

- bug diagnosis requires reading scattered code, historical context, logs, tests, and issue descriptions
- large repositories make relevant context hard to find quickly
- validation requires knowing which tests to run and how to interpret failures
- preparing a high-quality pull request requires root cause analysis, focused diffs, test evidence, and risk explanation
- review cycles are slowed by unclear rationale, missing validation, and oversized changes
- existing automation tools often lack governance, observability, reproducibility, and explainability

ForgeFlow exists to reduce this maintenance burden without removing human control from high-risk engineering decisions.

## 3. Target Users

ForgeFlow is designed for teams responsible for maintaining production software systems:

- software engineers
- platform engineering teams
- QA / test teams
- engineering productivity teams
- DevOps / CI maintainers

The first users should be engineers and platform teams who need reliable automation for low-to-medium-risk maintenance work, not fully autonomous production deployment.

## 4. Product Vision

The long-term ForgeFlow workflow is:

```text
GitHub Issue / Failed CI / Error Log
  -> Task Analysis
  -> Repository Understanding
  -> Bug Diagnosis
  -> Code Patch
  -> Validation
  -> Review
  -> Draft Pull Request
  -> Human Approval
  -> Evaluation / Memory Update
```

The long-term goal is to support autonomous software maintenance runs that produce draft pull requests with:

- clear task understanding
- repository evidence
- root cause analysis
- minimal code changes
- validation results
- risk review
- traceable run summaries
- human approval gates
- evaluation feedback
- stable memory updates when appropriate

ForgeFlow should make agent-created pull requests easier to trust, inspect, test, reject, or improve.

## 5. MVP Scope

The complete MVP vertical slice is:

```text
GitHub Issue
  -> Sandbox
  -> Repository Context
  -> PatchProposal
  -> Validation
  -> Review
  -> Draft PR
```

This MVP is intentionally narrow:

- single repository
- GitHub Issue input first
- sandbox execution
- repository context grounded in deterministic services
- structured `PatchProposal`
- bounded validation and retry behavior
- review and risk flags
- draft PR output only

The MVP is not the first implementation step. ForgeFlow must first establish a foundation slice that makes repository context reliable, observable, and evaluable.

## 6. Milestone 1 Scope

Milestone 1 is the Repository Context Foundation Slice.

It focuses only on Repository Context Service: a deterministic capability that gives later agent workflows evidence-backed repository context.

Milestone 1 includes:

- repo workspace input
- issue text / query input
- file search
- text search
- evidence references
- simple test command hints
- structured `RepositoryContextResult`

Milestone 1 does not include:

- patch generation
- code editing
- PR creation
- similar issue retrieval
- dependency graph
- automatic memory write

This slice should prove that ForgeFlow can ground future agent decisions in inspectable repository facts before attempting automated patch generation.

## 7. Core Principles

ForgeFlow is guided by these principles:

- Agent decides, tools execute.
- Repository facts come from deterministic services, not free-form agent memory.
- Structured contracts are preferred over free-form outputs.
- Execution is sandbox-first.
- High-risk actions require human approval.
- Observability is a product capability, not just internal logging.
- Evaluation starts from day one.
- Memory stores only stable engineering knowledge.

These principles are constraints, not slogans. They exist to keep the system governable as it becomes more capable.

## 8. Non-goals

The first phase does not include:

- Jira integration
- Slack approval
- automatic merge
- automatic deployment
- multi-repo orchestration
- IDE plugin
- complex enterprise permission system
- SWE-bench as the first evaluation target

These may become relevant later, but they should not shape the first implementation milestones.

## 9. Success Criteria

Early ForgeFlow success should be measured by foundation quality, not demo breadth.

Milestone 1 succeeds when ForgeFlow can produce:

- clear repository context results
- evidence-backed outputs
- bounded and inspectable scope
- traceable run summaries
- controlled sandbox and security policy direction
- small controlled evaluation fixtures
- a credible path toward the later Draft PR MVP

The MVP succeeds when a GitHub Issue can lead to a draft pull request with a minimal patch, validation evidence, review result, risk explanation, and human approval boundary.

## 10. Relationship with DeerFlow

DeerFlow is the upstream framework and reference implementation for ForgeFlow.

DeerFlow is expected to provide foundational capabilities such as:

- runtime primitives
- graph execution
- thread state primitives
- tool orchestration
- checkpointing
- middleware hooks
- tracing hooks

ForgeFlow owns the software engineering platform layer:

- software engineering domain state
- structured contracts
- repository context
- sandbox governance
- security policy
- patch boundary policy
- PR workflow
- evaluation framework
- product-level run summary

ForgeFlow should build on DeerFlow without becoming a shallow fork or simple rename. The platform should keep its own application boundary and use DeerFlow as the runtime foundation where it fits.
