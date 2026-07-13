"""Deterministic canonical JSON and identity helpers for PatchProposal contracts."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields, is_dataclass
import hashlib
import json

from .models import (
    CandidateChange,
    PatchProposal,
    PatchProposalValidationError,
    PolicyDecisionRef,
)


def canonical_bytes(value: object, *, omit_fields: frozenset[str] = frozenset()) -> bytes:
    """Serialize supported contract values as deterministic UTF-8 JSON bytes."""
    return json.dumps(
        _canonical_value(value, omit_fields),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_hex(value: object, *, omit_fields: frozenset[str] = frozenset()) -> str:
    """Return the SHA-256 hex digest of a canonical contract value."""
    return hashlib.sha256(canonical_bytes(value, omit_fields=omit_fields)).hexdigest()


def proposal_id_for(value: PatchProposal) -> str:
    """Return the stable identity for a successful PatchProposal."""
    return f"pp_sha256:{sha256_hex(value, omit_fields=frozenset({'contract_id'}))}"


def proposal_error_id_for(value: PatchProposalValidationError) -> str:
    """Return the stable identity for a PatchProposal validation error."""
    return f"ppe_sha256:{sha256_hex(value, omit_fields=frozenset({'error_id'}))}"


def candidate_digest_for(changes: tuple[CandidateChange, ...]) -> str:
    """Return the identity input digest for ordered candidate intent tuples."""
    intent_tuples = tuple(
        (change.path, change.change_kind, change.rationale) for change in changes
    )
    return f"sha256:{sha256_hex(intent_tuples)}"


def policy_decision_id_for(value: PolicyDecisionRef) -> str:
    """Return the stable identity for a policy decision reference."""
    return f"pdr_sha256:{sha256_hex(value, omit_fields=frozenset({'decision_id'}))}"


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
