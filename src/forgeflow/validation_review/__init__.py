"""Fixture-only contracts for the Milestone 3 validation and review slice."""

from .canonical import (
    canonical_bytes,
    policy_decision_id_for,
    review_result_id_for,
    validation_result_id_for,
    validation_review_error_id_for,
    validation_terminal_id_for,
)
from .models import (
    PolicyDecisionRecordRef,
    ReviewFinding,
    ReviewResult,
    ValidationEnvelope,
    ValidationResult,
    ValidationReviewError,
    ValidationReviewErrorSummary,
    ValidationTerminal,
)
from .profile import M3_FIXTURE_V1
from .service import build_review_result, build_validation_envelope

__all__ = [
    "M3_FIXTURE_V1",
    "PolicyDecisionRecordRef",
    "ReviewFinding",
    "ReviewResult",
    "ValidationEnvelope",
    "ValidationResult",
    "ValidationReviewError",
    "ValidationReviewErrorSummary",
    "ValidationTerminal",
    "canonical_bytes",
    "build_review_result",
    "build_validation_envelope",
    "policy_decision_id_for",
    "review_result_id_for",
    "validation_result_id_for",
    "validation_review_error_id_for",
    "validation_terminal_id_for",
]
