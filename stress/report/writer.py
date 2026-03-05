from __future__ import annotations

import json
from pathlib import Path
from dataclasses import is_dataclass, asdict
from enum import Enum
from typing import Any, Dict

from OCRB.report.schema import RunRecord, AggregateSummary, to_dict


def _jsonify(obj: Any) -> Any:
    """
    Convert dataclasses/enums/paths into JSON-serializable primitives.
    """
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, dict):
        return {str(k): _jsonify(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonify(x) for x in obj]
    return obj


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_jsonify(data), indent=2, sort_keys=True))


def write_manifest(out_dir: str, manifest: Any) -> Path:
    """
    Accepts either:
      - a dict
      - a dataclass (RunManifest)
    """
    out = Path(out_dir)
    path = out / "manifest.json"
    _write_json(path, _jsonify(manifest) if not isinstance(manifest, dict) else manifest)
    return path


def write_run_record(out_dir: str, idx: int, record: RunRecord) -> Path:
    out = Path(out_dir)
    path = out / "runs" / f"run_{idx:02d}.json"
    _write_json(path, to_dict(record))
    return path


def write_aggregate_summary(out_dir: str, summary: AggregateSummary) -> Path:
    out = Path(out_dir)
    path = out / "aggregate_summary.json"
    _write_json(path, to_dict(summary))
    return path


def write_disclosure(out_dir: str, disclosure_text: str) -> Path:
    out = Path(out_dir)
    path = out / "disclosure.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(disclosure_text.strip() + "\n")
    return path
