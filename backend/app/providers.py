"""External-service boundaries with explicit providers and honest fallbacks."""

from dataclasses import dataclass
import json
import math
import os
import threading
import time
from typing import Any, Protocol
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


class MappingProvider(Protocol):
    name: str

    def alternatives(self, origin: str, destination: str,
                     origin_coordinates: tuple[float, float] | None = None,
                     destination_coordinates: tuple[float, float] | None = None) -> dict[str, Any]: ...


@dataclass(frozen=True)
class DemoMappingProvider:
    """Clearly non-navigable placeholders. Never fabricate geometry or metrics."""

    name: str = "demo"

    def alternatives(self, origin: str, destination: str,
                     origin_coordinates: tuple[float, float] | None = None,
                     destination_coordinates: tuple[float, float] | None = None) -> dict[str, Any]:
        options = [
            {"id": "demo-direct", "label": "Illustrative option A", "distance_km": 0, "minutes": 0,
             "risk_score": None, "confidence": 0, "classification": "insufficient", "navigable": False,
             "provider": self.name, "explanation": ["No live mapping or route data is configured.", "Safety data cannot be classified."]},
            {"id": "demo-connected", "label": "Illustrative option B", "distance_km": 0, "minutes": 0,
             "risk_score": None, "confidence": 0, "classification": "insufficient", "navigable": False,
             "provider": self.name, "explanation": ["Illustrative placeholder only; it is not a real route.", "No live mapping or route data is configured."]},
        ]
        return {"origin": origin, "destination": destination, "provider_state": "demo_only",
                "warning": "These are placeholders, not real routes. Configure a mapping provider before navigation.",
                "routes": options}


@dataclass(frozen=True)
class UnavailableMappingProvider:
    name: str
    reason: str

    def alternatives(self, origin: str, destination: str,
                     origin_coordinates: tuple[float, float] | None = None,
                     destination_coordinates: tuple[float, float] | None = None) -> dict[str, Any]:
        return {"origin": origin, "destination": destination, "provider_state": "not_configured",
                "warning": self.reason, "routes": []}


