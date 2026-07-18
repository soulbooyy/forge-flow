# Milestone 4: Deterministic Patch Artifact and Security Scanning Canonical Implementation Plan

## Authority and Status

This Draft becomes the sole execution authority for this Feature 2 milestone
only after explicit user acceptance. It reconciles the [AI-assisted draft](../../_history/ai-assisted/implementation-plans/2026-07-16-deterministic-patch-artifact-security.md)
against the accepted Feature 2 OpenSpec, RFC-002/004/005 scoped amendments,
RFC-006, ADR-011, M4 Fixture Environment Registration, and M4 Patch Metadata
Security Profile. Chat prompts do not redefine phase scope, files, interfaces,
or acceptance.

## Terminal-first Amendment (Pending User Acceptance)

This amendment supersedes the execution order and interfaces below because the
previous plan allowed a raw rationale-bearing PatchIntent to exist before
security scanning. Under the accepted architecture decision, raw rationale and
matched text must never enter any contract. The historical Phase 1–3 completion
records remain factual records of prior work, but are not conformant evidence
for the amended contract and do not authorize further implementation.

After the amended RFC/OpenSpec/profile and this plan are accepted, implementation
must restart with fresh phase authorization in this order:

1. **Pre-scan contracts and terminal identity** — replace the pre-scan
   PatchIntent/Artifact lineage with `PreScanPatchMetadataIdentity`, revised
   scan/redaction references, `PatchSecurityTerminal`, controlled terminal
   reasons, and canonical identities.
2. **Transient metadata security facts** — scan/redact only a bounded transient
   projection anchored by the pre-scan identity; ensure unsafe facts return a
   terminal with no raw metadata, intent, artifact, or candidate.
3. **Passed-path assembly** — validate M2/fixture lineage; create PatchIntent,
   PatchArtifact, and candidate only after passed/not-needed facts.
4. **Acceptance and boundary hardening** — verify every OpenSpec scenario,
   terminal secrecy, no side-effect surface, and no authority escape.

Each re-baselined phase requires RED → GREEN → cumulative verification, a
focused commit, and the mandatory independent-review gate. No historical Phase
4 implementation may resume until this amendment is accepted and the relevant
re-baselined phase is explicitly authorized.

## Goal

Deliver deterministic, immutable, metadata-only patch/security facts from M2
PatchProposal lineage, with no source/diff/patch material, side effect,
persistence, or authorization capability.

## Reconciliation of AI Draft

- The AI draft's four phases are retained because each produces an independently
  testable contract boundary and one focused commit.
- The accepted metadata security profile, not a new implementation-defined
  rule set, controls every scan/redaction rule, status, and candidate condition.
- The plan removes all diff-rendering and transient raw-patch work. Feature 2
  constructs metadata only; later source-access/materialization authority is
  explicitly out of scope.
- All phases use RED → GREEN → scoped refactor → cumulative verification;
  phase acceptance additionally requires no new side-effect surface.

## Global Constraints

- Python 3.12 standard library and `unittest` only; add no dependencies.
- Never read, generate, persist, or expose raw source, raw diff, patch material,
  credential, environment value, command output, or temporary workspace path.
- Never invoke OCI, subprocesses, network, GitHub, artifact-store publication,
  approval, PDR evaluation, validation/review, retry, or workspace mutation.
- Treat `PatchProposal`, `PatchIntent`, `PatchArtifact`, security facts, and
  candidates as non-authorizing; only a later fresh PDR can authorize a later
  action.
- Before any phase is accepted, apply the Implementation Execution review gate:
  record whether independent review is required, whether it completed, whether
  a subagent was used, and the approved rationale. Phase 1 changes contracts,
  security boundary, and canonical identity, so independent review is required.
- Before Phase 1, create and record exactly branch
  `feature/m4-deterministic-patch-artifact-security` and worktree
  `.worktrees/m4-deterministic-patch-artifact-security`; do not reuse Feature 1.

## Phase 1: Immutable Contract and Canonical Identity

**Depends on:** Accepted OpenSpec/profile and assigned implementation environment.

**Files:**

- Create `src/forgeflow/deterministic_patch_artifact_security/{__init__,models,canonical}.py` — frozen contracts and deterministic IDs.
- Create `tests/deterministic_patch_artifact_security/{__init__,test_contracts,test_canonical}.py` — contract and canonicalization verification.

