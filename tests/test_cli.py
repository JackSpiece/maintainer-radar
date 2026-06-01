from __future__ import annotations

import unittest

from maintainer_radar.cli import _as_pr_list, build_parser


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

    def test_as_pr_list_accepts_common_shapes(self) -> None:
        self.assertEqual(_as_pr_list({"number": 1}), [{"number": 1}])
        self.assertEqual(_as_pr_list([{"number": 1}]), [{"number": 1}])
        self.assertEqual(_as_pr_list({"items": [{"number": 1}]}), [{"number": 1}])


if __name__ == "__main__":
    unittest.main()

