from __future__ import annotations

from typing import Any


GITLAB_PIPELINE_CONCLUSIONS = {
    "success": "SUCCESS",
    "failed": "FAILURE",
    "canceled": "CANCELLED",
    "cancelled": "CANCELLED",
    "skipped": "SKIPPED",
}

GITLAB_PENDING_STATUSES = {
    "created",
    "manual",
    "pending",
    "preparing",
    "running",
    "scheduled",
    "waiting_for_resource",
}


def normalize_items(data: Any, *, source: str) -> list[dict[str, Any]]:
    items = _as_items(data)
    if source == "github":
        return items
    if source == "gitlab":
        return [normalize_gitlab_mr(item) for item in items]
    raise ValueError(f"Unsupported source: {source}")


def _as_items(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("items", "merge_requests", "mergeRequests"):
            if isinstance(data.get(key), list):
                return data[key]
        return [data]
    raise ValueError("JSON input must be an object, a list, or an object with items")


def normalize_gitlab_mr(mr: dict[str, Any]) -> dict[str, Any]:
    author = mr.get("author") or {}
    changes = _changes(mr)
    additions, deletions = _diff_stats(mr, changes)
    labels = _labels(mr.get("labels"))
    comments = _comments(mr)
    pipeline = mr.get("head_pipeline") or mr.get("pipeline") or {}

    return {
        "number": mr.get("iid") or mr.get("number") or mr.get("id"),
        "title": mr.get("title"),
        "url": mr.get("web_url") or mr.get("url"),
        "author": {
            "login": author.get("username") or author.get("name") or mr.get("author_username")
        },
        "body": mr.get("description") or mr.get("body") or "",
        "updatedAt": mr.get("updated_at") or mr.get("updatedAt"),
        "createdAt": mr.get("created_at") or mr.get("createdAt"),
        "isDraft": bool(mr.get("draft") or mr.get("work_in_progress") or _title_is_draft(mr)),
        "labels": labels,
        "reviewDecision": _review_decision(mr),
        "statusCheckRollup": [_pipeline_check(pipeline)] if pipeline else [],
        "comments": comments,
        "latestReviews": _latest_reviews(mr),
        "files": _files(changes),
        "additions": additions,
        "deletions": deletions,
        "changedFiles": _changed_files(mr, changes),
    }


def _title_is_draft(mr: dict[str, Any]) -> bool:
    title = str(mr.get("title") or "").lower().strip()
    return title.startswith("draft:") or title.startswith("wip:")


def _labels(value: Any) -> list[dict[str, str]]:
    if not value:
        return []
    if isinstance(value, str):
        parts = [part.strip() for part in value.split(",")]
    elif isinstance(value, list):
        parts = [str(item.get("name") if isinstance(item, dict) else item).strip() for item in value]
    else:
        parts = []
    return [{"name": part} for part in parts if part]


def _pipeline_check(pipeline: dict[str, Any]) -> dict[str, str | None]:
    status = str(pipeline.get("status") or "").lower()
    if status in GITLAB_PENDING_STATUSES:
        return {
            "name": pipeline.get("ref") or "pipeline",
            "status": status.upper(),
            "conclusion": None,
        }
    return {
        "name": pipeline.get("ref") or "pipeline",
        "status": "COMPLETED" if status else "",
        "conclusion": GITLAB_PIPELINE_CONCLUSIONS.get(status, status.upper() or None),
    }


def _review_decision(mr: dict[str, Any]) -> str:
    if mr.get("blocking_discussions_resolved") is False:
        return "CHANGES_REQUESTED"
    if mr.get("approved") or mr.get("approved_by"):
        return "APPROVED"
    if str(mr.get("detailed_merge_status") or "").lower() in {
        "discussions_not_resolved",
        "ci_must_pass",
        "not_approved",
    }:
        return "CHANGES_REQUESTED"
    return "REVIEW_REQUIRED"


def _changes(mr: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("changes", "diffs"):
        value = mr.get(key)
        if isinstance(value, list):
            return value
    return []


def _files(changes: list[dict[str, Any]]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for change in changes:
        path = change.get("new_path") or change.get("old_path") or change.get("path")
        if path:
            result.append({"path": str(path)})
    return result


def _changed_files(mr: dict[str, Any], changes: list[dict[str, Any]]) -> int:
    for key in ("changes_count", "changed_files", "changedFiles"):
        value = mr.get(key)
        if value is not None:
            try:
                return int(value)
            except (TypeError, ValueError):
                pass
    return len(changes)


def _diff_stats(mr: dict[str, Any], changes: list[dict[str, Any]]) -> tuple[int, int]:
    stats = mr.get("stats") or {}
    additions = _int_or_none(stats.get("additions") or mr.get("additions"))
    deletions = _int_or_none(stats.get("deletions") or mr.get("deletions"))
    if additions is not None or deletions is not None:
        return additions or 0, deletions or 0

    added = removed = 0
    for change in changes:
        diff = str(change.get("diff") or "")
        for line in diff.splitlines():
            if line.startswith("+++") or line.startswith("---"):
                continue
            if line.startswith("+"):
                added += 1
            elif line.startswith("-"):
                removed += 1
    return added, removed


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _comments(mr: dict[str, Any]) -> list[dict[str, str]]:
    comments: list[dict[str, str]] = []
    for key in ("comments", "notes"):
        value = mr.get(key)
        if isinstance(value, list):
            for note in value:
                body = note.get("body") if isinstance(note, dict) else str(note)
                if body:
                    comments.append({"body": str(body)})
    discussions = mr.get("discussions")
    if isinstance(discussions, list):
        for discussion in discussions:
            notes = discussion.get("notes") if isinstance(discussion, dict) else None
            if not isinstance(notes, list):
                continue
            for note in notes:
                body = note.get("body") if isinstance(note, dict) else str(note)
                if body:
                    comments.append({"body": str(body)})
    return comments


def _latest_reviews(mr: dict[str, Any]) -> list[dict[str, str]]:
    if mr.get("blocking_discussions_resolved") is False:
        return [{"state": "CHANGES_REQUESTED", "body": "Blocking discussions are unresolved."}]
    if mr.get("approved") or mr.get("approved_by"):
        return [{"state": "APPROVED", "body": ""}]
    return []

