# Re-baselined Phase 3: Passed-Path Assembly

## Goal

Create Feature 2's passed-path metadata facts only after terminal-first scan
and redaction processing proves eligibility.

## Delivered

- `build_patch_security_facts` validates immutable M2 proposal lineage and the
  registered fixture repository/base revision.
- The passed path emits `PatchIntent`, `PatchArtifact`, and
  `RedactedArtifactReferenceCandidate` only after a passed scan and
  not-needed redaction fact.
- Blocked, failed, indeterminate, malformed, or mismatched-lineage inputs emit
  only a bounded `PatchSecurityTerminal` and never a candidate or passed-path
  artifact fact.

## Verification and Review

- RED/GREEN targeted service verification passed (8/8 at phase acceptance).
- Cumulative Feature 2 verification, strict OpenSpec validation, diff hygiene,
  and static no-I/O boundary checks passed.
- Independent review was required and completed under the user-authorized
  review workflow.

## Scope Confirmation

The service has no source/diff renderer, patch material, execution, workspace,
OCI, GitHub, persistence, approval, PDR, validation/review, retry, network, or
credential capability.

Commit: `0a62369` (`feat(patch-security): assemble terminal-first facts`).

Status: **Accepted**.
