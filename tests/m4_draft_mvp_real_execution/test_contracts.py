from __future__ import annotations

import unittest

from forgeflow.controlled_materialization_payload_simulation.models import MaterializationPDR
from forgeflow.m4_draft_mvp_real_execution.models import RealMutationPDR, RealMutationRequest, RealMutationTerminal


class RealMutationContractsTest(unittest.TestCase):
    def pdr(self):
        return RealMutationPDR.create(
            attempt_id="real-mutation-1", issued_at=10, expires_at=11,
            repository_id="1300511729", base_sha="97c8220cd713ebf61124ac2de2f3eadc6e4dc222",
            payload_id="sha256:" + "a" * 64, payload_digest="sha256:" + "b" * 64,
            idempotency_key="sha256:" + "c" * 64,
        )

    def test_fresh_real_mutation_pdr_is_independent_and_exact(self):
        pdr = self.pdr()
        self.assertEqual(pdr.authority_kind, "real_mutation")
        self.assertTrue(pdr.is_fresh_at(10))
        self.assertFalse(pdr.is_fresh_at(11))

    def test_request_rejects_v1_authority_and_simulation_identity_before_adapter(self):
        request = RealMutationRequest.create(self.pdr(), now=10)
        self.assertEqual(request.repository_id, "1300511729")
        with self.assertRaises(ValueError):
            RealMutationRequest.create(MaterializationPDR.create(
                attempt_id="m-1", issued_at=1, expires_at=2, repository_id="1300511729",
                base_sha="97c8220cd713ebf61124ac2de2f3eadc6e4dc222", snapshot_digest="sha256:" + "d" * 64,
                transformation_id="fixture-transform-v1", transformation_version="1", target_file_id="fixture-test-file-v1",
                expected_input_digest="sha256:" + "e" * 64, profile_id="forgeflow-m4-fixture-only", profile_version="1.0.0"), now=10)
        with self.assertRaises(ValueError):
            RealMutationRequest.from_fields("1300511729", "97c8220cd713ebf61124ac2de2f3eadc6e4dc222", "forgeflow-sim-commit-x", "sha256:" + "b" * 64, "sha256:" + "c" * 64)

    def test_terminal_is_bounded_and_non_authorizing(self):
        terminal = RealMutationTerminal.create("real_mutation_rejected", "real-mutation-1", "simulation_identity")
        self.assertEqual(terminal.automatic_retries, 0)


if __name__ == "__main__":
    unittest.main()
