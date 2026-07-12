from __future__ import annotations

from dataclasses import asdict, replace
import json
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.repository_context.matching import match_scanned_files
from forgeflow.repository_context.normalization import normalize_issue_text, normalize_query
from forgeflow.repository_context.profile import M1_DEFAULTS
from forgeflow.repository_context.scanner import ScannedFile, scan_workspace
from forgeflow.repository_context.workspace import WorkspaceBoundary


FIXTURE_ROOT = (
    Path(__file__).resolve().parents[2]
    / "openspec"
    / "changes"
    / "repository-context-foundation"
    / "fixtures"
    / "workspaces"
    / "phase-5-matching"
)
EXPECTED_PATH = (
    Path(__file__).resolve().parents[2]
    / "openspec"
    / "changes"
    / "repository-context-foundation"
    / "fixtures"
    / "expected"
    / "phase-5-matching"
    / "matching.json"
)


class MatchingAcceptanceSkeletonTests(unittest.TestCase):
    def test_fixture_matches_expected_direct_signals_and_text_locators(self) -> None:
        boundary = WorkspaceBoundary.create(FIXTURE_ROOT, "phase-5-matching")
        scanned_files = scan_workspace(boundary, M1_DEFAULTS).files
        query = normalize_query("  PAYMENT\t")

        matches = match_scanned_files(scanned_files, query, M1_DEFAULTS)

        with EXPECTED_PATH.open(encoding="utf-8") as handle:
            expected = json.load(handle)

        actual = {
            "query_normalized": query.normalized,
            "relevant_files": [
                {
                    "path": relevant_file.path,
                    "ranking_inputs": asdict(relevant_file.ranking_inputs),
                    "match_score": relevant_file.match_score,
                    "match_reasons": list(relevant_file.match_reasons),
                }
                for relevant_file in matches.relevant_files
            ],
            "search_results": [
                {
                    "path": search_result.path,
                    "start_line": search_result.locator.start_line,
                    "end_line": search_result.locator.end_line,
                }
                for search_result in matches.search_results
            ],
        }

        self.assertEqual(actual, expected)
        self.assertEqual(
            {reference.id for reference in matches.evidence_refs},
            {
                reference_id
                for relevant_file in matches.relevant_files
                for reference_id in relevant_file.evidence_ref_ids
            }
            | {result.evidence_ref_id for result in matches.search_results},
        )
        self.assertTrue(
            all(
                reference.content_hash is not None
                for reference in matches.evidence_refs
                if reference.retrieval_signal == "text_match"
            )
        )

    def test_normalization_is_nfc_collapsed_casefolded_and_bounds_issue_text(self) -> None:
        query = normalize_query("  Cafe\u0301\tPAYMENT  ")
        issue_text = normalize_issue_text(
            "  abcdef  ", replace(M1_DEFAULTS, max_issue_text_chars=3)
        )

        self.assertEqual(query.normalized, "Café PAYMENT")
        self.assertEqual(query.matching_view, "café payment")
        self.assertTrue(issue_text.present)
        self.assertEqual(issue_text.normalized, "abc")
        self.assertTrue(issue_text.truncated)

    def test_text_duplicates_collapse_per_line_and_paths_break_score_ties(self) -> None:
        scanned_files = (
            ScannedFile("z.txt", "text", "payment payment\nPAYMENT\n", False),
            ScannedFile("a.txt", "text", "payment\nPAYMENT\n", False),
        )

        matches = match_scanned_files(
            scanned_files, normalize_query("payment"), M1_DEFAULTS
        )

        self.assertEqual(
            [file.path for file in matches.relevant_files], ["a.txt", "z.txt"]
        )
        self.assertEqual(matches.relevant_files[0].match_score, 50)
        self.assertEqual(matches.relevant_files[0].ranking_inputs.text_match_count, 2)
        self.assertEqual(
            [result.locator.start_line for result in matches.search_results],
            [1, 2, 1, 2],
        )

    def test_file_signals_create_file_evidence_without_search_results(self) -> None:
        matches = match_scanned_files(
            (ScannedFile("payment.py", "text", "unrelated\n", False),),
            normalize_query("payment.py"),
            M1_DEFAULTS,
        )

        self.assertEqual(matches.relevant_files[0].match_score, 150)
        self.assertEqual(matches.search_results, ())
        self.assertEqual(
            [reference.retrieval_signal for reference in matches.evidence_refs],
            ["filename_match", "path_match"],
        )
        self.assertTrue(all(reference.locator is None for reference in matches.evidence_refs))

    def test_truncated_text_evidence_hashes_only_the_inspected_range(self) -> None:
        matches = match_scanned_files(
            (ScannedFile("notes.txt", "text", "payment\n", True),),
            normalize_query("payment"),
            M1_DEFAULTS,
        )

        evidence = matches.evidence_refs[0]
        self.assertEqual(evidence.retrieval_signal, "text_match")
        self.assertEqual(evidence.hash_scope, "truncated_inspected_range")
        self.assertEqual(evidence.content_hash.algorithm, "sha256")
        self.assertEqual(len(evidence.content_hash.value), 64)


if __name__ == "__main__":
    unittest.main()
