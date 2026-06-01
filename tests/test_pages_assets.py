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
        self.assertIn("run summary", html)
        self.assertIn('id="repo-form"', html)
        self.assertIn('id="copy-link"', html)
        self.assertIn('id="copy-markdown"', html)
        self.assertIn('href="browser-preview.html"', html)
        self.assertIn("https://github.com/JackSpiece/maintainer-radar/issues/new/choose", html)
        self.assertIn('<script src="assets/demo.js"></script>', html)
        self.assertIn('property="og:image"', html)
        self.assertIn("https://jackspiece.github.io/maintainer-radar/assets/social-preview.png", html)
        self.assertIn('name="twitter:card" content="summary_large_image"', html)

    def test_social_preview_png_has_expected_dimensions(self) -> None:
        data = (ROOT / "docs" / "assets" / "social-preview.png").read_bytes()

        self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))
        width, height = struct.unpack(">II", data[16:24])
        self.assertEqual((width, height), (1200, 630))

    def test_social_preview_svg_keeps_source_text(self) -> None:
        svg = (ROOT / "docs" / "assets" / "social-preview.svg").read_text(encoding="utf-8")

        self.assertIn("Maintainer Radar", svg)
        self.assertIn("Local-first PR triage for maintainers", svg)
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
        self.assertIn("Copy Markdown", docs)


if __name__ == "__main__":
    unittest.main()
