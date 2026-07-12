"""Deterministic validation-envelope construction."""

from __future__ import annotations

from dataclasses import replace

from .canonical import error_id_for
from .models import (
    RepositoryContextRequest,
    RepositoryContextValidationError,
    ValidationErrorSummary,
)
from .normalization import NormalizedQuery
from .profile import RepositoryContextProfile


def validate_request(
    request: RepositoryContextRequest,
    query: NormalizedQuery,
    profile: RepositoryContextProfile,
) -> RepositoryContextValidationError | None:
    """Validate profile and query inputs after workspace validation succeeds."""
    if request.configuration_profile_id != profile.configuration_profile_id:
        return build_validation_error(
            request,
            error_code="invalid_config_profile",
            input_category="configuration_profile",
            message="configuration profile is not supported",
            query_present=bool(query.normalized),
        )
    if not query.normalized:
        return build_validation_error(
            request,
            error_code="empty_query",
            input_category="query",
            message="query must not be empty",
            query_present=False,
        )
    if len(query.normalized) > profile.max_query_chars:
        return build_validation_error(
            request,
            error_code="query_too_large",
            input_category="query",
            message="query exceeds the configured limit",
            query_present=True,
        )
    return None


def build_validation_error(
    request: RepositoryContextRequest,
    *,
    error_code: str,
    input_category: str,
    message: str,
    query_present: bool,
) -> RepositoryContextValidationError:
    """Build a stable validation envelope without host-path details."""
    error = RepositoryContextValidationError(
        error_id="",
        error_code=error_code,
        input_category=input_category,
        message=message,
        summary=ValidationErrorSummary(
            workspace_root_id=request.workspace_ref.root_id,
            configuration_profile_id=request.configuration_profile_id,
            query_present=query_present,
        ),
    )
    return replace(error, error_id=error_id_for(error))
