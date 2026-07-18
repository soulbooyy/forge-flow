# Phase 3: Metadata-only Assembly Service

## 1. Goal

Assemble Feature 2's immutable metadata and security facts from a validated M2
`PatchProposal` and the registered fixture binding, without adding source
access, rendering, persistence, authorization, or external side effects.

## 2. Scope

### Included

- Public `build_patch_security_facts` service returning immutable Feature 2
  facts or the existing safe validation-error contract.
- Canonical derivation of `PatchIntent` and metadata-only `PatchArtifact` from
  validated M2 proposal lineage, the registered repository identity, and fixed
  base revision.
- Invocation of Phase 2 scan/redaction/candidate functions, including
  fail-closed scanner terminal handling.
- Validation of M2 proposal/policy self-identities, accepted source/envelope,
  registered M2 profile/evaluator/revalidation data, and fixed no-source
  provenance limitations.
- Focused service tests for clean, blocked, failed, indeterminate, invalid
  lineage, unregistered fixture binding, unregistered M2 policy, and absent
  provenance.

### Excluded

- Source or diff access/generation, workspace mutation, execution, OCI,
  GitHub, branch/commit/PR operations, persistence, artifact-store publication,
  DurableRunSummary, PDR evaluation or approval, validation/review, retry,
  credentials, environment access, and network activity.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `src/forgeflow/deterministic_patch_artifact_security/service.py` | Added | Assemble validated metadata-only Feature 2 facts. |
| `src/forgeflow/deterministic_patch_artifact_security/__init__.py` | Modified | Export the deliberate public service and type aliases. |
| `tests/deterministic_patch_artifact_security/test_service.py` | Added | Verify service terminals, lineage, and prohibited capability boundary. |
| `docs/milestones/m4-deterministic-patch-artifact-security/progress.md` | Modified | Record Phase 3 execution and acceptance. |
| `docs/milestones/m4-deterministic-patch-artifact-security/phases/phase-3-metadata-only-assembly-service.md` | Added | Record Phase 3 evidence and review gate. |

## 4. Implementation

The service accepts only a canonical M2 `PatchProposal` carrying the accepted
M2 source, result envelope, policy profile/version/evaluator, revalidation
flag, candidate digest, and full fixed limitation set. It additionally accepts
only the registered fixture repository identity and fixed base SHA. It derives
metadata-only target scope and change description from bounded M2 candidate
facts, then returns `(PatchIntent, PatchArtifact, SecretScanResult,
RedactionFact, optional candidate)` or a safe validation error. It does not
evaluate a PDR or confer any action authority.

## 5. Design Decisions

- Candidate rationale is the deterministic input to `PatchIntent`'s bounded
  change description, ensuring the actual declared change metadata is scanned
  under the Phase 2 allowlist.
- The service rejects rather than reinterprets an M2 proposal that lacks the
  fixed `no_source_payload` provenance limitation.
- Exact fixture identity and fixed base revision are service preconditions;
  safe-looking arbitrary values cannot create a Feature 2 artifact fact.
- Scanner failed/indeterminate test seams simulate the Phase 2 fact terminals
  without introducing a scanner adapter, retry, or external dependency.

## 6. TDD and Tests

- RED: the initial targeted service test failed because `service.py` did not
  yet exist.
- GREEN: the first service assembly implementation passed 6 targeted tests.
- Refactor/correction: independent review added coverage and implementation
  checks for registered fixture identity/base, fixed M2 source/profile/evaluator
  lineage, and no-source-payload provenance before metadata projection.
- Cumulative verification: `PYTHONPATH=src uv run --no-sync python -m unittest
  discover -s tests -v` passed 152 tests; `openspec validate
  deterministic-patch-artifact-security --strict` and `git diff --check`
  passed.
- Static boundary verification found no subprocess, network, filesystem-path,
  or external-I/O imports in the Feature 2 package.

## 7. Important Fixes and Edge Cases

- Clean facts may yield only an in-memory candidate; blocked, failed, and
  indeterminate facts cannot yield one.
- A changed M2 proposal or policy identity, unregistered evaluator, missing
  provenance limitation, unregistered repository identity, or stale base
  revision returns a safe error with no partial Feature 2 facts.
- No returned fact contains raw source, raw diff, patch content, workspace
  state, action authorization, or persistent artifact reference.

## 8. Commit

- Initial implementation: `0fbb308` — `feat(patch-security): assemble metadata security facts`
- Review correction: `0cf469b` — `fix(patch-security): bind service to registered lineage`

## 9. Acceptance

Targeted service tests passed 8/8. The cumulative suite passed 152 tests.
Strict OpenSpec validation, diff hygiene, and the static no-I/O boundary check
passed. The required independent review completed after corrective review and
approved the final Phase 3 state with no P1/P2 findings.

Status: **Accepted after independent review**.

## 10. Review Gate

- Independent review required: Yes — Phase 3 creates the public Feature 2
  assembly boundary and validates cross-feature lineage.
- Independent review completed: Yes — a read-only independent subagent review
  found three P1 lineage/provenance issues, verified their corrections, and
  approved the final state with no P1/P2.
- Subagent used: Yes.
- Review-method rationale and user-approval scope: The user explicitly extended
  independent subagent review authorization to Phase 3. Independent review was
  required because local tests alone cannot establish that cross-feature
  fixture/profile lineage is bound rather than merely syntactically valid.

## 11. Scope Boundary Confirmation

Phase 3 added no source/diff renderer or reader, filesystem access, workspace
mutation, command, OCI call, GitHub integration, persistence path,
artifact-store object, durable reference, PDR evaluator, approval, validation
or review action, retry, network request, credential, or environment access.
The returned candidate remains in-memory and non-authorizing.

## 12. Follow-up

Next Phase: Acceptance and Boundary Hardening. It remains unstarted and
requires explicit Phase 4 implementation authorization.
