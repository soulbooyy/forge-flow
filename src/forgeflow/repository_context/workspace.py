"""Trusted workspace and path boundary helpers."""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath, PureWindowsPath

from .models import WorkspaceRef


class WorkspaceBoundaryError(ValueError):
    """Raised when a workspace identity or path crosses the boundary."""

    code: str

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class WorkspaceBoundary:
    """Bind a caller-supplied logical identity to one trusted workspace root."""

    def __init__(self, root: Path, lexical_root: Path, root_id: str) -> None:
        self._root = root
        self._lexical_root = lexical_root
        self._root_id = root_id

    @classmethod
    def create(cls, root: Path, root_id: str) -> WorkspaceBoundary:
        root_path = Path(root)
        if not root_path.exists() or not root_path.is_dir():
            raise WorkspaceBoundaryError("invalid_workspace")
        if not _is_safe_root_id(root_id):
            raise WorkspaceBoundaryError("invalid_workspace_ref")
        return cls(root_path.resolve(), root_path.absolute(), root_id)

    @property
    def root_id(self) -> str:
        return self._root_id

    @property
    def filesystem_root(self) -> Path:
        """Return the resolved root for internal read-only scanner use."""
        return self._root

    def validate_workspace_ref(self, workspace_ref: WorkspaceRef) -> None:
        if not _is_safe_root_id(workspace_ref.root_id):
            raise WorkspaceBoundaryError("invalid_workspace_ref")
        if workspace_ref.root_id != self._root_id:
            raise WorkspaceBoundaryError("workspace_identity_mismatch")

    def canonical_path(self, input_path: str | Path) -> str:
        raw_path = str(input_path)
        if _is_foreign_windows_path(raw_path, os.name):
            raise WorkspaceBoundaryError("path_escape")

        path = Path(raw_path.replace("\\", "/"))
        if ".." in path.parts:
            raise WorkspaceBoundaryError("path_escape")

        lexical_path = path if path.is_absolute() else self._root / path
        resolved_path = lexical_path.resolve(strict=False)
        try:
            resolved_path.relative_to(self._root)
        except ValueError:
            if not path.is_absolute() or self._relative_to_root(path) is not None:
                raise WorkspaceBoundaryError("symlink_escape") from None
            raise WorkspaceBoundaryError("path_escape") from None

        relative_path = self._relative_to_root(path) if path.is_absolute() else path
        if relative_path is None:
            raise WorkspaceBoundaryError("path_escape") from None

        canonical = PurePosixPath(*relative_path.parts).as_posix()
        if canonical == ".":
            raise WorkspaceBoundaryError("path_escape")
        return canonical

    def _relative_to_root(self, path: Path) -> Path | None:
        if str(path).startswith("//"):
            path = Path(str(path)[1:])
        for root in (self._lexical_root, self._root):
            try:
                return path.relative_to(root)
            except ValueError:
                continue
        return None


def _is_safe_root_id(root_id: object) -> bool:
    return (
        isinstance(root_id, str)
        and bool(root_id)
        and len(root_id) <= 255
        and root_id == root_id.strip()
        and root_id not in {".", ".."}
        and "/" not in root_id
        and "\\" not in root_id
        and not _is_windows_path_like(root_id)
    )


def _is_windows_path_like(value: str) -> bool:
    return bool(PureWindowsPath(value).drive)


def _is_foreign_windows_path(value: str, platform_name: str) -> bool:
    return (
        platform_name != "nt"
        and not value.startswith("//")
        and _is_windows_path_like(value)
    )
