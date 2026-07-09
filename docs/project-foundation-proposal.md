# ForgeFlow Project Foundation Proposal

Status: Draft  
Type: Foundation Design Artifact  
Last Updated: 2026-07-09

This document captures the initial project foundation for ForgeFlow before formal RFCs are written.

It is not the final architecture specification.  
Authoritative architectural decisions will be defined in the RFC documents under `rfcs/`.

Related documents:
- `docs/vision.md`
- `docs/milestones.md`
- `docs/development-process.md`
- `rfcs/`

## 1. Positioning

ForgeFlow is an enterprise autonomous software engineering agent platform built on DeerFlow and LangGraph.

Long-term target workflow:

```text
GitHub Issue / Failed CI / Error Log
  -> task analysis
  -> repository understanding
  -> bug diagnosis
  -> code patch
  -> validation
  -> review
  -> draft pull request
  -> human approval
  -> evaluation / memory update
```

This long-term workflow is the product direction, not the first implementation step.

ForgeFlow should not become a generic coding chatbot, a thin DeerFlow rename, or a toy LangChain demo. Its product boundary is automated software maintenance with observable, reviewable, reversible outputs. The primary long-term delivery artifact is a draft pull request backed by evidence, tests, trace data, explicit risk review, and human approval gates.

Core principles:

- Agents judge, tools execute, and deterministic services provide repository facts.
- Repository Context and Code Intelligence are infrastructure, not agent personas.
- Cross-role handoff must use structured contracts.
- High-risk actions require human approval.
- Validation has bounded retries and bounded cost.
- Memory stores stable engineering knowledge only.
- Observability and evaluation are product capabilities from day one.
- Security guardrails must exist before the MVP vertical slice, not after it.

## 2. Milestone 1 vs MVP

The most important scope correction is to separate the first foundation slice from the later MVP vertical slice.

### Milestone 1: Repository Context Service / Foundation Slice

Milestone 1 builds the smallest useful repository-context capability that later PatchProposal and autonomous repair workflows can rely on.

Milestone 1 is not the full MVP. It should not create patches, modify code, create pull requests, or run an autonomous repair loop.

Milestone 1 responsibilities:

- accept a repo workspace
- accept a query
- accept optional issue text
- return relevant files
- return evidence references
- return simple file/text search results
- return candidate test command hints from config or conventions
- output a structured `RepositoryContextResult`

Milestone 1 does not include:

- patch generation
- code modification
- pull request creation
- automatic repair
- complex issue history retrieval
- full dependency graph
- full CI integration
- memory write
- multi-repo context
- large-scale embedding index
- language-specific deep static analysis

### MVP: GitHub Issue to Draft PR Vertical Slice

The MVP is a later vertical slice:

```text
GitHub Issue
  -> Sandbox
  -> Repository Context
  -> PatchProposal
  -> Validation
  -> Review
  -> Draft PR
```

This MVP should start only after the foundation RFC decisions and the Repository Context Service spec are clear. It remains intentionally narrow:

- single repository
- GitHub Issue input first
- sandbox execution
- local validation first
- draft PR output only
- no automatic merge
- no automatic deployment
- no Jira
- no Slack approval
- no multi-repo orchestration
- no IDE plugin

## 3. Recommended Repository Structure

Recommended initial structure:

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

Defer `src/` and `tests/` until the first accepted OpenSpec feature is ready for implementation. Creating source directories too early invites fake abstractions, premature APIs, and agent classes before workflow boundaries are settled.

Directory rationale:

