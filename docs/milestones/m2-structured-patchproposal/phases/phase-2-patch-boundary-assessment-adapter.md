# Phase 2: Patch-Boundary Assessment Adapter

## 1. Goal

Implement the pure, deterministic M2 patch-boundary evaluator that applies the
frozen conservative policy profile to ordered declarative candidate changes.
It returns a policy decision reference for allowed or approval-required intent,
and returns no successful reference for a blocked path.

## 2. Scope

### Included

- The public `assess_boundary(changes, profile)` interface and
  `PolicyBlockedError` result for blocked path policy.
- Profile-driven blocked and approval-required path classification, candidate
  bounds, deterministic risk flags, candidate digest, and policy-decision ID.
- Expected fragments for allowed, blocked, and approval-required outcomes.
- Focused policy tests, including exact case-insensitive auth segments,
  deletion escalation, profile identity, and stale-decision invalidation.

### Excluded

- Validation-envelope assembly, repository-context evidence validation,
  fixture-source lookup, or proposal service orchestration.
- Workspace, filesystem, network, command, provider, MCP, DeerFlow, Git, PR,
  memory, diff, or mutation behavior.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `src/forgeflow/patch_proposal/policy.py` | Added | Provide the pure, profile-driven boundary evaluator and blocked result. |
| `src/forgeflow/patch_proposal/__init__.py` | Modified | Export the Phase 2 public policy interface. |
| `tests/patch_proposal/test_policy.py` | Added | Verify all policy outcomes, precedence, bounds, IDs, and profile-driven behavior. |
| `openspec/changes/structured-patch-proposal/fixtures/expected/phase-2-policy/allowed.json` | Added | Lock deterministic allowed policy output. |
| `openspec/changes/structured-patch-proposal/fixtures/expected/phase-2-policy/blocked.json` | Added | Lock the safe blocked-policy fragment. |
| `openspec/changes/structured-patch-proposal/fixtures/expected/phase-2-policy/requires-human-approval.json` | Added | Lock deterministic approval-required policy output. |

## 4. Implementation

`assess_boundary()` first accepts only the frozen
`patch-proposal/m2-conservative-v1` profile and a non-empty candidate tuple
within its bound. It hashes the ordered candidate intent, applies blocked rules
first, then derives environment, high-risk, and deletion risk flags from the
profile. A blocked result raises `PolicyBlockedError` with only policy identity
and candidate digest; it carries no path or successful policy reference.

Allowed and approval-required outcomes construct a `PolicyDecisionRef` and
calculate its self-excluding deterministic decision ID. The evaluator has no
I/O or provider dependency.

## 5. Design Decisions

- Blocked path rules take precedence over deletion and approval-required rules.
- Auth matching NFC-normalizes and case-folds each complete path segment; a
  filename such as `authorizer.py` does not match `auth`.
- The profile's `approval_required_for_remove_file` setting controls deletion
  escalation, preventing an accepted profile rule from becoming inert.
- Phase 2 exposes a safe blocked result rather than a validation envelope;
  Phase 3 owns terminal-envelope assembly.

## 6. TDD and Tests

- RED: `uv run --no-sync python -m unittest tests.patch_proposal.test_policy -v`
  failed because `assess_boundary` did not yet exist.
- GREEN: after the pure evaluator was added, policy behavior passed and the
  fixture-lock test then exposed the intentionally absent expected fragments.
- Refactor/correction: generated real canonical fragments; independent review
  found that deletion escalation did not read its profile flag. Added a RED
  regression test, then made the evaluator use that flag.
- Targeted verification: `uv run --no-sync python -m unittest
  tests.patch_proposal.test_policy -v` passed 10/10.
- Cumulative verification: `uv run --no-sync python -m unittest discover -s
  tests -v` passed 84/84; `openspec validate structured-patch-proposal --strict`
  and `git diff --check` passed.

## 7. Important Fixes and Edge Cases

- Blocked secret-like paths cannot produce `PolicyDecisionRef` objects.
- Environment files, exact auth segments, CI/CD, infrastructure, migrations,
  lockfiles, and deletion escalate only to declarative human approval.
- A changed candidate rationale changes both candidate digest and policy
  decision identity, preventing stale policy reuse.
- Candidate bounds and profile drift are rejected before a policy decision is
  produced.

## 8. Commit

- Full commit hash: `6f1f6e39fe1645c5bf552836fffb6e386666c17e`
- Commit message: `feat(patch-proposal): add boundary assessment`

## 9. Acceptance

The evaluator produces deterministic allowed and approval-required policy
references, blocks secret-like paths before success assembly, derives sorted
risk flags from the fixed profile, and changes its decision identity when
candidate intent changes. All Phase 2 policy tests and the cumulative suite
passed.

Status: **Accepted**.

## 10. Scope Boundary Confirmation

This phase added no fixture source, repository-context adapter, proposal
service, validation-envelope assembly, workspace access, provider/MCP/DeerFlow
integration, diff, command, network, mutation, Git/PR, or memory behavior.

## 11. Follow-up

Next Phase: Deterministic Fixture Proposal-Source Adapter. It requires explicit
user authorization before starting.
