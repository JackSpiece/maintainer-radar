from __future__ import annotations

from typing import Final

from . import __version__


REPORT_EXTENSIONS: Final[dict[str, str]] = {
    "markdown": "md",
    "html": "html",
    "json": "json",
    "csv": "csv",
}

WORKFLOW_SORTS: Final[set[str]] = {"input", "action", "score", "risk", "stale", "number"}
ACTION_REPOSITORY: Final[str] = "JackSpiece/maintainer-radar"


def render_github_action_workflow(
    *,
    report_format: str = "markdown",
    schedule: str = "0 8 * * 1-5",
    limit: int = 50,
    sort: str = "action",
    hydrate: bool = True,
    top: int | None = None,
    config: str | None = None,
    step_summary: bool = True,
    action_ref: str | None = None,
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
    clean_config = (config or "").strip()
    if "\n" in clean_config or "\r" in clean_config:
        raise ValueError("--config must be a single-line path")
    clean_schedule = schedule.strip()
    if not clean_schedule or "\n" in clean_schedule or "\r" in clean_schedule:
        raise ValueError("--schedule must be a single-line cron expression")

    extension = REPORT_EXTENSIONS[report_format]
    output_path = f"maintainer-radar.{extension}"
    artifact_name = f"maintainer-radar-{report_format}"
    action = action_ref or f"{ACTION_REPOSITORY}@v{__version__}"
    top_input = f'          top: "{top}"\n' if top is not None else ""
    escaped_config = clean_config.replace('"', '\\"')
    config_input = f'          config: "{escaped_config}"\n' if clean_config else ""

    escaped_schedule = clean_schedule.replace('"', '\\"')
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
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - name: Build {report_format} report
        id: radar
        uses: {action}
        env:
          GH_TOKEN: ${{{{ github.token }}}}
        with:
          repository: ${{{{ github.repository }}}}
          format: {report_format}
          output: {output_path}
          limit: "{limit}"
          sort: {sort}
{top_input}{config_input}          hydrate: "{str(hydrate).lower()}"
          step-summary: "{str(step_summary).lower()}"
      - uses: actions/upload-artifact@v4
        with:
          name: {artifact_name}
          path: ${{{{ steps.radar.outputs.report-path }}}}
"""
