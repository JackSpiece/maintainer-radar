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
        uses: JackSpiece/maintainer-radar@v0.16.32
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
| `output` | format-specific path | Output file path. Defaults to `maintainer-radar.md`, `.html`, `.json`, or `.csv`; review plans default to `review-plan.md`, `review-plan.html`, or `review-plan.json`. |
| `limit` | `50` | Maximum pull requests to scan. |
| `label` | empty | Only include pull requests with this label. |
| `author` | empty | Only include pull requests by this author. |
| `stale-days` | empty | Only include pull requests quiet for at least N days. |
| `updated-since` | empty | Only include pull requests updated on or after this ISO date. |
| `action` | empty | Only include pull requests with this action slug, such as `review-now`. |
| `min-score` | empty | Only include pull requests with reviewability greater than or equal to N. |
| `max-risk` | empty | Only include pull requests with risk less than or equal to N. |
| `sort` | `action` | Sort order: `input`, `action`, `score`, `risk`, `stale`, or `number`. |
| `top` | empty | Keep only the first N pull requests after sorting. |
| `group-by` | empty | Group Markdown and HTML queue reports. Supported value: `action`. |
| `review-plan-minutes` | empty | Render a Markdown, HTML, or JSON review-session plan for this many maintainer minutes. |
| `config` | empty | Optional path to a Maintainer Radar config JSON file. |
| `hydrate` | `true` | Fetch full PR details for body, file, review, merge readiness, and richer scoring signals. |
| `step-summary` | `true` | Publish Markdown output or a compact summary to the Actions run summary. |

## Outputs

| Output | Description |
| --- | --- |
| `report-path` | Path to the generated report file. Use it with `actions/upload-artifact`. |
| `summary-json` | JSON summary for the generated report. |
| `total` | Number of pull requests in the report after filters. |
| `review-now` | Number of pull requests ready for review. |
| `author-follow-up` | Number of pull requests needing author follow-up. |
| `ci-blocked` | Number of pull requests with failing CI. |
| `ci-pending` | Number of pull requests waiting for CI. |
| `maintainer-blocked` | Number of pull requests blocked by maintainer feedback or labels. |
| `large-or-triage` | Number of pull requests that are too large or need triage. |
| `stale` | Number of pull requests quiet for 7 or more days. |
| `average-score` | Average reviewability score for the report. |
| `plan-budget-minutes` | Review-plan budget in minutes when `review-plan-minutes` is set. |
| `planned-prs` | Number of pull requests included in the review plan. |
| `planned-minutes` | Estimated active maintainer minutes in the review plan. |
| `remaining-minutes` | Unused minutes left in the review-plan budget. |
| `deferred-prs` | Number of pull requests deferred by the review-plan budget. |
| `watch-only-prs` | Number of wait-for-CI or wait-for-author pull requests in the review plan. |

Use summary outputs in later workflow steps:

```yaml
- run: echo "${{ steps.radar.outputs.review-now }} PRs are ready for review"
```

For handoff or escalation workflows, use `maintainer-blocked` to detect PRs
that already have maintainer feedback or blocking labels.

For review-plan workflows, use `planned-prs`, `planned-minutes`,
`remaining-minutes`, `deferred-prs`, and `watch-only-prs` in later notification
or dashboard steps without parsing the Markdown artifact.

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

For HTML and JSON review-plan artifacts, the run summary also includes the plan
budget, planned PR count, estimated active time, remaining minutes, deferred
count, and watch-only count.

Review plans also include draft follow-up comments for PRs that need author
action. The Action does not post those comments; it only writes the draft text
to the report artifact or JSON fields. HTML review-plan artifacts include Copy
Draft buttons for those drafts.

## Focused Reports

Use filters when a scheduled report should answer one review-session question
instead of listing the whole queue:

```yaml
with:
  repository: ${{ github.repository }}
  action: review-now
  min-score: "80"
  top: "10"
  group-by: action
```

For a time-boxed maintainer session, add a review plan. Use Markdown when you
want the plan in the run summary:

```yaml
with:
  repository: ${{ github.repository }}
  format: markdown
  sort: action
  review-plan-minutes: "30"
  hydrate: "true"
```

Use HTML when you want a browser-friendly plan artifact:

```yaml
with:
  repository: ${{ github.repository }}
  format: html
  output: review-plan.html
  sort: action
  review-plan-minutes: "30"
  hydrate: "true"
```

See [review-plan.md](review-plan.md) for how the estimates work.

For stale follow-up sweeps:

```yaml
with:
  repository: ${{ github.repository }}
  stale-days: "14"
  sort: stale
```

## Project Config

Use the `config` input when a repository has custom size, stale, test path, doc
path, or generated file thresholds:

```yaml
with:
  repository: ${{ github.repository }}
  config: .maintainer-radar.json
```

## Bootstrap Command

If you already use the CLI locally, generate the workflow instead of writing YAML
by hand:

```bash
maintainer-radar init-action --path .github/workflows/maintainer-radar.yml
maintainer-radar init-action --config .maintainer-radar.json --path .github/workflows/maintainer-radar.yml
maintainer-radar init-action --action review-now --min-score 80 --top 10 --path .github/workflows/review-ready.yml
maintainer-radar init-action --review-plan-minutes 30 --path .github/workflows/review-plan.yml
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
