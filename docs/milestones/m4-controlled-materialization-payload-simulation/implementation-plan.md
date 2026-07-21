# Controlled Materialization and Payload Simulation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local-only bridge from a registered snapshot to a deterministic ephemeral commit-payload identity and fake simulation, without real mutation authority.

**Architecture:** A new `forgeflow.controlled_materialization_payload_simulation` package owns immutable contracts, canonical identities, closed registries, and a narrowly scoped local-Docker seam. The harness owns every transient byte and handle; durable contracts retain only safe identities, digests, facts, and scoped PDRs. Tests inject fakes, while the sole concrete local backend is limited to the registered Docker command shape.

**Tech Stack:** Python 3.12 standard library, frozen/slots dataclasses, canonical UTF-8 JSON/SHA-256, unittest, injected fake Docker/Git-data protocols.

## Global Constraints

- Reuse `forgeflow.governed_action_sandbox.profile.M4_FIXTURE_V1` only by profile ID/version; do not duplicate or reinterpret its command, image, environment, network, timeout, or limits.
- Source is only harness-injected `(repository_id, base_sha, snapshot_digest)`; reject every caller path, directory, URL, checkout, ref, and fallback.
- A manifest contains only transformation ID/version, target-file ID, expected-input digest; no content, diff, template, replacement text, executable script, or dynamic language.
- Payload bytes and `EphemeralPayloadHandle` are private, non-serializable, one-attempt values; never persist them in contracts, stores, logs, terminals, or `DurableRunSummary`.
- Authority kinds are exactly `materialization`, `payload_eligibility`, and future-only `real_mutation`; PDRs are fresh, exact-bound, and non-elevatable.
- Docker is local-only: read-only snapshot, fixed profile image, network-disabled, empty environment, credential-free, bounded, and unable to clone/fetch/write externally. Its only process invocation is isolated to `sandbox.py`; tests use fakes.
- Fake IDs begin `forgeflow-sim-`; they are not Git/GitHub IDs and never enter Feature 4 or provider-facing schema/import surfaces.
- Automatic retries are zero. Manual retry creates new attempt, fresh scope-matched PDRs, and a new handle.

## File Structure

| Path | Responsibility |
| --- | --- |
| `src/forgeflow/controlled_materialization_payload_simulation/models.py` | immutable contracts, terminals, PDR scope validation |
| `src/forgeflow/controlled_materialization_payload_simulation/canonical.py` | canonical JSON, digests, self-excluding IDs |
| `src/forgeflow/controlled_materialization_payload_simulation/registry.py` | fixed snapshot/target/transformer registrations |
| `src/forgeflow/controlled_materialization_payload_simulation/policy.py` | PDR construction and exact lineage checks |
| `src/forgeflow/controlled_materialization_payload_simulation/sandbox.py` | local Docker command builder/backend plus injected facts protocol |
| `src/forgeflow/controlled_materialization_payload_simulation/service.py` | revalidation, assembly, scanning, validation, cleanup |
| `src/forgeflow/controlled_materialization_payload_simulation/fake_adapter.py` | deterministic fake simulation and real-input rejection |
| `tests/controlled_materialization_payload_simulation/test_contracts.py` | contract/forgery/fixed-point/immutability tests |
| `tests/controlled_materialization_payload_simulation/test_registry_service.py` | source/transformer/PDR/sandbox/cleanup tests |
| `tests/controlled_materialization_payload_simulation/test_fake_adapter.py` | simulation/binding/idempotency tests |
| `tests/controlled_materialization_payload_simulation/test_acceptance.py` | zero-effect and forbidden-surface matrix |

---

### Task 1: Phase 1 — contracts, canonical identity, and terminals

**Files:** Create package `__init__.py`, `models.py`, `canonical.py`, test package and `test_contracts.py`, plus `docs/milestones/m4-controlled-materialization-payload-simulation/progress.md`.

**Interfaces:** Produce `TransformationManifest`, `MaterializationPDR`, `MaterializedCommitPayload`, `PayloadEligibilityPDR`, `MaterializationTerminal`, `EphemeralPayloadHandle`, `canonical_bytes`, `sha256_hex`, and per-type `*_id_for` helpers. No source byte/path, Docker, credential, provider, or Feature 4 type is allowed.

- [ ] **Step 1: Write failing tests**

