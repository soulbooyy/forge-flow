# RFC-002: Contracts and State Model

## Status

Draft

Review stage: Grill-Me feedback has been incorporated as current draft decisions. RFC-002 is intended to validate the contract and state boundaries required to unblock RFC-001 acceptance.

## Current Draft Decisions

- Runtime State must not be persisted into Durable Run Summary by default.
- Runtime State may enter Durable Run Summary only through an explicit promotion, summarization, selection, and redaction step.
- Milestone 1 `RepositoryContextResult` must use deterministic retrieval metadata instead of broad probabilistic `confidence` or free-form `ranking_rationale`.
- Milestone 1 acceptance criteria must not require creation, validation, persistence, or use of `PatchProposal`, `ValidationResult`, `ReviewResult`, or `PRResult`.
- `evidence_refs` must identify evidence location and verification metadata; raw source snippets must not be embedded by default.
- Long-term Memory is entirely out of scope for Milestone 1, including both reads and writes.
- RFC-002 must define minimum contract/state criteria required to unblock RFC-001 acceptance.
- Milestone 3 is a contract-first, deterministic-fixture slice for
  `ValidationResult`, `ReviewResult`, artifact lineage, and policy-decision
  handoffs; it does not introduce real command execution or repair retries.
- A future execution attempt is distinct from a validation or review contract;
  retry policy belongs to future execution-runtime governance and must not
  mutate an otherwise immutable validation contract.
- M4 separates governance decisions, execution facts, review/scan findings,
  and external side effects into independent immutable contracts; none may
  silently stand in for another layer.

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

### Runtime-to-Durable Promotion Rule

Runtime State must not be persisted into Durable Run Summary by default.

Any value promoted from Runtime State into Durable Run Summary must pass through an explicit summarization, selection, and redaction step.

The promotion step may produce only bounded durable records such as:

- contract identifiers
- final contract summaries
- evidence references
- artifact identifiers
- policy decisions
- stop reasons
- retry counts
- final status
- bounded summaries

Raw runtime values must not be copied into Durable Run Summary by default.

Default persistence categories:

| Category | Data |
|---|---|
| Persist by default | contract IDs, final contract summaries, evidence references, artifact IDs, policy decisions, stop reason, retry count, final status, approved lineage metadata |
| Persist only if redacted and bounded | tool output excerpts, validation log excerpts, search result snippets, plan revision summaries, error excerpts, trace excerpts |
| Do not persist by default | raw source files, full logs, scratch reasoning, failed intermediate contract drafts, secrets, temporary workspace paths, raw environment variables, unbounded command output, raw tool payloads |

Durable Run Summary is an audit and product-facing record, not a dump of runtime internals.

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

For milestones after Milestone 1, Memory should default to no automatic writes. If memory writes exist at all in later milestones, they must require human confirmation and should only store stable engineering knowledge.

### Milestone 1 Memory Boundary

Long-term Memory is out of scope for Milestone 1.

Milestone 1 must not read from or write to Long-term Memory when producing `RepositoryContextResult`.

`RepositoryContextResult` must be derived only from:

- repo workspace
- query or issue text
- project configuration
- conventions detectable in the workspace
- deterministic retrieval signals
- evidence references

The following must not affect Milestone 1 repository context results:

- prior run notes
- manually curated memory
- historical repair outcomes
- previous validation summaries
- user preferences
- other memory-derived context

If memory reads are introduced in a later milestone, they must require a separate accepted RFC or OpenSpec, be clearly labeled as non-authoritative context, remain separated from repository facts, and be excluded from deterministic retrieval scoring.

Human-confirmed memory writes are not allowed in Milestone 1.

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
- deterministic retrieval metadata
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
- `match_score`
- `match_reasons`
- `ranking_inputs`
- `limitations`

`RepositoryContextResult` does not contain:

- patch
- diff
- final root cause decision
- code edits
- PR content
- memory write

`RepositoryContextResult` should be deterministic in Milestone 1. It should be grounded in file search, text search, cheap language-agnostic symbol hints, project configuration, repository conventions, and evidence references.

