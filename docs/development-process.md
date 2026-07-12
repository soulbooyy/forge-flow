# ForgeFlow Development Process

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

## 3. Document Types and Responsibilities

| Document | Responsibility |
|---|---|
| `docs/vision.md` | Project vision, target users, long-term direction, MVP boundary, Milestone 1 boundary, and core principles. |
| `docs/milestones.md` | Stage planning. Defines Milestone 1, MVP, later phases, scope exclusions, and exit criteria. |
| `docs/project-foundation-proposal.md` | Pre-RFC foundation design proposal. It is early design input, not the final architecture specification. |
| `rfcs/` | Major architecture decisions such as Agent Architecture, State Model, Tool/MCP Integration, Sandbox Governance, Evaluation Framework, and DeerFlow Extension Strategy. |
| `openspec/` or `specs/changes/` | Feature-level specifications such as Repository Context Service, PatchProposal generation, Validation workflow, ReviewResult generation, and Draft PR creation. |
| `adr/` | Accepted architecture decision records, usually created after RFC discussion reaches a decision. |
| `docs/implementation-plans/` | Canonical implementation sequence, file-level work, dependencies, TDD steps, and phase acceptance conditions. |
| `docs/milestones/<milestone-slug>/` | Milestone status index and formal Phase Completion Records. |
| `retrospectives/` | Milestone retrospectives that record what worked, what failed, causes of rework, and follow-up improvements. |
| `README.md` | Project entry point. It should contain only stable high-level information and navigation to current docs. |

Documentation should be treated as part of the product, not as optional commentary.

## 4. ForgeFlow Engineering Workflow

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

### 4.1 Architecture

Architecture starts from the project vision and produces RFCs and ADRs. RFCs
define architecture boundaries, system responsibilities, trade-offs, and
long-term technical direction. ADRs record accepted architectural decisions,
rejected alternatives, and important trade-offs.

Implementation must not begin while required architecture decisions remain
unresolved.

### 4.2 Specification

Specification takes the relevant RFCs and accepted ADRs as input and produces
an OpenSpec change. OpenSpec is the authoritative feature contract and must
include a proposal, design, tasks, and feature specifications. Each change must
state scope, acceptance criteria, non-goals, and constraints.

### 4.3 Grill-Me Design Review

Important features must receive a Grill-Me design challenge before planning.
Grill-Me exposes hidden assumptions, unclear boundaries, scope creep, and
architecture violations. It does not alter architecture decisions; final
decisions remain recorded in RFCs, ADRs, and OpenSpec.

### 4.4 Planning

Planning takes an accepted OpenSpec change as input and produces the canonical
Implementation Plan. The plan is the sole authority for execution order and
must define milestone scope, phase ordering, dependencies, expected file
changes, TDD strategy, and phase acceptance criteria.

For each milestone entering implementation, first use Superpowers or an
equivalent AI-assisted workflow to generate a draft implementation plan. Review
the draft against the accepted OpenSpec, relevant RFCs, and accepted ADRs before
writing the canonical plan. The review must reconcile phase boundaries,
dependencies, scope exclusions, TDD strategy, and acceptance criteria; when a
draft conflicts with repository authority, repository authority prevails and the
conflict is resolved in the canonical plan.

The resulting canonical plan may use useful execution detail from the draft,
but it is the only plan that later phases may treat as authoritative. The draft
may be retained as non-canonical planning evidence and must not create a second
plan that requires synchronization.

Implementation phases must come from the canonical plan. Chat prompts do not
redefine a phase's scope, interface, file list, or acceptance criteria.

### 4.5 Implementation

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

### 4.6 Verification

Every completed phase verifies that tests pass, scope is respected, the Git diff
has been reviewed, and documentation is updated. Before committing, run targeted
tests, cumulative implemented tests, `git diff --check`, and `git status`.

### 4.7 Documentation Authority Hierarchy

```text
Vision
-> RFC
-> ADR
-> OpenSpec
-> Implementation Plan
-> Phase Completion Record
-> Milestone Progress
```