| Directory | Purpose |
|---|---|
| `docs/` | Stable project-level documents: vision, foundation proposal, architecture overview, glossary, milestone plans. |
| `rfcs/` | Cross-cutting design decisions before implementation. RFCs compare options and record current recommendations before ADRs freeze decisions. |
| `specs/` | OpenSpec-style feature changes. Each feature should have concrete scope, design, tasks, and acceptance criteria. |
| `adr/` | Immutable architecture decision records after decisions are made. RFCs debate; ADRs record. |
| `retrospectives/` | Post-milestone learning from implementation, evaluation, incidents, and process gaps. |
| `scripts/` | Project automation helpers once needed, such as doc checks, eval runners, or setup commands. Keep empty except for a README initially. |
| `third_party/` | Metadata and references for upstream dependencies such as DeerFlow. Avoid copying upstream source initially. |

Add later, only when needed:

| Future Directory | Add When |
|---|---|
| `src/` | A feature spec is accepted and implementation begins. |
| `tests/` | There is executable code or spec-driven validation to test. |
| `examples/` | There is a working vertical slice worth demonstrating. |
| `evals/` | Evaluation fixtures and runners become concrete artifacts. |
| `infra/` | Sandbox, deployment, or observability infrastructure becomes real. |

## 4. DeerFlow and ForgeFlow Boundary

DeerFlow is the upstream framework/reference. ForgeFlow is the enterprise software-maintenance application/platform layer built around it.

### DeerFlow Responsibilities

DeerFlow should own or provide the foundation for:

- graph/runtime/thread primitives
- tool orchestration primitives
- checkpoint and state persistence primitives
- middleware hook primitives
- tracing hook primitives

### ForgeFlow Responsibilities

ForgeFlow should own:

- software-engineering domain state
- structured contracts
- `RepositoryContextResult`
- `PatchProposal`
- `ValidationResult`
- `ReviewResult`
- `PRResult`
- Repository Context Service
- sandbox governance
- security policy
- patch boundary policy
- PR workflow
- evaluation framework
- product-level run summary

### Integration Strategy

Options:

| Option | Pros | Cons | Current Fit |
|---|---|---|---|
| Git submodule | Pin exact upstream revision; keeps ForgeFlow separate; supports reproducible reference. | Adds submodule workflow overhead; premature before extension points are known. | Good after RFC-007. |
| Separate local reference repository | Zero coupling; easiest for early exploration; avoids vendoring decisions before architecture settles. | Not self-contained; contributors must fetch DeerFlow separately. | Best for current foundation stage. |
| Direct fork of DeerFlow | Easy to modify internals; full control. | Encourages drifting into a renamed fork; weakens ForgeFlow's product/platform boundary. | Not recommended now. |
| Copy DeerFlow source | Fast local hacking. | High maintenance cost; unclear provenance; hard upstream sync. | Avoid. |

Current recommendation: keep DeerFlow as a separate local reference repository and document the reference in `third_party/README.md` when the project structure is initialized.

RFC-007 must define the actual extension map before implementation: graph nodes, thread state extension, tool registry, checkpointing, middleware hooks, trace hooks, and any upstream changes ForgeFlow may need.

## 5. Agent Roles and Workflow Boundaries

Planner, Software Engineer, Validation, Review, and PR are workflow roles at this stage. They should not yet be implemented as independent classes, services, or long-lived agents.

The first architecture decision is role boundary, not code structure.

| Role | Current Boundary |
|---|---|
| Planner | Generates and revises a structured plan, success criteria, risk assumptions, and stop conditions. It does not own runtime scheduling. |
| Workflow Graph / Runtime | Executes the graph, performs dispatch, applies middleware, enforces stop conditions, and controls retry transitions. |
| Software Engineer | Produces patch intent and, in the later MVP, may use controlled sandbox edit tools to produce a diff. It cannot write files directly or bypass patch/security policy. |
| Validation | Runs validation commands and explains failures. It does not repair failures directly. |
| Repair Loop | A workflow-level transition that may return to Software Engineer for a revised `PatchProposal` when retry policy allows. |
| Review | Produces `ReviewResult`, risk flags, and blocking issues. It does not execute human approval. |
| Human Approval | Independent gate for sensitive actions, high-risk changes, exhausted validation, non-draft PR creation, merge, or policy escalation. |
| PR | Creates branch/commit/draft PR only after `ReviewResult` passes and policy allows it. Commit message and PR body must derive from contracts and evidence, not free-form re-summarization. |

