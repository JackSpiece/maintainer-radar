# GitHub Actions Integration

Maintainer Radar can run in CI and upload Markdown or HTML triage reports as
artifacts. This is useful for maintainers who want a daily queue snapshot
without installing another GitHub App.

The fastest setup is the bootstrap command:

```bash
maintainer-radar init-action --path .github/workflows/maintainer-radar.yml
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

Generated workflows publish Markdown output to the GitHub Actions run summary by
default. For HTML, JSON, and CSV artifacts, the workflow also publishes a compact
Markdown summary so the first read does not require downloading an artifact. Use
`--no-step-summary` if you only want uploaded artifacts.

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
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - name: Install Maintainer Radar
        run: python -m pip install git+https://github.com/JackSpiece/maintainer-radar.git
      - name: Build PR report
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          maintainer-radar repo "${{ github.repository }}" \
            --limit 50 \
            --hydrate \
            --sort action \
            > maintainer-radar.md
      - uses: actions/upload-artifact@v4
        with:
          name: maintainer-radar
          path: maintainer-radar.md
```

## HTML Artifact

For a static browser-friendly report:

```yaml
- name: Build HTML report
  env:
    GH_TOKEN: ${{ github.token }}
  run: |
    maintainer-radar repo "${{ github.repository }}" \
      --limit 50 \
      --hydrate \
      --sort action \
      --format html \
      > maintainer-radar.html
- uses: actions/upload-artifact@v4
  with:
    name: maintainer-radar-html
    path: maintainer-radar.html
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
