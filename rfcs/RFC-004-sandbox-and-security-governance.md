# RFC-004: Sandbox and Security Governance

## Status

Draft

RFC-004 is an RFC-001 acceptance precondition. RFC-001 should not become Accepted until RFC-004 defines a usable sandbox and security governance skeleton that can enforce the side-effect, approval, retry, and policy boundaries described by RFC-001.

Review stage: Grill-Me feedback has been incorporated as current draft decisions. RFC-004 is intended to validate the sandbox, security, approval, side-effect, and policy boundaries required to unblock RFC-001 acceptance.

## Current Draft Decisions

- Milestone 1 requires a controlled read-only workspace boundary, not full sandbox-local write/test execution.
- Tool permission levels classify capability surfaces; they are not final authorization decisions.
- Every command execution must be represented as a policy-evaluable Command Intent before execution.
- Every Human Approval gate must use a structured Approval Request artifact.
- Diff thresholds are policy-profile based, with conservative defaults and reviewed repo-level overrides.
- Every policy-evaluated action must produce a structured Policy Decision Record.
- Secret scanning and redaction must happen before artifact persistence, commit creation, draft PR packaging, or external publication.
- RFC-004 must define explicit RFC-001 Security Acceptance Criteria before it can unblock RFC-001 acceptance.
- Milestone 3 uses deterministic fixtures or a fake executor only to verify
  contract and policy-state transitions; it does not authorize real command
  execution, sandbox operation, dependency installation, or retry runtime.
- M4 controlled execution is limited to one allowlisted fixture/test
  repository, a fixed repository revision, and a versioned ForgeFlow policy
  profile. It is not general automation authority.

## Context

ForgeFlow is an enterprise autonomous software engineering agent platform built on DeerFlow and LangGraph.

Later ForgeFlow milestones may involve:

- repository reading
- file search
- code editing
- test execution
- git diff generation
- draft PR creation
- human approval

These capabilities introduce safety, security, audit, and governance risks. ForgeFlow must define sandbox and policy boundaries before automated patching, validation, and PR creation are implemented.

Milestone 1 remains the Repository Context Foundation Slice. It is mostly read-only, but it still needs early security boundaries for workspace access, evidence references, trace redaction, and safe future evolution.

## Problem Statement

Without explicit sandbox and security governance:

- Agent roles may execute dangerous commands.
- Agent roles may modify sensitive files.
- Agent roles may leak secrets.
- Agent roles may generate excessive diffs.
- Agent roles may retry indefinitely and create runaway cost.
- Sandbox logs, source code, or secrets may be written into memory or trace.
- Review may be mistaken for approval authority.
- Draft PRs may contain artifacts that policy did not allow.
- External side effects may happen without clear audit records.

ForgeFlow needs a policy-gated execution model where agents propose actions, policy evaluates those actions, and execution happens only through governed tools and runtime gates.

## Goals

- Define sandbox execution boundary.
- Define tool permission levels.
- Define command policy.
- Define path policy.
- Define sensitive file policy.
- Define diff boundary policy.
- Define secret scanning expectations.
- Define resource limits.
- Define network policy.
- Define human approval gates.
- Define observability and redaction requirements.
- Define relationship with RFC-001 workflow roles.
- Define relationship with RFC-002 contracts and policy decisions.

## Non-goals

- Implement sandbox runtime.
- Choose the final Docker, VM, remote worker, or DeerFlow abstraction.
- Implement complete enterprise RBAC.
- Implement a production-grade policy engine.
- Implement complete CI/CD security.
- Allow automatic merge.
- Allow automatic deployment.
- Define every language ecosystem package-management security policy.
- Solve all supply chain security problems.
- Create APIs, classes, services, or OpenSpec changes.

## Security Governance Model

ForgeFlow should use this governance model:

```text
Agent / Workflow Role
  -> Action Intent
  -> Policy Evaluation
  -> Allowed / Blocked / Requires Human Approval
  -> Execution in Sandbox or External Tool
  -> Durable Run Summary / Audit Record
```