class OSMnxWalkingProvider:
    """Build walking alternatives from the OSM pedestrian graph when explicitly enabled."""

    name = "osmnx_openstreetmap"
    _geocode_lock = threading.Lock()
    _last_geocode_at = 0.0

    def _geocode(self, ox: Any, query: str) -> tuple[float, float]:
        # Respect Nominatim's public-service request cadence. This is in-memory only.
        with self._geocode_lock:
            pause = 1.1 - (time.monotonic() - self._last_geocode_at)
            if pause > 0:
                time.sleep(pause)
            point = ox.geocoder.geocode(query)
            self._last_geocode_at = time.monotonic()
        return float(point[0]), float(point[1])

    @staticmethod
    def _path_geometry(graph: Any, path: list[int]) -> tuple[list[list[float]], float]:
        coordinates: list[list[float]] = []
        distance_m = 0.0
        for start, end in zip(path, path[1:]):
            edges = graph.get_edge_data(start, end) or {}
            if not edges:
                continue
            edge = min(edges.values(), key=lambda item: float(item.get("length", math.inf)))
            distance_m += float(edge.get("length", 0))
            start_xy = (float(graph.nodes[start]["x"]), float(graph.nodes[start]["y"]))
            end_xy = (float(graph.nodes[end]["x"]), float(graph.nodes[end]["y"]))
            geometry = edge.get("geometry")
            line = list(geometry.coords) if geometry is not None else [start_xy, end_xy]
            if line and math.dist(line[0], start_xy) > math.dist(line[-1], start_xy):
                line.reverse()
            for lon, lat in line:
                pair = [float(lon), float(lat)]
                if not coordinates or coordinates[-1] != pair:
                    coordinates.append(pair)
        return coordinates, distance_m

    def alternatives(self, origin: str, destination: str,
                     origin_coordinates: tuple[float, float] | None = None,
                     destination_coordinates: tuple[float, float] | None = None) -> dict[str, Any]:
        try:
            import osmnx as ox
        except ImportError:
            return {"origin": origin, "destination": destination, "provider_state": "dependency_missing",
                    "warning": "Install the declared OSMnx dependency and set BEFIKR_MAPPING_PROVIDER=osmnx to enable pedestrian routing.",
                    "routes": []}
        try:
            ox.settings.use_cache = False
            ox.settings.log_console = False
            ox.settings.requests_timeout = 30
            ox.settings.http_user_agent = "BEFIKR-Raahi/0.1"
            origin_point = origin_coordinates or self._geocode(ox, origin)
            destination_point = destination_coordinates or self._geocode(ox, destination)
            mean_lat = (origin_point[0] + destination_point[0]) / 2
            mean_lon = (origin_point[1] + destination_point[1]) / 2
            direct_m = 111_000 * math.hypot(destination_point[0] - origin_point[0],
                                             (destination_point[1] - origin_point[1]) * math.cos(math.radians(mean_lat)))
            radius_m = min(25_000, max(3_000, direct_m * 0.65 + 2_500))
            graph = ox.graph.graph_from_point((mean_lat, mean_lon), dist=radius_m,
                                              dist_type="bbox", network_type="walk", simplify=True)
            start_node = ox.distance.nearest_nodes(graph, X=origin_point[1], Y=origin_point[0])
            end_node = ox.distance.nearest_nodes(graph, X=destination_point[1], Y=destination_point[0])
            paths = list(ox.routing.k_shortest_paths(graph, start_node, end_node, k=3, weight="length"))
            routes = []
            seen: set[tuple[int, ...]] = set()
            for path in paths:
                if not path or len(path) < 2 or tuple(path) in seen:
                    continue
                seen.add(tuple(path))
                coordinates, distance_m = self._path_geometry(graph, path)
                if len(coordinates) < 2 or distance_m <= 0:
                    continue
                distance_km = distance_m / 1000
                routes.append({
                    "id": f"osm-walk-{len(routes) + 1}",
                    "label": "Shortest walking route" if not routes else f"Walking alternative {len(routes) + 1}",
                    "distance_km": round(distance_km, 2),
                    "minutes": round(distance_km / 4.5 * 60),
                    "risk_score": None,
                    "confidence": 0,
                    "classification": "insufficient",
                    "navigable": False,
                    "provider": self.name,
                    "geometry": {"type": "LineString", "coordinates": coordinates},
                    "explanation": ["Path follows the OpenStreetMap pedestrian network.",
                                    "No Safetipin or other route-matched personal-safety data is connected.",
                                    "Walking time is a rough estimate, not live navigation."],
                })
            return {"origin": origin, "destination": destination,
                    "provider_state": "walking_routes_available" if routes else "no_walking_route",
                    "provider": self.name,
                    "warning": "These are pedestrian-network options from OpenStreetMap. They are not safety-rated; the route geometry is a map estimate, not turn-by-turn navigation.",
                    "routes": routes}
        except Exception as error:
            return {"origin": origin, "destination": destination, "provider_state": "routing_unavailable",
                    "provider": self.name,
                    "warning": f"OpenStreetMap walking routes could not be loaded ({type(error).__name__}). Check the place names and internet connection, then try again.",
                    "routes": []}