```python
def test_payload_identity_is_self_excluding_and_has_no_bytes_or_path():
    payload = MaterializedCommitPayload.create(
        repository_id=REGISTERED_REPOSITORY_ID, base_sha=REGISTERED_BASE_SHA,
        target_file_id="fixture-test-file-v1", input_digest=DIGEST_A,
        output_digest=DIGEST_B, materialization_pdr_id=PDR_A,
        security_fact_ids=(FACT_A,), validation_fact_id=FACT_B, review_fact_ids=(),
    )
    self.assertEqual(payload.payload_id, materialized_payload_id_for(payload))
    self.assertNotIn("path", payload.__dataclass_fields__)
    self.assertNotIn("content", payload.__dataclass_fields__)
```

Cover lists, duplicate/unsorted fields, invalid/expired PDR, wrong authority kind, v1 `real_mutation`, forged ID, source-like text, path/handle/bytes, and prohibited terminal fields.

- [ ] **Step 2: Run RED**

Run: `PYTHONPATH=src uv run --no-sync python -m unittest tests.controlled_materialization_payload_simulation.test_contracts -v`

Expected: import failure because the package does not exist.

- [ ] **Step 3: Implement minimal contracts**

```python
@dataclass(frozen=True, slots=True)
class MaterializationPDR:
    authority_kind: Literal["materialization"]
    attempt_id: str
    issued_at: int
    expires_at: int
    repository_id: str
    base_sha: str
    snapshot_digest: str
    transformation_id: str
    transformation_version: str
    target_file_id: str
    expected_input_digest: str
    profile_id: str
    profile_version: str
```

Use canonical SHA-256 identities, strict digest/tuple/enum validation, and identity helpers that omit only their own identity fields. A handle uses a private object token and raises `TypeError` if serialization is attempted.

- [ ] **Step 4: Verify and commit**

Run: `PYTHONPATH=src uv run --no-sync python -m unittest tests.controlled_materialization_payload_simulation.test_contracts -v && ! rg -n '(^|[[:space:]])(subprocess|socket|requests|urllib|httpx|os\\.system|pathlib\\.Path|github)' src/forgeflow/controlled_materialization_payload_simulation/models.py src/forgeflow/controlled_materialization_payload_simulation/canonical.py && git diff --check`

After independent PASS, record safe Phase 1 evidence and commit `feat(materialization): add scoped payload contracts`.

### Task 2: Phase 2 — closed source registry, transformer, and materialization PDR

**Files:** Create `registry.py`, `policy.py`, `test_registry_service.py`; modify package exports and phase progress.

**Interfaces:** Consume Phase 1 and `M4_FIXTURE_V1`; produce internal `RegisteredSourceSnapshot`, `resolve_target_file(target_file_id)`, `resolve_transformer(manifest)`, `revalidate_snapshot(snapshot, injected_bytes)`, and `issue_materialization_pdr(manifest, snapshot, now)`.

- [ ] **Step 1: Write failing registry tests**

```python
def test_snapshot_mismatch_and_caller_source_selector_fail_closed():
    result = revalidate_snapshot(registered_snapshot(), {"fixture_test.py": b"wrong"})
    self.assertEqual(result.terminal.reason, "source_revalidation_failed")
    with self.assertRaises(TypeError):
        TransformationManifest("transform-v1", "1", "fixture-test-file-v1", DIGEST_A, "/tmp/source")
```

Cover unknown repository/base/snapshot/target/transformer, input digest mismatch, denied/expired PDR, wrong profile, and deterministic replay.

- [ ] **Step 2: Run RED**

Run: `PYTHONPATH=src uv run --no-sync python -m unittest tests.controlled_materialization_payload_simulation.test_registry_service -v`

Expected: missing registry/policy interfaces fail.

- [ ] **Step 3: Implement closed registrations**

```python
def issue_materialization_pdr(manifest, snapshot, now):
    require_revalidated(snapshot, manifest)
    return MaterializationPDR.create(
        attempt_id=new_attempt_id(manifest, snapshot, now), issued_at=now, expires_at=now + 1,
        repository_id=snapshot.repository_id, base_sha=snapshot.base_sha,
        snapshot_digest=snapshot.snapshot_digest, transformation_id=manifest.transformation_id,
        transformation_version=manifest.transformation_version, target_file_id=manifest.target_file_id,
        expected_input_digest=manifest.expected_input_digest,
        profile_id=M4_FIXTURE_V1.policy_profile_id, profile_version=M4_FIXTURE_V1.policy_profile_version,
    )
```

