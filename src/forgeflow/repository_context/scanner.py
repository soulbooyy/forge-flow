"""Deterministic, read-only repository candidate scanning."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Literal

from .models import Limitation
from .profile import RepositoryContextProfile
from .workspace import WorkspaceBoundary


FileKind = Literal["text", "binary", "unsupported_encoding"]


@dataclass(frozen=True, slots=True)
class ScannedFile:
    path: str
    file_kind: FileKind
    text: str | None
    text_truncated: bool


@dataclass(frozen=True, slots=True)
class ScanReport:
    files: tuple[ScannedFile, ...]
    discovered_files: int
    discovered_directories: int
    skipped_files: int
    skipped_directories: int
    limitations: tuple[Limitation, ...] = ()


def scan_workspace(boundary: WorkspaceBoundary, profile: RepositoryContextProfile) -> ScanReport:
    """Return deterministically ordered, bounded candidates within a workspace."""
    files: list[ScannedFile] = []
    limitations: list[Limitation] = []
    counts = _ScanCounts()
    _scan_directory(boundary.filesystem_root, boundary, profile, files, limitations, counts)
    return ScanReport(
        files=tuple(files),
        discovered_files=counts.discovered_files,
        discovered_directories=counts.discovered_directories,
        skipped_files=counts.skipped_files,
        skipped_directories=counts.skipped_directories,
        limitations=tuple(limitations),
    )


@dataclass(slots=True)
class _ScanCounts:
    discovered_files: int = 0
    discovered_directories: int = 0
    skipped_files: int = 0
    skipped_directories: int = 0


def _scan_directory(
    directory: Path,
    boundary: WorkspaceBoundary,
    profile: RepositoryContextProfile,
    files: list[ScannedFile],
    limitations: list[Limitation],
    counts: _ScanCounts,
) -> None:
    counts.discovered_directories += 1
    with os.scandir(directory) as entries:
        ordered_entries = sorted(entries, key=lambda entry: entry.name)

    for entry in ordered_entries:
        path = Path(entry.path)
        if entry.is_symlink():
            counts.skipped_files += 1
            limitation = _symlink_limitation(path, boundary)
            if limitation is not None:
                limitations.append(limitation)
            continue

        canonical_path = boundary.canonical_path(path)
        is_directory = entry.is_dir(follow_symlinks=False)
        if _is_ignored(canonical_path, is_directory):
            if is_directory:
                counts.skipped_directories += 1
            else:
                counts.skipped_files += 1
            continue

        if is_directory:
            _scan_directory(path, boundary, profile, files, limitations, counts)
            continue

        if not entry.is_file(follow_symlinks=False):
            counts.skipped_files += 1
            continue

        counts.discovered_files += 1
        try:
            candidate = _scan_file(path, canonical_path, profile)
        except OSError:
            counts.skipped_files += 1
            limitations.append(
                Limitation(
                    code="unreadable_file",
                    scope="file",
                    detail="file could not be read",
                    path=canonical_path,
                )
            )
            continue

        files.append(candidate)
        if candidate.file_kind != "text":
            counts.skipped_files += 1
            limitations.append(
                Limitation(
                    code=(
                        "binary_file_skipped"
                        if candidate.file_kind == "binary"
                        else "unsupported_encoding"
                    ),
                    scope="file",
                    detail="file content was not inspected as text",
                    path=canonical_path,
                )
            )
        if candidate.text_truncated:
            limitations.append(
                Limitation(
                    code="file_scan_truncated",
                    scope="file",
                    detail="file inspection was bounded",
                    path=canonical_path,
                )
            )


def _scan_file(path: Path, canonical_path: str, profile: RepositoryContextProfile) -> ScannedFile:
    with path.open("rb") as handle:
        data = handle.read(profile.max_text_bytes_per_file + 1)

    truncated = len(data) > profile.max_text_bytes_per_file
    inspected = data[: profile.max_text_bytes_per_file]
    if b"\x00" in inspected:
        return ScannedFile(canonical_path, "binary", None, truncated)

    try:
        text = inspected.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return ScannedFile(canonical_path, "unsupported_encoding", None, truncated)

    text = text.removeprefix("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    lines = text.splitlines(keepends=True)
    line_truncated = len(lines) > profile.max_lines_per_file
    if line_truncated:
        text = "".join(lines[: profile.max_lines_per_file])
    return ScannedFile(canonical_path, "text", text, truncated or line_truncated)


def _symlink_limitation(path: Path, boundary: WorkspaceBoundary) -> Limitation | None:
    canonical_path = path.relative_to(boundary.filesystem_root).as_posix()
    try:
        path.resolve(strict=True).relative_to(boundary.filesystem_root)
    except RuntimeError:
        return Limitation(
            code="symlink_loop",
            scope="file",
            detail="symlink loop was not followed",
            path=canonical_path,
        )
    except ValueError:
        return Limitation(
            code="symlink_escape",
            scope="file",
            detail="symlink target escaped the workspace",
            path=canonical_path,
        )
    except OSError:
        return Limitation(
            code="incomplete_coverage",
            scope="file",
            detail="symlink target could not be resolved",
            path=canonical_path,
        )
    return None


def _is_ignored(path: str, is_directory: bool) -> bool:
    parts = tuple(path.split("/"))
    if parts[0] == ".git":
        return True
    if len(parts) >= 2 and parts[:2] in {(".forgeflow", "cache"), (".forgeflow", "artifacts")}:
        return True
    return (
        len(parts) >= 5
        and parts[0:2] == ("openspec", "changes")
        and parts[3:5] == ("fixtures", "output")
    )
