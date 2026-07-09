# RFC-001: Agent Architecture

## Status

Draft

## Context

ForgeFlow is an enterprise autonomous software engineering agent platform built on DeerFlow and LangGraph.

The long-term product vision is a governed, observable, and evaluable software maintenance workflow:

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

The project is currently in Milestone 0: Project Foundation. Milestone 1 is the Repository Context Foundation Slice, not the full MVP. The full GitHub Issue to Draft PR workflow is a later MVP vertical slice.

This RFC defines the first-stage Agent Architecture boundary. It intentionally avoids implementation details, APIs, classes, service boundaries, or microservice decomposition.

## Problem Statement

Autonomous software engineering systems can become unsafe and unmaintainable when every capability is modeled as an unconstrained "agent."

The initial architecture draft identifies useful conceptual roles: Planner, Software Engineer, Validation, Review, and PR. However, if these roles are immediately implemented as independent classes, services, or microservices, the system risks:

- overlapping responsibilities
- unclear control flow
- hidden retry loops
- policy bypasses
- unbounded autonomy
- difficult observability
- premature coupling to runtime internals

ForgeFlow needs a clear first-stage architecture: roles should guide workflow design, while runtime scheduling, retries, stop conditions, and policy enforcement remain controlled by the workflow graph and DeerFlow runtime.

## Goals

- Define Planner, Software Engineer, Validation, Review, and PR as workflow roles in early phases.
- Prevent premature implementation as independent agent classes, services, or microservices.
- Clarify Planner responsibility and explicitly exclude runtime scheduling authority.
- Assign dispatch, branching, retry, and stop-condition enforcement to the workflow graph / DeerFlow runtime.
- Define Repository Context Service as a deterministic service, not an agent.
- Clarify boundaries for Software Engineer, Validation, Review, Human Approval, and PR roles.
- Keep Milestone 1 limited to the Repository Context Foundation Slice.
- Preserve a path toward the later GitHub Issue to Draft PR MVP vertical slice.

## Non-goals

- Define agent class structures.
- Define service APIs.
- Define OpenSpec feature behavior.
- Implement Repository Context Service.
- Implement patch generation.
- Implement validation execution.
- Implement draft PR creation.
- Define full production deployment architecture.
- Expand Milestone 1 into the full MVP.

## Proposed Architecture

ForgeFlow should treat "agents" as workflow roles during the foundation and early milestone phases.

The workflow graph and DeerFlow runtime own execution mechanics. Workflow roles own bounded judgment responsibilities and produce structured outputs.

At a high level:

```text
Task Input
  -> Planner role produces structured plan and stop conditions
  -> Workflow graph / DeerFlow runtime dispatches next steps
  -> Repository Context Service returns deterministic repository facts
  -> Software Engineer role later produces PatchProposal
  -> Validation role later produces ValidationResult
  -> Review role later produces ReviewResult
  -> Human Approval gate handles high-risk decisions
  -> PR role later produces PRResult and draft PR
```

Milestone 1 stops at Repository Context Service. The later roles are defined here to prevent boundary drift, not to start implementation.

## Workflow Roles

### Planner

Planner is a workflow role responsible for structured planning.

Planner may produce or revise:

- structured plan
- success criteria
- stop conditions
- risk assumptions

Planner must not:

- own runtime scheduling
- execute tools directly outside workflow policy
- perform hidden retries
- override stop conditions
- approve high-risk actions
- mutate repository files
- create pull requests

Planner output should guide the workflow graph. It should not replace the workflow graph.

### Software Engineer

Software Engineer is a workflow role responsible for patch intent in later milestones.

In the later MVP vertical slice, this role may use controlled sandbox edit tools to produce a diff. It must not write files directly or bypass sandbox governance, patch boundary policy, or security policy.

Software Engineer may later produce:

- root cause hypothesis
- fix strategy
- candidate changed files
- structured `PatchProposal`
- risk flags
- evidence references

Software Engineer must not:

- directly create PRs
- approve high-risk changes
- run an unbounded repair loop
- modify sensitive files without policy approval
- bypass sandbox edit tools

### Validation

