# CSV Output

Maintainer Radar supports CSV output for maintainers who track review queues in
spreadsheets or lightweight project trackers.

## Full Queue Output

```bash
maintainer-radar repo owner/repo --format csv
maintainer-radar from-json examples/sample-prs.json --format csv
```

The command returns one row per analyzed pull request.

Columns:

| Column | Meaning |
| --- | --- |
| `number` | Pull request number |
| `title` | Pull request title |
| `author` | Author login |
| `action` | Recommended maintainer action |
| `next_step` | Suggested next maintainer move |
| `reviewability` | Reviewability score from 0 to 100 |
| `risk` | Risk score from 0 to 100 |
| `stale_days` | Days since last update |
| `changed_files` | Number of changed files |
| `additions` | Added lines |
| `deletions` | Removed lines |
| `labels` | Semicolon-separated labels |
| `signals` | Semicolon-separated positive review signals |
| `flags` | Semicolon-separated risk flags |
| `score_breakdown` | Semicolon-separated risk impact explanations |
| `url` | Pull request URL |

## Summary Output

```bash
maintainer-radar repo owner/repo --summary-only --format csv
```

Summary output returns one row with the same fields as JSON summary output:

- `total`
- `review_now`
- `author_follow_up`
- `ci_blocked`
- `ci_pending`
- `maintainer_blocked`
- `large_or_triage`
- `stale`
- `average_score`
