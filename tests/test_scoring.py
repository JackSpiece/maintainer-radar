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

    def test_blocker_fixture_corpus_detects_maintainer_blockers(self) -> None:
        fixture_path = Path(__file__).parent / "fixtures" / "blocker-prs.json"
        prs = json.loads(fixture_path.read_text(encoding="utf-8"))

        for pr in prs:
            with self.subTest(pr=pr["number"]):
                result = analyze_pr(pr, now=NOW)
                self.assertIn("maintainer blocker language", result["flags"])



if __name__ == "__main__":
    unittest.main()
