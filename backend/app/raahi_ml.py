"""Local Machine Learning Component for RAAHI Risk Approximation Experiments.

Zero network dependency. Implements:
- Local tabular dataset preparation from synthetic fixtures
- Scikit-learn RandomForestRegressor & GradientBoostingRegressor
- Leakage-resistant train/test evaluation (MAE, RMSE, R^2, Feature Importance)
- Local model serialization to backend/data/raahi_ml_model.joblib
- Offline local inference
- Strict disclosure: DEMO ONLY, approximates formula, not real-world predictive safety.
"""

from __future__ import annotations

import csv
import os
from dataclasses import asdict, dataclass, field
from typing import Any

import joblib
import numpy as np

try:
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except Exception:
    GradientBoostingRegressor = None
    RandomForestRegressor = None
    mean_absolute_error = None
    mean_squared_error = None
    r2_score = None
    train_test_split = None
    SKLEARN_AVAILABLE = False


@dataclass
class MLEvaluationReport:
    model_name: str
    sample_count: int
    train_r2: float
    test_r2: float
    test_mae: float
    test_rmse: float
    feature_importances: dict[str, float]
    disclaimer: str = (
        "DEMONSTRATION ONLY: This model is trained on synthetic data to approximate the "
        "deterministic risk formula. It does NOT establish real-world predictive safety."
    )


MODEL_FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "raahi_ml_model.joblib"
)