This prevents Planner from becoming a super-agent and prevents Validation, Review, and PR responsibilities from overlapping.

## 6. Structured Contracts

ForgeFlow's workflow must be contract-driven. Contracts should be defined before production code, but full JSON schemas are not required in the foundation proposal.

Contracts to define in RFC-002:

- `RepositoryContextResult`
- `PatchProposal`
- `ValidationResult`
- `ReviewResult`
- `PRResult`

Each contract should consider these field categories:

- `schema_version`
- `run_id`
- source evidence references
- artifact IDs
- risk flags
- policy decisions
- retry lineage
- stop reason
- `created_at`
- `updated_at`
- immutable fields
- mutable fields

Minimum direction:

| Contract | Purpose |
|---|---|
| `RepositoryContextResult` | Evidence-backed repository context: relevant files, search results, symbol hints if cheap, and test command hints. |
| `PatchProposal` | Root cause, fix strategy, changed files, diff artifact reference, validation commands, risk flags, and limitations. |
| `ValidationResult` | Commands run, result status, parsed failures, failure analysis, retry count, retry lineage, and stop reason. |
| `ReviewResult` | Blocking issues, risk level, sensitive file findings, test sufficiency, approval-for-draft-PR recommendation, and required human gates. |
| `PRResult` | Branch, commit, draft PR URL, linked issue, PR body artifact, CI/check status if available, and policy decisions used. |

Contracts should reference artifacts instead of embedding large source files, full logs, or large diffs.

## 7. State Model

State must be split into three categories.

### Runtime State

Runtime State is mutable, short-lived working state for the current workflow execution.

Examples:

- current plan step
- current retry count
- current repository workspace path
- transient tool results
- active stop conditions
- temporary validation output
- intermediate failed patch attempts

Runtime State may extend DeerFlow thread/run state, but it should not be treated as durable audit history.

### Durable Run Summary / Audit Record

Durable Run Summary is persisted for traceability, review, PR explanation, and evaluation.

Persist:

- run ID and trace ID
- task source and normalized task summary
- plan and plan revisions
- evidence references
- contract artifacts
- changed file list
- root cause summary
- validation commands and summarized results
- review result and risk flags
- policy decisions
- retry count and stop reason
- token/cost/time metrics
- PR result
- human feedback

Do not persist raw cloned repository content, full source files, unnecessary full logs, secrets, or unredacted prompts/responses by default.

### Long-Term Memory

Long-term Memory stores only stable engineering knowledge.

Allowed examples:

- repository test command conventions
- stable architectural notes
- important paths
- accepted engineering conventions
- validated recurring failure patterns

Not allowed:

- source code
- secrets
- temporary logs
- unverified reasoning
- large diffs
- failed intermediate attempts
- customer-sensitive data

First-version Memory should default to no automatic writes. If memory writes exist at all, they must require human confirmation and should only store stable repository conventions or validated engineering knowledge.

## 8. Security and Governance Guardrails

Security governance cannot be deferred entirely to Phase 2. The MVP vertical slice edits code, runs commands, and creates draft PRs, so minimum guardrails must exist before that slice.

MVP-precondition guardrails:

- command policy
- path policy
- network policy
- resource limits
- diff threshold
- secret scan hook
- sensitive file policy
- cost and retry caps
- human approval gates

Sensitive files and areas must include at least:

- `.github/workflows`
- deployment configuration
- infrastructure files
- auth code
- crypto code
- permission code
- production configuration

Human approval gates should trigger before or after these events:

- high-risk command execution
- sensitive file modification
- diff size or changed file count exceeds threshold
- validation retry exhaustion
- `ReviewResult` contains blocking or high-risk findings
- non-draft PR creation
- merge
- deployment-related change

