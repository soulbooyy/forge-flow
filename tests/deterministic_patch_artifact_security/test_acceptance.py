"""Phase 4 terminal-first acceptance checks."""
from __future__ import annotations
from dataclasses import asdict, replace
import unittest
from forgeflow.deterministic_patch_artifact_security.models import PatchSecurityTerminal
from forgeflow.deterministic_patch_artifact_security.service import build_patch_security_facts
from tests.deterministic_patch_artifact_security.test_service import R, B, proposal

class AcceptanceTests(unittest.TestCase):
    def test_secret_like_input_yields_only_nonreversible_terminal(self):
        marker = "ghp_abcdefghijklmnopqrstuvwx"
        result = build_patch_security_facts(proposal("token=" + marker), R, B)
        self.assertIsInstance(result, PatchSecurityTerminal)
        self.assertEqual(result.terminal_status, "blocked")
        self.assertEqual(result.terminal_reason, "security_rule_blocked")
        self.assertNotIn(marker, repr(asdict(result)))
        self.assertFalse(hasattr(result, "patch_intent"))
        self.assertFalse(hasattr(result, "patch_artifact"))
        self.assertFalse(hasattr(result, "candidate"))
        for forbidden in ("approval", "execution", "write", "persist", "publish", "durable_reference"):
            self.assertFalse(any(forbidden in key for key in asdict(result)))

    def test_feature_package_has_no_side_effect_surface(self):
        from pathlib import Path
        root = Path(__file__).parents[2] / "src/forgeflow/deterministic_patch_artifact_security"
        paths = tuple(root.glob("*.py"))
        self.assertTrue(paths)
        source = "\n".join(path.read_text() for path in paths)
        for forbidden in ("subprocess", "socket", "requests", "urllib", "httpx", "os.system"):
            self.assertNotIn(forbidden, source)

if __name__ == "__main__": unittest.main()
