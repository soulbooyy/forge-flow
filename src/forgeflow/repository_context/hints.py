"""Root-only, descriptive test-command hint discovery."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace
import json
from pathlib import Path

from .canonical import evidence_id_for
from .models import EvidenceRef, Limitation, TestCommandHint
from .workspace import WorkspaceBoundary


@dataclass(frozen=True, slots=True)
class HintDiscovery:
    hints: tuple[TestCommandHint, ...]
    evidence_refs: tuple[EvidenceRef, ...]
    limitations: tuple[Limitation, ...]


def discover_test_hints(boundary: WorkspaceBoundary) -> HintDiscovery:
    """Discover only strict root package and Makefile test hints."""
    discoveries: list[tuple[TestCommandHint, EvidenceRef]] = []
    limitations: list[Limitation] = []

    package_path = boundary.filesystem_root / "package.json"
    if _is_root_file(package_path):
        try:
            parsed = json.loads(package_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            limitations.append(
                Limitation(
                    code="malformed_metadata",
                    scope="file",
                    detail="root package metadata could not be parsed",
                    path="package.json",
                )
            )
        else:
            test_command = _package_test_command(parsed)
            if test_command is not None:
                discoveries.append(_hint_with_evidence(test_command, "package.json"))

    makefile_path = boundary.filesystem_root / "Makefile"
    if _is_root_file(makefile_path):
        try:
            makefile_text = makefile_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            limitations.append(
                Limitation(
                    code="malformed_metadata",
                    scope="file",
                    detail="root Makefile metadata could not be read",
                    path="Makefile",
                )
            )
        else:
            if _has_test_target(makefile_text):
                discoveries.append(_hint_with_evidence("make test", "Makefile"))

    ordered = tuple(sorted(discoveries, key=lambda item: (item[0].command, item[0].source)))
    return HintDiscovery(
        hints=tuple(item[0] for item in ordered),
        evidence_refs=tuple(item[1] for item in ordered),
        limitations=tuple(limitations),
    )


def _is_root_file(path: Path) -> bool:
    return path.is_file() and not path.is_symlink()


def _package_test_command(value: object) -> str | None:
    if not isinstance(value, dict):
        return None
    scripts = value.get("scripts")
    if not isinstance(scripts, dict) or not isinstance(scripts.get("test"), str):
        return None
    return "npm test"


def _has_test_target(makefile_text: str) -> bool:
    for line in makefile_text.splitlines():
        if not line or line.startswith(("\t", "#")) or ":" not in line:
            continue
        targets, _ = line.split(":", 1)
        target_names = targets.split()
        if target_names == ["test"]:
            return True
    return False


def _hint_with_evidence(command: str, source: str) -> tuple[TestCommandHint, EvidenceRef]:
    reference = EvidenceRef(
        id="",
        evidence_kind="file_test_hint",
        retrieval_signal="test_hint",
        locator=None,
        path=source,
    )
    reference = replace(reference, id=evidence_id_for(reference))
    return (
        TestCommandHint(command=command, source=source, evidence_ref_ids=(reference.id,)),
        reference,
    )
