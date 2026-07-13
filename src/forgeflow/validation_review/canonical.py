"""Canonical serialization and independent identities for M3 contracts."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
import hashlib
import json
from typing import Any

from .models import (
    PolicyDecisionRecordRef,
    ReviewResult,
    ValidationResult,
    ValidationReviewError,
    ValidationTerminal,
)


def canonical_bytes(value: object, *, omit_fields: frozenset[str] = frozenset()) -> bytes:
    """Return compact, sorted UTF-8 JSON for supported immutable contract values."""

    return json.dumps(
        _canonical_value(value, omit_fields=omit_fields),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def validation_result_id_for(value: ValidationResult) -> str:
    return _hash_id("vr_sha256:", value, "contract_id")


def validation_terminal_id_for(value: ValidationTerminal) -> str:
    return _hash_id("vt_sha256:", value, "terminal_id")


def review_result_id_for(value: ReviewResult) -> str:
    return _hash_id("rr_sha256:", value, "contract_id")


def validation_review_error_id_for(value: ValidationReviewError) -> str:
    return _hash_id("vre_sha256:", value, "error_id")


def policy_decision_id_for(value: PolicyDecisionRecordRef) -> str:
    return _hash_id("pdr_sha256:", value, "decision_id")


def _hash_id(prefix: str, value: object, identity_field: str) -> str:
    return prefix + hashlib.sha256(canonical_bytes(value, omit_fields=frozenset({identity_field}))).hexdigest()


def _canonical_value(value: object, *, omit_fields: frozenset[str]) -> Any:
    if isinstance(value, float):
        raise ValueError("floats are not supported in canonical contract values")
    if is_dataclass(value) and not isinstance(value, type):
        return {
            item.name: _canonical_value(getattr(value, item.name), omit_fields=frozenset())
            for item in fields(value)
            if item.name not in omit_fields
        }
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ValueError("canonical object keys must be strings")
        return {key: _canonical_value(item, omit_fields=frozenset()) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_canonical_value(item, omit_fields=frozenset()) for item in value]
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise ValueError("unsupported canonical contract value")