- Vision explains why the work exists.
- RFCs define the architecture.
- ADRs record settled architectural choices.
- OpenSpec defines the feature contract.
- The Implementation Plan defines how to execute the work.
- Phase Completion Records state what a phase actually completed.
- Milestone Progress states where the milestone currently stands.

### 4.8 AI-assisted Development Tools

Superpowers and other AI-assisted development tools are execution aids. They may
help with task decomposition, implementation planning, or review assistance,
but they are not authoritative sources. They must not define architecture,
requirements, or acceptance criteria. Repository documentation remains the
source of truth.

An AI-generated draft plan is a planning input, not a replacement for the
canonical Implementation Plan. Its role is to improve completeness and
executability before the canonical plan is written and reviewed.

### 4.9 Recommended Development Flow

### Phase 0: Project Foundation

Activities:

- create project structure
- preserve the initial architecture draft
- write Project Foundation Proposal
- write `vision.md`
- write `milestones.md`
- write `development-process.md`

Outcome:

- project direction is clear
- Milestone 1 and MVP are separated
- RFC roadmap is ready
- implementation has not started prematurely

### Phase 1: RFC-driven Architecture

Activities:

- write RFC-001 Agent Architecture
- write RFC-002 State Model and Structured Contracts
- write RFC-004 Sandbox and Security Governance
- write RFC-007 DeerFlow Extension Strategy
- draft RFC-003 Tool and MCP Integration in parallel when useful
- draft RFC-005 Observability and Trace Model in parallel when useful
- draft RFC-006 Evaluation Framework in parallel when useful

Outcome:

- cross-cutting architecture decisions are explicit
- role boundaries, state boundaries, security constraints, and DeerFlow integration strategy are documented

### Phase 2: OpenSpec Feature Planning

Activities:

- create OpenSpec changes only for features supported by RFC skeleton decisions
- start with Repository Context Service as the first recommended feature
- include at least `proposal.md`, `design.md`, and `tasks.md` for each feature

Outcome:

- feature scope is implementation-ready
- include/exclude boundaries are explicit
- evaluation and safety expectations are known before coding

### Phase 3: Implementation

Activities:

- write tests or a test plan first
- implement the minimum feature described by OpenSpec
- avoid expanding scope during implementation
- update OpenSpec tasks as work progresses

Outcome:

- implementation matches the agreed feature scope
- code, tests, and docs remain traceable to the spec

### Phase 4: Evaluation and Review

Activities:

- use controlled fixtures for first-version evaluation
- record results, failure modes, scope creep, and security issues
- update RFCs, ADRs, or retrospectives when needed

Outcome:

- behavior is measured, not assumed
- risks and failures are visible
- learning feeds back into architecture and process

### Phase 5: Retrospective and Iteration

Activities:

- write a retrospective after each completed milestone
- do not write temporary implementation details back into `vision.md`
- record major direction changes through RFCs or ADRs

Outcome:

- the project improves deliberately
- future contributors can understand why changes happened

## 5. When to Use Grill-Me

Grill-Me is a design review mechanism. It should pressure-test assumptions, expose scope creep, and sharpen architectural boundaries.

Use Grill-Me:

- after Project Foundation Proposal is drafted
- after each major RFC draft is ready
- when OpenSpec feature scope is unclear
- when scope creep or architecture boundary confusion appears

Do not use Grill-Me:

- for every small function
- for simple implementation tasks whose scope is already clear
- as a replacement for tests
- as a replacement for RFCs or OpenSpec documents

Modes:

- Report mode: produce a one-time architecture review report with critical questions, risks, scope cuts, and readiness checks.
- Interactive mode: ask one question at a time and wait for an answer before continuing.

Grill-Me feedback should be incorporated into the relevant document rather than left only in chat history.

## 6. When to Use RFC

Use an RFC for decisions that affect architecture, project boundaries, safety, state, contracts, runtime integration, or evaluation.

RFCs are appropriate for:

- cross-module architecture changes
- agent role or workflow changes
- state and contract design
- tool permission model
- sandbox security model
- observability and evaluation design
- DeerFlow extension strategy

