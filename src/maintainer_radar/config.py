from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "large_diff_lines": 500,
    "very_large_diff_lines": 1500,
    "large_file_count": 10,
    "very_large_file_count": 25,
    "quiet_days": 7,
    "stale_days": 14,
    "test_hints": [],
    "doc_hints": [],
    "generated_hints": [],
}


def load_config(path: str | None = None) -> dict[str, Any]:
    config = dict(DEFAULT_CONFIG)
    config_path = Path(path) if path else Path(".maintainer-radar.json")
    if not config_path.exists():
        return config

    with config_path.open("r", encoding="utf-8") as fh:
        loaded = json.load(fh)
    if not isinstance(loaded, dict):
        raise ValueError("Config file must contain a JSON object")

    for key, value in loaded.items():
        if key not in DEFAULT_CONFIG:
            raise ValueError(f"Unknown config key: {key}")
        if key.endswith("_hints"):
            config[key] = _string_list(value, key)
        else:
            config[key] = _positive_int(value, key)
    return config


def _positive_int(value: Any, key: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Config key {key} must be an integer") from exc
    if parsed < 0:
        raise ValueError(f"Config key {key} must be non-negative")
    return parsed


def _string_list(value: Any, key: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"Config key {key} must be a list of strings")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"Config key {key} must be a list of strings")
        normalized = item.strip().lower()
        if normalized:
            result.append(normalized)
    return result

