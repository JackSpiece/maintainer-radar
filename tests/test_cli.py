from __future__ import annotations

import unittest

from maintainer_radar.cli import _as_pr_list, build_parser, filter_prs


class CliTests(unittest.TestCase):
    def test_format_works_before_subcommand(self) -> None:
        args = build_parser().parse_args(
            ["--format", "json", "from-json", "examples/sample-prs.json"]
        )

        self.assertEqual(args.format, "json")
        self.assertEqual(args.command, "from-json")

    def test_format_works_after_subcommand(self) -> None:
        args = build_parser().parse_args(
            ["from-json", "examples/sample-prs.json", "--format", "json"]
        )

        self.assertEqual(args.format, "json")
        self.assertEqual(args.command, "from-json")

    def test_summary_only_flag_is_available_for_queue_commands(self) -> None:
        repo_args = build_parser().parse_args(["repo", "owner/repo", "--summary-only"])
        author_args = build_parser().parse_args(["author", "alice", "--summary-only"])
        json_args = build_parser().parse_args(
            ["from-json", "examples/sample-prs.json", "--summary-only"]
        )

        self.assertTrue(repo_args.summary_only)
        self.assertTrue(author_args.summary_only)
        self.assertTrue(json_args.summary_only)

    def test_as_pr_list_accepts_common_shapes(self) -> None:
        self.assertEqual(_as_pr_list({"number": 1}), [{"number": 1}])
        self.assertEqual(_as_pr_list([{"number": 1}]), [{"number": 1}])
        self.assertEqual(_as_pr_list({"items": [{"number": 1}]}), [{"number": 1}])

    def test_filter_prs_supports_label_author_and_dates(self) -> None:
        prs = [
            {
                "number": 1,
                "author": {"login": "alice"},
                "labels": [{"name": "bug"}],
                "updatedAt": "2026-06-01T00:00:00Z",
            },
            {
                "number": 2,
                "author": {"login": "bob"},
                "labels": [{"name": "docs"}],
                "updatedAt": "2026-05-01T00:00:00Z",
            },
        ]

        self.assertEqual([pr["number"] for pr in filter_prs(prs, label="bug")], [1])
        self.assertEqual([pr["number"] for pr in filter_prs(prs, author="bob")], [2])
        self.assertEqual(
            [pr["number"] for pr in filter_prs(prs, updated_since="2026-05-15")],
            [1],
        )


if __name__ == "__main__":
    unittest.main()
