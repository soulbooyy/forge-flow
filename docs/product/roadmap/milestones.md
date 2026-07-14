# ForgeFlow Milestones

## 1. Purpose

This document defines the staged development roadmap for ForgeFlow.

Its purpose is to:

- define ForgeFlow's phased development path
- distinguish project foundation, foundation slices, vertical MVP, and later expansion
- prevent scope creep
- clarify the goal, scope, exclusions, and exit criteria for each milestone
- give RFCs, OpenSpec changes, implementation work, and evaluation clear stage boundaries

This is not an implementation design document. It does not define APIs, classes, or concrete service implementations.

## 2. Milestone Philosophy

ForgeFlow should progress through deliberate, reviewable stages.

Milestone principles:

- Start with foundation before automation.
- Build horizontal capabilities before full vertical automation.
- Keep Milestone 1 intentionally small.
- Treat the full Draft PR workflow as a later MVP, not the first feature.
- Use RFCs for architecture decisions.
- Use OpenSpec for feature-level implementation specs.
- Keep safety and evaluation present from the beginning.
- Prefer deterministic services for repository facts.
- Prefer structured contracts over free-form agent outputs.

The long-term vision is autonomous software maintenance. The first implementation steps must be smaller than that vision.

## 3. Milestone Overview

| Milestone | Name | Goal | Main Deliverable | Status | Depends On |
|---|---|---|---|---|---|
| Milestone 0 | Project Foundation | Establish project boundaries, documentation system, RFC roadmap, and scope corrections. | Foundation documents, RFC roadmap, and initial ADRs. | Near Complete | Initial architecture draft |
| Milestone 1 | Repository Context Foundation Slice | Build the first deterministic repository context capability. | Repository Context Service OpenSpec and `RepositoryContextResult`. | Completed | Milestone 0, RFC-001/002/004/007 skeleton decisions |
| Milestone 2 | Structured PatchProposal Slice | Produce evidence-backed patch intent from repository context. | Fixture-only `PatchProposal` contract and governed policy boundary. | Completed | Milestone 1, RFC-002/003/004 |
| Milestone 3 | Validation and Review Slice | Establish fixture-only validation facts and blocking-level review findings. | `ValidationResult`, `ValidationTerminal`, `ReviewResult`, and policy lineage contracts. | Completed | Milestone 2, RFC-002/003/004 |
| Milestone 4 | Draft PR MVP Vertical Slice | Complete the first GitHub Issue to Draft PR MVP path. | Controlled draft PR from a fixture or test repository. | Planned | Milestone 3, GitHub/tool policy decisions |
| Milestone 5 | Evaluation and Observability Hardening | Strengthen trace, run summary, redaction, and evaluation. | Reliable eval metrics and product-level run summaries. | Planned | Milestone 4 |
| Milestone 6 | Enterprise Integrations and Scaling | Add optional enterprise integrations after the core loop is stable. | Policy-gated integrations and scalable deployment direction. | Future | Milestone 5 |

## 4. Milestone 0: Project Foundation

Goal: establish project boundaries, documentation workflow, development process, and RFC roadmap.

Scope:

- initialize repository structure
- preserve initial architecture draft
- create Project Foundation Proposal
- create `vision.md`
- create milestone roadmap documents
- create engineering process documents
- define RFC roadmap
- clarify DeerFlow integration strategy
- run Grill-Me architecture review
- capture first round of scope corrections

Exclusions:

- production implementation
- agent classes
- OpenSpec feature implementation
- Repository Context Service code
- sandbox execution code
- PR automation

Exit criteria:

- Project Foundation Proposal exists
- `vision.md` exists
- milestone roadmap documents exist
- engineering process documents exist
- initial architecture draft is preserved
- RFC roadmap is documented
- Milestone 1 and MVP are clearly separated
- current documents are committed to Git

## 5. Milestone 1: Repository Context Foundation Slice

Milestone 1 is not the full MVP.

Status: completed. The implementation and closure evidence are recorded in the
[Milestone 1 progress index](../../milestones/m1-repository-context-foundation/progress.md)
and [retrospective](../../../retrospectives/milestone-1-repository-context-foundation.md).

Goal: implement ForgeFlow's first deterministic foundation capability: Repository Context Service.

