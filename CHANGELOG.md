# Changelog

## 0.16.23

- Added shareable browser demo links that preserve the current review-plan
  minutes with `?plan=30`.
- Copy Link, Copy Badge, copied Markdown, and the address bar now keep the
  current plan minutes after a scan.

## 0.16.22

- Added structured review-plan outputs to the reusable GitHub Action:
  `planned-prs`, `planned-minutes`, `remaining-minutes`, `deferred-prs`, and
  `watch-only-prs`.
- Added a reusable review-plan summary helper for plan output metrics.

## 0.16.21

- Updated browser Copy Workflow to generate a scheduled review-plan workflow
  using the current plan minutes value.

## 0.16.20

- Added a visible review-plan preview to the public browser demo, showing planned
  PRs, estimated active time, and remaining time before copying Markdown.

## 0.16.19

- Added Copy Plan to the public browser preview so visitors can copy a
  time-boxed review plan without installing the CLI.
- Added a plan-minutes control to the browser preview and documented the
  no-install review-plan flow.

## 0.16.18

- Added `--review-plan-minutes` for Markdown review-session plans that turn a
  PR queue into a time-boxed maintainer plan.
- Added `review-plan-minutes` support to generated workflows and the reusable
  GitHub Action.
- Added review plan docs and a copy-paste review-plan workflow example.

## 0.16.17

- Added a Maintainer blocked metric to the public browser preview and copied
  Markdown briefs.
- Documented the browser metric so the public demo matches the CLI and Action
  summary output.

## 0.16.16

- Added `maintainer_blocked` to summary output and `maintainer-blocked` to the
  reusable GitHub Action outputs.
- Added Maintainer blocked to Markdown, HTML, JSON, CSV, and compact Action run
  summaries.

## 0.16.15

- Expanded label-aware blocker scoring for dependency and upstream blocked PR
  labels such as `blocked-upstream` and `waiting-for-dependency`.

## 0.16.14

- Added label-aware blocker scoring for labels like blocked, do not merge,
  needs tests, changes requested, and waiting on author.
- Mirrored the label-aware blocker rule in the browser preview.

## 0.16.13

- Added a Copy CLI button to the public browser preview for copying the local
  command matching the current repository and grouped view.

## 0.16.12

- Added a Copy Badge button to the public browser preview for sharing a static
  README badge linked to the current scan.
- Documented the badge flow in the browser preview guide.

## 0.16.11

- Added shareable grouped browser preview links with `?group=action`.
- Made Copy Link and the address bar preserve the current Group by action view.

## 0.16.10

- Added a Group by action toggle to the public browser preview and made copied Markdown respect the grouped view.
- Updated the browser Copy Workflow output to include action-grouped reports.

## 0.16.9

- Added optional `--group-by action` support for Markdown and HTML reports so queues can be split into action sections.
- Added `group-by` support to the reusable GitHub Action, generated workflows, review-ready examples, docs, and CI smoke coverage.

## 0.16.8

- Added structured summary outputs to the reusable GitHub Action, including total, review-now, author-follow-up, CI, stale, and average-score counts.
- Updated Action docs and CI smoke coverage so workflows can consume report metrics without parsing artifacts.

## 0.16.7

- Added focused report filters to the reusable GitHub Action: label, author, stale-days, updated-since, action, min-score, and max-risk.
- Added matching `init-action` filter flags, focused Action docs, and a review-ready scheduled workflow example.

## 0.16.6

- Added deterministic `next_step` guidance to PR analyses so reports translate each action into a concrete maintainer move.
- Surfaced next steps in Markdown, HTML, CSV, JSON, detail output, generated samples, and the browser preview.

## 0.16.5

- Added a `config` input to the reusable GitHub Action so scheduled reports can use project-specific scoring thresholds.
- Added `maintainer-radar init-action --config` support and documented the Action config path in README and configuration docs.

## 0.16.4

- Updated README, package, Pages, and social-preview source descriptions to lead with the GitHub Action and read-only PR triage positioning.
- Added tests to keep public metadata aligned with the Action-first positioning.

## 0.16.3

- Added Copy Workflow to the browser demo so visitors can copy a ready scheduled GitHub Action workflow from the public preview.
- Added browser demo smoke coverage for workflow rendering and documented the new Copy Workflow button.

## 0.16.2

- Reworked the README quick start to lead with the reusable GitHub Action before local CLI install.
- Added a README ordering test so the Action adoption path stays prominent.

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
