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
        self.assertIn("label:", action)
        self.assertIn("stale-days:", action)
        self.assertIn("min-score:", action)
        self.assertIn("group-by:", action)
        self.assertIn("config:", action)
        self.assertIn("step-summary:", action)
        self.assertIn("report-path:", action)
        self.assertIn("summary-json:", action)
        self.assertIn("average-score:", action)
        self.assertIn("value: ${{ steps.build.outputs.report-path }}", action)
        self.assertIn("value: ${{ steps.build.outputs.average-score }}", action)

    def test_action_installs_local_package_and_uses_read_only_cli(self) -> None:
        action = (ROOT / "action.yml").read_text(encoding="utf-8")

        self.assertIn('python -m pip install "$GITHUB_ACTION_PATH"', action)
        self.assertIn('maintainer-radar repo "$repository"', action)
        self.assertIn('command+=(--config "$INPUT_CONFIG")', action)
        self.assertIn('summary_command+=(--config "$INPUT_CONFIG")', action)
        self.assertIn('command+=(--label "$INPUT_LABEL")', action)
        self.assertIn('command+=(--action "$INPUT_ACTION")', action)
        self.assertIn('command+=(--min-score "$INPUT_MIN_SCORE")', action)
        self.assertIn('command+=(--group-by "$INPUT_GROUP_BY")', action)
        self.assertIn('summary_command+=(--label "$INPUT_LABEL")', action)
        self.assertIn('summary_command+=(--action "$INPUT_ACTION")', action)
        self.assertIn('summary_command+=(--min-score "$INPUT_MIN_SCORE")', action)
        self.assertIn('summary_json="$("${summary_command[@]}" --format json)"', action)
        self.assertIn('summary-json<<MAINTAINER_RADAR_SUMMARY', action)
        self.assertIn('"average-score": "average_score"', action)
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

    def test_action_docs_cover_inputs_and_outputs(self) -> None:
        docs = (ROOT / "docs" / "github-action.md").read_text(encoding="utf-8")

        for name in [
            "repository",
            "format",
            "output",
            "limit",
            "label",
            "author",
            "stale-days",
            "updated-since",
            "action",
            "min-score",
            "max-risk",
            "sort",
            "top",
            "group-by",
            "config",
            "hydrate",
            "step-summary",
            "report-path",
            "summary-json",
            "average-score",
        ]:
            with self.subTest(name=name):
                self.assertIn(f"`{name}`", docs)


if __name__ == "__main__":
    unittest.main()
