# Browser Preview

The public demo includes a no-install browser preview for public GitHub
repositories:

https://jackspiece.github.io/maintainer-radar/

Enter a repository as `owner/repo`. The page reads public GitHub API data and
renders a lightweight triage report in your browser.

You can also share a prefilled scan link with a review-plan budget:

```text
https://jackspiece.github.io/maintainer-radar/?repo=python/cpython&plan=30
```

You can open the same scan with action grouping already enabled:

```text
https://jackspiece.github.io/maintainer-radar/?repo=python/cpython&group=action&plan=30
```

After a scan, the page updates the address bar and enables **Copy Link** for the
current repository, grouped view, and plan minutes.

Use **Copy Badge** to copy a static Markdown badge that links to the current
browser preview. It is intended for a README, maintainer handoff issue, or
project docs page.

Use **Copy CLI** to copy the matching local command for the current repository.
When **Group by action** is on, the copied command includes
`--group-by action`.

It also enables **Copy Markdown**, which copies a paste-ready queue brief with
the same action, next-step, score, risk-impact, and signal columns shown in the
preview.

Use **Copy Plan** to copy a time-boxed review plan for the scanned PRs. Set the
plan minutes field first when you want something other than the default 30
minute plan. The plan also includes draft follow-up comments for PRs that need
author action. The current minutes value is preserved in copied demo links.

The preview also shows a draft follow-up panel for the same planned, deferred,
and watch-only entries. Use **Copy Draft** to copy one editable author ask at a
time, then review and post it manually if it still fits the PR.

Use **Copy JSON** to copy the same review plan as structured JSON with planned,
deferred, and watch-only PR arrays plus `draft_follow_up_comment` fields. It is
meant for dashboards, scripts, or handoff tooling that should not parse
Markdown.

The page also shows a compact review plan preview and draft follow-up panel
under the summary metrics so you can inspect the planned active time and author
asks before copying Markdown.

The summary metrics include PRs scanned, review-now count, follow-up count,
Maintainer blocked count, and average score.

The attention card above those metrics gives a one-line queue headline plus an
attention level, such as `blocked`, `follow-up`, `triage`, `review`, or `quiet`.
It mirrors the Action outputs so maintainers can decide whether a queue needs a
human notification before reading the full table.

The same card includes a workflow recommendation, such as `blocker-sweep` or
`review-sprint`, so a maintainer can decide what kind of review session to run
before reading individual rows.

Turn on **Group by action** to split the preview and copied Markdown into
review-now, CI, author follow-up, and triage sections.

The **Copy Workflow** button copies a ready scheduled GitHub Action workflow that
uses the latest Maintainer Radar release and uploads the generated review plan
as an artifact. The copied workflow uses the current plan minutes value.

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
- maintainer blocking labels such as waiting on author or blocked upstream
- merge conflicts, branch-behind state, and repository merge gates
- requested reviewers and teams
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
maintainer-radar repo owner/repo --hydrate --sort action --review-plan-minutes 30
```

The CLI can use your authenticated `gh` session, inspect richer PR context, and
emit Markdown, JSON, CSV, or standalone HTML reports.

## Feedback

If the preview scores a public PR incorrectly, open a focused report:

https://github.com/JackSpiece/maintainer-radar/issues/new/choose

Useful reports include the public PR link, the action you expected, and the
signal that felt missing or too strong.
