"""Fixture-only Draft PR contracts; no GitHub client or credential surface."""

from .canonical import (
    idempotency_record_id_for,
    policy_decision_id_for,
    pr_result_id_for,
    request_id_for,
    terminal_id_for,
)
from .models import DraftPRRequest, FixturePolicyDecisionRecord, IdempotencyRecord, PRResult, PRTerminal
from .service import RedactedBodyFacts, evaluate_eligibility, render_redacted_body
from .adapter import AdapterOutcome, ControlledFixtureAdapter

__all__ = (
    "DraftPRRequest",
    "AdapterOutcome",
    "ControlledFixtureAdapter",
    "FixturePolicyDecisionRecord",
    "IdempotencyRecord",
    "PRResult",
    "PRTerminal",
    "RedactedBodyFacts",
    "evaluate_eligibility",
    "idempotency_record_id_for",
    "pr_result_id_for",
    "policy_decision_id_for",
    "request_id_for",
    "terminal_id_for",
    "render_redacted_body",
)
