# Structured PatchProposal Design

## Design Review Record

Grill-Me review completed during planning. Its accepted outcomes are reflected
in this change, RFC-003, ADR-007, and the versioned M2 policy profile: fixture
only provider neutrality; no source payload or runtime/tool invocation;
environment-file escalation; exact high-risk path-segment matching; and
approval-required deletion intent. No standalone review artifact is an
implementation authority.

## Boundaries

`RepositoryContextResult` remains immutable context and evidence. A
`PatchProposal` references it through `repository_context_contract_id` and
selected `evidence_ref.id` values; it never appends root-cause, policy, diff,
or validation state to the M1 result.

The proposal is declarative. It expresses what might change and why, not a
permission or a tool sequence. The workflow/policy layer owns authorization;
future Level 1 sandbox tooling owns any workspace mutation.

## Contract Shape

The complete M2 schema, controlled values, policy-reference identity, canonical
serialization, and validation-error boundary are defined in
[Milestone 2 PatchProposal Contract Design](contracts/milestone-2-patch-proposal-contract.md).

Successful envelopes have `result_type: "patch_proposal"` and contain:

- `schema_version` and hash-derived `contract_id`;
- `repository_context_contract_id` and bounded task-input reference;
- one or more bounded `root_cause_hypotheses`, each with supporting evidence
  IDs and an explicit uncertainty level;
- one bounded `fix_strategy` with an intended outcome and constraints;
- ordered `candidate_changes` with canonical workspace-relative paths,
  change-kind enum, rationale, and supporting evidence IDs;
- controlled `risk_flags`, `limitations`, and a `boundary_assessment_ref`.

Validation failures use `result_type: "patch_proposal_validation_error"` and
cannot include partial successful proposal fields. M2 uses the bounded fields,
controlled change kinds, and policy identity in
[`m2-patch-proposal-v1`](policy-profiles/m2-patch-proposal-v1.md).

## Security and Policy Boundary

### Policy Boundary

The proposal may carry a reference to the policy assessment that evaluated its
candidate paths and declared scope. It does not embed an approval, claim that
a sensitive file is authorized, or use a policy record as an editing permit.
The assessment result is `allowed`, `blocked`, or
`requires_human_approval`, as defined by RFC-004. An `allowed` assessment
still authorizes no filesystem mutation; a later Action Intent is required.

### Evidence and Payload Boundary

Every hypothesis and candidate change must cite at least one evidence ID from
the referenced M1 context. Raw source snippets, complete source files, raw
provider output, prompts, shell text, environment values, absolute paths, and
unbounded task input are excluded. A later governed artifact store may hold
redacted payloads by reference only after its own authority exists. M2 uses
only the local `m2/deterministic-fixture-v1` proposal source defined by ADR-007
and RFC-003; it sends no source material to a provider.

## Failure and Stop Behavior

Invalid or incompatible repository-context input, missing evidence references,
unsupported schema versions, malformed task input, unresolved policy profile,
or any readiness-gate failure produces a structured stop/validation outcome.
The producer must not infer missing evidence, reread the workspace, fall back
to uncontrolled tools, or emit a partial success.
