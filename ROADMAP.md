# Roadmap

## 0.1

- Deterministic PR scoring
- Markdown report output
- Offline JSON mode
- GitHub CLI integration
- Unit tests and CI

## 0.2

- Better maintainer blocker detection
- Repository health summary
- `--since` and `--label` filters
- More real-world fixtures

## 0.3

- GitLab support from exported merge request JSON
- Forgejo and Gitea support
- Optional comment classifier plugin
- Maintainer handoff report for release weeks

## 0.6

- CSV export for maintainers who keep review queues in spreadsheets

## 0.7

- Deterministic queue sorting for different maintainer review sessions

## Design Rules

- No hidden network service.
- No required AI model.
- No token storage.
- Prefer transparent heuristics over opaque scores.
- Markdown output first.