RFCs are not appropriate for:

- small bug fixes
- single test changes
- documentation wording changes
- local implementation details that do not affect architecture boundaries

Recommended RFC structure:

- Title
- Status
- Context
- Problem Statement
- Goals
- Non-goals
- Proposed Design
- Alternatives Considered
- Trade-offs
- Risks
- Open Questions
- Decision Summary

An RFC may be accepted, rejected, superseded, or deferred.

## 7. When to Use OpenSpec

Use OpenSpec for feature-level planning before implementation.

Good OpenSpec candidates:

- Repository Context Service
- PatchProposal generation
- Validation workflow
- ReviewResult generation
- Draft PR creation

Each OpenSpec change should include at least:

- `proposal.md`
- `design.md`
- `tasks.md`

OpenSpec should not be used to:

- replace `vision.md`
- replace RFCs
- debate unresolved large architecture questions
- cover the entire GitHub Issue to Draft PR MVP in one change

The first OpenSpec change should be Repository Context Service, and only after the relevant RFC skeleton decisions exist.

## 8. When to Use ADR

Use ADRs to record accepted technical decisions.

Example ADR topics:

- Use DeerFlow as upstream reference.
- Treat agents as workflow roles in early phases.
- Use deterministic Repository Context Service.
- Require human approval for high-risk actions.
- Start evaluation with controlled fixtures instead of SWE-bench.

ADRs should be short and durable.

Recommended ADR structure:

- Context
- Decision
- Consequences
- Related RFCs

ADRs should not reopen the full debate. That belongs in RFCs.

## 9. Git Workflow

Use clear, specific commit messages.

Recommended examples:

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

Guidelines:

- documentation changes must be committed
- RFC, OpenSpec, and ADR changes should remain traceable to related code changes
- avoid vague messages such as `update`, `fix stuff`, or `misc changes`
- keep commits focused enough that project evolution can be understood from Git history

## 10. Branching Recommendation

Use a lightweight branch strategy suitable for a personal project that may become open source.

Recommendations:

- keep `main` stable
- use short-lived branches for documents, RFCs, specs, features, and fixes
- avoid heavyweight Git Flow unless project scale requires it later

Example branch names:

```text
docs/rfc-001-agent-architecture
docs/openspec-repository-context
feature/repository-context-service
fix/...
```

Merge only when the relevant document, spec, implementation, tests, or review expectations are satisfied.

## 11. Definition of Ready

A feature is ready for implementation only when:

- `vision.md` clearly defines the current phase boundary
- `milestones.md` identifies the current milestone
- architecture-impacting design has an RFC
- the feature has an OpenSpec change
- includes and excludes are explicit
- safety constraints are explicit
- evaluation approach is explicit
- no major unanswered architecture question blocks implementation

For Milestone 1, this means Repository Context Service must remain a deterministic foundation slice, not a patch generation or PR automation workflow.

## 12. Definition of Done

A feature is done when:

- implementation satisfies OpenSpec tasks
- tests pass
- evaluation fixture is updated or executed
- trace / run summary requirements are satisfied
- documentation is updated
- new architecture decisions are captured in an ADR or RFC update
- milestone retrospective is created if the milestone is complete

Done means the feature is implemented, tested, evaluated, documented, and traceable.

## 13. Scope Control Rules

These rules apply during early ForgeFlow development:

- Do not expand Milestone 1 into the full MVP.
- Repository Context Service v1 does not generate patches.
- The first version does not include Jira, Slack, automatic merge, multi-repo support, or a complex permission system.
- First-version evaluation does not start with SWE-bench.
- Security guardrails must not be postponed entirely to Phase 2.
- Memory does not automatically write in early versions unless a human explicitly confirms stable engineering knowledge.

If a proposed change violates one of these rules, defer it or require an RFC before proceeding.

## 14. Lightweight Implementation Execution

This mode applies to narrowly scoped, accepted implementation phases in every
ForgeFlow milestone. It preserves TDD, scope control, focused commits, formal
completion records, and durable progress without treating AI execution
artifacts as long-term engineering documentation.

