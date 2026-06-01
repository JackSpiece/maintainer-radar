# Maintainer Workflows

Maintainer Radar works best as a queue-shaping tool. It does not decide whether
to merge a pull request. It helps decide what deserves attention first.

## Morning Queue

Start with a full queue snapshot:

```bash
maintainer-radar repo owner/repo --limit 50 --hydrate --sort action
```

Use this when the goal is to split the queue into review-now, CI-blocked,
author-follow-up, and triage work.

## Review-Ready Slice

Show only the most reviewable pull requests:

```bash
maintainer-radar repo owner/repo \
  --hydrate \
  --action review-now \
  --min-score 80 \
  --sort score \
  --top 10
```

This is the fastest path to finding small, green PRs with enough review
evidence.

## High-Risk Slice

Find the work most likely to waste review time:

```bash
maintainer-radar repo owner/repo \
  --hydrate \
  --sort risk \
  --top 10
```

Use this for queues with many failing, stale, large, or under-tested PRs.

## Release Freeze

During release week, focus on blockers and risky changes:

```bash
maintainer-radar repo owner/repo \
  --hydrate \
  --sort risk \
  --format html \
  > release-freeze.html
```

Look for failing CI, maintainer blocker language, very large diffs, stale PRs,
and code changes without tests.

## Contributor Follow-Up

For one PR:

```bash
maintainer-radar pr owner/repo 123
```

Draft a follow-up comment without posting it:

```bash
maintainer-radar pr owner/repo 123 --comment-template
```

The generated comment is a draft. Edit it before posting.

## CI Artifact

Use a scheduled workflow when maintainers want a daily report without installing
a GitHub App:

```bash
maintainer-radar repo owner/repo \
  --limit 50 \
  --hydrate \
  --sort action \
  --format html \
  > maintainer-radar.html
```

See [github-actions.md](github-actions.md) and
[../examples/github-actions](../examples/github-actions).

## Spreadsheet Export

For maintainers who track review queues outside GitHub:

```bash
maintainer-radar repo owner/repo \
  --hydrate \
  --sort action \
  --format csv \
  > maintainer-radar.csv
```

See [csv-output.md](csv-output.md).

## Offline Or Piped Data

Analyze saved JSON:

```bash
maintainer-radar from-json queue.json --sort risk --top 10
```

Analyze piped JSON:

```bash
cat queue.json | maintainer-radar from-json - --sort risk --top 10
```

Use `--source gitlab`, `--source forgejo`, or `--source gitea` for non-GitHub
export shapes.
