"""Offline Places Index and Search Feature for RAAHI and Safe Spot.

Zero network dependency. Provides:
- Offline place search & autocomplete for selecting pickup and drop locations
- Offline place coordinate resolution
- Nearest police station and safe spot discovery with safety-evaluated routes
- No external Google Places or Google Maps API dependency.
"""

from __future__ import annotations

import csv
import math
import os
import re
from dataclasses import dataclass, field
from typing import Any

from .geo import distance_km


@dataclass
class OfflinePlace:
    id: str
    name: str
    category: str  # police, hospital, park, public_space, restaurant, cafe, transit, etc.
    address: str
    latitude: float
    longitude: float
    tags: dict[str, str] = field(default_factory=dict)


class OfflinePlaceDirectory:
    """Manages offline place datasets for zero-network autocomplete and search."""

    def __init__(self):
        self.places: list[OfflinePlace] = []
        self.places_by_id: dict[str, OfflinePlace] = {}
        self.fixtures_dir = os.getenv(
            "BEFIKR_FIXTURES_DIR",
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "fixtures"
            )
        )
        self._load_all()

    def _load_all(self):
        # 1. Real Central Delhi Landmarks
        landmarks = [
            ("CP_RAJIV_CHOWK", "Rajiv Chowk Central Park", "public_space", "Connaught Place, Central Park, New Delhi", 28.6328, 77.2197),
            ("CP_BLOCK_A", "Connaught Place Block A", "commercial", "Connaught Place Inner Circle, New Delhi", 28.6329, 77.2195),
            ("CP_BLOCK_B", "Connaught Place Block B", "commercial", "Connaught Place Inner Circle, New Delhi", 28.6335, 77.2210),
            ("CP_BLOCK_C", "Connaught Place Block C", "commercial", "Connaught Place Inner Circle, New Delhi", 28.6325, 77.2225),
            ("CP_BLOCK_E", "Connaught Place Block E", "commercial", "Connaught Place Inner Circle, New Delhi", 28.6300, 77.2205),
            ("JANPATH_MARKET", "Janpath Tibetan Market", "public_space", "Janpath Road, Connaught Place, New Delhi", 28.6255, 77.2185),
            ("INDIA_GATE", "India Gate War Memorial", "monument", "Kartavya Path, India Gate, New Delhi", 28.6129, 77.2295),
            ("MANDI_HOUSE", "Mandi House Cultural Hub", "public_space", "Copernicus Marg, Mandi House, New Delhi", 28.6258, 77.2345),
            ("BARAKHAMBA_RD", "Barakhamba Road Metro", "transit", "Barakhamba Road, Connaught Place, New Delhi", 28.6280, 77.2260),
            ("NATIONAL_MUSEUM", "National Museum New Delhi", "monument", "Janpath & Maulana Azad Road, New Delhi", 28.6115, 77.2190),
            ("WINDSOR_PLACE", "Windsor Place", "public_space", "Ashoka Road & Janpath Crossing, New Delhi", 28.6210, 77.2175),
            ("ROHINI_SEC_23", "Rohini Sector 23", "residential", "Rohini Sector 23, North West Delhi", 28.7325, 77.0572),
            ("ROHINI_SEC_24", "Rohini Sector 24", "residential", "Rohini Sector 24, North West Delhi", 28.7350, 77.0600),
            ("ROHINI_SEC_22", "Rohini Sector 22", "residential", "Rohini Sector 22, North West Delhi", 28.7280, 77.0540),
        ]
        for pid, name, cat, addr, lat, lon in landmarks:
            self._add_place(OfflinePlace(id=f"off_lm_{pid.lower()}", name=name, category=cat, address=addr, latitude=lat, longitude=lon))

        # 2. delhi_safe_spots.csv
        p1 = os.path.join(self.fixtures_dir, "delhi_safe_spots.csv")
        if os.path.exists(p1):
            with open(p1, encoding="utf-8-sig") as f:
                for idx, r in enumerate(csv.DictReader(f)):
                    name = (r.get("Name") or "").strip()
                    lat_s = r.get("Latitude")
                    lon_s = r.get("Longitude")
                    cat = self._normalize_category(r.get("Category", "safe_spot"))
                    addr = (r.get("Address") or "").strip()
                    if name and lat_s and lon_s:
                        try:
                            lat = float(lat_s)
                            lon = float(lon_s)
                            if math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90:
                                self._add_place(OfflinePlace(
                                    id=f"off_ss_{idx + 1}",
                                    name=name,
                                    category=cat,
                                    address=addr or f"{name}, Delhi",
                                    latitude=lat,
                                    longitude=lon,
                                    tags={"phone": r.get("Phone", ""), "source": "safe_spots"}
                                ))
                        except (ValueError, TypeError):
                            continue

        # 3. delhi_public_places.csv
        p2 = os.path.join(self.fixtures_dir, "delhi_public_places.csv")
        if os.path.exists(p2):
            with open(p2, encoding="utf-8-sig") as f:
                for idx, r in enumerate(csv.DictReader(f)):
                    name = (r.get("Place Name") or "").strip()
                    lat_s = r.get("Latitude")
                    lon_s = r.get("Longitude")
                    cat = self._normalize_category(r.get("Category", "public_space"))
                    addr = (r.get("Area / Locality") or r.get("City") or "").strip()
                    if name and lat_s and lon_s:
                        try:
                            lat = float(lat_s)
                            lon = float(lon_s)
                            if math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90:
                                self._add_place(OfflinePlace(
                                    id=f"off_pub_{idx + 1}",
                                    name=name,
                                    category=cat,
                                    address=addr or f"{name}, Delhi",
                                    latitude=lat,
                                    longitude=lon,
                                    tags={"source": "public_places"}
                                ))
                        except (ValueError, TypeError):
                            continue

        # 4. delhi_safe_spots_additional.csv
        p3 = os.path.join(self.fixtures_dir, "delhi_safe_spots_additional.csv")
        if os.path.exists(p3):
            with open(p3, encoding="utf-8-sig") as f:
                for idx, r in enumerate(csv.DictReader(f)):
                    name = (r.get("Name") or r.get("Place Name") or "").strip()
                    lat_s = r.get("Latitude")
                    lon_s = r.get("Longitude")
                    cat = self._normalize_category(r.get("Category", "safe_spot"))
                    addr = (r.get("Address") or r.get("Area / Locality") or "").strip()
                    if name and lat_s and lon_s:
                        try:
                            lat = float(lat_s)
                            lon = float(lon_s)
                            if math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90:
                                self._add_place(OfflinePlace(
                                    id=f"off_add_{idx + 1}",
                                    name=name,
                                    category=cat,
                                    address=addr or f"{name}, Delhi",
                                    latitude=lat,
                                    longitude=lon,
                                    tags={"source": "additional"}
                                ))
                        except (ValueError, TypeError):
                            continue

        # 5. Synthetic road sectors from road_network.csv
        p4 = os.path.join(self.fixtures_dir, "raahi_synthetic", "road_network.csv")
        if os.path.exists(p4):
            with open(p4, encoding="utf-8") as f:
                seen_areas = set()
                for r in csv.DictReader(f):
                    area = (r.get("area") or "").strip()
                    road_name = (r.get("road_name") or "").strip()
                    lat_s = r.get("start_lat")
                    lon_s = r.get("start_lon")
                    if area and area not in seen_areas and lat_s and lon_s:
                        seen_areas.add(area)
                        self._add_place(OfflinePlace(
                            id=f"off_syn_{len(seen_areas)}",
                            name=area,
                            category="residential",
                            address=f"{area}, Rohini, Delhi",
                            latitude=float(lat_s),
                            longitude=float(lon_s),
                            tags={"is_synthetic": "true"}
                        ))

        # 6. Load verified places from web/data/offline_data.json if present
        data_json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web", "data", "offline_data.json")
        if not os.path.exists(data_json_path):
            data_json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "web", "data", "offline_data.json")
        if os.path.exists(data_json_path):
            try:
                import json
                with open(data_json_path, "r", encoding="utf-8") as f:
                    dj = json.load(f)
                    for p in dj.get("places", []):
                        pid = p.get("id") or f"off_verified_{len(self.places)}"
                        name = p.get("name") or p.get("label") or ""
                        cat = p.get("category") or "public_space"
                        addr = p.get("address") or f"{name}, Delhi"
                        lat = float(p.get("latitude", 28.6))
                        lon = float(p.get("longitude", 77.2))
                        if name and pid not in self.places_by_id:
                            self._add_place(OfflinePlace(id=pid, name=name, category=cat, address=addr, latitude=lat, longitude=lon))
            except Exception:
                pass

    def _normalize_category(self, raw_cat: str) -> str:
        c = (raw_cat or "").lower().strip()
        if "police" in c:
            return "police"
        if "hospital" in c or "clinic" in c or "health" in c:
            return "hospital"
        if "park" in c or "garden" in c:
            return "park"
        if "cafe" in c or "coffee" in c:
            return "cafe"
        if "restaurant" in c or "food" in c:
            return "restaurant"
        return "public_space"

    def _add_place(self, place: OfflinePlace):
        # Avoid duplicate coordinate names
        key = (place.name.lower(), round(place.latitude, 4), round(place.longitude, 4))
        for existing in self.places:
            if (existing.name.lower(), round(existing.latitude, 4), round(existing.longitude, 4)) == key:
                return
        self.places.append(place)
        self.places_by_id[place.id] = place

    def autocomplete(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search offline places for pickup/drop location selection."""
        q = (query or "").strip().lower()
        if not q or len(q) < 1:
            return []

        words = q.split()
        matches: list[tuple[int, OfflinePlace]] = []

        for p in self.places:
            target = f"{p.name} {p.address} {p.category}".lower()
            if not all(w in target for w in words):
                continue

            # Compute match score (exact prefix > word start > substring)
            p_name_lower = p.name.lower()
            if p_name_lower == q:
                priority = 0
            elif p_name_lower.startswith(q):
                priority = 1
            elif any(w.startswith(q) for w in p_name_lower.split()):
                priority = 2
            elif q in p_name_lower:
                priority = 3
            else:
                priority = 4

            matches.append((priority, p))

        matches.sort(key=lambda item: (item[0], item[1].name))

        suggestions = []
        for _, p in matches[:limit]:
            label = f"{p.name}, {p.address}" if p.address and p.address not in p.name else p.name
            suggestions.append({
                "place_id": p.id,
                "label": label,
                "name": p.name,
                "address": p.address,
                "category": p.category,
                "latitude": p.latitude,
                "longitude": p.longitude
            })

        return suggestions

    def resolve(self, place_id: str) -> dict[str, Any] | None:
        """Resolve a place_id to geographic coordinates and formatted address offline."""
        p = self.places_by_id.get(place_id)
        if not p:
            # Fallback search by ID or name
            for candidate in self.places:
                if candidate.id == place_id or candidate.name.lower() == place_id.lower():
                    p = candidate
                    break
        if not p:
            return None

        return {
            "place_id": p.id,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "address": p.address or p.name,
            "name": p.name,
            "category": p.category,
            "attributions": []
        }

    def find_nearest_safe_spot(
        self,
        latitude: float,
        longitude: float,
        preferred_category: str = "police"
    ) -> tuple[OfflinePlace | None, float]:
        """Find the nearest police station or safe spot to a user's location."""
        candidates = [p for p in self.places if p.category == preferred_category]
        if not candidates:
            # Fallback to hospital or any safe spot
            candidates = [p for p in self.places if p.category in ("police", "hospital", "safe_spot")]
        if not candidates:
            candidates = self.places

        best_place: OfflinePlace | None = None
        min_dist = math.inf

        for p in candidates:
            d = distance_km(latitude, longitude, p.latitude, p.longitude)
            if d < min_dist:
                min_dist = d
                best_place = p

        return best_place, round(min_dist, 3)

    def find_safe_spots_along_route(
        self,
        coordinates: list[list[float]],
        max_distance_km: float = 1.0,
        limit: int = 10
    ) -> list[dict[str, Any]]:
        """Find safe spots (police, hospital, verified havens) along a route corridor."""
        if not coordinates:
            return []

        # Target safe categories first
        safe_places = [
            p for p in self.places
            if p.category in ("police", "hospital", "safe_spot", "public_space")
        ]
        if not safe_places:
            safe_places = self.places

        results = []
        for p in safe_places:
            min_d = math.inf
            best_idx = 0
            for idx, pt in enumerate(coordinates):
                # pt is [lon, lat]
                d = distance_km(pt[1], pt[0], p.latitude, p.longitude)
                if d < min_d:
                    min_d = d
                    best_idx = idx

            if min_d <= max_distance_km:
                results.append((best_idx, min_d, p))

        # If none within max_distance_km, include the closest few
        if not results and safe_places:
            all_distances = []
            for p in safe_places:
                min_d = min(distance_km(pt[1], pt[0], p.latitude, p.longitude) for pt in coordinates)
                all_distances.append((min_d, p))
            all_distances.sort(key=lambda x: x[0])
            for d, p in all_distances[:limit]:
                results.append((0, d, p))

        # Sort by route waypoint index (order encountered along path)
        results.sort(key=lambda x: (x[0], x[1]))

        output = []
        seen_ids = set()
        for best_idx, dist, p in results[:limit]:
            if p.id in seen_ids:
                continue
            seen_ids.add(p.id)
            output.append({
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "address": p.address,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "distance_km": round(dist, 2),
                "distance_m": int(round(dist * 1000)),
                "waypoint_index": best_idx
            })
        return output


# Global singleton directory
OFFLINE_PLACES = OfflinePlaceDirectory()
