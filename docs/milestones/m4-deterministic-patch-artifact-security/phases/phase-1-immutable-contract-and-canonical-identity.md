# Phase 1: Immutable Contract and Canonical Identity

## 1. Goal

Establish immutable, metadata-only Feature 2 contracts and canonical identity
helpers without introducing policy evaluation, scanning, source access, diff
generation, workspace mutation, persistence, or external effects.

## 2. Scope

### Included

- Frozen, slotted `PatchIntent`, `PatchArtifact`, `SecretScanResult`,
  `RedactionFact`, candidate, and safe validation-error contracts.
- Controlled scan/redaction values, payload-free field boundaries, and safe
  metadata target-scope validation.
- Compact canonical UTF-8 JSON and SHA-256 helpers with self-excluding contract
  identity functions.
- Focused contract/canonical tests and package exports.

### Excluded

- Metadata security profile implementation, detection, redaction, candidate
  eligibility, or service assembly.
- Raw source, raw diff, patch material, source access, execution, sandbox,
  workspace I/O, persistence, approval, PDR evaluation, retry, network, GitHub,
  validation/review, or OCI integration.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `src/forgeflow/deterministic_patch_artifact_security/__init__.py` | Added | Export only Phase 1 contracts. |
| `src/forgeflow/deterministic_patch_artifact_security/models.py` | Added | Define immutable metadata-only contracts and validation. |
| `src/forgeflow/deterministic_patch_artifact_security/canonical.py` | Added | Canonically serialize values and derive SHA-256 identities. |
| `tests/deterministic_patch_artifact_security/__init__.py` | Added | Establish the Phase 1 test package. |
| `tests/deterministic_patch_artifact_security/test_contracts.py` | Added | Verify immutability, controlled values, and excluded fields. |
| `tests/deterministic_patch_artifact_security/test_canonical.py` | Added | Verify canonical serialization and self-excluding identity. |
| `docs/milestones/m4-deterministic-patch-artifact-security/progress.md` | Modified | Record assigned environment and Phase 1 completion. |
| `docs/milestones/m4-deterministic-patch-artifact-security/phases/phase-1-immutable-contract-and-canonical-identity.md` | Added | Record accepted Phase 1 facts. |

## 4. Implementation

The package adds frozen dataclasses for the accepted Feature 2 metadata facts.
`PatchArtifact` contains identity, base revision, target scope, metadata digest,
and lineage only; it has no diff, source, application, or execution fields.
All IDs use a lowercase `sha256:` digest form. Canonical serialization is
compact, sorted UTF-8 JSON and rejects floats and unsupported object values.

## 5. Design Decisions

- Phase 1 uses the existing ForgeFlow canonical JSON/SHA-256 convention while
  using the RFC-required generic digest identity form; contract type determines
  the identity's semantic role.
- Target scope accepts only sorted, unique, workspace-relative logical paths;
  it cannot represent an absolute or parent-escaping workspace path.
- Bounded metadata scanning/redaction remains owned by the accepted profile and
  is deferred intact to Phase 2.

## 6. TDD and Tests

- RED: the initial targeted `unittest` command failed because the new package
  did not yet exist; the worktree test environment also required `PYTHONPATH=src`
  to expose the project source tree.
- GREEN: `PYTHONPATH=src uv run --no-sync python -m unittest tests.deterministic_patch_artifact_security.test_contracts tests.deterministic_patch_artifact_security.test_canonical -v` passed 5 tests after the minimal Phase 1 package was added.
- Refactor/correction: no post-GREEN refactor was required.
- Cumulative verification: `PYTHONPATH=src uv run --no-sync python -m unittest discover -s tests -v` passed 128 tests; `openspec validate deterministic-patch-artifact-security --strict` and `git diff --check` passed.
- Static boundary verification found no subprocess, network, filesystem-path,
  or external-I/O imports in the Phase 1 package.

## 7. Important Fixes and Edge Cases

- `failed` and `indeterminate` scan results require a bounded failure reason;
  `passed` and `blocked` results reject one.
- Failed or indeterminate redaction rejects an output digest, preventing a
  future candidate from being constructed from an ambiguous result.
- Canonical identity excludes only its own identity field, so any other contract
  content change changes the computed digest.

## 8. Commit

- Full commit hash: `6ccb064ef9b9044919a3f557531620d68cb0ed73`
- Commit message: `feat(patch-security): add immutable metadata contracts`

## 9. Acceptance

The focused tests prove contract immutability, absence of diff/application
fields, controlled security values, canonical key ordering, float rejection,
and self-excluding identity. Cumulative tests, OpenSpec validation, diff
hygiene, and the static no-I/O boundary check all passed.

Status: **Accepted**.

## 10. Scope Boundary Confirmation

Phase 1 added no scanner/redactor, policy evaluator, service, diff renderer,
source reader, workspace operation, artifact store, DurableRunSummary, command,
sandbox, approval, retry, GitHub, network, or external side effect.

## 11. Follow-up

Next Phase: Registered Metadata Security Facts. It requires explicit user
authorization before starting.
