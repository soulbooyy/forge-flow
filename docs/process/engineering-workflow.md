# ForgeFlow Engineering Workflow

## 1. Purpose

This document defines the engineering development process for ForgeFlow.

Its purpose is to:

- define how ForgeFlow evolves from vision to RFCs, OpenSpec changes, implementation, testing, evaluation, and retrospectives
- clarify when to use RFCs, OpenSpec, ADRs, Grill-Me reviews, and retrospectives
- prevent premature coding before architecture boundaries are clear
- keep documentation, code, tests, and evaluation evolving together

ForgeFlow is an enterprise autonomous software engineering agent platform built on DeerFlow and LangGraph. It is not intended to become a toy coding assistant. Its development process should preserve governance, observability, evaluation, and human approval boundaries from the beginning.

## 2. Development Principles

ForgeFlow development follows these principles:

- Vision before architecture.
- RFC before major architecture changes.
- OpenSpec before feature implementation.
- Test before production behavior.
- Evaluation from day one.
- Security and governance before automation.
- Human approval for high-risk actions.
- Deterministic services for repository facts.
- Structured contracts over free-form outputs.
- Git history as the source of project evolution.

These principles apply especially while the project is still in foundation and pre-MVP stages.

## 3. ForgeFlow Engineering Workflow

ForgeFlow follows a staged engineering workflow:

```text
Vision
-> Architecture
-> Specification
-> Planning
-> Implementation
-> Verification
```

This workflow applies to every milestone. The following sections define one
continuous process; later sections provide detailed rules for individual stages.

### 3.1 Architecture

Architecture starts from the project vision and produces RFCs and ADRs. RFCs
define architecture boundaries, system responsibilities, trade-offs, and
long-term technical direction. ADRs record accepted architectural decisions,
rejected alternatives, and important trade-offs.

Implementation must not begin while required architecture decisions remain
unresolved.

### 3.2 Specification

Specification takes the relevant RFCs and accepted ADRs as input and produces
an OpenSpec change. OpenSpec is the authoritative feature contract and must
include a proposal, design, tasks, and feature specifications. Each change must
state scope, acceptance criteria, non-goals, and constraints.

### 3.3 Grill-Me Design Review

Important features must receive a Grill-Me design challenge before planning.
Grill-Me exposes hidden assumptions, unclear boundaries, scope creep, and
architecture violations. It does not alter architecture decisions; final
decisions remain recorded in RFCs, ADRs, and OpenSpec.

### 3.4 Planning

Planning takes an accepted OpenSpec change as input and produces the canonical
Implementation Plan. The plan is the sole authority for execution order and
must define milestone scope, phase ordering, dependencies, expected file
changes, TDD strategy, and phase acceptance criteria.

For each milestone entering implementation, first generate a detailed
AI-assisted draft implementation plan after the OpenSpec, relevant RFCs, and
accepted ADRs are ready. Superpowers `writing-plans` is the recommended aid;
an equivalent execution framework may produce the same draft. Store it at
`docs/_history/ai-assisted/implementation-plans/YYYY-MM-DD-<milestone-topic-slug>.md`,
where the topic slug excludes the `m<NUMBER>-` directory prefix.
The draft must identify phase order, dependencies, expected file changes, TDD
steps, verification, and phase acceptance conditions.

Review the draft against the accepted OpenSpec, relevant RFCs, and accepted
ADRs before writing the canonical plan. The review must reconcile phase
boundaries, dependencies, scope exclusions, TDD strategy, and acceptance
criteria; when a draft conflicts with repository authority, repository
authority prevails and the conflict is resolved in the canonical plan.

Both plans use phases as their top-level execution structure; tasks or steps
are subordinate work items within a phase. The resulting canonical plan may use useful execution detail from the draft,
but it is the only plan that later phases may treat as authoritative. The
AI-assisted draft remains non-canonical planning evidence in `_history`; it
must not create a second plan that requires synchronization.

Implementation phases must come from the canonical plan. Chat prompts do not
redefine a phase's scope, interface, file list, or acceptance criteria.

### 3.5 Implementation

Implementation uses Lightweight Implementation Execution and follows this
sequence for each phase:

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

Every completed phase verifies that tests pass, scope is respected, the Git diff
has been reviewed, and documentation is updated. Before committing, run targeted
tests, cumulative implemented tests, `git diff --check`, and `git status`.

### 3.7 AI-assisted Development Tools

Superpowers is a recommended execution-assistance framework, and other
AI-assisted tools or equivalent disciplined practices may replace it. They may
help with task decomposition, plan execution, implementation planning,
verification, or review assistance, but they are not authoritative sources or
ForgeFlow architecture dependencies. They must not define architecture,
requirements, acceptance criteria, or milestone lifecycle. Repository
documentation remains the source of truth.

Replacing or removing an execution-assistance framework must not affect RFCs,
accepted ADRs, OpenSpec, the canonical Implementation Plan, or milestone
lifecycle records. The mandatory workflow outcome is the reviewed,
reconciled draft and canonical plan, not use of a named tool.

An AI-generated draft plan is a planning input, not a replacement for the
canonical Implementation Plan. Its role is to improve completeness and
executability before the canonical plan is written and reviewed.