@dataclass(frozen=True)
class MapboxDirectionsProvider:
    access_token: str
    name: str = "mapbox_walking"

    @staticmethod
    def _get_json(url: str) -> dict[str, Any]:
        request = Request(url, headers={"User-Agent": "BEFIKR-Raahi/0.1"})
        with urlopen(request, timeout=20) as response:
            body = json.loads(response.read(2_000_001).decode("utf-8"))
        if not isinstance(body, dict):
            raise ValueError("The mapping provider returned an invalid response")
        return body

    def _geocode(self, query: str) -> tuple[float, float]:
        params = urlencode({"q": query, "country": "IN", "limit": 1, "access_token": self.access_token})
        result = self._get_json(f"https://api.mapbox.com/search/geocode/v6/forward?{params}")
        features = result.get("features") or []
        if not features:
            raise ValueError(f"Could not find {query}")
        longitude, latitude = features[0]["geometry"]["coordinates"][:2]
        return float(longitude), float(latitude)

    def alternatives(self, origin: str, destination: str,
                     origin_coordinates: tuple[float, float] | None = None,
                     destination_coordinates: tuple[float, float] | None = None) -> dict[str, Any]:
        try:
            start_lat_lon = origin_coordinates or self._geocode(origin)
            finish_lat_lon = destination_coordinates or self._geocode(destination)
            start = (start_lat_lon[1], start_lat_lon[0]) if origin_coordinates else start_lat_lon
            finish = (finish_lat_lon[1], finish_lat_lon[0]) if destination_coordinates else finish_lat_lon
            coordinates = f"{start[0]},{start[1]};{finish[0]},{finish[1]}"
            params = urlencode({"alternatives": "true", "geometries": "geojson", "overview": "full",
                                "access_token": self.access_token})
            result = self._get_json(f"https://api.mapbox.com/directions/v5/mapbox/walking/{quote(coordinates, safe=',;')}?{params}")
            if result.get("code") != "Ok":
                raise ValueError(result.get("message") or result.get("code") or "No walking route found")
            routes = []
            for index, route in enumerate(result.get("routes") or []):
                distance_km = float(route.get("distance", 0)) / 1000
                routes.append({
                    "id": f"mapbox-walk-{index + 1}",
                    "label": "Walking route" if index == 0 else f"Walking alternative {index + 1}",
                    "distance_km": round(distance_km, 2),
                    "minutes": round(float(route.get("duration", 0)) / 60),
                    "risk_score": None,
                    "confidence": 0,
                    "classification": "insufficient",
                    "navigable": False,
                    "provider": self.name,
                    "geometry": route.get("geometry"),
                    "explanation": ["Walking geometry and estimates are from Mapbox Directions.",
                                    "No Safetipin or other route-matched personal-safety data is connected."],
                })
            return {"origin": origin, "destination": destination, "provider_state": "walking_routes_available",
                    "provider": self.name,
                    "warning": "Mapbox returned walking routes. They are not safety-rated; navigation must be opened separately.",
                    "routes": routes}
        except Exception as error:
            return {"origin": origin, "destination": destination, "provider_state": "routing_unavailable",
                    "provider": self.name,
                    "warning": f"Mapbox walking routes could not be loaded ({type(error).__name__}). Check provider access and place names.",
                    "routes": []}