The registered transformer receives only registry-resolved target bytes and returns one bytes value. It accepts no request-provided function, script, template, or path.

- [ ] **Step 4: Verify and commit**

Run: `PYTHONPATH=src uv run --no-sync python -m unittest tests.controlled_materialization_payload_simulation.test_contracts tests.controlled_materialization_payload_simulation.test_registry_service -v && ! rg -n '(clone|fetch|git |https?://|Path\\(|cwd|workdir)' src/forgeflow/controlled_materialization_payload_simulation && git diff --check`

After independent PASS proving registry-only authority, record Phase 2 and commit `feat(materialization): add registered snapshot transformer`.

### Task 3: Phase 3 — injected Docker materialization, facts, and cleanup

**Files:** Create `sandbox.py` and `service.py`; modify `test_registry_service.py` and phase progress.

**Interfaces:** Consume a revalidated snapshot, registered transformer, fresh allowed materialization PDR, and `LocalDockerBackend`. Produce `MaterializedCommitPayload | MaterializationTerminal` with a private lease/handle. `DockerCliBackend` is the only concrete implementation; tests inject `FakeDocker`. Backend reports bounded structured facts; service recomputes digests and cleans up every terminal path.

- [ ] **Step 1: Write failing execution tests**

```python
def test_unproven_sandbox_or_extra_file_fails_closed_and_clears_bytes():
    lease = EphemeralPayloadLease.for_test(b"changed")
    result = materialize(allowed_pdr(), registered_snapshot(), manifest(), FakeDocker(extra_files=("other.py",), lease=lease))
    self.assertEqual(result.terminal.reason, "materialization_failed")
    self.assertTrue(lease.destroyed)
    self.assertFalse(lease.handle.is_live)
```

Cover false network/credential/read-only/image/environment/resource proofs; digest mismatch; secret scan blocked/indeterminate without matched text; validation failure versus infrastructure failure; expiry; and exception cleanup.

- [ ] **Step 2: Run RED**

Run: `PYTHONPATH=src uv run --no-sync python -m unittest tests.controlled_materialization_payload_simulation.test_registry_service -v`

Expected: missing sandbox/service interfaces fail.

- [ ] **Step 3: Implement injected local seam**

```python
class LocalDockerBackend(Protocol):
    def prove(self, profile: M4FixtureProfile) -> DockerCapabilityProof: ...
    def materialize(self, snapshot, manifest) -> DockerMaterializationFacts: ...
    def validate(self, lease, profile: M4FixtureProfile) -> ValidationFacts: ...
```

Add the sole concrete backend with a list-form command (never a shell):

```python
command = (
    "docker", "run", "--rm", "--network", "none", "--read-only",
    "--env", "PATH=/usr/local/bin:/usr/bin:/bin", "--mount", readonly_snapshot_mount,
    "--tmpfs", "/forgeflow-output", M4_FIXTURE_V1.oci_image_digest,
    M4_FIXTURE_V1.executable, *M4_FIXTURE_V1.args,
)
```

`DockerCliBackend` derives image, command, timeout, and resource arguments exclusively from `M4_FIXTURE_V1`; it may return only bounded facts and temporary output to the harness. Missing Docker/image/profile proof becomes `validation_infrastructure_failed` or `materialization_failed`, never a fallback. `service.py` itself never invokes a shell, subprocess, network, or provider API and destroys the lease in `finally`.

- [ ] **Step 4: Verify and commit**

Run: `PYTHONPATH=src uv run --no-sync python -m unittest tests.controlled_materialization_payload_simulation.test_contracts tests.controlled_materialization_payload_simulation.test_registry_service -v && ! rg -n '(^|[[:space:]])(socket|requests|urllib|httpx|os\\.system|pathlib\\.Path|github|git )' src/forgeflow/controlled_materialization_payload_simulation && rg -n '^import subprocess$|^from subprocess import' src/forgeflow/controlled_materialization_payload_simulation/sandbox.py && ! rg -n 'subprocess' src/forgeflow/controlled_materialization_payload_simulation/models.py src/forgeflow/controlled_materialization_payload_simulation/registry.py src/forgeflow/controlled_materialization_payload_simulation/policy.py src/forgeflow/controlled_materialization_payload_simulation/service.py && git diff --check`

