# Adoption Guide

Use Maintainer Radar in one repository first. The goal is a useful queue brief,
not another required maintainer ritual.

## Preview A Real Queue

Start with the browser preview on a public repository:

```text
https://jackspiece.github.io/maintainer-radar/?repo=owner/repo&group=action
```

If the grouped view matches how maintainers already think about the queue, add a
scheduled workflow.

## Daily Queue Brief

Use this when maintainers want one read-only report every weekday:

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
        uses: JackSpiece/maintainer-radar@v0.16.18
        env:
          GH_TOKEN: ${{ github.token }}
        with:
          repository: ${{ github.repository }}
          format: markdown
          output: maintainer-radar.md
          limit: "50"
          sort: action
          group-by: action
          hydrate: "true"
      - uses: actions/upload-artifact@v4
        with:
          name: maintainer-radar
          path: ${{ steps.radar.outputs.report-path }}
```

The Markdown report appears in the run summary and is also uploaded as an
artifact.

## Review-Ready Queue

Use this when the queue is large and maintainers only want PRs likely to be
worth reviewing now:

```yaml
- name: Build review-ready report
  id: radar
  uses: JackSpiece/maintainer-radar@v0.16.18
  env:
    GH_TOKEN: ${{ github.token }}
  with:
    repository: ${{ github.repository }}
    format: markdown
    output: review-ready.md
    action: review-now
    min-score: "80"
    top: "10"
    sort: score
    group-by: action
    hydrate: "true"
```

This keeps the report short enough to scan during a review session.

## 30 Minute Review Plan

Use this when maintainers want a concrete plan for a short review block:

```yaml
- name: Build 30 minute review plan
  id: radar
  uses: JackSpiece/maintainer-radar@v0.16.18
  env:
    GH_TOKEN: ${{ github.token }}
  with:
    repository: ${{ github.repository }}
    format: markdown
    output: review-plan.md
    review-plan-minutes: "30"
    sort: action
    hydrate: "true"
```

The plan estimates active maintainer time, lists PRs that fit the budget, and
keeps wait-for-CI or wait-for-author items in a watch-only section.

## Stale Follow-Up Queue

Use this when the team needs to clear old contributor threads:

```yaml
- name: Build stale follow-up report
  id: radar
  uses: JackSpiece/maintainer-radar@v0.16.18
  env:
    GH_TOKEN: ${{ github.token }}
  with:
    repository: ${{ github.repository }}
    format: markdown
    output: stale-follow-up.md
    stale-days: "14"
    sort: action
    group-by: action
    hydrate: "true"
```

Read the next-step column before writing replies. Maintainer Radar drafts
priorities, not decisions.

## First Run Checklist

- Run the workflow manually with `workflow_dispatch`.
- Confirm the report appears in the Actions run summary.
- Open the uploaded artifact if the summary is too long.
- Check that the top few PRs feel correctly grouped.
- If the queue is noisy, tighten the workflow with `action`, `min-score`,
  `stale-days`, `label`, `author`, or `top`.

## Keep It Read-Only

Maintainer Radar does not approve, reject, merge, label, or comment on pull
requests. Treat the report as a queue map for humans.