class RaahiOfflineMLEngine:
    """Trains, saves, loads and executes local ML models for offline risk approximation."""

    FEATURE_NAMES = [
        "length_km",
        "time_band_code",  # morning: 0, day: 1, evening: 2, night: 3
        "road_type_code",  # secondary: 0, primary: 1, residential: 2, tertiary: 3
        "cctv_cameras_count",
        "cctv_operational_ratio",
        "active_businesses",
        "avg_traffic_speed",
        "lighting_status_code",  # poor/unknown: 1, good/operational: 0
    ]

    TIME_BAND_MAP = {"morning": 0, "day": 1, "evening": 2, "night": 3}
    ROAD_TYPE_MAP = {"secondary": 0, "primary": 1, "residential": 2, "tertiary": 3, "footway": 4, "pedestrian": 5}
    LIGHTING_MAP = {"good": 0, "operational": 0, "fair": 0.5, "unknown": 1.0, "poor": 1.0, "broken": 1.0}

    def __init__(self):
        self.model: Any | None = None
        self.report: MLEvaluationReport | None = None
        self._try_load_model()

    def _try_load_model(self):
        if os.path.exists(MODEL_FILE_PATH):
            try:
                data = joblib.load(MODEL_FILE_PATH)
                self.model = data.get("model")
                report_dict = data.get("report")
                if report_dict:
                    self.report = MLEvaluationReport(**report_dict)
            except Exception:
                self.model = None
                self.report = None

    def prepare_training_dataset(self) -> tuple[np.ndarray, np.ndarray, list[str]]:
        """Extract multi-table features from backend/fixtures/raahi_synthetic/."""
        fixtures_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "fixtures", "raahi_synthetic"
        )

        stretches_csv = os.path.join(fixtures_dir, "raahi_stretches.csv")
        road_csv = os.path.join(fixtures_dir, "road_network.csv")
        cctv_csv = os.path.join(fixtures_dir, "cctv_coverage.csv")
        activity_csv = os.path.join(fixtures_dir, "road_activity.csv")
        traffic_csv = os.path.join(fixtures_dir, "traffic_data.csv")
        lighting_csv = os.path.join(fixtures_dir, "street_lighting.csv")

        roads = {}
        if os.path.exists(road_csv):
            with open(road_csv, "r", encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    roads[r["segment_id"]] = r

        cctv_map: dict[str, list[dict[str, Any]]] = {}
        if os.path.exists(cctv_csv):
            with open(cctv_csv, "r", encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    sid = r["segment_id"]
                    cctv_map.setdefault(sid, []).append(r)

        activity_map = {}
        if os.path.exists(activity_csv):
            with open(activity_csv, "r", encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    activity_map[(r["segment_id"], r["time_band"].lower())] = r

        traffic_map = {}
        if os.path.exists(traffic_csv):
            with open(traffic_csv, "r", encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    traffic_map[(r["segment_id"], r["time_band"].lower())] = r

        lighting_map = {}
        if os.path.exists(lighting_csv):
            with open(lighting_csv, "r", encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    lighting_map[r["segment_id"]] = r

        X_rows: list[list[float]] = []
        y_targets: list[float] = []

        if not os.path.exists(stretches_csv):
            return np.empty((0, len(self.FEATURE_NAMES))), np.empty((0,)), self.FEATURE_NAMES

        with open(stretches_csv, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                sid = r["segment_id"]
                tb = r["time_band"].lower()
                target_str = r.get("stretch_score")
                if not target_str:
                    continue

                length = float(r.get("length_km", 0.5))
                tb_code = float(self.TIME_BAND_MAP.get(tb, 1))

                road_type = roads.get(sid, {}).get("road_type", "secondary")
                rt_code = float(self.ROAD_TYPE_MAP.get(road_type, 0))

                cctv_list = cctv_map.get(sid, [])
                cctv_count = float(len(cctv_list))
                op_cctv = sum(1 for c in cctv_list if c.get("operational_status") == "operational")
                op_ratio = op_cctv / cctv_count if cctv_count > 0 else 0.0

                act = activity_map.get((sid, tb), {})
                active_biz = float(act.get("active_businesses_nearby", 10))

                traf = traffic_map.get((sid, tb), {})
                speed = float(traf.get("avg_speed_kmh", 30.0))

                light = lighting_map.get(sid, {})
                light_status = light.get("status", "unknown").lower()
                light_code = float(self.LIGHTING_MAP.get(light_status, 1.0))

                feats = [
                    length,
                    tb_code,
                    rt_code,
                    cctv_count,
                    op_ratio,
                    active_biz,
                    speed,
                    light_code
                ]
                X_rows.append(feats)
                y_targets.append(float(target_str))

        return np.array(X_rows, dtype=np.float32), np.array(y_targets, dtype=np.float32), self.FEATURE_NAMES

    def train_and_evaluate(self, model_type: str = "random_forest") -> MLEvaluationReport:
        """Train a lightweight tabular model locally and report real evaluation metrics."""
        if not SKLEARN_AVAILABLE:
            raise RuntimeError("scikit-learn is not available in this environment.")
        X, y, feature_names = self.prepare_training_dataset()
        if len(X) < 20:
            raise ValueError(f"Insufficient training rows ({len(X)}) to train ML model.")

        # 80/20 train/test split with deterministic random seed
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

        if model_type == "gradient_boosting":
            model = GradientBoostingRegressor(n_estimators=60, max_depth=3, learning_rate=0.1, random_state=42)
            name = "Gradient Boosting Regressor"
        else:
            model = RandomForestRegressor(n_estimators=50, max_depth=6, random_state=42)
            name = "Random Forest Regressor"

        model.fit(X_train, y_train)

        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)

        train_r2 = round(float(r2_score(y_train, train_pred)), 4)
        test_r2 = round(float(r2_score(y_test, test_pred)), 4)
        test_mae = round(float(mean_absolute_error(y_test, test_pred)), 3)
        test_rmse = round(float(np.sqrt(mean_squared_error(y_test, test_pred))), 3)

        # Feature importances
        raw_imp = model.feature_importances_
        importances = {name: round(float(val), 4) for name, val in zip(feature_names, raw_imp)}

        report = MLEvaluationReport(
            model_name=name,
            sample_count=len(X),
            train_r2=train_r2,
            test_r2=test_r2,
            test_mae=test_mae,
            test_rmse=test_rmse,
            feature_importances=importances
        )

        # Serialize model locally to disk
        os.makedirs(os.path.dirname(os.path.abspath(MODEL_FILE_PATH)), exist_ok=True)
        joblib.dump({"model": model, "report": asdict(report)}, MODEL_FILE_PATH)

        self.model = model
        self.report = report
        return report

    def predict_segment_risk(
        self,
        length_km: float = 0.5,
        time_band: str = "day",
        road_type: str = "secondary",
        cctv_count: int = 1,
        cctv_op_ratio: float = 1.0,
        active_businesses: int = 15,
        avg_speed: float = 30.0,
        lighting_status: str = "good"
    ) -> dict[str, Any]:
        """Offline local inference for demo risk prediction."""
        if not self.model:
            if SKLEARN_AVAILABLE:
                try:
                    self.train_and_evaluate("random_forest")
                except Exception:
                    pass

        if not self.model or not SKLEARN_AVAILABLE:
            # Deterministic formula fallback
            tb_mult = 1.4 if time_band.lower() == "night" else (1.1 if time_band.lower() == "evening" else 0.8)
            base = 25.0 * tb_mult
            if lighting_status.lower() in ("poor", "broken"): base += 25.0
            if cctv_count == 0: base += 15.0
            clamped = max(0.0, min(100.0, base))
            classification = "GREEN" if clamped < 35.0 else ("YELLOW" if clamped < 65.0 else "RED")
            return {
                "predicted_risk_score": round(clamped, 1),
                "predicted_classification": classification,
                "model_used": "Deterministic Rule-based Offline Formula",
                "offline_status": "local_inference_zero_network",
                "is_synthetic_demonstration": True,
                "disclaimer": "DEMONSTRATION ONLY. Approximates deterministic formula; not a real-world safety guarantee."
            }

        tb_code = float(self.TIME_BAND_MAP.get(time_band.lower(), 1))
        rt_code = float(self.ROAD_TYPE_MAP.get(road_type.lower(), 0))
        light_code = float(self.LIGHTING_MAP.get(lighting_status.lower(), 1.0))

        feat = np.array([[
            length_km,
            tb_code,
            rt_code,
            float(cctv_count),
            float(cctv_op_ratio),
            float(active_businesses),
            float(avg_speed),
            light_code
        ]], dtype=np.float32)

        pred_score = round(float(self.model.predict(feat)[0]), 1)
        clamped = max(0.0, min(100.0, pred_score))

        if clamped < 35.0:
            classification = "GREEN"
        elif clamped < 65.0:
            classification = "YELLOW"
        else:
            classification = "RED"

        return {
            "predicted_risk_score": clamped,
            "predicted_classification": classification,
            "model_used": self.report.model_name if self.report else "Random Forest Regressor",
            "offline_status": "local_inference_zero_network",
            "is_synthetic_demonstration": True,
            "disclaimer": "DEMONSTRATION ONLY. Approximates deterministic formula; not a real-world safety guarantee."
        }


# Global singleton instance
ML_ENGINE = RaahiOfflineMLEngine()
