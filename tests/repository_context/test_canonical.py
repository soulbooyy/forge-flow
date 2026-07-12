from __future__ import annotations

from pathlib import Path
import re
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.repository_context import (
    BoundedOptionalInput,
    CandidateCounts,
    EvidenceRef,
    InputSummary,
    NormalizedInput,
    RepositoryContextResult,
    RepositoryContextValidationError,
    ReturnedCounts,
    RunCounts,
    RunSummary,
    TextLocator,
    ValidationErrorSummary,
    WorkspaceRef,
    canonical_bytes,
    contract_id_for,
    error_id_for,
    evidence_id_for,
    sha256_hex,
)


def make_result(*, contract_id: str = "rcr_sha256:placeholder", query: str = "find me") -> RepositoryContextResult:
    return RepositoryContextResult(
        contract_id=contract_id,
        workspace_ref=WorkspaceRef(root_id="fixture-workspace"),
        query=NormalizedInput(normalized=query),
        issue_text=BoundedOptionalInput(present=False, normalized="", truncated=False),
        run_summary=RunSummary(
            operation_type="repository_context",
            completion_status="completed",
            input_summary=InputSummary(
                workspace_root_id="fixture-workspace",
                configuration_profile_id="repository-context/m1-defaults-v1",
                query_normalized=query,
                issue_text_present=False,
                issue_text_truncated=False,
                normalization_id="m1-nfc-trim-collapse-casefold-v1",
                limit_profile_id="m1-default-limits-v1",
                ignore_policy_id="m1-default-ignore-v1",
            ),
            counts=RunCounts(
                discovered_files=1,
                discovered_directories=1,
                scanned_text_files=1,
                skipped_files=0,
                skipped_directories=0,
                candidates=CandidateCounts(0, 0, 0, 0),
                returned=ReturnedCounts(0, 0, 0, 0, 0),
            ),
        ),
    )


def make_evidence(*, evidence_id: str = "ev_sha256:placeholder", path: str | None = None) -> EvidenceRef:
    return EvidenceRef(
        id=evidence_id,
        evidence_kind="file_text_match",
        retrieval_signal="text_match",
        locator=None,
        path=path,
    )


def make_error(*, error_id: str = "rce_sha256:placeholder", message: str = "Query is empty.") -> RepositoryContextValidationError:
    return RepositoryContextValidationError(
        error_id=error_id,
        error_code="empty_query",
        input_category="query",
        message=message,
        summary=ValidationErrorSummary(
            workspace_root_id="fixture-workspace",
            configuration_profile_id="repository-context/m1-defaults-v1",
            query_present=True,
        ),
    )


class CanonicalSerializationTests(unittest.TestCase):
    def test_same_input_produces_byte_identical_serialization_and_hash(self) -> None:
        value = {"nested": {"b": 2, "a": 1}, "items": ("first", None, "last")}

        self.assertEqual(canonical_bytes(value), canonical_bytes(value))
        self.assertEqual(sha256_hex(value), sha256_hex(value))

    def test_reordered_mapping_keys_produce_identical_bytes_and_hash(self) -> None:
        first = {"z": 3, "nested": {"b": 2, "a": 1}, "a": 0}
        second = {"a": 0, "nested": {"a": 1, "b": 2}, "z": 3}

        self.assertEqual(canonical_bytes(first), canonical_bytes(second))
        self.assertEqual(sha256_hex(first), sha256_hex(second))

    def test_serialization_is_sorted_compact_utf8(self) -> None:
        value = {"z": "café", "a": "汉字"}

        self.assertEqual(
            canonical_bytes(value),
            b'{"a":"\xe6\xb1\x89\xe5\xad\x97","z":"caf\xc3\xa9"}',
        )

    def test_tuples_become_arrays_without_changing_sequence_order(self) -> None:
        self.assertEqual(canonical_bytes(("third", "second", "first")), b'["third","second","first"]')

    def test_generic_mapping_none_locator_and_optional_fields_are_omitted(self) -> None:
        self.assertEqual(canonical_bytes({"locator": None, "optional": None}), b"{}")

    def test_evidence_ref_none_locator_is_preserved_as_json_null(self) -> None:
        evidence = make_evidence()

        self.assertEqual(
            canonical_bytes(evidence),
            b'{"evidence_kind":"file_text_match","id":"ev_sha256:placeholder","locator":null,"retrieval_signal":"text_match"}',
        )

    def test_omitted_fields_are_removed_recursively(self) -> None:
        value = {"id": "outer", "nested": {"id": "inner", "keep": True}}

        self.assertEqual(
            canonical_bytes(value, omit_fields=frozenset({"id"})),
            b'{"nested":{"keep":true}}',
        )

    def test_floats_and_unsupported_values_raise_type_error(self) -> None:
        with self.assertRaises(TypeError):
            canonical_bytes({"nested": [1, 2.5]})
        with self.assertRaises(TypeError):
            canonical_bytes(object())


class IdentityHelperTests(unittest.TestCase):
    def test_contract_id_ignores_only_contract_id_and_changes_with_content(self) -> None:
        first = make_result(contract_id="rcr_sha256:first")
        same_content_different_id = make_result(contract_id="rcr_sha256:second")
        changed = make_result(query="different query")

        self.assertEqual(contract_id_for(first), contract_id_for(same_content_different_id))
        self.assertNotEqual(contract_id_for(first), contract_id_for(changed))

    def test_evidence_id_ignores_only_evidence_id_and_changes_with_content(self) -> None:
        first = make_evidence(evidence_id="ev_sha256:first")
        same_content_different_id = make_evidence(evidence_id="ev_sha256:second")
        changed = make_evidence(path="src/changed.py")

        self.assertEqual(evidence_id_for(first), evidence_id_for(same_content_different_id))
        self.assertNotEqual(evidence_id_for(first), evidence_id_for(changed))

    def test_error_id_ignores_only_error_id_and_changes_with_content(self) -> None:
        first = make_error(error_id="rce_sha256:first")
        same_content_different_id = make_error(error_id="rce_sha256:second")
        changed = make_error(message="Query contains unsupported characters.")

        self.assertEqual(error_id_for(first), error_id_for(same_content_different_id))
        self.assertNotEqual(error_id_for(first), error_id_for(changed))

    def test_ids_are_stable_and_have_the_required_prefixes_and_hex_payloads(self) -> None:
        ids = (
            (contract_id_for(make_result()), contract_id_for(make_result()), "rcr_sha256:"),
            (evidence_id_for(make_evidence()), evidence_id_for(make_evidence()), "ev_sha256:"),
            (error_id_for(make_error()), error_id_for(make_error()), "rce_sha256:"),
        )

        for value, repeated_value, prefix in ids:
            with self.subTest(prefix=prefix):
                self.assertEqual(value, repeated_value)
                self.assertRegex(value, rf"^{re.escape(prefix)}[0-9a-f]{{64}}$")


if __name__ == "__main__":
    unittest.main()
