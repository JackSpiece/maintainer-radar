from __future__ import annotations

from typing import Final


REPORT_EXTENSIONS: Final[dict[str, str]] = {
    "markdown": "md",
    "html": "html",
    "json": "json",
    "csv": "csv",
}

WORKFLOW_SORTS: Final[set[str]] = {"input", "action", "score", "risk", "stale", "number"}


def render_github_action_workflow(
    *,
    report_format: str = "markdown",
    schedule: str = "0 8 * * 1-5",
    limit: int = 50,
    sort: str = "action",
    hydrate: bool = True,
    top: int | None = None,
    step_summary: bool = True,
) -> str:
    if report_format not in REPORT_EXTENSIONS:
        formats = ", ".join(sorted(REPORT_EXTENSIONS))
        raise ValueError(f"--report-format must be one of: {formats}")
    if sort not in WORKFLOW_SORTS:
        sorts = ", ".join(sorted(WORKFLOW_SORTS))
        raise ValueError(f"--sort must be one of: {sorts}")
    if limit < 1:
        raise ValueError("--limit must be 1 or greater")
    if top is not None and top < 1:
        raise ValueError("--top must be 1 or greater")
    clean_schedule = schedule.strip()
    if not clean_schedule or "\n" in clean_schedule or "\r" in clean_schedule:
        raise ValueError("--schedule must be a single-line cron expression")

    extension = REPORT_EXTENSIONS[report_format]
    output_path = f"maintainer-radar.{extension}"
    artifact_name = f"maintainer-radar-{report_format}"
    command = _build_report_command(
        report_format=report_format,
        output_path=output_path,
        limit=limit,
        sort=sort,
        hydrate=hydrate,
        top=top,
        step_summary=step_summary,
    )
    summary_step = _render_summary_step(limit=limit, sort=sort, hydrate=hydrate, top=top)

    escaped_schedule = clean_schedule.replace('"', '\\"')
    job_summary_note = (
        "\n"
        "      - name: Publish job summary\n"
        "        continue-on-error: true\n"
        "        env:\n"
        "          GH_TOKEN: ${{ github.token }}\n"
        "        run: |\n"
        f"{summary_step}"
        if step_summary and report_format != "markdown"
        else ""
    )
    return f"""name: Maintainer Radar Report

on:
  workflow_dispatch:
  schedule:
    - cron: "{escaped_schedule}"

permissions:
  contents: read
  pull-requests: read

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - name: Install Maintainer Radar
        run: python -m pip install git+https://github.com/JackSpiece/maintainer-radar.git
      - name: Build {report_format} report
        env:
          GH_TOKEN: ${{{{ github.token }}}}
        run: |
{command}
      - uses: actions/upload-artifact@v4
        with:
          name: {artifact_name}
          path: {output_path}
{job_summary_note}
"""


def _repo_command_base(
    *,
    limit: int,
    sort: str,
    hydrate: bool,
    top: int | None,
) -> list[str]:
    lines = [
        '          maintainer-radar repo "${{ github.repository }}" \\',
        f"            --limit {limit} \\",
    ]
    if hydrate:
        lines.append("            --hydrate \\")
    lines.append(f"            --sort {sort} \\")
    if top is not None:
        lines.append(f"            --top {top} \\")
    return lines


def _build_report_command(
    *,
    report_format: str,
    output_path: str,
    limit: int,
    sort: str,
    hydrate: bool,
    top: int | None,
    step_summary: bool,
) -> str:
    lines: list[str] = []
    if step_summary and report_format == "markdown":
        lines.append("          set -o pipefail")
    lines.extend(_repo_command_base(limit=limit, sort=sort, hydrate=hydrate, top=top))
    if step_summary and report_format == "markdown":
        lines.extend(
            [
                "            --format markdown \\",
                f'            | tee {output_path} >> "$GITHUB_STEP_SUMMARY"',
            ]
        )
    else:
        lines.extend(
            [
                f"            --format {report_format} \\",
                f"            > {output_path}",
            ]
        )
    return "\n".join(lines)


def _render_summary_step(
    *,
    limit: int,
    sort: str,
    hydrate: bool,
    top: int | None,
) -> str:
    lines = _repo_command_base(limit=limit, sort=sort, hydrate=hydrate, top=top)
    lines.append('            --summary-only >> "$GITHUB_STEP_SUMMARY"')
    return "\n".join(lines)
