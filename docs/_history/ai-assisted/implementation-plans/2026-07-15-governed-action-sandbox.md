# Governed Action and Sandbox Boundary Implementation Draft Plan

> **Non-canonical planning evidence.** Generated with Superpowers
> `writing-plans`; reconcile against the accepted `governed-action-sandbox`
> OpenSpec, RFC-002, RFC-004, RFC-005, RFC-006, ADR-011, and registered fixture
> documents before execution. This file never authorizes a phase.

> **For agentic workers:** Follow the reconciled ForgeFlow canonical plan and
> Lightweight Implementation Execution phase-by-phase. Do not treat this draft
> or a Superpowers workflow as execution authority.

**Goal:** Deliver the M4 fixture-only governed-action and OCI sandbox boundary:
immutable intent/policy/attempt contracts, one exact command capability, and a
fail-closed OCI execution seam with no GitHub side effect.

**Architecture:** A pure contract/policy layer creates `ActionIntent`, exact
`CommandIntent`, and fresh `PolicyDecisionRecord` values. A ForgeFlow-owned
service evaluates policy before asking an injected OCI adapter to prove the
registered capability and execute the sole command. The adapter returns bounded
facts only; the service turns them into immutable `ExecutionAttempt` contracts.

**Tech Stack:** Python 3.12 standard library (`dataclasses`, `hashlib`, `json`,
`subprocess`, `tempfile`, `unittest`); OCI-compatible Docker/Podman CLI only as
a controlled backend selected by the local harness, with no new dependency.

## Global Constraints

- Use only the registered `forgeflow-m4-fixture-only` profile version `1.0.0`,
  image digest `sha256:81b691e3b5d43b2f4e717eaeef63437705addd115aee32917efd5d7387807f28`,
  repository ID `1300511729`, and base SHA
  `97c8220cd713ebf61124ac2de2f3eadc6e4dc222`.
- The only command is `python3 -m unittest discover -s tests`, with empty
  environment, `workspace_root`, 120000 ms timeout, and 65536-byte output
  limit. Do not add shell wrappers or a general allowlist.
- The adapter must prove digest pinning, network disabled, credential absence,
  no dynamic installation, temporary fixed-revision workspace, workspace-only
  writes, and no artifact-store mount. Any missing proof is
  `sandbox_unavailable`; no host-process fallback exists.
- No PatchIntent/PatchArtifact, scan/redaction implementation, approval
  workflow, artifact store, DurableRunSummary, GitHub adapter/mutation,
  DeerFlow attachment, provider, retry, repair loop, or external credential.
- Output remains transient and discarded. Every attempt has `artifact_ref_ids:
  []`; raw output, source, environment, credentials, workspace paths, and
  runtime objects never enter a contract.
- `max_automatic_retries` is `0`. `cancelled` applies only after a real start
  and requires `cancelled_by_request`; it never becomes `command_failed`.
- A stale base revision yields `requires_human_approval` plus
  `not_started/base_revision_mismatch`, with no mutation or execution facts.
  A later approval requires fresh intent and decision lineage bound to the
  current revision.
- Each phase uses RED → GREEN → REFACTOR, targeted and cumulative `unittest`,
  strict OpenSpec validation, scope checks, one focused commit, an approved
  review when required, and a completion record/progress update only after the
  canonical plan exists.

## File Structure

