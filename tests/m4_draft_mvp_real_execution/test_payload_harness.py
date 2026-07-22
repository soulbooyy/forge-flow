from __future__ import annotations

import unittest

from forgeflow.governed_changes.real_mutation.payload_harness import _mint_verified_fixture_source, transform_fixture_bytes


class FixturePayloadHarnessTest(unittest.TestCase):
    def test_registered_transform_replaces_only_the_return_operator(self):
        value = b"def add(left, right):\n    return left - right\n# - remains\n"

        self.assertEqual(transform_fixture_bytes(value), b"def add(left, right):\n    return left + right\n# - remains\n")

    def test_unverified_source_cannot_be_materialized(self):
        with self.assertRaises(ValueError):
            _mint_verified_fixture_source(b"unregistered source")


if __name__ == "__main__":
    unittest.main()
