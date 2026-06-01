from __future__ import annotations

import argparse
from datetime import timezone
import json
import sys
from typing import Any

from .config import load_config
from .github import GitHubCliError, list_repo_prs, search_author_prs, view_pr
from .normalize import normalize_items
from .render import (
    render_comment_template,
    render_comment_csv,
    render_csv,
    render_detail,
    render_markdown,
    render_summary_csv,
    render_summary_markdown,
    summarize_report,
)
from .scoring import analyze_pr, days_since, parse_github_datetime

ACTION_SLUGS = {
    "review-now": "review now",
    "review-with-caution": "review with caution",
    "wait-for-author": "wait for author",
    "wait-for-ci": "wait for CI",
    "ask-for-ci-fix": "ask for CI fix",
    "needs-author-follow-up": "needs author follow-up",
    "request-smaller-pr": "request smaller PR",
    "needs-triage": "needs triage",
}


def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _as_pr_list(data: Any, *, source: str = "github") -> list[dict[str, Any]]:
    return normalize_items(data, source=source)


def _label_names(pr: dict[str, Any]) -> set[str]:
    labels = pr.get("labels") or []
    names: set[str] = set()
    for label in labels:
        if isinstance(label, str):
            names.add(label.lower())
        elif isinstance(label, dict) and label.get("name"):
            names.add(str(label["name"]).lower())
    return names


def _author_login(pr: dict[str, Any]) -> str:
    author = pr.get("author")
    if isinstance(author, dict):
        return str(author.get("login") or "").lower()
    return str(author or "").lower()


def filter_prs(
    prs: list[dict[str, Any]],
    *,
    label: str | None = None,
    author: str | None = None,
    stale_days: int | None = None,
    updated_since: str | None = None,
) -> list[dict[str, Any]]:
    result = prs
    if label:
        wanted = label.lower()
        result = [pr for pr in result if wanted in _label_names(pr)]
    if author:
        wanted_author = author.lower()
        result = [pr for pr in result if _author_login(pr) == wanted_author]
    if stale_days is not None:
        stale_result: list[dict[str, Any]] = []
        for pr in result:
            quiet_days = days_since(pr.get("updatedAt"))
            if quiet_days is not None and quiet_days >= stale_days:
                stale_result.append(pr)
        result = stale_result
    if updated_since:
        since = parse_github_datetime(updated_since)
        if since is None:
            raise ValueError("--updated-since must be an ISO date, for example 2026-06-01")
        if since.tzinfo is None:
            since = since.replace(tzinfo=timezone.utc)
        updated_result: list[dict[str, Any]] = []
        for pr in result:
            updated_at = parse_github_datetime(pr.get("updatedAt"))
            if updated_at is None:
                continue
            if updated_at.tzinfo is None:
                updated_at = updated_at.replace(tzinfo=timezone.utc)
            if updated_at >= since:
                updated_result.append(pr)
        result = updated_result
    return result


def filter_analyses(
    analyses: list[dict[str, Any]],
    *,
    action: str | None = None,
    min_score: int | None = None,
    max_risk: int | None = None,
) -> list[dict[str, Any]]:
    result = analyses
    if action:
        wanted_action = ACTION_SLUGS[action]
        result = [item for item in result if item.get("action") == wanted_action]
    if min_score is not None:
        result = [item for item in result if int(item.get("reviewability") or 0) >= min_score]
    if max_risk is not None:
        result = [item for item in result if int(item.get("risk") or 0) <= max_risk]
    return result


