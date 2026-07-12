# ForgeFlow Development Lifecycle

## 1. Recommended Development Flow

### Phase 0: Project Foundation

Activities:

- create project structure
- preserve the initial architecture draft
- write Project Foundation Proposal
- write product vision documents
- write milestone roadmap documents
- write engineering process documents

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
## 2. Definition of Ready

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

## 3. Definition of Done

A feature is done when:

- implementation satisfies OpenSpec tasks
- tests pass
- evaluation fixture is updated or executed
- trace / run summary requirements are satisfied
- documentation is updated
- new architecture decisions are captured in an ADR or RFC update
- milestone retrospective is created if the milestone is complete

Done means the feature is implemented, tested, evaluated, documented, and traceable.

## 4. Scope Control Rules

These rules apply during early ForgeFlow development:

- Do not expand Milestone 1 into the full MVP.
- Repository Context Service v1 does not generate patches.
- The first version does not include Jira, Slack, automatic merge, multi-repo support, or a complex permission system.
- First-version evaluation does not start with SWE-bench.
- Security guardrails must not be postponed entirely to Phase 2.
- Memory does not automatically write in early versions unless a human explicitly confirms stable engineering knowledge.

If a proposed change violates one of these rules, defer it or require an RFC before proceeding.
