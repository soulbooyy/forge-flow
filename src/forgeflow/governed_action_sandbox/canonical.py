"""Canonical UTF-8 JSON and self-excluding immutable M4 identities."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields, is_dataclass
import hashlib
import json

from .models import ActionIntent, CommandIntent, ExecutionAttempt, GovernedActionSandboxValidationError, PolicyDecisionRecord


def canonical_bytes(value: object, *, omit_fields: frozenset[str] = frozenset()) -> bytes:
    return json.dumps(_value(value, omit_fields), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_hex(value: object, *, omit_fields: frozenset[str] = frozenset()) -> str:
    return hashlib.sha256(canonical_bytes(value, omit_fields=omit_fields)).hexdigest()


def action_intent_id_for(value: ActionIntent) -> str:
    return f"ai_sha256:{sha256_hex(value, omit_fields=frozenset({'contract_id', 'action_id', 'created_at'}))}"


def command_intent_id_for(value: CommandIntent) -> str:
    return f"ci_sha256:{sha256_hex(value, omit_fields=frozenset({'contract_id', 'created_at'}))}"


def policy_decision_id_for(value: PolicyDecisionRecord) -> str:
    return f"pdr_sha256:{sha256_hex(value, omit_fields=frozenset({'contract_id', 'decision_id', 'created_at'}))}"


def input_lineage_digest_for(action: ActionIntent, command: CommandIntent) -> str:
    """Return the canonical PDR input digest for the current immutable intent pair."""
    return "sha256:" + sha256_hex(
        {
            "action_intent_contract_id": action.contract_id,
            "command_intent_contract_id": command.contract_id,
            "repository_id": command.repository_id,
            "base_commit_sha": command.base_commit_sha,
            "policy_profile_id": command.policy_profile_id,
            "policy_profile_version": command.policy_profile_version,
            "oci_image_digest": command.oci_image_digest,
        }
    )


def execution_attempt_id_for(value: ExecutionAttempt) -> str:
    return f"ea_sha256:{sha256_hex(value, omit_fields=frozenset({'contract_id', 'attempt_id', 'created_at'}))}"


def validation_error_id_for(value: GovernedActionSandboxValidationError) -> str:
    return f"gase_sha256:{sha256_hex(value, omit_fields=frozenset({'error_id'}))}"


def _value(value: object, omit_fields: frozenset[str]) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        raise TypeError("floats are not supported in canonical JSON")
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _value(getattr(value, field.name), omit_fields) for field in fields(value) if field.name not in omit_fields and getattr(value, field.name) is not None}
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise TypeError("canonical JSON mapping keys must be strings")
        return {key: _value(item, omit_fields) for key, item in value.items() if key not in omit_fields and item is not None}
    if isinstance(value, (list, tuple)):
        return [_value(item, omit_fields) for item in value]
    raise TypeError(f"unsupported canonical JSON value: {type(value).__name__}")