Rules:

- Agent roles may propose action intent.
- Agent roles must not decide whether an action is safe.
- Policy gates decide whether an action is allowed, blocked, or requires Human Approval.
- Human Approval is an independent gate.
- Tool execution must record the policy decision that allowed, blocked, or escalated the action.
- Policy decisions should be written into Durable Run Summary / Audit Record.
- Policy decisions should align with RFC-002 structured contracts.

This model follows the principle: Agent proposes, policy decides.

### Policy Decision Record

Policy decisions must be structured audit records, not unstructured log lines.

Every policy-evaluated action must produce a Policy Decision Record, whether the result is:

- `allowed`
- `blocked`
- `requires_human_approval`

At minimum, a Policy Decision Record should include:

- decision ID
- run ID
- policy profile ID and version
- action intent ID when applicable
- command intent ID when applicable
- approval request ID when applicable
- tool level
- action type
- target paths
- decision result
- triggered rules
- risk flags
- required approvals
- artifact IDs
- evidence references
- timestamp
- evaluator identity and version
- expiration or revalidation requirement when applicable
- bounded reason summary

Policy Decision Records must link policy outcomes to the specific action, artifacts, paths, policy profile, and evidence evaluated at decision time.

They must be suitable for:

- audit
- debugging
- human review
- PR evidence
- evaluation

A later action must not rely on a stale Policy Decision Record if any of the following changed:

- action intent
- command intent
- approval request
- artifact
- diff
- target paths
- policy profile
- validation result
- review result
- human approval state

## Tool Permission Levels

ForgeFlow tools should be classified by capability level. Tool permission levels are capability classifications, not final authorization decisions.

A tool level describes the capability surface exposed by a tool, such as read-only repository access, sandbox-local mutation, external side effects, or actions that may require Human Approval. The level alone must not determine whether a concrete action is allowed.

Every concrete tool action must still be evaluated by policy. Policy evaluation should consider:

- tool level
- target path
- command or action
- diff size
- sensitive file category
- network access
- artifact persistence
- approval state
- run context
- milestone scope
- applicable security or governance rules

| Level | Name | Examples | Expected Use |
|---|---|---|---|
| Level 0 | Read-only repository context | file search, text search, read bounded file references, inspect project config, read-only `git status` or `git log` if allowed | Milestone 1 |
| Level 1 | Sandbox-local write | edit files inside isolated workspace, create temporary files, generate diff, run tests inside sandbox | Patch / Validation slices |
| Level 2 | External side effect | create branch, create commit, create draft PR, comment on GitHub issue / PR, query CI status | Draft PR MVP |
| Level 3 | High-risk / approval-gated category | modify sensitive files, delete files, change GitHub Actions, change deployment config, change auth / crypto / permission logic, large diff, merge PR, deployment, production access | Approval-gated only |

Milestone 1 should primarily use Level 0.

Patch and Validation milestones may use Level 1.

The Draft PR MVP may use Level 2.

Level 0 must not be treated as automatically safe, because read-only access may still expose sensitive files, secrets, proprietary source, or restricted configuration.

Level 1 must not be treated as automatically allowed, because sandbox-local writes may still affect sensitive files or exceed diff policy.

Level 2 must not be treated as automatically authorized, because external side effects require artifact and policy checks.

Level 3 should be understood as a policy outcome or approval-gated action category, not a substitute for policy evaluation.

Tool permission level classifies capability surface; policy decides authorization for a specific action.

The MVP does not allow automatic merge or deployment.

## Sandbox Boundary

Sandbox execution exists to isolate repository work and make tool behavior auditable.

Sandbox responsibilities:

- isolate repository workspace
- restrict command execution
- restrict filesystem access
- optionally restrict network access
- enforce timeouts
- enforce resource limits
- collect logs
- produce artifacts
- destroy or reset workspace when needed

