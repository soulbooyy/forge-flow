"""Terminal PatchProposal assembly from immutable context and fixture intent."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields, is_dataclass, replace
import re

from forgeflow.repository_context.models import RepositoryContextResult

from .canonical import proposal_error_id_for, proposal_id_for
from .models import (
    CandidateChange,
    FixtureCandidateChangeDraft,
    FixtureProposalDraft,
    FixtureRootCauseDraft,
    FixStrategy,
    PatchProposal,
    PatchProposalEnvelope,
    PatchProposalValidationError,
    RootCauseHypothesis,
    TaskInput,
    ValidationErrorSummary,
)
from .policy import PolicyBlockedError, assess_boundary
from .profile import M2_CONSERVATIVE_V1, PatchProposalProfile


_REPOSITORY_CONTEXT_ID = re.compile(r"^rcr_sha256:[0-9a-f]{64}$")
_FORBIDDEN_DRAFT_FIELDS = frozenset(
    {
        "raw_source",
        "raw_payload",
        "source_content",
        "diff",
        "patch",
        "command",
        "command_output",
        "provider_payload",
        "prompt",
        "absolute_path",
        "environment_value",
        "timestamp",
        "run_id",
        "network",
        "branch",
        "commit",
        "pr",
        "memory",
        "workflow",
    }
)
_FIXED_LIMITATION_CODES = (
    "fixture_only_source",
    "no_diff_generated",
    "no_source_payload",
    "no_validation_executed",
)


def build_patch_proposal(
    context: object, task_input: object, draft: object
) -> PatchProposalEnvelope:
    """Build exactly one payload-free success or validation terminal envelope."""
    profile = _active_profile()
    if profile is None:
        return _validation_error(
            "invalid_policy_profile",
            "policy_profile",
            "the M2 conservative policy profile is unavailable",
            context=context,
            task_input=task_input,
            include_profile=False,
        )
    if not _is_supported_context(context):
        return _validation_error(
            "unsupported_repository_context",
            "repository_context",
            "repository context is unsupported",
            context=context,
            task_input=task_input,
        )
    if not isinstance(task_input, TaskInput):
        return _validation_error(
            "invalid_task_input",
            "task_input",
            "task input is invalid",
            context=context,
        )
    if _has_forbidden_draft_field(draft):
        return _validation_error(
            "raw_payload_forbidden",
            "proposal_draft",
            "fixture draft contains a forbidden payload field",
            context=context,
            task_input=task_input,
        )
    if not isinstance(draft, FixtureProposalDraft):
        return _validation_error(
            "fixture_draft_malformed",
            "proposal_draft",
            "fixture draft is malformed",
            context=context,
            task_input=task_input,
        )

    converted = _convert_draft(context, task_input, draft, profile)
    if isinstance(converted, PatchProposalValidationError):
        return converted
    hypotheses, strategy, candidates = converted
    evidence_ids = {reference.id for reference in context.evidence_refs}
    declared_evidence_ids = {
        evidence_id
        for hypothesis in hypotheses
        for evidence_id in hypothesis.supporting_evidence_ref_ids
    } | {
        evidence_id
        for candidate in candidates
        for evidence_id in candidate.supporting_evidence_ref_ids
    }
    if not declared_evidence_ids <= evidence_ids:
        return _validation_error(
            "dangling_evidence_ref",
            "proposal_draft",
            "fixture draft references evidence absent from repository context",
            context=context,
            task_input=task_input,
        )
    try:
        policy_decision = assess_boundary(candidates, profile)
    except PolicyBlockedError:
        return _validation_error(
            "policy_blocked",
            "candidate_change",
            "candidate changes are blocked by the active policy profile",
            context=context,
            task_input=task_input,
        )
    except ValueError:
        return _validation_error(
            "invalid_policy_profile",
            "policy_profile",
            "the M2 conservative policy profile is invalid",
            context=context,
            task_input=task_input,
            include_profile=False,
        )

    provisional = PatchProposal(
        contract_id="pp_sha256:" + "0" * 64,
        proposal_source_id=profile.proposal_source_id,
        repository_context_contract_id=context.contract_id,
        task_input=task_input,
        root_cause_hypotheses=hypotheses,
        fix_strategy=strategy,
        candidate_changes=candidates,
        policy_decision=policy_decision,
        risk_flags=policy_decision.risk_flags,
        limitation_codes=_FIXED_LIMITATION_CODES,
    )
    return replace(provisional, contract_id=proposal_id_for(provisional))


def _active_profile() -> PatchProposalProfile | None:
    return M2_CONSERVATIVE_V1 if isinstance(M2_CONSERVATIVE_V1, PatchProposalProfile) else None


def _is_supported_context(value: object) -> bool:
    return (
        isinstance(value, RepositoryContextResult)
        and value.schema_version == "repository-context-result/v1"
        and value.result_type == "repository_context_result"
        and bool(_REPOSITORY_CONTEXT_ID.fullmatch(value.contract_id))
    )


def _has_forbidden_draft_field(value: object) -> bool:
    if isinstance(value, Mapping):
        return any(isinstance(key, str) and key in _FORBIDDEN_DRAFT_FIELDS for key in value)
    if is_dataclass(value) and not isinstance(value, type):
        return bool(_FORBIDDEN_DRAFT_FIELDS & {field.name for field in fields(value)})
    return False


def _convert_draft(
    context: RepositoryContextResult,
    task_input: TaskInput,
    draft: FixtureProposalDraft,
    profile: PatchProposalProfile,
) -> tuple[tuple[RootCauseHypothesis, ...], FixStrategy, tuple[CandidateChange, ...]] | PatchProposalValidationError:
    if not isinstance(draft.root_cause_hypotheses, tuple) or not draft.root_cause_hypotheses:
        return _validation_error(
            "empty_hypotheses",
            "proposal_draft",
            "fixture draft has no root-cause hypotheses",
            context=context,
            task_input=task_input,
        )
    if len(draft.root_cause_hypotheses) > profile.max_root_cause_hypotheses:
        return _validation_error(
            "bounds_exceeded",
            "proposal_draft",
            "fixture draft exceeds a configured bound",
            context=context,
            task_input=task_input,
        )
    if not isinstance(draft.candidate_changes, tuple) or not draft.candidate_changes:
        return _validation_error(
            "invalid_candidate_change",
            "candidate_change",
            "fixture draft has no candidate changes",
            context=context,
            task_input=task_input,
        )
    if len(draft.candidate_changes) > profile.max_candidate_changes:
        return _validation_error(
            "bounds_exceeded",
            "candidate_change",
            "fixture draft exceeds a configured bound",
            context=context,
            task_input=task_input,
        )
    if _text_exceeds_bound(draft.fix_strategy_summary, profile.max_fix_strategy_chars):
        return _validation_error(
            "bounds_exceeded",
            "proposal_draft",
            "fixture draft exceeds a configured bound",
            context=context,
            task_input=task_input,
        )
    try:
        hypotheses = tuple(
            sorted(
                (_convert_hypothesis(item, profile) for item in draft.root_cause_hypotheses),
                key=lambda item: (item.statement, item.uncertainty, item.supporting_evidence_ref_ids),
            )
        )
        candidates = tuple(
            sorted(
                (_convert_candidate(item, profile) for item in draft.candidate_changes),
                key=lambda item: (item.path, item.change_kind, item.rationale),
            )
        )
        strategy = FixStrategy(
            summary=draft.fix_strategy_summary,
            constraint_codes=profile.required_fix_strategy_constraint_codes,
        )
    except _DraftBoundsError:
        return _validation_error(
            "bounds_exceeded",
            "proposal_draft",
            "fixture draft exceeds a configured bound",
            context=context,
            task_input=task_input,
        )
    except _DraftChangeKindError:
        return _validation_error(
            "invalid_change_kind",
            "candidate_change",
            "fixture draft uses an unsupported change kind",
            context=context,
            task_input=task_input,
        )
    except (TypeError, ValueError):
        return _validation_error(
            "fixture_draft_malformed",
            "proposal_draft",
            "fixture draft is malformed",
            context=context,
            task_input=task_input,
        )
    return hypotheses, strategy, candidates


def _convert_hypothesis(
    value: object, profile: PatchProposalProfile
) -> RootCauseHypothesis:
    if not isinstance(value, FixtureRootCauseDraft):
        raise TypeError
    if _text_exceeds_bound(value.statement, profile.max_hypothesis_chars):
        raise _DraftBoundsError
    return RootCauseHypothesis(
        statement=value.statement,
        uncertainty=value.uncertainty,  # type: ignore[arg-type]
        supporting_evidence_ref_ids=value.supporting_evidence_ref_ids,
    )


def _convert_candidate(
    value: object, profile: PatchProposalProfile
) -> CandidateChange:
    if not isinstance(value, FixtureCandidateChangeDraft):
        raise TypeError
    if _text_exceeds_bound(value.rationale, profile.max_candidate_rationale_chars):
        raise _DraftBoundsError
    if value.change_kind not in profile.allowed_change_kinds:
        raise _DraftChangeKindError
    return CandidateChange(
        path=value.path,
        change_kind=value.change_kind,  # type: ignore[arg-type]
        rationale=value.rationale,
        supporting_evidence_ref_ids=value.supporting_evidence_ref_ids,
    )


def _text_exceeds_bound(value: object, maximum: int) -> bool:
    return isinstance(value, str) and len(value) > maximum


class _DraftBoundsError(ValueError):
    pass


class _DraftChangeKindError(ValueError):
    pass


def _validation_error(
    error_code: str,
    input_category: str,
    message: str,
    *,
    context: object | None = None,
    task_input: object | None = None,
    include_profile: bool = True,
) -> PatchProposalValidationError:
    summary = ValidationErrorSummary(
        repository_context_contract_id=(
            context.contract_id if _is_supported_context(context) else None
        ),
        task_ref=task_input.task_ref if isinstance(task_input, TaskInput) else None,
        policy_profile_id=(
            M2_CONSERVATIVE_V1.policy_profile_id
            if include_profile and isinstance(M2_CONSERVATIVE_V1, PatchProposalProfile)
            else None
        ),
    )
    provisional = PatchProposalValidationError(
        error_id="ppe_sha256:" + "0" * 64,
        error_code=error_code,  # type: ignore[arg-type]
        input_category=input_category,  # type: ignore[arg-type]
        message=message,
        summary=summary,
    )
    return replace(provisional, error_id=proposal_error_id_for(provisional))
