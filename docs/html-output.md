# HTML Output

Maintainer Radar can generate a standalone static HTML report. This is useful
when a maintainer wants to share a queue snapshot with a team without running a
hosted dashboard.

## Usage

```bash
maintainer-radar repo owner/repo --hydrate --sort action --format html > review-queue.html
maintainer-radar from-json examples/sample-prs.json --format html > review-queue.html
```

Use grouped sections for review-session artifacts:

```bash
maintainer-radar repo owner/repo --hydrate --sort action --group-by action --format html > review-queue.html
```

The report includes:

- summary metrics
- a triage table
- optional action-grouped sections
- review-plan draft follow-ups with Copy Draft buttons
- links back to pull requests when the URL is safe
- action labels
- next-step guidance for each pull request
- per-PR risk impact explanations
- escaped titles, signals, flags, and comment text

## Summary Output

```bash
maintainer-radar repo owner/repo --summary-only --format html > summary.html
```

Summary-only HTML omits the table and keeps only the metric view.

## Review Plans

When HTML output is combined with `--review-plan-minutes`, draft follow-up
comments are shown in the review plan artifact. Each draft has a **Copy Draft**
button, so a maintainer can copy the suggested author ask, edit it, and post it
manually.

## Design

The HTML output is a single file with embedded CSS and a small embedded copy
helper. It does not load external JavaScript, fonts, external assets, or
analytics. It is meant to be attached to an internal handoff, uploaded as a CI
artifact, or opened locally in a browser.
