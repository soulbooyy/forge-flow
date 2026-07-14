# ADR-011: Use an OCI Container Adapter for M4 Controlled Execution

## Status

Accepted

## Context

M4 is ForgeFlow's first real controlled-execution slice. A local controlled
harness defines ForgeFlow's policy and adapter ownership, but it cannot alone
prove network isolation, filesystem isolation, or execution-environment
constraints. Host-process execution and DeerFlow sandbox behavior do not meet
the required M4 security boundary.

## Decision

M4 uses a ForgeFlow-owned OCI container adapter as its controlled-execution
infrastructure. The local controlled harness remains the product-level owner
of policy decisions, immutable contracts, artifact lineage, and durable state;
the OCI adapter only supplies an isolated execution capability.

Each `ExecutionAttempt` uses a pre-audited OCI image pinned by immutable digest
and a temporary isolated workspace fixed to the evaluated repository revision.
The workspace is destroyed when the attempt ends. The adapter must enforce no
network access, no credential injection, no dynamic dependency installation,
and writes confined to the sandbox workspace. The controlled artifact store is
not mounted into the execution environment.

Docker or Podman may implement the adapter only when they satisfy this OCI
contract. Neither is a ForgeFlow architecture dependency. If a selected backend
cannot prove every required capability, no host-process fallback is permitted:
the attempt fails closed as `sandbox_unavailable`.

DeerFlow runtime and sandbox facilities are not M4 security-boundary owners and
may not bypass the ForgeFlow adapter or policy wrapper.

## Consequences

- M4 can prove a bounded, reproducible execution boundary without binding its
  product contracts to a container vendor or DeerFlow.
- Fixture images must be built and audited before they are registered; dynamic
  package installation is not an M4 escape hatch.
- Backend capability verification and the `sandbox_unavailable` fault path are
  mandatory later OpenSpec acceptance cases.
- Future VM, remote-worker, or other sandbox backends require a new assessment
  and ADR if they change the security guarantees or adapter contract.

## Related RFCs

- [RFC-004](../rfcs/RFC-004-sandbox-and-security-governance.md)
- [RFC-005](../rfcs/RFC-005-observability-and-trace-model.md)
- [RFC-006](../rfcs/RFC-006-evaluation-framework.md)
- [RFC-007](../rfcs/RFC-007-deerflow-extension-strategy.md)