Dangerous command protection should not rely only on a string blacklist. RFC-004 should define allowlists, denylists, path policy, diff policy, resource limits, network policy, secret scanning, and approval escalation together.

## 9. Repository Context Service Scope

Repository Context Service is the first OpenSpec candidate and the Milestone 1 foundation slice.

It must be a deterministic service, not a Repository Context Agent.

### Include in First Version

- repo workspace input
- query input
- optional issue text input
- file search
- text search
- simple symbol search if cheap and tooling is already available
- test command hints from config and conventions
- evidence references
- structured `RepositoryContextResult`
- trace hooks that record summary and evidence references, not full source snapshots

### Exclude from First Version

- patch generation
- code modification
- automatic repair
- similar issue retrieval
- full dependency graph
- large-scale embedding index
- GitHub issue or PR history ingestion
- multi-repo context
- language-specific deep static analysis
- full CI integration
- memory write

Open questions for the spec:

- Is the service language-agnostic in the first version?
- Does it read git history at all, or only the current workspace?
- Are test hints purely convention/config based?
- Is indexing ephemeral per run or persisted?
- What exactly counts as an evidence reference?
- What trace data is safe to persist?

## 10. Documentation Strategy

ForgeFlow should use five document types with distinct jobs.

| Document Type | Role |
|---|---|
| Vision document | Explains why ForgeFlow exists, who it serves, target workflows, MVP boundaries, and non-goals. |
| RFC | Pre-decision design proposal for cross-cutting architecture. RFCs compare options and produce recommendations. |
| OpenSpec feature spec | Concrete implementation-ready feature change with proposal, design, tasks, and acceptance criteria. |
| ADR | Short durable record of an accepted architecture decision, usually linked to an RFC. |
| Retrospective | Post-milestone learning about what worked, failed, or needs adjustment. |

RFCs debate. ADRs record. OpenSpec scopes a concrete change after enough RFC decisions exist.

## 11. Updated RFC Roadmap

### RFC-001 Agent Architecture

Purpose: define the minimal workflow roles and prevent premature agent/service/class design.

Key questions:

- Are Planner, Software Engineer, Validation, Review, and PR conceptual workflow roles or runtime components?
- What does each role own?
- What does the workflow graph/runtime own?
- How is repair loop ownership separated from Validation?
- How does Planner avoid becoming a super-agent?

Expected decisions:

- Treat the five agents as workflow roles during foundation and first specs.
- Planner generates/revises plan and stop conditions only.
- Runtime/workflow graph performs scheduling, retries, middleware, and stop enforcement.
- Validation explains failures but does not repair.
- Review produces risk flags but does not approve high-risk actions.

Why it matters: premature agent entity design will cause overlap, hard-to-test behavior, and policy bypasses.

Current recommendation: keep roles conceptual until the MVP vertical slice proves which boundaries deserve implementation artifacts.

### RFC-002 State Model and Structured Contracts

Purpose: define runtime state, durable run summary, long-term memory, and the required structured contracts.

Key questions:

- What extends DeerFlow thread/run state?
- What is runtime-only?
- What becomes a durable audit record?
- What is allowed in long-term memory?
- What fields are required for `RepositoryContextResult`, `PatchProposal`, `ValidationResult`, `ReviewResult`, and `PRResult`?
- How are schema versions, evidence refs, artifact IDs, risk flags, policy decisions, retry lineage, stop reasons, and mutable/immutable fields represented?

Expected decisions:

- Split state into Runtime State, Durable Run Summary / Audit Record, and Long-term Memory.
- Persist contract artifacts and summaries, not raw repository content or unredacted logs.
- Memory does not auto-write in the first version unless human-confirmed.

Why it matters: contract and state boundaries drive auditability, evaluation, retry safety, and PR trust.

Current recommendation: define minimal contract field categories before writing implementation code, but defer full JSON schema details to the RFC.

### RFC-003 Tool and MCP Integration

