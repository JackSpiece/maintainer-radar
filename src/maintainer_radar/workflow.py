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
    command_lines = [
        '          maintainer-radar repo "${{ github.repository }}" \\',
        f"            --limit {limit} \\",
    ]
    if hydrate:
        command_lines.append("            --hydrate \\")
    command_lines.extend(
        [
            f"            --sort {sort} \\",
        ]
    )
    if top is not None:
        command_lines.append(f"            --top {top} \\")
    command_lines.extend(
        [
            f"            --format {report_format} \\",
            f"            > {output_path}",
        ]
    )

    escaped_schedule = clean_schedule.replace('"', '\\"')
    command = "\n".join(command_lines)
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
"""
