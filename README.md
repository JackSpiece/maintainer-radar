# Maintainer Radar

[![CI](https://github.com/JackSpiece/maintainer-radar/actions/workflows/ci.yml/badge.svg)](https://github.com/JackSpiece/maintainer-radar/actions/workflows/ci.yml)

GitHub Action and local CLI for read-only pull request triage reports.

Maintainer Radar scans a pull request queue and produces a short brief: what is ready to review, what needs author follow-up, what is blocked, and what fits into the next review session. Every score includes a visible breakdown. It does not post, label, approve, reject, or merge anything.

[Try the browser demo](https://jackspiece.github.io/maintainer-radar/)

## Quick Start

The fastest path is the GitHub Action. The latest published release is `v0.20.0`:

```yaml
- uses: actions/setup-python@v6
  with:
    python-version: "3.12"
- uses: JackSpiece/maintainer-radar@v0.20.0
  id: radar
  env:
    GH_TOKEN: ${{ github.token }}
  with:
    repository: ${{ github.repository }}
    format: markdown
```

For a local run, install the published source tag from GitHub:

```bash
python -m pip install "git+https://github.com/JackSpiece/maintainer-radar.git@v0.20.0"
maintainer-radar recommend https://github.com/owner/repo/pulls
```

Requires the [GitHub CLI](https://cli.github.com/) for authenticated live scans. Run `gh auth login` once.

To scaffold a config and scheduled workflow:

```bash
maintainer-radar init-repo --profile balanced
```

For stricter queue thresholds:

```bash
maintainer-radar init-config --profile strict --path .maintainer-radar.json
```

## What It Does

It reads pull request metadata through the GitHub CLI, the GitHub Action token, or offline JSON, then reports:

- PRs that appear ready for review
- CI failures, merge conflicts, and author follow-up
- unresolved maintainer feedback
- transparent reviewability and risk signals
- a time-boxed review plan for the next session
- editable draft follow-ups that a maintainer can review before posting

Reports are available as Markdown, JSON, CSV, and standalone HTML.

## Before-review workflow

Use AI reviewers to inspect code. Use Maintainer Radar before that to decide which pull requests deserve maintainer attention now.

The `recommend` command turns a queue scan into one decision: the current attention level, a suggested workflow, the reason, a next-session brief, and the next command to run. This is a before-review workflow, not an automated reviewer.

```bash
maintainer-radar repo owner/repo --hydrate --sort action --review-plan-minutes 30
```

## Common Commands

```bash
# Queue brief for a repository
maintainer-radar repo owner/repo

# Deeper scan with pull request details
maintainer-radar repo owner/repo --hydrate --sort action

# Single pull request breakdown
maintainer-radar pr owner/repo 123

# Offline analysis
maintainer-radar from-json queue.json

# Short review-ready list
maintainer-radar repo owner/repo --action review-now --min-score 80 --top 10
```

Run `maintainer-radar --help` for the complete reference.

## GitHub Action Outputs

The action exposes outputs for notifications, dashboards, and handoffs, including:

`review-now`, `ci-blocked`, `merge-conflicts`, `branch-behind`, `maintainer-blocked`, `attention-level`, `workflow-mode`, `workflow-recommendation`, and `next-session-brief`.

See [GitHub Action usage](docs/github-action.md) and [attention workflows](docs/attention-workflows.md).

## Documentation

- [Two minute quickstart](docs/quickstart.md)
- [Adoption guide](docs/adoption.md)
- [GitHub Action](docs/github-action.md)
- [Review plans](docs/review-plan.md)
- [Scoring heuristics](docs/heuristics.md)
- [Configuration](docs/configuration.md)
- [Privacy and permissions](docs/privacy-permissions.md)
- [Project positioning](docs/positioning.md)
- [GitLab, Forgejo, and Gitea JSON](docs/forgejo-gitea-json.md)

## Contributing

Issues and focused pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
