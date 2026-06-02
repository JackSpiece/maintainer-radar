# Privacy and Permissions

Maintainer Radar is designed to make pull request queues easier to scan without
giving another service control of the repository.

## What It Reads

For live GitHub scans, Maintainer Radar reads pull request metadata through the
GitHub CLI or the GitHub Actions token:

- pull request title, author, labels, body, update time, and URL
- review decision and requested reviewers
- check run status and conclusions
- changed file names and diff size totals
- merge readiness fields such as conflicts, branch-behind state, and merge gates
- issue comments and review comments used to detect maintainer blocker language

It does not read repository secrets. It does not clone private source code unless
your own workflow checks out the repository for another step.

## Where Data Goes

The CLI writes output to your terminal or to the file path you choose. The
GitHub Action writes a report artifact and, by default, a compact run summary.

Maintainer Radar does not send queue data to a hosted service, analytics
endpoint, webhook, model provider, or external database.

## GitHub Action Permissions

Use the smallest permissions needed for a queue report:

```yaml
permissions:
  contents: read
  pull-requests: read
```

The Action uses the workflow token you pass as `GH_TOKEN`. It does not need a
personal access token for normal repository scans.

{% raw %}
```yaml
env:
  GH_TOKEN: ${{ github.token }}
```
{% endraw %}

## Browser Preview

The browser preview reads public repository pull request data from GitHub's
public API. It does not ask for a token, and it does not post comments or write
to the repository.

Because the browser preview is unauthenticated, it can hit public API rate
limits. The GitHub Action and CLI are better for regular maintainer workflows.

## What It Refuses To Do

Maintainer Radar does not:

- approve or reject pull requests
- merge pull requests
- label issues or pull requests
- post comments
- assign reviewers
- train on repository data

Draft follow-up comments are written into reports so a maintainer can copy,
edit, and decide what to post.

## Private Repositories

For private repositories, keep the report artifact inside the repository's own
GitHub Actions run unless your team has a separate sharing policy. If a workflow
uploads the report elsewhere, that is behavior added by the workflow, not by
Maintainer Radar.

