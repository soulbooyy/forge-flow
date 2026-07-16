"""Canonical JSON and identity helpers for Feature 2 contracts."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields, is_dataclass
import hashlib
import json

from .models import (
    DeterministicPatchArtifactSecurityValidationError,
    PatchArtifact,
    PatchIntent,
    RedactionFact,
    SecretScanResult,
)


def canonical_bytes(value: object, *, omit_fields: frozenset[str] = frozenset()) -> bytes:
    """Serialize supported values as deterministic UTF-8 JSON."""
    return json.dumps(
        _canonical_value(value, omit_fields),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_hex(value: object, *, omit_fields: frozenset[str] = frozenset()) -> str:
    """Return a lowercase SHA-256 hexadecimal digest."""
    return hashlib.sha256(canonical_bytes(value, omit_fields=omit_fields)).hexdigest()


def intent_id_for(value: PatchIntent) -> str:
    return f"sha256:{sha256_hex(value, omit_fields=frozenset({'intent_id'}))}"


def artifact_id_for(value: PatchArtifact) -> str:
    return f"sha256:{sha256_hex(value, omit_fields=frozenset({'artifact_id'}))}"


def scan_id_for(value: SecretScanResult) -> str:
    return f"sha256:{sha256_hex(value, omit_fields=frozenset({'scan_id'}))}"


def redaction_id_for(value: RedactionFact) -> str:
    return f"sha256:{sha256_hex(value, omit_fields=frozenset({'redaction_id'}))}"


def validation_error_id_for(value: DeterministicPatchArtifactSecurityValidationError) -> str:
    return f"sha256:{sha256_hex(value, omit_fields=frozenset({'error_id'}))}"


def _canonical_value(value: object, omit_fields: frozenset[str]) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        raise TypeError("floats are not supported in canonical JSON")
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _canonical_value(getattr(value, field.name), omit_fields)
            for field in fields(value)
            if field.name not in omit_fields and getattr(value, field.name) is not None
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
