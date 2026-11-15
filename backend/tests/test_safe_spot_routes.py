"""In-app Safe Spot routes keep walking geometry and fail without inventing paths."""

import io
import json
import unittest
from unittest.mock import patch

from app import main
from app.providers import DemoMappingProvider, PublicWalkingProvider


class SafeSpotRoutesTests(unittest.TestCase):
    def response(self, *, code="Ok", geometry=None):
        return io.BytesIO(json.dumps({"code": code, "routes": [{
            "distance": 490, "duration": 420,
            "geometry": geometry or {"type": "LineString", "coordinates": [[77.21, 28.62], [77.22, 28.63]]},
            "legs": [{"steps": [{"name": "Public Road", "distance": 490, "maneuver": {"type": "depart"}},
                                {"distance": 0, "maneuver": {"type": "arrive"}}]}],
        }]}).encode())

    def test_foot_service_receives_coordinates_and_preserves_walking_geometry(self):
        with patch("app.providers.urlopen", return_value=self.response()) as request, patch("app.providers.time.sleep"):
            result = PublicWalkingProvider().alternatives("Start", "Police", (28.62, 77.21), (28.63, 77.22))
        self.assertIn("/routed-foot/route/v1/driving/77.21,28.62;77.22,28.63", request.call_args.args[0].full_url)
        route = result["routes"][0]
        self.assertEqual(route["distance_km"], 0.49)
        self.assertEqual(route["minutes"], 7)
        self.assertEqual(route["geometry"]["coordinates"], [[77.21, 28.62], [77.22, 28.63]])
        self.assertEqual(route["steps"][0]["instruction"], "Start walking on Public Road")
        self.assertIsNone(route["risk_score"])

    def test_missing_endpoints_do_not_send_network_requests(self):
        with patch("app.providers.urlopen") as request:
            result = PublicWalkingProvider().alternatives("Start", "Police")
        request.assert_not_called()
        self.assertEqual(result["routes"], [])

    def test_no_route_or_network_failure_returns_no_straight_line(self):
        for failure in [None, OSError("Unavailable")]:
            with self.subTest(failure=failure), patch("app.providers.time.sleep"), \
                    patch("app.providers.urlopen", side_effect=failure, return_value=self.response(code="NoRoute")):
                result = PublicWalkingProvider().alternatives("Start", "Police", (28.62, 77.21), (28.63, 77.22))
                self.assertEqual(result["routes"], [])

    def test_safe_spot_request_can_route_without_google_or_osmnx(self):
        with patch.object(main, "MAPPING_PROVIDER", DemoMappingProvider()), \
                patch.object(PublicWalkingProvider, "alternatives", return_value={"routes": [], "provider": "test"}) as provider:
            main.route_alternatives(main.RouteInput(origin="Start", destination="Police", context="safe_spot",
                origin_latitude=28.62, origin_longitude=77.21, destination_latitude=28.63, destination_longitude=77.22), user={"id": "test"})
        provider.assert_called_once_with("Start", "Police", (28.62, 77.21), (28.63, 77.22))


if __name__ == "__main__":
    unittest.main()
