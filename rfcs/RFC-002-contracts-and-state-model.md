# RFC-002: Contracts and State Model

## Status

Draft

## Context

ForgeFlow is an enterprise autonomous software engineering agent platform built on DeerFlow and LangGraph.

RFC-001 defines the first-stage Agent Architecture: Planner, Software Engineer, Validation, Review, and PR are workflow roles, not concrete implementation units. Runtime scheduling, branching, retries, stop-condition enforcement, and policy gates are owned by the workflow graph / DeerFlow runtime boundary rather than by any single role.

This RFC defines the state model and structured contract direction needed to support those role boundaries.

Milestone 1 remains the Repository Context Foundation Slice. It requires only the Repository Context contract family, especially `RepositoryContextResult`. Later contracts such as `PatchProposal`, `ValidationResult`, `ReviewResult`, and `PRResult` are described here as directional design constraints for future milestones, not implementation requirements for Milestone 1.

## Problem Statement

Autonomous software engineering workflows fail when roles exchange free-form text that implicitly carries hidden authority, assumptions, or execution instructions.

Without structured contracts, ForgeFlow risks:

- role outputs becoming ambiguous
- Planner or Review text turning into hidden execution control
- Validation output becoming repair instructions
- PR summaries drifting away from actual evidence
- policy gates receiving incomplete or inconsistent inputs
- evaluation depending on brittle natural-language parsing
- long-term memory accidentally storing source code, secrets, temporary logs, or unverified reasoning

ForgeFlow needs explicit state boundaries and structured handoff objects before implementation begins.

## Goals

- Define the three state categories: Runtime State, Durable Run Summary / Audit Record, and Long-term Memory.
- Establish structured contract principles for role handoff and policy evaluation.
- Define the responsibility and boundaries of `RepositoryContextResult` for Milestone 1.
- Define directional contract boundaries for `PatchProposal`, `ValidationResult`, `ReviewResult`, and `PRResult`.
- Explain common field categories such as schema version, run ID, evidence refs, artifact IDs, risk flags, policy decisions, retry lineage, and stop reason.
- Explain evidence references and artifact IDs without embedding large content directly in contracts.
- Support RFC-001 role boundaries without promoting workflow roles into implementation units.

## Non-goals

- Define complete JSON Schemas.
- Write production code.
- Create Python classes or data models.
- Create an OpenSpec change.
- Define sandbox command, path, network, diff, or approval policy. Those belong to RFC-004.
- Define DeerFlow extension mechanics. Those belong to RFC-007.
- Define final trace format or observability storage. Those belong to RFC-005.
- Define evaluation metrics in detail. Those belong to RFC-006.
- Expand Milestone 1 beyond Repository Context Foundation Slice.

## State Model Overview

ForgeFlow state must be split into three categories:

| State Category | Lifetime | Mutability | Purpose |
|---|---|---|---|
| Runtime State | One workflow run | Mutable | Helps the workflow graph execute the current run. |
| Durable Run Summary / Audit Record | Persisted after or during run | Append-oriented / controlled updates | Supports trace, PR summary, evaluation, retrospective, and audit. |
| Long-term Memory | Cross-run | Highly curated | Stores stable engineering knowledge only. |

This split prevents temporary workflow context from becoming permanent memory and prevents long-term memory from becoming a source of unverified repository facts.

## Runtime State

Runtime State is short-lived, mutable state used by the workflow graph during a single run.

Examples:

- current workflow node
- current plan artifacts
- active stop-condition candidates
- current retry count
- current workspace reference
- transient tool outputs
- current contract draft under construction
- temporary validation output
- current policy gate status

Runtime State exists to support execution. It should not be treated as a durable audit record or long-term memory.

Runtime State may contain temporary references to repository files or command outputs, but it should avoid retaining large source snapshots or raw logs longer than needed.

## Durable Run Summary / Audit Record

Durable Run Summary / Audit Record is persisted for traceability, PR summary generation, evaluation, retrospective review, and audit.

It should persist structured summaries and references, not unbounded raw content.

It may include:

- `run_id`
- trace ID
- task source and normalized task summary
- selected workflow path
- plan revisions or plan summary
- contract artifacts
- evidence references
- artifact IDs
- changed file list when applicable
- validation command summaries
- validation result summaries
- review findings
- policy decisions
- human approval state
- retry lineage
- stop reason
- token, cost, and timing summaries when available
- PR result when available

It should not persist by default:

- full repository source code
- secrets
- unnecessary full logs
- raw unredacted LLM prompts or responses
- large diffs embedded directly in the record
- temporary failed reasoning
- unverified hypotheses as durable memory

## Long-term Memory

Long-term Memory stores stable engineering knowledge that is useful across runs.

Allowed examples:

- accepted repository conventions
- stable test command patterns
- stable architecture notes
- important paths
- validated recurring failure patterns
- human-confirmed engineering lessons

Long-term Memory must not store:

- source code
- secrets
- temporary logs
- unverified reasoning
- large diffs
- full tool outputs
- transient run context
- customer-sensitive data

First-version Memory should default to no automatic writes. If memory writes exist at all, they must require human confirmation and should only store stable engineering knowledge.

## Structured Contract Principles

ForgeFlow should prefer structured contracts over free-form role outputs.

Structured contracts are required because they:

- reduce implicit coupling between workflow roles
- make role outputs testable
- support trace and evaluation
- provide readable inputs to policy gates
- support PR summary generation
- enable schema evolution
- make retry lineage and artifact lineage inspectable
- prevent free-form text from becoming hidden execution authority

Contracts should be explicit about what they represent and what they do not authorize.

For example:

- Planner artifacts may be declarative and advisory, but they do not execute workflow branches.
- `ValidationResult` may diagnose failures, but it does not prescribe the next patch.
- `ReviewResult` may recommend draft PR readiness, but policy decides eligibility.
- `PRResult` records PR side effects, but the PR role must not alter the patch artifact.

## Contract Lifecycle

A contract should generally move through these lifecycle stages:

```text
created
  -> populated from deterministic evidence or role judgment
  -> validated for required fields
  -> referenced by workflow graph / policy middleware
  -> persisted as an artifact or summarized in the durable run record
  -> optionally superseded by a later retry or revision
```

Contracts should be versioned and traceable to a run. When a retry produces a revised contract, the new contract should reference prior attempts through retry lineage rather than overwriting history.

Milestone 1 should focus only on the lifecycle of `RepositoryContextResult`.

## RepositoryContextResult

`RepositoryContextResult` is the primary contract for Milestone 1.

It represents evidence-backed repository context related to a query or optional issue text in a specific repo workspace.

It should express:

- repo workspace reference
- query and optional issue text reference
- relevant files
- evidence references
- text search results
- file search results
- optional simple symbol hints
- test command hints
- confidence or ranking rationale
- limitations

Minimum field direction:

- `schema_version`
- `run_id`
- `contract_id`
- `created_at`
- `updated_at`
- `query_ref` or normalized query summary
- `workspace_ref`
- `relevant_files`
- `search_results`
- `symbol_hints`
- `test_command_hints`
- `evidence_refs`
- `confidence`
- `ranking_rationale`
- `limitations`

`RepositoryContextResult` does not contain:

- patch
- diff
- final root cause decision
- code edits
- PR content
- memory write

`RepositoryContextResult` should be deterministic in Milestone 1. It should be grounded in file search, text search, cheap language-agnostic symbol hints, project configuration, repository conventions, and evidence references.

## PatchProposal

`PatchProposal` is a future milestone contract. It is not required for Milestone 1 implementation.

It should represent structured patch intent or proposed diff information derived from repository context and role judgment.

It may include:

- root cause hypothesis
- fix strategy
- candidate changed files
- proposed diff or patch intent
- risk flags
- evidence refs
- validation commands
- limitations

`PatchProposal` should not authorize PR creation, merge, deployment, or sensitive file modification by itself. Those decisions belong to workflow graph policy, RFC-004 governance, and Human Approval gates.

## ValidationResult

`ValidationResult` is a future milestone contract. It records test execution and diagnostic findings.

It may include:

- executed commands
- exit codes
- parsed test results
- failure analysis
- diagnostic output
- retry lineage
- stop reason
- evidence refs
- artifact IDs for logs or test reports

