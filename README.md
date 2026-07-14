# ForgeFlow

ForgeFlow is an enterprise autonomous software engineering agent platform built on DeerFlow and LangGraph.

The long-term goal is to support governed, observable, and evaluable software maintenance workflows such as:

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

ForgeFlow is not a general coding assistant, chatbot, or toy agent demo. It is intended to become a production-oriented platform for preparing evidence-backed, testable, reviewable engineering changes.

## Current Status

ForgeFlow is currently in:

```text
Current phase: Milestone 3 closure complete
Next stage: architecture and specification preparation for Milestone 4
```

The project foundation documentation, accepted architecture baseline, DeerFlow
extension assessment, and initial ADRs are in place. Milestone 1 implemented
the deterministic Repository Context Foundation Slice and completed its
contract, fixtures, acceptance coverage, and hardening verification.

Milestone 1 was limited to a deterministic Repository Context Service that
provides relevant files, evidence references, file/text search results, and
descriptive test command hints. It did not generate patches, edit code, create
pull requests, or run an autonomous repair loop. See the [Milestone 1 progress
index](docs/milestones/m1-repository-context-foundation/progress.md) and
[retrospective](retrospectives/milestone-1-repository-context-foundation.md).

Milestone 2 added a deterministic, fixture-only `PatchProposal` contract that
binds bounded root-cause and candidate-change intent to M1 evidence and the
versioned conservative policy profile. It produces declarative proposals or
safe validation envelopes only; it does not call a provider, create a diff,
read or mutate a workspace, run commands/tests, or perform Git/PR actions. See
the [Milestone 2 progress index](docs/milestones/m2-structured-patchproposal/progress.md)
and [retrospective](retrospectives/m2-structured-patchproposal.md).

Milestone 3 added immutable, fixture-only `ValidationResult`,
`ValidationTerminal`, and `ReviewResult` contracts with independent policy,
artifact, and evidence lineage. It records completed deterministic facts,
governance terminals, and review findings without granting command authority or
introducing sandbox, workspace, network, retry, provider, Git, or PR behavior.
See the [Milestone 3 progress index](docs/milestones/m3-validation-review-slice/progress.md)
and [retrospective](retrospectives/m3-validation-review-slice.md).

The later MVP is the GitHub Issue to Draft PR vertical slice:

```text
GitHub Issue
  -> Sandbox
  -> Repository Context
  -> PatchProposal
  -> Validation
  -> Review
  -> Draft PR
```

## Documentation Navigation

- [Documentation Index](docs/index.md)
- [Vision](docs/product/vision.md)
- [Milestones](docs/product/roadmap/milestones.md)
- [Development Process](docs/process/index.md)
- [Project Foundation Proposal](docs/architecture/foundation/project-foundation-proposal.md)
- [Initial Architecture Draft](docs/_history/architecture/initial-architecture-draft.md)
- [DeerFlow Extension Assessment](docs/architecture/assessments/deerflow-extension-points.md)
- [RFC Index](rfcs/README.md)
- [ADR Index](adr/README.md)

## Architecture Records

ForgeFlow uses three levels of architecture and delivery documentation:

- RFCs are used for architecture proposals and review.
- ADRs are used for accepted architecture decisions.
- OpenSpec defines feature-level implementation specifications.

Core RFCs:

- [RFC-001 Agent Architecture](rfcs/RFC-001-agent-architecture.md)
- [RFC-002 Contracts and State Model](rfcs/RFC-002-contracts-and-state-model.md)
- [RFC-004 Sandbox and Security Governance](rfcs/RFC-004-sandbox-and-security-governance.md)
- [RFC-007 DeerFlow Extension Strategy](rfcs/RFC-007-deerflow-extension-strategy.md)

Current ADRs:

- [ADR-001 Treat Agents as Workflow Roles](adr/ADR-001-treat-agents-as-workflow-roles.md)
- [ADR-002 Use Deterministic Repository Context Service](adr/ADR-002-use-deterministic-repository-context-service.md)
- [ADR-003 Separate ForgeFlow Product Layer from DeerFlow Runtime](adr/ADR-003-separate-forgeflow-product-layer-from-deerflow-runtime.md)

## Methodology

ForgeFlow uses a staged, document-driven development process:

- RFC-driven architecture
- OpenSpec feature specification
- Grill-Me architecture review
- Test-driven implementation
- Evaluation from day one

The project should not move from architecture to implementation until the relevant RFC decisions, feature specifications, safety constraints, and evaluation approach are clear.

## Next Steps

1. Review the Milestone 3 retrospective and closure evidence.
2. Establish the architecture and OpenSpec scope for Milestone 4.
3. Keep provider integration, code mutation, validation execution, and PR
   behavior outside work until their own contracts and governance are accepted.
