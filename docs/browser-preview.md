# Browser Preview

The public demo includes a no-install browser preview for public GitHub
repositories:

https://jackspiece.github.io/maintainer-radar/

Enter a repository as `owner/repo`. The page reads public GitHub API data and
renders a lightweight triage report in your browser.

You can also share a prefilled scan link:

```text
https://jackspiece.github.io/maintainer-radar/?repo=python/cpython
```

After a scan, the page updates the address bar and enables **Copy Link** for the
current repository.

It also enables **Copy Markdown**, which copies a paste-ready queue brief with
the same action, next-step, score, risk-impact, and signal columns shown in the
preview.

Turn on **Group by action** to split the preview and copied Markdown into
review-now, CI, author follow-up, and triage sections.

The **Copy Workflow** button copies a ready scheduled GitHub Action workflow that
uses the latest Maintainer Radar release and uploads the generated report as an
artifact. The copied workflow uses action-grouped Markdown output.

## What It Fetches

For the recent open pull requests it scans, the preview fetches:

- pull request list
- pull request detail
- changed files
- public check runs for the PR head commit, when GitHub exposes them

This lets the preview detect basic queue signals like:

- draft PRs
- large diffs
- stale PRs
- missing test-plan language
- code changes without test files
- generated or lockfile changes
- public CI passed, failing, pending, or absent

## What It Does Not Do

- It does not ask for a GitHub token.
- It does not access private repositories.
- It does not post comments or mutate repositories.
- It does not send repository data to a Maintainer Radar server.
- It does not store scanned repository data.

The only network calls are from your browser to the public GitHub API and to the
static GitHub Pages assets.

## Limits

The browser preview is intentionally lightweight. GitHub can rate-limit
unauthenticated API requests, and some check-run data may be unavailable.

For deeper scans, use the CLI:

```bash
python -m pip install "git+https://github.com/JackSpiece/maintainer-radar.git"
maintainer-radar repo owner/repo --hydrate --sort action --top 10
```

The CLI can use your authenticated `gh` session, inspect richer PR context, and
emit Markdown, JSON, CSV, or standalone HTML reports.

## Feedback

If the preview scores a public PR incorrectly, open a focused report:

https://github.com/JackSpiece/maintainer-radar/issues/new/choose

Useful reports include the public PR link, the action you expected, and the
signal that felt missing or too strong.
