# ForgeFlow ADR Index

Architecture Decision Records (ADRs) capture decisions that have become stable enough to guide implementation and future review.

ADRs are not RFCs. RFCs explore and validate architecture options. ADRs record the decision that ForgeFlow currently follows after enough review has happened.

ADRs are also not OpenSpec feature plans. OpenSpec changes define feature-level behavior, design, tasks, and acceptance criteria.

## ADR Status

| Status | Meaning |
|---|---|
| Proposed | The decision is being considered, but is not yet binding. |
| Accepted | The decision is the current project direction. |
| Superseded | The decision has been replaced by a newer ADR or RFC-backed decision. |

## ADRs

| ID | Title | Status | Related RFCs |
|---|---|---|---|
| [ADR-001](ADR-001-treat-agents-as-workflow-roles.md) | Treat Agents as Workflow Roles | Accepted | [RFC-001](../rfcs/RFC-001-agent-architecture.md), [RFC-002](../rfcs/RFC-002-contracts-and-state-model.md), [RFC-004](../rfcs/RFC-004-sandbox-and-security-governance.md), [RFC-007](../rfcs/RFC-007-deerflow-extension-strategy.md) |
| [ADR-002](ADR-002-use-deterministic-repository-context-service.md) | Use Deterministic Repository Context Service | Accepted | [RFC-001](../rfcs/RFC-001-agent-architecture.md), [RFC-002](../rfcs/RFC-002-contracts-and-state-model.md), [RFC-004](../rfcs/RFC-004-sandbox-and-security-governance.md) |
| [ADR-003](ADR-003-separate-forgeflow-product-layer-from-deerflow-runtime.md) | Separate ForgeFlow Product Layer from DeerFlow Runtime | Accepted | [RFC-001](../rfcs/RFC-001-agent-architecture.md), [RFC-007](../rfcs/RFC-007-deerflow-extension-strategy.md) |
| [ADR-004](ADR-004-use-immutable-deterministic-repository-context-contracts.md) | Use Immutable Deterministic Repository Context Contracts | Accepted | [RFC-001](../rfcs/RFC-001-agent-architecture.md), [RFC-002](../rfcs/RFC-002-contracts-and-state-model.md), [RFC-004](../rfcs/RFC-004-sandbox-and-security-governance.md) |
| [ADR-005](ADR-005-use-filesystem-only-repository-context-inspection.md) | Use Filesystem-Only Repository Context Inspection | Accepted | [RFC-002](../rfcs/RFC-002-contracts-and-state-model.md), [RFC-004](../rfcs/RFC-004-sandbox-and-security-governance.md), [RFC-007](../rfcs/RFC-007-deerflow-extension-strategy.md) |
| [ADR-006](ADR-006-store-evidence-references-not-evidence-payloads.md) | Store Evidence References, Not Evidence Payloads | Accepted | [RFC-002](../rfcs/RFC-002-contracts-and-state-model.md), [RFC-004](../rfcs/RFC-004-sandbox-and-security-governance.md) |
| [ADR-007](ADR-007-use-provider-neutral-deterministic-fixture-synthesis-for-m2.md) | Use Provider-Neutral Deterministic Fixture Synthesis for M2 | Accepted | [RFC-002](../rfcs/RFC-002-contracts-and-state-model.md), [RFC-003](../rfcs/RFC-003-tool-and-mcp-integration.md), [RFC-004](../rfcs/RFC-004-sandbox-and-security-governance.md), [RFC-007](../rfcs/RFC-007-deerflow-extension-strategy.md) |
| [ADR-008](ADR-008-use-contract-first-deterministic-fixtures-for-m3.md) | Use Contract-First Deterministic Fixtures for M3 | Accepted | [RFC-002](../rfcs/RFC-002-contracts-and-state-model.md), [RFC-003](../rfcs/RFC-003-tool-and-mcp-integration.md), [RFC-004](../rfcs/RFC-004-sandbox-and-security-governance.md) |
| [ADR-009](ADR-009-use-runtime-neutral-adapters-before-deerflow-deep-integration.md) | Use Runtime-Neutral Adapters Before DeerFlow Deep Integration | Accepted | [RFC-002](../rfcs/RFC-002-contracts-and-state-model.md), [RFC-004](../rfcs/RFC-004-sandbox-and-security-governance.md), [RFC-005](../rfcs/RFC-005-observability-and-trace-model.md), [RFC-007](../rfcs/RFC-007-deerflow-extension-strategy.md) |
| [ADR-010](ADR-010-restrict-m4-github-mutations-to-policy-gated-fixture-repository.md) | Restrict M4 GitHub Mutations to a Policy-Gated Fixture Repository | Accepted | [RFC-003](../rfcs/RFC-003-tool-and-mcp-integration.md), [RFC-004](../rfcs/RFC-004-sandbox-and-security-governance.md), [RFC-005](../rfcs/RFC-005-observability-and-trace-model.md) |
| [ADR-011](ADR-011-use-oci-container-adapter-for-m4-controlled-execution.md) | Use an OCI Container Adapter for M4 Controlled Execution | Accepted | [RFC-004](../rfcs/RFC-004-sandbox-and-security-governance.md), [RFC-005](../rfcs/RFC-005-observability-and-trace-model.md), [RFC-006](../rfcs/RFC-006-evaluation-framework.md), [RFC-007](../rfcs/RFC-007-deerflow-extension-strategy.md) |
| [ADR-012](ADR-012-use-registered-transformers-and-ephemeral-payloads-for-m4.md) | Use Registered Transformers and Ephemeral Payloads for M4 | Proposed | [RFC-008](../rfcs/RFC-008-controlled-materialization-and-mutation-authority.md), [RFC-004](../rfcs/RFC-004-sandbox-and-security-governance.md), [RFC-005](../rfcs/RFC-005-observability-and-trace-model.md) |
