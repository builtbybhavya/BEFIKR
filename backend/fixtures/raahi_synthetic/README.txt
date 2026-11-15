# RAAHI Synthetic Complete Dataset (Demo Only)

**IMPORTANT:** Every record is fabricated. Coordinates and road geometries are illustrative and do not represent a verified Delhi road network. This package must not be used for real-world navigation, safety decisions, or claims.

## Files
- `road_network.csv`: synthetic segment/node geometry represented by endpoints (CSV form).
- `crime_incidents.csv`: fictional incident records.
- `street_lighting.csv`: fictional lighting status and illumination.
- `population_footfall.csv`: fictional population/footfall values.
- `cctv_coverage.csv`: fictional camera coverage records.
- `traffic_data.csv`: fictional speed/travel-time/closure values by time band.
- `road_activity.csv`: fictional activity / isolation proxies by time band.
- `data_sources.csv`: provenance entry identifying the generator.
- `raahi_stretches.csv`: derived synthetic risk scores, confidence, status, and GREEN/YELLOW/RED/GREY color.
- `raahi_routes.csv`: derived synthetic route examples.
- `raahi_config.json`: exact user-provided weights and formula rules.

The CSV road network uses endpoint coordinates for convenient testing. It is not a routable graph nor GeoJSON. App code should keep this DEMO dataset separate from production data.
