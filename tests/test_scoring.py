from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import unittest

from maintainer_radar.scoring import analyze_pr


NOW = datetime(2026, 6, 1, tzinfo=timezone.utc)


class AnalyzePrTests(unittest.TestCase):
    def test_review_now_for_small_green_pr_with_tests(self) -> None:
        result = analyze_pr(
            {
                "number": 42,
                "title": "Fix parser cache race",
                "body": "Test plan: unit tests and local repro.",
                "updatedAt": "2026-06-01T00:00:00Z",
                "additions": 42,
                "deletions": 18,
                "changedFiles": 3,
                "reviewDecision": "REVIEW_REQUIRED",
                "statusCheckRollup": [
                    {"status": "COMPLETED", "conclusion": "SUCCESS"},
                    {"status": "COMPLETED", "conclusion": "SUCCESS"},
                ],
                "files": [
                    {"path": "src/parser/cache.py"},
                    {"path": "tests/test_parser_cache.py"},
                ],
            },
            now=NOW,
        )

        self.assertEqual(result["action"], "review now")
        self.assertGreaterEqual(result["reviewability"], 75)
        self.assertIn("CI passed", result["signals"])
        self.assertIn("tests changed", result["signals"])
        self.assertEqual(
            result["next_step"],
            "Review now while the PR appears small, active, and low risk.",
        )
        self.assertIn(
            {"label": "CI passed", "risk_delta": -8, "kind": "signal"},
            result["score_breakdown"],
        )
        self.assertLessEqual(result["raw_risk"], result["risk"])

    def test_blocked_large_pr_needs_author_follow_up(self) -> None:
        result = analyze_pr(
            {
                "number": 43,
                "title": "Add universal plugin system",
                "body": "Implementation update.",
                "updatedAt": "2026-05-10T00:00:00Z",
                "additions": 2200,
                "deletions": 120,
                "changedFiles": 40,
                "reviewDecision": "CHANGES_REQUESTED",
                "statusCheckRollup": [
                    {"status": "COMPLETED", "conclusion": "FAILURE"},
                ],
                "comments": [{"body": "This is not working in the preview."}],
                "files": [{"path": "src/plugin/runtime.ts"}],
            },
            now=NOW,
        )

        self.assertIn(result["action"], {"ask for CI fix", "needs author follow-up"})
        self.assertLess(result["reviewability"], 50)
        self.assertIn("very large diff", result["flags"])
        self.assertIn("maintainer blocker language", result["flags"])
        self.assertEqual(
            result["next_step"],
            "Ask the author to get failing checks green before deeper review.",
        )
        self.assertIn(
            {"label": "very large diff", "risk_delta": 30, "kind": "flag"},
            result["score_breakdown"],
        )
        self.assertIn(
            {"label": "maintainer blocker language", "risk_delta": 25, "kind": "flag"},
            result["score_breakdown"],
        )

    def test_docs_only_shape_lowers_risk(self) -> None:
        result = analyze_pr(
            {
                "number": 44,
                "title": "Document release checklist",
                "body": "Validation: docs only.",
                "updatedAt": "2026-06-01T00:00:00Z",
                "additions": 25,
                "deletions": 2,
                "changedFiles": 1,
                "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "SUCCESS"}],
                "files": [{"path": "docs/release-checklist.md"}],
            },
            now=NOW,
        )

        self.assertIn("docs-only shape", result["signals"])
        self.assertNotIn("code changed without tests", result["flags"])
        self.assertEqual(
            result["next_step"],
            "Review now as a likely low-risk docs-only change.",
        )

    def test_blocker_fixture_corpus_detects_maintainer_blockers(self) -> None:
        fixture_path = Path(__file__).parent / "fixtures" / "blocker-prs.json"
        prs = json.loads(fixture_path.read_text(encoding="utf-8"))

        for pr in prs:
            with self.subTest(pr=pr["number"]):
                result = analyze_pr(pr, now=NOW)
                self.assertIn("maintainer blocker language", result["flags"])

    def test_blocking_label_needs_author_follow_up(self) -> None:
        result = analyze_pr(
            {
                "number": 46,
                "title": "Add parser fast path",
                "body": "Test plan: unit tests.",
                "updatedAt": "2026-06-01T00:00:00Z",
                "additions": 60,
                "deletions": 12,
                "changedFiles": 2,
                "labels": [{"name": "waiting-on-author"}],
                "reviewDecision": "REVIEW_REQUIRED",
                "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "SUCCESS"}],
                "files": [
                    {"path": "src/parser/fast_path.py"},
                    {"path": "tests/test_fast_path.py"},
                ],
            },
            now=NOW,
        )

        self.assertEqual(result["action"], "needs author follow-up")
        self.assertIn("maintainer blocking label", result["flags"])
        self.assertEqual(
            result["next_step"],
            "Ask the author to respond to unresolved maintainer feedback.",
        )
        self.assertIn(
            {"label": "maintainer blocking label", "risk_delta": 18, "kind": "flag"},
            result["score_breakdown"],
        )

    def test_ordinary_label_does_not_trigger_blocking_label(self) -> None:
        result = analyze_pr(
            {
                "number": 47,
                "title": "Fix docs typo",
                "body": "Validation: docs only.",
                "updatedAt": "2026-06-01T00:00:00Z",
                "additions": 4,
                "deletions": 1,
                "changedFiles": 1,
                "labels": ["documentation"],
                "reviewDecision": "REVIEW_REQUIRED",
                "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "SUCCESS"}],
                "files": [{"path": "docs/usage.md"}],
            },
            now=NOW,
        )

        self.assertEqual(result["action"], "review now")
        self.assertNotIn("maintainer blocking label", result["flags"])

    def test_dependency_blocking_label_needs_author_follow_up(self) -> None:
        result = analyze_pr(
            {
                "number": 48,
                "title": "Update generated client",
                "body": "Test plan: local client fixture.",
                "updatedAt": "2026-06-01T00:00:00Z",
                "additions": 80,
                "deletions": 12,
                "changedFiles": 3,
                "labels": [{"name": "blocked-upstream"}],
                "reviewDecision": "REVIEW_REQUIRED",
                "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "SUCCESS"}],
                "files": [
                    {"path": "src/client/generated.py"},
                    {"path": "tests/test_client.py"},
                ],
            },
            now=NOW,
        )

        self.assertEqual(result["action"], "needs author follow-up")
        self.assertIn("maintainer blocking label", result["flags"])

    def test_merge_conflict_needs_author_follow_up(self) -> None:
        result = analyze_pr(
            {
                "number": 49,
                "title": "Refresh parser branch",
                "body": "Test plan: unit tests.",
                "updatedAt": "2026-06-01T00:00:00Z",
                "additions": 60,
                "deletions": 12,
                "changedFiles": 2,
                "mergeStateStatus": "DIRTY",
                "mergeable": "CONFLICTING",
                "reviewRequests": [{"login": "maintainer-a"}],
                "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "SUCCESS"}],
                "files": [
                    {"path": "src/parser/branch.py"},
                    {"path": "tests/test_branch.py"},
                ],
            },
            now=NOW,
        )

        self.assertEqual(result["action"], "needs author follow-up")
        self.assertIn("merge conflicts", result["flags"])
        self.assertIn("review requested", result["signals"])
        self.assertEqual(result["merge_state_status"], "DIRTY")
        self.assertEqual(result["mergeable"], "CONFLICTING")
        self.assertEqual(result["review_requests"], 1)
        self.assertEqual(
            result["next_step"],
            "Ask the author to resolve merge conflicts before another review pass.",
        )
        self.assertIn(
            {"label": "merge conflicts", "risk_delta": 20, "kind": "flag"},
            result["score_breakdown"],
        )

    def test_branch_behind_needs_author_follow_up(self) -> None:
        result = analyze_pr(
            {
                "number": 50,
                "title": "Update API client",
                "body": "Test plan: unit tests.",
                "updatedAt": "2026-06-01T00:00:00Z",
                "additions": 60,
                "deletions": 12,
                "changedFiles": 2,
                "mergeStateStatus": "BEHIND",
                "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "SUCCESS"}],
                "files": [
                    {"path": "src/client.py"},
                    {"path": "tests/test_client.py"},
                ],
            },
            now=NOW,
        )

        self.assertEqual(result["action"], "needs author follow-up")
        self.assertIn("branch behind base", result["flags"])
        self.assertEqual(
            result["next_step"],
            "Ask the author to update the branch with the base branch before review.",
        )

    def test_merge_blocked_by_repo_rules_stays_reviewable(self) -> None:
        result = analyze_pr(
            {
                "number": 51,
                "title": "Small clean change",
                "body": "Test plan: unit tests.",
                "updatedAt": "2026-06-01T00:00:00Z",
                "additions": 20,
                "deletions": 4,
                "changedFiles": 2,
                "mergeStateStatus": "BLOCKED",
                "reviewRequests": [{"login": "maintainer-a"}, {"login": "maintainer-b"}],
                "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "SUCCESS"}],
                "files": [
                    {"path": "src/small.py"},
                    {"path": "tests/test_small.py"},
                ],
            },
            now=NOW,
        )

        self.assertEqual(result["action"], "review now")
        self.assertIn("merge blocked by repo rules", result["flags"])
        self.assertIn("2 reviews requested", result["signals"])

    def test_configurable_thresholds_and_hints(self) -> None:
        result = analyze_pr(
            {
                "number": 45,
                "title": "Custom repo shape",
                "body": "Validation: fixture run.",
                "updatedAt": "2026-05-20T00:00:00Z",
                "additions": 30,
                "deletions": 0,
                "changedFiles": 2,
                "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "SUCCESS"}],
                "files": [
                    {"path": "src/app.py"},
                    {"path": "specs/app_spec.py"},
                    {"path": "snapshots/app.snap"},
                ],
            },
            now=NOW,
            config={
                "large_diff_lines": 20,
                "very_large_diff_lines": 80,
                "large_file_count": 3,
                "very_large_file_count": 8,
                "quiet_days": 3,
                "stale_days": 10,
                "test_hints": ["specs/"],
                "doc_hints": [],
                "generated_hints": ["snapshots/"],
            },
        )

        self.assertIn("large diff", result["flags"])
        self.assertIn("stale 12 days", result["flags"])
        self.assertIn("tests changed", result["signals"])
        self.assertIn("generated or lockfile changes", result["flags"])

    def test_author_own_comment_does_not_trigger_blocker(self) -> None:
        result = analyze_pr(
            {
                "number": 52,
                "title": "Fix retry logic",
                "body": "Test plan: unit tests.",
                "updatedAt": "2026-06-01T00:00:00Z",
                "additions": 40,
                "deletions": 10,
                "changedFiles": 2,
                "author": {"login": "contributor-a"},
                "reviewDecision": "REVIEW_REQUIRED",
                "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "SUCCESS"}],
                "comments": [
                    {
                        "author": {"login": "contributor-a"},
                        "body": "This is not working yet on my machine, still debugging.",
                    }
                ],
                "files": [
                    {"path": "src/retry.py"},
                    {"path": "tests/test_retry.py"},
                ],
            },
            now=NOW,
        )

        self.assertNotIn("maintainer blocker language", result["flags"])

    def test_review_state_alone_is_not_blocker_language(self) -> None:
        result = analyze_pr(
            {
                "number": 53,
                "title": "Refactor scheduler",
                "body": "Test plan: unit tests.",
                "updatedAt": "2026-06-01T00:00:00Z",
                "additions": 40,
                "deletions": 10,
                "changedFiles": 2,
                "reviewDecision": "CHANGES_REQUESTED",
                "latestReviews": [{"state": "CHANGES_REQUESTED", "body": ""}],
                "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "SUCCESS"}],
                "files": [
                    {"path": "src/scheduler.py"},
                    {"path": "tests/test_scheduler.py"},
                ],
            },
            now=NOW,
        )

        self.assertIn("changes requested", result["flags"])
        self.assertNotIn("maintainer blocker language", result["flags"])

    def test_casual_test_mention_is_not_a_test_plan(self) -> None:
        result = analyze_pr(
            {
                "number": 54,
                "title": "Speed up pipeline",
                "body": "This should make the ci faster and the tests happier.",
                "updatedAt": "2026-06-01T00:00:00Z",
                "additions": 30,
                "deletions": 5,
                "changedFiles": 2,
                "reviewDecision": "REVIEW_REQUIRED",
                "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "SUCCESS"}],
                "files": [
                    {"path": "src/pipeline.py"},
                    {"path": "tests/test_pipeline.py"},
                ],
            },
            now=NOW,
        )

        self.assertIn("no test plan found", result["flags"])
        self.assertNotIn("test plan present", result["signals"])

    def test_test_only_pr_is_not_penalized_for_missing_tests(self) -> None:
        result = analyze_pr(
            {
                "number": 55,
                "title": "Add regression tests",
                "body": "Test plan: new regression tests.",
                "updatedAt": "2026-06-01T00:00:00Z",
                "additions": 50,
                "deletions": 0,
                "changedFiles": 1,
                "reviewDecision": "REVIEW_REQUIRED",
                "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "SUCCESS"}],
                "files": [{"path": "tests/test_regression.py"}],
            },
            now=NOW,
        )

        self.assertNotIn("code changed without tests", result["flags"])
        self.assertIn("tests changed", result["signals"])


