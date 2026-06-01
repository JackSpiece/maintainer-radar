# Maintainer Handoff Examples

Maintainer Radar reports are designed to be pasted into existing maintainer
workflows. These examples are generic and safe to adapt.

## Weekly Triage Note

```markdown
## PR Queue Triage

Generated with Maintainer Radar.

- Review now: 4
- Needs author follow-up: 3
- CI blocked or pending: 2
- Stale 7+ days: 6

Priority today:

1. Review small green PRs first.
2. Ask authors to update PRs with maintainer blocker language.
3. Leave large stale PRs for the weekly backlog pass.
```

## Release Freeze Checklist

```markdown
## Release Freeze PR Check

Do not merge before release unless a maintainer has direct context:

- PRs with failing CI
- Very large diffs
- PRs without a test plan
- PRs with unresolved "not working" maintainer comments
- Draft PRs
```

## Contributor Follow-Up Comment

```markdown
Thanks for the PR. Before this is ready for another review, could you please:

- Rebase on the latest main branch
- Add the missing test coverage
- Confirm the failing CI job locally or explain why it is unrelated
- Update the PR body with a short validation note

Once that is done, I can take another look.
```

## Maintainer Handoff

```markdown
## Handoff For Next Maintainer

The queue has been scanned with Maintainer Radar.

Good candidates for review:

- Small diff
- CI green
- Test plan present
- Tests changed

Needs follow-up:

- Maintainer blocker comment is unresolved
- CI failed
- Author has not responded for 14+ days
- Large diff should be split before review
```

## Local Commands

```bash
maintainer-radar repo owner/repo --limit 50 > triage.md
maintainer-radar repo owner/repo --stale-days 14 > stale-prs.md
maintainer-radar repo owner/repo --label bug > bug-prs.md
maintainer-radar pr owner/repo 123 > pr-123-brief.md
```