`ValidationResult` does not directly contain repair behavior.

It must not contain:

- revised fix strategies
- patch instructions
- code edits
- next-patch content
- changed-file directives

Validation explains what failed and why. It does not decide what to fix next.

## ReviewResult

`ReviewResult` is a future milestone contract. It records blocking-level automated review findings and draft PR readiness recommendations.

It may include:

- blocking issues
- risk flags
- security concerns
- sensitive file warnings
- test sufficiency findings
- approval recommendation
- required human approval reasons
- evidence refs
- policy-relevant observations

Review recommends; policy decides.

`ReviewResult` must not contain final authorization fields that bypass policy, such as treating `approved_for_pr` as sufficient for PR creation. Final PR eligibility belongs to workflow graph / policy middleware using `ReviewResult`, security policy, validation results, human approval state, and PR action policy.

## PRResult

`PRResult` is a future milestone contract. It records draft PR side effects after policy-eligible artifacts have been packaged.

It may include:

- branch
- commit metadata
- draft PR URL
- PR body artifact reference
- linked issue
- CI status if available
- policy eligibility summary
- human approval state when required
- artifact IDs

The PR role only packages policy-eligible artifacts. `PRResult` records what happened; it does not authorize patch modification, non-draft PR creation, merge, or deployment.

## Evidence References

`evidence_refs` point to the evidence used to produce a contract.

Evidence references may point to:

- file paths
- file snippets or line ranges
- text search results
- symbol hints
- test output excerpts
- tool outputs
- validation reports
- policy check results

Evidence references should be compact, reproducible, and safe to persist. They should avoid embedding large source files or full logs directly into contracts.

Evidence references matter because they make role outputs inspectable, testable, and suitable for PR summaries and evaluation.

## Artifact IDs

`artifact_ids` point to persisted artifacts that are too large, too sensitive, or too specialized to embed directly in contracts.

Artifact IDs may refer to:

- diff artifacts
- patch files
- logs
- test reports
- run summaries
- PR body drafts
- trace exports
- redacted tool output bundles

Contracts should reference artifacts rather than inline all content. This keeps contracts small, stable, and easier to validate.

Artifact storage, retention, and redaction details belong to RFC-005 and RFC-004 where appropriate.

## Retry Lineage

Retry lineage connects contract revisions across bounded retry loops.

It should help answer:

- Which attempt produced this contract?
- What prior contract did it supersede?
- Why was a retry attempted?
- What validation result or policy decision triggered the retry?
- What stop reason ended the retry loop?

Retry lineage is essential for evaluation, traceability, and preventing infinite repair loops.

RFC-002 owns the shape of retry lineage, but RFC-004 owns retry caps and enforcement policy.

## Policy Decisions

Contracts may carry or reference policy decisions when those decisions are relevant to downstream workflow steps.

Policy decisions may include:

- sensitive file detection result
- diff threshold result
- command policy result
- approval requirement
- approval state
- PR action eligibility
- retry eligibility

Contracts should not become policy engines. Policy is owned by RFC-004 and enforced by workflow graph / policy middleware. Contracts should make policy-relevant facts and decisions visible.

## Schema Versioning

Every contract should consider a `schema_version`.

Schema versioning matters because ForgeFlow contracts will evolve across milestones. Versioning supports:

- backward-compatible readers
- migration planning
- evaluation across historical runs
- artifact compatibility
- clearer debugging when contract shape changes

This RFC does not define the exact versioning scheme. It establishes that contract versioning is required.

## Relationship with RFC-001

RFC-002 supports RFC-001 by providing structured handoff objects for workflow roles.

It helps unblock RFC-001 acceptance by:

- giving workflow roles explicit structured outputs
- preventing Planner, Software Engineer, Validation, Review, and PR from coupling through free-form text
- clarifying that role outputs are declarative, diagnostic, or recommendational rather than direct execution authority
- providing readable inputs for policy gates and Human Approval
- enabling durable audit records and evaluation
- supporting retry lineage without letting roles own retry loops

RFC-001 defines role and authority boundaries. RFC-002 defines the contract and state model needed to preserve those boundaries.

## Relationship with Milestone 1

