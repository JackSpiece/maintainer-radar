# Heuristics

Maintainer Radar uses deterministic rules. The score is not truth. It is a
routing hint for maintainer attention.

Every analyzed PR includes a `score_breakdown` list. Each item names the
heuristic, shows its `risk_delta`, and marks it as a `signal` or `flag`. Positive
values raise risk. Negative values lower risk. The final risk score is clamped to
the 0 to 100 range, then reviewability is calculated as `100 - risk`.

Each analyzed PR also includes `next_step`, a deterministic sentence that turns
the selected action and strongest flags into a concrete maintainer move.

Example:

```json
[
  { "label": "CI passed", "risk_delta": -8, "kind": "signal" },
  { "label": "code changed without tests", "risk_delta": 10, "kind": "flag" }
]
```

## Positive Signals

- CI passed
- PR is approved
- test plan language is present
- tests changed
- docs-only shape

## Risk Flags

- draft PR
- large or very large diff
- no visible checks
- CI failing or pending
- changes requested
- stale update window
- maintainer blocker language
- no test plan found for code changes
- code changed without tests
- generated or lockfile changes

## Maintainer Blocker Language

Blocker detection intentionally looks for plain maintainer feedback patterns:

- not working
- broken
- failing or failed
- changes requested
- please fix
- regression
- cannot merge
- missing tests

This is not sentiment analysis. The goal is to catch comments that usually mean
"do not spend full review time until the author follows up."

## Fixture Corpus

The test suite includes `tests/fixtures/blocker-prs.json` to keep blocker
detection concrete. Add new fixture cases when a real maintainer pattern should
be detected.
