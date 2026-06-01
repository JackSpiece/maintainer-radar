# JSON Output

Maintainer Radar supports JSON output for scripts and dashboards.

## Full Queue Output

```bash
maintainer-radar repo owner/repo --format json
```

The command returns a list of analyzed pull requests.

Important fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `number` | integer | Pull request number |
| `title` | string | Pull request title |
| `url` | string | Pull request URL |
| `author` | string | Author login |
| `risk` | integer | Risk score from 0 to 100 |
| `reviewability` | integer | Reviewability score from 0 to 100 |
| `action` | string | Recommended maintainer action |
| `signals` | array | Positive review signals |
| `flags` | array | Risk flags |
| `checks` | object | Check summary |
| `files` | object | File shape summary |
| `stale_days` | integer or null | Days since last update |

## Summary Output

```bash
maintainer-radar repo owner/repo --summary-only --format json
```

Example:

```json
{
  "total": 30,
  "review_now": 8,
  "author_follow_up": 6,
  "ci_blocked": 2,
  "ci_pending": 3,
  "large_or_triage": 4,
  "stale": 9,
  "average_score": 72
}
```

Summary fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `total` | integer | Number of analyzed PRs after filters |
| `review_now` | integer | PRs recommended for immediate review |
| `author_follow_up` | integer | PRs needing author response |
| `ci_blocked` | integer | PRs with failing CI |
| `ci_pending` | integer | PRs waiting for CI |
| `large_or_triage` | integer | PRs that are too large or need triage |
| `stale` | integer | PRs quiet for 7+ days |
| `average_score` | integer | Average reviewability score |

## Script Example

```bash
score=$(maintainer-radar repo owner/repo --summary-only --format json |
  python -c 'import json,sys; print(json.load(sys.stdin)["average_score"])')

echo "Average reviewability: $score"
```