Milestone 1 only requires the Repository Context Foundation Slice.

For Milestone 1, RFC-002 requires direction for:

- `RepositoryContextResult`
- evidence references
- artifact references if needed
- Runtime State vs Durable Run Summary distinction for context queries
- no automatic Long-term Memory writes

Milestone 1 does not require implementation of:

- `PatchProposal`
- `ValidationResult`
- `ReviewResult`
- `PRResult`

Those contracts are included here only as future milestone design direction.

## Alternatives Considered

### Alternative 1: Free-form Role Outputs

Roles could exchange natural-language summaries only.

Rejected because free-form outputs are hard to test, hard to evaluate, difficult to route through policy, and prone to hidden authority.

### Alternative 2: One Large Run State Object

ForgeFlow could store everything in one mutable run state.

Rejected because it blurs runtime state, durable audit data, and long-term memory. It also increases the risk of persisting secrets, source code, temporary logs, or unverified reasoning.

### Alternative 3: Full JSON Schema Before Any Feature Spec

ForgeFlow could define complete JSON Schema documents for every future contract now.

Rejected for this RFC because it would over-specify future milestones. RFC-002 should define boundaries and field direction first; exact schemas can be refined through OpenSpec and later RFC updates.

### Alternative 4: Automatic Memory Writes from Successful Runs

ForgeFlow could write memory after every apparently successful run.

Rejected for early milestones because success may be partial, evidence may be incomplete, and unverified lessons can pollute future runs. Early memory writes require human confirmation.

## Trade-offs

Benefits:

- clearer workflow role handoffs
- better testability
- better auditability
- safer policy gating
- more reliable PR summaries
- repeatable evaluation
- easier schema evolution

Costs:

- more upfront documentation
- more careful contract design before implementation
- additional discipline around evidence and artifact references
- possible need to revise contracts as milestones mature

The trade-off is intentional. ForgeFlow prioritizes governable engineering automation over quick free-form agent behavior.

## Risks

- Contracts may become too broad if they try to capture every possible detail.
- Contracts may become too weak if important policy or evidence fields are omitted.
- Free-form fields may reintroduce implicit authority unless carefully bounded.
- Artifact references may become unusable if retention and redaction are not defined in RFC-005 and RFC-004.
- Long-term Memory may become unsafe if human confirmation is skipped.
- Milestone 1 may expand if future contracts are mistaken for implementation requirements.

## Open Questions

- What is the minimal Milestone 1 schema for `RepositoryContextResult`?
- What evidence reference format is stable enough for search results, file snippets, and test hints?
- Which artifacts need IDs in Milestone 1, if any?
- How should mutable and immutable contract fields be identified?
- How should contract supersession work across retries?
- What fields belong in Durable Run Summary versus contract artifacts?
- What memory review workflow is required before any memory writes are allowed?
- How should contract versions be represented across RFCs and OpenSpec changes?

## Decision Summary

- ForgeFlow state is split into Runtime State, Durable Run Summary / Audit Record, and Long-term Memory.
- Runtime State is short-lived, mutable workflow execution state.
- Durable Run Summary / Audit Record is persisted for trace, PR summary, evaluation, retrospective, and audit.
- Long-term Memory stores only stable engineering knowledge and must not store source code, secrets, temporary logs, unverified reasoning, or large diffs.
- First-version Memory does not auto-write unless human-confirmed.
- ForgeFlow uses structured contracts instead of free-form role outputs.
- `RepositoryContextResult` is the only contract required for Milestone 1.
- `PatchProposal`, `ValidationResult`, `ReviewResult`, and `PRResult` are future milestone contract directions.
- Contracts should consider schema version, run ID, contract ID, timestamps, evidence refs, artifact IDs, risk flags, policy decisions, retry lineage, stop reason, and mutable/immutable field boundaries.
- Evidence references point to files, snippets, search results, test outputs, and tool outputs.
- Artifact IDs point to larger persisted artifacts such as diffs, logs, run summaries, and PR body drafts.
- Contracts should reference large artifacts instead of embedding all content directly.
- RFC-002 supports RFC-001 by making workflow role handoffs explicit, testable, auditable, and policy-readable.