This RFC does not choose the final sandbox implementation technology. Docker, VM, remote worker, or DeerFlow-based abstractions remain open. The minimum sandbox contract still needs to answer:

- Is the workspace one-time or reusable?
- Is network access allowed?
- Is dependency installation allowed?
- What command timeout policy applies?
- How are stdout and stderr redacted?
- How are workspace artifacts persisted?
- How does sandbox failure enter `ValidationResult` or Durable Run Summary?

Sandbox failure should become structured evidence, not unbounded raw logs.

### Milestone 1 Read-Only Workspace Boundary

Milestone 1 does not require the full sandbox-local write/test execution environment. It requires a controlled read-only workspace boundary for Repository Context Service.

At minimum, Milestone 1 must:

- identify an explicit repository workspace root
- confine all repository reads to that workspace root
- forbid parent-directory escape
- forbid symlink escape
- forbid reads outside the workspace root
- forbid repository file writes
- forbid dependency installation
- forbid network access by default
- forbid arbitrary command execution
- allow only approved read-only search or inspection tools
- ensure approved read-only tools are workspace-confined
- ensure outputs are bounded and redacted according to evidence and summary policy

Any file output must be limited to controlled ForgeFlow artifacts when required, and those artifacts must not mutate the repository workspace.

Evidence references may include file paths, line ranges, match metadata, retrieval metadata, and content hashes by default, but must not embed raw source snippets by default.

Full sandbox-local write, edit, test, dependency installation, arbitrary command execution, and network semantics are deferred to later Level 1 or higher sandbox milestones.

Milestone 1 acceptance must not depend on future write/test sandbox infrastructure.

## Command Policy

Command execution must be policy-gated.

### Command Intent Boundary

Every command execution must be represented as a policy-evaluable Command Intent before execution.

Command Intent is a documentation-level contract for policy evaluation, not necessarily an implementation API in this RFC. It describes the proposed command action in structured form so policy can evaluate the action before sandbox execution.

At minimum, a Command Intent should identify:

- command name
- arguments
- working directory
- environment policy
- requested network access
- expected outputs or artifacts
- timeout request
- output size limit
- workflow step
- contract reference or run reference
- reason for execution
- proposed tool permission level

Command Intent must describe environment policy rather than persist or expose a raw environment dump.

Policy evaluation must consume the Command Intent and return an explicit decision before execution begins. Controlled decision values should include:

- `allowed`
- `blocked`
- `requires_human_approval`

Raw shell strings must not be the unit of policy evaluation.

Shell text, if used by the execution layer, must be derived from or associated with an approved Command Intent.

Execution logs and artifacts must link back to the Command Intent, workflow step, run reference, and relevant contract references so command execution remains auditable and reproducible.

Recommended command policy:

- Unknown commands are denied by default.
- Safe commands may be allowlisted.
- Denylists are secondary protection, not the primary model.
- Command allowlists and denylists are policy inputs; they must not replace Command Intent evaluation.
- Dangerous shell features should be blocked or approval-gated.
- Commands must have timeout limits.
- Commands must have output size limits.
- Commands must be associated with a reason, contract, or workflow step.

Allowed examples may include:

- `git status`
- `git diff`
- `grep` / `ripgrep`
- selected `pytest` tests
- `npm test` only if explicitly configured
- language-specific test commands from project config

Blocked or approval-required examples include:

- `rm -rf`
- broad `chmod` / `chown` changes
- `curl remote script | sh`
- `sudo`
- privileged container execution
- writing outside workspace
- modifying system files
- credential access commands

This RFC gives command-policy direction, not an implementation parser.

### M4 Controlled Execution Boundary

M4 may introduce real execution only through an immutable `CommandIntent` and
a fresh Policy Decision Record. The sandbox workspace is temporary, isolated,
and fixed to the evaluated repository revision; network and dynamic dependency
installation are disabled by default, the environment is prebuilt and
pre-audited, and writes are confined to that workspace. Arbitrary shell input,
repository configuration as authority, and credentials in the sandbox are
forbidden.