class PublicWalkingProvider:
    """Low-volume FOSSGIS foot routing; no local spatial packages or API key needed."""

    name = "openstreetmap_foot"
    _request_lock = threading.Lock()
    _last_request_at = 0.0

    def alternatives(self, origin: str, destination: str,
                     origin_coordinates: tuple[float, float] | None = None,
                     destination_coordinates: tuple[float, float] | None = None) -> dict[str, Any]:
        result = {"origin": origin, "destination": destination, "provider": self.name,
                  "provider_state": "routing_unavailable", "routes": [],
                  "warning": "Walking directions could not be loaded. Please retry shortly."}
        if origin_coordinates is None or destination_coordinates is None:
            return result
        start, end = origin_coordinates, destination_coordinates
        coordinates = f"{start[1]},{start[0]};{end[1]},{end[0]}"
        params = urlencode({"overview": "full", "geometries": "geojson", "steps": "true"})
        request = Request(f"https://routing.openstreetmap.de/routed-foot/route/v1/driving/{coordinates}?{params}",
                          headers={"User-Agent": "BEFIKR-SafeSpots/0.1", "Accept": "application/json"})
        try:
            # The public service permits at most one request per second.
            with self._request_lock:
                pause = 1.05 - (time.monotonic() - PublicWalkingProvider._last_request_at)
                if pause > 0:
                    time.sleep(pause)
                PublicWalkingProvider._last_request_at = time.monotonic()
                with urlopen(request, timeout=20) as response:
                    payload = json.loads(response.read(2_000_001).decode("utf-8"))
            if payload.get("code") != "Ok":
                return result
            routes = []
            for route in payload.get("routes", [])[:1]:
                geometry = route.get("geometry") or {}
                points = geometry.get("coordinates") or []
                metres, seconds = float(route.get("distance", 0)), float(route.get("duration", 0))
                if geometry.get("type") != "LineString" or len(points) < 2 or metres < 0 or seconds < 0:
                    continue
                steps = []
                for leg in route.get("legs", []):
                    for step in leg.get("steps", []):
                        maneuver = step.get("maneuver") or {}
                        action = maneuver.get("type", "continue").replace("_", " ")
                        modifier = maneuver.get("modifier", "")
                        if action == "depart":
                            instruction = "Start walking"
                        elif action == "arrive":
                            instruction = "Arrive at your destination"
                        elif action in {"roundabout", "rotary"}:
                            instruction = "Enter the roundabout"
                            if maneuver.get("exit"):
                                instruction += f" and take exit {maneuver['exit']}"
                        else:
                            instruction = " ".join(filter(None, [action.capitalize(), modifier]))
                        if step.get("name") and action != "arrive":
                            instruction += f" on {step['name']}"
                        steps.append({"instruction": instruction, "distance_m": round(float(step.get("distance", 0)))})
                routes.append({"id": "safe-spot-walk", "label": "Walking route", "provider": self.name,
                               "distance_km": round(metres / 1000, 2), "minutes": max(1, round(seconds / 60)),
                               "risk_score": None, "confidence": 0, "classification": "insufficient",
                               "navigable": False, "geometry": geometry, "steps": steps,
                               "explanation": ["Walking route estimate from OpenStreetMap via FOSSGIS."]})
            result.update(routes=routes, provider_state="walking_routes_available" if routes else "no_walking_route")
            if routes:
                result["warning"] = "Walking route estimate from OpenStreetMap via FOSSGIS; check local signs and access."
            return result
        except (OSError, ValueError, TypeError, KeyError, AttributeError):
            return result


def decode_google_polyline(encoded: str) -> list[list[float]]:
    coordinates: list[list[float]] = []
    latitude = longitude = index = 0
    while index < len(encoded):
        values = []
        for _ in range(2):
            result = shift = 0
            while True:
                byte = ord(encoded[index]) - 63
                index += 1
                result |= (byte & 0x1F) << shift
                shift += 5
                if byte < 0x20:
                    break
            values.append(~(result >> 1) if result & 1 else result >> 1)
        latitude += values[0]
        longitude += values[1]
        coordinates.append([longitude / 1e5, latitude / 1e5])
    return coordinates


