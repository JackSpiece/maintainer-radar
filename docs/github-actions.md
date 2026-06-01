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
- uses: JackSpiece/maintainer-radar@v0.16.4
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

The command prints YAML to stdout when `--path` is omitted. When `--path` is
provided, it creates parent directories and refuses to overwrite an existing
workflow unless `--force` is passed.

The action publishes Markdown output to the GitHub Actions run summary by
default. For HTML, JSON, and CSV artifacts, it also publishes a compact Markdown
summary so the first read does not require downloading an artifact. Use
`--no-step-summary` with `init-action`, or `step-summary: "false"` in direct
action usage, if you only want uploaded artifacts.

Copy-paste examples are available in:

- [examples/github-actions/daily-markdown-report.yml](../examples/github-actions/daily-markdown-report.yml)
- [examples/github-actions/daily-html-report.yml](../examples/github-actions/daily-html-report.yml)

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
        uses: JackSpiece/maintainer-radar@v0.16.4
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

## HTML Artifact

For a static browser-friendly report:

```yaml
- name: Build HTML report
  id: radar
  uses: JackSpiece/maintainer-radar@v0.16.4
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

For a review-ready queue artifact:

```yaml
- name: Build review-ready report
  env:
    GH_TOKEN: ${{ github.token }}
  run: maintainer-radar repo ${{ github.repository }} --action review-now --min-score 80 > review-ready.md
```

## Notes

- The tool uses `gh` for live GitHub data.
- GitHub-hosted runners include `gh` by default.
- The report is advisory. It does not approve, reject, or modify pull requests.
- Keep permissions read-only unless your own workflow adds posting behavior.
