from dataclasses import dataclass
import re

SCHEMA_VERSION = "forgeflow.fixture-draft-pr.v1"
REPOSITORY_IDENTITY = "soulbooyy-forgeflow-m4-fixture-1300511729"
ISSUE_ID = "4883496432"
ISSUE_NUMBER = 1
BASE_REVISION = "97c8220cd713ebf61124ac2de2f3eadc6e4dc222"
PROFILE_ID = "forgeflow-m4-fixture-only"
PROFILE_VERSION = "1.0.0"
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{2,63}$")
_COMMIT_ID = re.compile(r"^[0-9a-f]{40}$")
_TERMINALS = frozenset(("policy_blocked", "approval_required", "idempotency_conflict", "ambiguous_result"))


def _digest(value: object) -> None:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise ValueError("digest required")


def _identifier(value: object) -> None:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ValueError("bounded identifier required")


def _commit(value: object) -> None:
    if not isinstance(value, str) or not _COMMIT_ID.fullmatch(value):
        raise ValueError("commit sha required")


@dataclass(frozen=True, slots=True)
class DraftPRRequest:
    schema_version: str
    request_id: str
    run_id: str
    repository_identity: str
    issue_id: str
    issue_number: int
    base_revision: str
    profile_id: str
    profile_version: str
    policy_decision_id: str
    approval_decision_id: str
    artifact_reference_id: str
    durable_summary_id: str
    idempotency_key: str

    @classmethod
    def create(cls, run_id, policy_decision_id, approval_decision_id, artifact_reference_id, durable_summary_id, idempotency_key):
        from .canonical import request_id_for
        provisional = object.__new__(cls)
        for name, value in (("schema_version", SCHEMA_VERSION), ("request_id", "sha256:" + "0" * 64), ("run_id", run_id), ("repository_identity", REPOSITORY_IDENTITY), ("issue_id", ISSUE_ID), ("issue_number", ISSUE_NUMBER), ("base_revision", BASE_REVISION), ("profile_id", PROFILE_ID), ("profile_version", PROFILE_VERSION), ("policy_decision_id", policy_decision_id), ("approval_decision_id", approval_decision_id), ("artifact_reference_id", artifact_reference_id), ("durable_summary_id", durable_summary_id), ("idempotency_key", idempotency_key)):
            object.__setattr__(provisional, name, value)
        return cls(SCHEMA_VERSION, request_id_for(provisional), run_id, REPOSITORY_IDENTITY, ISSUE_ID, ISSUE_NUMBER, BASE_REVISION, PROFILE_ID, PROFILE_VERSION, policy_decision_id, approval_decision_id, artifact_reference_id, durable_summary_id, idempotency_key)

    def __post_init__(self) -> None:
        if (self.schema_version != SCHEMA_VERSION or self.repository_identity != REPOSITORY_IDENTITY or self.issue_id != ISSUE_ID or self.issue_number != ISSUE_NUMBER or self.base_revision != BASE_REVISION or self.profile_id != PROFILE_ID or self.profile_version != PROFILE_VERSION):
            raise ValueError("unsupported schema")
        _digest(self.request_id)
        _identifier(self.run_id)
        for value in (self.policy_decision_id, self.approval_decision_id, self.artifact_reference_id, self.durable_summary_id):
            _digest(value)
        _identifier(self.idempotency_key)
        from .canonical import request_id_for
        if self.request_id != request_id_for(self):
            raise ValueError("noncanonical request id")


@dataclass(frozen=True, slots=True)
class FixturePolicyDecisionRecord:
    """Canonical, request-bindable allowed-policy fact for the fixture only."""

    schema_version: str
    policy_decision_id: str
    repository_identity: str
    base_revision: str
    profile_id: str
    profile_version: str
    artifact_reference_id: str
    approval_decision_id: str
    idempotency_key: str
    outcome: str
    expires_at: int

    @classmethod
    def create(cls, artifact_reference_id, approval_decision_id, idempotency_key, outcome, expires_at):
        from .canonical import policy_decision_id_for
        provisional = object.__new__(cls)
        for name, value in (("schema_version", SCHEMA_VERSION), ("policy_decision_id", "sha256:" + "0" * 64), ("repository_identity", REPOSITORY_IDENTITY), ("base_revision", BASE_REVISION), ("profile_id", PROFILE_ID), ("profile_version", PROFILE_VERSION), ("artifact_reference_id", artifact_reference_id), ("approval_decision_id", approval_decision_id), ("idempotency_key", idempotency_key), ("outcome", outcome), ("expires_at", expires_at)):
            object.__setattr__(provisional, name, value)
        return cls(SCHEMA_VERSION, policy_decision_id_for(provisional), REPOSITORY_IDENTITY, BASE_REVISION, PROFILE_ID, PROFILE_VERSION, artifact_reference_id, approval_decision_id, idempotency_key, outcome, expires_at)

    def __post_init__(self) -> None:
        if (self.schema_version != SCHEMA_VERSION or self.repository_identity != REPOSITORY_IDENTITY or self.base_revision != BASE_REVISION or self.profile_id != PROFILE_ID or self.profile_version != PROFILE_VERSION or self.outcome not in ("allowed", "blocked", "requires_human_approval") or type(self.expires_at) is not int or self.expires_at <= 0):
            raise ValueError("invalid fixture policy decision")
        for value in (self.policy_decision_id, self.artifact_reference_id, self.approval_decision_id):
            _digest(value)
        _identifier(self.idempotency_key)
        from .canonical import policy_decision_id_for
        if self.policy_decision_id != policy_decision_id_for(self):
            raise ValueError("noncanonical policy decision id")


