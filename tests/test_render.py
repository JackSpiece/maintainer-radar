from __future__ import annotations

import unittest

from maintainer_radar.render import (
    render_comment_csv,
    render_comment_html,
    render_csv,
    render_comment_template,
    render_detail,
    render_html,
    render_markdown,
    render_summary_csv,
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
                    "score_breakdown": [
                        {"label": "CI passed", "risk_delta": -8, "kind": "signal"},
                    ],
                }
            ]
        )

        self.assertIn("Maintainer Radar Report", output)
        self.assertIn("PRs scanned: 1", output)
        self.assertIn("review now", output)
        self.assertIn("90", output)
        self.assertIn("CI passed (-8 risk)", output)
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

    def test_csv_output_contains_stable_columns(self) -> None:
        output = render_csv(
            [
                {
                    "number": 42,
                    "title": "Fix parser cache race",
                    "author": "alice",
                    "action": "review now",
                    "reviewability": 90,
                    "risk": 10,
                    "stale_days": 0,
                    "changed_files": 2,
                    "additions": 12,
                    "deletions": 3,
                    "labels": ["bug", "backend"],
                    "signals": ["CI passed"],
                    "flags": ["no test plan found"],
                    "score_breakdown": [
                        {"label": "no test plan found", "risk_delta": 8, "kind": "flag"},
                    ],
                    "url": "https://example.test/pull/42",
                }
            ]
        )

        self.assertIn("number,title,author,action,reviewability,risk", output)
        self.assertIn("score_breakdown,url", output)
        self.assertIn("42,Fix parser cache race,alice,review now,90,10", output)
        self.assertIn("bug; backend", output)
        self.assertIn("no test plan found (+8 risk)", output)
        self.assertIn("no test plan found", output)

    def test_summary_csv_output_contains_one_summary_row(self) -> None:
        output = render_summary_csv(
            [
                {"action": "review now", "reviewability": 90, "stale_days": 0},
                {
                    "action": "ask for CI fix",
                    "reviewability": 30,
                    "stale_days": 8,
                    "flags": ["CI failing"],
                },
            ]
        )

        self.assertIn("total,review_now,author_follow_up", output)
        self.assertIn("2,1,0,1,0,0,1,60", output)

    def test_comment_csv_output_quotes_multiline_comment(self) -> None:
        output = render_comment_csv("Thanks.\nPlease add tests.")

        self.assertTrue(output.startswith("comment\n"))
        self.assertIn('"Thanks.\nPlease add tests."', output)

    def test_html_output_contains_summary_and_escapes_content(self) -> None:
        output = render_html(
            [
                {
                    "number": 42,
                    "title": "Fix <parser>",
                    "url": "javascript:alert(1)",
                    "action": "review now",
                    "reviewability": 90,
                    "signals": ["CI passed"],
                    "flags": ["needs <tests>"],
                    "score_breakdown": [
                        {"label": "needs <tests>", "risk_delta": 8, "kind": "flag"},
                    ],
                }
            ]
        )

        self.assertIn("<!doctype html>", output)
        self.assertIn("PRs scanned", output)
        self.assertIn("#42 Fix &lt;parser&gt;", output)
        self.assertIn("needs &lt;tests&gt;", output)
        self.assertIn("needs &lt;tests&gt; (+8 risk)", output)
        self.assertNotIn("javascript:alert", output)

    def test_summary_html_output_omits_table(self) -> None:
        output = render_html(
            [{"number": 1, "action": "review now", "reviewability": 90}],
            summary_only=True,
        )

        self.assertIn("Maintainer Radar Report", output)
        self.assertNotIn("<table>", output)

    def test_comment_html_output_escapes_comment(self) -> None:
        output = render_comment_html("Thanks.\n<script>alert(1)</script>")

        self.assertIn("<pre>", output)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", output)

    def test_detail_contains_sections(self) -> None:
        output = render_detail(
            {
                "number": 1,
                "title": "Fix bug",
                "action": "review now",
                "reviewability": 90,
                "risk": 10,
                "raw_risk": 10,
                "checks": {"passed": 1},
                "files": {"code_files": 1, "test_files": 1, "doc_files": 0},
                "signals": ["CI passed"],
                "flags": [],
                "score_breakdown": [
                    {"label": "CI passed", "risk_delta": -8, "kind": "signal"},
                ],
            }
        )

        self.assertIn("Maintainer Brief", output)
        self.assertIn("### Checks", output)
        self.assertIn("### Score Breakdown", output)
        self.assertIn("CI passed: -8 risk", output)
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
