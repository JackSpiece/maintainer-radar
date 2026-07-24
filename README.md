# Maintainer Radar

[![CI](https://github.com/JackSpiece/maintainer-radar/actions/workflows/ci.yml/badge.svg)](https://github.com/JackSpiece/maintainer-radar/actions/workflows/ci.yml)

Know which pull requests deserve your time before you open a single diff.

Maintainer Radar scans your PR queue and produces a short, honest brief: what to review now, what needs author follow-up, and what's blocked — with a score breakdown that shows exactly why. No GitHub App. No hosted service. No AI tokens.

**[Try the browser demo →](https://jackspiece.github.io/maintainer-radar/)**

---

## Quick start

The fastest path is the GitHub Action. Add it to any workflow:

```yaml
- uses: actions/setup-python@v6
  with:
    python-version: "3.12"
- uses: JackSpiece/maintainer-radar@v0.21.0
  id: radar
  env:
    GH_TOKEN: ${{ github.token }}
  with:
    repository: ${{ github.repository }}
    format: markdown
```

Or scaffold a full scheduled workflow in one command:

```bash
maintainer-radar init-repo --profile balanced
```

Or just run it from your terminal right now:

```bash
pip install maintainer-radar
maintainer-radar recommend https://github.com/owner/repo/pulls
```

---

## What it does

It reads your PR queue through the GitHub CLI (or offline JSON) and tells you:

- Which PRs are ready to review
- Which need CI fixes or author follow-up before you touch them
- Which have unresolved maintainer feedback
- Roughly how long each one will take
- What fits in your next session, as a time-boxed plan

Every score has a visible breakdown. Nothing is a black box.

---

## Why

When there are 30+ open PRs — half of them AI-generated — and you have 45 minutes, you need something that already sorted the queue. Maintainer Radar does that. It runs read-only, requires no extra permissions, and never posts anything.

---

## Install

```bash
pip install maintainer-radar
```

Requires the [GitHub CLI](https://cli.github.com/) for live scans. Run `gh auth login` once.

For SHA-pinned installs:

```bash
maintainer-radar init-action --action-ref JackSpiece/maintainer-radar@<commit-sha>
```

---

## Common commands

```bash
# Queue brief for a repo
maintainer-radar repo owner/repo

# Deeper scan with full PR detail
maintainer-radar repo owner/repo --hydrate --sort action

# 30-minute review plan
maintainer-radar repo owner/repo --hydrate --sort action --review-plan-minutes 30

# Single PR breakdown
maintainer-radar pr owner/repo 123

# Just the workflow recommendation
maintainer-radar recommend owner/repo

# Offline from a JSON export
maintainer-radar from-json queue.json

# Filter to the most reviewable PRs
maintainer-radar repo owner/repo --action review-now --min-score 80 --top 10
```

Full reference: `maintainer-radar --help`

---

## GitHub Action outputs

The action exposes these as step outputs for notifications, dashboards, or follow-up steps:

`review-now` · `ci-blocked` · `merge-conflicts` · `branch-behind` · `maintainer-blocked` · `attention-level` · `workflow-mode` · `workflow-recommendation` · `next-session-brief`

See [docs/github-action.md](docs/github-action.md) for the full reference.

---

## Example output

```
| PR | Action | Score | Signals |
|---|---|---|---|
| #42 Fix parser cache race | review now | 100 | CI passed, test plan present, tests changed |
| #43 Add universal plugin system | ask for CI fix | 0 | very large diff, CI failing, no test plan |
```

Review plans, JSON, CSV, and standalone HTML are also available.

---

## Docs

- [Quickstart](docs/quickstart.md)
- [GitHub Action](docs/github-action.md)
- [Review plans](docs/review-plan.md)
- [Attention workflows](docs/attention-workflows.md)
- [Scoring heuristics](docs/heuristics.md)
- [Configuration](docs/configuration.md)
- [Privacy & permissions](docs/privacy-permissions.md)
- [GitLab / Forgejo / Gitea](docs/forgejo-gitea-json.md)

---

## Contributing

Issues and PRs are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