def _emit(
    analyses: list[dict[str, Any]],
    fmt: str,
    *,
    detail: bool = False,
    summary_only: bool = False,
) -> None:
    if fmt == "json":
        if summary_only:
            print(json.dumps(summarize_report(analyses), indent=2))
        else:
            print(json.dumps(analyses[0] if detail and len(analyses) == 1 else analyses, indent=2))
        return
    if fmt == "csv":
        if summary_only:
            print(render_summary_csv(analyses), end="")
        else:
            print(render_csv(analyses), end="")
        return
    if summary_only:
        print(render_summary_markdown(analyses), end="")
        return
    if detail and len(analyses) == 1:
        print(render_detail(analyses[0]), end="")
    else:
        print(render_markdown(analyses), end="")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="maintainer-radar",
        description="Generate local-first maintainer triage reports for GitHub pull requests.",
    )

    def add_format_argument(target: argparse.ArgumentParser, *, default: str | object) -> None:
        target.add_argument(
            "--format",
            choices=["markdown", "json", "csv"],
            default=default,
            help="Output format. Default: markdown.",
        )

    def add_config_argument(target: argparse.ArgumentParser) -> None:
        target.add_argument(
            "--config",
            help="Path to config JSON. Defaults to .maintainer-radar.json when present.",
        )

    add_format_argument(parser, default="markdown")
    sub = parser.add_subparsers(dest="command", required=True)

    repo = sub.add_parser("repo", help="Analyze pull requests in a repository.")
    add_format_argument(repo, default=argparse.SUPPRESS)
    add_config_argument(repo)
    repo.add_argument("repository", help="Repository in owner/name form.")
    repo.add_argument("--state", default="open", choices=["open", "closed", "all"])
    repo.add_argument("--limit", type=int, default=30)
    repo.add_argument("--label", help="Only include PRs with this label.")
    repo.add_argument("--author", help="Only include PRs by this author.")
    repo.add_argument("--stale-days", type=int, help="Only include PRs quiet for at least N days.")
    repo.add_argument("--updated-since", help="Only include PRs updated on or after this ISO date.")
    repo.add_argument(
        "--action",
        choices=sorted(ACTION_SLUGS),
        help="Only include PRs with this recommended action.",
    )
    repo.add_argument("--min-score", type=int, help="Only include PRs with reviewability >= N.")
    repo.add_argument("--max-risk", type=int, help="Only include PRs with risk <= N.")
    repo.add_argument("--summary-only", action="store_true", help="Print only the queue summary.")

    pr = sub.add_parser("pr", help="Analyze one pull request.")
    add_format_argument(pr, default=argparse.SUPPRESS)
    add_config_argument(pr)
    pr.add_argument("repository", help="Repository in owner/name form.")
    pr.add_argument("number", help="Pull request number.")
    pr.add_argument(
        "--comment-template",
        action="store_true",
        help="Render a draft maintainer follow-up comment. Does not post it.",
    )

    author = sub.add_parser("author", help="Analyze pull requests by author.")
    add_format_argument(author, default=argparse.SUPPRESS)
    add_config_argument(author)
    author.add_argument("username", help="GitHub username.")
    author.add_argument("--state", default="open", choices=["open", "closed"])
    author.add_argument("--limit", type=int, default=50)
    author.add_argument(
        "--action",
        choices=sorted(ACTION_SLUGS),
        help="Only include PRs with this recommended action.",
    )
    author.add_argument("--min-score", type=int, help="Only include PRs with reviewability >= N.")
    author.add_argument("--max-risk", type=int, help="Only include PRs with risk <= N.")
    author.add_argument("--summary-only", action="store_true", help="Print only the queue summary.")

    from_json = sub.add_parser("from-json", help="Analyze offline JSON fixture data.")
    add_format_argument(from_json, default=argparse.SUPPRESS)
    add_config_argument(from_json)
    from_json.add_argument("path", help="Path to JSON file.")
    from_json.add_argument(
        "--source",
        choices=["github", "gitlab", "forgejo", "gitea"],
        default="github",
        help="Input JSON source shape. Default: github.",
    )
    from_json.add_argument("--detail", action="store_true", help="Render a detailed single-PR brief.")
    from_json.add_argument(
        "--action",
        choices=sorted(ACTION_SLUGS),
        help="Only include PRs with this recommended action.",
    )
    from_json.add_argument("--min-score", type=int, help="Only include PRs with reviewability >= N.")
    from_json.add_argument("--max-risk", type=int, help="Only include PRs with risk <= N.")
    from_json.add_argument("--summary-only", action="store_true", help="Print only the queue summary.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
        if args.command == "repo":
            prs = list_repo_prs(args.repository, state=args.state, limit=args.limit)
            prs = filter_prs(
                prs,
                label=args.label,
                author=args.author,
                stale_days=args.stale_days,
                updated_since=args.updated_since,
            )
            analyses = filter_analyses(
                [analyze_pr(pr, config=config) for pr in prs],
                action=args.action,
                min_score=args.min_score,
                max_risk=args.max_risk,
            )
            _emit(
                analyses,
                args.format,
                summary_only=args.summary_only,
            )
        elif args.command == "pr":
            pr = view_pr(args.repository, args.number)
            analysis = analyze_pr(pr, config=config)
            if args.comment_template:
                if args.format == "json":
                    print(json.dumps({"comment": render_comment_template(analysis)}, indent=2))
                elif args.format == "csv":
                    print(render_comment_csv(render_comment_template(analysis)), end="")
                else:
                    print(render_comment_template(analysis), end="")
            else:
                _emit([analysis], args.format, detail=True)
        elif args.command == "author":
            prs = search_author_prs(args.username, state=args.state, limit=args.limit)
            analyses = filter_analyses(
                [analyze_pr(pr, config=config) for pr in prs],
                action=args.action,
                min_score=args.min_score,
                max_risk=args.max_risk,
            )
            _emit(
                analyses,
                args.format,
                summary_only=args.summary_only,
            )
        elif args.command == "from-json":
            prs = _as_pr_list(_load_json(args.path), source=args.source)
            detail = bool(args.detail and len(prs) == 1)
            analyses = filter_analyses(
                [analyze_pr(pr, config=config) for pr in prs],
                action=args.action,
                min_score=args.min_score,
                max_risk=args.max_risk,
            )
            _emit(
                analyses,
                args.format,
                detail=detail,
                summary_only=args.summary_only,
            )
        else:
            parser.error("unknown command")
    except (GitHubCliError, OSError, ValueError) as exc:
        print(f"maintainer-radar: {exc}", file=sys.stderr)
        return 2
    return 0