@dataclass(frozen=True)
class GoogleRoutesProvider:
    api_key: str
    name: str = "google_routes_walking"

    @staticmethod
    def _waypoint(label: str, coordinates: tuple[float, float] | None) -> dict[str, Any]:
        if coordinates:
            return {"location": {"latLng": {"latitude": coordinates[0], "longitude": coordinates[1]}}}
        return {"address": label}

    def alternatives(self, origin: str, destination: str,
                     origin_coordinates: tuple[float, float] | None = None,
                     destination_coordinates: tuple[float, float] | None = None) -> dict[str, Any]:
        body = {
            "origin": self._waypoint(origin, origin_coordinates),
            "destination": self._waypoint(destination, destination_coordinates),
            "travelMode": "WALK",
            "computeAlternativeRoutes": True,
            "languageCode": "en-IN",
            "units": "METRIC",
            "polylineQuality": "OVERVIEW",
        }
        request = Request(
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", "X-Goog-Api-Key": self.api_key,
                     "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=20) as response:
                payload = json.loads(response.read(2_000_001).decode("utf-8"))
            routes = []
            for index, route in enumerate(payload.get("routes") or []):
                distance_km = float(route.get("distanceMeters", 0)) / 1000
                duration = str(route.get("duration", "0s")).removesuffix("s")
                polyline = route.get("polyline", {}).get("encodedPolyline", "")
                geometry = decode_google_polyline(polyline)
                if len(geometry) < 2 or distance_km <= 0:
                    continue
                routes.append({
                    "id": f"google-walk-{index + 1}",
                    "label": "Walking route" if index == 0 else f"Walking alternative {index + 1}",
                    "distance_km": round(distance_km, 2),
                    "minutes": round(float(duration) / 60),
                    "risk_score": None,
                    "confidence": 0,
                    "classification": "insufficient",
                    "navigable": False,
                    "provider": self.name,
                    "geometry": {"type": "LineString", "coordinates": geometry},
                    "explanation": ["Walking geometry and estimates are from Google Routes.",
                                    "No verified personal-safety rating is connected."],
                })
            return {"origin": origin, "destination": destination,
                    "provider_state": "walking_routes_available" if routes else "no_walking_route",
                    "provider": self.name,
                    "warning": "Google returned walking routes. They are not safety-rated; Google Maps may choose a different route for navigation.",
                    "routes": routes}
        except Exception as error:
            return {"origin": origin, "destination": destination, "provider_state": "routing_unavailable",
                    "provider": self.name,
                    "warning": f"Google walking routes could not be loaded ({type(error).__name__}). Check API access, billing, and both points.",
                    "routes": []}


def configured_mapping_provider() -> MappingProvider:
    provider = os.getenv("BEFIKR_MAPPING_PROVIDER", "auto").strip().lower()
    if provider == "demo":
        return UnavailableMappingProvider("demo", "DEMO ONLY: Using synthetic risk scoring model. Not real safety data.")
    if provider in ("offline", "offline_ai_decider", "auto"):
        from .offline_provider import OfflineMappingProvider
        return OfflineMappingProvider()
    google_key = os.getenv("GOOGLE_MAPS_SERVER_KEY", "").strip()
    browser_key = os.getenv("GOOGLE_MAPS_BROWSER_KEY", "").strip()
    if provider == "google":
        if google_key and browser_key:
            return GoogleRoutesProvider(google_key)
        return UnavailableMappingProvider("google_routes", "Configure both Google Maps keys before enabling Google Routes: a server key and a restricted browser key for map display.")
    if provider == "osmnx":
        return OSMnxWalkingProvider()
    if provider == "mapbox":
        token = os.getenv("MAPBOX_ACCESS_TOKEN", "").strip()
        if token:
            return MapboxDirectionsProvider(token)
        return UnavailableMappingProvider("mapbox", "Set MAPBOX_ACCESS_TOKEN on the server before selecting the Mapbox provider.")
    from .offline_provider import OfflineMappingProvider
    return OfflineMappingProvider()


@dataclass(frozen=True)
class DeliveryResult:
    state: str
    confirmed: bool
    detail: str


class NotificationProvider(Protocol):
    def send(self, recipient: str, message: str) -> DeliveryResult: ...


@dataclass(frozen=True)
class UnconfiguredNotificationProvider:
    def send(self, recipient: str, message: str) -> DeliveryResult:
        return DeliveryResult("not_configured", False, "No notification provider is configured.")


class EvidenceStorageProvider(Protocol):
    def store(self, filename: str, content: bytes) -> str: ...


@dataclass(frozen=True)
class UnconfiguredEvidenceStorage:
    def store(self, filename: str, content: bytes) -> str:
        raise RuntimeError("Secure evidence storage and scanning are not configured.")
