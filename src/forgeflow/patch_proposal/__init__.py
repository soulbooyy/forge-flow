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
    FixtureCandidateChangeDraft,
    FixtureProposalDraft,
    FixtureRootCauseDraft,
    FixStrategy,
    PatchProposal,
    PatchProposalEnvelope,
    PatchProposalValidationError,
    PolicyDecisionRef,
    RootCauseHypothesis,
    TaskInput,
    ValidationErrorSummary,
)
from .fixture_source import FixtureDraftNotFoundError, load_fixture_draft
from .policy import PolicyBlockedError, assess_boundary
from .profile import M2_CONSERVATIVE_V1, PatchProposalProfile
from .service import build_patch_proposal

__all__ = [
    "CandidateChange",
    "FixtureCandidateChangeDraft",
    "FixtureDraftNotFoundError",
    "FixtureProposalDraft",
    "FixtureRootCauseDraft",
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
    "build_patch_proposal",
    "canonical_bytes",
    "policy_decision_id_for",
    "load_fixture_draft",
    "proposal_error_id_for",
    "proposal_id_for",
    "sha256_hex",
]
