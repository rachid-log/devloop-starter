"""Unit tests for .watched.json configuration validation."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from validate_config import (
    ALLOWED_DOMAINS,
    WATCH_FREQ_REGEX,
    validate_config,
    validate_config_file,
)


class TestValidateConfig(unittest.TestCase):
    """Test in-memory config validation dictionary checks."""

    def test_valid_default_config(self):
        config = {
            "goal": "Continuous stability, automated improvements, and domain optimization",
            "watch_freq": "1h",
            "domain": "BL",
            "active": True,
        }
        errors = validate_config(config)
        self.assertEqual(errors, [])

    def test_missing_required_fields(self):
        errors = validate_config({})
        self.assertIn("Missing required field: 'goal'", errors)
        self.assertIn("Missing required field: 'watch_freq'", errors)
        self.assertNotIn("Missing required field: 'domain'", errors)
        self.assertIn("Missing required field: 'active'", errors)

    def test_goal_validation(self):
        # Non-string
        self.assertTrue(any("goal" in e for e in validate_config({"goal": 123, "watch_freq": "1h", "domain": "BL", "active": True})))
        # Empty string
        self.assertTrue(any("goal" in e for e in validate_config({"goal": "", "watch_freq": "1h", "domain": "BL", "active": True})))
        # Whitespace-only string
        self.assertTrue(any("goal" in e for e in validate_config({"goal": "   ", "watch_freq": "1h", "domain": "BL", "active": True})))
        # Valid string
        self.assertEqual(validate_config({"goal": "Fix bugs", "watch_freq": "1h", "domain": "BL", "active": True}), [])

    def test_watch_freq_validation(self):
        valid_intervals = ["30m", "1h", "4h", "1d", "7d"]
        for interval in valid_intervals:
            errors = validate_config({"goal": "Fix bugs", "watch_freq": interval, "domain": "BL", "active": True})
            self.assertEqual(errors, [], f"Expected {interval} to be valid")

        invalid_intervals = ["", "10s", "10w", "1hour", "-1h", "h", "0", 123, None]
        for interval in invalid_intervals:
            errors = validate_config({"goal": "Fix bugs", "watch_freq": interval, "domain": "BL", "active": True})
            self.assertTrue(any("watch_freq" in e for e in errors), f"Expected {interval} to be invalid")

    def test_domain_validation(self):
        for domain in ALLOWED_DOMAINS:
            errors = validate_config({"goal": "Fix bugs", "watch_freq": "1h", "domain": domain, "active": True})
            self.assertEqual(errors, [], f"Expected {domain} to be valid")

        invalid_domains = ["frontend", "bl", "backend", "Security2", "", 123, None]
        for domain in invalid_domains:
            errors = validate_config({"goal": "Fix bugs", "watch_freq": "1h", "domain": domain, "active": True})
            self.assertTrue(any("domain" in e for e in errors), f"Expected {domain} to be invalid")

    def test_facets_validation(self):
        base = {"goal": "Fix bugs", "watch_freq": "1h", "active": True}
        for facets in ([], ["ux", "seo"], ["a11y"]):
            self.assertEqual(validate_config(dict(base, facets=facets)), [], facets)
        for facets in ("ux", ["UX/UI"], ["nope"], None):
            errors = validate_config(dict(base, facets=facets))
            self.assertTrue(any("facets" in e for e in errors), facets)

    def test_domains_per_cycle_validation(self):
        base = {"goal": "Fix bugs", "watch_freq": "1h", "active": True}
        for count in (1, 3, 5):
            self.assertEqual(validate_config(dict(base, domains_per_cycle=count)), [])
        for count in (0, 6, "2", 1.5, True):
            errors = validate_config(dict(base, domains_per_cycle=count))
            self.assertTrue(any("domains_per_cycle" in e for e in errors), count)

    def test_active_validation(self):
        self.assertEqual(validate_config({"goal": "Fix bugs", "watch_freq": "1h", "domain": "BL", "active": True}), [])
        self.assertEqual(validate_config({"goal": "Fix bugs", "watch_freq": "1h", "domain": "BL", "active": False}), [])

        invalid_actives = ["true", "false", 1, 0, None, [], {}]
        for val in invalid_actives:
            errors = validate_config({"goal": "Fix bugs", "watch_freq": "1h", "domain": "BL", "active": val})
            self.assertTrue(any("active" in e for e in errors), f"Expected active={val!r} to be invalid")


class TestValidateConfigFile(unittest.TestCase):
    """Test file-based validation checks."""

    def test_repo_watched_json(self):
        repo_root = Path(__file__).resolve().parent
        watched_path = repo_root / ".watched.json"
        is_valid, errors = validate_config_file(watched_path)
        self.assertTrue(is_valid, f"Expected .watched.json to be valid, got errors: {errors}")
        self.assertEqual(errors, [])

    def test_nonexistent_file(self):
        is_valid, errors = validate_config_file("nonexistent_file_path.json")
        self.assertFalse(is_valid)
        self.assertTrue(any("does not exist" in e for e in errors))

    def test_invalid_json_file(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as tmp:
            tmp.write("{bad json")
            tmp_path = tmp.name
        try:
            is_valid, errors = validate_config_file(tmp_path)
            self.assertFalse(is_valid)
            self.assertTrue(any("Invalid JSON" in e for e in errors))
        finally:
            os.remove(tmp_path)

    def test_non_dict_json_file(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as tmp:
            tmp.write('["not", "a", "dict"]')
            tmp_path = tmp.name
        try:
            is_valid, errors = validate_config_file(tmp_path)
            self.assertFalse(is_valid)
            self.assertTrue(any("must be a JSON object" in e for e in errors))
        finally:
            os.remove(tmp_path)


class TestCliExecution(unittest.TestCase):
    """Test command line execution of validate_config.py."""

    def test_cli_success_default_file(self):
        res = subprocess.run(
            [sys.executable, "validate_config.py"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("valid", res.stdout)

    def test_cli_failure_on_invalid_file(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as tmp:
            tmp.write('{"domain": "INVALID"}')
            tmp_path = tmp.name
        try:
            res = subprocess.run(
                [sys.executable, "validate_config.py", tmp_path],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 1)
            self.assertIn("Missing required field", res.stderr)
        finally:
            os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
