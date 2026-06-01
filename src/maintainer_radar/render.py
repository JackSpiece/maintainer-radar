from __future__ import annotations

import csv
from html import escape
from io import StringIO
import re
from typing import Any


CSV_FIELDS = [
    "number",
    "title",
    "author",
    "action",
    "next_step",
    "reviewability",
    "risk",
    "stale_days",
    "changed_files",
    "additions",
    "deletions",
    "labels",
    "signals",
    "flags",
    "score_breakdown",
    "url",
]

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f8fafc;
      --text: #111827;
      --muted: #475569;
      --line: #d8dee9;
      --panel: #ffffff;
      --blue: #2563eb;
      --green: #047857;
      --amber: #b45309;
      --red: #b91c1c;
      --purple: #7c3aed;
    }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 15px/1.5 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      width: min(1120px, calc(100% - 32px));
      margin: 32px auto;
    }}
    header {{
      margin-bottom: 24px;
    }}
    h1 {{
      margin: 0 0 6px;
      font-size: clamp(28px, 5vw, 42px);
      letter-spacing: 0;
    }}
    .subtitle {{
      margin: 0;
      color: var(--muted);
      font-size: 16px;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 10px;
      margin: 22px 0;
    }}
    .metric {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 12px;
    }}
    .metric strong {{
      display: block;
      font-size: 24px;
      line-height: 1.1;
    }}
    .metric span {{
      color: var(--muted);
      font-size: 13px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 11px 12px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background: #eef2f7;
      color: #243041;
      font-size: 13px;
      text-transform: uppercase;
    }}
    tr:last-child td {{
      border-bottom: 0;
    }}
    a {{
      color: var(--blue);
      text-decoration: none;
    }}
    a:hover {{
      text-decoration: underline;
    }}
    .score {{
      font-variant-numeric: tabular-nums;
      text-align: right;
      white-space: nowrap;
    }}
    .action {{
      display: inline-block;
      border-radius: 999px;
      padding: 2px 8px;
      background: #e5e7eb;
      color: #1f2937;
      white-space: nowrap;
    }}
    .action-review-now {{
      background: #d1fae5;
      color: var(--green);
    }}
    .action-ask-for-ci-fix,
    .action-needs-author-follow-up,
    .action-wait-for-author {{
      background: #fee2e2;
      color: var(--red);
    }}
    .action-wait-for-ci,
    .action-review-with-caution,
    .action-request-smaller-pr {{
      background: #fef3c7;
      color: var(--amber);
    }}
    .signals {{
      color: var(--muted);
    }}
    .impact {{
      color: var(--purple);
      font-size: 14px;
    }}
    .empty {{
      color: var(--muted);
      text-align: center;
    }}
    pre {{
      white-space: pre-wrap;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 14px;
      overflow-x: auto;
    }}
    footer {{
      margin-top: 18px;
      color: var(--muted);
      font-size: 13px;
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>{title}</h1>
      <p class="subtitle">Deterministic maintainer triage report.</p>
    </header>
    {summary}
    {table}
    <footer>Scores route maintainer attention. They do not replace review.</footer>
  </main>
</body>
</html>
"""


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
                "next_step": _next_step(item),
                "reviewability": item.get("reviewability", ""),
                "risk": item.get("risk", ""),
                "stale_days": item.get("stale_days", ""),
                "changed_files": item.get("changed_files", ""),
                "additions": item.get("additions", ""),
                "deletions": item.get("deletions", ""),
                "labels": _join_csv_value(item.get("labels")),
                "signals": _join_csv_value(item.get("signals")),
                "flags": _join_csv_value(item.get("flags")),
                "score_breakdown": _join_score_breakdown(item.get("score_breakdown")),
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


def render_html(
    analyses: list[dict[str, Any]],
    title: str = "Maintainer Radar Report",
    *,
    summary_only: bool = False,
) -> str:
    safe_title = escape(title)
    summary_html = _render_html_summary(analyses)
    table_html = "" if summary_only else _render_html_table(analyses)
    return HTML_TEMPLATE.format(title=safe_title, summary=summary_html, table=table_html)


def render_comment_html(comment: str) -> str:
    title = "Maintainer Radar Comment Draft"
    body = f"<pre>{escape(comment)}</pre>"
    return HTML_TEMPLATE.format(
        title=title,
        summary="",
        table=body,
    )


def _join_csv_value(value: Any) -> str:
    if not value:
        return ""
    if isinstance(value, list):
        return "; ".join(str(item) for item in value if item)
    return str(value)


def _next_step(item: dict[str, Any]) -> str:
    return str(item.get("next_step") or "Triage manually before assigning reviewer time.")


def _format_risk_delta(value: Any) -> str:
    try:
        delta = int(value)
    except (TypeError, ValueError):
        return "0"
    return f"+{delta}" if delta > 0 else str(delta)


def _join_score_breakdown(value: Any) -> str:
    if not value:
        return ""
    items: list[str] = []
    for entry in value:
        if not isinstance(entry, dict):
            continue
        label = str(entry.get("label") or "").strip()
        if not label:
            continue
        delta = _format_risk_delta(entry.get("risk_delta"))
        items.append(f"{label} ({delta} risk)")
    return "; ".join(items)


def _render_html_summary(analyses: list[dict[str, Any]]) -> str:
    summary = summarize_report(analyses)
    metrics = [
        ("PRs scanned", summary["total"]),
        ("Review now", summary["review_now"]),
        ("Author follow-up", summary["author_follow_up"]),
        ("CI blocked", summary["ci_blocked"] + summary["ci_pending"]),
        ("Large or triage", summary["large_or_triage"]),
        ("Stale 7+ days", summary["stale"]),
        ("Average score", f"{summary['average_score']}/100"),
    ]
    items = "\n".join(
        f'<div class="metric"><strong>{escape(str(value))}</strong><span>{escape(label)}</span></div>'
        for label, value in metrics
    )
    return f'<section class="metrics">{items}</section>'


def _render_html_table(analyses: list[dict[str, Any]]) -> str:
    if not analyses:
        return '<p class="empty">No pull requests matched this report.</p>'

    rows = "\n".join(_render_html_row(item) for item in analyses)
    return (
        "<table>"
        "<thead><tr>"
        "<th>PR</th><th>Action</th><th>Next step</th><th>Score</th><th>Risk impact</th><th>Signals</th>"
        "</tr></thead>"
        f"<tbody>{rows}</tbody>"
        "</table>"
    )


def _render_html_row(item: dict[str, Any]) -> str:
    number = item.get("number")
    title_text = str(item.get("title") or "Untitled")
    label = f"#{number} {title_text}" if number else title_text
    url = _safe_url(item.get("url"))
    if url:
        pr_html = f'<a href="{url}">{escape(label)}</a>'
    else:
        pr_html = escape(label)

    action = str(item.get("action") or "needs triage")
    signals = item.get("signals") or []
    flags = item.get("flags") or []
    impact_text = _join_score_breakdown(item.get("score_breakdown")) or "no score changes"
    signal_text = _join_csv_value([*signals, *flags]) or "no notable signals"
    return (
        "<tr>"
        f"<td>{pr_html}</td>"
        f'<td><span class="action {_action_class(action)}">{escape(action)}</span></td>'
        f"<td>{escape(_next_step(item))}</td>"
        f'<td class="score">{escape(str(item.get("reviewability") or 0))}</td>'
        f'<td class="impact">{escape(impact_text)}</td>'
        f'<td class="signals">{escape(signal_text)}</td>'
        "</tr>"
    )


def _safe_url(value: Any) -> str | None:
    url = str(value or "")
    if not url.startswith(("https://", "http://")):
        return None
    return escape(url, quote=True)


def _action_class(action: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", action.lower()).strip("-")
    return f"action-{slug}" if slug else "action-default"


def render_markdown(analyses: list[dict[str, Any]], title: str = "Maintainer Radar Report") -> str:
    lines = [
        render_summary_markdown(analyses, title=title).rstrip(),
        "",
        "| PR | Action | Next Step | Score | Risk Impact | Signals |",
        "| --- | --- | --- | ---: | --- | --- |",
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
        impact_text = _join_score_breakdown(item.get("score_breakdown")) or "no score changes"
        signal_text = ", ".join([*signals, *flags]) or "no notable signals"
        lines.append(
            f"| {label} | {item.get('action')} | {_next_step(item)} | {item.get('reviewability')} | {impact_text} | {signal_text} |"
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
        f"- **Next step:** {_next_step(item)}",
        f"- **Reviewability:** {item.get('reviewability')}/100",
        f"- **Risk:** {item.get('risk')}/100",
    ]
    raw_risk = item.get("raw_risk")
    if raw_risk is not None and raw_risk != item.get("risk"):
        lines.append(f"- **Raw risk before clamp:** {raw_risk}")
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

    lines.extend(["", "### Score Breakdown", ""])
    score_breakdown = item.get("score_breakdown") or []
    if score_breakdown:
        for entry in score_breakdown:
            if not isinstance(entry, dict):
                continue
            label = str(entry.get("label") or "").strip()
            if label:
                delta = _format_risk_delta(entry.get("risk_delta"))
                lines.append(f"- {label}: {delta} risk")
    else:
        lines.append("- No score adjustments detected")

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