Validation is a workflow role responsible for test execution and failure explanation.

Validation may later produce:

- executed command summaries
- parsed test results
- validation status
- failure analysis
- retry-relevant findings
- `ValidationResult`

Validation must not:

- directly fix failures
- generate patches
- silently expand scope
- retry indefinitely
- approve PR creation

If validation fails and retry policy allows another attempt, the workflow graph controls the repair loop and returns to the Software Engineer role for a revised `PatchProposal`.

### Review

Review is a workflow role responsible for blocking-level review and risk assessment.

Review may later produce:

- `ReviewResult`
- risk flags
- blocking issues
- sensitive file findings
- test sufficiency findings
- recommendation on whether draft PR creation is allowed by policy

Review must not:

- replace Human Approval
- merge PRs
- approve high-risk actions
- perform broad style-only review as a first-stage goal
- mutate code

Review is an automated risk and quality gate. It is not the human approval authority.

### PR

PR is a workflow role responsible for draft PR creation in the later MVP vertical slice.

PR may create a branch, commit, and draft pull request only when:

- `ReviewResult` permits draft PR creation
- policy allows the action
- required human approval gates have been satisfied when applicable

PR body content must derive from structured contracts and evidence, such as:

- `PatchProposal`
- `ValidationResult`
- `ReviewResult`
- trace summary
- policy decisions

PR must not freely re-summarize the run in a way that loses contract traceability.

## Runtime Responsibilities

The workflow graph / DeerFlow runtime owns execution mechanics.

Runtime responsibilities include:

- dispatching workflow steps
- selecting branches
- enforcing stop conditions
- controlling retries
- applying middleware
- invoking tools through policy boundaries
- maintaining runtime state
- coordinating checkpoints
- recording trace hooks where supported
- routing to Human Approval gates

Planner does not own these responsibilities.

This distinction prevents Planner from becoming an uncontrolled super-agent and keeps execution behavior inspectable.

## Role Boundaries

| Boundary | Decision |
|---|---|
| Agents as implementation units | In early phases, Planner, Software Engineer, Validation, Review, and PR are workflow roles, not classes, services, or microservices. |
| Planner vs runtime | Planner produces plan artifacts; workflow graph / DeerFlow runtime performs scheduling and retry control. |
| Repository facts | Repository Context Service provides deterministic repository facts. Agents must not invent repository state. |
| Software Engineer edits | Later diff generation must go through controlled sandbox edit tools and policy checks. |
| Validation repair | Validation explains failures but does not repair them. Repair loops return to Software Engineer through workflow control. |
| Review vs approval | Review produces risk findings; Human Approval is a separate gate. |
| PR creation | PR role creates draft PR only when review and policy allow. |

## Human Approval Gates

Human Approval is an independent workflow gate, not internal behavior of the Review role.

Human Approval should be required for high-risk actions such as:

- sensitive file modification
- high-risk command execution
- excessive diff size or changed file count
- validation retry exhaustion
- blocking or high-risk `ReviewResult`
- non-draft PR creation
- merge
- deployment-related changes

This RFC does not define the full approval policy. That belongs primarily in RFC-004: Sandbox and Security Governance.

## Relationship with DeerFlow

DeerFlow is the upstream framework and runtime reference for ForgeFlow.

DeerFlow is expected to provide or inform:

- graph/runtime primitives
- thread state primitives
- tool orchestration
- checkpointing
- middleware hooks
- tracing hooks

ForgeFlow owns the software engineering platform layer:

- workflow role definitions
- software engineering domain state
- structured contracts
- Repository Context Service boundary
- sandbox governance
- security policy
- patch boundary policy
- PR workflow
- evaluation framework
- product-level run summary

This RFC assumes ForgeFlow builds on DeerFlow without becoming a shallow fork. The exact extension map belongs in RFC-007: DeerFlow Extension Strategy.

## Relationship with Milestone 1

Milestone 1 is Repository Context Foundation Slice.

Milestone 1 should implement or specify only the deterministic repository context capability. It should provide:

