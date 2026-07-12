"""Deterministic input normalization for repository-context retrieval."""

from __future__ import annotations

from dataclasses import dataclass
import unicodedata

from .models import BoundedOptionalInput
from .profile import RepositoryContextProfile


@dataclass(frozen=True, slots=True)
class NormalizedQuery:
    normalized: str
    matching_view: str


def normalize_query(value: str) -> NormalizedQuery:
    """Normalize a query while retaining a separate casefolded match view."""
    normalized = _collapse_whitespace(value)
    return NormalizedQuery(normalized=normalized, matching_view=normalized.casefold())


def normalize_issue_text(
    value: str | None, profile: RepositoryContextProfile
) -> BoundedOptionalInput:
    """Return bounded input context without using it for retrieval."""
    if value is None:
        return BoundedOptionalInput(present=False, normalized="", truncated=False)

    normalized = _collapse_whitespace(value)
    bounded = normalized[: profile.max_issue_text_chars]
    return BoundedOptionalInput(
        present=True,
        normalized=bounded,
        truncated=len(normalized) > len(bounded),
    )


def normalized_matching_view(value: str) -> str:
    """Return the NFC, collapsed, casefolded view used for direct matching."""
    return _collapse_whitespace(value).casefold()


def _collapse_whitespace(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).split())