### 14.1 Authoritative Inputs

Before starting a phase, read the current feature specification, relevant RFCs,
accepted ADRs, the canonical implementation plan, and the milestone
`progress.md`. Chat prompts may provide context, but they do not define phase
interfaces, file lists, acceptance criteria, or scope.

The authority order for conflicts is:

1. OpenSpec or the accepted feature specification for requirements, acceptance criteria, and exclusions.
2. Accepted ADRs for binding architecture decisions.
3. RFCs for architecture boundaries and deferred decisions.
4. The canonical implementation plan for implementation sequence and task detail.
5. Milestone progress for execution state only.

If these sources conflict or do not identify a safe next phase, stop
implementation and report the conflict. Do not invent an architecture decision
or silently revise an authoritative source.

### 14.2 Phase Identification

Identify the next phase from the canonical implementation plan and the last
completed entry in milestone `progress.md`. Reconcile any mismatch between
execution numbering and the canonical plan before implementation begins.

### 14.3 Test-Driven Development

Each phase follows RED -> GREEN -> REFACTOR:

- add or change a test before production behavior;
- confirm it fails because the current capability is absent or incorrect;
- implement the smallest code that satisfies the current phase;
- run targeted tests, then the complete implemented suite;
- perform only small, phase-scoped refactoring after green.

Tests added after a complete implementation are not a substitute for this
sequence.

### 14.4 Scope Control

Implement exactly one canonical-plan phase at a time. Do not add future-phase
abstractions, modify unrelated modules, or expand feature scope. Missing or
conflicting authority is a stop condition, not permission to fill the gap.

### 14.5 Git and Commit Strategy

Use the branch and worktree assigned to the milestone. Do not create a new
branch or worktree for each phase unless the canonical plan or an accepted
workflow decision explicitly requires it.

Create one focused commit per phase. Before committing, run targeted tests,
the complete implemented test suite, `git diff --check`, and `git status
--short`; inspect generated files and unrelated modifications.

### 14.6 Review Strategy

The default lightweight review is a self-review of the current diff, passing
tests, and scope boundaries. Do not generate subagent briefs, review diffs,
rereview diffs, or long checkpoint reports by default.

Escalate to independent review when a change modifies a feature contract,
security boundary, canonical identity algorithm, external dependency, or
cross-platform security behavior; when it diverges from the canonical plan; or
when explicitly requested by the user.

### 14.7 Phase Completion Records and Progress

Every implementation phase in every milestone must have one formal Phase
Completion Record at
`docs/milestones/<milestone-slug>/phase-<number>-<phase-name>.md`. Derive the
file name from the reconciled canonical implementation-plan phase name in stable
kebab-case; preserve established completion-record file names. Do not derive
future file names from a chat prompt.

All Phase Completion Records use exactly this template. No later phase may use
a shortened or different structure:

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

The `Changed Files` section uses a `File | Change | Purpose` table. The `TDD
and Tests` section records RED, GREEN, any necessary refactor or corrective
iteration, commands, targeted results, and cumulative-suite results. The
record captures completed engineering facts, not agent dispatches, review-diff
bodies, or temporary debugging narration.

After each phase commit, create or update both the Phase Completion Record and
the milestone `progress.md`. The completion record contains the phase detail;
`progress.md` is a concise milestone index with phase status, commit, record
link, current phase, next incomplete phase, and milestone-level reconciliation
items. Neither document redefines requirements, architecture, or sequencing.

`progress.md` does not replace a Phase Completion Record, record detailed
implementation, or define requirements or architecture.

Do not generate Superpowers briefs, review diffs, rereview diffs, or agent
execution reports by default. New architecture decisions belong in ADRs,
requirement changes in OpenSpec, and sequencing changes in the canonical
implementation plan.

After updating the completion record and progress index, provide a concise
summary and stop for user confirmation. Do not automatically begin the next
phase.

### 14.8 Translation Policy

English process documents are canonical. Existing `.zh.md` process documents
are maintained translations for stable, durable process rules. Rolling progress
records and temporary execution artifacts are not translated by default.
