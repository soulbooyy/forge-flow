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
Milestone 0: Project Foundation
```

This stage focuses on project boundaries, architecture methodology, documentation, RFC planning, and scope control. Production implementation has not started.

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

## Documentation

- [Vision](docs/vision.md)
- [Milestones](docs/milestones.md)
- [Development Process](docs/development-process.md)
- [Project Foundation Proposal](docs/project-foundation-proposal.md)
- [Initial Architecture Draft](docs/initial-architecture-draft.md)

## Methodology

ForgeFlow uses a staged, document-driven development process:

- RFC-driven architecture
- OpenSpec feature specification
- Grill-Me architecture review
- Test-driven implementation
- Evaluation from day one

The project should not move from architecture to implementation until the relevant RFC decisions, feature specifications, safety constraints, and evaluation approach are clear.
