"""Pure deterministic policy fixtures for Milestone 3 contract tests."""

from __future__ import annotations

from dataclasses import replace

from .canonical import policy_decision_id_for
from .models import PolicyDecisionRecordRef
from .profile import M3_FIXTURE_V1


_POLICY_CASES: dict[str, tuple[str, tuple[str, ...]]] = {
    "allowed-default": ("allowed", ()),
    "blocked-default": ("blocked", ("blocked_by_policy",)),
    "requires-human-approval-default": (
        "requires_human_approval",
        ("human_approval_required",),
    ),
}


def policy_record_for(subject_contract_id: str, case_id: str) -> PolicyDecisionRecordRef:
    """Return a computed, fixture-only policy record for one controlled case."""

    try:
        decision, risk_flags = _POLICY_CASES[case_id]
    except KeyError as error:
        raise LookupError("unknown deterministic policy fixture case") from error

    provisional = PolicyDecisionRecordRef(
        decision_id="pdr_sha256:" + "0" * 64,
        decision=decision,  # type: ignore[arg-type]
        policy_profile_id=M3_FIXTURE_V1.policy_profile_id,
        policy_version=M3_FIXTURE_V1.policy_version,
        evaluator_id=M3_FIXTURE_V1.evaluator_id,
        subject_contract_id=subject_contract_id,
        risk_flags=risk_flags,
    )
    return replace(provisional, decision_id=policy_decision_id_for(provisional))