Purpose: define how agents and workflow roles access GitHub, sandbox, repository search, test execution, diff, and security capabilities.

Key questions:

- Which tools are read-only, sandbox-write, external-write, or approval-gated?
- What evidence must each tool return?
- How are tool errors represented?
- How are tool calls traced and correlated with contracts?
- Which MCP integrations are necessary for Milestone 1 versus MVP?

Expected decisions:

- Repository facts must come from deterministic services/tools.
- Tools must return structured evidence.
- External write actions require policy mediation.
- Sandbox edit tools are controlled and cannot be bypassed by agent roles.

Why it matters: the platform is only trustworthy if repository claims and side effects are traceable to tools.

Current recommendation: Milestone 1 needs repository workspace/search-style tooling only; GitHub write operations belong to the later MVP vertical slice.

### RFC-004 Sandbox and Security Governance

Purpose: define minimum safety policy before any code modification or test execution workflow.

Key questions:

- Is network access disabled by default?
- How are dependency installation and package downloads handled?
- Which commands are allowlisted or denied?
- Which file paths are sensitive?
- What resource limits apply?
- What diff thresholds trigger escalation?
- How does secret scanning run?
- When are human approval gates required?
- How are logs and traces redacted?

Expected decisions:

- Define command, path, network, resource, diff, secret, sensitive file, cost, retry, and approval policies.
- Sensitive files include `.github/workflows`, deployment config, infrastructure files, auth, crypto, permission, and production config.
- Security guardrails are MVP prerequisites, not Phase 2 luxuries.

Why it matters: sandbox execution without clear policy creates risk while appearing safe.

Current recommendation: implement no repair/PR MVP until these guardrails are specified; Milestone 1 can proceed with read-oriented repository context under limited local workspace access.

### RFC-005 Observability and Trace Model

Purpose: define product-level trace, run summary, redaction, retention, and PR-facing trace excerpts.

Key questions:

- What is the canonical run summary?
- Which spans are required?
- Which data can be recorded, summarized, redacted, or forbidden?
- How are LLM calls, tool calls, contract artifacts, validation, review, policy decisions, cost, and feedback linked?
- What appears in the PR body versus internal audit record?

Expected decisions:

- Every run has a trace ID and durable run summary.
- Observability is product UX and audit infrastructure, not only logs.
- Redaction and retention rules are required before storing prompts, tool results, logs, or diffs.

Why it matters: enterprises will not trust autonomous PRs without inspectable evidence, and the platform cannot improve without reliable traces.

Current recommendation: first-version trace should store summaries and evidence references by default, not full source snapshots or unredacted logs.

### RFC-006 Evaluation Framework

Purpose: define first-version evaluation that is small, repeatable, and connected to product traces.

Key questions:

- What is the first evaluation dataset?
- Which metrics are mandatory for Milestone 1?
- Which metrics are mandatory for the MVP vertical slice?
- How do evaluation results link to run summaries and contract artifacts?
- What failures should block promotion to the next milestone?

Expected decisions:

- Start with 5-10 small controlled repo fixtures or curated historical issue fixtures.
- For Milestone 1, measure context retrieval precision, evidence quality, test recommendation usefulness, and run summary completeness.
- For MVP, add patch changed files count, validation determinism, test pass rate, retry count, token/cost, execution time, and failure rate.
- Keep SWE-bench and SWE-bench Verified as long-term targets, not first-version prerequisites.

Why it matters: evaluation must prevent anecdote-driven progress and oversized benchmark commitments.

Current recommendation: create a tiny controlled fixture set before attempting broad benchmarks.

### RFC-007 DeerFlow Extension Strategy

Purpose: define how ForgeFlow builds on DeerFlow without becoming a fork or depending on unstable internals.

Key questions:

- Which DeerFlow abstractions will ForgeFlow extend?
- How does ForgeFlow attach domain state?
- How does ForgeFlow register tools?
- How do checkpointing, middleware hooks, and trace hooks map to ForgeFlow needs?
- Should DeerFlow be a local reference repo, submodule, package dependency, or fork?
- What changes might be contributed upstream?