### Repository Context Ranking Metadata

During Milestone 1, `RepositoryContextResult` must not expose broad probabilistic or semantic judgment fields such as generic `confidence` or free-form `ranking_rationale`.

Ranking metadata must describe deterministic retrieval signals only.

Milestone 1 should use bounded fields such as:

- `match_score`
- `match_reasons`
- `ranking_inputs`
- `evidence_refs`
- `limitations`

Field direction:

- `match_score`: deterministic score derived from reproducible retrieval inputs.
- `match_reasons`: bounded enum or controlled list of retrieval reasons.
- `ranking_inputs`: deterministic signals used to compute ordering.
- `evidence_refs`: references to evidence used by retrieval.
- `limitations`: known retrieval gaps, unavailable analyzers, or incomplete coverage.

`match_score` must be derived from deterministic retrieval inputs such as:

- filename matches
- path matches
- text matches
- cheap language-agnostic symbol hints
- project configuration
- test conventions
- other reproducible repository signals

`match_reasons` should use controlled values such as:

- `filename_match`
- `path_match`
- `text_match`
- `symbol_hint`
- `test_convention_match`
- `config_match`

Free-form semantic rationale is not allowed in Milestone 1 unless it is clearly a bounded deterministic explanation of retrieval signals.

`RepositoryContextResult` ranking metadata explains deterministic retrieval signals; it must not infer semantic relevance beyond evidence or represent agent belief.

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

### Milestone 3 Contract Readiness

Milestone 3 is the first proposed slice to make the `PatchProposal` handoff
observable through validation and blocking-level review. Its contract work must
preserve the M2 boundary: a `PatchProposal` is declarative, immutable, and
non-authorizing. In particular, a candidate change, limitation code, or
policy-decision reference in a proposal does not authorize command execution,
workspace access, result persistence, retry, or a later side effect.

Before a Milestone 3 OpenSpec can authorize implementation, this RFC and
RFC-004 must resolve or explicitly constrain the following contract questions:

- the tagged-envelope and schema-version boundaries for successful validation,
  validation failure, review findings, and terminal stop outcomes;
- which fields are contract facts, which are artifact or evidence references,
  and the redaction, bounds, and retention rules for command output and parsed
  reports;
- identity and immutable lineage among `PatchProposal`, Command Intent, Policy
  Decision Record, `ValidationResult`, `ReviewResult`, and a Durable Run
  Summary;
- the distinction among a command not being authorized, not being started,
  being cancelled or timed out, failing in the sandbox, returning a non-zero
  exit code, and producing output that cannot be safely parsed;
- the blocking-review finding shape and its relationship to policy escalation,
  without creating an authorization or PR-approval field; and
- retry-lineage fields, while leaving retry budgets, eligibility, and
  enforcement to RFC-004 policy and workflow runtime.

These are architecture readiness questions, not permission for M3 execution
or a default schema. The Milestone 3 OpenSpec must select only the decisions
accepted through the relevant RFC or ADR authority.

For M3, this readiness direction is now bounded as follows:

- fixtures or a fake executor may produce only deterministic, bounded,
  non-side-effecting attempt facts for contract and state-transition tests;
- they must not spawn a process, inspect or mutate a workspace, access a
  network, install dependencies, access credentials, or invoke a provider,
  MCP server, DeerFlow runtime, Git, or PR integration;
- a validation or review result records observed or simulated facts and their
  evidence/artifact lineage; it cannot contain repair instructions or change
  the referenced `PatchProposal`; and
- retry is not an M3 capability. A future execution-runtime design may attach
  bounded retry lineage to immutable attempt results, but it must define its
  own policy and terminal semantics.

### M4 Execution Contract Boundary

M4 extends the contract direction without granting a `PatchProposal` execution
authority. The following are separate immutable contract families with
explicit lineage:

- `TaskInput` records a normalized, redacted task derived from the single
  pre-registered fixture Issue;
- `ActionIntent` describes a proposed governed action;
- `CommandIntent` describes one structured command proposed for a controlled
  execution environment;
