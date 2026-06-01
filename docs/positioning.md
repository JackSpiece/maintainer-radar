# Positioning

Maintainer Radar is not another AI code reviewer.

The project sits before review. It answers a simpler question:

> Where should a maintainer spend review attention first?

## Existing Categories

- AI code review bots comment on diffs.
- GitHub Apps automate policy checks.
- Bounty boards match contributors to paid tasks.
- Generic dashboards show repository activity.

## Maintainer Radar's Angle

Maintainer Radar generates a local, transparent triage brief:

- review now
- wait for CI
- ask for CI fix
- needs author follow-up
- request smaller PR
- needs triage

This is intentionally small. It makes the review queue easier to scan without
adding another bot account, webhook, or SaaS subscription.

## Why Maintainers Might Care

AI-assisted code contributions create a new review burden. Some PRs are useful.
Some are large, under-tested, stale, or already known not to work.

Maintainer Radar helps sort that queue without judging the author.

