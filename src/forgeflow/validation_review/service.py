"""Fixture-only assembly of M3 validation and review contracts."""

from __future__ import annotations

from dataclasses import replace
from collections.abc import Mapping

from forgeflow.patch_proposal import PatchProposal

from .canonical import review_result_id_for, validation_result_id_for, validation_review_error_id_for, validation_terminal_id_for
from .fixture_source import load_review_fixture, load_validation_fixture
from .models import ReviewResult, ValidationEnvelope, ValidationResult, ValidationReviewError, ValidationReviewErrorSummary, ValidationTerminal
from .policy import policy_record_for
from .profile import M3_FIXTURE_V1


def build_validation_envelope(proposal: object, policy_case: object, fixture_case: object) -> ValidationEnvelope | ValidationReviewError:
    if not isinstance(proposal, PatchProposal):
        return _error("unsupported_patch_proposal")
    if not isinstance(policy_case, str):
        return _error("invalid_policy_reference", proposal.contract_id)
    try:
        policy = policy_record_for(proposal.contract_id, policy_case)
    except LookupError:
        return _error("invalid_policy_reference", proposal.contract_id)
    evidence_ids = _proposal_evidence_ids(proposal)
    if policy.decision != "allowed":
        reason = "policy_blocked" if policy.decision == "blocked" else "human_approval_required"
        provisional = ValidationTerminal("vt_sha256:" + "0" * 64, proposal.contract_id, reason, (policy,), evidence_ids, ())
        return replace(provisional, terminal_id=validation_terminal_id_for(provisional))
    if _has_forbidden_payload_field(fixture_case):
        return _error("forbidden_payload", proposal.contract_id)
    if not isinstance(fixture_case, str):
        return _error("invalid_fixture_case", proposal.contract_id)
    try:
        fixture = load_validation_fixture(fixture_case)
    except LookupError:
        return _error("invalid_fixture_case", proposal.contract_id)
    if not set(fixture.evidence_ref_ids).issubset(evidence_ids):
        return _error("dangling_evidence_ref", proposal.contract_id, fixture.case_id)
    provisional = ValidationResult("vr_sha256:" + "0" * 64, proposal.contract_id, fixture.attempt_id, fixture.case_id, fixture.outcome, fixture.finding_codes, (policy,), fixture.evidence_ref_ids, fixture.artifact_ids)
    return replace(provisional, contract_id=validation_result_id_for(provisional))


def build_review_result(proposal: object, validation_result: object, policy_case: object, review_case: object) -> ReviewResult | ValidationReviewError:
    if not isinstance(proposal, PatchProposal) or not isinstance(validation_result, ValidationResult):
        return _error("invalid_review_input")
    if validation_result.patch_proposal_contract_id != proposal.contract_id or not isinstance(policy_case, str):
        return _error("invalid_review_input", proposal.contract_id)
    if _has_forbidden_payload_field(review_case):
        return _error("forbidden_payload", proposal.contract_id)
    if not isinstance(review_case, str):
        return _error("invalid_review_input", proposal.contract_id)
    try:
        policy = policy_record_for(validation_result.contract_id, policy_case)
        fixture = load_review_fixture(review_case)
    except LookupError:
        return _error("invalid_review_input", proposal.contract_id)
    if not set(fixture.evidence_ref_ids).issubset(_proposal_evidence_ids(proposal)):
        return _error("dangling_evidence_ref", proposal.contract_id)
    provisional = ReviewResult("rr_sha256:" + "0" * 64, proposal.contract_id, validation_result.contract_id, fixture.findings, (policy,), fixture.evidence_ref_ids, fixture.artifact_ids)
    return replace(provisional, contract_id=review_result_id_for(provisional))


def _proposal_evidence_ids(proposal: PatchProposal) -> tuple[str, ...]:
    return tuple(sorted({item for hypothesis in proposal.root_cause_hypotheses for item in hypothesis.supporting_evidence_ref_ids} | {item for change in proposal.candidate_changes for item in change.supporting_evidence_ref_ids}))


def _has_forbidden_payload_field(value: object) -> bool:
    return isinstance(value, Mapping) and any(
        isinstance(key, str) and key in M3_FIXTURE_V1.forbidden_payload_field_names
        for key in value
    )


def _error(code: str, proposal_id: str | None = None, fixture_case_id: str | None = None) -> ValidationReviewError:
    messages = {"unsupported_patch_proposal": "Patch proposal is unsupported.", "invalid_policy_reference": "Policy fixture is invalid.", "invalid_fixture_case": "Fixture case is invalid.", "forbidden_payload": "Fixture payload field is forbidden.", "dangling_evidence_ref": "Fixture evidence does not close over proposal evidence.", "invalid_review_input": "Review input is invalid."}
    provisional = ValidationReviewError("vre_sha256:" + "0" * 64, code, messages[code], ValidationReviewErrorSummary(proposal_id, fixture_case_id, "validation-review/m3-fixture-v1" if proposal_id else None))
    return replace(provisional, error_id=validation_review_error_id_for(provisional))
