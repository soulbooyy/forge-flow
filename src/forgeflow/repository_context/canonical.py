"""Deterministic canonical JSON and identity helpers for repository contracts."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields, is_dataclass
import hashlib
import json

from .models import (
    EvidenceRef,
    RepositoryContextResult,
    RepositoryContextValidationError,
)


def canonical_bytes(value: object, *, omit_fields: frozenset[str] = frozenset()) -> bytes:
    """Serialize supported contract values as deterministic UTF-8 JSON bytes."""
    canonical_value = _canonical_value(value, omit_fields)
    return json.dumps(
        canonical_value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_hex(value: object, *, omit_fields: frozenset[str] = frozenset()) -> str:
    """Return the SHA-256 hex digest of a canonical contract value."""
    return hashlib.sha256(canonical_bytes(value, omit_fields=omit_fields)).hexdigest()


def contract_id_for(result: RepositoryContextResult) -> str:
    """Return the stable identity for a repository context result."""
    return f"rcr_sha256:{sha256_hex(result, omit_fields=frozenset({'contract_id'}))}"


def evidence_id_for(evidence: EvidenceRef) -> str:
    """Return the stable identity for an evidence reference."""
    return f"ev_sha256:{sha256_hex(evidence, omit_fields=frozenset({'id'}))}"


def error_id_for(error: RepositoryContextValidationError) -> str:
    """Return the stable identity for a repository context validation error."""
    return f"rce_sha256:{sha256_hex(error, omit_fields=frozenset({'error_id'}))}"


def _canonical_value(value: object, omit_fields: frozenset[str]) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        raise TypeError("floats are not supported in canonical JSON")
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _canonical_value(getattr(value, field.name), omit_fields)
            for field in fields(value)
            if field.name not in omit_fields
            and (
                getattr(value, field.name) is not None
                or (isinstance(value, EvidenceRef) and field.name == "locator")
            )
        }
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise TypeError("canonical JSON mapping keys must be strings")
        return {
            key: _canonical_value(item, omit_fields)
            for key, item in value.items()
            if key not in omit_fields and item is not None
        }
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item, omit_fields) for item in value]
    raise TypeError(f"unsupported canonical JSON value: {type(value).__name__}")
