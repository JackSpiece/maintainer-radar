from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any


class GitHubCliError(RuntimeError):
    pass


def _require_gh() -> None:
    if shutil.which("gh") is None:
        raise GitHubCliError("GitHub CLI not found. Install gh or use from-json mode.")


def gh_json(args: list[str]) -> Any:
    _require_gh()
    proc = subprocess.run(
        ["gh", *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        raise GitHubCliError(proc.stderr.strip() or "gh command failed")
    try:
        return json.loads(proc.stdout or "null")
    except json.JSONDecodeError as exc:
        raise GitHubCliError(f"gh returned invalid JSON: {exc}") from exc


PR_LIST_FIELDS = ",".join(
    [
        "additions",
        "author",
        "changedFiles",
        "comments",
        "createdAt",
        "deletions",
        "isDraft",
        "labels",
        "mergeable",
        "mergeStateStatus",
        "number",
        "reviewDecision",
        "reviewRequests",
        "statusCheckRollup",
        "title",
        "updatedAt",
        "url",
    ]
)

PR_VIEW_FIELDS = ",".join(
    [
        PR_LIST_FIELDS,
        "body",
        "files",
        "latestReviews",
    ]
)


def list_repo_prs(repo: str, *, state: str = "open", limit: int = 30) -> list[dict[str, Any]]:
    return gh_json(
        [
            "pr",
            "list",
            "--repo",
            repo,
            "--state",
            state,
            "--limit",
            str(limit),
            "--json",
            PR_LIST_FIELDS,
        ]
    )


def view_pr(repo: str, number: str | int) -> dict[str, Any]:
    return gh_json(
        [
            "pr",
            "view",
            str(number),
            "--repo",
            repo,
            "--json",
            PR_VIEW_FIELDS,
        ]
    )


def search_author_prs(author: str, *, state: str = "open", limit: int = 50) -> list[dict[str, Any]]:
    items = gh_json(
        [
            "search",
            "prs",
            "--author",
            author,
            "--state",
            state,
            "--limit",
            str(limit),
            "--json",
            "author,commentsCount,createdAt,isDraft,labels,number,repository,state,title,updatedAt,url",
        ]
    )
    normalized: list[dict[str, Any]] = []
    for item in items:
        normalized.append(
            {
                "author": item.get("author"),
                "comments": [{}] * int(item.get("commentsCount") or 0),
                "createdAt": item.get("createdAt"),
                "isDraft": item.get("isDraft"),
                "labels": item.get("labels"),
                "number": item.get("number"),
                "repository": item.get("repository"),
                "state": item.get("state"),
                "title": item.get("title"),
                "updatedAt": item.get("updatedAt"),
                "url": item.get("url"),
            }
        )
    return normalized
