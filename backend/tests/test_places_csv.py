"""CSV nearby search: accurate radius, categories, provenance and provider isolation."""

import csv
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from app import main, places_csv
from app.geo import distance_km


class CsvNearbyTests(unittest.TestCase):
    def test_haversine_known_distance_and_symmetry(self):
        self.assertEqual(distance_km(28.6, 77.2, 28.6, 77.2), 0)
        self.assertAlmostEqual(distance_km(0, 0, 0, 1), 111.1949266, places=5)
        self.assertEqual(distance_km(28, 77, 29, 78), distance_km(29, 78, 28, 77))
        self.assertTrue(math.isfinite(distance_km(0, 0, 0, 180)))

    def test_nonfinite_or_out_of_range_coordinates_are_rejected(self):
        for lat, lon in [(91, 77), (28, 181), (math.nan, 77), (28, math.inf)]:
            with self.subTest(lat=lat, lon=lon), self.assertRaises(ValueError):
                places_csv.nearby_csv_places(lat, lon)

    def test_uploaded_records_preserve_provenance_and_skip_missing_coordinates(self):
        result = places_csv.nearby_csv_places(28.6329, 77.2197)
        self.assertEqual(result["dataset_total"], 185)
        self.assertEqual(result["dataset_usable"], 181)
        self.assertEqual(result["skipped_coordinates"], 4)
        self.assertGreater(result["csv_count"], 0)
        self.assertEqual(result["places"][0]["id"], "csv-2")
        self.assertTrue(all(p["source_kind"] == "user_csv" and p["verified_at"] is None for p in result["places"]))
        self.assertTrue(all(p["phone"] != "NA" for p in result["places"]))
        self.assertTrue(all(distance_km(28.6329, 77.2197, p["latitude"], p["longitude"]) <= 5 for p in result["places"]))
        actual = [distance_km(28.6329, 77.2197, p["latitude"], p["longitude"]) for p in result["places"]]
        self.assertEqual(actual, sorted(actual))

    def test_every_category_filters_and_crowded_places_map_to_public_spaces(self):
        for category in set(places_csv.CATEGORIES.values()):
            result = places_csv.nearby_csv_places(28.6329, 77.2197, 100, category)
            self.assertTrue(result["places"], category)
            self.assertTrue(all(p["category"] == category for p in result["places"]))
        result = places_csv.nearby_csv_places(28.6329, 77.2197, 100, "public_space")
        self.assertTrue(any(p["category_label"] == "Crowded Place" for p in result["places"]))

    def test_additional_layouts_preserve_all_sixty_rows_and_category_mapping(self):
        additional = places_csv.read_place_rows(places_csv.ADDITIONAL_PATHS[0])
        public = places_csv.read_place_rows(places_csv.ADDITIONAL_PATHS[1])
        self.assertEqual((len(additional), len(public)), (26, 34))
        self.assertEqual(additional[0]["Name"], "B.R. Healthcare Rohini | Multi Speciality Hospital")
        self.assertEqual(additional[0]["Latitude"], "28.7351")
        self.assertEqual(additional[0]["Phone"], "")
        self.assertEqual(public[0]["Name"], "Indian Coffee House")
        self.assertEqual(public[0]["Address"], "Connaught Place, New Delhi")
        self.assertTrue(all(row["Source"].startswith("https://www.google.com/maps/") for row in additional + public))
        rohini = places_csv.nearby_csv_places(28.7351, 77.1182)
        self.assertTrue(any(p["name"] == additional[0]["Name"] for p in rohini["places"]))
        self.assertTrue(any(p["name"] == "Dillicious: Taste of Delhi 06" for p in rohini["places"]))
        landmarks = places_csv.nearby_csv_places(28.6275, 77.2167, category="public_space")
        self.assertTrue(any(p["name"] == "Jantar Mantar" for p in landmarks["places"]))
        self.assertTrue(any(p["name"] == "Janpath Market" for p in landmarks["places"]))

    def test_duplicate_filter_keeps_distinct_branches_and_category_specific_matches(self):
        result = places_csv.nearby_csv_places(28.6329, 77.2197)
        self.assertGreater(result["duplicate_count"], 0)
        self.assertEqual(sum(p["name"] == "United Coffee House" for p in result["places"]), 1)
        for category in ("cafe", "restaurant"):
            result = places_csv.nearby_csv_places(28.6329, 77.2197, category=category)
            self.assertTrue(any(p["name"] == "United Coffee House" for p in result["places"]))
        result = places_csv.nearby_csv_places(28.56, 77.20, 100, "cafe")
        tokai = [p for p in result["places"] if p["name"].startswith("Blue Tokai Coffee Roasters")]
        self.assertEqual(len(tokai), 5)

    def test_exact_radius_filter_runs_before_rounding_and_includes_boundary(self):
        with places_csv.DATASET_PATH.open(encoding="utf-8-sig", newline="") as source:
            original = next(csv.DictReader(source))
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            path = Path(directory) / "boundary.csv"
            rows = []
            for ident, km in [("outside", 5.0001), ("inside", 4.9999), ("near", 0.001)]:
                rows.append({**original, "ID": ident, "Latitude": str(math.degrees(km / 6371)), "Longitude": "0"})
            with path.open("w", encoding="utf-8", newline="") as dest:
                writer = csv.DictWriter(dest, fieldnames=list(original))
                writer.writeheader()
                writer.writerows(rows)
            result = places_csv.nearby_csv_places(0, 0, path=path)
            self.assertEqual([p["id"] for p in result["places"]], ["csv-near", "csv-inside"])
            boundary = distance_km(0, 0, float(rows[1]["Latitude"]), 0)
            result = places_csv.nearby_csv_places(0, 0, boundary, path=path)
            self.assertIn("csv-inside", [p["id"] for p in result["places"]])

    def test_missing_or_malformed_file_reports_unavailable(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            path = Path(directory) / "bad.csv"
            for content in [None, "Name,Address\nExample,Delhi\n"]:
                if content is not None:
                    path.write_text(content, encoding="utf-8")
                result = places_csv.nearby_csv_places(28.6, 77.2, path=path)
                self.assertEqual(result["places"], [])
                self.assertEqual(result["source_state"], "csv_dataset_unavailable")

    def test_csv_default_search_needs_no_google_or_database(self):
        with patch.object(main, "google_nearby_places", side_effect=AssertionError("No Google call expected")), \
                patch.object(main.db, "connect", side_effect=AssertionError("No database expected")):
            result = main.search_nearby_places(main.NearbyPlacesInput(latitude=28.6329, longitude=77.2197))
        self.assertEqual(result["source_state"], "csv_dataset")
        self.assertEqual(result["radius_km"], 5)
        self.assertGreater(len(result["places"]), 0)

    def test_google_search_is_still_available_explicitly(self):
        with patch.object(main, "GOOGLE_MAPS_SERVER_KEY", "test-only"), \
                patch.object(main, "google_nearby_places", return_value=[]) as google:
            result = main.search_nearby_places(main.NearbyPlacesInput(latitude=28.6, longitude=77.2, source="google"))
        google.assert_called_once_with(28.6, 77.2, 5, None)
        self.assertEqual(result["source_state"], "google_places")


if __name__ == "__main__":
    unittest.main()