M4 creates a deterministic `PatchIntent` and `PatchArtifact` rather than
interpreting a `PatchProposal` as write authority. Before a patch is applied,
the policy profile must evaluate target paths, diff bounds, sensitive paths,
artifact identity, and secret-scan status. Each immutable PatchArtifact has at
most one validation execution attempt; `max_automatic_retries` is `0`.
Failures, timeout, cancellation, sandbox failure, parser failure, and
redaction failure are terminal/failed execution facts. Any later rerun requires
a new intent, attempt, fresh decision, and revalidation of artifact and base
revision.

Secret scanning and redaction use a versioned deterministic local rule set over
the PatchArtifact, diff, persistable artifacts, PR body, and persistable log
summaries. Confirmed secret matches block commit, Draft PR, and raw
persistence. Scanner or redaction failure must be blocked or require approval
as selected by policy; it never defaults to allow. A `SecretScanResult` is an
immutable lineage contract, and a redacted artifact is distinct from its raw
source.

Review after execution is a separate deterministic, provider-free evaluator.
It receives only scanned PatchArtifact, execution summary, SecretScanResult,
and policy lineage, then records findings and severity. Review cannot authorize
execution or a Draft PR; a new Policy Decision Record selects the outcome.

For the allowlisted fixture repository only, a fresh `allowed` decision may
automate branch, commit, and Draft PR creation. Any changed repository or base
revision, changed artifact, sensitive path, secret warning, threshold breach,
or non-allowlisted command requires a bound ApprovalRequest. `blocked` is a
terminal state and approval cannot bypass it. Approval binds action, artifact,
policy version, and repository revision and expires on any input change.

#### M4 Controlled GitHub Issue Input

The GitHub adapter may perform a read-only Issue retrieval only for the
pre-registered fixture repository, configured Issue identity, and expected base
revision. The read operation is a governed adapter action, not sandbox network
access, and it must produce evidence sufficient to bind the resulting task to
that repository and revision.

The adapter normalizes the result into a redacted immutable `TaskInput` before
it enters ForgeFlow workflow state. Raw GitHub Issue payloads must not be
persisted in the controlled artifact store or `DurableRunSummary`. User- or
agent-selected Issues, repositories, and organization resources are denied by
default. Enterprise Issue ingestion requires independently governed repository
onboarding, authorization, retention, and multi-tenant policy; it is outside
M4.

#### M4 Terminal and Failure Semantics

M4 keeps governance decisions separate from execution facts. A
`PolicyDecisionRecord` has one outcome: `allowed`,
`requires_human_approval`, or `blocked`. `allowed` is not a completed action,
and the other two outcomes must not be represented as fabricated command,
exit-code, or output facts.

An `ExecutionAttempt` records only lifecycle facts using `succeeded`,
`failed`, `cancelled`, `timed_out`, or `not_started`. Any non-successful
attempt must carry exactly one failure reason from `policy_blocked`,
`approval_required`, `sandbox_unavailable`, `command_failed`,
`parser_failed`, `redaction_failed`, `base_revision_mismatch`, or
`resource_limit_exceeded`. This reason explains what happened to that attempt;
it does not replace or create a Policy Decision Record. In particular, policy
block and approval requirement produce an immutable `not_started` attempt
fact, distinct from a command that actually started and later failed.

`SecretScanResult` and execution-review `ReviewResult` are fact/finding
contracts. They must not encode execution authorization or Draft PR approval.
A fresh Policy Decision Record consumes their current lineage before any later
action. `PRResult` is likewise an external-side-effect record only: it states
whether the branch, commit, and Draft PR were created, or why they were not;
it never authorizes those mutations.

### Milestone 3 Validation and Review Readiness

Milestone 3 may not interpret a `PatchProposal`, including a proposal's
candidate paths or any future validation-command hint, as an executable
instruction. If M3 introduces validation execution, each concrete command must
first have a structured Command Intent and a fresh Policy Decision Record;
neither a prior M2 boundary decision nor a `PatchProposal` policy reference is
reusable execution authority.

