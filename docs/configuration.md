# Configuration

Maintainer Radar can read project-specific thresholds from
`.maintainer-radar.json` in the current directory.

Use `--config path/to/config.json` to load a different file.

## Example

```json
{
  "large_diff_lines": 500,
  "very_large_diff_lines": 1500,
  "large_file_count": 10,
  "very_large_file_count": 25,
  "quiet_days": 7,
  "stale_days": 14,
  "test_hints": ["specs/"],
  "doc_hints": ["guides/"],
  "generated_hints": ["snapshots/"]
}
```

## Fields

| Field | Default | Meaning |
| --- | ---: | --- |
| `large_diff_lines` | 500 | Diff line count that adds a `large diff` flag |
| `very_large_diff_lines` | 1500 | Diff line count that adds a `very large diff` flag |
| `large_file_count` | 10 | Changed file count that adds a `large diff` flag |
| `very_large_file_count` | 25 | Changed file count that adds a `very large diff` flag |
| `quiet_days` | 7 | Days without updates before a `quiet N days` flag |
| `stale_days` | 14 | Days without updates before a `stale N days` flag |
| `test_hints` | `[]` | Extra lowercase path fragments that count as tests |
| `doc_hints` | `[]` | Extra lowercase path fragments that count as docs |
| `generated_hints` | `[]` | Extra lowercase path fragments that count as generated files |

Unknown keys fail fast so configuration mistakes do not silently change scoring.

## Usage

```bash
maintainer-radar repo owner/repo --config .maintainer-radar.json
maintainer-radar from-json queue.json --config strict-config.json
```

