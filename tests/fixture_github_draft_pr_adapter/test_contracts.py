import unittest
from dataclasses import FrozenInstanceError

from forgeflow.governed_changes.draft_pr.models import DraftPRRequest, PRTerminal, IdempotencyRecord, PRResult, BASE_REVISION, ISSUE_ID, ISSUE_NUMBER, PROFILE_ID, PROFILE_VERSION, REPOSITORY_IDENTITY
from forgeflow.governed_changes.draft_pr.canonical import request_id_for, idempotency_record_id_for, pr_result_id_for

D = "sha256:" + "a" * 64


class ContractTests(unittest.TestCase):
    def _request(self):
        return DraftPRRequest.create("run-0001", D, D, D, D, "idempotency-001")
    def test_request_is_frozen_fixture_bound_and_payload_free(self):
        value = self._request()
        with self.assertRaises(FrozenInstanceError):
            value.run_id = "run-0002"
        self.assertFalse(hasattr(value, "credential"))
        self.assertFalse(hasattr(value, "source"))

    def test_rejects_unregistered_lineage_and_unsafe_idempotency(self):
        with self.assertRaises(ValueError):
            DraftPRRequest("v", D, "run-0001", REPOSITORY_IDENTITY, ISSUE_ID, ISSUE_NUMBER, BASE_REVISION, PROFILE_ID, PROFILE_VERSION, D, D, D, D, "idempotency-001")
        with self.assertRaises(ValueError):
            DraftPRRequest("forgeflow.fixture-draft-pr.v1", D, "run/source", REPOSITORY_IDENTITY, ISSUE_ID, ISSUE_NUMBER, BASE_REVISION, PROFILE_ID, PROFILE_VERSION, D, D, D, D, "idempotency-001")
        with self.assertRaises(ValueError):
            PRTerminal("forgeflow.fixture-draft-pr.v1", D, D, "retrying")

    def test_idempotency_and_result_are_immutable_canonical_facts(self):
        request = self._request()
        from dataclasses import replace
        record = IdempotencyRecord.create(request.request_id, "idempotency-001", "pending")
        terminal = PRTerminal.create(request.request_id, "policy_blocked")
        result = PRResult.create_no_effect(request.request_id, record.record_id, terminal.terminal_id)
        created = PRResult.create_draft_pr(
            request.request_id,
            record.record_id,
            "forgeflow-m4-fixture-001",
            "a" * 40,
            "draft-pr-001",
        )
        self.assertEqual(record.record_id, idempotency_record_id_for(record))
        self.assertEqual(result.result_id, pr_result_id_for(result))
        self.assertEqual(created.result_id, pr_result_id_for(created))
        with self.assertRaises(FrozenInstanceError):
            result.outcome = "draft_pr_created"

    def test_result_rejects_unbounded_or_sensitive_external_references(self):
        request = self._request()
        record = IdempotencyRecord.create(request.request_id, "idempotency-001", "pending")
        with self.assertRaises(ValueError):
            PRResult.create_no_effect(request.request_id, record.record_id, "token=secret")
        with self.assertRaises(ValueError):
            PRResult.create_draft_pr(request.request_id, record.record_id, "branch/raw-source", "a" * 40, "draft-pr-001")
        with self.assertRaises(ValueError):
            PRResult.create_draft_pr(request.request_id, record.record_id, "forgeflow-m4-fixture-001", "a" * 39, "draft-pr-001")
        with self.assertRaises(ValueError):
            PRResult.create_draft_pr(request.request_id, record.record_id, "forgeflow-m4-fixture-001", "a" * 40, "x" * 65)
