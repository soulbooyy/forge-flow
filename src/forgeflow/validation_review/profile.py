"""Immutable controlled values for the deterministic M3 fixture profile."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValidationReviewFixtureProfile:
    policy_profile_id: str = "validation-review/m3-fixture-v1"
    policy_version: int = 1
    evaluator_id: str = "m3/deterministic-policy-fixture-v1"
    max_finding_codes: int = 5
    max_evidence_refs: int = 10
    max_artifact_ids: int = 10
    max_review_findings: int = 5
    allowed_risk_flags: tuple[str, ...] = (
        "blocked_by_policy",
        "human_approval_required",
        "review_blocking_finding",
    )
    allowed_validation_finding_codes: tuple[str, ...] = (
        "fixture_assertion_failed",
        "fixture_test_insufficient",
    )
    allowed_review_finding_codes: tuple[str, ...] = (
        "validation_failure_requires_review",
        "fixture_security_concern",
    )
    forbidden_payload_field_names: tuple[str, ...] = (
        "command",
        "exit_code",
        "stdout",
        "stderr",
        "output",
        "raw_output",
        "report_payload",
        "environment",
        "source",
        "prompt",
    )


M3_FIXTURE_V1 = ValidationReviewFixtureProfile()
