from __future__ import annotations

import unittest

from maintainer_radar.render import (
    render_comment_template,
    render_detail,
    render_markdown,
    render_summary_markdown,
    summarize_report,
)


class RenderTests(unittest.TestCase):
    def test_markdown_table_contains_action_and_score(self) -> None:
        output = render_markdown(
            [
                {
                    "number": 1,
                    "title": "Fix bug",
                    "url": "https://example.test/pull/1",
                    "action": "review now",
                    "reviewability": 90,
                    "signals": ["CI passed"],
                    "flags": [],
                }
            ]
        )

        self.assertIn("Maintainer Radar Report", output)
        self.assertIn("PRs scanned: 1", output)
        self.assertIn("review now", output)
        self.assertIn("90", output)
        self.assertIn("Average reviewability: 90/100\n\n| PR |", output)

    def test_summary_counts_actions(self) -> None:
        summary = summarize_report(
            [
                {"action": "review now", "reviewability": 90, "stale_days": 0},
                {
                    "action": "ask for CI fix",
                    "reviewability": 30,
                    "stale_days": 8,
                    "flags": ["CI failing"],
                },
                {"action": "needs triage", "reviewability": 20, "stale_days": 1},
            ]
        )

        self.assertEqual(summary["total"], 3)
        self.assertEqual(summary["review_now"], 1)
        self.assertEqual(summary["ci_blocked"], 1)
        self.assertEqual(summary["large_or_triage"], 1)
        self.assertEqual(summary["stale"], 1)

    def test_summary_counts_ci_flags_even_when_action_differs(self) -> None:
        summary = summarize_report(
            [
                {
                    "action": "wait for author",
                    "reviewability": 0,
                    "stale_days": 0,
                    "flags": ["draft PR", "CI failing"],
                }
            ]
        )

        self.assertEqual(summary["ci_blocked"], 1)

    def test_summary_only_output_has_no_table(self) -> None:
        output = render_summary_markdown(
            [
                {"action": "review now", "reviewability": 90, "stale_days": 0},
            ]
        )

        self.assertIn("Maintainer Radar Summary", output)
        self.assertIn("Review now: 1", output)
        self.assertNotIn("| PR |", output)

    def test_detail_contains_sections(self) -> None:
        output = render_detail(
            {
                "number": 1,
                "title": "Fix bug",
                "action": "review now",
                "reviewability": 90,
                "risk": 10,
                "checks": {"passed": 1},
                "files": {"code_files": 1, "test_files": 1, "doc_files": 0},
                "signals": ["CI passed"],
                "flags": [],
            }
        )

        self.assertIn("Maintainer Brief", output)
        self.assertIn("### Checks", output)
        self.assertIn("### Flags", output)

    def test_comment_template_is_draft_and_uses_flags(self) -> None:
        output = render_comment_template(
            {
                "action": "needs author follow-up",
                "reviewability": 42,
                "flags": [
                    "CI failing",
                    "no test plan found",
                    "code changed without tests",
                    "maintainer blocker language",
                ],
            }
        )

        self.assertIn("Current triage suggests", output)
        self.assertIn("Get CI passing", output)
        self.assertIn("Add a short validation", output)
        self.assertIn("Generated as a draft", output)


if __name__ == "__main__":
    unittest.main()