| File | Responsibility |
| --- | --- |
| `src/forgeflow/governed_action_sandbox/models.py` | Frozen M4 contracts, bounded observations, and validation errors. |
| `src/forgeflow/governed_action_sandbox/canonical.py` | Canonical JSON and self-excluding SHA-256 identities. |
| `src/forgeflow/governed_action_sandbox/profile.py` | Immutable registered fixture policy constants. |
| `src/forgeflow/governed_action_sandbox/policy.py` | Pure fresh PolicyDecisionRecord evaluator. |
| `src/forgeflow/governed_action_sandbox/oci_adapter.py` | OCI backend protocol, capability proof, argv construction, and bounded result. |
| `src/forgeflow/governed_action_sandbox/service.py` | Intent-to-attempt orchestration with no mutation beyond the approved sandbox. |
| `src/forgeflow/governed_action_sandbox/__init__.py` | Deliberate public API exports only. |
| `tests/governed_action_sandbox/test_contracts.py` | Contract, identity, lineage, and payload-boundary tests. |
| `tests/governed_action_sandbox/test_policy.py` | Fresh-decision and exact-command policy tests. |
| `tests/governed_action_sandbox/test_oci_adapter.py` | Fake-backend capability, argv, limit, cancellation, and no-fallback tests. |
| `tests/governed_action_sandbox/test_service.py` | End-to-end in-process orchestration tests with controlled backend doubles. |
| `tests/governed_action_sandbox/test_acceptance.py` | Feature acceptance matrix and prohibited-surface tests. |
| `openspec/changes/governed-action-sandbox/fixtures/expected/phase-*/` | Computed public contract fragments; never raw command output. |

## Phase 1: Immutable Contracts, Profile, and Canonical Identity

**Depends on:** accepted OpenSpec, RFC-002, RFC-004, and approved fixture/image
registrations.

**Files:**

- Create: `src/forgeflow/governed_action_sandbox/__init__.py`
- Create: `src/forgeflow/governed_action_sandbox/models.py`
- Create: `src/forgeflow/governed_action_sandbox/canonical.py`
- Create: `src/forgeflow/governed_action_sandbox/profile.py`
- Create: `tests/governed_action_sandbox/__init__.py`
- Create: `tests/governed_action_sandbox/test_contracts.py`
- Create: `tests/governed_action_sandbox/test_canonical.py`
- Create: `openspec/changes/governed-action-sandbox/fixtures/expected/phase-1-contract/{action-intent.json,command-intent.json,policy-decision.json,execution-attempt.json,error.json}`

**Interfaces:**

```python
@dataclass(frozen=True, slots=True)
class ActionIntent:
    contract_id: str
    action_id: str
    run_id: str
    created_at: str
    task_input_contract_id: str
    repository_id: str
    base_commit_sha: str
    requested_command_id: str
    policy_profile_id: str
    policy_profile_version: str

@dataclass(frozen=True, slots=True)
class CommandIntent:
    contract_id: str
    run_id: str
    created_at: str
    action_intent_contract_id: str
    repository_id: str
    base_commit_sha: str
    command_id: str
    executable: str
    args: tuple[str, ...]
    working_directory: str
    allowed_environment: tuple[str, ...]
    oci_image_digest: str
    timeout_ms: int
    max_output_bytes: int
    policy_profile_id: str
    policy_profile_version: str

@dataclass(frozen=True, slots=True)
class PolicyDecisionRecord:
    contract_id: str
    decision_id: str
    run_id: str
    created_at: str
    subject_contract_id: str
    input_lineage_digest: str
    policy_profile_id: str
    policy_profile_version: str
    outcome: str
    reason_codes: tuple[str, ...]
    evidence_ref_ids: tuple[str, ...]
    evaluated_at: str

@dataclass(frozen=True, slots=True)
class ExecutionAttempt:
    contract_id: str
    attempt_id: str
    run_id: str
    created_at: str
    command_intent_contract_id: str
    policy_decision_contract_id: str
    status: str
    failure_reason: str | None
    resource_observations: ResourceObservations
    artifact_ref_ids: tuple[str, ...]
    oci_image_digest: str | None
    exit_code: int | None
    started_at: str | None
    finished_at: str | None

@dataclass(frozen=True, slots=True)
class ResourceObservations:
    wall_clock_ms: int
    sandbox_lifetime_ms: int
    command_output_bytes: int
    workspace_write_bytes: int
    artifact_bytes: int
    diff_bytes: int
    changed_files: int
    tool_call_count: int
    limits_reached: tuple[str, ...]
```

