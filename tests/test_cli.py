import json
import tempfile
import unittest
from pathlib import Path

from black_scholes.cli import load_json_config


class FileHandlerTests(unittest.TestCase):
    def test_json_config_is_loaded_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "option.json"
            expected = {"spot": 100, "strike": 100, "volatility": 0.2}
            config_path.write_text(json.dumps(expected), encoding="utf-8")

            self.assertEqual(load_json_config(config_path), expected)
            self.assertEqual(json.loads(config_path.read_text(encoding="utf-8")), expected)

    def test_missing_config_has_a_clear_error(self):
        with self.assertRaisesRegex(ValueError, "configuration file not found"):
            load_json_config("missing-option-config.json")


if __name__ == "__main__":
    unittest.main()
