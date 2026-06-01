from __future__ import annotations

from pathlib import Path
import re
import unittest

from maintainer_radar import __version__


ROOT = Path(__file__).resolve().parents[1]


class MetadataTests(unittest.TestCase):
    def test_package_version_matches_project_version(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        match = re.search(r'^version = "([^"]+)"$', pyproject, re.MULTILINE)

        self.assertIsNotNone(match)
        self.assertEqual(__version__, match.group(1))

    def test_readme_quick_start_leads_with_github_action(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("## Quick Start", readme)
        self.assertLess(
            readme.index("JackSpiece/maintainer-radar@"),
            readme.index('python -m pip install "git+https://github.com/JackSpiece/maintainer-radar.git"'),
        )


if __name__ == "__main__":
    unittest.main()
