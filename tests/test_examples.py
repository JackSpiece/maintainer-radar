from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_ACTION_VERSION = "v0.20.0"


class ExampleTests(unittest.TestCase):
    def test_github_action_examples_use_reusable_action(self) -> None:
        for path in (ROOT / "examples" / "github-actions").glob("*.yml"):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")

                self.assertIn(
                    f"uses: JackSpiece/maintainer-radar@{PUBLISHED_ACTION_VERSION}",
                    text,
                )
                self.assertNotIn("maintainer-radar@v0.21.0", text)
                self.assertIn("uses: actions/upload-artifact@v7", text)
                self.assertIn("GH_TOKEN: ${{ github.token }}", text)
                self.assertIn("path: ${{ steps.radar.outputs.report-path }}", text)
                self.assertNotIn("python -m pip install git+", text)


if __name__ == "__main__":
    unittest.main()
