"""Immutable contracts and canonical identities for Milestone 2 PatchProposal."""

from .canonical import (
    candidate_digest_for,
    canonical_bytes,
    policy_decision_id_for,
    proposal_error_id_for,
    proposal_id_for,
    sha256_hex,
)
from .models import (
    CandidateChange,
    FixStrategy,
    PatchProposal,
    PatchProposalEnvelope,
    PatchProposalValidationError,
    PolicyDecisionRef,
    RootCauseHypothesis,
    TaskInput,
    ValidationErrorSummary,
)
from .policy import PolicyBlockedError, assess_boundary
from .profile import M2_CONSERVATIVE_V1, PatchProposalProfile

__all__ = [
    "CandidateChange",
    "FixStrategy",
    "M2_CONSERVATIVE_V1",
    "PatchProposal",
    "PatchProposalEnvelope",
    "PatchProposalProfile",
    "PatchProposalValidationError",
    "PolicyBlockedError",
    "PolicyDecisionRef",
    "RootCauseHypothesis",
    "TaskInput",
    "ValidationErrorSummary",
    "candidate_digest_for",
    "assess_boundary",
    "canonical_bytes",
    "policy_decision_id_for",
    "proposal_error_id_for",
    "proposal_id_for",
    "sha256_hex",
]
