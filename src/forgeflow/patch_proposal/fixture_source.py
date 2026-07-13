"""In-memory deterministic proposal-intent fixtures for Milestone 2."""

from .models import (
    FixtureCandidateChangeDraft,
    FixtureProposalDraft,
    FixtureRootCauseDraft,
)


class FixtureDraftNotFoundError(KeyError):
    """Raised when a caller requests an unsupported M2 fixture case."""


_VALID_DEFAULT = FixtureProposalDraft(
    root_cause_hypotheses=(
        FixtureRootCauseDraft(
            statement="Payment state can be absent at the handler boundary.",
            uncertainty="medium",
            supporting_evidence_ref_ids=("ev_sha256:" + "a" * 64,),
        ),
    ),
    fix_strategy_summary="Add the smallest evidence-backed guard and focused test.",
    candidate_changes=(
        FixtureCandidateChangeDraft(
            path="src/payment_handler.py",
            change_kind="modify_existing_file",
            rationale="Guard the missing payment state before dereferencing it.",
            supporting_evidence_ref_ids=("ev_sha256:" + "a" * 64,),
        ),
    ),
)

_FIXTURE_DRAFTS = {"valid-default": _VALID_DEFAULT}


def load_fixture_draft(case_id: str) -> FixtureProposalDraft:
    """Return a fixed transient draft without reading external state."""
    try:
        return _FIXTURE_DRAFTS[case_id]
    except KeyError as error:
        raise FixtureDraftNotFoundError(case_id) from error