@dataclass(frozen=True, slots=True)
class PRTerminal:
    schema_version: str
    terminal_id: str
    request_id: str
    reason: str
    @classmethod
    def create(cls, request_id, reason):
        from .canonical import terminal_id_for
        provisional=object.__new__(cls)
        for name,value in (("schema_version",SCHEMA_VERSION),("terminal_id","sha256:"+"0"*64),("request_id",request_id),("reason",reason)): object.__setattr__(provisional,name,value)
        return cls(SCHEMA_VERSION,terminal_id_for(provisional),request_id,reason)

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("unsupported schema")
        _digest(self.terminal_id); _digest(self.request_id)
        if self.reason not in _TERMINALS:
            raise ValueError("unsupported terminal")
        from .canonical import terminal_id_for
        if self.terminal_id != terminal_id_for(self): raise ValueError("noncanonical terminal id")


@dataclass(frozen=True, slots=True)
class IdempotencyRecord:
    schema_version: str
    record_id: str
    request_id: str
    idempotency_key: str
    state: str
    @classmethod
    def create(cls, request_id, idempotency_key, state):
        from .canonical import idempotency_record_id_for
        provisional=object.__new__(cls)
        for name,value in (("schema_version",SCHEMA_VERSION),("record_id","sha256:"+"0"*64),("request_id",request_id),("idempotency_key",idempotency_key),("state",state)): object.__setattr__(provisional,name,value)
        return cls(SCHEMA_VERSION,idempotency_record_id_for(provisional),request_id,idempotency_key,state)
    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION or self.state not in ("pending", "reconciled", "terminal"):
            raise ValueError("invalid idempotency record")
        _digest(self.record_id); _digest(self.request_id); _identifier(self.idempotency_key)
        from .canonical import idempotency_record_id_for
        if self.record_id != idempotency_record_id_for(self): raise ValueError("noncanonical record id")


@dataclass(frozen=True, slots=True)
class PRResult:
    schema_version: str
    result_id: str
    request_id: str
    idempotency_record_id: str
    outcome: str
    branch_id: str | None
    commit_id: str | None
    draft_pr_id: str | None
    terminal_id: str | None
    @classmethod
    def create_no_effect(cls, request_id, idempotency_record_id, terminal_id):
        from .canonical import pr_result_id_for
        provisional=object.__new__(cls)
        for name,value in (("schema_version",SCHEMA_VERSION),("result_id","sha256:"+"0"*64),("request_id",request_id),("idempotency_record_id",idempotency_record_id),("outcome","no_effect"),("branch_id",None),("commit_id",None),("draft_pr_id",None),("terminal_id",terminal_id)): object.__setattr__(provisional,name,value)
        return cls(SCHEMA_VERSION,pr_result_id_for(provisional),request_id,idempotency_record_id,"no_effect",None,None,None,terminal_id)

    @classmethod
    def create_draft_pr(cls, request_id, idempotency_record_id, branch_id, commit_id, draft_pr_id):
        from .canonical import pr_result_id_for
        provisional = object.__new__(cls)
        for name, value in (("schema_version", SCHEMA_VERSION), ("result_id", "sha256:" + "0" * 64), ("request_id", request_id), ("idempotency_record_id", idempotency_record_id), ("outcome", "draft_pr_created"), ("branch_id", branch_id), ("commit_id", commit_id), ("draft_pr_id", draft_pr_id), ("terminal_id", None)):
            object.__setattr__(provisional, name, value)
        return cls(SCHEMA_VERSION, pr_result_id_for(provisional), request_id, idempotency_record_id, "draft_pr_created", branch_id, commit_id, draft_pr_id, None)
    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION or self.outcome not in ("draft_pr_created", "no_effect"):
            raise ValueError("invalid pr result")
        _digest(self.result_id); _digest(self.request_id); _digest(self.idempotency_record_id)
        if self.outcome == "draft_pr_created":
            if self.terminal_id is not None:
                raise ValueError("created result requires bounded external references")
            _identifier(self.branch_id)
            _commit(self.commit_id)
            _identifier(self.draft_pr_id)
        else:
            if self.terminal_id is None or any(value is not None for value in (self.branch_id, self.commit_id, self.draft_pr_id)):
                raise ValueError("no-effect result requires terminal only")
            _digest(self.terminal_id)
        from .canonical import pr_result_id_for
        if self.result_id != pr_result_id_for(self): raise ValueError("noncanonical result id")
