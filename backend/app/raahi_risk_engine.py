"""Exact Safety Risk Scoring and Evaluation Engine for RAAHI.

Zero network dependency. Implements:
- 7 weighted parameters from raahi_config.json (sum = 0.90)
- Segment scoring, coverage, confidence (with corroboration)
- GREEN / YELLOW / RED / GREY classifications
- Whole-route length-weighted scoring and peak-stretch penalty
- Time-dependent analysis (morning, day, evening, night)
- Strict Mode A (Synthetic Demonstration) vs Mode B (Real Road Routing) data isolation
- CCTV supporting evidence (not included in the 7 weighted inputs)
"""

from __future__ import annotations

import csv
import math
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from . import db

# Exact weights from raahi_config.json (sum = 0.90)
RISK_WEIGHTS: dict[str, float] = {
    "incident_risk": 0.25,
    "report_freshness": 0.15,
    "population_foot_traffic_risk": 0.10,
    "lighting_risk": 0.10,
    "time_of_day_risk": 0.10,
    "historical_risk": 0.10,
    "isolation_risk": 0.10
}
TOTAL_WEIGHT_SUM: float = sum(RISK_WEIGHTS.values())  # 0.90


@dataclass
class SegmentRiskAssessment:
    segment_id: str
    score: float | None
    confidence: int
    coverage: float
    corroboration: float
    classification: str  # GREEN, YELLOW, RED, GREY
    data_status: str  # SCORED, INSUFFICIENT, UNASSESSED
    length_km: float
    time_band: str
    available_inputs: dict[str, float] = field(default_factory=dict)
    missing_inputs: list[str] = field(default_factory=list)
    supporting_evidence: dict[str, Any] = field(default_factory=dict)
    explanations: list[str] = field(default_factory=list)
    is_synthetic: bool = False


@dataclass
class RouteRiskAssessment:
    route_score: float | None
    route_confidence: int
    classification: str  # GREEN, YELLOW, RED, GREY
    data_status: str  # SCORED, INSUFFICIENT, UNASSESSED
    total_length_km: float
    assessed_length_km: float
    assessed_distance_ratio: float
    scored_stretch_count: int
    length_weighted_average: float | None
    highest_stretch_score: float | None
    highest_risk_segment_id: str | None
    segment_assessments: list[SegmentRiskAssessment] = field(default_factory=list)
    influential_factors: list[str] = field(default_factory=list)
    explanations: list[str] = field(default_factory=list)
    is_synthetic: bool = False


