# Review Plans

Review plans turn a pull request queue into a time-boxed maintainer session.

Use this when the question is not "what is in the queue?" but "what should I do
with the next 30 minutes?"

```bash
maintainer-radar repo owner/repo --hydrate --sort action --review-plan-minutes 30
```

The plan is Markdown so it can go directly into a terminal, GitHub Actions run
summary, issue, or maintainer handoff note.

## What The Plan Includes

- the time budget
- planned PRs that fit the budget
- estimated active maintainer time per PR
- next-step guidance for each planned PR
- deferred PRs that did not fit the budget
- watch-only PRs that are waiting for CI or author action

## How Time Is Estimated

The estimate is deterministic and intentionally rough. It is meant to help
maintainers budget attention, not predict exact review time.

- small review-now PRs usually count as 12 minutes
- docs-only review-now PRs count lower
- medium or larger reviewable PRs count higher
- review-with-caution PRs add extra inspection time
- quick unblock actions such as CI fix, author follow-up, or smaller-PR request
  count as 5 minutes
- wait-for-CI and wait-for-author PRs are listed as watch-only items

## Scheduled Review Plan

Generate a workflow that puts the review plan in the run summary every weekday:

```bash
maintainer-radar init-action \
  --review-plan-minutes 30 \
  --group-by action \
  --path .github/workflows/maintainer-radar.yml
```

Or configure the reusable Action directly:

```yaml
with:
  repository: ${{ github.repository }}
  format: markdown
  sort: action
  review-plan-minutes: "30"
  hydrate: "true"
```

Review plans require Markdown output because they are designed for human
handoffs and Actions run summaries.

## Why This Is Different

AI reviewers inspect code after someone chooses a PR. Maintainer Radar helps
choose where maintainer attention should go before that review starts. It stays
read-only and does not approve, reject, merge, label, or comment on pull
requests.
