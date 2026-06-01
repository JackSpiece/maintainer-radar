# Queue Sorting

Maintainer Radar keeps input order by default. Add `--sort` when a review
session needs a specific queue shape.

## Usage

```bash
maintainer-radar repo owner/repo --sort action
maintainer-radar repo owner/repo --sort score
maintainer-radar from-json examples/sample-prs.json --sort risk
```

Supported sorts:

| Sort | Behavior |
| --- | --- |
| `input` | Preserve the source order. This is the default. |
| `action` | Put reviewable work first, followed by CI, author follow-up, and triage work. |
| `score` | Highest reviewability first. |
| `risk` | Highest risk first. |
| `stale` | Oldest quiet PRs first. |
| `number` | Lowest PR number first. |

Sorting runs after filters such as `--action`, `--min-score`, and `--max-risk`.
Use `--top N` to keep only the first N items after sorting.
