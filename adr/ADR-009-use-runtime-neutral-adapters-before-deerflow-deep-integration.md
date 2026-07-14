# ADR-009: Use Runtime-Neutral Adapters Before DeerFlow Deep Integration

## Status

Accepted

## Context

M4 is the first milestone that may require workflow execution, tool lifecycle,
approval pause/resume, checkpoint mapping, and sandbox integration. ForgeFlow
must evaluate those capabilities without allowing DeerFlow runtime state or
undocumented hooks to define ForgeFlow product semantics.

## Decision

ForgeFlow keeps execution contracts, policy, artifact storage, durable run
summary, and workflow semantics runtime-neutral. M4 first assesses immutable
DeerFlow revision `c0b917cce2cd8b8644a3ed17d58ddb31adc5299a` at source level,
then attaches through ForgeFlow-owned adapters or a local controlled harness.

DeerFlow configuration, checkpoints, tool registration, and runtime state may
not bypass ForgeFlow policy wrappers or become product-layer durable truth. A
submodule, source-level extension, or deeper integration is permitted only
after the assessment demonstrates that documented stable hooks are inadequate
and a later ADR accepts the target revision, coupling, maintenance cost, and
migration risk.

## Consequences

- M4 can test controlled execution without prematurely coupling to DeerFlow.
- Adapter assumptions and revision changes remain explicit and reviewable.
- A deeper integration may add adapter work or delay a capability if upstream
  hooks are insufficient; it cannot be introduced as an implementation shortcut.

## Related RFCs

- [RFC-002](../rfcs/RFC-002-contracts-and-state-model.md)
- [RFC-004](../rfcs/RFC-004-sandbox-and-security-governance.md)
- [RFC-005](../rfcs/RFC-005-observability-and-trace-model.md)
- [RFC-007](../rfcs/RFC-007-deerflow-extension-strategy.md)
