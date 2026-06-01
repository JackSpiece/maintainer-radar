from __future__ import annotations

import unittest

from maintainer_radar import __version__
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
        self.assertIn(f"uses: JackSpiece/maintainer-radar@v{__version__}", output)
        self.assertIn("id: radar", output)
        self.assertIn("format: markdown", output)
        self.assertIn('sort: action', output)
        self.assertIn('step-summary: "true"', output)
        self.assertIn("path: ${{ steps.radar.outputs.report-path }}", output)

    def test_render_github_action_workflow_supports_html_without_hydration(self) -> None:
        output = render_github_action_workflow(
            report_format="html",
            schedule="15 7 * * 1",
            limit=25,
            sort="risk",
            hydrate=False,
            top=10,
            config=".maintainer-radar.json",
        )

        self.assertIn('cron: "15 7 * * 1"', output)
        self.assertIn('limit: "25"', output)
        self.assertIn('hydrate: "false"', output)
        self.assertIn("sort: risk", output)
        self.assertIn('top: "10"', output)
        self.assertIn('config: ".maintainer-radar.json"', output)
        self.assertIn("format: html", output)
        self.assertIn("maintainer-radar.html", output)
        self.assertIn('step-summary: "true"', output)

    def test_render_github_action_workflow_can_skip_step_summary(self) -> None:
        output = render_github_action_workflow(step_summary=False)

        self.assertIn('step-summary: "false"', output)

    def test_render_github_action_workflow_rejects_invalid_values(self) -> None:
        with self.assertRaises(ValueError):
            render_github_action_workflow(report_format="xml")
        with self.assertRaises(ValueError):
            render_github_action_workflow(limit=0)
        with self.assertRaises(ValueError):
            render_github_action_workflow(top=0)
        with self.assertRaises(ValueError):
            render_github_action_workflow(config="config.json\nname: injected")
        with self.assertRaises(ValueError):
            render_github_action_workflow(schedule="0 8 * * 1\nname: injected")


if __name__ == "__main__":
    unittest.main()