def calculate_segment_score(
    inputs: dict[str, float | None],
    length_km: float = 0.5,
    corroboration: float = 0.0,
    segment_id: str = "SEG",
    time_band: str = "day",
    supporting_evidence: dict[str, Any] | None = None,
    is_synthetic: bool = False
) -> SegmentRiskAssessment:
    """Exact segment risk scoring per raahi_config.json."""
    available: dict[str, float] = {}
    missing: list[str] = []

    for key, weight in RISK_WEIGHTS.items():
        val = inputs.get(key)
        if val is not None and math.isfinite(val):
            # Validate 0 - 100 range
            clamped = max(0.0, min(100.0, float(val)))
            available[key] = clamped
        else:
            missing.append(key)

    available_weights = sum(RISK_WEIGHTS[k] for k in available)
    coverage = round(available_weights, 3)
    corrob_clamped = max(0.0, min(1.0, float(corroboration)))

    # Confidence formula: round(100 * coverage * (0.35 + 0.65 * corroboration))
    confidence = int(round(100 * coverage * (0.35 + 0.65 * corrob_clamped)))

    # Insufficient if: coverage < 0.40 OR confidence < 35
    if coverage < 0.40 or confidence < 35 or not available:
        score = round(sum(RISK_WEIGHTS[k] * v for k, v in available.items()) / available_weights, 1) if available_weights > 0 else None
        explanations = [
            f"Coverage ({coverage:.2f}) or confidence ({confidence}) is below threshold.",
            "Insufficient evidence to safely classify this segment."
        ]
        return SegmentRiskAssessment(
            segment_id=segment_id,
            score=score,
            confidence=confidence,
            coverage=coverage,
            corroboration=corrob_clamped,
            classification="GREY",
            data_status="INSUFFICIENT" if available else "UNASSESSED",
            length_km=round(length_km, 3),
            time_band=time_band,
            available_inputs=available,
            missing_inputs=missing,
            supporting_evidence=supporting_evidence or {},
            explanations=explanations,
            is_synthetic=is_synthetic
        )

    score = round(sum(RISK_WEIGHTS[k] * v for k, v in available.items()) / available_weights, 1)

    if score < 35.0:
        classification = "GREEN"
    elif score < 65.0:
        classification = "YELLOW"
    else:
        classification = "RED"

    explanations = []
    if available.get("incident_risk", 0) >= 60:
        explanations.append("Elevated incident frequency reported in this stretch.")
    if available.get("lighting_risk", 0) >= 50:
        explanations.append("Poor or unverified street lighting reported.")
    if available.get("isolation_risk", 0) >= 50:
        explanations.append("High physical isolation or low pedestrian activity.")
    if not explanations:
        explanations.append("Lower reported risk factors relative to baseline; not a safety guarantee.")

    return SegmentRiskAssessment(
        segment_id=segment_id,
        score=score,
        confidence=confidence,
        coverage=coverage,
        corroboration=corrob_clamped,
        classification=classification,
        data_status="SCORED",
        length_km=round(length_km, 3),
        time_band=time_band,
        available_inputs=available,
        missing_inputs=missing,
        supporting_evidence=supporting_evidence or {},
        explanations=explanations,
        is_synthetic=is_synthetic
    )


def calculate_whole_route_risk(
    segments: list[SegmentRiskAssessment],
    is_synthetic: bool = False
) -> RouteRiskAssessment:
    """Exact whole-route scoring per raahi_config.json."""
    total_len = sum(s.length_km for s in segments)
    scored = [s for s in segments if s.score is not None and s.classification != "GREY"]

    if not scored:
        return RouteRiskAssessment(
            route_score=None,
            route_confidence=0,
            classification="GREY",
            data_status="UNASSESSED",
            total_length_km=round(total_len, 3),
            assessed_length_km=0.0,
            assessed_distance_ratio=0.0,
            scored_stretch_count=0,
            length_weighted_average=None,
            highest_stretch_score=None,
            highest_risk_segment_id=None,
            segment_assessments=segments,
            influential_factors=["No verified safety evidence available for this corridor."],
            explanations=["Route is currently unassessed. Cannot certify as safe."],
            is_synthetic=is_synthetic
        )

    scored_lengths = [max(0.001, s.length_km) for s in scored]
    sum_scored_len = sum(scored_lengths)

    # length_weighted_average = sum(stretch_length_km * stretch_score) / sum(scored_stretch_lengths)
    weighted_avg = sum(l * s.score for l, s in zip(scored_lengths, scored)) / sum_scored_len

    # highest_stretch_score = max(stretch_scores)
    peak_segment = max(scored, key=lambda s: s.score or 0.0)
    peak_score = peak_segment.score or 0.0

    # route_score = 0.70 * length_weighted_average + 0.30 * highest_stretch_score
    raw_route_score = 0.70 * weighted_avg + 0.30 * peak_score
    route_score = round(raw_route_score, 2)

    # route_confidence = round(sum(stretch_length_km * stretch_confidence) / sum(scored_stretch_lengths))
    route_conf = int(round(sum(l * s.confidence for l, s in zip(scored_lengths, scored)) / sum_scored_len))

    assessed_ratio = round(sum_scored_len / total_len, 3) if total_len > 0 else 0.0

    # insufficient_if: no scored stretches OR route_confidence < 35
    if route_conf < 35 or assessed_ratio < 0.30:
        classification = "GREY"
        data_status = "INSUFFICIENT"
    elif route_score < 35.0:
        classification = "GREEN"
        data_status = "SCORED"
    elif route_score < 65.0:
        classification = "YELLOW"
        data_status = "SCORED"
    else:
        classification = "RED"
        data_status = "SCORED"

    # Identify influential factors
    influential = []
    if peak_score >= 65:
        influential.append(f"High risk peak stretch ({peak_segment.segment_id}) with score {peak_score:.1f}")
    if any("Poor or unverified street lighting reported." in s.explanations for s in scored):
        influential.append("Lighting risk identified on one or more segments")
    if any("Elevated incident frequency reported in this stretch." in s.explanations for s in scored):
        influential.append("Historical incident risk on evaluated segments")

    explanations = [
        f"Route assessed over {assessed_ratio * 100:.1f}% of total distance.",
        f"Weighted average risk: {weighted_avg:.1f}, Peak segment penalty: {peak_score:.1f}.",
        f"Final route risk score: {route_score:.1f} (Confidence: {route_conf}%)."
    ]

    return RouteRiskAssessment(
        route_score=route_score,
        route_confidence=route_conf,
        classification=classification,
        data_status=data_status,
        total_length_km=round(total_len, 3),
        assessed_length_km=round(sum_scored_len, 3),
        assessed_distance_ratio=assessed_ratio,
        scored_stretch_count=len(scored),
        length_weighted_average=round(weighted_avg, 2),
        highest_stretch_score=round(peak_score, 2),
        highest_risk_segment_id=peak_segment.segment_id,
        segment_assessments=segments,
        influential_factors=influential,
        explanations=explanations,
        is_synthetic=is_synthetic
    )


