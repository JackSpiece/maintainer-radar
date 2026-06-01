# Maintainer Workflows

## Morning Review Queue

```bash
maintainer-radar repo owner/repo --limit 30 > review-queue.md
```

Use the report to pick the first PRs to review.

## Release Freeze

Run the report on open PRs and look for:

- CI failing
- large diffs
- no test plan
- maintainer blocker language

These are poor release-week merge candidates unless the maintainer already has
strong context.

## Contributor Follow-Up

For one PR:

```bash
maintainer-radar pr owner/repo 123
```

Use the detail report to decide whether to ask for tests, wait for CI, or review
the current diff.