Exports: `action_intent_id_for(value: ActionIntent) -> str`,
`command_intent_id_for(value: CommandIntent) -> str`,
`policy_decision_id_for(value: PolicyDecisionRecord) -> str`, and
`execution_attempt_id_for(value: ExecutionAttempt) -> str`. Each calls the
canonical JSON/SHA-256 helper with the exact self-identity and audit-time field
exclusions specified by the OpenSpec contract design.

- [ ] **Step 1: Write failing contract tests.**

```python
def test_not_started_attempt_has_no_execution_facts() -> None:
    attempt = make_attempt(status="not_started", failure_reason="policy_blocked")
    self.assertIsNone(attempt.oci_image_digest)
    self.assertIsNone(attempt.exit_code)
    self.assertEqual(attempt.artifact_ref_ids, ())
```

- [ ] **Step 2: Run RED tests.**

Run: `uv run --no-sync python -m unittest tests.governed_action_sandbox.test_contracts tests.governed_action_sandbox.test_canonical -v`

Expected: FAIL because `forgeflow.governed_action_sandbox` does not exist.

- [ ] **Step 3: Implement frozen models and identity helpers.**

```python
def policy_decision_id_for(value: PolicyDecisionRecord) -> str:
    return _hash_id("pdr_sha256:", value, {"contract_id", "decision_id"})
```

Enforce exact profile literals, same-value PDR `contract_id`/`decision_id`,
canonical arrays, zero artifact references, observation bounds, forbidden raw
payload field names, and `cancelled` ↔ `cancelled_by_request` exclusivity.

- [ ] **Step 4: Run GREEN and fixture checks.**

Run: `uv run --no-sync python -m unittest tests.governed_action_sandbox.test_contracts tests.governed_action_sandbox.test_canonical -v`

Expected: PASS; canonical fixtures recompute their own IDs.

- [ ] **Step 5: Run cumulative verification and commit.**

Run: `uv run --no-sync python -m unittest discover -s tests -v && openspec validate governed-action-sandbox --strict && git diff --check`

Expected: PASS with no raw-payload or identity mismatch.

Commit: `feat(governed-action-sandbox): add immutable execution contracts`

**Acceptance:** all M4 contracts are frozen and self-identifying; no
`not_started` attempt can carry a started fact; `cancelled_by_request` cannot
describe a non-started attempt.

## Phase 2: Pure Policy Evaluation and Intent Assembly

**Depends on:** accepted Phase 1.

**Files:**

- Create: `src/forgeflow/governed_action_sandbox/policy.py`
- Modify: `src/forgeflow/governed_action_sandbox/__init__.py`
- Create: `tests/governed_action_sandbox/test_policy.py`
- Create: `openspec/changes/governed-action-sandbox/fixtures/expected/phase-2-policy/{allowed.json,blocked.json,approval-required.json,command-mismatch.json}`

**Interfaces:**

```python
build_action_intent(*, run_id: str, task_input_contract_id: str) -> ActionIntent
build_command_intent(action: ActionIntent) -> CommandIntent
evaluate_command_intent(intent: CommandIntent) -> PolicyDecisionRecord
```

- [ ] **Step 1: Write failing policy tests.**

```python
def test_extra_argument_is_policy_blocked() -> None:
    record = evaluate_command_intent(command_with(args=("-m", "unittest", "discover", "-s", "tests", "-v")))
    self.assertEqual(record.outcome, "blocked")
    self.assertIn("command_mismatch", record.reason_codes)

def test_stale_base_requires_human_approval_without_start() -> None:
    record = evaluate_command_intent(command_with(base_commit_sha="0" * 40))
    self.assertEqual(record.outcome, "requires_human_approval")
```

- [ ] **Step 2: Run RED tests.**

Run: `uv run --no-sync python -m unittest tests.governed_action_sandbox.test_policy -v`

Expected: FAIL because pure intent builders and evaluator do not exist.

- [ ] **Step 3: Implement the policy-only flow.**

```python
if intent.base_commit_sha != FIXTURE_BASE_COMMIT_SHA:
    return approval_record(intent, reason_code="base_revision_mismatch")
if intent.command_id != FIXTURE_COMMAND_ID or intent.oci_image_digest != OCI_IMAGE_DIGEST:
    return blocked_record(intent, reason_code="command_mismatch")
```