- `PatchIntent` describes a deterministic proposed patch against a fixed
  repository revision;
- `PatchArtifact` records the resulting, identity-bound patch artifact;
- `ExecutionAttempt` records the lifecycle facts of one execution attempt;
- `SecretScanResult` records deterministic scanning facts for its scoped
  artifact(s);
- `ReviewResult` records deterministic review findings and evidence;
- `PolicyDecisionRecord` records a governance decision over specified current
  inputs;
- `ApprovalRequest` and its decision record an independently governed human
  approval interaction when policy requires it;
- `PRResult` records a branch, commit, and Draft PR side effect or why no such
  side effect occurred; and
- `DurableRunSummary` references the bounded, redacted lineage rather than
  embedding its raw payloads.

Each contract must identify its schema version and immutable contract ID. M4
lineage must bind, where applicable, the originating `PatchProposal` contract
ID, repository identity and fixed base revision, intent ID, artifact ID,
attempt ID, policy-decision ID, approval ID, evidence/artifact references, and
Draft PR result ID. A contract reference is not reusable authorization: a
later action requires a fresh `PolicyDecisionRecord` over its current inputs.
Artifact and evidence references use ForgeFlow-owned IDs (including run ID,
artifact ID, contract ID, and policy-decision ID) as their identity. A local
store path is a resolved location only and must never be the sole durable
identity or lineage key.

#### M4 Controlled Issue Input

The M4 task source is only a pre-registered fixture Issue. The ForgeFlow-owned
GitHub adapter may read it through a repository- and Issue-identity allowlist
that also binds the expected base revision. A user, agent, or workflow role
cannot select an arbitrary repository, Issue, organization resource, or other
external task source.

The adapter must normalize the read-only Issue into an immutable `TaskInput`.
`TaskInput` contains only the redacted task summary, Issue identity, content
hash, repository identity, expected base revision, and adapter/evidence
references required for lineage. The raw GitHub Issue payload is neither a
ForgeFlow durable artifact nor a `DurableRunSummary` field. A later enterprise
Issue-input capability requires a separate OpenSpec that defines repository
onboarding, authorization, data retention, and multi-tenant policy.

#### M4 Layered Terminal Model

`PolicyDecisionRecord.outcome` is the governance layer and has exactly these
values:

- `allowed`
- `requires_human_approval`
- `blocked`

`ExecutionAttempt.status` records only actual execution-lifecycle facts and
has exactly these values:

- `succeeded`
- `failed`
- `cancelled`
- `timed_out`
- `not_started`

For every non-successful attempt, `ExecutionAttempt.failure_reason` is
required and must be one of:

- `policy_blocked`
- `approval_required`
- `sandbox_unavailable`
- `command_failed`
- `parser_failed`
- `redaction_failed`
- `base_revision_mismatch`
- `resource_limit_exceeded`
- `cancelled_by_request`

The failure reason explains execution facts; it neither replaces nor infers a
policy decision. In particular, `not_started` paired with `policy_blocked` or
`approval_required` remains distinct from a started attempt that failed.
`cancelled_by_request` applies only to an attempt that actually started and
whose status is `cancelled`; it cannot describe a policy, approval, or other
pre-start stop. A cancelled attempt must use that cancellation reason rather
than `command_failed`, and it does not authorize an automatic retry.
`SecretScanResult` and `ReviewResult` produce facts and findings only. A new
`PolicyDecisionRecord` consumes those inputs to decide whether a later action
is allowed, requires human approval, or is blocked. `PRResult` records an
external side effect or why it did not occur; it never authorizes that effect.

#### M4 First Execution-Feature Contract Shape

The first M4 controlled-execution OpenSpec must use the following minimum
immutable contract shape. Every listed contract contains `schema_version`,
`contract_id`, `run_id`, and `created_at`.

- `ActionIntent` contains `action_id`, kind `execute_fixture_test`, `TaskInput`
  ID, repository ID, base SHA, requested `command_id`, and policy-profile ID and
  version. It is declarative and never grants execution authority.