class CheckRollupTests(unittest.TestCase):
    """Regression cover for how check results are bucketed."""

    def _pr(self, rollup: list[dict[str, object]]) -> dict[str, object]:
        return {
            "number": 200,
            "title": "Fix worker retries",
            "body": "Test plan: unit tests.",
            "updatedAt": "2026-06-01T00:00:00Z",
            "additions": 20,
            "deletions": 4,
            "changedFiles": 2,
            "statusCheckRollup": rollup,
            "files": [
                {"path": "src/worker.py"},
                {"path": "tests/test_worker.py"},
            ],
        }

    def test_legacy_commit_status_failure_is_detected(self) -> None:
        result = analyze_pr(
            self._pr(
                [
                    {"__typename": "StatusContext", "context": "ci/circleci", "state": "FAILURE"},
                    {"__typename": "StatusContext", "context": "ci/lint", "state": "SUCCESS"},
                ]
            ),
            now=NOW,
        )

        self.assertEqual(result["checks"]["failed"], 1)
        self.assertEqual(result["checks"]["passed"], 1)
        self.assertIn("CI failing", result["flags"])
        self.assertNotIn("no visible checks", result["flags"])
        self.assertEqual(result["action"], "ask for CI fix")

    def test_legacy_commit_status_error_is_a_failure(self) -> None:
        result = analyze_pr(
            self._pr([{"context": "ci/deploy", "state": "ERROR"}]),
            now=NOW,
        )

        self.assertEqual(result["checks"]["failed"], 1)
        self.assertIn("CI failing", result["flags"])

    def test_cancelled_checks_are_not_reported_as_failures(self) -> None:
        result = analyze_pr(
            self._pr(
                [
                    {"status": "COMPLETED", "conclusion": "CANCELLED"},
                    {"status": "COMPLETED", "conclusion": "CANCELLED"},
                ]
            ),
            now=NOW,
        )

        self.assertEqual(result["checks"]["failed"], 0)
        self.assertEqual(result["checks"]["skipped"], 2)
        self.assertNotIn("CI failing", result["flags"])
        self.assertNotIn("CI passed", result["signals"])
        self.assertIn("no visible checks", result["flags"])

    def test_skipped_only_checks_do_not_read_as_passing(self) -> None:
        result = analyze_pr(
            self._pr([{"status": "COMPLETED", "conclusion": "SKIPPED"}]),
            now=NOW,
        )

        self.assertNotIn("CI passed", result["signals"])
        self.assertIn("no visible checks", result["flags"])

    def test_action_required_check_is_pending_not_failed(self) -> None:
        result = analyze_pr(
            self._pr([{"status": "COMPLETED", "conclusion": "ACTION_REQUIRED"}]),
            now=NOW,
        )

        self.assertEqual(result["checks"]["failed"], 0)
        self.assertEqual(result["checks"]["pending"], 1)
        self.assertIn("CI pending", result["flags"])
        self.assertEqual(result["action"], "wait for CI")

    def test_startup_failure_conclusion_is_a_failure(self) -> None:
        result = analyze_pr(
            self._pr([{"status": "COMPLETED", "conclusion": "STARTUP_FAILURE"}]),
            now=NOW,
        )

        self.assertEqual(result["checks"]["failed"], 1)
        self.assertIn("CI failing", result["flags"])
        self.assertEqual(result["action"], "ask for CI fix")

    def test_unknown_conclusion_does_not_stall_on_wait_for_ci(self) -> None:
        result = analyze_pr(
            self._pr([{"status": "COMPLETED", "conclusion": "STALE"}]),
            now=NOW,
        )

        self.assertEqual(result["checks"]["pending"], 0)
        self.assertNotEqual(result["action"], "wait for CI")


