"""Fixture-only GitHub mutation orchestration with an injected provider seam."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from typing import Protocol

from .models import RealMutationPDR, RealMutationRequest
from .fixture_registry import FIXTURE_TARGET_FILE_ID, FIXTURE_TARGET_PATH


_REPOSITORY_ID = "1300511729"
_BASE_SHA = "97c8220cd713ebf61124ac2de2f3eadc6e4dc222"
_MINT_CAPABILITY = object()
_COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_PROVIDER_FAILURE_CODES = frozenset(("credential_rejected", "rate_limited", "provider_rejected", "provider_unavailable"))


class FixtureGitHubProvider(Protocol):
    """Only this seam may later speak to the GitHub provider."""

    def read_base_sha(self) -> str: ...
    def find_by_idempotency_key(self, key: str) -> tuple[str, str | None, str | None] | None:
        """Find the deterministic branch even when no commit or PR exists yet."""
    def create_branch(self, branch_name: str, base_sha: str) -> str: ...
    def create_commit(self, branch_name: str, target_path: str, content: bytes, message: str) -> str: ...
    def create_draft_pr(self, branch_name: str, base_branch: str, title: str, body: str) -> str: ...


class EphemeralMutationPayload:
    """Harness-private bytes; never a contract, log field, or provider identity."""

    __slots__ = ("payload_id", "payload_digest", "target_file_id", "_content", "destroyed")

    def __init__(self, capability: object, payload_id: str, payload_digest: str, target_file_id: str, content: bytes) -> None:
        if capability is not _MINT_CAPABILITY:
            raise TypeError("real mutation payload may only be minted by the harness")
        self.payload_id = payload_id
        self.payload_digest = payload_digest
        self.target_file_id = target_file_id
        self._content = content
        self.destroyed = False

    @property
    def content_for_provider(self) -> bytes:
        if self.destroyed:
            raise ValueError("ephemeral mutation payload is destroyed")
        return self._content

    def destroy(self) -> None:
        self._content = b""
        self.destroyed = True

    def __getstate__(self) -> object:
        raise TypeError("ephemeral mutation payload cannot be serialized")

    def __reduce__(self) -> object:
        raise TypeError("ephemeral mutation payload cannot be serialized")


def _mint_ephemeral_payload(payload_id: str, payload_digest: str, target_file_id: str, content: bytes) -> EphemeralMutationPayload:
    """Private runtime seam; tests model the harness through this function."""
    if not isinstance(content, bytes) or "sha256:" + hashlib.sha256(content).hexdigest() != payload_digest:
        raise ValueError("payload content does not match its digest")
    return EphemeralMutationPayload(_MINT_CAPABILITY, payload_id, payload_digest, target_file_id, content)


@dataclass(frozen=True, slots=True)
class RealMutationResult:
    """Durable references and controlled outcome only; never payload bytes or paths."""

    outcome: str
    branch_name: str | None = None
    commit_sha: str | None = None
    draft_pr_number: str | None = None
    automatic_retries: int = 0
    provider_failure_code: str | None = None

    def __post_init__(self) -> None:
        if self.outcome not in {"draft_pr_created", "reconciled", "base_revision_mismatch", "not_authorized", "ambiguous_result", "provider_failed"}:
            raise ValueError("result outcome must be controlled")
        if self.automatic_retries != 0:
            raise ValueError("automatic retries are prohibited")
        if self.outcome == "provider_failed" and self.provider_failure_code not in _PROVIDER_FAILURE_CODES:
            raise ValueError("provider failure requires a controlled code")
        if self.outcome != "provider_failed" and self.provider_failure_code is not None:
            raise ValueError("provider failure code is exclusive to provider failure")
        if self.provider_failure_code is not None and self.provider_failure_code not in _PROVIDER_FAILURE_CODES:
            raise ValueError("provider failure code must be controlled")


class FixtureGitHubMutationAdapter:
    """Fail-closed mutation boundary for the sole registered fixture scenario."""

    def __init__(self, provider: FixtureGitHubProvider) -> None:
        self._provider = provider
        self._claimed_keys: set[str] = set()

    def execute(self, request: RealMutationRequest, pdr: RealMutationPDR, payload: EphemeralMutationPayload, *, now: int) -> RealMutationResult:
        try:
            if not self._authorized(request, pdr, payload, now):
                return RealMutationResult("not_authorized")
            if self._provider.read_base_sha() != _BASE_SHA:
                return RealMutationResult("base_revision_mismatch")
            branch_name = "forgeflow-governed-change-" + request.idempotency_key[7:19]
            existing = self._provider.find_by_idempotency_key(request.idempotency_key)
            if existing is not None:
                branch, commit, pr_number = existing
                if branch != branch_name or commit is None or pr_number is None or not _COMMIT_SHA.fullmatch(commit) or not pr_number.isdecimal():
                    return RealMutationResult("ambiguous_result")
                return RealMutationResult("reconciled", branch, commit, pr_number)
            if request.idempotency_key in self._claimed_keys:
                return RealMutationResult("ambiguous_result")
            # Claim before the provider call: a transport failure can occur after
            # the remote ref was created, and retrying that uncertainty is unsafe.
            self._claimed_keys.add(request.idempotency_key)
            if self._provider.create_branch(branch_name, _BASE_SHA) != branch_name:
                return RealMutationResult("ambiguous_result")
            commit = self._provider.create_commit(branch_name, FIXTURE_TARGET_PATH, payload.content_for_provider, "fix: correct calculator addition")
            if not _COMMIT_SHA.fullmatch(commit):
                return RealMutationResult("ambiguous_result")
            pr_number = self._provider.create_draft_pr(branch_name, "main", "Fix calculator addition bug", "Closes #1.\n\nAutomated fixture-only draft PR.")
            if not pr_number.isdecimal():
                return RealMutationResult("ambiguous_result")
            return RealMutationResult("draft_pr_created", branch_name, commit, pr_number)
        except Exception as error:
            candidate = getattr(error, "code", None)
            code = candidate if isinstance(candidate, str) and candidate in _PROVIDER_FAILURE_CODES else "provider_unavailable"
            return RealMutationResult("provider_failed", provider_failure_code=code)
        finally:
            if isinstance(payload, EphemeralMutationPayload):
                payload.destroy()

    @staticmethod
    def _authorized(request: object, pdr: object, payload: object, now: int) -> bool:
        if not isinstance(request, RealMutationRequest) or not isinstance(pdr, RealMutationPDR) or not isinstance(payload, EphemeralMutationPayload):
            return False
        if payload.destroyed or payload.target_file_id != FIXTURE_TARGET_FILE_ID or not pdr.is_fresh_at(now):
            return False
        if (request.repository_id, request.base_sha, request.payload_id, request.payload_digest, request.idempotency_key, request.real_mutation_pdr_id) != (
            _REPOSITORY_ID, _BASE_SHA, pdr.payload_id, pdr.payload_digest, pdr.idempotency_key, pdr.pdr_id
        ):
            return False
        return (payload.payload_id, payload.payload_digest) == (pdr.payload_id, pdr.payload_digest)
