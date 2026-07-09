# ForgeFlow RFC Index

RFCs are used to document architecture decisions before implementation.

In ForgeFlow, RFCs should be used for cross-cutting design topics such as agent architecture, state and contracts, tool integration, sandbox governance, observability, evaluation, and DeerFlow extension strategy.

RFCs are not feature implementation specs. Feature-level implementation plans belong in OpenSpec changes under `specs/` or `openspec/`.

## RFC Status

| Status | Meaning |
|---|---|
| Draft | The RFC is being written or reviewed. It is not yet an accepted project decision. |
| Accepted | The RFC has been accepted as the current architecture direction. Follow-up ADRs may record final decisions. |
| Superseded | The RFC has been replaced by a newer RFC or decision. The document remains for historical context. |

## Planned RFCs

| RFC | Title | Status | Purpose |
|---|---|---|---|
| [RFC-001](RFC-001-agent-architecture.md) | Agent Architecture | Draft | Define Planner, Software Engineer, Validation, Review, and PR as workflow roles; clarify role boundaries, workflow graph ownership, repair-loop ownership, and human approval separation. |
| RFC-002 | State Model and Structured Contracts | Draft | Define Runtime State, Durable Run Summary / Audit Record, Long-term Memory, and the required contract families such as `RepositoryContextResult`, `PatchProposal`, `ValidationResult`, `ReviewResult`, and `PRResult`. |
| RFC-003 | Tool and MCP Integration | Draft | Define tool capability levels, evidence-returning requirements, MCP integration boundaries, sandbox edit access, and external write policy. |
| RFC-004 | Sandbox and Security Governance | Draft | Define command policy, path policy, network policy, resource limits, diff thresholds, secret scanning, sensitive file policy, cost/retry caps, and human approval gates. |
| RFC-005 | Observability and Trace Model | Draft | Define product-level run summaries, trace spans, evidence references, redaction, retention, cost metrics, and PR-facing trace summaries. |
| RFC-006 | Evaluation Framework | Draft | Define first-version evaluation using controlled fixtures, core metrics, failure tracking, and later paths toward broader benchmarks. |
| RFC-007 | DeerFlow Extension Strategy | Draft | Define how ForgeFlow uses DeerFlow runtime, graph, thread state, tool orchestration, checkpointing, middleware hooks, and tracing hooks without becoming a shallow fork. |

## RFC vs OpenSpec

- RFCs define architecture decisions.
- OpenSpec changes define feature implementation details.

For example, RFC-002 should define the contract model and state boundaries. A later OpenSpec change for Repository Context Service should define the specific feature behavior, tasks, and acceptance criteria for producing `RepositoryContextResult`.
