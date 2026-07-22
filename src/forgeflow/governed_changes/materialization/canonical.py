"""Canonical JSON and self-excluding identities for M4 payload contracts."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields, is_dataclass
import hashlib
import json


def canonical_bytes(value: object, *, omit_fields: frozenset[str] = frozenset()) -> bytes:
    return json.dumps(
        _canonical_value(value, omit_fields), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_hex(value: object, *, omit_fields: frozenset[str] = frozenset()) -> str:
    return hashlib.sha256(canonical_bytes(value, omit_fields=omit_fields)).hexdigest()


def materialization_pdr_id_for(value: object) -> str:
    return f"sha256:{sha256_hex(value, omit_fields=frozenset({'pdr_id'}))}"


def materialized_payload_id_for(value: object) -> str:
    return f"sha256:{sha256_hex(value, omit_fields=frozenset({'payload_id'}))}"


def payload_eligibility_pdr_id_for(value: object) -> str:
    return f"sha256:{sha256_hex(value, omit_fields=frozenset({'pdr_id'}))}"


def terminal_id_for(value: object) -> str:
    return f"sha256:{sha256_hex(value, omit_fields=frozenset({'terminal_id'}))}"


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
        return {key: _canonical_value(item, omit_fields) for key, item in value.items() if key not in omit_fields and item is not None}
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item, omit_fields) for item in value]
    raise TypeError(f"unsupported canonical JSON value: {type(value).__name__}")
