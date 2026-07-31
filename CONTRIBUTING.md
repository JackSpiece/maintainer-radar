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

## Tests, Lint, and Types

CI runs the unit test suite on Python 3.10, 3.11, and 3.12, plus `ruff` for
linting and `mypy` for advisory type checking. Run them locally before opening
a PR:

```bash
make test
make lint       # requires: python -m pip install "ruff==0.16.0"
make typecheck  # requires: python -m pip install "mypy==2.3.0"
```

## Good Contributions

- new scoring fixtures from real maintainer workflows
- clearer Markdown reports
- more accurate risk flags
- support for exported JSON from other forges
- docs that help maintainers adopt the tool

If you try Maintainer Radar on a public repository, the maintainer feedback
issue template is the best place to share what queue routing felt useful or
wrong.

## Pull Request Checklist

- Add or update tests for scoring changes.
- Keep output deterministic.
- Do not add a network service or persistent token storage.
- Explain any new heuristic in plain language.
- Keep the browser demo scoring (docs/assets/demo.js) in sync when changing
  Python scoring heuristics, or call out the divergence in the PR.

## Release Process

1. Bump `__version__` in `src/maintainer_radar/__init__.py` (the package
   version is single-sourced from there).
2. Add a `CHANGELOG.md` entry and update the pinned action tag in `README.md`
   and `examples/github-actions/`.
3. Merge to `main`, then create a `vX.Y.Z` tag and a GitHub release.
4. Publishing the release triggers the `Release` workflow, which builds the
   package and publishes it to PyPI via trusted publishing (the `pypi`
   environment must be configured with a PyPI trusted publisher).