class SyntheticRiskDatasetStore:
    """Mode A: Loads and manages the synthetic 12-file package from backend/fixtures/raahi_synthetic/."""

    def __init__(self):
        fixtures_root = os.getenv("BEFIKR_FIXTURES_DIR", os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "fixtures"
        ))
        self.fixtures_dir = os.path.join(fixtures_root, "raahi_synthetic")
        self.stretches: dict[tuple[str, str], dict[str, Any]] = {}
        self.cctv: dict[str, list[dict[str, Any]]] = {}
        self.lighting: dict[str, dict[str, Any]] = {}
        self.traffic: dict[tuple[str, str], dict[str, Any]] = {}
        self.loaded = False
        self._load()

    def _load(self):
        stretches_csv = os.path.join(self.fixtures_dir, "raahi_stretches.csv")
        if not os.path.exists(stretches_csv):
            return

        with open(stretches_csv, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                self.stretches[(r["segment_id"], r["time_band"].lower())] = r

        cctv_csv = os.path.join(self.fixtures_dir, "cctv_coverage.csv")
        if os.path.exists(cctv_csv):
            with open(cctv_csv, "r", encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    sid = r["segment_id"]
                    if sid not in self.cctv:
                        self.cctv[sid] = []
                    self.cctv[sid].append(r)

        lighting_csv = os.path.join(self.fixtures_dir, "street_lighting.csv")
        if os.path.exists(lighting_csv):
            with open(lighting_csv, "r", encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    self.lighting[r["segment_id"]] = r

        traffic_csv = os.path.join(self.fixtures_dir, "traffic_data.csv")
        if os.path.exists(traffic_csv):
            with open(traffic_csv, "r", encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    self.traffic[(r["segment_id"], r["time_band"].lower())] = r

        self.loaded = True

    def get_segment_risk(self, segment_id: str, time_band: str = "day") -> SegmentRiskAssessment | None:
        tb = time_band.lower()
        row = self.stretches.get((segment_id, tb))
        if not row:
            # Fallback to day or first available
            row = self.stretches.get((segment_id, "day"))
            if not row:
                return None

        inputs = {
            "incident_risk": float(row["incident_risk"]) if row.get("incident_risk") else None,
            "report_freshness": float(row["report_freshness"]) if row.get("report_freshness") else None,
            "population_foot_traffic_risk": float(row["population_foot_traffic_risk"]) if row.get("population_foot_traffic_risk") else None,
            "lighting_risk": float(row["lighting_risk"]) if row.get("lighting_risk") else None,
            "time_of_day_risk": float(row["time_of_day_risk"]) if row.get("time_of_day_risk") else None,
            "historical_risk": float(row["historical_risk"]) if row.get("historical_risk") else None,
            "isolation_risk": float(row["isolation_risk"]) if row.get("isolation_risk") else None,
        }

        # Supporting evidence: CCTV and Traffic
        cctv_records = self.cctv.get(segment_id, [])
        active_cctv = sum(1 for c in cctv_records if c.get("operational_status") == "operational")

        supporting = {
            "cctv_cameras_count": len(cctv_records),
            "cctv_operational_count": active_cctv,
            "lighting_status": self.lighting.get(segment_id, {}).get("status", "unknown"),
            "traffic": self.traffic.get((segment_id, tb), {})
        }

        return calculate_segment_score(
            inputs=inputs,
            length_km=float(row.get("length_km", 0.5)),
            corroboration=float(row.get("corroboration", 0.0)),
            segment_id=segment_id,
            time_band=tb,
            supporting_evidence=supporting,
            is_synthetic=True
        )

    def get_risk_lookup(self, time_band: str = "day") -> dict[str, float]:
        """Map of segment_id -> score for risk-weighted pathfinding."""
        lookup = {}
        tb = time_band.lower()
        for (sid, t), row in self.stretches.items():
            if t == tb:
                score_str = row.get("stretch_score")
                if score_str:
                    lookup[sid] = float(score_str)
        return lookup


# Global singleton stores
SYNTHETIC_STORE = SyntheticRiskDatasetStore()


def assess_route_segments(
    segment_ids: list[str],
    lengths_km: list[float],
    time_band: str = "day",
    mode: str = "synthetic"  # "synthetic" (Mode A) or "real" (Mode B)
) -> RouteRiskAssessment:
    """Evaluate a sequence of road segments under Mode A or Mode B."""
    tb = time_band.lower()
    assessments: list[SegmentRiskAssessment] = []

    if mode == "synthetic":
        for sid, length in zip(segment_ids, lengths_km):
            ass = SYNTHETIC_STORE.get_segment_risk(sid, time_band=tb)
            if not ass:
                # Unassessed synthetic connector
                ass = SegmentRiskAssessment(
                    segment_id=sid,
                    score=None,
                    confidence=0,
                    coverage=0.0,
                    corroboration=0.0,
                    classification="GREY",
                    data_status="UNASSESSED",
                    length_km=round(length, 3),
                    time_band=tb,
                    is_synthetic=True
                )
            else:
                ass.length_km = round(length, 3)
            assessments.append(ass)
        return calculate_whole_route_risk(assessments, is_synthetic=True)

    else:
        # Mode B: Genuine Real Road Network
        # Strict rule: Never assign synthetic incident or lighting scores to real roads.
        # Check Befikr validated community reports from SQLite with k-anonymity >= 3.
        for sid, length in zip(segment_ids, lengths_km):
            assessments.append(SegmentRiskAssessment(
                segment_id=sid,
                score=None,
                confidence=0,
                coverage=0.0,
                corroboration=0.0,
                classification="GREY",
                data_status="UNASSESSED",
                length_km=round(length, 3),
                time_band=tb,
                explanations=["Real road corridor without verified audit feed. Unassessed by design."],
                is_synthetic=False
            ))
        return calculate_whole_route_risk(assessments, is_synthetic=False)
