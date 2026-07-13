"""Pure, profile-driven PatchProposal boundary assessment for Milestone 2."""

from __future__ import annotations

from dataclasses import replace
import unicodedata

from .canonical import candidate_digest_for, policy_decision_id_for
from .models import CandidateChange, PolicyDecisionRef
from .profile import M2_CONSERVATIVE_V1, PatchProposalProfile


class PolicyBlockedError(ValueError):
    """A blocked path-only policy result with no successful policy reference."""

    error_code = "policy_blocked"

    def __init__(self, *, profile: PatchProposalProfile, candidate_digest: str) -> None:
        super().__init__("candidate changes are blocked by the active policy profile")
        self.policy_profile_id = profile.policy_profile_id
        self.policy_version = profile.policy_version
        self.evaluator_id = profile.evaluator_id
        self.evaluated_candidate_digest = candidate_digest


def assess_boundary(
    changes: tuple[CandidateChange, ...], profile: PatchProposalProfile
) -> PolicyDecisionRef:
    """Assess ordered declarative candidate changes without performing side effects."""
    _require_active_m2_profile(profile)
    _require_candidate_bounds(changes, profile)

    candidate_digest = candidate_digest_for(changes)
    if any(_is_blocked(change.path, profile) for change in changes):
        raise PolicyBlockedError(profile=profile, candidate_digest=candidate_digest)

    environment_match = any(_is_environment_path(change.path, profile) for change in changes)
    high_risk_match = any(_is_high_risk_path(change.path, profile) for change in changes)
    deletion_intent = profile.approval_required_for_remove_file and any(
        change.change_kind == "remove_file" for change in changes
    )
    requires_approval = environment_match or high_risk_match or deletion_intent
    risk_flags = _risk_flags(
        environment_match=environment_match,
        high_risk_match=high_risk_match,
        deletion_intent=deletion_intent,
        requires_approval=requires_approval,
    )
    decision = "requires_human_approval" if requires_approval else "allowed"
    provisional = PolicyDecisionRef(
        decision_id="pdr_sha256:" + "0" * 64,
        decision=decision,
        policy_profile_id=profile.policy_profile_id,
        policy_version=profile.policy_version,
        evaluator_id=profile.evaluator_id,
        evaluated_candidate_digest=candidate_digest,
        risk_flags=risk_flags,
        revalidation_required=True,
    )
    return replace(provisional, decision_id=policy_decision_id_for(provisional))


def _require_active_m2_profile(profile: PatchProposalProfile) -> None:
    if profile != M2_CONSERVATIVE_V1:
        raise ValueError("the active M2 conservative policy profile is required")


def _require_candidate_bounds(
    changes: tuple[CandidateChange, ...], profile: PatchProposalProfile
) -> None:
    if not isinstance(changes, tuple) or not changes:
        raise ValueError("candidate changes must be a non-empty tuple")
    if len(changes) > profile.max_candidate_changes:
        raise ValueError("candidate changes exceed the active policy profile bound")
    if not all(isinstance(change, CandidateChange) for change in changes):
        raise ValueError("candidate changes must use the M2 contract type")


def _is_blocked(path: str, profile: PatchProposalProfile) -> bool:
    segments = path.split("/")
    file_name = segments[-1]
    return (
        any(segment in profile.blocked_path_segments for segment in segments[:-1])
        or file_name.endswith(profile.blocked_file_suffixes)
        or file_name in profile.blocked_file_names
    )


def _is_environment_path(path: str, profile: PatchProposalProfile) -> bool:
    file_name = path.rsplit("/", 1)[-1]
    return file_name in profile.approval_environment_file_names or file_name.startswith(
        profile.approval_environment_file_prefixes
    )


def _is_high_risk_path(path: str, profile: PatchProposalProfile) -> bool:
    segments = path.split("/")
    file_name = segments[-1]
    normalized_segments = tuple(
        unicodedata.normalize("NFC", segment).casefold() for segment in segments
    )
    return (
        any(
            path.startswith(f"{directory}/")
            for directory in profile.approval_ci_directory_prefixes
        )
        or file_name in profile.approval_ci_file_names
        or any(segment in profile.approval_infrastructure_path_segments for segment in segments[:-1])
        or file_name.endswith(profile.approval_infrastructure_file_suffixes)
        or any(segment in profile.approval_auth_path_segments for segment in normalized_segments)
        or any(
            path.startswith(f"{directory}/")
            for directory in profile.approval_migration_directory_prefixes
        )
        or file_name in profile.approval_lockfile_names
    )


def _risk_flags(
    *,
    environment_match: bool,
    high_risk_match: bool,
    deletion_intent: bool,
    requires_approval: bool,
) -> tuple[str, ...]:
    flags: set[str] = set()
    if requires_approval:
        flags.add("policy_requires_human_approval")
    if environment_match:
        flags.add("environment_path")
    if high_risk_match:
        flags.add("high_risk_path")
    if deletion_intent:
        flags.add("deletion_intent")
    return tuple(sorted(flags))