The following decisions remain open and must be resolved in this RFC, an
accepted ADR where a durable choice is made, or an explicitly bounded M3
OpenSpec before implementation begins:

- the authoritative source and versioning model for allowed validation command
  definitions;
- the minimum sandbox boundary and executor identity, including workspace
  lifecycle and isolation guarantees;
- default network, dependency-installation, working-directory, and environment
  policies for validation;
- command allowlist/profile semantics, argument constraints, timeout, output,
  and artifact-size limits;
- redaction before command output or reports become evidence or persisted
  artifacts, including artifact retention and access boundaries;
- the policy outcome and terminal semantics for command denial, approval
  requirement, timeout, cancellation, sandbox failure, parser failure, and
  non-zero exit status; and
- retry eligibility, caps, resource budgets, stop conditions, and human
  approval escalation.

Review remains an evidence-producing recommendation capability. A blocking
review finding may inform a new Policy Decision Record or Human Approval
Request, but it must not itself authorize a command, retry, commit, or PR
action.

For M3, fixture or fake-executor outputs are simulated attempt evidence only.
They must remain deterministic, bounded, and side-effect-free, and they must
not be mistaken for a sandbox implementation or an authorization path. M3
policy fixtures may model both `blocked` and `requires_human_approval` review
outcomes. `blocked` means the platform must not continue the modeled flow;
`requires_human_approval` means the modeled flow is not eligible to continue
without a separately governed approval decision. The governing policy profile
selects between those outcomes.

## Path Policy

All file operations must remain inside the sandbox workspace unless explicitly allowed by policy.

Path policy rules:

- No parent directory escape.
- No symlink escape.
- No absolute path write unless explicitly allowed.
- Generated artifacts should go to a controlled artifact directory.
- Source edits must be diff-tracked.
- Writes outside the workspace are blocked by default.

Path policy is part of Patch Boundary and Sandbox Governance. It must not be delegated to LLM judgment.

## Sensitive File Policy

Sensitive files and areas require policy gating and often Human Approval.

Sensitive categories include:

- `.github/workflows/`
- deployment configuration
- infrastructure files
- production configuration
- auth code
- crypto code
- permission / access control code
- secret / credential files
- environment files
- package manager lockfiles if policy-sensitive
- database migration files if high-risk

Modifying sensitive files is not always forbidden, but it must be policy-gated. In most cases, it should require Human Approval.

## Diff Boundary Policy

Diffs must be bounded and inspectable.

Diff thresholds are policy inputs, not agent suggestions.

Diff boundary policy should be policy-profile based, with conservative global defaults and repo-level overrides only through reviewed configuration.

A diff policy profile should define thresholds and handling rules for:

- changed file count threshold
- total changed line threshold
- deletions
- binary modifications
- generated file handling
- sensitive paths
- scope drift
- human approval thresholds
- hard block thresholds

Policy evaluation must record:

- which policy profile was used
- which thresholds were applied
- which repo-level overrides were active
- which sensitive-path overrides were active
- which generated-file rules were applied
- which rule produced the final decision

Repo-level overrides may adjust thresholds only through reviewed and auditable configuration.

Repo-level overrides must not silently weaken:

- sensitive-path policy
- approval requirements
- hard block rules
- milestone scope constraints
- secret scanning requirements
- external side-effect policy

Agent roles may explain why a large diff is necessary, but they must not create, modify, weaken, or bypass diff thresholds.

The workflow graph and policy middleware must treat threshold values as policy-controlled inputs.

Diff boundary violations should produce one of these policy decisions:

- `allowed`
- `blocked`
- `requires_human_approval`

The policy decision should be recorded in the durable run record and made available to downstream contracts where relevant.

## Secret Scanning and Data Redaction

Secret scanning and redaction are minimum guardrails.

ForgeFlow should:

- scan generated diffs before commit creation, branch packaging, or draft PR packaging
- scan PR body drafts before draft PR creation
- scan logs, tool outputs, command outputs, validation outputs, and trace excerpts before durable persistence or user-facing summaries
- avoid storing secrets in memory
- avoid storing raw source snippets in long-term memory
- redact sensitive tool outputs
- redact credentials, tokens, private keys, and environment values
- prefer trace references and artifact IDs over large raw payloads when possible

A patch artifact with unresolved secret warnings must not be used for commit creation or PR packaging until policy has resolved the warning.

PR body generation must not externally publish:

- tokens
- credentials
- customer data
- sensitive configuration
- unredacted secret-like content

Confirmed secrets must be blocked, not merely approval-gated.

Uncertain or low-confidence secret warnings may require Human Approval or security review according to severity and policy profile.

Secret scanning and redaction results must produce or reference a Policy Decision Record that records:

- scanned artifact
- triggered rules
- severity
- decision
- required approvals if any
- redaction status
- artifact IDs

Secret scanning must be preventive, not merely detective.

Audit trails should show that unsafe artifacts were blocked or redacted before persistence, commit creation, PR packaging, or external publication.

Secret scanning is a minimum guardrail, not a complete security guarantee.

Redaction policy details should align with RFC-005. Memory and contract payload boundaries should align with RFC-002.

## Network Policy

Milestone 1 should not require broad network access.

Recommended network policy:

- Sandbox network defaults to disabled or restricted.
- Dependency installation must be explicit and logged.
- External requests must be policy-evaluated.
- Remote script execution is blocked.
- GitHub API access should happen through governed tools, not arbitrary sandbox network access.

Open questions remain around dependency installation, package registries, and language-specific package managers.

## Resource and Cost Limits

Resource and cost limits prevent runaway execution and unbounded automation.

Limits should include:

- command timeout
- sandbox lifetime
- max tool calls
- max retries
- max validation repair loops
- max output size
- max diff size
- token / model cost budget

These limits prevent infinite loops, token burn, runaway test execution, and unexplained large-scale modifications.

RFC-004 owns the policy shape. Exact values can be decided later through OpenSpec or implementation-specific configuration.

## Human Approval Gates

Human Approval is required for high-risk actions.

Human Approval should be required for:

- high-risk command
- sensitive file modification
- diff exceeding threshold
- validation retry exhaustion
- blocking issues from Review
- secret scan warning
- external side effect beyond draft PR
- non-draft PR creation if supported later
- merge PR
- deployment
- production or credential access

The MVP allows draft PR creation only through policy-gated workflow. It does not allow automatic merge.

Human Approval is independent from Review. Review recommends; policy and Human Approval decide.

### Human Approval Request Boundary

Any Human Approval gate must be represented by a structured Approval Request artifact.

Human Approval must approve a specific policy-gated action artifact, not a vague workflow stage.

An Approval Request should identify:

- requested action
- action intent ID or command intent ID
- triggering policy rule
- risk flags
- affected paths
- sensitive file categories
- diff summary when applicable
- evidence references
- artifact IDs
- validation status when applicable
- review status when applicable
- available approval choices
- expiration or revalidation requirements
- audit record linkage

Approval choices should include at least:

- approve
- reject
- request changes

An approval decision must be scoped to the specific action, artifacts, policy state, and risk context presented in the Approval Request.

It must not be reused for broader actions, changed artifacts, expanded diff scope, different affected paths, or later side effects unless policy explicitly allows reuse and revalidation conditions are satisfied.

If the underlying artifact, diff, policy result, validation result, review result, affected path set, or requested side effect changes after approval, the approval must expire or require revalidation.

Human Approval is an auditable policy gate. It must not be reduced to an unstructured chat prompt.

## Observability and Redaction Requirements

Security-relevant decisions must be visible in traces and durable run records.

ForgeFlow should record:

- policy evaluation result
- tool permission level
- command or action intent summary
- approval requirement
- approval state
- blocked reason
- resource-limit stop reason
- redaction status for persisted excerpts
- artifact IDs for logs, diffs, scans, and PR body drafts