The service provides evidence-backed repository context for later PatchProposal, Validation, Review, and Draft PR workflows.

Scope:

- accept repo workspace input
- accept query and optional issue text
- perform file search
- perform text search
- return evidence references
- return relevant files
- return simple test command hints from project config or conventions
- produce `RepositoryContextResult`
- record minimal trace / run summary
- support small controlled evaluation fixtures

Exclusions:

- patch generation
- code editing
- test execution
- draft PR creation
- similar issue retrieval
- full dependency graph
- GitHub issue / PR history ingestion
- large-scale embedding index
- multi-repo support
- automatic memory write
- language-specific deep static analysis

Exit criteria:

- `RepositoryContextResult` contract is specified
- OpenSpec change exists for Repository Context Service
- minimal file/text search works
- evidence references are returned
- controlled evaluation fixtures exist
- scope exclusions are documented
- security assumptions are documented
- no patch generation is introduced in this milestone

## 6. Milestone 2: Structured PatchProposal Slice

Status: completed. The implementation and closure evidence are recorded in the
[Milestone 2 progress index](../../milestones/m2-structured-patchproposal/progress.md)
and [retrospective](../../../retrospectives/m2-structured-patchproposal.md).

Goal: use Repository Context to produce a structured `PatchProposal` that represents minimal code-change intent for later automated repair workflows.

Scope:

- define `PatchProposal` contract
- use `RepositoryContextResult` as input
- derive deterministic fixture root-cause hypotheses and a fix strategy
- identify bounded candidate changed files
- produce structured, declarative patch intent without a diff
- enforce patch boundary policy
- record risk flags and evidence references

Exclusions:

- real LLM, MCP, DeerFlow runtime, or other provider integration
- source-code edits, diff generation, sandbox mutation, command execution, or
  test execution
- full autonomous repair loop
- PR creation
- automatic merge
- multi-round validation repair
- large-scale refactoring
- sensitive file modification without approval

Exit criteria:

- `PatchProposal` contract is documented
- patch proposal is evidence-backed
- changed files are bounded
- risk flags are produced
- patch boundary policy is enforced
- basic tests or fixtures exist

## 7. Milestone 3: Validation and Review Slice

Status: completed. The implementation and closure evidence are recorded in the
[Milestone 3 progress index](../../milestones/m3-validation-review-slice/progress.md)
and [retrospective](../../../retrospectives/m3-validation-review-slice.md).

Goal: establish auditable, immutable `ValidationResult`, `ValidationTerminal`,
and `ReviewResult` contracts so ForgeFlow can model validation facts, terminal
governance, and blocking-level review before it introduces command execution.

Scope:

- define `ValidationResult` contract
- define separate `ValidationTerminal` contract
- define `ReviewResult` contract
- define artifact/evidence and Policy Decision Record lineage
- use deterministic fixtures/fake executor inputs to model passed/failed
  attempt facts, governance terminals, and review findings
- detect fixture-mode blocking review issues and reference policy outcomes

Exclusions:

- infinite repair loop
- real command execution, test execution, command parsing, or sandbox platform
- workspace access/mutation, network, dynamic dependency installation, or
  provider/DeerFlow runtime integration
- retry policy or runtime retry enforcement
- full CI integration
- automatic production deployment
- automatic merge
- broad style-only code review comments

Exit criteria:

- `ValidationResult`, `ValidationTerminal`, and `ReviewResult` are documented
  as separate immutable contracts
- no unexecuted flow can claim command, exit-code, or output facts
- policy terminals and review findings have auditable evidence/artifact lineage
- Review only records findings; policy decides `blocked` or
  `requires_human_approval`
- no M3 implementation introduces an execution, sandbox, retry, or side-effect
  capability

## 8. Milestone 4: Draft PR MVP Vertical Slice

Status: Execution Architecture Readiness in progress. M4 must not create one
OpenSpec for the complete Issue-to-Draft-PR path, and no implementation
environment is authorized until the readiness gates below are accepted.

Goal: complete the first true vertical MVP:

```text
GitHub Issue
  -> Sandbox
  -> Repository Context
  -> PatchProposal
  -> Validation
  -> Review
  -> Draft PR
```

