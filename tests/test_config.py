from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from maintainer_radar.config import DEFAULT_CONFIG, load_config


class ConfigTests(unittest.TestCase):
    def test_missing_config_returns_defaults(self) -> None:
        self.assertEqual(load_config("/no/such/file.json"), DEFAULT_CONFIG)

    def test_load_config_merges_known_keys(self) -> None:
        config = load_config("tests/fixtures/maintainer-radar-config.json")

        self.assertEqual(config["large_diff_lines"], 20)
        self.assertEqual(config["stale_days"], 10)
        self.assertIn("specs/", config["test_hints"])

    def test_unknown_config_key_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text(json.dumps({"surprise": 1}), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_config(str(path))


if __name__ == "__main__":
    unittest.main()

