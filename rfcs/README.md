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
| [RFC-001](RFC-001-agent-architecture.md) | Agent Architecture | Accepted | Define Planner, Software Engineer, Validation, Review, and PR as workflow roles; clarify role boundaries, workflow graph ownership, repair-loop ownership, and human approval separation. |
| [RFC-002](RFC-002-contracts-and-state-model.md) | Contracts and State Model | Draft | Define Runtime State, Durable Run Summary / Audit Record, Long-term Memory, and the required contract families such as `RepositoryContextResult`, `PatchProposal`, `ValidationResult`, `ReviewResult`, and `PRResult`. |
| [RFC-003](RFC-003-tool-and-mcp-integration.md) | Tool and MCP Integration | Accepted | Define the fixture-only, provider-neutral M2 boundary and requirements for future governed tool/MCP integration. |
| [RFC-004](RFC-004-sandbox-and-security-governance.md) | Sandbox and Security Governance | Draft | Define command policy, path policy, network policy, resource limits, diff thresholds, secret scanning, sensitive file policy, cost/retry caps, and human approval gates. |
| [RFC-005](RFC-005-observability-and-trace-model.md) | Observability and Trace Model | Draft | Define product-level run summaries, trace spans, evidence references, redaction, retention, cost metrics, and PR-facing trace summaries. |
| [RFC-006](RFC-006-evaluation-framework.md) | Evaluation Framework | Draft | Define first-version evaluation using controlled fixtures, core metrics, failure tracking, and later paths toward broader benchmarks. |
| [RFC-007](RFC-007-deerflow-extension-strategy.md) | DeerFlow Extension Strategy | Draft | Define how ForgeFlow uses DeerFlow runtime, graph, thread state, tool orchestration, checkpointing, middleware hooks, and tracing hooks without becoming a shallow fork. |

## RFC vs OpenSpec

- RFCs define architecture decisions.
- OpenSpec changes define feature implementation details.

For example, RFC-002 should define the contract model and state boundaries. A later OpenSpec change for Repository Context Service should define the specific feature behavior, tasks, and acceptance criteria for producing `RepositoryContextResult`.
