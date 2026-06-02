# Maintainer Radar

[![CI](https://github.com/JackSpiece/maintainer-radar/actions/workflows/ci.yml/badge.svg)](https://github.com/JackSpiece/maintainer-radar/actions/workflows/ci.yml)

GitHub Action and local CLI for read-only pull request triage reports in the AI
contribution era.

Demo: <https://jackspiece.github.io/maintainer-radar/> includes a no-install
browser preview for public repositories.

The demo shows a review plan and copyable draft follow-ups before you install
anything. It also shows a next-session digest, so a maintainer can see what
fits in the next 60 minutes before opening a report artifact.

Example scan: <https://jackspiece.github.io/maintainer-radar/?repo=python/cpython>

First local recommendation:

```bash
maintainer-radar recommend https://github.com/owner/repo/pulls
```

Browser preview details: [docs/browser-preview.md](docs/browser-preview.md)

Two minute quickstart: [docs/quickstart.md](docs/quickstart.md)

Adoption guide: [docs/adoption.md](docs/adoption.md)

GitHub Action usage: [docs/github-action.md](docs/github-action.md)

Review plan guide: [docs/review-plan.md](docs/review-plan.md)

Attention workflows: [docs/attention-workflows.md](docs/attention-workflows.md)

Privacy and permissions: [docs/privacy-permissions.md](docs/privacy-permissions.md)

![Maintainer Radar terminal preview](docs/assets/terminal-preview.svg)

Maintainer Radar turns GitHub pull request metadata into a short, deterministic
review brief: which PRs are ready to review, which ones need author follow-up,
which ones are blocked by CI, and which ones are too risky to merge without more
evidence. It can also turn the queue into a time-boxed review plan for the next
maintainer session, with a default 60-minute session brief in every summary.

Use AI reviewers to inspect code. Use Maintainer Radar before that to decide
which pull requests deserve maintainer attention first.

It is not a review bot and it does not require a GitHub App. It runs from your
terminal, uses the GitHub CLI when live data is needed, and can also analyze JSON
fixtures offline.

## Why This Exists

Maintainers are getting more drive-by and AI-assisted PRs. The hard part is not
only reading code. It is deciding where review time is worth spending.

Maintainer Radar focuses on that first 60 seconds:

- Is the PR small enough to review?
- Did CI pass?
- Is the branch mergeable or blocked by conflicts?
- Did the author include a test plan?
- Are tests changed when code changed?
- Did a maintainer already say "not working" or request changes?
- Is this stale enough that it needs a fresh author response?
- Is this a review-now PR or a follow-up-needed PR?

## What Makes It Different

Most tools in this area are AI reviewers, GitHub Apps, bounty boards, or generic
dashboards. Maintainer Radar is different on purpose:

- **Before-review workflow:** it routes attention before anyone spends time on
  code review.
- **Maintainer-first:** it prioritizes review time, not contributor output.
- **Local-first:** no SaaS, no webhook, no hosted database.
- **Low-permission:** live GitHub reports need read-only repository and pull
  request access.
- **Deterministic:** every score comes with a visible heuristic breakdown.
- **AI-era aware:** it catches the common failure shape of large PRs with weak
  test evidence and unresolved maintainer feedback.
- **Handoff-ready:** review plans include editable draft follow-ups for PRs that
  need author action, while staying read-only.
- **Session-aware:** summaries say what fits in the next 60 maintainer minutes,
  how many items are quick unblocks, and what should stay on watch.
- **Markdown-native:** output can be pasted into issues, PR comments, worklogs,
  release notes, or maintainer handoff docs.

For a category comparison, see [docs/positioning.md](docs/positioning.md).

## Quick Start

For most maintainers, the fastest path is the reusable GitHub Action:

```yaml
- uses: actions/setup-python@v6
  with:
    python-version: "3.12"
- uses: JackSpiece/maintainer-radar@v0.19.0
  id: radar
  env:
    GH_TOKEN: ${{ github.token }}
  with:
    repository: ${{ github.repository }}
    format: markdown
```

Or generate a complete scheduled workflow:

```bash
maintainer-radar init-action --path .github/workflows/maintainer-radar.yml
```

This writes a workflow that scans the current repository's PR queue and uploads
a Markdown triage artifact. The report also appears in the GitHub Actions run
summary, so maintainers do not have to download the artifact just to read the
queue. The Action also exposes summary outputs such as `review-now`,
`ci-blocked`, `merge-conflicts`, `branch-behind`, `maintainer-blocked`, and
`attention-level`, plus `workflow-mode` and `workflow-recommendation` for later
handoff or notification steps. The `next-session-brief` output gives a concise
60-minute maintainer digest for notifications or dashboards. It refuses to
overwrite an existing file unless you pass `--force`.

If your project uses custom thresholds, include them in the generated workflow:

```bash
maintainer-radar init-config --profile strict --path .maintainer-radar.json
maintainer-radar init-action --config .maintainer-radar.json --path .github/workflows/maintainer-radar.yml
```

For a smaller scheduled report, generate a focused review-ready workflow:

```bash
maintainer-radar init-action --action review-now --min-score 80 --top 10 --group-by action --path .github/workflows/review-ready.yml
```

For local CLI use, install directly from GitHub:

```bash
python -m pip install "git+https://github.com/JackSpiece/maintainer-radar.git"
maintainer-radar recommend https://github.com/owner/repo/pulls
maintainer-radar repo owner/repo --hydrate --sort action --top 10
```

Live CLI scans require the GitHub CLI:

```bash
gh auth login
```

For local development from a checkout:

```bash
python -m pip install -e .
python -m unittest discover -s tests
```

Or run without installing:

```bash
PYTHONPATH=src python -m maintainer_radar --help
PYTHONPATH=src python -m unittest discover -s tests
```

## Offline Example

![Maintainer Radar quickstart sequence](docs/assets/quickstart-sequence.svg)

Try the offline sample data first:

```bash
PYTHONPATH=src python -m maintainer_radar from-json examples/sample-prs.json
```

## Usage

Analyze open PRs in a repository:

```bash
maintainer-radar repo owner/repo --limit 20
```

Ask for the next maintainer workflow before opening the full report:

```bash
maintainer-radar recommend owner/repo
maintainer-radar recommend https://github.com/owner/repo/pulls --format json
```

Pasted GitHub repository URLs work too:

```bash
maintainer-radar repo https://github.com/owner/repo/pulls --limit 20
```

Fetch full PR detail for deeper live scoring:

```bash
maintainer-radar repo owner/repo --limit 20 --hydrate
```

Filter noisy queues:

```bash
maintainer-radar repo owner/repo --label bug --stale-days 14
maintainer-radar repo owner/repo --author contributor --updated-since 2026-06-01
```

Get a compact queue snapshot:

```bash
maintainer-radar repo owner/repo --summary-only
```

Focus a report on the most reviewable PRs:

```bash
maintainer-radar repo owner/repo --action review-now --min-score 80
maintainer-radar from-json queue.json --max-risk 25
```

Sort a queue for the review session:

```bash
maintainer-radar repo owner/repo --sort action
maintainer-radar from-json queue.json --sort risk
```

Turn the queue into a time-boxed maintainer session:

```bash
maintainer-radar repo owner/repo --hydrate --sort action --review-plan-minutes 30
```

Group Markdown or HTML reports by action:

```bash
maintainer-radar repo owner/repo --sort action --group-by action
```

Keep only the first results after filtering and sorting:

```bash
maintainer-radar repo owner/repo --hydrate --sort risk --top 10
```

Use project-specific thresholds:

```bash
maintainer-radar init-config --profile large-repo --path .maintainer-radar.json
maintainer-radar repo owner/repo --config .maintainer-radar.json
```

Analyze one PR in detail:

```bash
maintainer-radar pr owner/repo 123
```

Or paste the PR URL directly:

```bash
maintainer-radar pr https://github.com/owner/repo/pull/123
```

Draft a maintainer follow-up comment without posting it:

```bash
maintainer-radar pr owner/repo 123 --comment-template
```

Track one contributor's open PRs:

```bash
maintainer-radar author JackSpiece --state open --limit 50
```

Analyze offline JSON:

```bash
maintainer-radar from-json examples/sample-prs.json
cat examples/sample-prs.json | maintainer-radar from-json -
maintainer-radar from-json gitlab-merge-requests.json --source gitlab
maintainer-radar from-json forgejo-pull-requests.json --source forgejo
maintainer-radar from-json gitea-pull-requests.json --source gitea
```

JSON output is available for automation:

```bash
maintainer-radar repo owner/repo --format json
```

CSV output is available for spreadsheets:

```bash
maintainer-radar repo owner/repo --format csv
```

HTML output is available for shareable local reports:

```bash
maintainer-radar repo owner/repo --hydrate --sort action --format html > review-queue.html
```

Bootstrap a repository workflow without copying YAML by hand:

```bash
maintainer-radar init-action --report-format html --path .github/workflows/maintainer-radar.yml
```

## Example Output

```markdown
## Maintainer Radar Report

| PR | Action | Next Step | Score | Risk Impact | Signals |
| --- | --- | --- | ---: | --- | --- |
| #42 Fix parser cache race | review now | Review now while the PR appears small, active, and low risk. | 100 | CI passed (-8 risk) | CI passed, test plan present, tests changed |
| #43 Add universal plugin system | ask for CI fix | Ask the author to get failing checks green before deeper review. | 0 | very large diff (+30 risk); CI failing (+30 risk) | very large diff, CI failing, changes requested |
```

## Signals

Maintainer Radar currently checks:

- draft PRs
- review decision
- CI state
- stale update windows
- additions, deletions, and changed file count
- body test-plan language
- code changes without nearby tests
- generated file paths and lockfiles
- maintainer comments that look like blockers
- failing or pending checks
- draft follow-up comments inside review plans, without posting anything
- per-PR score breakdowns that show each risk adjustment
- per-PR next steps that translate triage into a maintainer move
- draft follow-up comments for one PR, without posting automatically

The goal is not to replace review. The goal is to route attention.

## Project Status

This is an early public release. The core CLI, scoring engine, Markdown renderer,
offline JSON mode, hydrated GitHub scans, and tests are present. Next work is
focused on richer maintainer blocker detection and examples from real OSS review
workflows.

See [ROADMAP.md](ROADMAP.md).

For copy-paste maintainer workflows, see
[docs/handoff-examples.md](docs/handoff-examples.md).

For scheduled queue reports, see [docs/github-actions.md](docs/github-actions.md).

For copy-paste workflows and sample data, see [examples/README.md](examples/README.md).

For generated sample reports, see [examples/output](examples/output).

For scoring details, see [docs/heuristics.md](docs/heuristics.md).

For automation output, see [docs/json-output.md](docs/json-output.md).

For spreadsheet output, see [docs/csv-output.md](docs/csv-output.md).

For shareable static reports, see [docs/html-output.md](docs/html-output.md).

For queue ordering, see [docs/sorting.md](docs/sorting.md).

For compact queue snapshots, see [docs/focused-reports.md](docs/focused-reports.md).

For stable sample output, see [docs/reproducible-reports.md](docs/reproducible-reports.md).

For deeper live GitHub reports, see [docs/hydrated-scans.md](docs/hydrated-scans.md).

For GitLab exports, see [docs/gitlab-json.md](docs/gitlab-json.md).

For Forgejo and Gitea exports, see
[docs/forgejo-gitea-json.md](docs/forgejo-gitea-json.md).

For project-specific thresholds, see [docs/configuration.md](docs/configuration.md).

## Contributing

Issues and PRs are welcome, especially:

- better heuristics for maintainer feedback
- fixtures from real open-source review patterns
- integrations with `gh`, GitLab, Forgejo, or static JSON exports
- examples that help maintainers adopt the tool without workflow churn

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
