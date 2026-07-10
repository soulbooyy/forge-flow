# ADR-001: Treat Agents as Workflow Roles

Status: Accepted  
Date: 2026-07-10

## Context

ForgeFlow uses several agent-like concepts: Planner, Software Engineer, Validation, Review, and PR. These names are useful for reasoning about responsibilities, but implementing them immediately as production classes, services, microservices, or independent orchestration units would create premature boundaries.

RFC-001 has been accepted as the Agent Architecture baseline and Milestone 1 scope guard. It defines these agents as workflow roles during early milestones.

## Decision

In early milestones, Planner, Software Engineer, Validation, Review, and PR are treated as workflow roles, not production runtime classes, services, or implementation units.

Planner output is declarative, advisory, and non-binding. It may describe task type, goals, assumptions, success criteria, risks, candidate context needs, constraints, and stop-condition candidates. It must not define binding branches, retry loops, tool-call sequences, node execution order, approval routing, validation execution, sandbox edits, or PR creation instructions.

The workflow graph / runtime owns scheduling, branching, retries, stop conditions, policy gates, and execution control.

Role promotion requires future RFC or OpenSpec justification. Milestone 1 must not create production implementation units for Planner, Software Engineer, Validation, Review, or PR.

## Consequences

Positive consequences:

- Keeps role boundaries clear before implementation begins.
- Prevents Planner from becoming a hidden super-agent.
- Keeps scheduling, retry, and stop-condition behavior inspectable.
- Allows Milestone 1 to focus on Repository Context Foundation Slice.
- Makes later role promotion explicit and reviewable.

Negative consequences / trade-offs:

- Slower path to a visible multi-agent demo.
- Some role boundaries remain conceptual until later OpenSpec work.
- Workflow graph design becomes more important.

Follow-up implications:

- Future OpenSpec changes must justify any role becoming a concrete implementation unit.
- Role outputs should align with RFC-002 structured contracts.
- Role actions must remain constrained by RFC-004 policy gates.
- DeerFlow integration must preserve ForgeFlow-owned workflow semantics.

## Alternatives Considered

- Implement each role as a class immediately: rejected because it would encode premature abstractions and invite role-owned control loops.
- Implement each role as a service or microservice: rejected because operational boundaries are not justified for Milestone 1.
- Use a single super-agent for planning, editing, testing, review, and PR creation: rejected because it would weaken governance, observability, and human approval boundaries.

## Related Documents

- [RFC-001: Agent Architecture](../rfcs/RFC-001-agent-architecture.md)
- [RFC-002: Contracts and State Model](../rfcs/RFC-002-contracts-and-state-model.md)
- [RFC-004: Sandbox and Security Governance](../rfcs/RFC-004-sandbox-and-security-governance.md)
- [RFC-007: DeerFlow Extension Strategy](../rfcs/RFC-007-deerflow-extension-strategy.md)
- [Milestones](../docs/milestones.md)
