# GitHub Actions Integration

Maintainer Radar can run in CI and upload Markdown or HTML triage reports as
artifacts. This is useful for maintainers who want a daily queue snapshot
without installing another GitHub App.

For the reusable action contract, inputs, outputs, and troubleshooting, see
[github-action.md](github-action.md).

The fastest setup is the bootstrap command:

```bash
maintainer-radar init-action --path .github/workflows/maintainer-radar.yml
```

This writes a workflow that uses the reusable action:

```yaml
- uses: actions/setup-python@v6
  with:
    python-version: "3.12"
- uses: JackSpiece/maintainer-radar@v0.16.17
  id: radar
  env:
    GH_TOKEN: ${{ github.token }}
  with:
    repository: ${{ github.repository }}
    format: markdown
```

For an HTML artifact:

```bash
maintainer-radar init-action \
  --report-format html \
  --path .github/workflows/maintainer-radar.yml
```

For a focused review-ready report:

```bash
maintainer-radar init-action \
  --action review-now \
  --min-score 80 \
  --top 10 \
  --group-by action \
  --path .github/workflows/review-ready.yml
```

The command prints YAML to stdout when `--path` is omitted. When `--path` is
provided, it creates parent directories and refuses to overwrite an existing
workflow unless `--force` is passed.

The action publishes Markdown output to the GitHub Actions run summary by
default. For HTML, JSON, and CSV artifacts, it also publishes a compact Markdown
summary so the first read does not require downloading an artifact. Use
`--no-step-summary` with `init-action`, or `step-summary: "false"` in direct
action usage, if you only want uploaded artifacts.

The reusable Action also exposes summary outputs such as `review-now`,
`ci-blocked`, `maintainer-blocked`, `stale`, and `average-score` for later
workflow steps.

Copy-paste examples are available in:

- [examples/github-actions/daily-markdown-report.yml](../examples/github-actions/daily-markdown-report.yml)
- [examples/github-actions/daily-html-report.yml](../examples/github-actions/daily-html-report.yml)
- [examples/github-actions/review-ready-report.yml](../examples/github-actions/review-ready-report.yml)

## Scheduled Queue Report

```yaml
name: Maintainer Radar

on:
  workflow_dispatch:
  schedule:
    - cron: "0 8 * * 1-5"

permissions:
  contents: read
  pull-requests: read

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - name: Build PR report
        id: radar
        uses: JackSpiece/maintainer-radar@v0.16.17
        env:
          GH_TOKEN: ${{ github.token }}
        with:
          repository: ${{ github.repository }}
          format: markdown
          output: maintainer-radar.md
          limit: "50"
          sort: action
          hydrate: "true"
      - uses: actions/upload-artifact@v4
        with:
          name: maintainer-radar
          path: ${{ steps.radar.outputs.report-path }}
```

## Focused Review-Ready Report

For a smaller scheduled report that only shows PRs ready for maintainer review:

```yaml
- name: Build review-ready report
  id: radar
  uses: JackSpiece/maintainer-radar@v0.16.17
  env:
    GH_TOKEN: ${{ github.token }}
  with:
    repository: ${{ github.repository }}
    format: markdown
    output: review-ready.md
    action: review-now
    min-score: "80"
    top: "10"
    group-by: action
    sort: score
    hydrate: "true"
- uses: actions/upload-artifact@v4
  with:
    name: review-ready
    path: ${{ steps.radar.outputs.report-path }}
```

## HTML Artifact

For a static browser-friendly report:

```yaml
- name: Build HTML report
  id: radar
  uses: JackSpiece/maintainer-radar@v0.16.17
  env:
    GH_TOKEN: ${{ github.token }}
  with:
    repository: ${{ github.repository }}
    format: html
    output: maintainer-radar.html
    limit: "50"
    sort: action
    hydrate: "true"
- uses: actions/upload-artifact@v4
  with:
    name: maintainer-radar-html
    path: ${{ steps.radar.outputs.report-path }}
```

## Summary-Only Report

For a compact status artifact:

```yaml
- name: Build PR summary
  env:
    GH_TOKEN: ${{ github.token }}
  run: maintainer-radar repo ${{ github.repository }} --limit 100 --summary-only > maintainer-radar-summary.md
```

## Notes

- The tool uses `gh` for live GitHub data.
- GitHub-hosted runners include `gh` by default.
- The report is advisory. It does not approve, reject, or modify pull requests.
- Keep permissions read-only unless your own workflow adds posting behavior.
