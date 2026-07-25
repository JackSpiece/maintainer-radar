from __future__ import annotations

import json
from pathlib import Path
import unittest

from maintainer_radar.normalize import normalize_forgejo_pr, normalize_gitlab_mr, normalize_items
from maintainer_radar.scoring import analyze_pr


class NormalizeTests(unittest.TestCase):
    def test_normalize_gitlab_merge_request(self) -> None:
        fixture = json.loads(
            (Path(__file__).parent / "fixtures" / "gitlab-merge-requests.json").read_text(
                encoding="utf-8"
            )
        )
        normalized = normalize_items(fixture, source="gitlab")

        self.assertEqual(len(normalized), 2)
        self.assertEqual(normalized[0]["number"], 12)
        self.assertEqual(normalized[0]["author"]["login"], "alice")
        self.assertEqual(normalized[0]["reviewDecision"], "APPROVED")
        self.assertEqual(normalized[0]["mergeStateStatus"], "CLEAN")
        self.assertEqual(normalized[0]["mergeable"], "MERGEABLE")
        self.assertEqual(normalized[0]["statusCheckRollup"][0]["conclusion"], "SUCCESS")
        self.assertEqual(normalized[0]["changedFiles"], 2)
        self.assertEqual(normalized[0]["files"][1]["path"], "tests/test_api_cache.py")

    def test_gitlab_merge_request_scores_with_existing_engine(self) -> None:
        fixture = json.loads(
            (Path(__file__).parent / "fixtures" / "gitlab-merge-requests.json").read_text(
                encoding="utf-8"
            )
        )
        analyses = [analyze_pr(item) for item in normalize_items(fixture, source="gitlab")]

        self.assertEqual(analyses[0]["action"], "review now")
        self.assertIn("approved", analyses[0]["signals"])
        self.assertEqual(analyses[1]["action"], "wait for author")
        self.assertIn("CI failing", analyses[1]["flags"])
        self.assertIn("maintainer blocker language", analyses[1]["flags"])

    def test_gitlab_diff_line_counts_are_used_without_stats(self) -> None:
        normalized = normalize_gitlab_mr(
            {
                "iid": 1,
                "title": "Small diff",
                "changes": [
                    {
                        "new_path": "src/main.py",
                        "diff": "--- a/src/main.py\n+++ b/src/main.py\n-old\n+new\n+extra\n",
                    }
                ],
            }
        )

        self.assertEqual(normalized["additions"], 2)
        self.assertEqual(normalized["deletions"], 1)

    def test_gitlab_conflict_merge_state_is_normalized(self) -> None:
        normalized = normalize_gitlab_mr(
            {
                "iid": 2,
                "title": "Conflict",
                "has_conflicts": True,
                "reviewers": [{"username": "maintainer"}],
            }
        )

        self.assertEqual(normalized["mergeStateStatus"], "DIRTY")
        self.assertEqual(normalized["mergeable"], "CONFLICTING")
        self.assertEqual(len(normalized["reviewRequests"]), 1)

    def test_normalize_forgejo_pull_request(self) -> None:
        fixture = json.loads(
            (Path(__file__).parent / "fixtures" / "forgejo-pull-requests.json").read_text(
                encoding="utf-8"
            )
        )
        normalized = normalize_items(fixture, source="forgejo")

        self.assertEqual(len(normalized), 2)
        self.assertEqual(normalized[0]["number"], 7)
        self.assertEqual(normalized[0]["author"]["login"], "maya")
        self.assertEqual(normalized[0]["reviewDecision"], "APPROVED")
        self.assertEqual(normalized[0]["mergeStateStatus"], "CLEAN")
        self.assertEqual(normalized[0]["mergeable"], "MERGEABLE")
        self.assertEqual(normalized[0]["statusCheckRollup"][0]["conclusion"], "SUCCESS")
        self.assertEqual(normalized[0]["changedFiles"], 2)
        self.assertEqual(normalized[0]["files"][1]["path"], "tests/test_webhook_retry.py")

    def test_gitea_source_alias_uses_forgejo_normalizer(self) -> None:
        fixture = json.loads(
            (Path(__file__).parent / "fixtures" / "forgejo-pull-requests.json").read_text(
                encoding="utf-8"
            )
        )
        normalized = normalize_items(fixture, source="gitea")

        self.assertEqual(normalized[1]["number"], 8)
        self.assertEqual(normalized[1]["author"]["login"], "kai")
        self.assertEqual(normalized[1]["reviewDecision"], "CHANGES_REQUESTED")
        self.assertEqual(normalized[1]["statusCheckRollup"][0]["conclusion"], "FAILURE")

    def test_forgejo_pull_request_scores_with_existing_engine(self) -> None:
        fixture = json.loads(
            (Path(__file__).parent / "fixtures" / "forgejo-pull-requests.json").read_text(
                encoding="utf-8"
            )
        )
        analyses = [analyze_pr(item) for item in normalize_items(fixture, source="forgejo")]

        self.assertEqual(analyses[0]["action"], "review now")
        self.assertIn("approved", analyses[0]["signals"])
        self.assertEqual(analyses[1]["action"], "wait for author")
        self.assertIn("CI failing", analyses[1]["flags"])
        self.assertIn("maintainer blocker language", analyses[1]["flags"])

    def test_forgejo_file_stats_are_used_without_pr_stats(self) -> None:
        normalized = normalize_forgejo_pr(
            {
                "number": 1,
                "title": "Small diff",
                "files": [
                    {"filename": "src/main.py", "additions": 3, "deletions": 1},
                    {"filename": "tests/test_main.py", "additions": 2, "deletions": 0},
                ],
            }
        )

        self.assertEqual(normalized["additions"], 5)
        self.assertEqual(normalized["deletions"], 1)

    def test_forgejo_conflict_merge_state_is_normalized(self) -> None:
        normalized = normalize_forgejo_pr(
            {
                "number": 2,
                "title": "Conflict",
                "mergeable": False,
                "requested_reviewers": [{"login": "maintainer"}],
            }
        )

        self.assertEqual(normalized["mergeStateStatus"], "DIRTY")
        self.assertEqual(normalized["mergeable"], "CONFLICTING")
        self.assertEqual(len(normalized["reviewRequests"]), 1)


