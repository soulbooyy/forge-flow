"""The sole concrete GitHub CLI seam for the registered fixture mutation."""

from __future__ import annotations

import base64
import json
import re
import subprocess
from typing import Protocol

from .fixture_registry import FIXTURE_TARGET_PATH


_REPOSITORY = "soulbooyy/forgeflow-m4-fixture"
_BASE_SHA = "97c8220cd713ebf61124ac2de2f3eadc6e4dc222"
_BASE_BRANCH = "main"
_BRANCH = re.compile(r"^forgeflow-governed-change-[0-9a-f]{12}$")
_SHA = re.compile(r"^[0-9a-f]{40}$")


class GhRunner(Protocol):
    def run(self, args: tuple[str, ...], input_bytes: bytes | None = None) -> str: ...


class GhNotFound(LookupError):
    """Only a verified GitHub HTTP 404 may mean a remote object is absent."""


class GhProviderFailure(LookupError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class SubprocessGhRunner:
    """Runs a fixed `gh` argv; it never accepts a shell string or credential."""

    def run(self, args: tuple[str, ...], input_bytes: bytes | None = None) -> str:
        completed = subprocess.run(args, input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if completed.returncode != 0:
            if b"HTTP 404" in completed.stderr:
                raise GhNotFound("github object is absent")
            if b"HTTP 401" in completed.stderr or b"HTTP 403" in completed.stderr:
                raise GhProviderFailure("credential_rejected")
            if b"HTTP 429" in completed.stderr:
                raise GhProviderFailure("rate_limited")
            if b"HTTP 422" in completed.stderr:
                raise GhProviderFailure("provider_rejected")
            raise GhProviderFailure("provider_unavailable")
        return completed.stdout.decode("utf-8")


class GitHubCliFixtureProvider:
    """Concrete fixture-only provider; credential resolution stays inside `gh`."""

    def __init__(self, runner: GhRunner | None = None) -> None:
        self._runner = runner or SubprocessGhRunner()

    def read_base_sha(self) -> str:
        return self._runner.run(("gh", "api", f"repos/{_REPOSITORY}/git/ref/heads/{_BASE_BRANCH}", "--jq", ".object.sha")).strip()

    def find_by_idempotency_key(self, key: str) -> tuple[str, str | None, str | None] | None:
        branch = "forgeflow-governed-change-" + key[7:19]
        try:
            commit = self._runner.run(("gh", "api", f"repos/{_REPOSITORY}/git/ref/heads/{branch}", "--jq", ".object.sha")).strip()
        except GhNotFound:
            return None
        except GhProviderFailure as error:
            if error.code != "provider_unavailable":
                raise
            raise GhProviderFailure("branch_lookup_failed") from None
        except Exception:
            raise GhProviderFailure("branch_lookup_failed") from None
        if not _SHA.fullmatch(commit):
            raise LookupError("branch ref did not return a commit SHA")
        try:
            records = json.loads(self._runner.run(("gh", "pr", "list", "--repo", _REPOSITORY, "--head", f"soulbooyy:{branch}", "--state", "all", "--limit", "2", "--json", "number,headRefOid")))
        except GhProviderFailure as error:
            if error.code != "provider_unavailable":
                raise
            raise GhProviderFailure("pr_lookup_failed") from None
        except Exception:
            raise GhProviderFailure("pr_lookup_failed") from None
        if not isinstance(records, list) or len(records) > 1:
            return (branch, None, None)
        if not records:
            return (branch, commit, None)
        record = records[0]
        if not isinstance(record, dict) or not isinstance(record.get("number"), int) or record.get("headRefOid") != commit:
            return (branch, None, None)
        return (branch, commit, str(record["number"]))

    def create_branch(self, branch_name: str, base_sha: str) -> str:
        if base_sha != _BASE_SHA or not _BRANCH.fullmatch(branch_name):
            raise ValueError("unregistered branch request")
        payload = {"ref": f"refs/heads/{branch_name}", "sha": _BASE_SHA}
        response = self._json(("gh", "api", "--method", "POST", f"repos/{_REPOSITORY}/git/refs", "--input", "-"), payload, "branch_create_failed")
        return branch_name if response.get("ref") == f"refs/heads/{branch_name}" else ""

    def create_commit(self, branch_name: str, target_path: str, content: bytes, message: str) -> str:
        if not _BRANCH.fullmatch(branch_name) or target_path != FIXTURE_TARGET_PATH or message != "fix: correct calculator addition":
            raise ValueError("unregistered commit request")
        base = self._json(("gh", "api", f"repos/{_REPOSITORY}/git/commits/{_BASE_SHA}"), None, "base_read_failed")
        tree_sha = base.get("tree", {}).get("sha") if isinstance(base.get("tree"), dict) else None
        if not isinstance(tree_sha, str) or not _SHA.fullmatch(tree_sha):
            raise GhProviderFailure("base_read_failed")
        blob = self._json(("gh", "api", "--method", "POST", f"repos/{_REPOSITORY}/git/blobs", "--input", "-"), {"content": base64.b64encode(content).decode("ascii"), "encoding": "base64"}, "blob_create_failed")
        blob_sha = blob.get("sha")
        if not isinstance(blob_sha, str) or not _SHA.fullmatch(blob_sha):
            raise GhProviderFailure("blob_create_failed")
        tree = self._json(("gh", "api", "--method", "POST", f"repos/{_REPOSITORY}/git/trees", "--input", "-"), {"base_tree": tree_sha, "tree": [{"path": FIXTURE_TARGET_PATH, "mode": "100644", "type": "blob", "sha": blob_sha}]}, "tree_create_failed")
        created_tree = tree.get("sha")
        if not isinstance(created_tree, str) or not _SHA.fullmatch(created_tree):
            raise GhProviderFailure("tree_create_failed")
        commit = self._json(("gh", "api", "--method", "POST", f"repos/{_REPOSITORY}/git/commits", "--input", "-"), {"message": message, "tree": created_tree, "parents": [_BASE_SHA]}, "commit_create_failed")
        commit_sha = commit.get("sha")
        if not isinstance(commit_sha, str) or not _SHA.fullmatch(commit_sha):
            raise GhProviderFailure("commit_create_failed")
        ref = self._json(("gh", "api", "--method", "PATCH", f"repos/{_REPOSITORY}/git/refs/heads/{branch_name}", "--input", "-"), {"sha": commit_sha, "force": False}, "branch_update_failed")
        response_sha = ref.get("object", {}).get("sha") if isinstance(ref.get("object"), dict) else None
        if ref.get("ref") != f"refs/heads/{branch_name}" or response_sha != commit_sha:
            raise GhProviderFailure("branch_update_failed")
        return commit_sha

    def create_draft_pr(self, branch_name: str, base_branch: str, title: str, body: str) -> str:
        if not _BRANCH.fullmatch(branch_name) or base_branch != _BASE_BRANCH or title != "Fix calculator addition bug" or body != "Closes #1.\n\nAutomated fixture-only draft PR.":
            raise ValueError("unregistered draft PR request")
        result = json.loads(self._runner.run(("gh", "pr", "create", "--repo", _REPOSITORY, "--base", _BASE_BRANCH, "--head", branch_name, "--title", title, "--body", body, "--draft", "--json", "number")))
        number = result.get("number") if isinstance(result, dict) else None
        if not isinstance(number, int):
            raise LookupError("draft PR creation did not return a number")
        return str(number)

    def _json(self, args: tuple[str, ...], payload: object | None, failure_code: str = "provider_unavailable") -> dict[str, object]:
        input_bytes = None if payload is None else json.dumps(payload, separators=(",", ":")).encode("utf-8")
        try:
            result = json.loads(self._runner.run(args, input_bytes))
        except Exception:
            raise GhProviderFailure(failure_code) from None
        if not isinstance(result, dict):
            raise LookupError("github provider response is not an object")
        return result
