# Roadmap

## 0.1

- Deterministic PR scoring
- Markdown report output
- Offline JSON mode
- GitHub CLI integration
- Unit tests and CI

## 0.2

- Better maintainer blocker detection
- Repository health summary
- `--since` and `--label` filters
- More real-world fixtures

## 0.3

- GitLab support from exported merge request JSON
- Forgejo and Gitea support
- Optional comment classifier plugin
- Maintainer handoff report for release weeks

## 0.6

- CSV export for maintainers who keep review queues in spreadsheets

## 0.7

- Deterministic queue sorting for different maintainer review sessions

## 0.8

- Hydrated live GitHub scans for deeper body, file, and review signals

## 0.9

- Standalone static HTML reports for sharing local queue snapshots
- Copy-paste workflow examples for Markdown and HTML CI artifacts

## 0.10

- Focused top-N queue reports after filtering and sorting

## 0.11

- Stdin support for offline JSON pipelines
- Expanded maintainer workflow examples

## 0.12

- Reproducible report time with `--now`
- Generated sample output artifacts

## 0.13

- Score breakdowns for transparent risk impact in reports and automation

## 0.14

- Interactive browser preview for public GitHub repositories
- Public check-run signals and feedback links for the demo

## 0.15

- `init-action` workflow generator for scheduled reports
- GitHub Actions run-summary output for Markdown and compact summaries

## 0.16

- Reusable composite GitHub Action
- GitHub Action quick start and dedicated docs
- Browser demo Copy Workflow flow
- Project-specific config support for scheduled Action reports
- Deterministic next-step guidance in reports and generated samples

## Next

- More real-world maintainer blocker fixtures
- Better grouped review-session reports for busy queues
- Marketplace/listing discovery once the Action is published through GitHub UI

## Design Rules

- No hidden network service.
- No required AI model.
- No token storage.
- Prefer transparent heuristics over opaque scores.
- Markdown output first.