Construct a new PDR for every current input lineage. Do not read repository
configuration, environment, Issue content, credentials, or a runtime backend.

- [ ] **Step 4: Run GREEN and cumulative tests.**

Run: `uv run --no-sync python -m unittest tests.governed_action_sandbox.test_policy -v && uv run --no-sync python -m unittest discover -s tests -v`

Expected: PASS; only exact registered values become `allowed`.

- [ ] **Step 5: Verify scope and commit.**

Run: `! rg -n 'subprocess|socket|requests|urllib|httpx|os\.system' src/forgeflow/governed_action_sandbox/{models,canonical,profile,policy}.py && git diff --check`

Expected: PASS; Phase 2 remains pure.

Commit: `feat(governed-action-sandbox): add exact policy evaluation`

**Acceptance:** intent remains declarative; a PDR is the only authorization
source; command/repository/image mismatches stop before workspace/process
creation, while stale base revision is an approval-required, no-start fact.

## Phase 3: OCI Capability Proof and Controlled Attempt Service

**Depends on:** accepted Phases 1–2 and an explicitly assigned M4
branch/worktree; actual registry/image execution remains fixture-owner-only.

**Files:**

- Create: `src/forgeflow/governed_action_sandbox/oci_adapter.py`
- Create: `src/forgeflow/governed_action_sandbox/service.py`
- Modify: `src/forgeflow/governed_action_sandbox/__init__.py`
- Create: `tests/governed_action_sandbox/test_oci_adapter.py`
- Create: `tests/governed_action_sandbox/test_service.py`
- Create: `openspec/changes/governed-action-sandbox/fixtures/expected/phase-3-service/{blocked.json,approval-required.json,sandbox-unavailable.json,command-failed.json,cancelled.json,resource-limited.json}`

**Interfaces:**

```python
@dataclass(frozen=True, slots=True)
class OciRunFacts:
    status: str
    failure_reason: str | None
    oci_image_digest: str | None
    exit_code: int | None
    started_at: str | None
    finished_at: str | None
    resource_observations: ResourceObservations

execute_governed_attempt(
    action: ActionIntent, backend: OciBackend
) -> ExecutionAttempt | GovernedActionSandboxValidationError
```

`OciBackend` is a `typing.Protocol` exposing
`prove_and_run(command: CommandIntent) -> OciRunFacts`; only the controlled
local harness supplies a concrete backend, and all tests supply controlled
fakes.

- [ ] **Step 1: Write failing adapter/service tests with a controlled fake backend.**

```python
def test_backend_without_network_proof_is_not_started() -> None:
    attempt = execute_governed_attempt(allowed_action(), backend=BackendWithoutNetworkProof())
    self.assertEqual((attempt.status, attempt.failure_reason), ("not_started", "sandbox_unavailable"))
```

- [ ] **Step 2: Run RED tests.**

Run: `uv run --no-sync python -m unittest tests.governed_action_sandbox.test_oci_adapter tests.governed_action_sandbox.test_service -v`

Expected: FAIL because the adapter protocol and service do not exist.

- [ ] **Step 3: Implement the minimal fail-closed adapter seam.**

```python
if record.outcome != "allowed":
    return not_started_attempt(command, record)
facts = backend.prove_and_run(command)
return attempt_from_facts(command, record, facts)
```

The concrete local harness backend must construct an argument vector without a
shell; require `--network=none`, no credential/environment forwarding, a
temporary workspace mount, the digest-qualified image reference, and an
explicit cleanup path. If any proof/cleanup precondition is unavailable, return
`sandbox_unavailable` before launch. Capture output only up to the policy limit
and discard it after deriving facts.

- [ ] **Step 4: Run GREEN tests and controlled fixture check.**

Run: `uv run --no-sync python -m unittest tests.governed_action_sandbox.test_oci_adapter tests.governed_action_sandbox.test_service -v`