After independent PASS on cleanup, facts-only validation, scanner redaction, and profile reuse, record Phase 3 and commit `feat(materialization): add local governed payload assembly`.

### Task 4: Phase 4 — fake simulation, real-surface rejection, acceptance

**Files:** Create `fake_adapter.py`, `test_fake_adapter.py`, `test_acceptance.py`; modify exports and phase progress.

**Interfaces:** Consume a live handle, exact payload, fresh `PayloadEligibilityPDR`, and in-memory state. Produce `forgeflow-sim-blob-*`, tree, commit, ref IDs and `reject_real_mutation_input(value)`.

- [ ] **Step 1: Write failing adapter/acceptance tests**

```python
def test_replay_is_deterministic_and_real_surface_rejects_simulation_identity():
    first = FakeGitDataAdapter().simulate(live_handle(), payload(), eligible_pdr())
    replay = FakeGitDataAdapter().simulate(live_handle(), payload(), eligible_pdr())
    self.assertEqual(first, replay)
    self.assertTrue(first.commit_id.startswith("forgeflow-sim-commit-"))
    with self.assertRaises(ValueError): reject_real_mutation_input(first.commit_id)
```

Cover expired/forged handle; repository/base/digest/payload/PDR mismatch; materialization PDR as eligibility; stale PDR; idempotency; zero external effects; cleanup; forbidden provider imports; and no simulation ID in Feature 4 schemas.

- [ ] **Step 2: Run RED**

Run: `PYTHONPATH=src uv run --no-sync python -m unittest tests.controlled_materialization_payload_simulation.test_fake_adapter tests.controlled_materialization_payload_simulation.test_acceptance -v`

Expected: missing fake-adapter interfaces fail.

- [ ] **Step 3: Implement in-memory simulation only**

```python
def simulate(self, handle, payload, pdr):
    require_live_handle_and_exact_bindings(handle, payload, pdr)
    return FakeMutationResult.from_seed(canonical_bytes({"payload_id": payload.payload_id, "base_sha": payload.base_sha}))

def reject_real_mutation_input(value):
    if isinstance(value, (MaterializationPDR, PayloadEligibilityPDR)) or (isinstance(value, str) and value.startswith("forgeflow-sim-")):
        raise ValueError("v1 authority or simulation identity is not real-mutation input")
```

Keep state in memory, import no Feature 4 adapter/`gh`/GitHub/Git CLI/network client, and destroy the handle after every attempt.

- [ ] **Step 4: Verify and commit**

Run: `PYTHONPATH=src uv run --no-sync python -m unittest discover -s tests -v && ! rg -n '(^|[[:space:]])(socket|requests|urllib|httpx|os\\.system|pathlib\\.Path|github|gh |git )' src/forgeflow/controlled_materialization_payload_simulation && rg -n '^import subprocess$|^from subprocess import' src/forgeflow/controlled_materialization_payload_simulation/sandbox.py && ! rg -n 'subprocess' src/forgeflow/controlled_materialization_payload_simulation/models.py src/forgeflow/controlled_materialization_payload_simulation/registry.py src/forgeflow/controlled_materialization_payload_simulation/policy.py src/forgeflow/controlled_materialization_payload_simulation/service.py src/forgeflow/controlled_materialization_payload_simulation/fake_adapter.py && ! rg -n 'forgeflow-sim-' src/forgeflow/fixture_github_draft_pr_adapter && openspec validate controlled-materialization-payload-simulation --strict && git diff --check`

After independent PASS on zero effects, cleanup, and PDR non-elevation, record Phase 4, reconcile OpenSpec tasks without GitHub-E2E claims, and commit `feat(materialization): complete fake payload simulation`.

## Plan Self-Review

| Requirement | Tasks |
| --- | --- |
| closed source/transformer authority | 1, 2 |
| immutable identities and PDR non-elevation | 1, 2, 4 |
| ephemeral bytes and cleanup | 1, 3, 4 |
| Feature 1 profile, Docker, security, validation facts | 3 |
| controlled terminals and zero retry | 1, 3 |
| simulation identity/provider isolation | 4 |
| no GitHub/credential/remote write | 2, 3, 4 |

The plan schedules no real GitHub adapter, credential, external fixture, or mutation-scoped PDR implementation.
