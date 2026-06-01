from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ActionMetadataTests(unittest.TestCase):
    def test_action_metadata_exposes_composite_action_contract(self) -> None:
        action = (ROOT / "action.yml").read_text(encoding="utf-8")

        self.assertIn("name: Maintainer Radar", action)
        self.assertIn("branding:", action)
        self.assertIn("icon: activity", action)
        self.assertIn("using: composite", action)
        self.assertIn("repository:", action)
        self.assertIn("format:", action)
        self.assertIn("step-summary:", action)
        self.assertIn("report-path:", action)
        self.assertIn("value: ${{ steps.build.outputs.report-path }}", action)

    def test_action_installs_local_package_and_uses_read_only_cli(self) -> None:
        action = (ROOT / "action.yml").read_text(encoding="utf-8")

        self.assertIn('python -m pip install "$GITHUB_ACTION_PATH"', action)
        self.assertIn('maintainer-radar repo "$repository"', action)
        self.assertIn('--summary-only', action)
        self.assertIn('>> "$GITHUB_STEP_SUMMARY"', action)
        self.assertNotIn("gh pr comment", action)
        self.assertNotIn("pull-requests: write", action)

    def test_action_derives_output_path_from_report_format(self) -> None:
        action = (ROOT / "action.yml").read_text(encoding="utf-8")

        self.assertIn('markdown) default_output="maintainer-radar.md"', action)
        self.assertIn('html) default_output="maintainer-radar.html"', action)
        self.assertIn('json) default_output="maintainer-radar.json"', action)
        self.assertIn('csv) default_output="maintainer-radar.csv"', action)
        self.assertIn('output="${INPUT_OUTPUT:-$default_output}"', action)
        self.assertIn('echo "report-path=$output" >> "$GITHUB_OUTPUT"', action)


if __name__ == "__main__":
    unittest.main()
