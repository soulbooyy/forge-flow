from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys
import tempfile
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.repository_context.assembly import assemble_result
from forgeflow.repository_context.matching import match_scanned_files
from forgeflow.repository_context.models import (
    BoundedOptionalInput,
    NormalizedInput,
    RepositoryContextRequest,
    RepositoryContextValidationError,
    WorkspaceRef,
)
from forgeflow.repository_context.normalization import normalize_query
from forgeflow.repository_context.profile import M1_DEFAULTS
from forgeflow.repository_context.scanner import scan_workspace
from forgeflow.repository_context.service import inspect_repository
from forgeflow.repository_context.workspace import WorkspaceBoundary


class RepositoryContextServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.workspace_root = Path(self.temporary_directory.name) / "workspace"
        self.workspace_root.mkdir()

    def write_text(self, relative_path: str, content: str) -> None:
        path = self.workspace_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def request(
        self,
        *,
        query: str = "payment",
        configuration_profile_id: str = "repository-context/m1-defaults-v1",
    ) -> RepositoryContextRequest:
        return RepositoryContextRequest(
            workspace_root=self.workspace_root,
            workspace_ref=WorkspaceRef(root_id="service-fixture"),
            configuration_profile_id=configuration_profile_id,
            query=query,
        )

    def test_empty_query_returns_stable_validation_error_without_success_fields(self) -> None:
        first = inspect_repository(self.request(query=" \t "))
        second = inspect_repository(self.request(query="\n"))

        self.assertIsInstance(first, RepositoryContextValidationError)
        self.assertEqual(first.error_code, "empty_query")
        self.assertEqual(first.error_id, second.error_id)
        self.assertFalse(hasattr(first, "contract_id"))
        self.assertFalse(hasattr(first, "relevant_files"))

    def test_invalid_profile_returns_a_deterministic_validation_error(self) -> None:
        result = inspect_repository(
            self.request(configuration_profile_id="repository-context/m1-defaults-v2")
        )

        self.assertIsInstance(result, RepositoryContextValidationError)
        self.assertEqual(result.error_code, "invalid_config_profile")
        self.assertEqual(result.input_category, "configuration_profile")

    def test_service_assembles_stable_result_with_root_only_hints(self) -> None:
        self.write_text("src/payment.py", "def process_payment():\n    return 'ok'\n")
        self.write_text("docs/notes.txt", "Payment requests require validation.\n")
        self.write_text("package.json", '{"scripts": {"test": "python -m unittest"}}')
        self.write_text("Makefile", "test:\n\t@echo test\n")

        first = inspect_repository(self.request())
        second = inspect_repository(self.request())

        self.assertEqual(first, second)
        self.assertEqual(first.result_type, "repository_context_result")
        self.assertTrue(first.contract_id.startswith("rcr_sha256:"))
        self.assertEqual([file.path for file in first.relevant_files], ["src/payment.py", "docs/notes.txt"])
        self.assertEqual([hint.command for hint in first.test_command_hints], ["make test", "npm test"])
        self.assertEqual(first.run_summary.counts.candidates.relevant_files, 2)
        self.assertEqual(first.run_summary.counts.returned.relevant_files, 2)
        returned_evidence_ids = {reference.id for reference in first.evidence_refs}
        self.assertTrue(
            all(
                reference_id in returned_evidence_ids
                for file in first.relevant_files
                for reference_id in file.evidence_ref_ids
            )
        )
        self.assertTrue(
            all(
                result.evidence_ref_id in returned_evidence_ids
                for result in first.search_results
            )
        )

    def test_assembly_caps_results_and_reports_grouped_truncation(self) -> None:
        self.write_text("a/payment.py", "payment\n")
        self.write_text("b/payment.py", "payment\n")
        profile = replace(M1_DEFAULTS, max_relevant_files=1)
        boundary = WorkspaceBoundary.create(self.workspace_root, "service-fixture")
        scan_report = scan_workspace(boundary, profile)
        matches = match_scanned_files(
            scan_report.files, normalize_query("payment"), profile
        )

        result = assemble_result(
            workspace_ref=WorkspaceRef(root_id="service-fixture"),
            query=NormalizedInput(normalized="payment"),
            issue_text=BoundedOptionalInput(False, "", False),
            scan_report=scan_report,
            matches=matches,
            hints=(),
            hint_evidence_refs=(),
            profile=profile,
        )

        self.assertEqual(len(result.relevant_files), 1)
        self.assertEqual(result.run_summary.counts.candidates.relevant_files, 2)
        self.assertEqual(result.run_summary.counts.returned.relevant_files, 1)
        self.assertEqual(result.limitations[0].code, "result_set_truncated")
        returned_evidence_ids = {reference.id for reference in result.evidence_refs}
        self.assertTrue(
            all(
                reference_id in returned_evidence_ids
                for file in result.relevant_files
                for reference_id in file.evidence_ref_ids
            )
        )


if __name__ == "__main__":
    unittest.main()
