# ADR-003: Separate ForgeFlow Product Layer from DeerFlow Runtime

Status: Accepted  
Date: 2026-07-10

## Context

ForgeFlow is built on DeerFlow and LangGraph, but it should not become a renamed DeerFlow fork or a copy of DeerFlow source. The project needs a clear boundary between upstream runtime foundations and ForgeFlow's software engineering product semantics.

RFC-007 defines the DeerFlow extension strategy and records the DeerFlow upstream reference used for Milestone 1 assessment.

## Decision

ForgeFlow treats DeerFlow as upstream framework/runtime foundation, while ForgeFlow owns software-engineering product semantics.

DeerFlow may provide runtime, graph, thread, tool orchestration, checkpoint, middleware, and tracing foundations where applicable.

ForgeFlow owns workflow roles, structured contracts, Repository Context Service, `RepositoryContextResult`, sandbox governance, security policy, PR workflow semantics, product-level run summary, evaluation, and human approval semantics.

ForgeFlow should not modify DeerFlow core during Milestone 1 unless a future RFC explicitly justifies it.

DeerFlow revision and extension assumptions are documented in RFC-007 and `docs/assessments/deerflow-extension-points.md`.

## Consequences

Positive consequences:

- Keeps ForgeFlow product behavior separate from DeerFlow framework mechanics.
- Preserves upstream compatibility.
- Avoids prematurely forking or copying DeerFlow source.
- Makes integration assumptions explicit and reviewable.
- Protects ForgeFlow contracts, policy boundaries, and durable state from hidden runtime coupling.

Negative consequences / trade-offs:

- Some integration work may require adapters or wrappers.
- Avoiding DeerFlow core changes may slow early implementation if extension hooks are missing.
- Contributors must understand both the upstream framework boundary and ForgeFlow-owned product semantics.

Follow-up implications:

- Milestone 1 may use DeerFlow as reference or minimal runtime foundation, but must not require a deep fork.
- Future reliance on DeerFlow internals must be recorded as an integration assumption.
- Future submodule or fork decisions should be recorded through RFC or ADR.
- Later milestones require deeper source-level assessment before relying on DeerFlow internals for write/test/PR workflows.

## Alternatives Considered

- Build ForgeFlow entirely inside DeerFlow core: rejected because it would blur framework and product ownership.
- Copy DeerFlow source into ForgeFlow: rejected because it would lose upstream tracking and make maintenance harder.
- Fork DeerFlow immediately: rejected for Milestone 1 because deep core changes have not been proven necessary.

## Related Documents

- [RFC-001: Agent Architecture](../rfcs/RFC-001-agent-architecture.md)
- [RFC-007: DeerFlow Extension Strategy](../rfcs/RFC-007-deerflow-extension-strategy.md)
- [DeerFlow Extension-Point Capability Assessment](../docs/assessments/deerflow-extension-points.md)
- [Vision](../docs/vision.md)
- [Milestones](../docs/milestones.md)
