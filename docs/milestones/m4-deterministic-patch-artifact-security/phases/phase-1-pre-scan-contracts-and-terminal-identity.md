# Re-baselined Phase 1: Pre-scan Contracts and Terminal Identity

## Goal

Replace the superseded artifact-first contract order with terminal-first,
payload-free contracts. This phase adds no scanner/redactor operation, service
assembly, source access, artifact persistence, approval, or side effect.

## Scope

- Add immutable `PreScanPatchMetadataIdentity` as the non-persistent lineage
  anchor for a bounded transient metadata projection.
- Make `SecretScanResult` and `RedactionFact` bind that pre-scan identity.
- Remove `change_description` from returned `PatchIntent`; make it a passed-path
  contract bound to a metadata digest and pre-scan identity.
- Add non-authorizing `PatchSecurityTerminal` with canonical identity and the
  accepted controlled status/reason vocabulary.
- Add canonical pre-scan and terminal ID helpers, update package exports, and
  update the in-code allowlist names to the accepted pre-scan projection.

## TDD and Verification

- RED: terminal-first contract/canonical tests failed to import the absent
  pre-scan and terminal contracts/helpers.
- GREEN: targeted contract and canonical tests pass 9/9.
- Static boundary check found no subprocess, network, filesystem-path, or
  external-I/O surface in the Feature 2 package.
- `openspec validate deterministic-patch-artifact-security --strict` and
  `git diff --check` pass.
- The repository-wide suite was run. Its 19 Feature 2 policy/service failures
  are the expected, recorded incompatibility of historical artifact-first Phase
  2/3 tests and implementations; they are owned by re-baselined Phases 2 and 3
  and were not bypassed by retaining prohibited pre-scan PatchIntent content.

## Independent Review Gate

- Independent review required: Yes — this phase modifies feature contracts,
  security boundary, and canonical identity.
- Subagent used: Yes — the user approved independent review for the phase.
- Review outcome: Two P1 findings were corrected: terminal reasons now bind
  compatible scan/redaction evidence, and `not_needed` redaction requires a
  passed scan. The reviewer approved the corrected phase diff.

## Scope Confirmation

No raw rationale, matched text, source, diff, patch material, command output,
credentials, environment value, workspace path, execution, approval, PDR,
persistence, OCI, GitHub, retry, or validation/review capability was added.
