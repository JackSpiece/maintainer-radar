# GitHub Action

Maintainer Radar ships as a reusable GitHub Action for repositories that want a
read-only pull request queue report in CI.

Use it when you want the report to appear in the GitHub Actions run summary and
also be saved as an artifact.

## Minimal Workflow

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
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - name: Build PR report
        id: radar
        uses: JackSpiece/maintainer-radar@v0.16.2
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

## Inputs

| Input | Default | Description |
| --- | --- | --- |
| `repository` | current workflow repository | Repository to scan in `owner/name` form. |
| `format` | `markdown` | Report format: `markdown`, `html`, `json`, or `csv`. |
| `output` | format-specific path | Output file path. Defaults to `maintainer-radar.md`, `.html`, `.json`, or `.csv`. |
| `limit` | `50` | Maximum pull requests to scan. |
| `sort` | `action` | Sort order: `input`, `action`, `score`, `risk`, `stale`, or `number`. |
| `top` | empty | Keep only the first N pull requests after sorting. |
| `hydrate` | `true` | Fetch full PR details for body, file, review, and richer scoring signals. |
| `step-summary` | `true` | Publish Markdown output or a compact summary to the Actions run summary. |

## Outputs

| Output | Description |
| --- | --- |
| `report-path` | Path to the generated report file. Use it with `actions/upload-artifact`. |

## Report Formats

Markdown is best for a run summary. HTML is best when maintainers want a local
browser-friendly artifact. JSON and CSV are useful for dashboards and
spreadsheets.

```yaml
with:
  repository: ${{ github.repository }}
  format: html
  output: maintainer-radar.html
```

For HTML, JSON, and CSV reports, the action still writes a compact Markdown
summary to the run summary by default. Disable that with:

```yaml
with:
  step-summary: "false"
```

## Bootstrap Command

If you already use the CLI locally, generate the workflow instead of writing YAML
by hand:

```bash
maintainer-radar init-action --path .github/workflows/maintainer-radar.yml
```

## Permissions

The action is read-only. It needs:

```yaml
permissions:
  contents: read
  pull-requests: read
```

It does not approve, reject, merge, label, or comment on pull requests.

## Troubleshooting

- If the action cannot read pull requests, confirm `GH_TOKEN: ${{ github.token }}`
  is present on the action step.
- If the report is shallow, keep `hydrate: "true"` so the action can inspect PR
  bodies, files, reviews, and richer signals.
- If the workflow is too slow for a large queue, lower `limit` or set `top`.
- If you only want downloadable artifacts, set `step-summary: "false"`.
