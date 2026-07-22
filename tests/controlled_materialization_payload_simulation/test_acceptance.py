from __future__ import annotations

import unittest

from forgeflow.governed_changes.materialization.fake_adapter import reject_real_mutation_input
from forgeflow.governed_changes.materialization.models import MaterializationPDR, PayloadEligibilityPDR


class AcceptanceTest(unittest.TestCase):
    def test_real_surface_rejects_v1_authority_and_simulation_namespace(self):
        with self.assertRaises(ValueError):
            reject_real_mutation_input("forgeflow-sim-commit-not-a-provider-object")
        self.assertIsNone(reject_real_mutation_input("ordinary-real-input-is-outside-v1"))


if __name__ == "__main__":
    unittest.main()
