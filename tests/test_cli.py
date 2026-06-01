from __future__ import annotations

import unittest

from maintainer_radar.cli import (
    _as_pr_list,
    build_parser,
    filter_analyses,
    filter_prs,
    hydrate_prs,
    sort_analyses,
)


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

    def test_csv_format_is_available(self) -> None:
        args = build_parser().parse_args(
            ["from-json", "examples/sample-prs.json", "--format", "csv"]
        )

        self.assertEqual(args.format, "csv")

    def test_html_format_is_available(self) -> None:
        args = build_parser().parse_args(
            ["from-json", "examples/sample-prs.json", "--format", "html"]
        )

        self.assertEqual(args.format, "html")

    def test_summary_only_flag_is_available_for_queue_commands(self) -> None:
        repo_args = build_parser().parse_args(["repo", "owner/repo", "--summary-only"])
        author_args = build_parser().parse_args(["author", "alice", "--summary-only"])
        json_args = build_parser().parse_args(
            ["from-json", "examples/sample-prs.json", "--summary-only"]
        )

        self.assertTrue(repo_args.summary_only)
        self.assertTrue(author_args.summary_only)
        self.assertTrue(json_args.summary_only)

    def test_action_score_and_risk_flags_parse(self) -> None:
        args = build_parser().parse_args(
            [
                "repo",
                "owner/repo",
                "--action",
                "review-now",
                "--min-score",
                "80",
                "--max-risk",
                "20",
            ]
        )

        self.assertEqual(args.action, "review-now")
        self.assertEqual(args.min_score, 80)
        self.assertEqual(args.max_risk, 20)

    def test_sort_flag_is_available_for_queue_commands(self) -> None:
        repo_args = build_parser().parse_args(["repo", "owner/repo", "--sort", "action"])
        author_args = build_parser().parse_args(["author", "alice", "--sort", "risk"])
        json_args = build_parser().parse_args(
            ["from-json", "examples/sample-prs.json", "--sort", "stale"]
        )

        self.assertEqual(repo_args.sort, "action")
        self.assertEqual(author_args.sort, "risk")
        self.assertEqual(json_args.sort, "stale")

    def test_hydrate_flag_is_available_for_live_queue_commands(self) -> None:
        repo_args = build_parser().parse_args(["repo", "owner/repo", "--hydrate"])
        author_args = build_parser().parse_args(["author", "alice", "--hydrate"])

        self.assertTrue(repo_args.hydrate)
        self.assertTrue(author_args.hydrate)

    def test_comment_template_flag_is_available_for_pr_command(self) -> None:
        args = build_parser().parse_args(["pr", "owner/repo", "123", "--comment-template"])

        self.assertTrue(args.comment_template)

    def test_as_pr_list_accepts_common_shapes(self) -> None:
        self.assertEqual(_as_pr_list({"number": 1}), [{"number": 1}])
        self.assertEqual(_as_pr_list([{"number": 1}]), [{"number": 1}])
        self.assertEqual(_as_pr_list({"items": [{"number": 1}]}), [{"number": 1}])

    def test_from_json_accepts_gitlab_source(self) -> None:
        args = build_parser().parse_args(
            ["from-json", "tests/fixtures/gitlab-merge-requests.json", "--source", "gitlab"]
        )

        self.assertEqual(args.source, "gitlab")

    def test_from_json_accepts_forgejo_and_gitea_sources(self) -> None:
        forgejo_args = build_parser().parse_args(
            ["from-json", "tests/fixtures/forgejo-pull-requests.json", "--source", "forgejo"]
        )
        gitea_args = build_parser().parse_args(
            ["from-json", "tests/fixtures/forgejo-pull-requests.json", "--source", "gitea"]
        )

        self.assertEqual(forgejo_args.source, "forgejo")
        self.assertEqual(gitea_args.source, "gitea")

    def test_config_flag_is_available_for_commands(self) -> None:
        args = build_parser().parse_args(
            ["from-json", "examples/sample-prs.json", "--config", "config.json"]
        )

        self.assertEqual(args.config, "config.json")

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

    def test_filter_analyses_supports_action_score_and_risk(self) -> None:
        analyses = [
            {"number": 1, "action": "review now", "reviewability": 90, "risk": 10},
            {"number": 2, "action": "ask for CI fix", "reviewability": 30, "risk": 70},
            {"number": 3, "action": "review now", "reviewability": 65, "risk": 35},
        ]

        self.assertEqual(
            [item["number"] for item in filter_analyses(analyses, action="review-now")],
            [1, 3],
        )
        self.assertEqual(
            [item["number"] for item in filter_analyses(analyses, min_score=80)],
            [1],
        )
        self.assertEqual(
            [item["number"] for item in filter_analyses(analyses, max_risk=20)],
            [1],
        )

    def test_hydrate_prs_fetches_detail_and_merges_existing_context(self) -> None:
        calls: list[tuple[str, int | str]] = []

        def viewer(repo: str, number: int | str) -> dict[str, object]:
            calls.append((repo, number))
            return {
                "number": number,
                "body": "Test plan: unit tests.",
                "files": [{"path": "tests/test_parser.py"}],
            }

        hydrated = hydrate_prs(
            [
                {
                    "number": 42,
                    "title": "Fix parser",
                    "labels": [{"name": "bug"}],
                }
            ],
            repository="owner/repo",
            viewer=viewer,
        )

        self.assertEqual(calls, [("owner/repo", 42)])
        self.assertEqual(hydrated[0]["title"], "Fix parser")
        self.assertEqual(hydrated[0]["body"], "Test plan: unit tests.")
        self.assertEqual(hydrated[0]["files"][0]["path"], "tests/test_parser.py")

    def test_hydrate_prs_uses_repository_from_author_search_items(self) -> None:
        calls: list[tuple[str, int | str]] = []

        def viewer(repo: str, number: int | str) -> dict[str, object]:
            calls.append((repo, number))
            return {"number": number, "body": "Validation: local run."}

        hydrated = hydrate_prs(
            [
                {
                    "number": 7,
                    "repository": {"nameWithOwner": "org/project"},
                    "title": "Fix race",
                }
            ],
            viewer=viewer,
        )

        self.assertEqual(calls, [("org/project", 7)])
        self.assertEqual(hydrated[0]["body"], "Validation: local run.")

    def test_hydrate_prs_keeps_items_without_repository_context(self) -> None:
        hydrated = hydrate_prs([{"number": 1, "title": "Unknown repo"}])

        self.assertEqual(hydrated, [{"number": 1, "title": "Unknown repo"}])

    def test_sort_analyses_supports_priority_score_risk_stale_and_number(self) -> None:
        analyses = [
            {
                "number": 3,
                "action": "ask for CI fix",
                "reviewability": 20,
                "risk": 80,
                "stale_days": 3,
            },
            {
                "number": 1,
                "action": "review now",
                "reviewability": 90,
                "risk": 10,
                "stale_days": 1,
            },
            {
                "number": 2,
                "action": "needs triage",
                "reviewability": 30,
                "risk": 70,
                "stale_days": 12,
            },
        ]

        self.assertEqual([item["number"] for item in sort_analyses(analyses)], [3, 1, 2])
        self.assertEqual(
            [item["number"] for item in sort_analyses(analyses, "action")],
            [1, 3, 2],
        )
        self.assertEqual(
            [item["number"] for item in sort_analyses(analyses, "score")],
            [1, 2, 3],
        )
        self.assertEqual(
            [item["number"] for item in sort_analyses(analyses, "risk")],
            [3, 2, 1],
        )
        self.assertEqual(
            [item["number"] for item in sort_analyses(analyses, "stale")],
            [2, 3, 1],
        )
        self.assertEqual(
            [item["number"] for item in sort_analyses(analyses, "number")],
            [1, 2, 3],
        )


if __name__ == "__main__":
    unittest.main()
