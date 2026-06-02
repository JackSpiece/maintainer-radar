# Two Minute Quickstart

Use this path when you want to see whether Maintainer Radar helps a repository
before changing any maintainer workflow.

## No Install Preview

For a public GitHub repository, open the browser preview and replace the query
with your repository:

```text
https://jackspiece.github.io/maintainer-radar/?repo=owner/repo
```

The browser preview uses public pull request metadata. It does not ask for a
GitHub token, does not post comments, and does not install anything.

## First GitHub Action Run

For a real maintainer queue report, add this workflow and run it manually:

{% raw %}
```yaml
name: Maintainer Radar

on:
  workflow_dispatch:

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
      - uses: JackSpiece/maintainer-radar@v0.18.0
        id: radar
        env:
          GH_TOKEN: ${{ github.token }}
        with:
          repository: ${{ github.repository }}
          format: markdown
          hydrate: true
          sort: action
          review-plan-minutes: 60
```
{% endraw %}

Open the Action run summary after it finishes. The summary should show:

- `queue-headline`: the one-line state of the PR queue
- `attention-level`: whether the queue is blocked, needs follow-up, needs
  triage, is ready for review, or is quiet
- `workflow-mode`: the suggested maintainer workflow for the next pass
- `next-session-brief`: what fits in the next 60 minutes

The workflow is read-only. It does not approve, reject, merge, label, or comment.

## First CLI Run

Install from GitHub if you want to test locally:

```bash
python -m pip install "git+https://github.com/JackSpiece/maintainer-radar.git"
```

Then paste a repository URL:

```bash
maintainer-radar recommend https://github.com/owner/repo/pulls
maintainer-radar repo https://github.com/owner/repo/pulls --hydrate --sort action --summary-only
```

Or inspect one pull request:

```bash
maintainer-radar pr https://github.com/owner/repo/pull/123
```

Live CLI scans use the GitHub CLI for authenticated GitHub API access:

```bash
gh auth login
```

## What To Do With The First Report

Use the report to choose one concrete maintainer session:

- Run `maintainer-radar recommend owner/repo` when you only want the next
  workflow, attention level, and exact follow-up commands.
- If `attention-level` is `blocked`, clear CI failures, conflicts, stale branch
  state, or unresolved maintainer blockers first.
- If `workflow-mode` is `review-sprint`, review the highest-score PRs while
  they are still small and active.
- If `workflow-mode` is `author-follow-up`, send edited follow-up asks instead
  of starting deep review.
- If `attention-level` is `quiet`, leave the workflow scheduled and avoid
  checking the queue by hand.

For scheduled workflows and notification gates, see
[Attention Workflows](attention-workflows.md) and
[GitHub Action Usage](github-action.md).
