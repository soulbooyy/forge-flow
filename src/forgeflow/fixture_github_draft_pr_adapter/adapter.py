"""Fail-closed Phase 3 fixture adapter seam with no mutation capability."""

from dataclasses import dataclass

from .models import DraftPRRequest, IdempotencyRecord, PRResult, PRTerminal
from .service import RedactedBodyFacts, evaluate_eligibility, render_redacted_body


@dataclass(frozen=True, slots=True)
class AdapterOutcome:
    """Bounded reconciliation result that never retains a credential or body."""

    idempotency_record: IdempotencyRecord
    terminal: PRTerminal
    result: PRResult

    def __post_init__(self) -> None:
        if (
            self.idempotency_record.state != "terminal"
            or self.idempotency_record.request_id != self.terminal.request_id
            or self.result.request_id != self.terminal.request_id
            or self.result.idempotency_record_id != self.idempotency_record.record_id
            or self.result.terminal_id != self.terminal.terminal_id
        ):
            raise ValueError("inconsistent adapter terminal outcome")


class ControlledFixtureAdapter:
    """The sole future GitHub seam, intentionally incapable of mutation today."""

    __slots__ = ("_outcomes",)

    def __init__(self) -> None:
        self._outcomes: dict[str, AdapterOutcome] = {}

    @property
    def external_mutation_count(self) -> int:
        """This metadata-only phase has no branch, commit, or Draft-PR operation."""
        return 0

    @staticmethod
    def _terminal(request: DraftPRRequest, reason: str) -> AdapterOutcome:
        record = IdempotencyRecord.create(request.request_id, request.idempotency_key, "terminal")
        terminal = PRTerminal.create(request.request_id, reason)
        return AdapterOutcome(record, terminal, PRResult.create_no_effect(request.request_id, record.record_id, terminal.terminal_id))

    def reconcile(
        self,
        request: object,
        policy: object,
        approval: object,
        reference: object,
        summary: object,
        facts: object,
        now: object,
        credential: object,
    ) -> AdapterOutcome:
        """Reconcile one request without inspecting or retaining the credential."""
        if not isinstance(request, DraftPRRequest):
            raise ValueError("canonical request required")
        existing = self._outcomes.get(request.idempotency_key)
        if existing is not None:
            if existing.terminal.request_id == request.request_id:
                return existing
            return self._terminal(request, "idempotency_conflict")
        terminal = evaluate_eligibility(request, policy, approval, reference, summary, now)
        if terminal is not None:
            outcome = self._terminal(request, terminal.reason)
        elif credential is None:
            outcome = self._terminal(request, "policy_blocked")
        else:
            try:
                render_redacted_body(request, reference, summary, facts)
            except ValueError:
                outcome = self._terminal(request, "policy_blocked")
            else:
                # Metadata lineage is not a source/patch materialization authority.
                outcome = self._terminal(request, "materialization_unavailable")
        self._outcomes[request.idempotency_key] = outcome
        return outcome
