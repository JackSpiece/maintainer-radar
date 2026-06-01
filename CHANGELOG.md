# Changelog

## 0.16.1

- Added dedicated GitHub Action usage documentation with copy-paste workflow, inputs, outputs, permissions, and troubleshooting.
- Linked GitHub Action docs from README, homepage navigation, and the GitHub Actions guide.
- Added tests that keep the action documentation discoverable and aligned with the action contract.

## 0.16.0

- Added a reusable composite GitHub Action via `action.yml`.
- Updated generated workflows and bundled examples to use `JackSpiece/maintainer-radar@v0.16.0`.
- Added action metadata tests for inputs, outputs, run-summary behavior, and read-only guardrails.
- Added CI smoke coverage that runs the action locally with `uses: ./`.

## 0.15.1

- Updated generated GitHub Actions workflows to publish Markdown reports or summaries to the Actions run summary by default.
- Added `--no-step-summary` for artifact-only workflows.
- Added step-summary coverage for Markdown and non-Markdown workflow artifacts.

## 0.15.0

- Added `init-action` to print or write a read-only GitHub Actions workflow.
- Added workflow rendering tests and CLI overwrite protection.
- Documented one-command workflow bootstrap in the README and GitHub Actions guide.

## 0.14.2

- Added Copy Markdown to the browser demo for paste-ready queue briefs.
- Added browser-demo Markdown rendering tests and documentation.

## 0.14.1

- Added shareable browser demo links with `?repo=owner/repo`.
- Added a Copy Link flow after scanning a public repository in the browser demo.

## 0.14.0

- Added a no-install browser preview for public GitHub repositories.
- Added public check-run signals to the browser preview for CI passed, failing, pending, or absent states.
- Added GitHub Pages demo metadata, social preview image, browser-preview documentation, and feedback links.
- Added CI coverage for browser demo assets, Pages metadata, and package version alignment.

## 0.13.0

- Added score breakdowns that show which heuristics changed each PR's risk score.
- Added risk impact output to Markdown, HTML, CSV, JSON, and detailed PR briefs.

## 0.12.0

- Added `--now` for reproducible stale calculations.
- Added generated sample output artifacts for Markdown, JSON, CSV, and HTML.

## 0.11.1

- Expanded maintainer workflow documentation with current CLI examples.

## 0.11.0

- Added stdin support for offline JSON with `from-json -`.
- Added stdin pipeline documentation.

## 0.10.0

- Added `--top` for focused queue reports after filtering and sorting.
- Added focused report documentation.

## 0.9.1

- Added copy-paste GitHub Actions workflow examples for Markdown and HTML artifacts.
- Added examples documentation.

## 0.9.0

- Added standalone static HTML report output.
- Added HTML output documentation.

## 0.8.0

- Added opt-in hydrated live GitHub scans with `--hydrate`.
- Added documentation for fast versus hydrated scan tradeoffs.

## 0.7.0

- Added queue sorting with `--sort` for action, score, risk, stale days, and PR number.
- Added queue sorting documentation.

## 0.6.0

- Added CSV output for queue reports and summary reports.
- Added CSV documentation for spreadsheet triage workflows.

## 0.5.1

- Added a README quickstart screenshot sequence using sample data.

## 0.5.0

- Added Forgejo and Gitea pull request JSON normalization.
- Added Forgejo/Gitea fixture coverage and documentation.

## 0.4.1

- Added `.maintainer-radar.json` configuration support for thresholds and path hints.

## 0.4.0

- Added GitLab merge request JSON normalization.
- Added GitLab fixture coverage and documentation.

## 0.3.0

- Added `pr --comment-template` for draft maintainer follow-up comments.

## 0.2.3

- Added JSON output documentation for scripts and dashboards.

## 0.2.2

- Added maintainer blocker fixture corpus.
- Added heuristic documentation.

## 0.2.1

- Added output filters for recommended action, minimum reviewability score, and maximum risk.

## 0.2.0

- Added `--summary-only` for queue commands.
- Added a terminal preview image to the README.
- Added GitHub Actions integration documentation.

## 0.1.3

- Added maintainer handoff and follow-up examples.

## 0.1.2

- Added label, author, stale-days, and updated-since filters for repo scans.

## 0.1.1

- Added a repo-level report summary.
- Updated GitHub Actions workflow to current official actions.

## 0.1.0

- Initial public release.
- Added deterministic PR scoring.
- Added Markdown and JSON output.
- Added GitHub CLI repository, PR, and author modes.
- Added offline JSON analysis mode.
- Added tests and CI.