- repo workspace input
- query and optional issue text input
- file search
- text search
- simple symbol search if cheap and language-agnostic
- evidence references
- relevant files
- simple test command hints
- `RepositoryContextResult`

Milestone 1 must not include:

- patch generation
- code editing
- test execution
- draft PR creation
- autonomous repair
- similar issue retrieval
- full dependency graph
- automatic memory write

This RFC defines later workflow roles so their boundaries are known, but it does not authorize implementing the full Draft PR workflow in Milestone 1.

## Alternatives Considered

### Alternative 1: Implement Each Agent as a Separate Class Immediately

This would make role boundaries concrete early.

Rejected for now because it risks encoding premature abstractions before workflow and contract boundaries are validated. It may also encourage each "agent" to own control flow and retries independently.

### Alternative 2: Implement Each Agent as a Separate Service or Microservice

This would create strong operational separation.

Rejected for early phases because it adds unnecessary deployment, versioning, network, observability, and policy complexity before the platform has proven its core workflow boundaries.

### Alternative 3: Single Super-Agent Owns Planning, Editing, Testing, Review, and PR Creation

This is the fastest demo path.

Rejected because it violates ForgeFlow's governance model. It would make tool evidence, policy enforcement, validation retry, human approval, and evaluation harder to inspect.

### Alternative 4: Treat Repository Context as an Agent

This would allow flexible repository investigation.

Rejected for Milestone 1 because repository facts should come from deterministic services. Repository Context Service should return evidence-backed file/search/test hints, not perform autonomous repair reasoning.

## Trade-offs

Benefits:

- clearer responsibility boundaries
- lower risk of premature abstraction
- easier observability and evaluation
- safer retry control
- better separation between judgment, execution, and approval
- smoother path to deterministic Repository Context Service in Milestone 1

Costs:

- slower path to a flashy end-to-end demo
- more documentation and review before implementation
- some role boundaries may need revision after real feature work begins
- workflow graph design becomes important earlier

The trade-off is intentional. ForgeFlow optimizes for maintainable enterprise automation, not a fast but uncontrolled demo.

## Risks

- Roles may remain too abstract if not later grounded in OpenSpec changes.
- The workflow graph may become overly complex if every small decision becomes a separate node.
- Planner may still drift toward hidden orchestration unless prompt and contract boundaries are enforced.
- Review may be mistaken for Human Approval unless UI, policy, and contract language remain explicit.
- PR body generation may lose traceability if it is allowed to free-form summarize instead of referencing structured contracts.
- Milestone 1 could expand into patch generation unless scope rules are enforced.

## Open Questions

- At what milestone should workflow roles become concrete implementation units, if ever?
- Which DeerFlow graph and middleware extension points should represent these roles?
- What is the minimal plan contract Planner should produce before Repository Context Service begins?
- How should workflow graph retry policy reference `ValidationResult` and `PatchProposal` lineage?
- What exact fields should `ReviewResult` include to distinguish automated review from human approval?
- Which policy decisions must be available before PR role can create a draft PR?
- How should role-level trace spans map to product-level run summaries?

## Decision Summary

For early ForgeFlow development:

- Planner, Software Engineer, Validation, Review, and PR are workflow roles, not immediate classes, services, or microservices.
- Planner produces structured plans, success criteria, stop conditions, and risk assumptions.
- Planner does not own runtime scheduling.
- Workflow graph / DeerFlow runtime owns dispatch, branching, retry control, and stop-condition enforcement.
- Repository Context Service is a deterministic service, not an agent.
- Software Engineer may later produce diffs only through governed sandbox edit tools.
- Validation runs tests, parses results, and explains failures; it does not fix failures directly.
- Repair loops are controlled by the workflow graph and return to Software Engineer for revised `PatchProposal`.
- Review produces `ReviewResult`, risk flags, and blocking issues; it does not replace Human Approval.
- Human Approval is an independent gate.
- PR role creates draft PR only when `ReviewResult` passes and policy allows it.
- PR body content must derive from structured contracts and evidence.
- Milestone 1 remains limited to Repository Context Foundation Slice.
- The full GitHub Issue to Draft PR workflow remains a later MVP vertical slice.
