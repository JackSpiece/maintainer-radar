from __future__ import annotations

import csv
from io import StringIO
from typing import Any


CSV_FIELDS = [
    "number",
    "title",
    "author",
    "action",
    "reviewability",
    "risk",
    "stale_days",
    "changed_files",
    "additions",
    "deletions",
    "labels",
    "signals",
    "flags",
    "url",
]


def summarize_report(analyses: list[dict[str, Any]]) -> dict[str, int]:
    actions = [str(item.get("action") or "") for item in analyses]
    scores = [int(item.get("reviewability") or 0) for item in analyses]
    stale_count = sum(1 for item in analyses if (item.get("stale_days") or 0) >= 7)
    ci_blocked = sum(1 for item in analyses if "CI failing" in (item.get("flags") or []))
    ci_pending = sum(1 for item in analyses if "CI pending" in (item.get("flags") or []))
    return {
        "total": len(analyses),
        "review_now": actions.count("review now"),
        "author_follow_up": actions.count("needs author follow-up"),
        "ci_blocked": ci_blocked,
        "ci_pending": ci_pending,
        "large_or_triage": actions.count("request smaller PR") + actions.count("needs triage"),
        "stale": stale_count,
        "average_score": round(sum(scores) / len(scores)) if scores else 0,
    }


def render_summary_markdown(
    analyses: list[dict[str, Any]],
    title: str = "Maintainer Radar Summary",
) -> str:
    summary = summarize_report(analyses)
    lines = [
        f"## {title}",
        "",
        f"- PRs scanned: {summary['total']}",
        f"- Review now: {summary['review_now']}",
        f"- Needs author follow-up: {summary['author_follow_up']}",
        f"- CI blocked or pending: {summary['ci_blocked'] + summary['ci_pending']}",
        f"- Large or needs triage: {summary['large_or_triage']}",
        f"- Stale 7+ days: {summary['stale']}",
        f"- Average reviewability: {summary['average_score']}/100",
        "",
    ]
    return "\n".join(lines)


def render_csv(analyses: list[dict[str, Any]]) -> str:
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    for item in analyses:
        writer.writerow(
            {
                "number": item.get("number"),
                "title": item.get("title") or "",
                "author": item.get("author") or "",
                "action": item.get("action") or "",
                "reviewability": item.get("reviewability", ""),
                "risk": item.get("risk", ""),
                "stale_days": item.get("stale_days", ""),
                "changed_files": item.get("changed_files", ""),
                "additions": item.get("additions", ""),
                "deletions": item.get("deletions", ""),
                "labels": _join_csv_value(item.get("labels")),
                "signals": _join_csv_value(item.get("signals")),
                "flags": _join_csv_value(item.get("flags")),
                "url": item.get("url") or "",
            }
        )
    return output.getvalue()


def render_summary_csv(analyses: list[dict[str, Any]]) -> str:
    summary = summarize_report(analyses)
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=list(summary), lineterminator="\n")
    writer.writeheader()
    writer.writerow(summary)
    return output.getvalue()


def render_comment_csv(comment: str) -> str:
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=["comment"], lineterminator="\n")
    writer.writeheader()
    writer.writerow({"comment": comment})
    return output.getvalue()


def _join_csv_value(value: Any) -> str:
    if not value:
        return ""
    if isinstance(value, list):
        return "; ".join(str(item) for item in value if item)
    return str(value)


