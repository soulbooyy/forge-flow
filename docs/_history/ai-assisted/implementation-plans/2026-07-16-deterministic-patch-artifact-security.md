# Deterministic Patch Artifact and Security Scanning Implementation Draft Plan

> **Non-canonical planning evidence.** Generated with Superpowers
> `writing-plans`; reconcile against the accepted Feature 2 OpenSpec,
> RFC-002/004/005 scoped amendments, RFC-006, ADR-011, the M4 Fixture
> Environment Registration, and the accepted M4 Patch Metadata Security Profile
> before execution. This file never authorizes a phase.

**Goal:** Build deterministic, metadata-only patch/security facts from an M2
PatchProposal without source access, diff generation, workspace mutation,
persistence, or authorization.

**Architecture:** Add one focused Python package parallel to `patch_proposal`
and `validation_review`. Immutable models and canonical identity come first;
the accepted metadata security profile drives scan/redaction facts; a service
then assembles the only public envelope and optional in-memory candidate.

**Tech Stack:** Python 3.12 standard library, frozen dataclasses, canonical
UTF-8 JSON/SHA-256 helpers, and `unittest`; no dependencies or external tools.

## Global Constraints

- Create no raw source, raw diff, patch material, workspace path, credential,
  environment value, command output, artifact-store object, or GitHub effect.
- Consume only `PatchProposal` lineage and the registered metadata security
  profile; no user, Issue, agent, repository, or artifact input can select
  rules or budgets.
- `PatchArtifact` is metadata-only; source access and patch materialization are
  outside this milestone.
- Scanner failure, redaction failure, indeterminate results, and blocked
  findings yield no candidate and are later PDR `blocked` inputs.
- No implementation environment is assigned by this plan. Phase 1 needs the
  separately authorized branch and worktree named in the canonical plan.

## File Structure

| File | Responsibility |
| --- | --- |
| `src/forgeflow/deterministic_patch_artifact_security/models.py` | Frozen contracts, controlled values, and safe validation envelopes. |
| `src/forgeflow/deterministic_patch_artifact_security/canonical.py` | Canonical JSON, SHA-256, and identity helpers. |
| `src/forgeflow/deterministic_patch_artifact_security/profile.py` | In-code representation of the accepted metadata security profile. |
| `src/forgeflow/deterministic_patch_artifact_security/policy.py` | Metadata projection, deterministic detection, redaction, and candidate eligibility. |
| `src/forgeflow/deterministic_patch_artifact_security/service.py` | Metadata-only assembly from M2 PatchProposal to Feature 2 envelope. |
| `src/forgeflow/deterministic_patch_artifact_security/__init__.py` | Deliberate public exports only. |
| `tests/deterministic_patch_artifact_security/test_contracts.py` | Contract/forbidden-payload tests. |
| `tests/deterministic_patch_artifact_security/test_canonical.py` | Identity and canonicalization tests. |
| `tests/deterministic_patch_artifact_security/test_policy.py` | Profile, detection, redaction, and fail-closed tests. |
| `tests/deterministic_patch_artifact_security/test_service.py` | End-to-end in-memory assembly tests. |
| `tests/deterministic_patch_artifact_security/test_acceptance.py` | Feature acceptance and no-side-effect boundary tests. |

## Phase 1: Immutable Contract and Canonical Identity

**Depends on:** Accepted OpenSpec and metadata security profile.

**Files:** Create the package initializer, `models.py`, `canonical.py`, and the
contract/canonical test modules.

**Interfaces:** `PatchIntent`, `PatchArtifact`, `SecretScanResult`,
`RedactionFact`, `RedactedArtifactReferenceCandidate`, and
`DeterministicPatchArtifactSecurityValidationError` are frozen contracts.
`intent_id_for`, `artifact_id_for`, `scan_id_for`, `redaction_id_for`, and
`validation_error_id_for` derive IDs from canonical payloads with their own ID
field omitted.

- [ ] Write failing tests for required fields, controlled scan/redaction values,
  forbidden raw payloads, absent-output conditions, deterministic IDs, and
  canonical ordering.
- [ ] Run `uv run --no-sync python -m unittest tests.deterministic_patch_artifact_security.test_contracts tests.deterministic_patch_artifact_security.test_canonical -v`; expect missing-module failures.
- [ ] Implement only the frozen contracts and identity helpers required by those
  tests; preserve M2 canonical JSON conventions.
