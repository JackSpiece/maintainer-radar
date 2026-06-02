from __future__ import annotations

from pathlib import Path
import struct
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PagesAssetTests(unittest.TestCase):
    def test_pages_demo_has_share_metadata_and_interactive_script(self) -> None:
        html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")

        self.assertIn("Try a public repo", html)
        self.assertIn("maintainer-radar init-action", html)
        self.assertIn("GitHub Action", html)
        self.assertIn('href="adoption.html"', html)
        self.assertIn('href="github-action.html"', html)
        self.assertIn("run summary", html)
        self.assertIn("Next step", html)
        self.assertIn("Review now while the PR appears small, active, and low risk.", html)
        self.assertIn('id="repo-form"', html)
        self.assertIn('id="copy-link"', html)
        self.assertIn('id="copy-badge"', html)
        self.assertIn('id="copy-markdown"', html)
        self.assertIn('id="copy-workflow"', html)
        self.assertIn('id="group-action"', html)
        self.assertIn("Group by action", html)
        self.assertIn('href="browser-preview.html"', html)
        self.assertIn("https://github.com/JackSpiece/maintainer-radar/issues/new/choose", html)
        self.assertIn('<script src="assets/demo.js"></script>', html)
        self.assertIn("GitHub Action and local CLI for read-only PR triage reports", html)
        self.assertIn('property="og:image"', html)
        self.assertIn("https://jackspiece.github.io/maintainer-radar/assets/social-preview.png", html)
        self.assertIn('name="twitter:card" content="summary_large_image"', html)

    def test_adoption_guide_has_copy_paste_workflows(self) -> None:
        docs = (ROOT / "docs" / "adoption.md").read_text(encoding="utf-8")

        self.assertIn("Adoption Guide", docs)
        self.assertIn("Daily Queue Brief", docs)
        self.assertIn("Review-Ready Queue", docs)
        self.assertIn("Stale Follow-Up Queue", docs)
        self.assertIn("JackSpiece/maintainer-radar@v0.16.12", docs)
        self.assertIn("group-by: action", docs)
        self.assertIn("does not approve, reject, merge, label, or comment", docs)

    def test_positioning_keeps_before_review_message(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        docs = (ROOT / "docs" / "positioning.md").read_text(encoding="utf-8")

        self.assertIn("Use AI reviewers to inspect code", readme)
        self.assertIn("Before-review workflow", readme)
        self.assertIn("Where should a maintainer spend review attention first?", docs)
        self.assertIn("What It Refuses To Do", docs)
        self.assertIn("does not approve, reject, merge, label, or comment", docs)

    def test_social_preview_png_has_expected_dimensions(self) -> None:
        data = (ROOT / "docs" / "assets" / "social-preview.png").read_bytes()

        self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))
        width, height = struct.unpack(">II", data[16:24])
        self.assertEqual((width, height), (1200, 630))

    def test_social_preview_svg_keeps_source_text(self) -> None:
        svg = (ROOT / "docs" / "assets" / "social-preview.svg").read_text(encoding="utf-8")

        self.assertIn("Maintainer Radar", svg)
        self.assertIn("GitHub Action for PR triage", svg)
        self.assertIn("uses: JackSpiece/maintainer-radar", svg)
        self.assertIn("jackspiece.github.io/maintainer-radar", svg)

    def test_browser_preview_docs_explain_network_and_limits(self) -> None:
        docs = (ROOT / "docs" / "browser-preview.md").read_text(encoding="utf-8")

        self.assertIn("public GitHub API", docs)
        self.assertIn("does not ask for a GitHub token", docs)
        self.assertIn("does not post comments", docs)
        self.assertIn("rate-limit", docs)
        self.assertIn("issues/new/choose", docs)
        self.assertIn("?repo=python/cpython", docs)
        self.assertIn("Copy Link", docs)
        self.assertIn("Copy Badge", docs)
        self.assertIn("static Markdown badge", docs)
        self.assertIn("Copy Markdown", docs)
        self.assertIn("Copy Workflow", docs)
        self.assertIn("Group by action", docs)
        self.assertIn("?repo=python/cpython&group=action", docs)

    def test_github_action_docs_explain_contract_and_guardrails(self) -> None:
        docs = (ROOT / "docs" / "github-action.md").read_text(encoding="utf-8")

        self.assertIn("JackSpiece/maintainer-radar@v0.16.12", docs)
        self.assertIn("report-path", docs)
        self.assertIn("step-summary", docs)
        self.assertIn("contents: read", docs)
        self.assertIn("pull-requests: read", docs)
        self.assertIn("does not approve, reject, merge, label, or comment", docs)


if __name__ == "__main__":
    unittest.main()
