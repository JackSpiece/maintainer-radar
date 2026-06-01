# GitLab Merge Request JSON

Maintainer Radar can analyze exported GitLab merge request JSON without a hosted
integration or stored token.

## Usage

```bash
maintainer-radar from-json gitlab-merge-requests.json --source gitlab
maintainer-radar from-json gitlab-merge-requests.json --source gitlab --summary-only
```

The command normalizes common GitLab merge request fields into the same internal
shape used for GitHub pull requests.

## Supported Fields

| GitLab field | Maintainer Radar use |
| --- | --- |
| `iid` | PR/MR number |
| `title` | title |
| `web_url` | URL |
| `author.username` | author login |
| `description` | body and test-plan detection |
| `updated_at` | stale window |
| `draft` or `work_in_progress` | draft detection |
| `labels` | label filters and output |
| `head_pipeline.status` or `pipeline.status` | CI status |
| `approved` or `approved_by` | approved signal |
| `blocking_discussions_resolved` | changes-requested signal when false |
| `changes_count` | changed file count |
| `changes[].new_path` | changed file paths |
| `changes[].diff` | additions and deletions when stats are absent |
| `stats.additions` and `stats.deletions` | diff size |
| `notes[]` or `discussions[].notes[]` | maintainer blocker language |

## Expected Shape

The file can be:

- one merge request object
- a list of merge request objects
- an object with `merge_requests`
- an object with `items`

Example:

```json
{
  "merge_requests": [
    {
      "iid": 12,
      "title": "Fix API cache invalidation",
      "web_url": "https://gitlab.example.com/group/project/-/merge_requests/12",
      "author": { "username": "alice" },
      "description": "Validation: unit tests and local repro.",
      "updated_at": "2026-06-01T00:00:00Z",
      "labels": ["bug", "backend"],
      "approved": true,
      "head_pipeline": { "status": "success" },
      "changes_count": "2",
      "changes": [
        { "new_path": "src/cache/api.py", "diff": "@@\n-old\n+new\n" },
        { "new_path": "tests/test_api_cache.py", "diff": "@@\n+test\n" }
      ]
    }
  ]
}
```

## Exporting Data

Maintainer Radar does not call GitLab directly yet. Export MR JSON through your
own script, CI job, or GitLab API tooling, then pass the saved file to
`from-json --source gitlab`.

