from __future__ import annotations

import unittest

from maintainer_radar.render import render_detail, render_markdown


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
        self.assertIn("review now", output)
        self.assertIn("90", output)

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


if __name__ == "__main__":
    unittest.main()

