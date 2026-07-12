from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.repository_context.canonical import canonical_bytes
from forgeflow.repository_context.models import (
    RepositoryContextRequest,
    RepositoryContextResult,
    RepositoryContextValidationError,
    WorkspaceRef,
)
from forgeflow.repository_context.service import inspect_repository


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = (
    REPOSITORY_ROOT
    / "openspec/changes/repository-context-foundation/fixtures/workspaces/phase-7-acceptance"
)
EXPECTED_ROOT = (
    REPOSITORY_ROOT
    / "openspec/changes/repository-context-foundation/fixtures/expected/phase-7-acceptance"
)


class RepositoryContextAcceptanceTests(unittest.TestCase):
    def request(
        self,
        *,
        query: str = "payment",
        issue_text: str | None = None,
    ) -> RepositoryContextRequest:
        return RepositoryContextRequest(
            workspace_root=FIXTURE_ROOT,
            workspace_ref=WorkspaceRef(root_id="phase-7-acceptance"),
            configuration_profile_id="repository-context/m1-defaults-v1",
            query=query,
            issue_text=issue_text,
        )

    def fixture_snapshot(self) -> tuple[tuple[str, str], ...]:
        return tuple(
            (path.relative_to(FIXTURE_ROOT).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest())
            for path in sorted(FIXTURE_ROOT.rglob("*"))
            if path.is_file()
        )

    def test_fixture_result_matches_expected_contract_fragment_deterministically(self) -> None:
        expected = json.loads((EXPECTED_ROOT / "result-fragment.json").read_text(encoding="utf-8"))
        before = self.fixture_snapshot()

        first = inspect_repository(self.request(query="  payment  "))
        second = inspect_repository(self.request(query="payment"))

        self.assertIsInstance(first, RepositoryContextResult)
        self.assertEqual(first, second)
        self.assertEqual(first.query.normalized, expected["query_normalized"])
        self.assertEqual([item.path for item in first.relevant_files], expected["relevant_paths"])
        self.assertEqual([item.path for item in first.search_results], expected["search_paths"])
        self.assertEqual(
            [hint.command for hint in first.test_command_hints], expected["test_commands"]
        )
        self.assertEqual(first.run_summary.counts.discovered_files, expected["discovered_files"])
        self.assertEqual(first.run_summary.counts.skipped_directories, expected["skipped_directories"])
        self.assertTrue(first.contract_id.startswith("rcr_sha256:"))
        self.assertTrue(all(reference.id.startswith("ev_sha256:") for reference in first.evidence_refs))
        self.assertTrue(
            all(
                reference.content_hash is not None
                for reference in first.evidence_refs
                if reference.evidence_kind == "file_text_match"
            )
        )

        evidence_ids = {reference.id for reference in first.evidence_refs}
        self.assertTrue(
            all(
                evidence_id in evidence_ids
                for item in first.relevant_files
                for evidence_id in item.evidence_ref_ids
            )
        )
        self.assertTrue(
            all(item.evidence_ref_id in evidence_ids for item in first.search_results)
        )
        self.assertEqual(before, self.fixture_snapshot())
        self.assertTrue(
            all(
                not path.path.startswith("/")
                and "/./" not in path.path
                and ".." not in path.path.split("/")
                for path in (*first.relevant_files, *first.search_results)
            )
        )

    def test_empty_query_matches_the_expected_validation_error_fragment(self) -> None:
        expected = json.loads(
            (EXPECTED_ROOT / "empty-query-error.json").read_text(encoding="utf-8")
        )

        first = inspect_repository(self.request(query=" \t\n "))
        second = inspect_repository(self.request(query=""))

        self.assertIsInstance(first, RepositoryContextValidationError)
        self.assertEqual(first, second)
        self.assertEqual(first.result_type, expected["result_type"])
        self.assertEqual(first.error_code, expected["error_code"])
        self.assertEqual(first.input_category, expected["input_category"])
        self.assertTrue(first.error_id.startswith("rce_sha256:"))

    def test_issue_text_is_bounded_and_never_becomes_result_payload(self) -> None:
        raw_issue = ("phase-seven\t\nsecret ") * 1_000
        result = inspect_repository(self.request(issue_text=raw_issue))

        self.assertIsInstance(result, RepositoryContextResult)
        self.assertTrue(result.issue_text.present)
        self.assertTrue(result.issue_text.truncated)
        self.assertEqual(result.issue_text.normalized, "phase-seven secret " * 215 + "phase-seven")
        self.assertNotIn(raw_issue.encode("utf-8"), canonical_bytes(result))

    def test_issue_text_does_not_change_query_only_retrieval(self) -> None:
        baseline = inspect_repository(self.request())
        with_context = inspect_repository(self.request(issue_text="private.env payment"))

        self.assertIsInstance(baseline, RepositoryContextResult)
        self.assertIsInstance(with_context, RepositoryContextResult)
        self.assertEqual(baseline.relevant_files, with_context.relevant_files)
        self.assertEqual(baseline.search_results, with_context.search_results)

    def test_external_symlink_is_not_exposed_as_a_match(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            workspace = temporary_root / "workspace"
            workspace.mkdir()
            outside = temporary_root / "outside-payment.txt"
            outside.write_text("payment must remain outside\n", encoding="utf-8")
            (workspace / "escaped-payment.txt").symlink_to(outside)

            result = inspect_repository(
                RepositoryContextRequest(
                    workspace_root=workspace,
                    workspace_ref=WorkspaceRef(root_id="symlink-fixture"),
                    configuration_profile_id="repository-context/m1-defaults-v1",
                    query="payment",
                )
            )

        self.assertIsInstance(result, RepositoryContextResult)
        self.assertEqual(result.relevant_files, ())
        self.assertEqual(result.search_results, ())
        self.assertNotIn(b"outside-payment", canonical_bytes(result))

    def test_binary_and_invalid_utf8_files_never_produce_text_results(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory) / "workspace"
            workspace.mkdir()
            (workspace / "binary-candidate.bin").write_bytes(b"\x00payment")
            (workspace / "invalid-candidate.txt").write_bytes(b"\xffpayment")

            result = inspect_repository(
                RepositoryContextRequest(
                    workspace_root=workspace,
                    workspace_ref=WorkspaceRef(root_id="encoding-fixture"),
                    configuration_profile_id="repository-context/m1-defaults-v1",
                    query="candidate",
                )
            )

        self.assertIsInstance(result, RepositoryContextResult)
        self.assertEqual(result.search_results, ())
        self.assertEqual(
            [(item.path, item.file_kind) for item in result.relevant_files],
            [("binary-candidate.bin", "binary"), ("invalid-candidate.txt", "unsupported_encoding")],
        )
        self.assertTrue(
            all(reference.content_hash is None for reference in result.evidence_refs)
        )

    def test_line_matches_collapse_and_score_ties_use_canonical_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory) / "workspace"
            (workspace / "a").mkdir(parents=True)
            (workspace / "z").mkdir()
            (workspace / "a/payment.txt").write_text("payment payment\nPAYMENT\n", encoding="utf-8")
            (workspace / "z/payment.txt").write_text("payment\nPAYMENT\n", encoding="utf-8")

            result = inspect_repository(
                RepositoryContextRequest(
                    workspace_root=workspace,
                    workspace_ref=WorkspaceRef(root_id="line-fixture"),
                    configuration_profile_id="repository-context/m1-defaults-v1",
                    query="payment",
                )
            )

        self.assertIsInstance(result, RepositoryContextResult)
        self.assertEqual([item.path for item in result.relevant_files], ["a/payment.txt", "z/payment.txt"])
        self.assertEqual([item.match_score for item in result.relevant_files], [200, 200])
        self.assertEqual(
            [(item.path, item.locator.start_line) for item in result.search_results],
            [("a/payment.txt", 1), ("a/payment.txt", 2), ("z/payment.txt", 1), ("z/payment.txt", 2)],
        )

    def test_text_beyond_the_bounded_read_range_cannot_match(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory) / "workspace"
            workspace.mkdir()
            (workspace / "large.txt").write_text("x" * 1_048_576 + "payment\n", encoding="utf-8")

            result = inspect_repository(
                RepositoryContextRequest(
                    workspace_root=workspace,
                    workspace_ref=WorkspaceRef(root_id="bounded-read-fixture"),
                    configuration_profile_id="repository-context/m1-defaults-v1",
                    query="payment",
                )
            )

        self.assertIsInstance(result, RepositoryContextResult)
        self.assertEqual(result.relevant_files, ())
        self.assertEqual(result.search_results, ())
        self.assertEqual(result.run_summary.counts.scanned_text_files, 1)


if __name__ == "__main__":
    unittest.main()
