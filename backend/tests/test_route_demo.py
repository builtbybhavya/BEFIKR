"""Regression tests for the supplied synthetic dataset, without live maps or a database."""

import copy
import csv
import json
import math
import tempfile
import unittest
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from app import main, route_demo


class SyntheticRouteDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = route_demo.read_dataset()

    def test_bundled_csv_and_json_preserve_the_supplied_data(self):
        with route_demo.DATASET_PATH.with_suffix(".csv").open(encoding="utf-8-sig", newline="") as source:
            csv_rows = list(csv.DictReader(source))
        self.assertEqual(len(self.rows), 135)
        self.assertEqual(csv_rows, [{key: str(value) for key, value in row.items()} for row in self.rows])
        self.assertEqual(len({row["route_segment_id"] for row in self.rows}), 45)
        self.assertEqual(len({(row["from_area"], row["to_area"]) for row in self.rows}), 45)
        self.assertEqual(Counter(row["time_band"] for row in self.rows), {"Day": 45, "Evening": 45, "Night": 45})
        self.assertEqual(Counter(row["safety_label"] for row in self.rows), {"GREEN": 65, "YELLOW": 70})

    def test_every_supplied_label_and_score_is_returned_unchanged(self):
        for row in self.rows:
            with self.subTest(segment=row["route_segment_id"], band=row["time_band"]):
                result = route_demo.demo_lookup(row["from_area"], row["to_area"], row["time_band"])
                self.assertTrue(result["available"])
                self.assertTrue(result["matched"])
                self.assertEqual(result["source"], "synthetic_demo")
                self.assertEqual(result["record"], row)
                self.assertIn("synthetic", result["notice"].lower())

    def test_reverse_pairs_are_not_invented(self):
        pairs = {(row["from_area"], row["to_area"]) for row in self.rows}
        for origin, destination in pairs:
            self.assertNotIn((destination, origin), pairs)
            with self.subTest(origin=destination, destination=origin):
                result = route_demo.demo_lookup(destination, origin, "Day")
                self.assertTrue(result["available"])
                self.assertFalse(result["matched"])
                self.assertIsNone(result["record"])

    def test_matching_does_not_promote_pins_or_substrings_to_named_areas(self):
        for origin, destination in [
            ("Pinned location", "India Gate"),
            ("28.6315, 77.2167", "India Gate"),
            ("Connaught Place Hospital", "India Gate"),
            ("Connaught Place", "India Gate Cafe"),
            ("Saket Hospital", "Mehrauli"),
            ("Connaught Place, Mumbai", "India Gate"),
            ("CP", "India Gate"),
        ]:
            with self.subTest(origin=origin, destination=destination):
                result = route_demo.demo_lookup(origin, destination, "Day")
                self.assertFalse(result["matched"])
                self.assertIsNone(result["record"])

    def test_case_spacing_and_explicit_delhi_suffixes_match(self):
        result = route_demo.demo_lookup("  connaught   place, New Delhi, India  ", "INDIA GATE, Delhi", "Day")
        self.assertTrue(result["matched"])
        self.assertEqual(result["record"]["route_segment_id"], "DEL-001")

    def test_current_band_uses_delhi_boundaries_even_for_utc_input(self):
        expected = [
            ("00:29:59", "Night", "22:00-06:00"),
            ("00:30:00", "Day", "06:00-18:00"),
            ("12:29:59", "Day", "06:00-18:00"),
            ("12:30:00", "Evening", "18:00-22:00"),
            ("16:29:59", "Evening", "18:00-22:00"),
            ("16:30:00", "Night", "22:00-06:00"),
        ]
        for clock, band, window in expected:
            instant = datetime.fromisoformat(f"2026-11-14T{clock}+00:00")
            with self.subTest(utc=clock):
                self.assertEqual(route_demo.resolve_time_band(at=instant), (band, window))
                self.assertEqual(route_demo.resolve_time_band(at=instant.astimezone(timezone(timedelta(hours=5, minutes=30)))), (band, window))
                result = route_demo.demo_lookup("Connaught Place", "India Gate", at=instant)
                self.assertEqual(result["time_band"], band)
                self.assertEqual(result["record"]["time_band"], band)

    def test_ambiguous_time_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            route_demo.resolve_time_band(at=datetime(2026, 11, 14, 18, 0))
        with self.assertRaises(ValueError):
            route_demo.resolve_time_band("Afternoon")

    def assert_unavailable_dataset(self, path):
        self.assertFalse(route_demo.demo_catalog(path=path)["available"])
        result = route_demo.demo_lookup("Connaught Place", "India Gate", "Day", path=path)
        self.assertFalse(result["available"])
        self.assertFalse(result["matched"])
        self.assertIsNone(result["record"])

    def test_missing_and_malformed_files_fail_closed(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent, prefix=".route-demo-") as directory:
            path = Path(directory) / "dataset.json"
            self.assert_unavailable_dataset(path)
            for content in ("{broken", "null", "{}", "[]"):
                with self.subTest(content=content):
                    path.write_text(content, encoding="utf-8")
                    self.assert_unavailable_dataset(path)

    def test_invalid_values_or_lost_provenance_fail_closed(self):
        invalid_fields = [
            ("safety_score_synthetic_0_100", -1),
            ("safety_score_synthetic_0_100", 101),
            ("safety_score_synthetic_0_100", math.nan),
            ("lighting_index_synthetic_0_100", math.inf),
            ("pedestrian_activity_index_synthetic_0_100", -1),
            ("cctv_coverage_index_synthetic_0_100", 101),
            ("distance_km_synthetic", 0),
            ("duration_minutes_synthetic", -1),
            ("synthetic_incident_signal_count", 1.5),
            ("synthetic_incident_signal_count", -1),
            ("safety_label", "SAFE"),
            ("data_status", "VERIFIED"),
            ("time_window", "00:00-23:59"),
        ]
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent, prefix=".route-demo-") as directory:
            path = Path(directory) / "dataset.json"
            for field, value in invalid_fields:
                with self.subTest(field=field, value=value):
                    rows = copy.deepcopy(self.rows)
                    rows[0][field] = value
                    path.write_text(json.dumps(rows), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        route_demo.read_dataset(path)
                    self.assert_unavailable_dataset(path)

    def test_duplicate_or_missing_time_band_does_not_return_partial_ratings(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent, prefix=".route-demo-") as directory:
            path = Path(directory) / "dataset.json"
            for rows in (self.rows[1:], self.rows + [self.rows[0]]):
                path.write_text(json.dumps(rows), encoding="utf-8")
                self.assert_unavailable_dataset(path)


class SyntheticRouteIntegrationTests(unittest.TestCase):
    def test_dataset_endpoints_are_available_without_database_or_external_calls(self):
        with patch.object(main.db, "connect", side_effect=AssertionError("Demo data must not query the user database")):
            catalog = main.safety_demo_catalog(user={"id": "test-only"})
            result = main.safety_demo_lookup(main.SafetyDemoInput(origin="Connaught Place", destination="India Gate", time_band="Day"), user={"id": "test-only"})
        self.assertTrue(catalog["available"])
        self.assertEqual(result["record"]["safety_label"], "GREEN")
        methods = set().union(*(route.methods for route in main.app.routes if route.path == "/api/routes/safety-demo"))
        self.assertTrue({"GET", "POST"}.issubset(methods))

    def test_demo_rating_does_not_change_live_route_risk_ranking_or_geometry(self):
        live_routes = [
            {"id": "walking-a", "label": "Walking route A", "distance_km": 4.1, "minutes": 55,
             "risk_score": None, "confidence": 0, "classification": "insufficient", "navigable": True,
             "provider": "test-map", "geometry": [[77.21, 28.63], [77.22, 28.61]], "explanation": ["No verified rating"]},
            {"id": "walking-b", "label": "Walking route B", "distance_km": 4.8, "minutes": 67,
             "risk_score": None, "confidence": 0, "classification": "insufficient", "navigable": True,
             "provider": "test-map", "geometry": [[77.21, 28.63], [77.23, 28.62], [77.22, 28.61]], "explanation": ["No verified rating"]},
        ]
        with patch.object(main, "MAPPING_PROVIDER") as provider, patch.object(main.db, "connect", side_effect=AssertionError("No database expected")):
            provider.alternatives.return_value = {"routes": copy.deepcopy(live_routes), "provider_state": "walking_routes_available"}
            result = main.route_alternatives(main.RouteInput(origin="Connaught Place", destination="India Gate", demo_time_band="Day"), user={"id": "test-only"})
        self.assertTrue(result["safety_demo"]["matched"])
        self.assertEqual(result["safety_demo"]["record"]["safety_score_synthetic_0_100"], 81)
        self.assertEqual(result["routes"], [{**row, "comparison_score": None} for row in live_routes])


if __name__ == "__main__":
    unittest.main()
