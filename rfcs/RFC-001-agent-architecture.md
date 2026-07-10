# RFC-001: Agent Architecture

## Status

Draft

Review stage: Grill-Me feedback has been incorporated as current draft decisions. RFC-002 and RFC-004 have validated their adjacent contract/state and security boundaries at skeleton level. Acceptance remains blocked on RFC-007 concrete DeerFlow extension assumptions, including pinned DeerFlow revision and extension-point capability assessment.

## Current Draft Decisions

- Milestone 1 must not create concrete Planner, Software Engineer, Validation, Review, or PR implementation units.
- Workflow role promotion requires an accepted OpenSpec.
- Planner output is declarative, advisory, and non-binding.
- Repository Context Service must not use LLM reasoning in Milestone 1.
- Validation output is diagnostic, not prescriptive.
- Review recommends draft PR readiness; policy decides final eligibility.
- PR packages policy-eligible artifacts and must not modify the patch.
- DeerFlow runtime and ForgeFlow workflow graph responsibilities are separate.
- Detailed contract, policy, runtime-extension, trace, tool, and evaluation decisions are deferred to other RFCs.
- RFC-001 remains Draft until RFC-007 records the concrete DeerFlow extension assumptions required to validate adjacent runtime boundaries.

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

### Planner Output Boundary

Planner output is declarative input to the workflow graph, not an executable workflow definition.

Planner may produce advisory planning artifacts such as:

- task type
- goal
- assumptions
- success criteria
- risk level
- candidate context needs
- recommended next logical step
- constraints
- stop-condition candidates

Planner must not produce:

- binding execution branches
- retry loops
- tool-call sequences
- node execution order
- sandbox edit instructions
- validation execution authority
- approval bypass logic
- PR creation instructions

The workflow graph / DeerFlow runtime may consume Planner output, but it owns all executable control decisions, including dispatch, branching, retry policy, tool sequencing, stop-condition enforcement, middleware application, checkpoint coordination, and Human Approval routing.

Planner output must not weaken, override, or redefine runtime policy, stop conditions, retry budgets, approval gates, sandbox governance, or security constraints.

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

### Validation Output Boundary

Validation output is diagnostic, not prescriptive.

Validation may report:

- command executed
- pass/fail status
- failing test names
- error excerpts
- structured failure data
- suspected failure category
- whether the failure appears related to the current patch
- retry-relevant facts
- stop reason when retry budget is exhausted

Validation must not produce:

- revised fix strategies
- patch instructions
- code edits
- next-patch content
- changed-file directives
- direct commands to the Software Engineer role

The workflow graph / DeerFlow runtime may pass `ValidationResult` back to the Software Engineer role when retry policy allows another attempt, but the Software Engineer role owns any revised `PatchProposal`.

Validation explains failure; it does not decide what to fix next.

### Review

Review is a workflow role responsible for blocking-level review and risk assessment.

Review may later produce:

- `ReviewResult`
- risk flags
- blocking issues
- sensitive file findings
- test sufficiency findings
- non-binding recommendation on draft PR readiness

Review must not:

- replace Human Approval
- merge PRs
- approve high-risk actions
- produce final authorization fields such as `approved_for_pr`
- perform broad style-only review as a first-stage goal
- mutate code

Review is an automated risk and quality gate. It is not the human approval authority.

### Review and PR Eligibility Boundary

Review is advisory with respect to draft PR creation.

Review may produce:

- blocking issues
- risk flags
- sensitive file findings
- test sufficiency findings
- policy-relevant observations
- a non-binding recommendation such as `recommend_draft_pr`

Review must not produce final authorization fields such as `approved_for_pr`, bypass policy checks, replace Human Approval, or directly permit PR creation.

Final draft PR eligibility is computed by the workflow graph / DeerFlow runtime and policy middleware from:

- `ReviewResult`
- security policy
- diff policy
- sensitive file policy
- validation result
- human approval state
- PR action policy

Review can recommend draft PR readiness; policy decides whether draft PR creation is allowed.

### PR

PR is a workflow role responsible for draft PR creation in the later MVP vertical slice.

PR may package policy-eligible artifacts into GitHub side effects only when:

- `ReviewResult` recommends draft PR readiness
- policy allows the action
- required human approval gates have been satisfied when applicable

PR body content must derive from structured contracts and evidence, such as:

- `PatchProposal`
- `ValidationResult`
- `ReviewResult`
- trace summary
- policy decisions

PR must not freely re-summarize the run in a way that loses contract traceability.

### PR Side-Effect Boundary

PR is a side-effect role. Each GitHub side effect must be policy-gated separately.

For the first Draft PR MVP:

- branch creation is policy-gated
- commit creation is policy-gated and must use the policy-eligible patch artifact
- draft PR creation is policy-gated and must use structured contracts and evidence
- non-draft PR creation requires explicit Human Approval
- merge is out of scope

Commit creation must use the patch artifact that has already passed required validation, review, policy, and approval gates when applicable.

Draft PR creation must use structured contracts and evidence such as:

- `PatchProposal`
- `ValidationResult`
- `ReviewResult`
- trace summary
- policy decisions
- human approval state when required

PR must not modify, reinterpret, expand, or regenerate the patch while creating a branch, commit, or draft pull request.

PR packages approved artifacts; it does not produce or alter code changes.

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

### DeerFlow Runtime and ForgeFlow Workflow Graph Boundary

DeerFlow runs the graph; ForgeFlow defines the software-engineering workflow.

DeerFlow runtime owns generic execution infrastructure, including:

- graph execution primitives
- thread and run state primitives
- checkpointing
- tool invocation framework
- middleware hooks
- tracing hooks
- other runtime-level mechanisms

ForgeFlow workflow graph owns software-engineering orchestration semantics, including:

- role sequencing
- node definitions
- transition policy
- retry budgets
- stop-condition interpretation
- contract routing
- policy-gate placement
- Human Approval node placement
- product-level run summary semantics
- evaluation semantics

ForgeFlow must not assume that DeerFlow provides product-specific approval, retry, patch, review, validation, PR, or security policy. Those decisions belong to ForgeFlow contracts, workflow graph design, and policy layers.

ForgeFlow should also avoid duplicating generic runtime primitives that DeerFlow already provides, unless a later RFC or OpenSpec proves that a ForgeFlow-specific extension is required.

## Role Boundaries

| Boundary | Decision |
|---|---|
| Agents as implementation units | In early phases, Planner, Software Engineer, Validation, Review, and PR are workflow roles, not classes, services, or microservices. |
| Planner vs runtime | Planner produces plan artifacts; workflow graph / DeerFlow runtime performs scheduling and retry control. |
| Repository facts | Repository Context Service provides deterministic repository facts. Agents must not invent repository state. |
| Software Engineer edits | Later diff generation must go through controlled sandbox edit tools and policy checks. |
| Validation repair | Validation explains failures but does not repair them. Repair loops return to Software Engineer through workflow control. |
| Review vs approval | Review produces risk findings; Human Approval is a separate gate. |
| PR creation | PR role packages policy-eligible artifacts only when review readiness, policy, and approval state allow each GitHub side effect. |

### Milestone 1 Implementation Constraint

During Milestone 1, Planner, Software Engineer, Validation, Review, and PR must remain workflow roles only.

Milestone 1 must not create concrete implementation units for these roles, including but not limited to:

- role-specific agent classes
- role-specific service objects
- role-specific modules such as `planner_agent.py`, `software_engineer_agent.py`, `validation_agent.py`, `review_agent.py`, or `pr_agent.py`
- independent role-level orchestration loops
- role-owned retry, scheduling, or stop-condition logic

Workflow roles may appear in documentation, trace labels, future graph design, and structured contract discussions. They must not become concrete classes, services, modules, microservices, or independent orchestration objects during Milestone 1.

Milestone 1 implementation should remain limited to Repository Context Service and deterministic supporting behavior.

### Role Promotion Rule

Planner, Software Engineer, Validation, Review, and PR are workflow roles by default.

A workflow role may be promoted to a concrete implementation unit only when an accepted OpenSpec explicitly demonstrates that the role requires an independent implementation boundary.

The OpenSpec must explain why the responsibility cannot remain one of the following:

- a workflow graph node
- a plain function
- a deterministic service
- a middleware-controlled behavior
- a structured contract-producing step
- a runtime-owned dispatch or retry decision

The OpenSpec must answer at least:

- what boundary the role needs
- why the workflow graph / DeerFlow runtime should not own the behavior
- what contracts the role consumes and produces
- what side effects, if any, the role performs
- how the role is traced and evaluated
- how policy constrains the role
- how retry, stop conditions, and failure handling are controlled
- how the role avoids responsibility overlap with other roles
- why promoting the role does not expand the current milestone scope

Until such an OpenSpec is accepted, workflow roles may appear only in documentation, trace labels, future graph design, and contract discussions. They must not become concrete classes, services, modules, microservices, or independent orchestration objects.

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

### Repository Context Determinism Boundary

During Milestone 1, Repository Context Service must be deterministic in both interface and core behavior.

Repository Context Service may rely on:

- file search
- text search
- cheap language-agnostic symbol hints
- project configuration
- repository conventions
- evidence references

Repository Context Service must not use LLM reasoning to:

- decide relevant files
- infer root cause
- summarize code meaning
- select repair strategy
- rank results by unverifiable semantic judgment
- recommend tests without evidence

Repository Context Service is the source of repository facts. Those facts must be evidence-backed, reproducible, and traceable to repository content or project configuration.

If LLM-assisted ranking, summarization, or relevance explanation is introduced in a later milestone, it must be approved by a separate RFC or OpenSpec, clearly separated from deterministic repository facts, and marked as non-authoritative assistance.

## Deferred Decisions / Owned by Other RFCs

RFC-001 defines role boundaries, runtime ownership boundaries, and first-stage Agent Architecture constraints only far enough to prevent role creep and milestone expansion. It does not own detailed contract schemas, sandbox policy, DeerFlow extension mechanics, trace formats, tool capability policy, or evaluation metrics.

