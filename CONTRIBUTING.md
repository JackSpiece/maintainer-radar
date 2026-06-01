# Contributing

Thanks for helping improve Maintainer Radar.

The project favors small, reviewable PRs with clear examples.

## Local Setup

```bash
python -m pip install -e .
python -m unittest discover -s tests
```

Without installing:

```bash
PYTHONPATH=src python -m unittest discover -s tests
PYTHONPATH=src python -m maintainer_radar from-json examples/sample-prs.json
```

## Good Contributions

- new scoring fixtures from real maintainer workflows
- clearer Markdown reports
- more accurate risk flags
- support for exported JSON from other forges
- docs that help maintainers adopt the tool

## Pull Request Checklist

- Add or update tests for scoring changes.
- Keep output deterministic.
- Do not add a network service or persistent token storage.
- Explain any new heuristic in plain language.
