# Focused Reports

Use `--top` when a report should stay short after filters and sorting.

## Examples

Show the 10 highest-risk PRs from an offline export:

```bash
maintainer-radar from-json queue.json --sort risk --top 10
```

Show the 5 most reviewable open PRs in a live repository:

```bash
maintainer-radar repo owner/repo --hydrate --sort score --top 5
```

Create a compact HTML artifact for the review session:

```bash
maintainer-radar repo owner/repo --hydrate --sort action --group-by action --top 15 --format html > review-queue.html
```

`--top` is applied after filtering and sorting. It does not change how many PRs
are fetched from GitHub. Use `--limit` for live fetch size and `--top` for final
report size.

`--group-by action` keeps Markdown and HTML reports easier to scan by separating
review-now, CI, author follow-up, and triage sections.
