import hashlib
import json
from dataclasses import asdict


def _id(value: object, field: str) -> str:
    fields = asdict(value)
    fields.pop(field)
    canonical = json.dumps(fields, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def request_id_for(value: object) -> str: return _id(value, "request_id")
def decision_id_for(value: object) -> str: return _id(value, "decision_id")
def artifact_reference_id_for(value: object) -> str: return _id(value, "artifact_reference_id")
def event_id_for(value: object) -> str: return _id(value, "event_id")
def summary_id_for(value: object) -> str: return _id(value, "summary_id")
