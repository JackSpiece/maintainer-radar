# GitHub Actions Integration

Maintainer Radar can run in CI and upload a Markdown triage report as an
artifact. This is useful for maintainers who want a daily queue snapshot without
installing another GitHub App.

## Scheduled Queue Report

```yaml
name: Maintainer Radar

on:
  workflow_dispatch:
  schedule:
    - cron: "0 8 * * 1-5"

permissions:
  contents: read
  pull-requests: read

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - name: Install Maintainer Radar
        run: python -m pip install git+https://github.com/JackSpiece/maintainer-radar.git
      - name: Build PR report
        env:
          GH_TOKEN: ${{ github.token }}
        run: maintainer-radar repo ${{ github.repository }} --limit 50 > maintainer-radar.md
      - uses: actions/upload-artifact@v4
        with:
          name: maintainer-radar
          path: maintainer-radar.md
```

## Summary-Only Report

For a compact status artifact:

```yaml
- name: Build PR summary
  env:
    GH_TOKEN: ${{ github.token }}
  run: maintainer-radar repo ${{ github.repository }} --limit 100 --summary-only > maintainer-radar-summary.md
```

## Notes

- The tool uses `gh` for live GitHub data.
- GitHub-hosted runners include `gh` by default.
- The report is advisory. It does not approve, reject, or modify pull requests.
- Keep permissions read-only unless your own workflow adds posting behavior.