class FileClassificationTests(unittest.TestCase):
    """Regression cover for path bucketing false positives."""

    def _pr(self, paths: list[str]) -> dict[str, object]:
        return {
            "number": 300,
            "title": "Change some files",
            "body": "Test plan: unit tests.",
            "updatedAt": "2026-06-01T00:00:00Z",
            "additions": 30,
            "deletions": 6,
            "changedFiles": len(paths),
            "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "SUCCESS"}],
            "files": [{"path": path} for path in paths],
        }

    def test_source_file_named_like_a_test_is_not_a_test_file(self) -> None:
        result = analyze_pr(
            self._pr(["src/latest_release.py", "src/contest_manager.py"]),
            now=NOW,
        )

        self.assertEqual(result["files"]["code_files"], 2)
        self.assertEqual(result["files"]["test_files"], 0)
        self.assertIn("code changed without tests", result["flags"])
        self.assertNotIn("tests changed", result["signals"])

    def test_real_test_paths_are_still_detected(self) -> None:
        result = analyze_pr(
            self._pr(
                [
                    "src/queue.py",
                    "tests/test_queue.py",
                    "src/ui/widget.test.tsx",
                    "packages/core/__tests__/parser.js",
                    "api/spec/router_spec.rb",
                ]
            ),
            now=NOW,
        )

        self.assertEqual(result["files"]["test_files"], 4)
        self.assertEqual(result["files"]["code_files"], 1)
        self.assertNotIn("code changed without tests", result["flags"])

    def test_license_and_readme_source_files_are_not_documentation(self) -> None:
        result = analyze_pr(
            self._pr(["src/license_checker.py", "src/readme_generator.py"]),
            now=NOW,
        )

        self.assertEqual(result["files"]["doc_files"], 0)
        self.assertEqual(result["files"]["code_files"], 2)
        self.assertNotIn("docs-only shape", result["signals"])

    def test_real_project_documents_are_still_documentation(self) -> None:
        result = analyze_pr(self._pr(["LICENSE", "README.md", "docs/guide.rst"]), now=NOW)

        self.assertEqual(result["files"]["doc_files"], 3)
        self.assertEqual(result["files"]["code_files"], 0)
        self.assertIn("docs-only shape", result["signals"])

    def test_infrastructure_and_config_files_count_as_code(self) -> None:
        result = analyze_pr(
            self._pr(["deploy/main.tf", "Dockerfile", ".github/workflows/release.yml"]),
            now=NOW,
        )

        self.assertEqual(result["files"]["code_files"], 3)
        self.assertIn("code changed without tests", result["flags"])

    def test_root_build_output_is_generated_but_nested_build_source_is_code(self) -> None:
        result = analyze_pr(
            self._pr(["build/bundle.js", "src/build/compiler.py"]),
            now=NOW,
        )

        self.assertEqual(result["files"]["generated_files"], 1)
        self.assertEqual(result["files"]["code_files"], 1)
        self.assertIn("generated or lockfile changes", result["flags"])

    def test_generated_substring_does_not_capture_ordinary_source(self) -> None:
        result = analyze_pr(self._pr(["src/generated_ids.py"]), now=NOW)

        self.assertEqual(result["files"]["generated_files"], 0)
        self.assertEqual(result["files"]["code_files"], 1)


