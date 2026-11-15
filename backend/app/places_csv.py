"""Radius search of the user-provided Delhi places CSV without external services."""

import csv
import math
from pathlib import Path
import re

from .geo import distance_km

DATASET_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "delhi_safe_spots.csv"
ADDITIONAL_PATHS = (DATASET_PATH.with_name("delhi_safe_spots_additional.csv"),
                    DATASET_PATH.with_name("delhi_public_places.csv"))
CATEGORIES = {"Police Station": "police", "Hospital": "hospital", "Cafe": "cafe",
              "Restaurant": "restaurant", "Park": "park", "Public Space": "public_space",
              "Crowded Place": "public_space", "Crowded Area / Market": "public_space",
              "Monument": "public_space"}
NOTICE = ("Nearby places within the chosen radius, nearest first. "
          "Distances are straight-line estimates. Listings and current availability are unverified.")


def read_place_rows(path: Path) -> list[dict]:
    """Read original and additional CSV layouts without rewriting the supplied files."""
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        columns = set(reader.fieldnames or [])
        required = {"ID", "Category", "Sub_Category", "Name", "Address", "District_Area",
                    "Latitude", "Longitude", "Phone", "Notes", "Confidence", "Source"}
        if required.issubset(columns):
            return list(reader)
        simple = {"Category", "Name", "Address", "Latitude", "Longitude", "Google Maps Link"}
        public = {"Category", "Place Name", "Area / Locality", "City", "Place Type",
                  "Latitude", "Longitude", "Google_Maps_Link"}
        if not (simple.issubset(columns) or public.issubset(columns)):
            raise ValueError("Unsupported places CSV columns")
        rows = []
        for number, raw in enumerate(reader, 1):
            if None in raw or any(value is None for value in raw.values()):
                raise ValueError("Incomplete places CSV row")
            expanded = public.issubset(columns)
            rows.append({
                "ID": f"{path.stem}-{number}", "Category": raw["Category"],
                "Sub_Category": raw["Place Type"] if expanded else raw["Category"],
                "Name": raw["Place Name"] if expanded else raw["Name"],
                "Address": ", ".join(filter(None, [raw["Area / Locality"], raw["City"]])) if expanded else raw["Address"],
                "District_Area": raw["Area / Locality"] if expanded else "",
                "Latitude": raw["Latitude"], "Longitude": raw["Longitude"],
                "Phone": "", "Notes": "", "Confidence": "",
                "Source": raw["Google_Maps_Link"] if expanded else raw["Google Maps Link"],
            })
        return rows


def place_identity(name: str) -> str:
    key = re.sub(r"[^a-z0-9]", "", name.casefold())
    # Explicit name variants only: retain branch and locality qualifiers on other names.
    return {"redfortlalqila": "redfort", "chandnichowkmarket": "chandnichowk",
            "connaughtplacerajivchowk": "connaughtplace",
            "selectcitywalknexus": "selectcitywalk", "lodigardens": "lodhigarden",
            "centralparkconnaughtplace": "centralpark"}.get(key, key)


def nearby_csv_places(latitude: float, longitude: float, radius_km: float = 5,
                      category: str | None = None, *, path: Path | None = None) -> dict:
    distance_km(latitude, longitude, latitude, longitude)
    if not math.isfinite(radius_km) or radius_km <= 0:
        raise ValueError("Radius must be a positive finite number")
    result = {"places": [], "source_state": "csv_dataset", "csv_count": 0,
              "google_count": 0, "managed_count": 0, "attribution": None,
              "radius_km": radius_km, "distance_method": "haversine_straight_line",
              "message": NOTICE, "empty_message": "No matching places are within this radius.",
              "dataset_total": 0, "dataset_usable": 0, "skipped_coordinates": 0,
              "skipped_records": 0, "duplicate_count": 0}
    try:
        sources = (Path(path),) if path is not None else (DATASET_PATH, *ADDITIONAL_PATHS)
        rows = [row for source in sources for row in read_place_rows(source)]
    except (OSError, ValueError, csv.Error):
        result.update(source_state="csv_dataset_unavailable", message="Nearby places could not be loaded.",
                      empty_message="Nearby listings are unavailable. Try again.")
        return result
    result["dataset_total"] = len(rows)
    nearby = []
    seen = set()
    for row in rows:
        try:
            lat, lon = float(row["Latitude"]), float(row["Longitude"])
            distance = distance_km(latitude, longitude, lat, lon)
        except (TypeError, ValueError):
            result["skipped_coordinates"] += 1
            continue
        mapped = CATEGORIES.get(row["Category"])
        if not mapped or not row["ID"] or row["ID"] in seen or not (row["Name"] or "").strip() or None in row:
            result["skipped_records"] += 1
            continue
        seen.add(row["ID"])
        result["dataset_usable"] += 1
        if distance > radius_km or (category and category != mapped):
            continue
        phone = (row["Phone"] or "").strip()
        if phone.upper() in {"NA", "N/A", "NONE", "NULL", "-"}:
            phone = ""
        source = row["Source"] or ""
        link = re.search(r"https?://[^\s<>)]+", source)
        item = {"id": f"csv-{row['ID']}", "name": row["Name"], "category": mapped,
                "category_label": row["Category"], "sub_category": row["Sub_Category"],
                "address": row["Address"], "district_area": row["District_Area"],
                "latitude": lat, "longitude": lon, "phone": phone,
                "notes": row["Notes"], "confidence": row["Confidence"],
                "source": source, "source_url": link.group(0) if link else None,
                "source_kind": "user_csv", "verified_at": None,
                "distance_km": round(distance, 3)}
        nearby.append((distance, item))
    unique = []
    identities: dict[str, list[dict]] = {}
    for _, item in sorted(nearby, key=lambda entry: entry[0]):
        key = place_identity(item["name"])
        duplicates = identities.get(key, [])
        if any(distance_km(item["latitude"], item["longitude"], other["latitude"], other["longitude"]) <= 0.25
               for other in duplicates):
            result["duplicate_count"] += 1
            continue
        identities.setdefault(key, []).append(item)
        unique.append(item)
    result["places"] = unique
    result["csv_count"] = len(unique)
    return result
