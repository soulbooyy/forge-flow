from dataclasses import replace
import unittest

from forgeflow.fixture_github_draft_pr_adapter.models import DraftPRRequest, IdempotencyRecord, PRTerminal, PRResult
from forgeflow.fixture_github_draft_pr_adapter.canonical import request_id_for, terminal_id_for, idempotency_record_id_for, pr_result_id_for

D = "sha256:" + "a" * 64


class CanonicalTests(unittest.TestCase):
    def test_every_identity_is_fixed_point_and_rejects_forgery(self):
        request = DraftPRRequest.create("run-0001", D, D, D, D, "idempotency-001")
        terminal = PRTerminal.create(request.request_id, "policy_blocked")
        record = IdempotencyRecord.create(request.request_id, "idempotency-001", "pending")
        result = PRResult.create_no_effect(request.request_id, record.record_id, terminal.terminal_id)
        created = PRResult.create_draft_pr(request.request_id, record.record_id, "forgeflow-m4-fixture-001", "a" * 40, "draft-pr-001")
        for value, helper, field in ((request, request_id_for, "request_id"), (terminal, terminal_id_for, "terminal_id"), (record, idempotency_record_id_for, "record_id"), (result, pr_result_id_for, "result_id"), (created, pr_result_id_for, "result_id")):
            self.assertEqual(getattr(value, field), helper(value))
            with self.assertRaises(ValueError):
                value.__class__(**{**{name:getattr(value,name) for name in value.__dataclass_fields__}, field:D})