Expected decisions:

- Keep DeerFlow as separate local reference during foundation.
- Define extension points before dependency mechanics.
- Reconsider pinned submodule or package dependency only after extension points are known.

Why it matters: unclear integration will produce either a fragile fork or a platform that cannot use the runtime effectively.

Current recommendation: document the extension map in RFC-007 before writing runtime integration code.

## 12. OpenSpec Readiness Plan

Current state:

- Not ready to generate an OpenSpec for the full GitHub Issue to Draft PR workflow.
- Ready to prepare a narrow OpenSpec draft for Repository Context Service after several RFC skeleton decisions are made.

Required RFC skeleton decisions before the Repository Context Service OpenSpec:

- RFC-001 Agent Architecture
- RFC-002 State Model and Structured Contracts
- RFC-004 Sandbox and Security Governance
- RFC-007 DeerFlow Extension Strategy

RFC-003, RFC-005, and RFC-006 can be drafted in parallel. They do not need to be fully accepted before the small Repository Context Service feature spec begins, but their open questions should be referenced.

Repository Context Service OpenSpec must include:

- `proposal.md`: user value, scope, non-goals, acceptance criteria.
- `design.md`: deterministic service boundary, inputs, outputs, evidence references, trace behavior, failure modes.
- `tasks.md`: documentation, tests, and implementation checklist once implementation is allowed.

The OpenSpec must explicitly exclude patch generation, code modification, PR creation, memory write, deep issue history, full dependency graph, and multi-repo support.

## 13. Updated Milestone Plan

### Milestone 0: Foundation Documents

Outputs:

- project vision
- revised foundation proposal
- RFC index and seven RFC drafts
- ADR index
- retrospective index
- documented DeerFlow upstream reference strategy

Exit criteria:

- Milestone 1 and MVP are clearly separated.
- Agent roles are defined as workflow roles.
- DeerFlow and ForgeFlow responsibilities are separated.
- Security and evaluation are not deferred out of the MVP prerequisites.

### Milestone 1: Repository Context Service / Foundation Slice

Outputs:

- accepted Repository Context Service OpenSpec
- `RepositoryContextResult` contract direction
- deterministic file/text search behavior
- evidence references
- candidate test command hints
- trace summary for context queries

Non-goals:

- no patch generation
- no code modification
- no PR creation
- no automatic repair
- no memory write

Exit criteria:

- Given a repo workspace and query, the service returns relevant files, evidence references, and test hints.
- Behavior is inspectable and evaluable against small controlled fixtures.
- No agent persona owns repository facts.

### Milestone 2: PatchProposal and Validation Slice

Outputs:

- controlled sandbox edit path
- `PatchProposal`
- local validation command execution
- `ValidationResult`
- bounded retry policy

Non-goals:

- no automatic merge
- no deployment
- no broad CI integration

### Milestone 3: Review and Draft PR Slice

Outputs:

- `ReviewResult`
- sensitive file and diff risk checks
- draft PR creation
- `PRResult`
- PR body generated from contracts and evidence

Exit criteria:

- Draft PR can be created only when review and policy allow.
- High-risk changes require human approval before PR creation.

### Milestone 4: MVP Vertical Slice

Goal:

```text
GitHub Issue -> Sandbox -> Repository Context -> PatchProposal -> Validation -> Review -> Draft PR
```

Exit criteria:

- single-repo GitHub Issue input
- controlled sandbox execution
- bounded repair loop
- product-level run summary
- small controlled evaluation set
- no automatic merge or deployment

## 14. Evaluation Plan

First-version evaluation must start small.

Do not start with SWE-bench as the first evaluation target. SWE-bench and SWE-bench Verified remain long-term goals after the platform can run controlled fixtures reliably.

### Milestone 1 Evaluation

