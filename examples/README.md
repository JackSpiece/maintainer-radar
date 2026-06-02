# Examples

This directory contains sample inputs and copy-paste workflow examples.

## Offline Data

- `sample-prs.json`: small GitHub-shaped PR queue for trying `from-json`
- `maintainer-radar-config.json`: sample project-specific threshold config

Generate a fresh config profile with:

```bash
maintainer-radar init-config --profile strict --path .maintainer-radar.json
```

## GitHub Actions

- `github-actions/daily-markdown-report.yml`: scheduled Markdown artifact
- `github-actions/daily-html-report.yml`: scheduled HTML artifact
- `github-actions/review-ready-report.yml`: focused scheduled report for high-score PRs

Copy one workflow into `.github/workflows/` in a repository that uses GitHub pull
requests, then run it manually from the Actions tab or wait for the schedule.
The examples use the reusable `JackSpiece/maintainer-radar` GitHub Action and
upload the generated report path exposed by the action. The review-ready example
uses the Action filters to keep only `review-now` PRs with a score of at least
80.

## Generated Output

- `output/sample-report.md`
- `output/sample-report.json`
- `output/sample-report.csv`
- `output/sample-report.html`

These files show the same sample queue in every supported output format,
including risk impact explanations. They are generated from `sample-prs.json`
with a fixed report time:

```bash
PYTHONPATH=src python -m maintainer_radar from-json examples/sample-prs.json \
  --now 2026-06-01T00:00:00Z
```