Scope:

- pre-registered fixture GitHub Issue input, normalized as `TaskInput`
- sandbox workspace setup
- repository context retrieval
- `PatchProposal` generation
- governed code modification
- test validation
- blocking-level review
- draft PR creation
- PR body generated from structured contracts
- human approval gates for high-risk actions
- traceable run summary

Exclusions:

- automatic merge
- automatic deployment
- Jira integration
- Slack approval
- multi-repo orchestration
- complex enterprise permission system
- full SWE-bench support

Exit criteria:

- a GitHub Issue can produce a draft PR in a controlled fixture or test repository
- PR body contains root cause, changes, validation, risk, and trace summary
- high-risk actions are blocked or require approval
- validation automatic retry is fixed at `0`
- run summary is persisted
- evaluation result is recorded

### M4 Feature Decomposition and Readiness Gates

M4 will use multiple dependent feature changes rather than one end-to-end
OpenSpec:

1. **Governed action and sandbox boundary** — `ActionIntent`/`CommandIntent`,
   policy evaluation, temporary fixed-revision workspace, and terminal
   execution semantics.
2. **Deterministic patch artifact and security scanning** — `PatchIntent`,
   `PatchArtifact`, path/diff controls, `SecretScanResult`, redaction, and
   immutable lineage.
3. **Approval, trace, and durable summary** — ApprovalRequest/Decision,
   execution-attempt lineage, local controlled artifact store, and
   ForgeFlow-owned DurableRunSummary.
4. **Fixture-repository GitHub Draft PR adapter** — allowlisted repository
   identity, opaque credential boundary, idempotent branch/commit materialization,
   and Draft PR result.
5. **M4 evaluation and acceptance** — controlled fault cases, policy terminals,
   idempotency, redaction, and end-to-end evidence.

Each change requires its own accepted architecture inputs, Grill-Me review,
OpenSpec, and readiness gate. The first M4 change remains blocked until
RFC-004/005/006/007 design boundaries are accepted and the cross-contract
lineage is reconciled. M4 has formally selected a ForgeFlow-owned local
controlled harness and runtime-neutral adapter seam; the separate DeerFlow-
backed adapter gate remains blocked and cannot authorize implementation.
M4 additionally requires a real external fixture-environment registration
package before any GitHub adapter implementation: repository owner/name/ID,
Issue number/ID, fixed base commit SHA, credential mode, reset/audit procedure,
concrete policy budgets, and acceptance thresholds. These are controlled inputs
and must not be invented by architecture or implementation work.
The required registration fields are maintained in the
[M4 Fixture Environment Registration](../../fixtures/m4-fixture-environment-registration.md)
template; it does not authorize provisioning or implementation.

## 9. Milestone 5: Evaluation and Observability Hardening

Goal: strengthen evaluation, trace, run summary, security redaction, and audit capabilities.

Scope:

- expand controlled fixtures
- track context retrieval precision
- track test recommendation usefulness
- track patch size and changed files
- track validation determinism
- track run summary completeness
- add redaction policy for prompts, tool outputs, logs, and diffs
- improve observability dashboard or trace format
- add cost and retry metrics

Exclusions:

- large-scale enterprise deployment
- full SWE-bench automation as mandatory baseline
- production SRE-level monitoring
- complex analytics platform

Exit criteria:

- evaluation metrics are consistently recorded
- redaction policy is documented and applied
- run summaries are useful for PR review and retrospectives
- cost, retry, and failure metrics are available
- known failure modes are documented

## 10. Milestone 6: Enterprise Integrations and Scaling

Goal: expand enterprise integrations and scaling only after the core loop is stable.

Possible scope:

- Jira integration
- Slack or IM approval
- deeper GitHub Actions integration
- similar issue retrieval
- Git / PR history retrieval
- multi-repo support
- repository memory with manual approval
- role-based permission model
- deployment in isolated worker infrastructure
- optional SWE-bench / SWE-bench Verified evaluation

Exclusions:

- anything that compromises safety boundaries
- automatic merge without explicit approval policy
- storing source code or secrets in memory
- unbounded autonomous repair

Exit criteria:

- enterprise integrations are optional and policy-gated
- security model scales with integrations
- evaluation covers both offline fixtures and online usage
- memory writes require clear approval policy
- system remains auditable and governable