class BlockerLanguageTests(unittest.TestCase):
    """Regression cover for what counts as maintainer blocker language."""

    def _pr(self, comments: list[dict[str, object]]) -> dict[str, object]:
        return {
            "number": 400,
            "title": "Fix retry logic",
            "body": "Test plan: unit tests.",
            "updatedAt": "2026-06-01T00:00:00Z",
            "additions": 40,
            "deletions": 10,
            "changedFiles": 2,
            "author": {"login": "contributor-b"},
            "reviewDecision": "REVIEW_REQUIRED",
            "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "SUCCESS"}],
            "comments": comments,
            "files": [
                {"path": "src/retry.py"},
                {"path": "tests/test_retry.py"},
            ],
        }

    def test_bot_comments_do_not_trigger_blocker_language(self) -> None:
        result = analyze_pr(
            self._pr(
                [
                    {
                        "author": {"login": "codecov[bot]"},
                        "body": "Coverage decreased. 3 checks failed.",
                    },
                    {
                        "author": {"login": "github-actions[bot]"},
                        "body": "This PR is blocked until the regression is fixed.",
                    },
                ]
            ),
            now=NOW,
        )

        self.assertNotIn("maintainer blocker language", result["flags"])
        self.assertEqual(result["action"], "review now")

    def test_bot_flagged_by_type_is_ignored(self) -> None:
        result = analyze_pr(
            self._pr([{"author": {"login": "ci-reporter", "type": "Bot"}, "body": "Build broken."}]),
            now=NOW,
        )

        self.assertNotIn("maintainer blocker language", result["flags"])

    def test_quoted_ci_log_does_not_trigger_blocker_language(self) -> None:
        result = analyze_pr(
            self._pr(
                [
                    {
                        "author": {"login": "maintainer-a"},
                        "body": (
                            "> FAILED tests/test_queue.py::test_drain\n"
                            "> AssertionError: queue is broken\n"
                            "\n"
                            "Looks unrelated to this change."
                        ),
                    }
                ]
            ),
            now=NOW,
        )

        self.assertNotIn("maintainer blocker language", result["flags"])

    def test_fenced_ci_log_does_not_trigger_blocker_language(self) -> None:
        result = analyze_pr(
            self._pr(
                [
                    {
                        "author": {"login": "maintainer-a"},
                        "body": (
                            "Full log:\n\n```\n"
                            "FAILED tests/test_queue.py\n"
                            "build broken\n"
                            "```\n\nRerunning."
                        ),
                    }
                ]
            ),
            now=NOW,
        )

        self.assertNotIn("maintainer blocker language", result["flags"])

    def test_genuine_maintainer_comment_still_triggers_blocker_language(self) -> None:
        result = analyze_pr(
            self._pr(
                [
                    {
                        "author": {"login": "maintainer-a"},
                        "body": "Please fix the regression before another review.",
                    }
                ]
            ),
            now=NOW,
        )

        self.assertIn("maintainer blocker language", result["flags"])
        self.assertEqual(result["action"], "needs author follow-up")


if __name__ == "__main__":
    unittest.main()