**Interfaces:** `PatchIntent`, `PatchArtifact`, `SecretScanResult`,
`RedactionFact`, `RedactedArtifactReferenceCandidate`, validation error envelope,
and digest helpers named in the AI draft.

- [ ] Write targeted failing contract/canonical tests and record RED results.
- [ ] Implement the minimum frozen models and canonical SHA-256 identity helpers; run targeted GREEN tests.
- [ ] Refactor only inside Phase 1; run the cumulative implemented suite.
- [ ] Run `git diff --check` and inspect `git status --short`.
- [ ] Create one focused commit, Phase 1 Completion Record, and progress update.

**Acceptance:** Contracts are payload-free, identity-stable, metadata-only, and
reject forbidden raw data without copying it; an approved independent review
must also complete before Phase 1 is accepted.

## Phase 2: Registered Metadata Security Facts

**Depends on:** Phase 1.

**Files:**

- Create `src/forgeflow/deterministic_patch_artifact_security/{profile,policy}.py` — accepted profile representation and pure scan/redaction functions.
- Create `tests/deterministic_patch_artifact_security/test_policy.py` — rule, status, redaction, and candidate tests.

**Interfaces:** `M4_PATCH_METADATA_SECURITY_V1`, `scan_metadata`,
`redact_metadata`, and `candidate_for` as defined in the AI draft.

- [ ] Write targeted failing tests for all registered rules and each scan/redaction terminal.
- [ ] Implement only profile-owned, metadata-only scanning/redaction; run targeted GREEN tests.
- [ ] Refactor only inside Phase 2; run the cumulative implemented suite.
- [ ] Run `git diff --check` and inspect `git status --short`.
- [ ] Create one focused commit, Phase 2 Completion Record, and progress update.

**Acceptance:** Only allowlisted metadata is processed; matched text is never
retained; unsafe results have no candidate and cannot become approval-required;
the required review-gate decision and any required independent review are
recorded before Phase 2 is accepted.

## Phase 3: Metadata-only Assembly Service

**Depends on:** Phases 1–2 and M2 PatchProposal contract availability.

**Files:**

- Create `src/forgeflow/deterministic_patch_artifact_security/service.py` — immutable upstream-lineage validation and envelope assembly.
- Modify `src/forgeflow/deterministic_patch_artifact_security/__init__.py` — deliberate public service export.
- Create `tests/deterministic_patch_artifact_security/test_service.py` — controlled M2 input and terminal assembly tests.

**Interfaces:** `build_patch_security_facts(proposal, repository_identity,
base_revision)` returns only Feature 2 success/failure contracts and in-memory
eligibility facts; it has no adapter parameter or side-effect dependency.

- [ ] Write targeted failing service tests for clean, blocked, failed, indeterminate, and lineage-invalid inputs.
- [ ] Implement the smallest assembly path; run targeted GREEN tests.
- [ ] Refactor only inside Phase 3; run the cumulative implemented suite.
- [ ] Run `git diff --check` and inspect `git status --short`.
- [ ] Create one focused commit, Phase 3 Completion Record, and progress update.

**Acceptance:** The service has no source/diff renderer, workspace/OCI/GitHub
integration, persistence path, or PDR evaluator; the required review-gate
decision and any required independent review are recorded before Phase 3 is
accepted.

## Phase 4: Acceptance and Boundary Hardening

**Depends on:** Phases 1–3.

**Files:**

- Create `tests/deterministic_patch_artifact_security/test_acceptance.py` — end-to-end contract and prohibited-capability checks.
- Modify only phase-scoped package/docs files if acceptance exposes a contract mismatch.

**Interfaces:** Public service and immutable contracts from Phases 1–3 only.

- [ ] Write targeted failing acceptance tests for every OpenSpec requirement and prohibited side effect.
- [ ] Implement only minimal corrections in accepted scope; run targeted GREEN tests.
- [ ] Refactor only inside Phase 4; run `uv run --no-sync python -m unittest discover -s tests -v`, `openspec validate deterministic-patch-artifact-security --strict`, `git diff --check`, and `git status --short`.
- [ ] Create one focused commit, Phase 4 Completion Record, and progress update.

**Acceptance:** All Feature 2 requirements pass with no raw material,
side-effect, persistence, or authorization escape; the required review-gate
decision and any required independent review are recorded before Phase 4 is
accepted.