## 11. Relationship Between Milestones and RFCs

Milestones and RFCs serve different purposes.

- Milestones define delivery stages.
- RFCs define architecture decisions.
- OpenSpec changes define feature implementation details.

Milestone 0 produces the RFC roadmap.

Required RFCs:

- RFC-001 supports Agent Architecture.
- RFC-002 supports State Model and Structured Contracts.
- RFC-003 supports Tool and MCP Integration.
- RFC-004 supports Sandbox and Security Governance.
- RFC-005 supports Observability and Trace Model.
- RFC-006 supports Evaluation Framework.
- RFC-007 supports DeerFlow Extension Strategy.

RFCs should be written before implementation when a decision affects multiple milestones, contracts, security posture, runtime integration, or evaluation.

## 12. Relationship Between Milestones and OpenSpec

OpenSpec should not be used for the entire MVP at once.

Each milestone may contain one or more OpenSpec changes. Each OpenSpec change should describe a focused feature and include:

- `proposal.md`
- `design.md`
- `tasks.md`

The first OpenSpec change should be Repository Context Service.

OpenSpec should be created only after the relevant RFC skeleton decisions exist. For Repository Context Service, the relevant skeleton decisions are:

- RFC-001 Agent Architecture
- RFC-002 State Model and Structured Contracts
- RFC-004 Sandbox and Security Governance
- RFC-007 DeerFlow Extension Strategy

RFC-003, RFC-005, and RFC-006 may be drafted in parallel and referenced by the first OpenSpec, but they do not need to be fully complete before the Repository Context Service spec begins.

## 13. Scope Control Rules

These rules protect ForgeFlow from turning the long-term vision into the first implementation.

- Milestone 1 must not expand into patch generation.
- Repository Context Service must remain deterministic in Milestone 1.
- Milestone 1 must not include autonomous code editing.
- Milestone 1 must not include validation repair loops.
- Milestone 1 must not include PR creation.
- Repository Context Service must not use LLM reasoning in Milestone 1.
- Draft PR is not required before Milestone 4.
- Similar issue retrieval is not required before Milestone 6.
- SWE-bench is not required for the first evaluation milestone.
- Automatic merge is out of scope for the MVP.
- Jira and Slack are out of scope for the MVP.
- Memory auto-write is out of scope for early milestones.
- Security guardrails must not be postponed entirely to later phases.

Any proposal that violates these rules should either be rejected, deferred, or written as an explicit RFC with a clear tradeoff discussion.

## 14. Milestone Exit Checklist

Use this checklist before declaring any milestone complete:

- [ ] Scope completed
- [ ] Exclusions respected
- [ ] Relevant RFCs updated
- [ ] OpenSpec tasks updated
- [ ] Tests or evaluation fixtures updated
- [ ] Security implications reviewed
- [ ] Observability requirements reviewed
- [ ] Documentation updated
- [ ] Git history contains meaningful commits
- [ ] Retrospective created if milestone is complete

## 15. Current Status

Current milestone:

```text
Milestone 3: Validation and Review Slice
Status: Completed; closure verification recorded
Next stage: architecture and specification preparation for Milestone 4
```

Completed:

- Project foundation documents created.
- RFC roadmap created.
- RFC-001 Agent Architecture baselined and accepted as the Milestone 1 scope guard.
- RFC-002 Contracts and State Model drafted and reviewed.
- RFC-004 Sandbox and Security Governance drafted and reviewed.
- RFC-007 DeerFlow Extension Strategy drafted and reviewed.
- DeerFlow upstream revision recorded.
- DeerFlow extension-point assessment completed.
- Initial ADRs recorded.
- Milestone 1 and full MVP boundary clarified.
- Milestone 2 fixture-only PatchProposal contract and conservative policy
  boundary completed and closure-verified.
- Milestone 3 fixture-only validation, terminal, review, and policy-lineage
  contracts completed and closure-verified.

Next steps:

- retain M1–M3 contracts as the dependency boundary for Milestone 4 planning
- do not introduce a real provider, MCP, DeerFlow runtime, sandbox, command,
  test, Git, or PR behavior without newly accepted scope and governance
