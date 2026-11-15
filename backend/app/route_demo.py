"""User-supplied synthetic area-pair examples, separate from live route risk."""

from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
import unicodedata
from typing import Any

DATASET_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "delhi_synthetic_route_safety_dataset.json"
DATA_STATUS = "SYNTHETIC_DEMO_NOT_REAL_INCIDENT_OR_POLICE_DATA"
TIME_WINDOWS = {"Day": "06:00-18:00", "Evening": "18:00-22:00", "Night": "22:00-06:00"}
IST = timezone(timedelta(hours=5, minutes=30), name="Asia/Kolkata")
NOTICE = (
    "Synthetic demo data supplied for Raahi, not real incident or police data. "
    "Colours describe a named area pair and time band, not individual roads or Google Maps alternatives. "
    "Higher scores mean higher synthetic safety, not a guarantee of safety."
)
UNAVAILABLE_NOTICE = "The synthetic demo dataset is unavailable. No safety colour has been assigned."


def _normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def _area_name(value: str, known: set[str]) -> str | None:
    """Match a complete area name, optionally followed only by Delhi/India suffixes."""
    normalized = _normalize(value)
    if normalized in known:
        return normalized
    parts = [part.strip() for part in normalized.split(",")]
    if len(parts) < 2 or parts[0] not in known:
        return None
    for part in parts[1:]:
        if not re.fullmatch(r"(?:delhi|new delhi|nct of delhi|india)(?:\s+\d{6})?", part):
            return None
    return parts[0]


def read_dataset(path: Path | None = None) -> list[dict[str, Any]]:
    """Validate every record before exposing any demo result; never repair or invent labels."""
    records = json.loads(Path(path or DATASET_PATH).read_text(encoding="utf-8-sig"))
    if not isinstance(records, list) or not records:
        raise ValueError("Expected a non-empty list of synthetic route records")
    score_keys = ("safety_score_synthetic_0_100", "lighting_index_synthetic_0_100",
                  "pedestrian_activity_index_synthetic_0_100", "cctv_coverage_index_synthetic_0_100")
    required = {"route_segment_id", "from_area", "to_area", "distance_km_synthetic", "time_band",
                "time_window", "duration_minutes_synthetic", "safety_label", "synthetic_incident_signal_count",
                "data_status", *score_keys}
    seen: set[tuple[str, str, str]] = set()
    id_pairs: dict[str, tuple[str, str]] = {}
    pair_ids: dict[tuple[str, str], str] = {}
    pair_bands: dict[tuple[str, str], set[str]] = {}
    for record in records:
        if not isinstance(record, dict) or not required.issubset(record):
            raise ValueError("A synthetic route record is incomplete")
        if any(not isinstance(record[key], str) or not record[key].strip()
               for key in ("route_segment_id", "from_area", "to_area", "time_band", "time_window", "safety_label", "data_status")):
            raise ValueError("Synthetic route names and labels must be non-empty text")
        if record["data_status"] != DATA_STATUS or record["safety_label"] not in {"GREEN", "YELLOW", "RED"}:
            raise ValueError("Unsupported synthetic data status or colour")
        band = record["time_band"]
        if band not in TIME_WINDOWS or record["time_window"] != TIME_WINDOWS[band]:
            raise ValueError("Unsupported synthetic time band")
        for key in (*score_keys, "distance_km_synthetic", "duration_minutes_synthetic", "synthetic_incident_signal_count"):
            value = record[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError("Synthetic numeric values must be finite numbers")
            if key in score_keys and not 0 <= value <= 100:
                raise ValueError("Synthetic score/index must be in 0-100")
            if key in {"distance_km_synthetic", "duration_minutes_synthetic"} and value <= 0:
                raise ValueError("Synthetic distance and duration must be positive")
        incident_count = record["synthetic_incident_signal_count"]
        if not isinstance(incident_count, int) or incident_count < 0:
            raise ValueError("Synthetic incident count must be a non-negative integer")
        pair = (_normalize(record["from_area"]), _normalize(record["to_area"]))
        key = (*pair, band)
        segment_id = record["route_segment_id"]
        if pair[0] == pair[1] or key in seen:
            raise ValueError("Duplicate or invalid synthetic route pair")
        if (segment_id in id_pairs and id_pairs[segment_id] != pair) or (pair in pair_ids and pair_ids[pair] != segment_id):
            raise ValueError("Synthetic route identifiers do not match area pairs")
        seen.add(key)
        id_pairs[segment_id] = pair
        pair_ids[pair] = segment_id
        pair_bands.setdefault(pair, set()).add(band)
    if any(bands != set(TIME_WINDOWS) for bands in pair_bands.values()):
        raise ValueError("Every synthetic route pair must include all three time bands")
    return records


def resolve_time_band(time_band: str = "current", at: datetime | None = None) -> tuple[str, str]:
    if time_band == "current":
        instant = at or datetime.now(timezone.utc)
        if instant.tzinfo is None:
            raise ValueError("Current time must include a timezone")
        hour = instant.astimezone(IST).hour
        time_band = "Day" if 6 <= hour < 18 else "Evening" if 18 <= hour < 22 else "Night"
    if time_band not in TIME_WINDOWS:
        raise ValueError("Select current, Day, Evening or Night")
    return time_band, TIME_WINDOWS[time_band]


def demo_catalog(path: Path | None = None) -> dict[str, Any]:
    catalog: dict[str, Any] = {
        "source": "synthetic_demo", "available": False, "notice": UNAVAILABLE_NOTICE,
        "route_pairs": [], "time_bands": [{"name": name, "time_window": window} for name, window in TIME_WINDOWS.items()],
        "counts": {"rows": 0, "route_pairs": 0, "labels": {"GREEN": 0, "YELLOW": 0, "RED": 0}},
    }
    try:
        records = read_dataset(path)
    except (OSError, ValueError, TypeError):
        return catalog
    pairs = {row["route_segment_id"]: {key: row[key] for key in ("route_segment_id", "from_area", "to_area")}
             for row in records}
    catalog.update(available=True, notice=NOTICE, route_pairs=list(pairs.values()))
    catalog["counts"] = {"rows": len(records), "route_pairs": len(pairs),
                         "labels": {label: sum(row["safety_label"] == label for row in records)
                                    for label in ("GREEN", "YELLOW", "RED")}}
    return catalog


def demo_lookup(origin: str, destination: str, time_band: str = "current", *,
                at: datetime | None = None, path: Path | None = None) -> dict[str, Any]:
    band, window = resolve_time_band(time_band, at)
    result: dict[str, Any] = {
        "source": "synthetic_demo", "available": False, "matched": False,
        "notice": UNAVAILABLE_NOTICE, "time_band": band, "time_window": window, "record": None,
    }
    try:
        records = read_dataset(path)
    except (OSError, ValueError, TypeError):
        return result
    result.update(available=True, notice=NOTICE)
    known = {_normalize(row[key]) for row in records for key in ("from_area", "to_area")}
    start, end = _area_name(origin, known), _area_name(destination, known)
    for row in records:
        if start == _normalize(row["from_area"]) and end == _normalize(row["to_area"]) and band == row["time_band"]:
            result.update(matched=True, record=dict(row))
            break
    return result
