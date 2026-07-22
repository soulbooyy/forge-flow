from __future__ import annotations

from dataclasses import replace
import json
import unittest

from forgeflow.governed_changes.materialization.canonical import (
    materialization_pdr_id_for,
    materialized_payload_id_for,
    payload_eligibility_pdr_id_for,
)
from forgeflow.governed_changes.materialization.models import (
    EphemeralPayloadHandle,
    MaterializationPDR,
    MaterializationTerminal,
    MaterializedCommitPayload,
    PayloadEligibilityPDR,
    TransformationManifest,
    _mint_ephemeral_handle,
)


REPOSITORY_ID = "1300511729"
BASE_SHA = "97c8220cd713ebf61124ac2de2f3eadc6e4dc222"
SNAPSHOT_DIGEST = "sha256:" + "a" * 64
INPUT_DIGEST = "sha256:" + "b" * 64
OUTPUT_DIGEST = "sha256:" + "c" * 64
FACT_A = "sha256:" + "d" * 64
FACT_B = "sha256:" + "e" * 64


def materialization_pdr() -> MaterializationPDR:
    return MaterializationPDR.create(
        attempt_id="attempt-materialization-1",
        issued_at=10,
        expires_at=11,
        repository_id=REPOSITORY_ID,
        base_sha=BASE_SHA,
        snapshot_digest=SNAPSHOT_DIGEST,
        transformation_id="fixture-transform-v1",
        transformation_version="1",
        target_file_id="fixture-test-file-v1",
        expected_input_digest=INPUT_DIGEST,
        profile_id="forgeflow-m4-fixture-only",
        profile_version="1.0.0",
    )


class ContractsTest(unittest.TestCase):
    def test_manifest_only_accepts_registered_selector_shape(self) -> None:
        manifest = TransformationManifest("fixture-transform-v1", "1", "fixture-test-file-v1", INPUT_DIGEST)
        self.assertEqual(manifest.transformation_id, "fixture-transform-v1")
        with self.assertRaises(TypeError):
            TransformationManifest("fixture-transform-v1", "1", "fixture-test-file-v1", INPUT_DIGEST, "/tmp/source")
        with self.assertRaises(ValueError):
            TransformationManifest("fixture-transform-v1", "1", "fixture-test-file-v1", "not-a-digest")

    def test_materialization_pdr_is_self_identifying_exact_and_fresh(self) -> None:
        pdr = materialization_pdr()
        self.assertEqual(pdr.pdr_id, materialization_pdr_id_for(pdr))
        self.assertTrue(pdr.is_fresh_at(10))
        self.assertFalse(pdr.is_fresh_at(11))
        with self.assertRaises(ValueError):
            replace(pdr, authority_kind="real_mutation")
        with self.assertRaises(ValueError):
            replace(pdr, expires_at=10)
        with self.assertRaises(ValueError):
            replace(pdr, pdr_id="sha256:" + "0" * 64)

    def test_payload_identity_is_self_excluding_and_has_no_bytes_or_path(self) -> None:
        pdr = materialization_pdr()
        payload = MaterializedCommitPayload.create(
            repository_id=REPOSITORY_ID,
            base_sha=BASE_SHA,
            snapshot_digest=SNAPSHOT_DIGEST,
            transformation_id="fixture-transform-v1",
            transformation_version="1",
            target_file_id="fixture-test-file-v1",
            input_digest=INPUT_DIGEST,
            output_digest=OUTPUT_DIGEST,
            materialization_pdr_id=pdr.pdr_id,
            security_fact_ids=(FACT_A,),
            validation_fact_id=FACT_B,
            review_fact_ids=(),
        )
        self.assertEqual(payload.payload_id, materialized_payload_id_for(payload))
        for forbidden in ("path", "content", "bytes", "diff", "handle"):
            self.assertNotIn(forbidden, payload.__dataclass_fields__)
        with self.assertRaises(ValueError):
            MaterializedCommitPayload.create(
                repository_id=REPOSITORY_ID, base_sha=BASE_SHA, snapshot_digest=SNAPSHOT_DIGEST,
                transformation_id="fixture-transform-v1", transformation_version="1", target_file_id="fixture-test-file-v1",
                input_digest=INPUT_DIGEST, output_digest=OUTPUT_DIGEST, materialization_pdr_id=pdr.pdr_id,
                security_fact_ids=(FACT_A, FACT_A), validation_fact_id=FACT_B, review_fact_ids=(),
            )
        with self.assertRaises(ValueError):
            replace(payload, payload_id="sha256:" + "0" * 64)

    def test_eligibility_pdr_cannot_represent_materialization_or_real_mutation(self) -> None:
        pdr = PayloadEligibilityPDR.create(
            attempt_id="attempt-eligibility-1", issued_at=12, expires_at=13,
            repository_id=REPOSITORY_ID, base_sha=BASE_SHA, payload_id="sha256:" + "f" * 64,
            output_digest=OUTPUT_DIGEST, security_fact_ids=(FACT_A,), validation_fact_id=FACT_B,
            review_fact_ids=(), materialization_pdr_id=materialization_pdr().pdr_id,
        )
        self.assertEqual(pdr.pdr_id, payload_eligibility_pdr_id_for(pdr))
        with self.assertRaises(ValueError):
            replace(pdr, authority_kind="materialization")
        with self.assertRaises(ValueError):
            replace(pdr, authority_kind="real_mutation")

    def test_terminal_uses_only_controlled_reason_and_safe_fields(self) -> None:
        terminal = MaterializationTerminal.create(
            reason="validation_infrastructure_failed", attempt_id="attempt-materialization-1",
            repository_id=REPOSITORY_ID, base_sha=BASE_SHA, profile_id="forgeflow-m4-fixture-only",
            profile_version="1.0.0", classification="runner_unavailable",
        )
        self.assertEqual(terminal.automatic_retries, 0)
        self.assertNotIn("output", terminal.__dataclass_fields__)
        self.assertNotIn("path", terminal.__dataclass_fields__)
        with self.assertRaises(ValueError):
            replace(terminal, reason="anything_else")
        with self.assertRaises(ValueError):
            replace(terminal, automatic_retries=1)

    def test_handle_is_private_nonserializable_and_liveness_is_not_forgeable(self) -> None:
        handle = _mint_ephemeral_handle()
        self.assertTrue(handle.is_live)
        with self.assertRaises(TypeError):
            json.dumps(handle)
        with self.assertRaises(TypeError):
            handle.__getstate__()
        handle.destroy()
        self.assertFalse(handle.is_live)


if __name__ == "__main__":
    unittest.main()
