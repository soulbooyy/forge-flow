from __future__ import annotations

import json
import unittest

from forgeflow.governed_changes.real_mutation.github_cli import GhNotFound, GitHubCliFixtureProvider


class FakeRunner:
    def __init__(self, responses: list[str | Exception]) -> None:
        self.responses = responses
        self.calls: list[tuple[tuple[str, ...], bytes | None]] = []

    def run(self, args: tuple[str, ...], input_bytes: bytes | None = None) -> str:
        self.calls.append((args, input_bytes))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class GitHubCliFixtureProviderTest(unittest.TestCase):
    def test_reads_only_registered_main_base(self):
        runner = FakeRunner(["97c8220cd713ebf61124ac2de2f3eadc6e4dc222\n"])
        provider = GitHubCliFixtureProvider(runner)

        self.assertEqual(provider.read_base_sha(), "97c8220cd713ebf61124ac2de2f3eadc6e4dc222")
        self.assertEqual(runner.calls[0][0], ("gh", "api", "repos/soulbooyy/forgeflow-m4-fixture/git/ref/heads/main", "--jq", ".object.sha"))

    def test_commit_uses_git_data_api_with_base64_content_and_no_shell(self):
        runner = FakeRunner([
            '{"tree":{"sha":"' + "b" * 40 + '"}}',
            '{"sha":"' + "c" * 40 + '"}',
            '{"sha":"' + "d" * 40 + '"}',
            '{"sha":"' + "e" * 40 + '"}',
            '{"ref":"refs/heads/forgeflow-governed-change-aaaaaaaaaaaa","object":{"sha":"' + "e" * 40 + '"}}',
        ])
        provider = GitHubCliFixtureProvider(runner)

        commit = provider.create_commit("forgeflow-governed-change-aaaaaaaaaaaa", "calculator.py", b"return left + right\n", "fix: correct calculator addition")

        self.assertEqual(commit, "e" * 40)
        blob_args, blob_body = runner.calls[1]
        self.assertEqual(blob_args[:5], ("gh", "api", "--method", "POST", "repos/soulbooyy/forgeflow-m4-fixture/git/blobs"))
        self.assertEqual(json.loads(blob_body or b"{}"), {"content": "cmV0dXJuIGxlZnQgKyByaWdodAo=", "encoding": "base64"})
        self.assertTrue(all(call[0][0] == "gh" for call in runner.calls))
        self.assertTrue(all("sh" not in arg for call, _ in runner.calls for arg in call))

    def test_rejects_foreign_branch_or_commit_target_before_cli(self):
        runner = FakeRunner([])
        provider = GitHubCliFixtureProvider(runner)

        with self.assertRaises(ValueError):
            provider.create_branch("other-branch", "97c8220cd713ebf61124ac2de2f3eadc6e4dc222")
        with self.assertRaises(ValueError):
            provider.create_commit("forgeflow-governed-change-aaaaaaaaaaaa", "other.py", b"x", "fix: correct calculator addition")
        with self.assertRaises(ValueError):
            provider.create_draft_pr("forgeflow-governed-change-aaaaaaaaaaaa", "other", "Fix calculator addition bug", "Closes #1.\n\nAutomated fixture-only draft PR.")

        self.assertEqual(runner.calls, [])

    def test_reconciliation_only_accepts_verified_not_found(self):
        not_found = GitHubCliFixtureProvider(FakeRunner([GhNotFound("missing")]))
        unavailable = GitHubCliFixtureProvider(FakeRunner([LookupError("unavailable")]))

        self.assertIsNone(not_found.find_by_idempotency_key("sha256:" + "a" * 64))
        with self.assertRaises(LookupError):
            unavailable.find_by_idempotency_key("sha256:" + "a" * 64)

    def test_malformed_git_identity_stops_before_following_write(self):
        runner = FakeRunner(['{"tree":{"sha":"' + "b" * 40 + '"}}', '{"sha":"not-a-sha"}'])
        provider = GitHubCliFixtureProvider(runner)

        with self.assertRaises(LookupError):
            provider.create_commit("forgeflow-governed-change-aaaaaaaaaaaa", "calculator.py", b"x", "fix: correct calculator addition")

        self.assertEqual(len(runner.calls), 2)


if __name__ == "__main__":
    unittest.main()
