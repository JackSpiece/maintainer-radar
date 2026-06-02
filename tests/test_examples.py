from __future__ import annotations

from pathlib import Path
import unittest

from maintainer_radar import __version__


ROOT = Path(__file__).resolve().parents[1]


class ExampleTests(unittest.TestCase):
    def test_github_action_examples_use_reusable_action(self) -> None:
        for path in (ROOT / "examples" / "github-actions").glob("*.yml"):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")

                self.assertIn(f"uses: JackSpiece/maintainer-radar@v{__version__}", text)
                self.assertIn("uses: actions/upload-artifact@v7", text)
                self.assertIn("GH_TOKEN: ${{ github.token }}", text)
                self.assertIn("path: ${{ steps.radar.outputs.report-path }}", text)
                self.assertNotIn("python -m pip install git+", text)


if __name__ == "__main__":
    unittest.main()
