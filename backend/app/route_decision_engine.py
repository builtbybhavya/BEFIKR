"""Safety-First Route Decision and Recommendation Engine for RAAHI.

Zero network dependency. Implements:
- 5-stage decision pipeline (Connectivity, Evidence, Risk, Practicality, Recommendation)
- Lowest-assessed-risk viable route recommendation
- Clear explainability, comparison metrics, and honest disclaimers
- Safe handling of unassessed corridors ("No route has sufficient evidence...")
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any

from .offline_places import OFFLINE_PLACES
from .pathfinding import PathResult
from .raahi_ml import ML_ENGINE
from .raahi_risk_engine import RouteRiskAssessment, assess_route_segments


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)
    y = math.sin(dlambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - (math.sin(phi1) * math.cos(phi2) * math.cos(dlambda))
    initial_bearing = math.atan2(y, x)
    return (math.degrees(initial_bearing) + 360) % 360


def generate_turn_by_turn_steps(path: PathResult, destination_name: str = "") -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    if not path.edges:
        if path.geometry and len(path.geometry) >= 2:
            steps.append({
                "instruction": f"Head towards {destination_name or 'destination'}",
                "street": "Direct Route",
                "distance_km": path.total_distance_km,
                "distance_m": int(round(path.total_distance_km * 1000)),
                "minutes": path.total_minutes,
                "maneuver": "straight",
                "start_coords": path.geometry[0],
                "end_coords": path.geometry[-1]
            })
            steps.append({
                "instruction": f"Arrive at {destination_name or 'destination'}",
                "street": destination_name or "Destination",
                "distance_km": 0.0,
                "distance_m": 0,
                "minutes": 0.0,
                "maneuver": "arrive",
                "start_coords": path.geometry[-1],
                "end_coords": path.geometry[-1]
            })
        return steps

    prev_bearing: float | None = None
    for i, edge in enumerate(path.edges):
        road_name = edge.name or "pedestrian pathway"
        if road_name.startswith("Connector") or road_name.startswith("osm_"):
            road_name = "connecting walkway"

        coords = edge.geometry
        bearing = None
        if coords and len(coords) >= 2:
            lat1, lon1 = coords[0][1], coords[0][0]
            lat2, lon2 = coords[-1][1], coords[-1][0]
            bearing = calculate_bearing(lat1, lon1, lat2, lon2)

        maneuver = "straight"
        if i == 0:
            instruction = f"Head on {road_name}"
        else:
            if prev_bearing is not None and bearing is not None:
                diff = (bearing - prev_bearing + 180) % 360 - 180
                if 40 < diff <= 135:
                    maneuver = "turn-right"
                    instruction = f"Turn right onto {road_name}"
                elif diff > 135:
                    maneuver = "sharp-right"
                    instruction = f"Make a sharp right onto {road_name}"
                elif -135 <= diff < -40:
                    maneuver = "turn-left"
                    instruction = f"Turn left onto {road_name}"
                elif diff < -135:
                    maneuver = "sharp-left"
                    instruction = f"Make a sharp left onto {road_name}"
                else:
                    maneuver = "straight"
                    instruction = f"Continue straight on {road_name}"
            else:
                instruction = f"Continue on {road_name}"

        prev_bearing = bearing
        mins = round((edge.length_km / 4.5) * 60, 1)
        steps.append({
            "instruction": instruction,
            "street": road_name,
            "distance_km": round(edge.length_km, 3),
            "distance_m": int(round(edge.length_km * 1000)),
            "minutes": mins,
            "maneuver": maneuver,
            "start_coords": coords[0] if coords else None,
            "end_coords": coords[-1] if coords else None
        })

    last_coords = path.geometry[-1] if path.geometry else None
    steps.append({
        "instruction": f"Arrive at {destination_name or 'destination'}",
        "street": destination_name or "Destination",
        "distance_km": 0.0,
        "distance_m": 0,
        "minutes": 0.0,
        "maneuver": "arrive",
        "start_coords": last_coords,
        "end_coords": last_coords
    })
    return steps


@dataclass
class CandidateRouteEvaluation:
    route_id: str
    label: str
    distance_km: float
    duration_minutes: float
    geometry: list[list[float]]  # GeoJSON [[lon, lat], ...]
    risk_assessment: RouteRiskAssessment
    ml_prediction: dict[str, Any] | None = None
    rank: int = 1
    is_recommended: bool = False
    selection_status: str = "ALTERNATIVE"
    tradeoff_explanation: str = ""
    rejection_reason: str | None = None
    comparison_score: float | None = None
    steps: list[dict[str, Any]] = field(default_factory=list)
    nearby_safe_spots: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        geom = self.geometry
        if isinstance(geom, list):
            geom = {"type": "LineString", "coordinates": geom}
        return {
            "id": self.route_id,
            "label": self.label,
            "distance_km": self.distance_km,
            "minutes": self.duration_minutes,
            "geometry": geom,
            "steps": self.steps,
            "nearby_safe_spots": self.nearby_safe_spots,
            "risk_score": self.risk_assessment.route_score,
            "confidence": self.risk_assessment.route_confidence,
            "classification": self.risk_assessment.classification,
            "data_status": self.risk_assessment.data_status,
            "assessed_distance_ratio": self.risk_assessment.assessed_distance_ratio,
            "highest_stretch_score": self.risk_assessment.highest_stretch_score,
            "highest_risk_segment_id": self.risk_assessment.highest_risk_segment_id,
            "influential_factors": self.risk_assessment.influential_factors,
            "explanations": self.risk_assessment.explanations,
            "is_recommended": self.is_recommended,
            "rank": self.rank,
            "selection_status": self.selection_status,
            "tradeoff_explanation": self.tradeoff_explanation,
            "rejection_reason": self.rejection_reason,
            "comparison_score": self.comparison_score,
            "ml_prediction": self.ml_prediction,
            "is_synthetic": self.risk_assessment.is_synthetic,
            "provider": "offline_ai_decider",
            "navigable": True
        }


@dataclass
class DecisionEngineOutput:
    recommended_route: CandidateRouteEvaluation | None
    candidates: list[CandidateRouteEvaluation]
    has_reliable_recommendation: bool
    status_message: str
    mode: str  # "synthetic" (Mode A) or "real" (Mode B)
    time_band: str
    offline_verified: bool = True
    disclaimer: str = (
        "Relative risk estimates based on available offline inputs. "
        "Does not guarantee personal safety."
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "recommended_route": self.recommended_route.to_dict() if self.recommended_route else None,
            "routes": [c.to_dict() for c in self.candidates],
            "has_reliable_recommendation": self.has_reliable_recommendation,
            "status_message": self.status_message,
            "mode": self.mode,
            "time_band": self.time_band,
            "offline_verified": self.offline_verified,
            "disclaimer": self.disclaimer
        }


def decide_safe_routes(
    candidate_paths: list[PathResult],
    time_band: str = "day",
    mode: str = "synthetic",
    max_detour_ratio: float = 1.50,
    include_ml: bool = True
) -> DecisionEngineOutput:
    """Execute the 5-stage safety-first route recommendation engine."""
    tb = time_band.lower()

    # Stage 1: Connectivity validation
    valid_paths = [p for p in candidate_paths if p.nodes and len(p.nodes) >= 2 and p.edges]
    if not valid_paths:
        return DecisionEngineOutput(
            recommended_route=None,
            candidates=[],
            has_reliable_recommendation=False,
            status_message="No traversable route connected in offline graph.",
            mode=mode,
            time_band=tb
        )

    shortest_dist = min(p.total_distance_km for p in valid_paths) or 0.1
    evaluations: list[CandidateRouteEvaluation] = []

    for idx, path in enumerate(valid_paths):
        route_id = f"route_{idx + 1}"
        road_names = [e.name for e in path.edges if e.name and not e.name.startswith("Connector") and not e.name.startswith("osm_")]
        label = f"Option {idx + 1}: Via {road_names[0]}" if road_names else f"Option {idx + 1}"

        # Segment identification and risk evaluation
        segment_ids = path.segment_ids()
        lengths = [e.length_km for e in path.edges]
        risk_ass = assess_route_segments(segment_ids, lengths, time_band=tb, mode=mode)

        # Stage 4: Practicality check
        detour_ratio = path.total_distance_km / shortest_dist
        rejection_reason = None
        if detour_ratio > max_detour_ratio:
            rejection_reason = f"Excessive detour: {detour_ratio:.2f}x of shortest distance exceeds {max_detour_ratio}x limit."

        # Optional ML demo inference for first stretch
        ml_pred = None
        if include_ml and mode == "synthetic" and path.edges:
            first_edge = path.edges[0]
            try:
                ml_pred = ML_ENGINE.predict_segment_risk(
                    length_km=first_edge.length_km,
                    time_band=tb,
                    road_type=first_edge.road_type
                )
            except Exception:
                ml_pred = None

        # Generate turn-by-turn guidance and find nearby safe spots along corridor
        steps = generate_turn_by_turn_steps(path)
        nearby_spots = OFFLINE_PLACES.find_safe_spots_along_route(path.geometry)

        evaluations.append(CandidateRouteEvaluation(
            route_id=route_id,
            label=label,
            distance_km=path.total_distance_km,
            duration_minutes=path.total_minutes,
            geometry=path.geometry,
            risk_assessment=risk_ass,
            ml_prediction=ml_pred,
            rejection_reason=rejection_reason,
            steps=steps,
            nearby_safe_spots=nearby_spots
        ))

    # Stage 2: Evidence validation
    assessed = [e for e in evaluations if e.risk_assessment.classification != "GREY" and e.risk_assessment.route_score is not None]

    if not assessed:
        # All routes are unassessed or insufficient
        for idx, ev in enumerate(evaluations):
            ev.rank = idx + 1
            ev.is_recommended = False
            ev.selection_status = "UNASSESSED_NAVIGABLE"
            ev.tradeoff_explanation = "Route is geographically navigable, but has no verified safety evidence."

        return DecisionEngineOutput(
            recommended_route=None,
            candidates=evaluations,
            has_reliable_recommendation=False,
            status_message="No route has sufficient evidence for a reliable safety recommendation.",
            mode=mode,
            time_band=tb
        )

    # Stage 3 & 4: Risk comparison among viable practical candidates
    viable = [e for e in assessed if not e.rejection_reason]
    if not viable:
        # If all assessed routes exceed detour, fall back to best assessed route
        viable = assessed

    # Rank viable by (route_score ascending, distance_km ascending)
    viable.sort(key=lambda e: (e.risk_assessment.route_score or 999.0, e.distance_km))

    # Choose lowest assessed risk viable route
    best = viable[0]
    best.is_recommended = True
    best.rank = 1
    best.selection_status = "RECOMMENDED"

    dist_diff_pct = ((best.distance_km - shortest_dist) / shortest_dist) * 100.0
    if dist_diff_pct > 2.0:
        best.tradeoff_explanation = (
            f"Recommended for lowest assessed risk ({best.risk_assessment.route_score:.1f} [{best.risk_assessment.classification}]), "
            f"despite being {dist_diff_pct:.1f}% longer than the most direct path."
        )
    else:
        best.tradeoff_explanation = (
            f"Recommended route: lowest assessed risk ({best.risk_assessment.route_score:.1f} [{best.risk_assessment.classification}]) "
            f"with near-optimal walking distance."
        )

    # Rank remaining candidates
    current_rank = 2
    for ev in evaluations:
        if ev.route_id == best.route_id:
            continue
        ev.rank = current_rank
        current_rank += 1
        if ev.rejection_reason:
            ev.selection_status = "REJECTED_DETOUR"
            ev.tradeoff_explanation = ev.rejection_reason
        elif ev.risk_assessment.classification == "GREY":
            ev.selection_status = "UNASSESSED_ALTERNATIVE"
            ev.tradeoff_explanation = "Insufficient evidence to determine relative safety."
        else:
            diff_score = (ev.risk_assessment.route_score or 0) - (best.risk_assessment.route_score or 0)
            ev.selection_status = "ALTERNATIVE"
            ev.tradeoff_explanation = (
                f"Assessed risk is {diff_score:+.1f} points higher than the recommended route."
            )

    # Sort final candidates by rank
    evaluations.sort(key=lambda e: e.rank)

    return DecisionEngineOutput(
        recommended_route=best,
        candidates=evaluations,
        has_reliable_recommendation=True,
        status_message=f"Recommended lowest assessed risk route: {best.label} (Risk: {best.risk_assessment.route_score:.1f})",
        mode=mode,
        time_band=tb
    )
