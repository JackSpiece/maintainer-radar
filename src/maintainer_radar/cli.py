from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .github import GitHubCliError, list_repo_prs, search_author_prs, view_pr
from .render import render_detail, render_markdown
from .scoring import analyze_pr


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


def _emit(analyses: list[dict[str, Any]], fmt: str, *, detail: bool = False) -> None:
    if fmt == "json":
        print(json.dumps(analyses[0] if detail and len(analyses) == 1 else analyses, indent=2))
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

    pr = sub.add_parser("pr", help="Analyze one pull request.")
    add_format_argument(pr, default=argparse.SUPPRESS)
    pr.add_argument("repository", help="Repository in owner/name form.")
    pr.add_argument("number", help="Pull request number.")

    author = sub.add_parser("author", help="Analyze pull requests by author.")
    add_format_argument(author, default=argparse.SUPPRESS)
    author.add_argument("username", help="GitHub username.")
    author.add_argument("--state", default="open", choices=["open", "closed"])
    author.add_argument("--limit", type=int, default=50)

    from_json = sub.add_parser("from-json", help="Analyze offline JSON fixture data.")
    add_format_argument(from_json, default=argparse.SUPPRESS)
    from_json.add_argument("path", help="Path to JSON file.")
    from_json.add_argument("--detail", action="store_true", help="Render a detailed single-PR brief.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "repo":
            prs = list_repo_prs(args.repository, state=args.state, limit=args.limit)
            _emit([analyze_pr(pr) for pr in prs], args.format)
        elif args.command == "pr":
            pr = view_pr(args.repository, args.number)
            _emit([analyze_pr(pr)], args.format, detail=True)
        elif args.command == "author":
            prs = search_author_prs(args.username, state=args.state, limit=args.limit)
            _emit([analyze_pr(pr) for pr in prs], args.format)
        elif args.command == "from-json":
            prs = _as_pr_list(_load_json(args.path))
            detail = bool(args.detail and len(prs) == 1)
            _emit([analyze_pr(pr) for pr in prs], args.format, detail=detail)
        else:
            parser.error("unknown command")
    except (GitHubCliError, OSError, ValueError) as exc:
        print(f"maintainer-radar: {exc}", file=sys.stderr)
        return 2
    return 0
