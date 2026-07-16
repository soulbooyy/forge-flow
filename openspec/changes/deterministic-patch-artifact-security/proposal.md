# Change: Deterministic Patch Artifact and Security Scanning

## Why

M1 repository context and M2's declarative `PatchProposal` establish bounded
repository and change-intent facts, while M4 Feature 1 establishes governed
execution without patch generation. M4 needs a separate Feature 2 that can
turn an accepted proposal into an identity-bound change-artifact metadata fact
and security facts without creating a diff, source-access capability, workspace
write, execution, commit, PR, or persistence authorization.

## Scope

- define immutable `PatchIntent`, `PatchArtifact`, `SecretScanResult`, and
  `RedactionFact` contracts with deterministic identity and explicit lineage;
- deterministically construct a metadata-only change artifact fact against the
  registered fixture repository identity and fixed base revision;
- enforce registered policy-profile path bounds while producing security facts
  from the versioned scanner and redaction rule sets over bounded metadata;
- create only an eligible, non-persistent `RedactedArtifactReferenceCandidate`
  when metadata scan and redaction both succeed; and
- specify fail-closed fixtures for secret findings, scanner failure, redaction
  failure, and indeterminate security results.

## Non-goals

- workspace mutation, patch application, `git apply`, execution, validation,
  review, retry, sandbox changes, or any OCI backend use;
- approval request/decision implementation, Policy Decision Record evaluation,
  artifact-store publication, durable references, or `DurableRunSummary`;
- GitHub Issue retrieval, branch/commit/Draft PR creation, or any external
  side effect;
- raw-patch, raw-diff, raw-source, raw-command-output, credential,
  environment-value, or temporary-workspace-path persistence; and
- creating or changing scanner/redaction rules, policy budgets, or fixture
  profile values.

## Architecture Readiness Gate

The scoped amendments accepted in RFC-002, RFC-004, and RFC-005 define this
change's contract, security, and pre-persistence boundary. RFC-006's registered
fixture profile supplies the sole source of path budgets and requires
scanner failure, redaction failure, and indeterminate security results to be
`blocked`. ADR-011 remains an execution-only boundary and is not invoked here.

Grill-Me Report mode has challenged and accepted the following scope cuts:
`PatchArtifact` is a metadata-only change fact rather than a diff; security
results are facts rather than authorization; Feature 3 owns controlled
publication and durable references; and patch materialization/application
remains outside Feature 2.

This Draft OpenSpec requires user review and acceptance before any planning.
It authorizes neither a branch/worktree nor implementation activity.

## Impact

This change adds Feature 2's contract and security-fact boundary. It preserves
the existing rule that a fresh `PolicyDecisionRecord` over current inputs is
the only authorization decision for a later action.
