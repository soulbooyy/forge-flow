from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys
import tempfile
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.repository_context.profile import M1_DEFAULTS
from forgeflow.repository_context.scanner import scan_workspace
from forgeflow.repository_context.workspace import WorkspaceBoundary


class DeterministicScannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.workspace_root = Path(self.temporary_directory.name) / "workspace"
        self.workspace_root.mkdir()
        self.boundary = WorkspaceBoundary.create(self.workspace_root, "fixture-workspace")

    def write_bytes(self, relative_path: str, content: bytes) -> None:
        path = self.workspace_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def test_scans_text_nested_binary_and_ignored_candidates_in_stable_order(self) -> None:
        self.write_bytes("z-last.txt", b"last\n")
        self.write_bytes("nested/a-first.txt", b"first\r\n")
        self.write_bytes("binary.dat", b"\x00binary")
        self.write_bytes(".forgeflow/cache/generated.txt", b"ignored")

        report = scan_workspace(self.boundary, M1_DEFAULTS)

        self.assertEqual(
            [candidate.path for candidate in report.files],
            ["binary.dat", "nested/a-first.txt", "z-last.txt"],
        )
        self.assertEqual(report.files[0].file_kind, "binary")
        self.assertIsNone(report.files[0].text)
        self.assertEqual(report.files[1].text, "first\n")
        self.assertEqual(report.skipped_directories, 1)
        self.assertEqual(report.skipped_files, 1)

    def test_repeated_scan_has_identical_candidate_output(self) -> None:
        self.write_bytes("b.txt", b"b")
        self.write_bytes("a.txt", b"a")

        first = scan_workspace(self.boundary, M1_DEFAULTS)
        second = scan_workspace(self.boundary, M1_DEFAULTS)

        self.assertEqual(first, second)

    def test_bounded_text_read_marks_prefix_as_truncated(self) -> None:
        self.write_bytes("large.txt", b"abcdef")
        profile = replace(M1_DEFAULTS, max_text_bytes_per_file=4)

        candidate = scan_workspace(self.boundary, profile).files[0]

        self.assertEqual(candidate.path, "large.txt")
        self.assertEqual(candidate.text, "abcd")
        self.assertTrue(candidate.text_truncated)

    def test_invalid_utf8_is_classified_without_lossy_decoding(self) -> None:
        self.write_bytes("invalid.txt", b"\xff\xfe")

        candidate = scan_workspace(self.boundary, M1_DEFAULTS).files[0]

        self.assertEqual(candidate.file_kind, "unsupported_encoding")
        self.assertIsNone(candidate.text)

    def test_symlink_is_not_followed_or_returned_as_a_candidate(self) -> None:
        outside = Path(self.temporary_directory.name) / "outside.txt"
        outside.write_text("outside", encoding="utf-8")
        link = self.workspace_root / "link.txt"
        try:
            link.symlink_to(outside)
        except OSError as error:
            self.skipTest(f"platform cannot create symlinks: {error}")

        report = scan_workspace(self.boundary, M1_DEFAULTS)

        self.assertEqual(report.files, ())
        self.assertEqual(report.skipped_files, 1)

    def test_fixed_ignore_policy_does_not_honor_gitignore_or_dependency_defaults(self) -> None:
        self.write_bytes(".gitignore", b"node_modules/\n")
        self.write_bytes("node_modules/kept.txt", b"kept")
        self.write_bytes(".git/config", b"ignored")

        report = scan_workspace(self.boundary, M1_DEFAULTS)

        self.assertEqual([candidate.path for candidate in report.files], [".gitignore", "node_modules/kept.txt"])
        self.assertEqual(report.skipped_directories, 1)


if __name__ == "__main__":
    unittest.main()
