# RFC-004: Sandbox and Security Governance

## Status

Draft

RFC-004 is an RFC-001 acceptance precondition. RFC-001 should not become Accepted until RFC-004 defines a usable sandbox and security governance skeleton that can enforce the side-effect, approval, retry, and policy boundaries described by RFC-001.

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

## Tool Permission Levels

ForgeFlow tools should be classified by capability level.

| Level | Name | Examples | Expected Use |
|---|---|---|---|
| Level 0 | Read-only repository context | file search, text search, read bounded file references, inspect project config, read-only `git status` or `git log` if allowed | Milestone 1 |
| Level 1 | Sandbox-local write | edit files inside isolated workspace, create temporary files, generate diff, run tests inside sandbox | Patch / Validation slices |
| Level 2 | External side effect | create branch, create commit, create draft PR, comment on GitHub issue / PR, query CI status | Draft PR MVP |
| Level 3 | High-risk / approval-required | modify sensitive files, delete files, change GitHub Actions, change deployment config, change auth / crypto / permission logic, large diff, merge PR, deployment, production access | Approval-gated only |

Milestone 1 should primarily use Level 0.

Patch and Validation milestones may use Level 1.

The Draft PR MVP may use Level 2.

Level 3 requires Human Approval. The MVP does not allow automatic merge or deployment.

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

## Command Policy

Command execution must be policy-gated.

Recommended command policy:

- Unknown commands are denied by default.
- Safe commands may be allowlisted.
- Denylists are secondary protection, not the primary model.
- Commands must be parsed structurally, not only string-matched.
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

Diff boundary policy should evaluate:

- changed file count threshold
- total changed line threshold
- generated file handling
- deletion detection
- binary file modification detection
- sensitive path detection
- scope drift detection

Diff boundary violations should produce one of these policy decisions:

- allowed
- blocked
- requires_human_approval

The policy decision should be recorded in the durable run record and made available to downstream contracts where relevant.

## Secret Scanning and Data Redaction

Secret scanning and redaction are minimum guardrails.

ForgeFlow should:

- scan generated diff
- scan logs if persisted
- scan PR body if generated
- avoid storing secrets in memory
- avoid storing raw source snippets in long-term memory
- redact sensitive tool outputs
- redact credentials, tokens, private keys, and environment values
- prefer trace references and artifact IDs over large raw payloads when possible

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
- PR role only packages policy-eligible artifacts.
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

- read-only path policy
- evidence reference policy
- trace redaction policy
- workspace boundary
- no memory auto-write
- no LLM reasoning inside Repository Context Service

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
- Milestone 1 is read-only repository context.
- Security guardrails must not be postponed.
- High-risk actions require approval.
- Automatic merge and deployment are out of MVP scope.
- Policy decisions are stored in Durable Run Summary / Audit Record.
- Prefer references and artifacts over raw sensitive payloads.
- Level 0 tools are appropriate for Milestone 1.
- Level 1 tools are expected for later Patch / Validation slices.
- Level 2 tools are expected for Draft PR MVP.
- Level 3 actions require Human Approval.

## Acceptance Preconditions

RFC-004 should become Accepted only after:

- tool permission levels are agreed
- minimum sandbox boundary is agreed
- command, path, diff, and secret policies are defined at skeleton level
- human approval gates are agreed
- relationship with RFC-001 and RFC-002 is validated
- Milestone 1 constraints are consistent with `docs/milestones.md`
- no conflict with RFC-007 DeerFlow Extension Strategy is found