ForgeFlow should avoid recording:

- raw source files
- secrets
- full unredacted logs
- unbounded tool output
- raw environment variables

Detailed trace shape belongs to RFC-005. RFC-004 defines the security and redaction expectations that RFC-005 must respect.

## Relationship with RFC-001

RFC-001 defines workflow roles. RFC-004 defines the action boundaries those roles must obey.

RFC-004 supports RFC-001 by confirming:

- Planner output is advisory, not permission.
- Review recommends; policy decides.
- Human Approval is an independent gate.
- Human Approval approves structured Approval Request artifacts, not vague workflow stages.
- PR role only packages policy-eligible artifacts.
- PR side effects such as branch creation, commit creation, and draft PR creation are separately policy-gated.
- Workflow graph must respect policy outcomes.
- Agent roles must not own policy, approval, retries, or side-effect authorization.

RFC-001 defines authority boundaries. RFC-004 defines the policy mechanisms required to enforce those boundaries.

## Relationship with RFC-002

RFC-004 and RFC-002 must align around structured contracts and durable audit records.

RFC-004 expects:

- policy decisions recorded in contracts or Durable Run Summary
- `risk_flags` informed by policy and review outputs
- `artifact_ids` referencing sandbox logs, diffs, scans, and PR body artifacts
- `evidence_refs` avoiding large raw sensitive payloads
- `stop_reason` recording `blocked`, `approval_required`, `resource_limit_exceeded`, or similar outcomes
- Policy Decision Records referenced from contracts or run summary when policy decisions affect downstream eligibility

Contracts should not become policy engines. Policy authority belongs to RFC-004 and policy middleware; contracts make policy-relevant facts visible.

## Relationship with Milestone 1

Milestone 1 is the Repository Context Foundation Slice.

Milestone 1 primarily uses read-only repository context capability.

Milestone 1 does not require:

- code editing
- test execution
- patch generation
- PR creation

Milestone 1 still requires:

- explicit repository workspace root
- read-only path policy
- evidence reference policy
- trace redaction policy
- workspace boundary
- approved workspace-confined read-only search or inspection tools
- no memory auto-write
- no LLM reasoning inside Repository Context Service
- no dependency installation
- no arbitrary command execution
- no broad network access

Security guardrails must not be postponed simply because Milestone 1 is read-only. The Milestone 1 security scope should be small, but explicit.

## Alternatives Considered

### Alternative A: Trust the Agent to Decide Safety

Rejected.

Agent judgment is not sufficient for enterprise governance. It is not predictable, auditable, or reliable enough to decide command execution, sensitive file changes, external side effects, or approval requirements.

### Alternative B: Sandbox Only, No Policy Layer

Rejected.

Sandboxing reduces blast radius but does not solve external side effects, secret leakage, PR risk, diff scope drift, approval routing, or durable audit requirements.

### Alternative C: Policy-gated Sandbox Execution

Recommended.

This model is auditable, extensible, and aligned with enterprise governance. It allows agents to propose work while policy and runtime gates control execution.

### Alternative D: Human Approval for Everything

Rejected for normal workflow.

Human Approval for every action would block useful automation. It remains appropriate for high-risk actions.

## Trade-offs

- Safety vs automation speed: strict gates slow early development but prevent unsafe automation.
- Deterministic policy vs agent flexibility: policy reduces agent freedom but improves auditability.
- Read-only foundation slice vs faster vertical MVP: starting with read-only context delays PR demos but reduces rework.
- Redaction vs observability completeness: redaction protects sensitive data but may reduce debugging detail.
- Strict command policy vs developer convenience: allowlists reduce risk but require maintenance.
- Sandbox isolation vs dependency installation friction: isolation improves safety but may complicate realistic test execution.

## Risks

