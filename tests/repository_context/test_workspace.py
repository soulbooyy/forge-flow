from __future__ import annotations

from pathlib import Path
import sys
import tempfile
from typing import get_type_hints
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.repository_context.models import WorkspaceRef
from forgeflow.repository_context import workspace
from forgeflow.repository_context.workspace import WorkspaceBoundary, WorkspaceBoundaryError


class WorkspaceBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.workspace_root = Path(self.temporary_directory.name) / "workspace"
        self.workspace_root.mkdir()
        self.boundary = WorkspaceBoundary.create(
            self.workspace_root,
            root_id="fixture-workspace",
        )

    def assert_boundary_error(self, code: str, callback: object) -> None:
        with self.assertRaises(WorkspaceBoundaryError) as raised:
            callback()
        self.assertEqual(raised.exception.code, code)

    def test_canonical_workspace_relative_path_is_deterministic_and_never_absolute(self) -> None:
        first = self.boundary.canonical_path("src/context.py")
        second = self.boundary.canonical_path("src/context.py")

        self.assertEqual(first, "src/context.py")
        self.assertEqual(first, second)
        self.assertNotIn(self.temporary_directory.name, first)
        self.assertFalse(first.startswith("/"))

    def test_canonical_nested_path_uses_stable_posix_separators(self) -> None:
        path = Path("nested") / "module" / "item.py"

        self.assertEqual(self.boundary.canonical_path(path), "nested/module/item.py")

    def test_parent_traversal_is_rejected_before_normalization(self) -> None:
        self.assert_boundary_error(
            "path_escape",
            lambda: self.boundary.canonical_path("../outside"),
        )

    def test_absolute_path_outside_workspace_is_rejected(self) -> None:
        outside = Path(self.temporary_directory.name) / "outside.txt"

        self.assert_boundary_error(
            "path_escape",
            lambda: self.boundary.canonical_path(outside),
        )

    def test_absolute_path_inside_workspace_returns_relative_path(self) -> None:
        absolute_path = self.workspace_root / "src" / "context.py"

        self.assertEqual(self.boundary.canonical_path(absolute_path), "src/context.py")

    def test_double_slash_absolute_path_inside_workspace_returns_relative_path(self) -> None:
        double_slash_path = Path("//") / self.workspace_root.relative_to("/") / "src" / "context.py"

        self.assertEqual(self.boundary.canonical_path(double_slash_path), "src/context.py")

    def test_windows_absolute_like_paths_are_rejected_on_posix_hosts(self) -> None:
        for input_path in (
            "C:/tmp/secret.txt",
            r"C:\tmp\secret.txt",
            r"\\server\share\file",
        ):
            with self.subTest(input_path=input_path):
                self.assert_boundary_error(
                    "path_escape",
                    lambda input_path=input_path: self.boundary.canonical_path(input_path),
                )

    def test_windows_path_form_is_foreign_only_on_non_windows_hosts(self) -> None:
        self.assertTrue(workspace._is_foreign_windows_path(r"C:\\repo\\src\\file.py", "posix"))
        self.assertFalse(workspace._is_foreign_windows_path(r"C:\\repo\\src\\file.py", "nt"))

    def test_symlink_that_escapes_workspace_is_rejected(self) -> None:
        outside = Path(self.temporary_directory.name) / "outside"
        outside.mkdir()
        link = self.workspace_root / "escaped"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"platform cannot create symlinks: {error}")

        self.assert_boundary_error(
            "symlink_escape",
            lambda: self.boundary.canonical_path(link / "secret.txt"),
        )

    def test_workspace_identity_mismatch_is_rejected(self) -> None:
        self.assert_boundary_error(
            "workspace_identity_mismatch",
            lambda: self.boundary.validate_workspace_ref(WorkspaceRef(root_id="other-workspace")),
        )

    def test_unsafe_or_missing_root_id_is_rejected(self) -> None:
        for root_id in (
            "",
            " workspace",
            "workspace ",
            ".",
            "..",
            "a/b",
            "a\\b",
            "C:",
            r"C:\workspace",
            r"\\server\share",
        ):
            with self.subTest(root_id=root_id):
                self.assert_boundary_error(
                    "invalid_workspace_ref",
                    lambda root_id=root_id: WorkspaceBoundary.create(self.workspace_root, root_id),
                )

    def test_drive_like_workspace_ref_is_invalid_before_identity_matching(self) -> None:
        self.assert_boundary_error(
            "invalid_workspace_ref",
            lambda: self.boundary.validate_workspace_ref(WorkspaceRef(root_id="C:")),
        )

    def test_workspace_root_must_exist_and_be_a_directory(self) -> None:
        missing = Path(self.temporary_directory.name) / "missing"
        file_root = Path(self.temporary_directory.name) / "file-root"
        file_root.touch()

        for root in (missing, file_root):
            with self.subTest(root=root):
                self.assert_boundary_error(
                    "invalid_workspace",
                    lambda root=root: WorkspaceBoundary.create(root, "fixture-workspace"),
                )

    def test_boundary_error_exposes_a_string_code(self) -> None:
        self.assertIs(get_type_hints(WorkspaceBoundaryError)["code"], str)


if __name__ == "__main__":
    unittest.main()