- [ ] Re-run the targeted command; expect all tests to pass.
- [ ] Plan one focused commit: `feat(patch-security): add immutable metadata contracts`.

## Phase 2: Registered Metadata Security Facts

**Depends on:** Phase 1.

**Files:** Create `profile.py`, `policy.py`, and `test_policy.py`.

**Interfaces:** `M4_PATCH_METADATA_SECURITY_V1` exposes the accepted IDs,
allowlisted fields, ordered detection rules, result semantics, and redaction
statuses. `scan_metadata` returns `SecretScanResult`; `redact_metadata` returns
`RedactionFact` and an in-memory digest only; `candidate_for` returns a
candidate only for passed/not-needed lineage.

- [ ] Write failing tests for each registered detection rule, clean metadata,
  projection failure, scanner failure, redaction failure, indeterminate input,
  redaction ordering, digest-only output, and candidate ineligibility.
- [ ] Run `uv run --no-sync python -m unittest tests.deterministic_patch_artifact_security.test_policy -v`; expect failures before policy code exists.
- [ ] Implement the accepted profile exactly, scanning only the allowlisted
  metadata projection and never retaining matched text or redacted metadata.
- [ ] Re-run the targeted command; expect all tests to pass.
- [ ] Plan one focused commit: `feat(patch-security): add metadata scan and redaction facts`.

## Phase 3: Metadata-only Assembly Service

**Depends on:** Phases 1–2 and the M2 `PatchProposal` contract.

**Files:** Create `service.py`, update `__init__.py`, and create
`test_service.py`.

**Interfaces:** `build_patch_security_facts(proposal, repository_identity,
base_revision)` validates immutable upstream lineage, builds `PatchIntent` and
metadata-only `PatchArtifact`, invokes the Phase 2 policy functions, and
returns a complete success/failure envelope without any filesystem, subprocess,
OCI, network, GitHub, or artifact-store dependency.

- [ ] Write failing tests using controlled M2 PatchProposal objects for clean,
  blocked, failed, indeterminate, forbidden-payload, and mismatched-lineage
  inputs.
- [ ] Run `uv run --no-sync python -m unittest tests.deterministic_patch_artifact_security.test_service -v`; expect failures before service assembly exists.
- [ ] Implement only service orchestration and bounded validation-error mapping;
  do not add a renderer, source reader, workspace abstraction, or PDR evaluator.
- [ ] Re-run the targeted command; expect all tests to pass.
- [ ] Plan one focused commit: `feat(patch-security): assemble metadata security facts`.

## Phase 4: Acceptance and Boundary Hardening

**Depends on:** Phases 1–3.

**Files:** Create `test_acceptance.py`; modify only package exports and
OpenSpec fixture/contract documents if tests reveal an accepted-contract gap.

**Interfaces:** Acceptance invokes the public service only and asserts immutable
lineage, no candidate on every unsafe path, no persisted payload, and no
side-effect surface.

- [ ] Write failing acceptance tests for metadata-only PatchArtifact behavior,
  all fail-closed scanner/redaction terminals, no raw payload in contracts or
  errors, no candidate except passed/not-needed, and zero external effects.
- [ ] Run `uv run --no-sync python -m unittest tests.deterministic_patch_artifact_security.test_acceptance -v`; expect failures before hardening is complete.
- [ ] Implement the smallest phase-scoped corrections required by acceptance;
  do not broaden Feature 2 authority.
- [ ] Run `uv run --no-sync python -m unittest discover -s tests -v`, `openspec validate deterministic-patch-artifact-security --strict`, and `git diff --check`; expect success.
- [ ] Plan one focused commit: `test(patch-security): harden metadata artifact acceptance`.

## Self-Review

- Spec coverage: Phases 1–3 cover metadata contracts, identity, profile-owned
  security facts, and candidate boundaries; Phase 4 covers every normative
  fail-closed and no-side-effect scenario.
- Scope: no phase creates a diff, reads source, executes a command, mutates a
  workspace, publishes an artifact, creates a summary, or contacts GitHub.
- Consistency: the same contract names, scan results, redaction statuses, and
  `build_patch_security_facts` boundary are used throughout.
