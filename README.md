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
Current phase: transitioning from RFC-driven Architecture to OpenSpec Feature Planning
Milestone 0: Project Foundation near complete
```

The project foundation documentation, first accepted architecture baseline, DeerFlow extension assessment, and initial ADRs are now in place. Production implementation has not started.

Milestone 1 will be the Repository Context Foundation Slice. It is not the full MVP.

Milestone 1 is limited to a deterministic Repository Context Service that can provide repository context such as relevant files, evidence references, file/text search results, and simple test command hints. It will not generate patches, edit code, create pull requests, or run an autonomous repair loop.

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

- [Vision](docs/vision.md)
- [Milestones](docs/milestones.md)
- [Development Process](docs/development-process.md)
- [Project Foundation Proposal](docs/project-foundation-proposal.md)
- [Initial Architecture Draft](docs/initial-architecture-draft.md)
- [DeerFlow Extension Assessment](docs/assessments/deerflow-extension-points.md)
- [RFC Index](rfcs/README.md)
- [ADR Index](adr/README.md)

## Architecture Records

ForgeFlow uses three levels of architecture and delivery documentation:

- RFCs are used for architecture proposals and review.
- ADRs are used for accepted architecture decisions.
- OpenSpec will be used for feature-level implementation specifications.

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

1. Initialize OpenSpec.
2. Create the Repository Context Service change spec.
3. Run Grill-Me review on the OpenSpec change.
4. Prepare the Milestone 1 implementation plan.
5. Do not implement patch generation, validation repair loop, or PR creation in Milestone 1.
