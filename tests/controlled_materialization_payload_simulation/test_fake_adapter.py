from __future__ import annotations

import unittest

from forgeflow.controlled_materialization_payload_simulation.fake_adapter import FakeGitDataAdapter, reject_real_mutation_input
from forgeflow.controlled_materialization_payload_simulation.models import PayloadEligibilityPDR
from forgeflow.controlled_materialization_payload_simulation.service import EphemeralPayloadLease
from tests.controlled_materialization_payload_simulation.test_contracts import FACT_A, FACT_B, OUTPUT_DIGEST, REPOSITORY_ID, BASE_SHA, materialization_pdr


class FakeAdapterTest(unittest.TestCase):
    def payload_and_pdr(self):
        from forgeflow.controlled_materialization_payload_simulation.models import MaterializedCommitPayload
        payload = MaterializedCommitPayload.create(repository_id=REPOSITORY_ID, base_sha=BASE_SHA, snapshot_digest="sha256:" + "a" * 64, transformation_id="fixture-transform-v1", transformation_version="1", target_file_id="fixture-test-file-v1", input_digest="sha256:" + "b" * 64, output_digest=OUTPUT_DIGEST, materialization_pdr_id=materialization_pdr().pdr_id, security_fact_ids=(FACT_A,), validation_fact_id=FACT_B, review_fact_ids=())
        pdr = PayloadEligibilityPDR.create(attempt_id="eligibility-1", issued_at=10, expires_at=11, repository_id=REPOSITORY_ID, base_sha=BASE_SHA, payload_id=payload.payload_id, output_digest=payload.output_digest, security_fact_ids=payload.security_fact_ids, validation_fact_id=payload.validation_fact_id, review_fact_ids=payload.review_fact_ids, materialization_pdr_id=payload.materialization_pdr_id)
        return payload, pdr

    def test_replay_is_deterministic_and_real_surface_rejects_simulation_identity(self):
        payload, pdr = self.payload_and_pdr()
        adapter = FakeGitDataAdapter()
        first_lease, second_lease = EphemeralPayloadLease.for_test(b"x"), EphemeralPayloadLease.for_test(b"x")
        adapter._bind_for_harness(first_lease.handle, payload, pdr)
        adapter._bind_for_harness(second_lease.handle, payload, pdr)
        first = adapter.simulate(first_lease.handle, payload, pdr, now=10)
        second = adapter.simulate(second_lease.handle, payload, pdr, now=10)
        self.assertEqual(first, second)
        self.assertTrue(first.commit_id.startswith("forgeflow-sim-commit-"))
        with self.assertRaises(ValueError): reject_real_mutation_input(first.commit_id)
        with self.assertRaises(ValueError): reject_real_mutation_input(materialization_pdr())
        self.assertFalse(first_lease.handle.is_live)
        stale = adapter.simulate(EphemeralPayloadLease.for_test(b"x").handle, payload, pdr, now=11)
        self.assertEqual(stale.reason, "simulation_binding_failed")
