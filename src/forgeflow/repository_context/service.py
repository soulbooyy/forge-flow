"""Public deterministic Repository Context Service entry point."""

from __future__ import annotations

from .assembly import assemble_with_hints
from .hints import discover_test_hints
from .matching import match_scanned_files
from .models import (
    NormalizedInput,
    RepositoryContextEnvelope,
    RepositoryContextRequest,
)
from .normalization import normalize_issue_text, normalize_query
from .profile import M1_DEFAULTS
from .scanner import scan_workspace
from .validation import build_validation_error, validate_request
from .workspace import WorkspaceBoundary, WorkspaceBoundaryError


def inspect_repository(request: RepositoryContextRequest) -> RepositoryContextEnvelope:
    """Inspect a workspace through deterministic, read-only Repository Context rules."""
    query = normalize_query(request.query)
    try:
        boundary = WorkspaceBoundary.create(request.workspace_root, request.workspace_ref.root_id)
        boundary.validate_workspace_ref(request.workspace_ref)
    except WorkspaceBoundaryError as error:
        return build_validation_error(
            request,
            error_code=error.code,
            input_category="workspace",
            message="workspace input is not valid",
            query_present=bool(query.normalized),
        )

    validation_error = validate_request(request, query, M1_DEFAULTS)
    if validation_error is not None:
        return validation_error

    issue_text = normalize_issue_text(request.issue_text, M1_DEFAULTS)
    scan_report = scan_workspace(boundary, M1_DEFAULTS)
    matches = match_scanned_files(scan_report.files, query, M1_DEFAULTS)
    hints = discover_test_hints(boundary)
    return assemble_with_hints(
        workspace_ref=request.workspace_ref,
        query=NormalizedInput(normalized=query.normalized),
        issue_text=issue_text,
        scan_report=scan_report,
        matches=matches,
        discovery=hints,
        profile=M1_DEFAULTS,
    )