Expected: PASS using only fake backends. Run the registered Docker/Podman
fixture command only when the fixture owner explicitly authorizes that external
environment action and retains reset/audit evidence.

- [ ] **Step 5: Cumulative verification and commit.**

Run: `uv run --no-sync python -m unittest discover -s tests -v && openspec validate governed-action-sandbox --strict && git diff --check`

Expected: PASS; no host fallback or GitHub activity.

Commit: `feat(governed-action-sandbox): add fail-closed oci attempt service`

**Acceptance:** a backend cannot run without proving every OCI constraint;
blocked/approval paths create no workspace/process; cancellation records only
`cancelled_by_request` after an actual start.

## Phase 4: Acceptance Matrix and Boundary Hardening

**Depends on:** accepted Phases 1–3.

**Files:**

- Create: `tests/governed_action_sandbox/test_acceptance.py`
- Create: `openspec/changes/governed-action-sandbox/fixtures/expected/phase-4-acceptance/{attempt-fragments.json,error-fragments.json}`
- Modify: `src/forgeflow/governed_action_sandbox/{models.py,policy.py,oci_adapter.py,service.py}` only for acceptance failures.

**Interfaces:** use only `build_action_intent`, `build_command_intent`,
`evaluate_command_intent`, and `execute_governed_attempt`; introduce no public
API.

- [ ] **Step 1: Write failing acceptance tests.**

```python
def test_all_non_allowed_paths_have_zero_backend_launches() -> None:
    backend = CountingBackend()
    for action in (blocked_action(), approval_required_action(), stale_revision_action()):
        execute_governed_attempt(action, backend)
    self.assertEqual(backend.launch_count, 0)
```

- [ ] **Step 2: Run RED acceptance tests.**

Run: `uv run --no-sync python -m unittest tests.governed_action_sandbox.test_acceptance -v`

Expected: FAIL until every terminal, capability-proof, output-limit,
cancellation, canonical-ID, raw-payload, and prohibited-side-effect case is
covered.

- [ ] **Step 3: Make only scoped corrections.**

```python
FORBIDDEN_IMPORTS = ("socket", "requests", "urllib", "httpx", "os.system")
```

Keep the correction inside this feature; do not add artifact persistence,
approval, patch, GitHub, provider, DeerFlow, or retry code.

- [ ] **Step 4: Run final verification.**

Run: `uv run --no-sync python -m unittest tests.governed_action_sandbox.test_acceptance -v && uv run --no-sync python -m unittest discover -s tests -v && openspec validate governed-action-sandbox --strict && ! rg -n 'socket|requests|urllib|httpx|os\.system|shell=True' src/forgeflow/governed_action_sandbox && git diff --check && git status --short`

Expected: PASS; all fault/denial paths use controlled fakes and cause zero
external mutation.

- [ ] **Step 5: Commit and record the phase.**

Commit: `test(governed-action-sandbox): add acceptance coverage`

Create the canonical Phase 4 completion record and update M4 progress only
after the canonical plan creates those lifecycle documents.

**Acceptance:** every OpenSpec scenario is deterministic and test-covered;
only separately authorized fixture-owner evaluation may run the registered OCI
image; the codebase exposes no arbitrary execution surface.

## Self-Review

- **Spec coverage:** Phase 1 implements immutable contracts and IDs; Phase 2
  covers exact policy authority; Phase 3 covers OCI proof and attempt lifecycle;
  Phase 4 covers all acceptance terminals, cancellation, zero retry, and
  prohibited surfaces. Patch, scan/redaction, approval, durable-state, GitHub,
  provider, and DeerFlow work remain excluded.
- **Placeholder scan:** no TBD/TODO or unspecified error-handling task remains;
  every phase names files, interfaces, RED/GREEN commands, and an acceptance
  condition.
- **Type consistency:** Phase 1 defines all contract types; Phase 2 consumes
  intents/PDRs; Phase 3 consumes those types through `OciBackend`; Phase 4 uses
  only the exported Phase 2/3 functions.
