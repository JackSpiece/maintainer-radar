from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any

from .config import DEFAULT_CONFIG

CODE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".css",
    ".go",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".mjs",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".scss",
    ".sh",
    ".sql",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
}

TEST_HINTS = (
    "/test/",
    "/tests/",
    "__tests__",
    ".spec.",
    ".test.",
    "_test.",
    "test_",
)

DOC_HINTS = (
    ".md",
    ".mdx",
    "/docs/",
    "docs/",
    "readme",
    "changelog",
    "license",
)

GENERATED_HINTS = (
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "poetry.lock",
    "cargo.lock",
    "go.sum",
    "dist/",
    "build/",
    "vendor/",
    "generated",
)

BLOCKER_RE = re.compile(
    r"\b("
    r"not working|doesn'?t work|fails?|failure|broken|blocked|blocker|"
    r"changes requested|please fix|needs? changes?|regression|"
    r"cannot merge|won'?t merge|missing tests?|please test"
    r")\b",
    re.IGNORECASE,
)

TEST_PLAN_RE = re.compile(
    r"\b(test plan|tests?|validation|verified|repro|manual test|ci)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CheckSummary:
    passed: int = 0
    failed: int = 0
    pending: int = 0
    skipped: int = 0
    total: int = 0


@dataclass(frozen=True)
class FileSummary:
    code_files: int = 0
    doc_files: int = 0
    test_files: int = 0
    generated_files: int = 0
    total_files: int = 0


def parse_github_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    cleaned = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        return None


def days_since(value: str | None, now: datetime | None = None) -> int | None:
    dt = parse_github_datetime(value)
    if dt is None:
        return None
    now = now or datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max(0, (now - dt).days)


def summarize_checks(items: list[dict[str, Any]] | None) -> CheckSummary:
    passed = failed = pending = skipped = 0
    for item in items or []:
        status = str(item.get("status") or "").upper()
        conclusion = str(item.get("conclusion") or "").upper()
        if status and status != "COMPLETED":
            pending += 1
        elif conclusion in {"SUCCESS", "NEUTRAL"}:
            passed += 1
        elif conclusion == "SKIPPED":
            skipped += 1
        elif conclusion in {"FAILURE", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED"}:
            failed += 1
        elif conclusion:
            pending += 1
    return CheckSummary(
        passed=passed,
        failed=failed,
        pending=pending,
        skipped=skipped,
        total=passed + failed + pending + skipped,
    )


def summarize_files(
    files: list[dict[str, Any]] | None,
    config: dict[str, Any] | None = None,
) -> FileSummary:
    config = config or DEFAULT_CONFIG
    test_hints = (*TEST_HINTS, *config.get("test_hints", []))
    doc_hints = (*DOC_HINTS, *config.get("doc_hints", []))
    generated_hints = (*GENERATED_HINTS, *config.get("generated_hints", []))
    code_files = doc_files = test_files = generated_files = 0
    for file_info in files or []:
        path = str(file_info.get("path") or file_info.get("filename") or "").lower()
        if not path:
            continue
        if any(hint in path for hint in test_hints):
            test_files += 1
        if any(path.endswith(hint) or hint in path for hint in doc_hints):
            doc_files += 1
        if any(hint in path for hint in generated_hints):
            generated_files += 1
        if any(path.endswith(ext) for ext in CODE_EXTENSIONS):
            code_files += 1
    return FileSummary(
        code_files=code_files,
        doc_files=doc_files,
        test_files=test_files,
        generated_files=generated_files,
        total_files=len(files or []),
    )


def _body(pr: dict[str, Any]) -> str:
    return str(pr.get("body") or "")


def _comments_and_reviews(pr: dict[str, Any]) -> list[str]:
    text: list[str] = []
    for comment in pr.get("comments") or []:
        text.append(str(comment.get("body") or ""))
    for review in pr.get("latestReviews") or pr.get("reviews") or []:
        text.append(str(review.get("body") or ""))
        state = str(review.get("state") or "")
        if state:
            text.append(state.replace("_", " "))
    return text


def _has_blocker(pr: dict[str, Any]) -> bool:
    return any(BLOCKER_RE.search(text) for text in _comments_and_reviews(pr))


def _has_test_plan(pr: dict[str, Any]) -> bool:
    body = _body(pr)
    return bool(body and TEST_PLAN_RE.search(body))


def _label_names(pr: dict[str, Any]) -> list[str]:
    labels = pr.get("labels") or []
    result: list[str] = []
    for label in labels:
        if isinstance(label, str):
            result.append(label)
        else:
            result.append(str(label.get("name") or ""))
    return [name for name in result if name]


def analyze_pr(
    pr: dict[str, Any],
    now: datetime | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return deterministic maintainer triage metadata for one PR dictionary."""
    config = config or DEFAULT_CONFIG
    checks = summarize_checks(pr.get("statusCheckRollup"))
    files = summarize_files(pr.get("files"), config=config)
    additions = int(pr.get("additions") or 0)
    deletions = int(pr.get("deletions") or 0)
    changed_files = int(pr.get("changedFiles") or files.total_files or 0)
    total_diff = additions + deletions
    review_decision = str(pr.get("reviewDecision") or "").upper()
    is_draft = bool(pr.get("isDraft") or pr.get("draft"))
    stale_days = days_since(pr.get("updatedAt"), now)
    has_blocker = _has_blocker(pr)
    has_test_plan = _has_test_plan(pr)
    has_body = "body" in pr

    risk = 0
    signals: list[str] = []
    flags: list[str] = []

    if is_draft:
        risk += 25
        flags.append("draft PR")

    if total_diff > config["very_large_diff_lines"] or changed_files > config["very_large_file_count"]:
        risk += 30
        flags.append("very large diff")
    elif total_diff > config["large_diff_lines"] or changed_files > config["large_file_count"]:
        risk += 15
        flags.append("large diff")

    if checks.total == 0:
        risk += 8
        flags.append("no visible checks")
    elif checks.failed:
        risk += 30
        flags.append("CI failing")
    elif checks.pending:
        risk += 10
        flags.append("CI pending")
    elif checks.passed:
        risk -= 8
        signals.append("CI passed")

    if review_decision == "APPROVED":
        risk -= 10
        signals.append("approved")
    elif review_decision == "CHANGES_REQUESTED":
        risk += 25
        flags.append("changes requested")
    elif review_decision == "REVIEW_REQUIRED":
        signals.append("review required")

    if stale_days is not None:
        if stale_days >= config["stale_days"]:
            risk += 15
            flags.append(f"stale {stale_days} days")
        elif stale_days >= config["quiet_days"]:
            risk += 8
            flags.append(f"quiet {stale_days} days")

    if has_blocker:
        risk += 25
        flags.append("maintainer blocker language")

    if has_body and not has_test_plan and files.code_files:
        risk += 8
        flags.append("no test plan found")
    elif has_test_plan:
        signals.append("test plan present")

    if files.code_files and not files.test_files:
        risk += 10
        flags.append("code changed without tests")
    elif files.test_files:
        signals.append("tests changed")

    if files.generated_files:
        risk += min(12, files.generated_files * 3)
        flags.append("generated or lockfile changes")

    if not files.code_files and files.doc_files:
        risk -= 6
        signals.append("docs-only shape")

    risk = max(0, min(100, risk))
    reviewability = 100 - risk
    action = choose_action(
        reviewability=reviewability,
        is_draft=is_draft,
        checks=checks,
        has_blocker=has_blocker,
        total_diff=total_diff,
        changed_files=changed_files,
        review_decision=review_decision,
        config=config,
    )

    return {
        "number": pr.get("number"),
        "title": pr.get("title"),
        "url": pr.get("url"),
        "author": (pr.get("author") or {}).get("login") if isinstance(pr.get("author"), dict) else pr.get("author"),
        "labels": _label_names(pr),
        "risk": risk,
        "reviewability": reviewability,
        "action": action,
        "flags": flags,
        "signals": signals,
        "checks": checks.__dict__,
        "files": files.__dict__,
        "stale_days": stale_days,
        "additions": additions,
        "deletions": deletions,
        "changed_files": changed_files,
    }


def choose_action(
    *,
    reviewability: int,
    is_draft: bool,
    checks: CheckSummary,
    has_blocker: bool,
    total_diff: int,
    changed_files: int,
    review_decision: str,
    config: dict[str, Any] | None = None,
) -> str:
    config = config or DEFAULT_CONFIG
    if is_draft:
        return "wait for author"
    if checks.failed:
        return "ask for CI fix"
    if checks.pending:
        return "wait for CI"
    if review_decision == "CHANGES_REQUESTED" or has_blocker:
        return "needs author follow-up"
    if total_diff > config["very_large_diff_lines"] or changed_files > config["very_large_file_count"]:
        return "request smaller PR"
    if reviewability >= 75:
        return "review now"
    if reviewability >= 55:
        return "review with caution"
    return "needs triage"
