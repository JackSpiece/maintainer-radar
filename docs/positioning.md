# Positioning

Maintainer Radar is not another AI code reviewer.

The project sits before review. It answers a simpler question:

> Where should a maintainer spend review attention first?

Use AI reviewers to inspect code. Use Maintainer Radar before that to decide
which pull requests are worth maintainer attention now.

## Existing Categories

- AI code review bots comment on diffs.
- GitHub Apps automate policy checks.
- Bounty boards match contributors to paid tasks.
- GitHub Actions automate repository workflows.
- Generic dashboards show repository activity.

## Comparison

| Category | Main Job | Tradeoff | Maintainer Radar Difference |
| --- | --- | --- | --- |
| AI review bots | Comment on code changes | Can add review noise and needs model access | Routes queue attention before review |
| GitHub Apps | Enforce policy in a repo | Needs installation and permissions | Runs locally with read-only `gh` access |
| GitHub Actions | Run scheduled repository jobs | Usually needs custom scripts for triage | Ships a reusable read-only Action and workflow generator |
| Generic dashboards | Show repository activity | Often broad and hosted | Produces paste-ready maintainer reports and artifacts |
| Bounty boards | Match tasks to contributors | Optimized for contributor work | Optimized for maintainer review load |

## Maintainer Radar's Angle

Maintainer Radar generates a transparent triage brief from the CLI, a reusable
GitHub Action, or a no-install browser preview:

- review now
- wait for CI
- ask for CI fix
- needs author follow-up
- request smaller PR
- needs triage

Each PR includes a score breakdown and a next step, so the report explains both
why a PR was routed and what a maintainer should do next.

This is intentionally small. It makes the review queue easier to scan without a
bot account, webhook, hosted database, or SaaS subscription.

## What It Refuses To Do

- It does not approve, reject, merge, label, or comment on pull requests.
- It does not claim to understand code better than a maintainer.
- It does not require a model key or hosted service to produce a queue brief.

## Why Maintainers Might Care

AI-assisted code contributions create a new review burden. Some PRs are useful.
Some are large, under-tested, stale, or already known not to work.

Maintainer Radar helps sort that queue without judging the author.