Use 5-10 small controlled repository fixtures.

Measure:

- context retrieval precision
- evidence reference quality
- test recommendation usefulness
- run summary completeness
- determinism across repeated runs

### MVP Evaluation

Add:

- patch changed files count
- patch size
- validation determinism
- test pass rate
- retry count
- token cost
- execution time
- failure rate
- draft PR completeness

Evaluation results should link to run summaries, contract artifacts, and trace IDs.

## 15. Updated MVP Readiness Checklist

Before the first MVP implementation work begins:

- [ ] Milestone 1 and MVP are explicitly separated.
- [ ] Repository Context Service is defined as a deterministic service, not an agent.
- [ ] RFC-001 decides whether the five agents remain workflow roles or become runtime components later.
- [ ] RFC-001 limits Planner to plan revision and stop conditions.
- [ ] RFC-001 assigns scheduling, retry transitions, and stop enforcement to the workflow graph/runtime.
- [ ] RFC-002 defines minimum contract fields for `RepositoryContextResult`, `PatchProposal`, `ValidationResult`, `ReviewResult`, and `PRResult`.
- [ ] RFC-002 separates Runtime State, Durable Run Summary / Audit Record, and Long-term Memory.
- [ ] RFC-002 states that Memory does not auto-write in the first version unless human-confirmed.
- [ ] RFC-003 defines tool permission levels and evidence-returning requirements.
- [ ] RFC-004 defines command, path, network, resource, diff, secret scan, sensitive file, cost, retry, and approval policies.
- [ ] RFC-004 lists sensitive file categories including workflows, deployment, infra, auth, crypto, permission, and production config.
- [ ] RFC-005 defines run summary fields, redaction, and retention rules.
- [ ] RFC-006 defines first-version controlled fixtures and metrics.
- [ ] RFC-007 defines DeerFlow extension points and ForgeFlow-owned platform responsibilities.
- [ ] Repository Context Service OpenSpec excludes patch generation, code modification, PR creation, memory write, deep issue history, full dependency graph, and multi-repo support.
- [ ] Human approval gates are explicit nodes, not a generic "high risk" statement.
- [ ] Validation retry has hard caps for rounds, token cost, tool calls, elapsed time, diff growth, and repeated failure type.
- [ ] Draft PR body is generated from contracts, evidence, validation, review, and trace summaries.

## 16. Initial Git Workflow

Recommended early commits:

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

Keep commits document-focused until RFC-001, RFC-002, RFC-004, and RFC-007 have enough skeleton decisions to support the Repository Context Service OpenSpec. Do not add production code in foundation commits.

## 17. Concrete Document Changes Applied

This revision applies the Grill-Me architecture review by changing the foundation proposal in these concrete ways:

- separates Milestone 1 from the later MVP vertical slice
- defines Repository Context Service as the first foundation slice
- narrows Repository Context Service scope to file/text search, cheap symbol hints, test hints, evidence references, and `RepositoryContextResult`
- states that Planner, Software Engineer, Validation, Review, and PR are workflow roles, not implementation classes or services
- limits Planner to structured plan revision and stop conditions
- moves scheduling, retries, and stop enforcement to workflow graph/runtime
- clarifies that Validation does not repair directly
- separates Review Agent output from Human Approval gates
- defines DeerFlow and ForgeFlow responsibility boundaries
- strengthens RFC-002 contract decision points
- splits state into Runtime State, Durable Run Summary / Audit Record, and Long-term Memory
- makes first-version memory non-automatic unless human-confirmed
- brings minimum security guardrails into MVP prerequisites
- narrows first-version Code Intelligence / Repository Context scope
- updates OpenSpec readiness so the full GitHub Issue to Draft PR flow is not spec-ready yet
- updates RFC roadmap with current recommendation for each RFC
- changes first-version evaluation from SWE-bench-first to small controlled fixtures
- updates the MVP readiness checklist with policy, state, contract, evaluation, and approval gates
