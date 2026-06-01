from __future__ import annotations

import unittest

from maintainer_radar.workflow import render_github_action_workflow


class WorkflowTests(unittest.TestCase):
    def test_render_github_action_workflow_defaults_to_read_only_markdown_artifact(self) -> None:
        output = render_github_action_workflow()

        self.assertIn("name: Maintainer Radar Report", output)
        self.assertIn("workflow_dispatch:", output)
        self.assertIn('cron: "0 8 * * 1-5"', output)
        self.assertIn("contents: read", output)
        self.assertIn("pull-requests: read", output)
        self.assertIn('GH_TOKEN: ${{ github.token }}', output)
        self.assertIn("set -o pipefail", output)
        self.assertIn('--sort action', output)
        self.assertIn('--format markdown', output)
        self.assertIn('| tee maintainer-radar.md >> "$GITHUB_STEP_SUMMARY"', output)

    def test_render_github_action_workflow_supports_html_without_hydration(self) -> None:
        output = render_github_action_workflow(
            report_format="html",
            schedule="15 7 * * 1",
            limit=25,
            sort="risk",
            hydrate=False,
            top=10,
        )

        self.assertIn('cron: "15 7 * * 1"', output)
        self.assertIn("--limit 25", output)
        self.assertNotIn("--hydrate", output)
        self.assertIn("--sort risk", output)
        self.assertIn("--top 10", output)
        self.assertIn("--format html", output)
        self.assertIn("maintainer-radar.html", output)
        self.assertIn("Publish job summary", output)
        self.assertIn("continue-on-error: true", output)
        self.assertIn('--summary-only >> "$GITHUB_STEP_SUMMARY"', output)
        self.assertLess(output.index("actions/upload-artifact"), output.index("Publish job summary"))

    def test_render_github_action_workflow_can_skip_step_summary(self) -> None:
        output = render_github_action_workflow(step_summary=False)

        self.assertNotIn("GITHUB_STEP_SUMMARY", output)
        self.assertNotIn("set -o pipefail", output)
        self.assertIn("> maintainer-radar.md", output)

    def test_render_github_action_workflow_rejects_invalid_values(self) -> None:
        with self.assertRaises(ValueError):
            render_github_action_workflow(report_format="xml")
        with self.assertRaises(ValueError):
            render_github_action_workflow(limit=0)
        with self.assertRaises(ValueError):
            render_github_action_workflow(top=0)
        with self.assertRaises(ValueError):
            render_github_action_workflow(schedule="0 8 * * 1\nname: injected")


if __name__ == "__main__":
    unittest.main()