def render_markdown(analyses: list[dict[str, Any]], title: str = "Maintainer Radar Report") -> str:
    lines = [
        render_summary_markdown(analyses, title=title).rstrip(),
        "",
        "| PR | Action | Score | Signals |",
        "| --- | --- | ---: | --- |",
    ]
    for item in analyses:
        number = item.get("number")
        title_text = item.get("title") or "Untitled"
        url = item.get("url")
        label = f"#{number} {title_text}" if number else title_text
        if url:
            label = f"[{label}]({url})"
        signals = item.get("signals") or []
        flags = item.get("flags") or []
        signal_text = ", ".join([*signals, *flags]) or "no notable signals"
        lines.append(
            f"| {label} | {item.get('action')} | {item.get('reviewability')} | {signal_text} |"
        )

    lines.extend(
        [
            "",
            "Scores are deterministic heuristics. They route maintainer attention, not merge authority.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_detail(item: dict[str, Any]) -> str:
    lines = [
        f"## PR #{item.get('number')} Maintainer Brief",
        "",
        f"- **Title:** {item.get('title')}",
        f"- **Action:** {item.get('action')}",
        f"- **Reviewability:** {item.get('reviewability')}/100",
        f"- **Risk:** {item.get('risk')}/100",
    ]
    if item.get("url"):
        lines.append(f"- **URL:** {item.get('url')}")
    if item.get("author"):
        lines.append(f"- **Author:** {item.get('author')}")
    if item.get("stale_days") is not None:
        lines.append(f"- **Last activity:** {item.get('stale_days')} days ago")

    checks = item.get("checks") or {}
    files = item.get("files") or {}
    lines.extend(
        [
            "",
            "### Checks",
            "",
            f"- Passed: {checks.get('passed', 0)}",
            f"- Failed: {checks.get('failed', 0)}",
            f"- Pending: {checks.get('pending', 0)}",
            f"- Skipped: {checks.get('skipped', 0)}",
            "",
            "### Diff Shape",
            "",
            f"- Additions: {item.get('additions', 0)}",
            f"- Deletions: {item.get('deletions', 0)}",
            f"- Changed files: {item.get('changed_files', 0)}",
            f"- Code files: {files.get('code_files', 0)}",
            f"- Test files: {files.get('test_files', 0)}",
            f"- Docs files: {files.get('doc_files', 0)}",
        ]
    )

    flags = item.get("flags") or []
    signals = item.get("signals") or []
    lines.extend(["", "### Signals", ""])
    if signals:
        lines.extend(f"- {signal}" for signal in signals)
    else:
        lines.append("- No positive signals detected")

    lines.extend(["", "### Flags", ""])
    if flags:
        lines.extend(f"- {flag}" for flag in flags)
    else:
        lines.append("- No risk flags detected")

    return "\n".join(lines) + "\n"


def render_comment_template(item: dict[str, Any]) -> str:
    action = str(item.get("action") or "needs triage")
    flags = [str(flag) for flag in item.get("flags") or []]
    reviewability = item.get("reviewability")

    requests: list[str] = []
    if any("CI failing" in flag for flag in flags):
        requests.append("Get CI passing or explain why the failing check is unrelated.")
    if any("CI pending" in flag for flag in flags):
        requests.append("Wait for CI to finish before requesting another review.")
    if any("no test plan" in flag for flag in flags):
        requests.append("Add a short validation or test plan to the PR body.")
    if any("code changed without tests" in flag for flag in flags):
        requests.append("Add regression coverage, or explain why tests are not practical for this change.")
    if any("maintainer blocker language" in flag for flag in flags):
        requests.append("Respond to the unresolved maintainer feedback before the next review pass.")
    if any("large diff" in flag or "very large diff" in flag for flag in flags):
        requests.append("Consider splitting the PR or explaining why the current scope needs to stay together.")
    if any(flag.startswith("stale ") or flag.startswith("quiet ") for flag in flags):
        requests.append("Rebase or leave a short status update so reviewers know the PR is still active.")
    if not requests:
        requests.append("Keep CI green and leave any extra context that would make review easier.")

    lines = [
        "Thanks for the PR.",
        "",
        f"Current triage suggests: **{action}**.",
    ]
    if reviewability is not None:
        lines.append(f"Reviewability score: **{reviewability}/100**.")
    lines.extend(["", "Before the next maintainer pass, please:"])
    lines.extend(f"- {request}" for request in requests)
    lines.extend(
        [
            "",
            "_Generated as a draft with Maintainer Radar. Please edit before posting._",
            "",
        ]
    )
    return "\n".join(lines)
