from __future__ import annotations

import hashlib
import unittest

from forgeflow.governed_changes.real_mutation.github_adapter import (
    FixtureGitHubMutationAdapter,
    FixtureGitHubProvider,
    _mint_ephemeral_payload,
)
from forgeflow.governed_changes.real_mutation.github_cli import GhProviderFailure
from forgeflow.governed_changes.real_mutation.models import RealMutationPDR, RealMutationRequest


class FakeProvider(FixtureGitHubProvider):
    def __init__(self, base_sha: str) -> None:
        self.base_sha = base_sha
        self.existing = None
        self.branch_result = None
        self.branch_side_effect = False
        self.commit_failure = False
        self.created: list[str] = []

    def read_base_sha(self) -> str:
        return self.base_sha

    def find_by_idempotency_key(self, key: str):
        return self.existing

    def create_branch(self, branch_name: str, base_sha: str) -> str:
        self.created.append("branch")
        if self.branch_side_effect:
            self.existing = (branch_name, None, None)
        return self.branch_result or branch_name

    def create_commit(self, branch_name: str, target_path: str, content: bytes, message: str) -> str:
        self.created.append("commit")
        self.asserted = (branch_name, target_path, content, message)
        if self.commit_failure:
            self.existing = (branch_name, None, None)
            raise RuntimeError("injected commit failure")
        return "a" * 40

    def create_draft_pr(self, branch_name: str, base_branch: str, title: str, body: str) -> str:
        self.created.append("draft_pr")
        return "42"


class FixtureGitHubMutationAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.base_sha = "97c8220cd713ebf61124ac2de2f3eadc6e4dc222"
        self.payload_bytes = b"def add(left, right):\n    return left + right\n"
        self.payload_id = "sha256:" + "a" * 64
        self.payload_digest = "sha256:" + hashlib.sha256(self.payload_bytes).hexdigest()
        self.key = "sha256:" + "c" * 64
        self.pdr = RealMutationPDR.create(
            attempt_id="real-mutation-2", issued_at=10, expires_at=20,
            repository_id="1300511729", base_sha=self.base_sha,
            payload_id=self.payload_id, payload_digest=self.payload_digest,
            idempotency_key=self.key,
        )
        self.request = RealMutationRequest.create(self.pdr, now=10)

    def test_allowed_request_creates_exactly_one_branch_commit_and_draft_pr(self):
        provider = FakeProvider(self.base_sha)
        payload = _mint_ephemeral_payload(self.payload_id, self.payload_digest, "fixture-calculator-v1", self.payload_bytes)

        result = FixtureGitHubMutationAdapter(provider).execute(self.request, self.pdr, payload, now=10)

        self.assertEqual(provider.created, ["branch", "commit", "draft_pr"])
        self.assertEqual(result.outcome, "draft_pr_created")
        self.assertEqual(result.commit_sha, "a" * 40)
        self.assertTrue(payload.destroyed)

    def test_replay_reconciles_without_new_external_writes(self):
        provider = FakeProvider(self.base_sha)
        provider.existing = ("forgeflow-governed-change-" + self.key[7:19], "a" * 40, "42")
        payload = _mint_ephemeral_payload(self.payload_id, self.payload_digest, "fixture-calculator-v1", self.payload_bytes)

        result = FixtureGitHubMutationAdapter(provider).execute(self.request, self.pdr, payload, now=10)

        self.assertEqual(provider.created, [])
        self.assertEqual(result.outcome, "reconciled")
        self.assertTrue(payload.destroyed)

    def test_stale_base_fails_before_provider_write(self):
        provider = FakeProvider("b" * 40)
        payload = _mint_ephemeral_payload(self.payload_id, self.payload_digest, "fixture-calculator-v1", self.payload_bytes)

        result = FixtureGitHubMutationAdapter(provider).execute(self.request, self.pdr, payload, now=10)

        self.assertEqual(provider.created, [])
        self.assertEqual(result.outcome, "base_revision_mismatch")
        self.assertTrue(payload.destroyed)

    def test_expired_or_payload_mismatch_is_rejected_before_provider_write(self):
        provider = FakeProvider(self.base_sha)
        expired = RealMutationPDR.create(
            attempt_id="real-mutation-3", issued_at=10, expires_at=11,
            repository_id="1300511729", base_sha=self.base_sha,
            payload_id=self.payload_id, payload_digest=self.payload_digest,
            idempotency_key=self.key,
        )
        expired_request = RealMutationRequest.create(expired, now=10)
        payload = _mint_ephemeral_payload(self.payload_id, self.payload_digest, "fixture-calculator-v1", self.payload_bytes)

        result = FixtureGitHubMutationAdapter(provider).execute(expired_request, expired, payload, now=11)

        self.assertEqual(provider.created, [])
        self.assertEqual(result.outcome, "not_authorized")
        self.assertTrue(payload.destroyed)

    def test_partial_reconciliation_is_ambiguous_and_never_retries_a_write(self):
        provider = FakeProvider(self.base_sha)
        provider.existing = ("forgeflow-governed-change-" + self.key[7:19], None, None)
        payload = _mint_ephemeral_payload(self.payload_id, self.payload_digest, "fixture-calculator-v1", self.payload_bytes)

        result = FixtureGitHubMutationAdapter(provider).execute(self.request, self.pdr, payload, now=10)

        self.assertEqual(provider.created, [])
        self.assertEqual(result.outcome, "ambiguous_result")
        self.assertTrue(payload.destroyed)

    def test_unexpected_branch_response_stops_before_commit(self):
        provider = FakeProvider(self.base_sha)
        provider.branch_result = "unexpected-branch"
        provider.branch_side_effect = True
        adapter = FixtureGitHubMutationAdapter(provider)
        payload = _mint_ephemeral_payload(self.payload_id, self.payload_digest, "fixture-calculator-v1", self.payload_bytes)

        result = adapter.execute(self.request, self.pdr, payload, now=10)
        retry_payload = _mint_ephemeral_payload(self.payload_id, self.payload_digest, "fixture-calculator-v1", self.payload_bytes)
        retry = FixtureGitHubMutationAdapter(provider).execute(self.request, self.pdr, retry_payload, now=10)

        self.assertEqual(provider.created, ["branch"])
        self.assertEqual(result.outcome, "ambiguous_result")
        self.assertEqual(retry.outcome, "ambiguous_result")
        self.assertTrue(payload.destroyed)
        self.assertTrue(retry_payload.destroyed)

    def test_fault_after_branch_claim_blocks_retry_without_new_write(self):
        provider = FakeProvider(self.base_sha)
        provider.commit_failure = True
        adapter = FixtureGitHubMutationAdapter(provider)
        first_payload = _mint_ephemeral_payload(self.payload_id, self.payload_digest, "fixture-calculator-v1", self.payload_bytes)

        first = adapter.execute(self.request, self.pdr, first_payload, now=10)
        retry_payload = _mint_ephemeral_payload(self.payload_id, self.payload_digest, "fixture-calculator-v1", self.payload_bytes)
        retry = adapter.execute(self.request, self.pdr, retry_payload, now=10)

        self.assertEqual(first.outcome, "provider_failed")
        self.assertEqual(retry.outcome, "ambiguous_result")
        self.assertEqual(provider.created, ["branch", "commit"])
        self.assertTrue(first_payload.destroyed)
        self.assertTrue(retry_payload.destroyed)

    def test_provider_failure_retains_only_controlled_code(self):
        class RejectedProvider(FakeProvider):
            def create_branch(self, branch_name: str, base_sha: str) -> str:
                raise GhProviderFailure("provider_rejected")

        payload = _mint_ephemeral_payload(self.payload_id, self.payload_digest, "fixture-calculator-v1", self.payload_bytes)
        result = FixtureGitHubMutationAdapter(RejectedProvider(self.base_sha)).execute(self.request, self.pdr, payload, now=10)

        self.assertEqual(result.outcome, "provider_failed")
        self.assertEqual(result.provider_failure_code, "provider_rejected")
        self.assertTrue(payload.destroyed)

    def test_unknown_provider_code_is_normalized_fail_closed(self):
        class ForgedProvider(FakeProvider):
            def create_branch(self, branch_name: str, base_sha: str) -> str:
                error = RuntimeError()
                error.code = "untrusted-value"  # type: ignore[attr-defined]
                raise error

        payload = _mint_ephemeral_payload(self.payload_id, self.payload_digest, "fixture-calculator-v1", self.payload_bytes)
        result = FixtureGitHubMutationAdapter(ForgedProvider(self.base_sha)).execute(self.request, self.pdr, payload, now=10)

        self.assertEqual((result.outcome, result.provider_failure_code), ("provider_failed", "branch_create_failed"))
        self.assertTrue(payload.destroyed)

    def test_unhashable_provider_code_is_normalized_fail_closed(self):
        class ForgedProvider(FakeProvider):
            def create_branch(self, branch_name: str, base_sha: str) -> str:
                error = RuntimeError()
                error.code = []  # type: ignore[attr-defined]
                raise error

        payload = _mint_ephemeral_payload(self.payload_id, self.payload_digest, "fixture-calculator-v1", self.payload_bytes)
        result = FixtureGitHubMutationAdapter(ForgedProvider(self.base_sha)).execute(self.request, self.pdr, payload, now=10)

        self.assertEqual((result.outcome, result.provider_failure_code), ("provider_failed", "branch_create_failed"))


if __name__ == "__main__":
    unittest.main()
