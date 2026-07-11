from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from pathlib import Path
import sys
from typing import Literal, get_type_hints
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.repository_context.models import (
    BoundedOptionalInput,
    CandidateCounts,
    ContentHash,
    EvidenceRef,
    InputSummary,
    Limitation,
    LimitationDetail,
    NormalizedInput,
    RankingInputs,
    RelevantFile,
    ResultSetTruncatedDetail,
    RepositoryContextRequest,
    RepositoryContextResult,
    RepositoryContextValidationError,
    ReturnedCounts,
    RunCounts,
    RunSummary,
    SearchResult,
    TestCommandHint,
    TextLocator,
    ValidationErrorSummary,
    WorkspaceRef,
)
from forgeflow.repository_context.profile import M1_DEFAULTS


class ContractModelTests(unittest.TestCase):
    def test_ranking_inputs_are_immutable_and_narrow(self) -> None:
        value = RankingInputs(filename_match=True, path_match=False, text_match_count=1)

        self.assertEqual(
            [field.name for field in fields(value)],
            ["filename_match", "path_match", "text_match_count"],
        )
        with self.assertRaises(FrozenInstanceError):
            value.text_match_count = 2

    def test_result_set_truncated_detail_is_frozen_slotted_and_object_shaped(self) -> None:
        detail = ResultSetTruncatedDetail(
            affected_arrays=("relevant_files", "search_results")
        )

        self.assertEqual([field.name for field in fields(detail)], ["affected_arrays"])
        self.assertEqual(detail.affected_arrays, ("relevant_files", "search_results"))
        self.assertFalse(hasattr(detail, "__dict__"))
        self.assertEqual(LimitationDetail, str | ResultSetTruncatedDetail)
        self.assertIsInstance(
            Limitation(
                code="result_set_truncated",
                scope="result",
                detail=detail,
            ).detail,
            ResultSetTruncatedDetail,
        )
        with self.assertRaises(FrozenInstanceError):
            detail.affected_arrays = ("evidence_refs",)

    def test_success_contract_pins_literals_and_tuple_collections(self) -> None:
        locator = TextLocator(start_line=12, end_line=12)
        content_hash = ContentHash(algorithm="sha256", value="a" * 64)
        evidence = EvidenceRef(
            id="ev_sha256:" + "b" * 64,
            path="src/context.py",
            evidence_kind="file_text_match",
            retrieval_signal="text_match",
            locator=locator,
            content_hash=content_hash,
            hash_scope="full_inspected_text",
        )
        relevant_file = RelevantFile(
            path="src/context.py",
            file_kind="text",
            ranking_inputs=RankingInputs(False, False, 1),
            match_score=25,
            match_reasons=("text_match",),
            evidence_ref_ids=(evidence.id,),
            limitation_codes=(),
        )
        summary = RunSummary(
            operation_type="repository_context",
            completion_status="completed_with_limitations",
            input_summary=InputSummary(
                workspace_root_id="fixture-basic-context",
                configuration_profile_id=M1_DEFAULTS.configuration_profile_id,
                query_normalized="repository context",
                issue_text_present=False,
                issue_text_truncated=False,
                normalization_id=M1_DEFAULTS.normalization_id,
                limit_profile_id=M1_DEFAULTS.limit_profile_id,
                ignore_policy_id=M1_DEFAULTS.ignore_policy_id,
            ),
            counts=RunCounts(
                discovered_files=1,
                discovered_directories=1,
                scanned_text_files=1,
                skipped_files=0,
                skipped_directories=0,
                candidates=CandidateCounts(1, 1, 1, 0),
                returned=ReturnedCounts(1, 1, 1, 0, 1),
            ),
            limitation_codes=("no_matches",),
        )
        result = RepositoryContextResult(
            contract_id="rcr_sha256:" + "c" * 64,
            workspace_ref=WorkspaceRef(
                root_id="fixture-basic-context",
                source_ref="openspec-fixture:basic-context",
            ),
            query=NormalizedInput(normalized="repository context"),
            issue_text=BoundedOptionalInput(present=False, normalized="", truncated=False),
            relevant_files=(relevant_file,),
            search_results=(SearchResult("src/context.py", locator, evidence.id),),
            test_command_hints=(TestCommandHint("npm test", "package.json", (evidence.id,)),),
            evidence_refs=(evidence,),
            limitations=(Limitation("no_matches", "result", "not used"),),
            run_summary=summary,
        )

        self.assertEqual(result.result_type, "repository_context_result")
        self.assertEqual(result.schema_version, "repository-context-result/v1")
        self.assertIsInstance(result.relevant_files, tuple)
        self.assertIsInstance(result.search_results, tuple)
        self.assertIsInstance(result.test_command_hints, tuple)
        self.assertIsInstance(result.evidence_refs, tuple)
        self.assertIsInstance(result.limitations, tuple)
        with self.assertRaises(FrozenInstanceError):
            result.contract_id = "changed"

    def test_validation_error_pins_literals_and_excludes_success_fields(self) -> None:
        error = RepositoryContextValidationError(
            error_id="rce_sha256:" + "d" * 64,
            error_code="empty_query",
            input_category="query",
            message="Query must contain a non-empty normalized value.",
            summary=ValidationErrorSummary(
                workspace_root_id="fixture-basic-context",
                configuration_profile_id=M1_DEFAULTS.configuration_profile_id,
                query_present=True,
            ),
        )

        self.assertEqual(error.result_type, "repository_context_validation_error")
        self.assertEqual(error.schema_version, "repository-context-validation-error/v1")
        self.assertEqual(error.completion_status, "validation_error")
        self.assertNotIn("contract_id", [field.name for field in fields(error)])
        self.assertFalse(
            {"relevant_files", "search_results", "test_command_hints", "evidence_refs", "limitations"}
            & {field.name for field in fields(error)}
        )

    def test_required_collection_defaults_are_explicit_empty_tuples(self) -> None:
        relevant_file = RelevantFile(
            path="README.md",
            file_kind="text",
            ranking_inputs=RankingInputs(False, False, 0),
            match_score=0,
        )
        hint = TestCommandHint(command="make test", source="Makefile")
        limitation = Limitation(code="no_matches", scope="result", detail="No matches.")

        self.assertEqual(relevant_file.match_reasons, ())
        self.assertEqual(relevant_file.evidence_ref_ids, ())
        self.assertEqual(relevant_file.limitation_codes, ())
        self.assertEqual(hint.evidence_ref_ids, ())
        self.assertEqual(limitation.related_evidence_ref_ids, ())

    def test_request_and_summary_models_are_immutable(self) -> None:
        request = RepositoryContextRequest(
            workspace_root=Path("/workspace"),
            workspace_ref=WorkspaceRef(root_id="workspace"),
            configuration_profile_id=M1_DEFAULTS.configuration_profile_id,
            query="repository context",
        )
        candidates = CandidateCounts(1, 2, 3, 4)
        returned = ReturnedCounts(1, 2, 3, 4, 5)

        self.assertIsNone(request.issue_text)
        self.assertEqual(candidates.evidence_refs, 3)
        self.assertEqual(returned.limitations, 5)
        with self.assertRaises(FrozenInstanceError):
            request.query = "changed"

        self.assertEqual(
            get_type_hints(InputSummary)["configuration_profile_id"],
            Literal["repository-context/m1-defaults-v1"],
        )
        self.assertIs(get_type_hints(RepositoryContextRequest)["configuration_profile_id"], str)
        self.assertEqual(
            get_type_hints(ValidationErrorSummary)["configuration_profile_id"],
            str | None,
        )

    def test_profile_values_are_exact_and_immutable(self) -> None:
        self.assertEqual(
            M1_DEFAULTS,
            type(M1_DEFAULTS)(
                configuration_profile_id="repository-context/m1-defaults-v1",
                normalization_id="m1-nfc-trim-collapse-casefold-v1",
                limit_profile_id="m1-default-limits-v1",
                ignore_policy_id="m1-default-ignore-v1",
                max_query_chars=512,
                max_issue_text_chars=4096,
                max_text_bytes_per_file=1_048_576,
                max_lines_per_file=20_000,
                max_text_locators_per_file=20,
                max_relevant_files=50,
                max_search_results=200,
                max_evidence_refs=300,
                max_test_command_hints=10,
            ),
        )
        with self.assertRaises(FrozenInstanceError):
            M1_DEFAULTS.max_query_chars = 1

    def test_models_exclude_runtime_and_future_stage_fields(self) -> None:
        forbidden_names = {
            "runtime_metadata",
            "timestamp",
            "timestamps",
            "run_id",
            "command_output",
            "raw_payload",
            "host_path",
            "patch",
            "validation",
            "branch",
            "commit",
            "pr",
            "memory",
            "agent",
            "workflow",
        }
        model_types = (
            RepositoryContextRequest,
            RepositoryContextResult,
            RepositoryContextValidationError,
            WorkspaceRef,
            NormalizedInput,
            BoundedOptionalInput,
            RelevantFile,
            RankingInputs,
            SearchResult,
            TestCommandHint,
            EvidenceRef,
            TextLocator,
            ContentHash,
            Limitation,
            InputSummary,
            CandidateCounts,
            ReturnedCounts,
            RunSummary,
        )

        for model_type in model_types:
            with self.subTest(model_type=model_type.__name__):
                self.assertFalse(forbidden_names & {field.name for field in fields(model_type)})


if __name__ == "__main__":
    unittest.main()
