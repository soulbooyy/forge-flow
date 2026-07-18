# Change: Approval, Trace, and Durable Summary

## Why

Feature 3 turns eligible Feature 2 metadata lineage into bounded, immutable
metadata-artifact references and an auditable durable summary without creating
patch content or external side effects.

## Scope

- ApprovalRequest/ApprovalDecision facts with expiry and exact input lineage.
- Local controlled publication of immutable metadata artifacts only.
- Append-oriented TraceEvent and DurableRunSummary references.

## Non-goals

- Source access, patch/diff generation or persistence, workspace mutation,
  sandbox execution, GitHub/Draft PR, validation/review, retry, remote store,
  encryption, retention service, or DeerFlow integration.

## Architecture Readiness Gate

RFC-002/004/005 and the Feature 2 terminal-first boundary apply. RFC-005 now
states metadata-only publication. Grill-Me Report findings are incorporated;
this Draft still requires review and acceptance before planning or implementation.

## Impact

Adds Feature 3 contracts without changing Feature 2 publication eligibility or
granting authority to any fact or reference.