- Policy too strict may block useful tasks.
- Policy too loose may allow unsafe actions.
- Redaction may remove debugging information.
- Sandbox may differ from the real CI environment.
- Dependency installation may require network access.
- Secret scanning may produce false positives.
- Hidden path or symlink escape risks may remain.
- Large logs may contain sensitive information.
- Human Approval may become a bottleneck.
- Security assumptions in this RFC may conflict with future DeerFlow extension constraints; RFC-007 must validate integration feasibility.

## Open Questions

- What is the final sandbox implementation: Docker, VM, remote worker, or DeerFlow abstraction?
- What is the exact command allowlist?
- What is the default network policy?
- Where are policy rules stored?
- Who owns policy updates?
- How are approval requests represented?
- How are sandbox artifacts persisted?
- How do logs and artifacts expire?
- Which secret scanner should be used?
- How should sandbox tests align with CI?
- How should package installation be governed across language ecosystems?

## Decision Summary

- Use policy-gated sandbox execution.
- Agent proposes; policy decides.
- Review recommends; policy decides.
- Human Approval is an independent gate.
- Human Approval uses structured Approval Request artifacts.
- Every policy-evaluated action produces a structured Policy Decision Record.
- Command execution requires a policy-evaluable Command Intent before execution.
- Tool permission levels classify capability surface; policy decides authorization for concrete actions.
- Milestone 1 is controlled read-only repository context, not full sandbox-local write/test execution.
- Security guardrails must not be postponed.
- High-risk actions require approval.
- Automatic merge and deployment are out of MVP scope.
- Policy decisions are stored in Durable Run Summary / Audit Record.
- Prefer references and artifacts over raw sensitive payloads.
- Diff thresholds are policy-profile based, with conservative defaults and reviewed repo-level overrides.
- Secret scanning and redaction happen before persistence, commit creation, PR packaging, or external publication.
- Level 0 capability is appropriate for Milestone 1 when policy allows specific read-only actions.
- Level 1 capability is expected for later Patch / Validation slices.
- Level 2 capability is expected for Draft PR MVP.
- Level 3 is an approval-gated action category, not a substitute for policy evaluation.

## RFC-001 Security Acceptance Criteria

RFC-004 is sufficient to unblock RFC-001 acceptance only if it demonstrates that the security, policy, approval, sandbox, retry, and side-effect boundaries required by RFC-001 can be enforced.

At minimum, RFC-004 must confirm that:

- Every executable or side-effecting action is represented by an Action Intent or Command Intent before execution.
- Every policy-evaluated action produces a structured Policy Decision Record with an explicit result such as `allowed`, `blocked`, or `requires_human_approval`.
- Tool permission levels are capability classifications, not final authorization decisions.
- Human Approval uses structured Approval Request artifacts and approves specific policy-gated actions, not vague workflow stages.
- PR side effects, including branch creation, commit creation, and draft PR creation, are separately policy-gated.
- `ReviewResult` cannot authorize PR creation, replace Human Approval, or contain final approval fields such as `approved_for_pr`.
- Diff, secret scanning, path, command, network, artifact persistence, and external side-effect policies can block or escalate actions before execution, persistence, packaging, commit creation, or external publication.
- Retry budgets, resource limits, timeout limits, and stop-condition enforcement are owned by workflow graph / runtime policy, not by workflow roles.
- Policy decisions are persisted into Durable Run Summary or audit records as structured policy evidence.
- Milestone 1 has an explicit read-only workspace boundary that is distinct from later sandbox-local write/test execution.

If RFC-004 cannot satisfy these criteria, RFC-001 must remain Draft until the security and policy boundaries are revised.

## Acceptance Preconditions

RFC-004 should become Accepted only after:

- tool permission levels are agreed
- minimum sandbox boundary is agreed
- command, path, diff, and secret policies are defined at skeleton level
- human approval gates are agreed
- relationship with RFC-001 and RFC-002 is validated
- Milestone 1 constraints are consistent with `docs/product/roadmap/milestones.md`
- no conflict with RFC-007 DeerFlow Extension Strategy is found