class GitlabMergeStatusTests(unittest.TestCase):
    """Regression cover for GitLab merge-status to review-decision mapping."""

    def test_ci_must_pass_is_not_changes_requested(self) -> None:
        normalized = normalize_gitlab_mr(
            {"iid": 20, "title": "Add cache layer", "detailed_merge_status": "ci_must_pass"}
        )

        self.assertEqual(normalized["reviewDecision"], "REVIEW_REQUIRED")
        self.assertEqual(normalized["mergeStateStatus"], "BLOCKED")

    def test_not_approved_is_not_changes_requested(self) -> None:
        normalized = normalize_gitlab_mr(
            {"iid": 21, "title": "Add cache layer", "detailed_merge_status": "not_approved"}
        )

        self.assertEqual(normalized["reviewDecision"], "REVIEW_REQUIRED")
        self.assertEqual(normalized["mergeStateStatus"], "BLOCKED")

    def test_unresolved_discussions_still_request_changes(self) -> None:
        normalized = normalize_gitlab_mr(
            {
                "iid": 22,
                "title": "Add cache layer",
                "detailed_merge_status": "discussions_not_resolved",
            }
        )

        self.assertEqual(normalized["reviewDecision"], "CHANGES_REQUESTED")

    def test_ci_gate_does_not_push_merge_request_to_author_follow_up(self) -> None:
        analysis = analyze_pr(
            normalize_gitlab_mr(
                {
                    "iid": 23,
                    "title": "Add cache layer",
                    "description": "Test plan: unit tests.",
                    "updated_at": "2026-06-01T00:00:00Z",
                    "detailed_merge_status": "ci_must_pass",
                    "head_pipeline": {"status": "success", "ref": "cache"},
                    "changes_count": "2",
                    "stats": {"additions": 30, "deletions": 4},
                    "changes": [
                        {"new_path": "src/cache.py"},
                        {"new_path": "tests/test_cache.py"},
                    ],
                }
            )
        )

        self.assertNotIn("changes requested", analysis["flags"])
        self.assertIn("merge blocked by repo rules", analysis["flags"])
        self.assertEqual(analysis["action"], "review now")

    def test_blocked_pipeline_is_reported_as_pending(self) -> None:
        normalized = normalize_gitlab_mr(
            {"iid": 24, "title": "Manual gate", "pipeline": {"status": "blocked", "ref": "main"}}
        )
        check = normalized["statusCheckRollup"][0]

        self.assertEqual(check["status"], "BLOCKED")
        self.assertIsNone(check["conclusion"])

        analysis = analyze_pr(normalized)
        self.assertIn("CI pending", analysis["flags"])
        self.assertEqual(analysis["action"], "wait for CI")


if __name__ == "__main__":
    unittest.main()
