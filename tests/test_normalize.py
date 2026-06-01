from __future__ import annotations

import json
from pathlib import Path
import unittest

from maintainer_radar.normalize import normalize_gitlab_mr, normalize_items
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


if __name__ == "__main__":
    unittest.main()

