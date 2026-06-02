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
        self.assertIn('href="review-plan.html"', html)
        self.assertIn("run summary", html)
        self.assertIn("time-boxed review", html)
        self.assertIn("Next step", html)
        self.assertIn("Maintainer blocked", html)
        self.assertIn("mergeable, review requested", html)
        self.assertIn("merge conflicts", html)
        self.assertIn("Resolve merge conflicts", html)
        self.assertIn("Review now while the PR appears small, active, and low risk.", html)
        self.assertIn('id="repo-form"', html)
        self.assertIn('id="copy-link"', html)
        self.assertIn('id="copy-badge"', html)
        self.assertIn('id="copy-cli"', html)
        self.assertIn('id="copy-markdown"', html)
        self.assertIn('id="copy-plan"', html)
        self.assertIn('id="copy-plan-json"', html)
        self.assertIn('id="copy-workflow"', html)
        self.assertIn('id="plan-minutes"', html)
        self.assertIn('id="plan-title"', html)
        self.assertIn('id="plan-meta"', html)
        self.assertIn('id="plan-body"', html)
        self.assertIn('id="draft-meta"', html)
        self.assertIn('id="draft-followup-body"', html)
        self.assertIn('data-copy-target="demo-draft-follow-up-1"', html)
        self.assertIn("Copy Draft", html)
        self.assertIn("Copy Plan", html)
        self.assertIn("30 minute review plan", html)
        self.assertIn('id="metric-blocked"', html)
        self.assertIn('id="attention-card"', html)
        self.assertIn('id="attention-level"', html)
        self.assertIn('id="attention-headline"', html)
        self.assertIn('id="attention-reason"', html)
        self.assertIn("Queue attention", html)
        self.assertIn('id="group-action"', html)
        self.assertIn("Group by action", html)
        self.assertIn('href="browser-preview.html"', html)
        self.assertIn("https://github.com/JackSpiece/maintainer-radar/issues/new/choose", html)
        self.assertIn('<script src="assets/demo.js"></script>', html)
        self.assertIn("Read-only PR triage reports and review plans for maintainers", html)
        self.assertIn('property="og:image"', html)
        self.assertIn("https://jackspiece.github.io/maintainer-radar/assets/social-preview.png", html)
        self.assertIn('name="twitter:card" content="summary_large_image"', html)

    def test_adoption_guide_has_copy_paste_workflows(self) -> None:
        docs = (ROOT / "docs" / "adoption.md").read_text(encoding="utf-8")

        self.assertIn("Adoption Guide", docs)
        self.assertIn("Daily Queue Brief", docs)
        self.assertIn("Review-Ready Queue", docs)
        self.assertIn("30 Minute Review Plan", docs)
        self.assertIn("Stale Follow-Up Queue", docs)
        self.assertIn("Merge Readiness Watch", docs)
        self.assertIn("JackSpiece/maintainer-radar@v0.16.36", docs)
        self.assertIn("review-plan-minutes", docs)
        self.assertIn("merge-conflicts", docs)
        self.assertIn("branch-behind", docs)
        self.assertIn("merge-gated", docs)
        self.assertIn("review-requested", docs)
        self.assertIn("queue-headline", docs)
        self.assertIn("attention-level", docs)
        self.assertIn("attention-reason", docs)
        self.assertIn("group-by: action", docs)
        self.assertIn("does not approve, reject, merge, label, or comment", docs)

    def test_pages_markdown_keeps_actions_expressions_in_raw_blocks(self) -> None:
        for path in sorted((ROOT / "docs").glob("*.md")):
            in_raw_block = False
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if "{% raw %}" in line:
                    self.assertFalse(in_raw_block, f"{path}:{lineno} nested raw block")
                    in_raw_block = True

                if "${{" in line:
                    self.assertTrue(in_raw_block, f"{path}:{lineno} needs a Liquid raw block")

                if "{% endraw %}" in line:
                    self.assertTrue(in_raw_block, f"{path}:{lineno} raw block was not open")
                    in_raw_block = False

            self.assertFalse(in_raw_block, f"{path} has an unclosed raw block")

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("{% raw %}", readme)
        self.assertNotIn("{% endraw %}", readme)

    def test_positioning_keeps_before_review_message(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        docs = (ROOT / "docs" / "positioning.md").read_text(encoding="utf-8")

        self.assertIn("Use AI reviewers to inspect code", readme)
        self.assertIn("time-boxed review plan", readme)
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
        self.assertIn("Read-only PR triage + review plans", svg)
        self.assertIn("Copy draft asks", svg)
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
        self.assertIn("?repo=python/cpython&plan=30", docs)
        self.assertIn("?repo=python/cpython&group=action&plan=30", docs)
        self.assertIn("Copy Link", docs)
        self.assertIn("Copy Badge", docs)
        self.assertIn("Copy CLI", docs)
        self.assertIn("--group-by action", docs)
        self.assertIn("static Markdown badge", docs)
        self.assertIn("Copy Markdown", docs)
        self.assertIn("Copy Plan", docs)
        self.assertIn("Copy JSON", docs)
        self.assertIn("Copy Draft", docs)
        self.assertIn("draft follow-up panel", docs)
        self.assertIn("planned,\ndeferred, and watch-only PR arrays", docs)
        self.assertIn("draft_follow_up_comment", docs)
        self.assertIn("--review-plan-minutes 30", docs)
        self.assertIn("copied demo links", docs)
        self.assertIn("Copy Workflow", docs)
        self.assertIn("current plan minutes", docs)
        self.assertIn("Maintainer blocked", docs)
        self.assertIn("attention card", docs)
        self.assertIn("blocked`, `follow-up`, `triage`, `review`, or `quiet", docs)
        self.assertIn("Group by action", docs)
        self.assertIn("merge conflicts, branch-behind state, and repository merge gates", docs)
        self.assertIn("requested reviewers and teams", docs)

    def test_github_action_docs_explain_contract_and_guardrails(self) -> None:
        docs = (ROOT / "docs" / "github-action.md").read_text(encoding="utf-8")

        self.assertIn("JackSpiece/maintainer-radar@v0.16.36", docs)
        self.assertIn("report-path", docs)
        self.assertIn("step-summary", docs)
        self.assertIn("maintainer-blocked", docs)
        self.assertIn("queue-headline", docs)
        self.assertIn("attention-level", docs)
        self.assertIn("attention-reason", docs)
        self.assertIn('echo "Attention: ${{ steps.radar.outputs.attention-level }}"', docs)
        self.assertNotIn('echo "${{ steps.radar.outputs.attention-level }}:', docs)
        self.assertIn("review-plan-minutes", docs)
        self.assertIn("contents: read", docs)
        self.assertIn("pull-requests: read", docs)
        self.assertIn("format: html", docs)
        self.assertIn("review-plan.html", docs)
        self.assertIn("review-plan.json", docs)
        self.assertIn(
            "review plans default to `review-plan.md`, `review-plan.html`, or `review-plan.json`",
            docs,
        )
        self.assertIn("estimated active time", docs)
        self.assertIn("watch-only count", docs)
        self.assertIn("draft follow-up comments", docs)
        self.assertIn("Copy\nDraft buttons", docs)
        self.assertIn("does not approve, reject, merge, label, or comment", docs)

    def test_review_plan_docs_explain_time_boxed_workflow(self) -> None:
        docs = (ROOT / "docs" / "review-plan.md").read_text(encoding="utf-8")

        self.assertIn("Review Plans", docs)
        self.assertIn("--review-plan-minutes 30", docs)
        self.assertIn("--format html --review-plan-minutes 30", docs)
        self.assertIn("--format json --review-plan-minutes 30", docs)
        self.assertIn("review-plan-minutes", docs)
        self.assertIn("browser-friendly", docs)
        self.assertIn("dashboards and automation", docs)
        self.assertIn("watch-only", docs)
        self.assertIn("Draft Follow-ups", docs)
        self.assertIn("Copy Draft", docs)
        self.assertIn("draft_follow_up_comment", docs)
        self.assertIn("does not approve, reject, merge, label, or comment", docs)

    def test_html_output_docs_explain_copyable_review_plan_drafts(self) -> None:
        docs = (ROOT / "docs" / "html-output.md").read_text(encoding="utf-8")

        self.assertIn("HTML Output", docs)
        self.assertIn("Copy Draft", docs)
        self.assertIn("embedded copy\nhelper", docs)
        self.assertIn("does not load external JavaScript", docs)

    def test_summary_output_docs_include_maintainer_blocked(self) -> None:
        json_docs = (ROOT / "docs" / "json-output.md").read_text(encoding="utf-8")
        csv_docs = (ROOT / "docs" / "csv-output.md").read_text(encoding="utf-8")

        self.assertIn("maintainer_blocked", json_docs)
        self.assertIn("merge_state_status", json_docs)
        self.assertIn("review_requests", json_docs)
        self.assertIn("merge_conflicts", json_docs)
        self.assertIn("branch_behind", json_docs)
        self.assertIn("merge_gated", json_docs)
        self.assertIn("review_requested", json_docs)
        self.assertIn("queue_headline", json_docs)
        self.assertIn("attention_level", json_docs)
        self.assertIn("attention_reason", json_docs)
        self.assertIn("PRs blocked by maintainer feedback or labels", json_docs)
        self.assertIn("maintainer_blocked", csv_docs)
        self.assertIn("merge_conflicts", csv_docs)
        self.assertIn("branch_behind", csv_docs)
        self.assertIn("merge_gated", csv_docs)
        self.assertIn("review_requested", csv_docs)
        self.assertIn("queue_headline", csv_docs)
        self.assertIn("attention_level", csv_docs)
        self.assertIn("attention_reason", csv_docs)

    def test_heuristics_docs_explain_label_blockers(self) -> None:
        docs = (ROOT / "docs" / "heuristics.md").read_text(encoding="utf-8")

        self.assertIn("maintainer blocking label", docs)
        self.assertIn("waiting on author", docs)
        self.assertIn("waiting for dependency", docs)
        self.assertIn("blocked upstream", docs)
        self.assertIn("These labels route the PR to author follow-up", docs)
        self.assertIn("Merge Readiness", docs)
        self.assertIn("Merge conflicts route the PR to author follow-up", docs)
        self.assertIn("Requested reviewers are shown as positive queue context", docs)


if __name__ == "__main__":
    unittest.main()
