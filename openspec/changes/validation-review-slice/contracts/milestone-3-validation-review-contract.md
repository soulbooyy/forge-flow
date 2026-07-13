# Milestone 3 Contract Design: Validation and Review

## Purpose

This reference makes the accepted M3 OpenSpec implementable without allowing a
phase to invent terminal semantics, lineage, or an execution surface. It is
subordinate to the M3 OpenSpec change.

## Envelope Families

```text
ValidationEnvelope = ValidationResult | ValidationTerminal
ReviewEnvelope = ReviewResult | ValidationReviewError
```

All successful and terminal contracts are frozen, independently identified,
and payload-free. They contain no command text, working directory, exit code,
stdout, stderr, environment value, raw report, source payload, runtime trace,
timestamp, run ID, retry count, repair instruction, approval, or PR-readiness
field.

## Shared Lineage Rules

Every envelope has `patch_proposal_contract_id: pp_sha256:<lowercase-hex>` and
one or more Policy Decision Record references. Artifact and evidence references
use only IDs that were supplied by the deterministic M3 fixture set; their
payloads are not copied. An attempt ID exists only for a completed
`ValidationResult` and is `m3a_sha256:<lowercase-hex>`.

## ValidationResult

Required fields:

- `schema_version`: `"validation-result/v1"`
- `result_type`: `"validation_result"`
- `contract_id`: `vr_sha256:<lowercase-hex>`
- `patch_proposal_contract_id`
- `attempt_id`
- `fixture_case_id`: controlled M3 deterministic fixture case ID
- `outcome`: `"passed" | "failed"`
- `finding_codes`: sorted unique bounded controlled values
- `policy_decision_refs`: non-empty sorted Policy Decision Record IDs
- `evidence_ref_ids`: sorted unique bounded IDs
- `artifact_ids`: sorted unique bounded IDs

An `allowed` policy decision reference is required. `failed` is a fixture fact,
not retry eligibility, repair intent, or execution failure semantics.

## ValidationTerminal

Required fields:

- `schema_version`: `"validation-terminal/v1"`
- `result_type`: `"validation_terminal"`
- `terminal_id`: `vt_sha256:<lowercase-hex>`
- `patch_proposal_contract_id`
- `terminal_reason`: `"policy_blocked" | "human_approval_required"`
- `policy_decision_refs`: non-empty sorted Policy Decision Record IDs
- `evidence_ref_ids`: sorted unique bounded IDs
- `artifact_ids`: sorted unique bounded IDs

`terminal_reason: "policy_blocked"` requires a referenced `blocked` Policy
Decision Record. `terminal_reason: "human_approval_required"` requires a
referenced `requires_human_approval` record. A terminal has no `attempt_id`,
fixture case, outcome, or simulated execution fact.

## ReviewResult

Required fields:

- `schema_version`: `"review-result/v1"`
- `result_type`: `"review_result"`
- `contract_id`: `rr_sha256:<lowercase-hex>`
- `patch_proposal_contract_id`
- `validation_result_contract_id`: `vr_sha256:<lowercase-hex>`
- `findings`: non-empty ordered `ReviewFinding[]`
- `policy_decision_refs`: non-empty sorted Policy Decision Record IDs
- `evidence_ref_ids`: sorted unique bounded IDs
- `artifact_ids`: sorted unique bounded IDs

`ReviewFinding` contains a bounded `finding_code`, a severity of
`"advisory" | "blocking"`, and sorted bounded evidence-reference IDs. A
review result never contains an outcome, approval, authorization, retry, or PR
field. It cannot reference a `ValidationTerminal`.

## Policy Decision Record Reference

M3 references a separate immutable Policy Decision Record with:

- `decision_id`: `pdr_sha256:<lowercase-hex>`
- `decision`: `"allowed" | "blocked" | "requires_human_approval"`
- `policy_profile_id`: `"validation-review/m3-fixture-v1"`
- `policy_version`: integer `1`
- `evaluator_id`: `"m3/deterministic-policy-fixture-v1"`
- `subject_contract_id`: the proposal, validation, or review contract evaluated
- `risk_flags`: sorted unique bounded controlled values

This is a fixture representation of the RFC-004 Policy Decision Record shape,
not a policy-engine implementation or approval artifact.

## ValidationReviewError

Required fields:

- `schema_version`: `"validation-review-error/v1"`
- `result_type`: `"validation_review_error"`
- `error_id`: `vre_sha256:<lowercase-hex>`
- `completion_status`: `"validation_error"`
- `error_code`: one of `"unsupported_patch_proposal"`,
  `"invalid_fixture_case"`, `"invalid_policy_reference"`,
  `"policy_lineage_mismatch"`, `"dangling_evidence_ref"`,
  `"dangling_artifact_ref"`, `"forbidden_payload"`,
  `"invalid_review_input"`, or `"bounds_exceeded"`
- `message`: bounded safe fixed message
- `summary`: only safe contract IDs, fixture case ID, and policy profile ID when
  available

The error envelope contains no partial validation terminal, result, finding,
or raw input value.

## Canonical Identity

Canonical JSON follows M1/M2 rules: UTF-8, lexicographic object-key ordering,
compact separators, integers only, explicit required empty arrays, omitted
absent optional fields, and the stated deterministic array ordering. Floats,
unknown object values, and forbidden payload field names are validation errors.

`ValidationResult.contract_id`, `ReviewResult.contract_id`,
`ValidationTerminal.terminal_id`, and `ValidationReviewError.error_id` derive
from SHA-256 canonical payloads with only their respective identity field
omitted.
