# Phase 1: Contract Foundation and Canonical Fixtures

## 1. Goal

Deliver immutable M4 governed-action contracts, canonical identities, exact
fixture policy constants, and safe computed fixture fragments.

## 2. Scope

### Included

- Frozen, slotted `ActionIntent`, `CommandIntent`, `PolicyDecisionRecord`,
  `ExecutionAttempt`, `ResourceObservations`, and validation-error contracts.
- Canonical UTF-8 JSON, self-excluding SHA-256 identities, and immutable
  ActionIntent → CommandIntent → PDR lineage validation.
- Exact registered fixture/profile constants and Phase 1 safe ID fixtures.
- Phase 1 contract and canonicalization tests.

### Excluded

- Policy assembly or evaluation, OCI execution, workspaces, artifacts,
  approvals, retries, GitHub actions, and all Phase 2+ behavior.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `src/forgeflow/governed_action_sandbox/__init__.py` | Create | Deliberate public Phase 1 contract exports. |
| `src/forgeflow/governed_action_sandbox/models.py` | Create | Immutable contracts, fact combinations, resource and lineage validation. |
| `src/forgeflow/governed_action_sandbox/canonical.py` | Create | Canonical serialization, contract IDs, and PDR input-lineage digest. |
| `src/forgeflow/governed_action_sandbox/profile.py` | Create | Exact registered M4 fixture command and budget constants. |
| `tests/governed_action_sandbox/` | Create | Contract, identity, terminal-fact, budget, and lineage coverage. |
| `openspec/changes/governed-action-sandbox/fixtures/expected/phase-1-contract/canonical-identities.json` | Create | Computed safe identity fragment. |
| `docs/process/implementation-execution.md` | Modify | Require an explicit subagent recommendation and rationale in independent-review approval requests. |
| `docs/milestones/m4-governed-action-sandbox/progress.md` | Modify | Record the assigned M4 execution environment and Phase 1 start. |

## 4. Implementation

Implemented the Phase 1 public contract surface using Python 3.12 standard
library dataclasses. Successful contracts validate their canonical IDs against
their immutable payloads. Execution attempts enforce truthful start/finish,
terminal, budget, and timeout facts; the PDR lineage helpers recompute and
validate ActionIntent → CommandIntent → PDR bindings without I/O.

## 5. Design Decisions

- The M4 registered fixture profile is the sole source of command, image,
  repository, revision, and budget literals.
- Contract IDs exclude their own identity fields and immutable audit timestamps;
  PDR `contract_id` and `decision_id` are equal.
- Command timeout is proven by observed started/finished lifecycle timestamps,
  not by aggregate wall-clock observation alone.
- The implementation follows the accepted governed-action OpenSpec,
  RFC-002/RFC-004/RFC-005/RFC-006, and ADR-011; it creates no execution or
  side-effect capability.

## 6. TDD and Tests

- RED: Added Phase 1 contract/canonical tests before the package existed;
  `uv run --no-sync python -m unittest tests.governed_action_sandbox.test_contracts tests.governed_action_sandbox.test_canonical -v`
  failed with `ModuleNotFoundError` for `forgeflow.governed_action_sandbox`.
- GREEN: Implemented the minimal models, profile, canonical helpers, fixtures,
  and focused corrections discovered during independent review.
- Refactor/correction: Added canonical-ID enforcement; exact terminal/budget,
  timeout-lifecycle, integer exit-code, and cross-contract PDR lineage checks.
- Cumulative verification: `uv run --no-sync python -m unittest discover -s tests -v` passed 141 tests; `openspec validate governed-action-sandbox --strict` and `git diff --check` passed.

## 7. Important Fixes and Edge Cases

- `not_started` attempts reject observed execution facts.
- Stale revision, policy block, approval, sandbox, cancellation, resource, and
  timeout facts remain distinct and bounded.
- Resource-limit identifiers require registered, observed bounds; command
  timeout requires a terminal lifecycle of at least 120000 ms.
- Raw/non-integer exit-code values and forged PDR lineage digests are rejected.

## 8. Commit

`88bbbae` — `feat(governed-action-sandbox): add immutable execution contracts`

## 9. Acceptance

The immutable contract foundation, exact registered fixture constants,
canonical identities, safe fixture fragment, and Phase 1 acceptance tests are
implemented and verified. Independent closure review found no remaining P1/P2
issues after the final corrections.

## 10. Scope Boundary Confirmation

No policy evaluation, OCI backend, subprocess, network, GitHub mutation,
artifact persistence, approval workflow, retry, or Phase 2 behavior was
implemented.

## 11. Follow-up

Phase 2 is the next incomplete canonical-plan phase. It has not been started;
wait for explicit user authorization.
