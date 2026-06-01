from __future__ import annotations

import argparse
from datetime import timezone
import json
import sys
from typing import Any

from .github import GitHubCliError, list_repo_prs, search_author_prs, view_pr
from .render import render_detail, render_markdown, render_summary_markdown, summarize_report
from .scoring import analyze_pr, days_since, parse_github_datetime


def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _as_pr_list(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return data["items"]
    if isinstance(data, dict):
        return [data]
    raise ValueError("JSON input must be a PR object, a list of PR objects, or an object with items")


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
            choices=["markdown", "json"],
            default=default,
            help="Output format. Default: markdown.",
        )

    add_format_argument(parser, default="markdown")
    sub = parser.add_subparsers(dest="command", required=True)

    repo = sub.add_parser("repo", help="Analyze pull requests in a repository.")
    add_format_argument(repo, default=argparse.SUPPRESS)
    repo.add_argument("repository", help="Repository in owner/name form.")
    repo.add_argument("--state", default="open", choices=["open", "closed", "all"])
    repo.add_argument("--limit", type=int, default=30)
    repo.add_argument("--label", help="Only include PRs with this label.")
    repo.add_argument("--author", help="Only include PRs by this author.")
    repo.add_argument("--stale-days", type=int, help="Only include PRs quiet for at least N days.")
    repo.add_argument("--updated-since", help="Only include PRs updated on or after this ISO date.")
    repo.add_argument("--summary-only", action="store_true", help="Print only the queue summary.")

    pr = sub.add_parser("pr", help="Analyze one pull request.")
    add_format_argument(pr, default=argparse.SUPPRESS)
    pr.add_argument("repository", help="Repository in owner/name form.")
    pr.add_argument("number", help="Pull request number.")

    author = sub.add_parser("author", help="Analyze pull requests by author.")
    add_format_argument(author, default=argparse.SUPPRESS)
    author.add_argument("username", help="GitHub username.")
    author.add_argument("--state", default="open", choices=["open", "closed"])
    author.add_argument("--limit", type=int, default=50)
    author.add_argument("--summary-only", action="store_true", help="Print only the queue summary.")

    from_json = sub.add_parser("from-json", help="Analyze offline JSON fixture data.")
    add_format_argument(from_json, default=argparse.SUPPRESS)
    from_json.add_argument("path", help="Path to JSON file.")
    from_json.add_argument("--detail", action="store_true", help="Render a detailed single-PR brief.")
    from_json.add_argument("--summary-only", action="store_true", help="Print only the queue summary.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "repo":
            prs = list_repo_prs(args.repository, state=args.state, limit=args.limit)
            prs = filter_prs(
                prs,
                label=args.label,
                author=args.author,
                stale_days=args.stale_days,
                updated_since=args.updated_since,
            )
            _emit(
                [analyze_pr(pr) for pr in prs],
                args.format,
                summary_only=args.summary_only,
            )
        elif args.command == "pr":
            pr = view_pr(args.repository, args.number)
            _emit([analyze_pr(pr)], args.format, detail=True)
        elif args.command == "author":
            prs = search_author_prs(args.username, state=args.state, limit=args.limit)
            _emit(
                [analyze_pr(pr) for pr in prs],
                args.format,
                summary_only=args.summary_only,
            )
        elif args.command == "from-json":
            prs = _as_pr_list(_load_json(args.path))
            detail = bool(args.detail and len(prs) == 1)
            _emit(
                [analyze_pr(pr) for pr in prs],
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
