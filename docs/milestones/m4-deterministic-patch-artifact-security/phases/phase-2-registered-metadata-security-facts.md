# Phase 2: Registered Metadata Security Facts

## 1. Goal

Implement the accepted, versioned metadata-security profile and pure,
deterministic scan/redaction facts without source access, patch material, or
external side effects.

## 2. Scope

### Included

- Immutable representation of the accepted M4 Patch Metadata Security Profile,
  including its field allowlist, rule order, and deterministic rule patterns.
- Metadata-only secret-scan and redaction facts, including fail-closed terminal
  outcomes and ordered, payload-free findings.
- In-memory candidate eligibility guarded by canonical identity and complete
  intent/artifact/scan/redaction lineage recomputation.
- Regression tests for all registered rules, profile mismatch, failed and
  indeterminate outcomes, forged lineage, standard PEM markers, and overlapping
  redaction matches.
- RFC-002 and Feature 2 contract alignment for the consumed scan binding in
  `RedactionFact`.

### Excluded

- Patch/diff/source generation, source access, workspace mutation, command or
  OCI execution, GitHub, commit, branch, PR, approval/PDR evaluation, retry,
  artifact-store persistence, DurableRunSummary, validation/review, network,
  credentials, and environment access.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `src/forgeflow/deterministic_patch_artifact_security/profile.py` | Added | Represent the accepted profile as immutable data and own detection rules. |
| `src/forgeflow/deterministic_patch_artifact_security/policy.py` | Added | Produce pure scan/redaction facts and guarded candidates. |
| `src/forgeflow/deterministic_patch_artifact_security/models.py` | Modified | Bind redaction to its consumed scan and derive finding validation from the profile. |
| `tests/deterministic_patch_artifact_security/test_policy.py` | Added | Exercise profile rules, terminals, lineage, and redaction ordering. |
| `tests/deterministic_patch_artifact_security/test_contracts.py` | Modified | Cover scan-bound redaction and UTF-8-safe metadata validation. |
| `openspec/changes/deterministic-patch-artifact-security/contracts/m4-deterministic-patch-artifact-security-contract.md` | Modified | State `RedactionFact.secret_scan_id`. |
| `rfcs/RFC-002-contracts-and-state-model.md` | Modified | Align scoped M4 contract amendment with scan-bound redaction lineage. |

## 4. Implementation

The accepted profile is the single source of metadata field allowlisting, rule
ordering, and rule patterns. The scanner projects only the registered fields
and emits only `(rule_id, field_name)` facts. The redactor handles replacements
over the original metadata projection, selecting non-overlapping spans in
profile order; it exposes only a digest. A candidate is created only after the
implementation recomputes and exactly matches the canonical intent, artifact,
scan, and redaction facts. All blocked, failed, or indeterminate paths have no
candidate.

## 5. Design Decisions

- An unregistered/mismatched profile yields an `indeterminate` fact using the
  accepted profile identity; unregistered profile values are never copied into
  a security fact.
- `RedactionFact.secret_scan_id` cryptographically binds redaction to its exact
  scan fact, while `candidate_for` recomputes the entire metadata-only chain.
- UTF-8-invalid surrogate/control metadata is rejected before canonical
  serialization, preventing a permissive or exception-based scan path.
- The profile's earlier matching rule wins any overlap; no later substitution
  runs against already-redacted text.

## 6. TDD and Tests

- RED: the initial policy test failed because `policy.py` did not exist.
- GREEN: the initial profile/scan/redaction/candidate implementation passed its
  targeted test suite.
- Refactor/correction: independent review drove regressions for profile-owned
  rule data, intent/artifact alignment, exact scan/redaction binding,
  UTF-8-safe metadata, canonical upstream identities, documented PEM grammar,
  and overlap-safe redaction.
- Cumulative verification: `PYTHONPATH=src uv run --no-sync python -m unittest
  discover -s tests -v` passed 144 tests; `openspec validate
  deterministic-patch-artifact-security --strict` and `git diff --check`
  passed.
- Static boundary verification found no subprocess, network, filesystem-path,
  or external-I/O imports in the Phase 2 package.

## 7. Important Fixes and Edge Cases

- Every registered secret-like rule blocks and exposes no matched text.
- Scanner failure, redaction failure, `indeterminate`, and blocked findings
  never yield a candidate.
- Unrelated or noncanonical intent/artifact facts fail closed before scanning.
- Self-consistent forged scan/redaction facts cannot produce a candidate because
  the candidate path recomputes expected facts from the validated metadata.
- Standard and multi-space PEM markers are blocked according to the accepted
  profile grammar.

## 8. Commit

- Initial implementation: `27a2685` — `feat(patch-security): add metadata security facts`
- Review corrections: `6281867`, `fe476fb`, `0d1ac55`, `6f7bbab`, and `2f54dd2`.

## 9. Acceptance

Targeted policy tests passed 11/11. The cumulative suite passed 144 tests.
Strict OpenSpec validation, diff hygiene, and the static no-I/O boundary check
passed. The required independent review completed after corrective rounds and
approved the final overlap-safe redaction implementation with no remaining
P1/P2 findings.

Status: **Accepted after independent review**.

## 10. Review Gate

- Independent review required: Yes — Phase 2 introduces security-rule handling,
  security facts, and candidate eligibility.
- Independent review completed: Yes — independent read-only review completed
  multiple corrective rounds and approved the final state with no P1/P2.
- Subagent used: Yes.
- Review-method rationale and user-approval scope: The user explicitly approved
  independent subagent reviews through the end of Phase 2. They were necessary
  because self-review and test evidence cannot independently establish the
  profile-as-sole-rule-source, fail-closed, and lineage-security properties.

## 11. Scope Boundary Confirmation

Phase 2 created no raw source/diff/patch material, source reader, renderer,
workspace operation, command, OCI call, artifact-store object, durable
reference, PDR, approval, GitHub action, validation/review action, retry,
network request, credential access, or environment access. The candidate is an
in-memory, non-authorizing eligibility fact only.

## 12. Follow-up

Next Phase: Metadata-only Assembly Service. It remains unstarted and requires
explicit Phase 3 implementation authorization.
