# HTML Output

Maintainer Radar can generate a standalone static HTML report. This is useful
when a maintainer wants to share a queue snapshot with a team without running a
hosted dashboard.

## Usage

```bash
maintainer-radar repo owner/repo --hydrate --sort action --format html > review-queue.html
maintainer-radar from-json examples/sample-prs.json --format html > review-queue.html
```

The report includes:

- summary metrics
- a triage table
- links back to pull requests when the URL is safe
- action labels
- escaped titles, signals, flags, and comment text

## Summary Output

```bash
maintainer-radar repo owner/repo --summary-only --format html > summary.html
```

Summary-only HTML omits the table and keeps only the metric view.

## Design

The HTML output is a single file with embedded CSS. It does not load JavaScript,
fonts, external assets, or analytics. It is meant to be attached to an internal
handoff, uploaded as a CI artifact, or opened locally in a browser.
