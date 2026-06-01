# Forgejo and Gitea Pull Request JSON

Maintainer Radar can analyze exported Forgejo or Gitea pull request JSON without
a hosted integration or stored token.

## Usage

```bash
maintainer-radar from-json forgejo-pull-requests.json --source forgejo
maintainer-radar from-json gitea-pull-requests.json --source gitea --summary-only
```

The command normalizes common Forgejo and Gitea pull request fields into the
same internal shape used for GitHub pull requests.

## Supported Fields

| Forgejo or Gitea field | Maintainer Radar use |
| --- | --- |
| `number`, `id`, or `index` | PR number |
| `title` | title |
| `html_url` or `url` | URL |
| `user.login` or `user.username` | author login |
| `body` | body and test-plan detection |
| `updated_at` | stale window |
| `draft` or title prefix `Draft:` / `WIP:` | draft detection |
| `labels` | label filters and output |
| `statuses[]`, `checks[]`, or `status` | CI status |
| `reviews[].state` | approved or changes-requested signal |
| `files[]` | changed file paths |
| `changed_files` | changed file count |
| `additions` and `deletions` | diff size |
| `files[].additions` and `files[].deletions` | diff size when PR stats are absent |
| `comments[]`, `issue_comments[]`, or `review_comments[]` | maintainer blocker language |

## Expected Shape

The file can be:

- one pull request object
- a list of pull request objects
- an object with `pull_requests`
- an object with `pulls`
- an object with `items`

Example:

```json
{
  "pull_requests": [
    {
      "number": 7,
      "title": "Fix webhook retry loop",
      "html_url": "https://forgejo.example.com/org/project/pulls/7",
      "user": { "login": "maya" },
      "body": "Validation: unit tests and local replay.",
      "updated_at": "2026-06-01T00:00:00Z",
      "labels": [{ "name": "bug" }],
      "reviews": [{ "state": "APPROVED" }],
      "statuses": [{ "context": "ci/test", "state": "success" }],
      "changed_files": 2,
      "files": [
        { "filename": "src/webhook/retry.py" },
        { "filename": "tests/test_webhook_retry.py" }
      ]
    }
  ]
}
```

## Exporting Data

Maintainer Radar does not call Forgejo or Gitea directly yet. Export PR JSON
through your own script, CI job, or API tooling, then pass the saved file to
`from-json --source forgejo` or `from-json --source gitea`.
