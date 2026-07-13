"""In-memory deterministic attempt and review fixture facts for M3."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .models import ReviewFinding


@dataclass(frozen=True, slots=True)
class FixtureValidationAttempt:
    case_id: Literal["passed-default", "failed-default"]
    attempt_id: str
    outcome: Literal["passed", "failed"]
    finding_codes: tuple[str, ...]
    evidence_ref_ids: tuple[str, ...]
    artifact_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FixtureReviewFindings:
    case_id: Literal["blocking-default"]
    findings: tuple[ReviewFinding, ...]
    evidence_ref_ids: tuple[str, ...]
    artifact_ids: tuple[str, ...]


_EVIDENCE_ID = "ev_sha256:" + "a" * 64
_ARTIFACT_ID = "artifact_sha256:" + "b" * 64

_VALIDATION_FIXTURES: dict[str, FixtureValidationAttempt] = {
    "passed-default": FixtureValidationAttempt(
        case_id="passed-default",
        attempt_id="m3a_sha256:" + "c" * 64,
        outcome="passed",
        finding_codes=(),
        evidence_ref_ids=(_EVIDENCE_ID,),
        artifact_ids=(_ARTIFACT_ID,),
    ),
    "failed-default": FixtureValidationAttempt(
        case_id="failed-default",
        attempt_id="m3a_sha256:" + "d" * 64,
        outcome="failed",
        finding_codes=("fixture_assertion_failed",),
        evidence_ref_ids=(_EVIDENCE_ID,),
        artifact_ids=(_ARTIFACT_ID,),
    ),
}

_REVIEW_FIXTURES: dict[str, FixtureReviewFindings] = {
    "blocking-default": FixtureReviewFindings(
        case_id="blocking-default",
        findings=(
            ReviewFinding(
                finding_code="validation_failure_requires_review",
                severity="blocking",
                evidence_ref_ids=(_EVIDENCE_ID,),
            ),
        ),
        evidence_ref_ids=(_EVIDENCE_ID,),
        artifact_ids=(),
    )
}


def load_validation_fixture(case_id: str) -> FixtureValidationAttempt:
    """Return one completed in-memory attempt fact or raise a lookup error."""

    try:
        return _VALIDATION_FIXTURES[case_id]
    except KeyError as error:
        raise LookupError("unknown deterministic validation fixture case") from error


def load_review_fixture(case_id: str) -> FixtureReviewFindings:
    """Return one in-memory review finding set or raise a lookup error."""

    try:
        return _REVIEW_FIXTURES[case_id]
    except KeyError as error:
        raise LookupError("unknown deterministic review fixture case") from error
