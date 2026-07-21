import hashlib
import json
from dataclasses import asdict


def _id(value: object, field: str) -> str:
    data = asdict(value)
    data.pop(field)
    return "sha256:" + hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def request_id_for(value: object) -> str: return _id(value, "request_id")
def terminal_id_for(value: object) -> str: return _id(value, "terminal_id")
def idempotency_record_id_for(value: object) -> str: return _id(value, "record_id")
def pr_result_id_for(value: object) -> str: return _id(value, "result_id")