- `CommandIntent` contains `action_intent_id`, repository ID, base SHA, the
  sole registered `command_id`, exact executable, ordered arguments, working
  directory, empty allowed environment, required OCI image digest, timeout and
  output limits, and policy-profile ID and version. Every value must exactly
  match the fixture policy profile and registered OCI image. No CommandIntent
  is executable until that image registration supplies an immutable digest.
- `PolicyDecisionRecord` contains `decision_id`, subject contract ID,
  input-lineage digest, policy-profile ID and version, outcome, reason codes,
  evidence references, and `evaluated_at`. It is the only authorization
  decision source.
- `ExecutionAttempt` contains `attempt_id`, `CommandIntent` ID, Policy Decision
  Record ID, status, failure reason when non-successful, bounded resource
  observations, immutable artifact references, and started/finished timestamps
  when those facts exist. Actual image digest, exit code, and output artifact
  reference exist only after execution started and produced those facts.

`ExecutionAttempt` must not reference a mutable workspace path or runtime
object. Its audit lineage uses immutable contract IDs, evidence/artifact
references, and image digest so sandbox-backend or runtime-adapter replacement
does not break the durable record. No contract in this set may persist raw
command output, environment, credentials, workspace paths, raw source, or an
unredacted artifact. A `not_started` attempt must not carry image, exit-code,
or output facts.

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
- line ranges
- text search results
- symbol hints
- command IDs
- tool call IDs
- artifact IDs
- retrieval methods
- content hashes
- match metadata
- validation reports
- policy check results

Evidence references should be compact, reproducible, and safe to persist. They should avoid embedding large source files or full logs directly into contracts.

Evidence references matter because they make role outputs inspectable, testable, and suitable for PR summaries and evaluation.

### Evidence Reference and Payload Boundary

Contracts should prefer evidence references over embedded evidence payloads.

`evidence_refs` identify where evidence came from and how it can be verified. They may include:

- file path
- line range
- symbol name
- search query
- command ID
- tool call ID
- artifact ID
- retrieval method
- content hash
- match metadata

`evidence_refs` must not embed raw source content by default.

Inline evidence excerpts are evidence payloads, not evidence references.

Evidence payloads may include source snippets, validation output excerpts, or tool output excerpts only when they are:

- optional
- bounded
- redacted
- policy-governed
- retained according to RFC-004 and RFC-005 policy

For Milestone 1, `RepositoryContextResult` may include file paths, line ranges, match metadata, retrieval metadata, and content hashes by default.

Inline source snippets must not be required for Milestone 1 acceptance criteria and must not be persisted by default.

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

## RFC-001 Acceptance Support

RFC-002 is sufficient to unblock RFC-001 acceptance only if its contract and state model preserves the role, authority, runtime-control, and persistence boundaries defined by RFC-001.

At minimum, RFC-002 must confirm that:

- Planner artifacts remain declarative, advisory, and non-executable.
- `RepositoryContextResult` contains deterministic retrieval evidence and bounded retrieval metadata, not agent judgment, root-cause inference, or repair strategy.
- `PatchProposal` is the first contract that may carry fix strategy, patch intent, changed-file intent, or proposed code changes.
- `ValidationResult` is diagnostic and must not prescribe repair, produce patch instructions, or direct changed files.
- `ReviewResult` is recommendational and must not authorize PR creation, replace Human Approval, or contain final approval fields such as `approved_for_pr`.
- `PRResult` records policy-gated side effects and artifact references, but must not authorize side effects, mutate patches, or reinterpret reviewed artifacts.
- Policy decisions may be referenced or recorded by contracts, but policy authority belongs to RFC-004 and policy middleware.
- Retry lineage must be representable without giving any workflow role ownership of retry loops, retry budgets, or stop-condition enforcement.
- Durable Run Summary can be produced through explicit promotion and redaction without persisting raw Runtime State by default.

If RFC-002 cannot satisfy these criteria, RFC-001 must remain Draft until the contract and state boundaries are revised.

## Relationship with Milestone 1

Milestone 1 only requires the Repository Context Foundation Slice.

For Milestone 1, RFC-002 requires direction for:

- `RepositoryContextResult`
- evidence references
- artifact references if needed
- Runtime State vs Durable Run Summary distinction for context queries
- no Long-term Memory reads or writes

Milestone 1 does not require implementation of:

- `PatchProposal`
- `ValidationResult`
- `ReviewResult`
- `PRResult`

Those contracts are included here only as future milestone design direction.

### Milestone 1 Contract Scope

Milestone 1 acceptance criteria must not require creation, validation, persistence, or use of:

- `PatchProposal`
- `ValidationResult`
- `ReviewResult`
- `PRResult`

During Milestone 1, these future contracts may be referenced only as compatibility anchors to avoid contract and state decisions that would block later workflow stages.

They must not be:

- implemented
- tested
- validated
- persisted
- exposed as Milestone 1 outputs
- required by Milestone 1 acceptance criteria

`RepositoryContextResult` is the only required Milestone 1 contract deliverable.

Future contracts may be described in RFC-002 as future directions, but their presence in the document must not expand Milestone 1 scope.

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

Rejected for Milestone 1 because success may be partial, evidence may be incomplete, and unverified lessons can pollute future runs. Later memory reads or writes require a separate accepted RFC or OpenSpec, and writes require human confirmation.

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
- Long-term Memory may become unsafe if introduced before a later RFC or OpenSpec defines read/write boundaries.
- Milestone 1 may expand if future contracts are mistaken for implementation requirements.
- Durable Run Summary may leak runtime internals if promotion and redaction are skipped.
- Evidence payloads may leak source code if confused with evidence references.

## Open Questions

- What is the minimal Milestone 1 schema for `RepositoryContextResult`?
- What evidence reference format is stable enough for search results, file line ranges, and test hints?
- Which artifacts need IDs in Milestone 1, if any?
- How should mutable and immutable contract fields be identified?
- How should contract supersession work across retries?
- What fields belong in Durable Run Summary versus contract artifacts?
- What later milestone should introduce non-authoritative memory reads, if any?
- What memory review workflow is required before any future memory writes are allowed?
- How should contract versions be represented across RFCs and OpenSpec changes?

## Decision Summary

- ForgeFlow state is split into Runtime State, Durable Run Summary / Audit Record, and Long-term Memory.
- Runtime State is short-lived, mutable workflow execution state.
- Durable Run Summary / Audit Record is persisted for trace, PR summary, evaluation, retrospective, and audit.
- Runtime State must enter Durable Run Summary only through explicit promotion, summarization, selection, and redaction.
- Long-term Memory stores only stable engineering knowledge and must not store source code, secrets, temporary logs, unverified reasoning, or large diffs.
- Long-term Memory is entirely out of scope for Milestone 1, including reads and writes.
- ForgeFlow uses structured contracts instead of free-form role outputs.
- `RepositoryContextResult` is the only contract required for Milestone 1.
- Milestone 1 acceptance criteria must not require creation, validation, persistence, or use of `PatchProposal`, `ValidationResult`, `ReviewResult`, or `PRResult`.
- `PatchProposal`, `ValidationResult`, `ReviewResult`, and `PRResult` are future milestone contract directions.
- Milestone 1 `RepositoryContextResult` uses deterministic retrieval metadata such as `match_score`, `match_reasons`, and `ranking_inputs`, not broad probabilistic confidence or free-form ranking rationale.
- Contracts should consider schema version, run ID, contract ID, timestamps, evidence refs, artifact IDs, risk flags, policy decisions, retry lineage, stop reason, and mutable/immutable field boundaries.
- Evidence references point to evidence location and verification metadata, not raw source content by default.
- Evidence payloads such as snippets or output excerpts are optional, bounded, redacted, and policy-governed.
- Artifact IDs point to larger persisted artifacts such as diffs, logs, run summaries, and PR body drafts.
- Contracts should reference large artifacts instead of embedding all content directly.
- RFC-002 supports RFC-001 by making workflow role handoffs explicit, testable, auditable, and policy-readable.
- RFC-002 defines minimum contract/state criteria required to unblock RFC-001 acceptance.
