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

    def test_blocker_fixture_corpus_detects_maintainer_blockers(self) -> None:
        fixture_path = Path(__file__).parent / "fixtures" / "blocker-prs.json"
        prs = json.loads(fixture_path.read_text(encoding="utf-8"))

        for pr in prs:
            with self.subTest(pr=pr["number"]):
                result = analyze_pr(pr, now=NOW)
                self.assertIn("maintainer blocker language", result["flags"])

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



if __name__ == "__main__":
    unittest.main()
