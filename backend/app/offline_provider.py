"""Offline Mapping and Route Provider for RAAHI.

Zero network dependency. Fulfills the MappingProvider protocol:
- 100% offline local pathfinding (A*, Dijkstra, Yen's, Risk-weighted A*)
- Mode A (Synthetic Demonstration) & Mode B (Genuine Real Road Corridors)
- Local coordinate snapping via SpatialGridIndex
- Local place name geocoding against offline fixtures
- Safe Spot walking routes (replaces public FOSSGIS / Google with local graph!)
- Backup (Tap Me) integration
"""

from __future__ import annotations

import csv
import math
import os
import re
from dataclasses import dataclass
from typing import Any

from .geo import distance_km
from .offline_graph import (
    Edge,
    Node,
    OfflineRoutingGraph,
    build_delhi_real_osm_corridors,
    build_delhi_synthetic_topology,
)
from .pathfinding import PathResult, a_star, generate_candidate_routes
from .raahi_risk_engine import SYNTHETIC_STORE
from .route_decision_engine import DecisionEngineOutput, decide_safe_routes


class OfflineGeocodingDirectory:
    """Local, offline dictionary for resolving common Delhi place names to coordinates."""

    KNOWN_COORDINATES: dict[str, tuple[float, float]] = {
        "connaught place": (28.6329, 77.2195),
        "cp": (28.6329, 77.2195),
        "rajiv chowk": (28.6328, 77.2197),
        "india gate": (28.6129, 77.2295),
        "janpath": (28.6255, 77.2185),
        "mandi house": (28.6258, 77.2345),
        "barakhamba": (28.6280, 77.2260),
        "kartavya path": (28.6130, 77.2170),
        "national museum": (28.6115, 77.2190),
        "rohini sector 23": (28.7325, 77.0572),
        "rohini": (28.7325, 77.0572),
    }

    def __init__(self):
        self.places: dict[str, tuple[float, float]] = dict(self.KNOWN_COORDINATES)
        self._load_fixtures()

    def _load_fixtures(self):
        fixtures_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "fixtures"
        )
        # Load from delhi_safe_spots.csv and delhi_public_places.csv
        for fn in ("delhi_safe_spots.csv", "delhi_public_places.csv"):
            fp = os.path.join(fixtures_dir, fn)
            if not os.path.exists(fp):
                continue
            with open(fp, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    name = (r.get("Name") or r.get("Place Name") or "").strip().lower()
                    lat_str = r.get("Latitude")
                    lon_str = r.get("Longitude")
                    if name and lat_str and lon_str:
                        try:
                            lat = float(lat_str)
                            lon = float(lon_str)
                            if math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90:
                                self.places[name] = (lat, lon)
                        except (ValueError, TypeError):
                            continue

    def resolve(self, text: str) -> tuple[float, float] | None:
        if not text:
            return None
        cleaned = re.sub(r",?\s*(delhi|new delhi|nct of delhi|india|\d{6})\b", "", text.strip(), flags=re.I).strip().lower()
        if cleaned in self.places:
            return self.places[cleaned]
        for name, coords in self.places.items():
            if cleaned in name or name in cleaned:
                return coords
        return None


OFFLINE_GEOCODER = OfflineGeocodingDirectory()


@dataclass
class OfflineMappingProvider:
    """Offline routing engine fulfilling Befikr's MappingProvider protocol."""

    name: str = "offline_ai_decider"
    default_mode: str = "auto"  # "auto", "synthetic", or "real"

    def __init__(self, mode: str = "auto"):
        self.mode = mode
        self.real_graph = build_delhi_real_osm_corridors()
        self.synthetic_graph = build_delhi_synthetic_topology()

    def _determine_mode(
        self,
        origin: str,
        destination: str,
        orig_coords: tuple[float, float] | None,
        dest_coords: tuple[float, float] | None
    ) -> str:
        if self.mode in ("synthetic", "real"):
            return self.mode

        # Real road network is default for all genuine navigation
        text = f"{origin} {destination}".lower()
        if "n000" in text or "rseg0" in text:
            return "synthetic"

        return "real"

    def alternatives(
        self,
        origin: str,
        destination: str,
        origin_coordinates: tuple[float, float] | None = None,
        destination_coordinates: tuple[float, float] | None = None,
        time_band: str = "day",
        context: str | None = None
    ) -> dict[str, Any]:
        """Compute offline routes, evaluate risk, and return decision recommendations."""
        # 1. Resolve coordinates
        orig_coords = origin_coordinates
        if not orig_coords:
            orig_coords = OFFLINE_GEOCODER.resolve(origin)

        dest_coords = destination_coordinates
        if not dest_coords:
            dest_coords = OFFLINE_GEOCODER.resolve(destination)

        # 2. Determine Mode A (Synthetic Demo) vs Mode B (Real Road)
        chosen_mode = self._determine_mode(origin, destination, orig_coords, dest_coords)
        graph = self.synthetic_graph if chosen_mode == "synthetic" else self.real_graph

        if not orig_coords or not dest_coords:
            # Check if origin/destination match graph node IDs directly (e.g. N0001, CP_BLOCK_A)
            start_node_id = origin.strip().upper() if origin.strip().upper() in graph.nodes else None
            dest_node_id = destination.strip().upper() if destination.strip().upper() in graph.nodes else None

            if not start_node_id or not dest_node_id:
                return {
                    "origin": origin,
                    "destination": destination,
                    "provider_state": "demo_only",
                    "provider": self.name,
                    "warning": "Origin or destination is not mapped in the offline road network.",
                    "routes": [{
                        "id": "unmapped-1",
                        "label": f"{origin} → {destination}",
                        "distance_km": None,
                        "minutes": None,
                        "risk_score": None,
                        "confidence": 0,
                        "classification": "insufficient",
                        "navigable": False,
                        "provider": self.name,
                        "geometry": None,
                        "explanation": ["Location is not in the offline road network."]
                    }]
                }
        else:
            # 3. Snap coordinates to nearest traversable nodes
            start_node, _ = graph.snap(orig_coords[0], orig_coords[1], max_distance_km=15.0)
            dest_node, _ = graph.snap(dest_coords[0], dest_coords[1], max_distance_km=15.0)

            if not start_node or not dest_node:
                return {
                    "origin": origin,
                    "destination": destination,
                    "provider_state": "offline_unconnected",
                    "warning": "Could not snap origin or destination to offline road network.",
                    "routes": []
                }
            start_node_id = start_node.id
            dest_node_id = dest_node.id

        # 4. Generate candidate routes via local pathfinding
        risk_lookup = SYNTHETIC_STORE.get_risk_lookup(time_band) if chosen_mode == "synthetic" else {}
        candidate_paths = generate_candidate_routes(
            graph,
            start_node_id,
            dest_node_id,
            risk_lookup=risk_lookup,
            k_alternatives=5
        )

        if not candidate_paths or (len(candidate_paths) == 1 and not candidate_paths[0].edges):
            if orig_coords and dest_coords:
                d_direct = distance_km(orig_coords[0], orig_coords[1], dest_coords[0], dest_coords[1])
                geom = [[orig_coords[1], orig_coords[0]], [dest_coords[1], dest_coords[0]]]
                mins = max(1.0, round(d_direct / 4.5 * 60, 1))
                direct_edge = Edge(
                    id=f"direct_{start_node_id}",
                    start=start_node_id,
                    end=dest_node_id,
                    length_km=round(d_direct, 3),
                    road_type="footway",
                    name="Direct Walking Path",
                    geometry=geom
                )
                candidate_paths = [PathResult(
                    nodes=[start_node_id, dest_node_id],
                    edges=[direct_edge],
                    total_distance_km=round(d_direct, 3),
                    total_minutes=mins,
                    geometry=geom
                )]
            else:
                # If start and target are the same node or disconnected
                fallback_path = a_star(graph, start_node_id, dest_node_id)
                if fallback_path:
                    candidate_paths = [fallback_path]

        # 5. Run Decision Engine (Risk scoring, ranking, explainability)
        decision = decide_safe_routes(
            candidate_paths,
            time_band=time_band,
            mode=chosen_mode,
            max_detour_ratio=1.60,
            include_ml=True
        )

        routes_data = [c.to_dict() for c in decision.candidates]

        # Format compatible with Befikr's frontend expectations
        output: dict[str, Any] = {
            "origin": origin,
            "destination": destination,
            "provider_state": "offline_ai_decider",
            "mode": chosen_mode,
            "time_band": time_band,
            "offline": True,
            "has_reliable_recommendation": decision.has_reliable_recommendation,
            "recommendation_summary": decision.status_message,
            "recommended_route": decision.recommended_route.to_dict() if decision.recommended_route else None,
            "routes": routes_data,
            "warning": (
                "DEMO ONLY: Using synthetic risk scoring model. Not real safety data."
                if chosen_mode == "synthetic"
                else "Real road network: corridors are UNASSESSED / GREY until verified audit feeds are connected."
            ),
            "disclaimer": decision.disclaimer
        }

        # Safe Spot context: add in-app walking route summary
        if context == "safe_spot" and routes_data:
            rec = routes_data[0]
            output["safe_spot_walking"] = {
                "distance_km": rec["distance_km"],
                "minutes": rec["minutes"],
                "geometry": rec["geometry"],
                "steps": [f"Follow {e.name or 'path'} ({e.length_km} km)" for e in candidate_paths[0].edges[:6]] if candidate_paths else []
            }

        return output