The following decisions are intentionally delegated to later RFCs:

- RFC-002 owns exact contract schemas, runtime / durable / memory state separation, contract versioning, evidence reference format, and retry lineage.
- RFC-003 owns tool and MCP capability levels, tool evidence-returning requirements, and tool exposure rules.
- RFC-004 owns sandbox command, path, network, and resource policy; sensitive file policy; diff thresholds; secret scanning; cost and retry caps; and approval policy.
- RFC-005 owns product-level trace shape, run summary structure, and user-facing evidence presentation.
- RFC-006 owns evaluation fixtures, metrics, benchmark design, regression criteria, and success measurement.
- RFC-007 owns DeerFlow extension points, graph integration, thread state extension, tool registry integration, checkpoint mapping, middleware hooks, and trace hook mapping.

Examples in RFC-001 are boundary examples unless explicitly marked as normative schemas. Later RFCs and accepted OpenSpecs must refine these delegated areas without violating the role and control boundaries defined here.

## Acceptance Preconditions

RFC-001 should remain in Draft until the skeletons for RFC-002, RFC-004, and RFC-007 exist and confirm that their adjacent boundaries do not contradict this Agent Architecture.

Before RFC-001 is promoted to Accepted:

- RFC-002 must confirm that contract schemas, state separation, evidence references, and retry lineage can support the role boundaries defined here. This condition is satisfied at skeleton level by RFC-002's RFC-001 Acceptance Support section.
- RFC-004 must confirm that sandbox policy, approval policy, retry caps, sensitive file policy, diff policy, and security governance can enforce the side-effect and authority boundaries defined here. This condition is satisfied at skeleton level by RFC-004's RFC-001 Security Acceptance Criteria section.
- RFC-007 must confirm that DeerFlow graph/runtime extension points can support the runtime and workflow graph responsibility split defined here. This condition is not yet satisfied because RFC-007 requires a pinned or immutably recorded DeerFlow revision, a documented extension-point capability assessment, and recorded integration assumptions before it can unblock RFC-001 acceptance.

Until acceptance, the constraints in this RFC should be treated as current draft decisions for Milestone 1 planning. They may guide OpenSpec drafting and implementation scoping, but they should not be treated as final schemas or final DeerFlow integration mechanics.

## Acceptance Review Notes

RFC-001 has been reviewed against RFC-002, RFC-004, RFC-007, and the Milestone 1 planning documents.

Current review status:

- RFC-002 satisfies the contract and state-model validation needed by RFC-001 at skeleton level.
- RFC-004 satisfies the sandbox, security, policy, approval, and side-effect validation needed by RFC-001 at skeleton level.
- RFC-007 defines the correct DeerFlow / ForgeFlow ownership boundary, but it explicitly requires additional concrete assumptions before unblocking RFC-001 acceptance.

RFC-001 should remain Draft until RFC-007 records:

- the pinned or immutably recorded DeerFlow upstream revision used for assessment
- the DeerFlow extension-point capability assessment for Milestone 1 read-only Repository Context assumptions
- confirmation that Milestone 1 does not depend on DeerFlow core modifications, temporary patches, or unmerged patches
- any unsupported extension assumptions, integration gaps, or upstream risks as explicit risks or open questions

Once those RFC-007 conditions are documented and do not contradict this RFC, RFC-001 may be promoted to Accepted as the Agent Architecture baseline and Milestone 1 scope guard.

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
- Repository Context Service may become an implicit agent if LLM reasoning is introduced without a later RFC or OpenSpec.

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
- Milestone 1 must not create concrete implementation units for these roles.
- Promoting a workflow role to a concrete implementation unit requires an accepted OpenSpec.
- Planner produces structured plans, success criteria, stop conditions, and risk assumptions.
- Planner does not own runtime scheduling.
- Planner output is declarative, advisory, and non-binding.
- DeerFlow runtime owns generic execution infrastructure; ForgeFlow workflow graph owns software-engineering orchestration semantics.
- Repository Context Service is a deterministic service, not an agent.
- Repository Context Service must not use LLM reasoning in Milestone 1.
- Software Engineer may later produce diffs only through governed sandbox edit tools.
- Validation runs tests, parses results, and explains failures; it does not fix failures directly or prescribe next patches.
- Repair loops are controlled by the workflow graph and return to Software Engineer for revised `PatchProposal`.
- Review produces `ReviewResult`, risk flags, blocking issues, and non-binding draft PR readiness recommendations; it does not replace Human Approval.
- Human Approval is an independent gate.
- PR role packages policy-eligible artifacts only; each GitHub side effect is separately policy-gated.
- PR body content must derive from structured contracts and evidence.
- Detailed contract, policy, runtime-extension, trace, tool, and evaluation decisions are deferred to later RFCs.
- RFC-001 remains Draft until RFC-007 records the concrete DeerFlow extension assumptions required to validate adjacent runtime boundaries.
- Milestone 1 remains limited to Repository Context Foundation Slice.
- The full GitHub Issue to Draft PR workflow remains a later MVP vertical slice.
