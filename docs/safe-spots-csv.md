# Safe Spots CSV radius search

The supplied CSV is stored unchanged in `backend/fixtures/delhi_safe_spots.csv`.
The original file has 125 rows: 121 usable coordinate pairs and four rows without coordinates.
Those four rows remain in the original file and are excluded from radius results.
Crowded Place and Public Space both appear in the Public spaces category, while
their original categories and subcategories are retained on each record.

For user point (latitude φ1, longitude λ1) and place point (φ2, λ2), convert degrees
to radians, then calculate the Haversine great-circle distance:

```text
Δφ = φ2 − φ1
Δλ = λ2 − λ1
a = sin²(Δφ/2) + cos(φ1) × cos(φ2) × sin²(Δλ/2)
d_km = 2 × 6371 × atan2(√a, √(1−a))
include place if d_km ≤ 5
sort included places by d_km ascending
```

Filtering and sorting use the unrounded distance. Distances returned for display
are rounded to three decimal places. They are straight-line estimates, not travel
distances or walking times. The dataset alone does not verify safety or opening hours.
Original source, confidence and notes remain in the backend records without upgrading their status.
The public interface uses ordinary nearby-place labels and availability information;
it does not expose file formats, upload controls or import notes.
Missing phone values such as NA are omitted from call links.

After signing in, open Safe Spots, allow device location or select a map pin, and
confirm it. Nearby places is the default source. The interface requests a 5 km
radius and lists the nearest matches. Category-specific Google Maps search links appear below the listings; the All
category offers police stations, hospitals, restaurants, cafes and parks. There
is no source selector.
The nearby list needs no Google API key, though background map tiles need internet.

`POST /api/places/nearby` accepts:

```json
{"latitude":28.6329,"longitude":77.2197,"radius_km":5,"source":"csv","category":"police"}
```

`source` defaults to `csv`; choose `google` for the existing Places API integration.
Omit category for all local CSV categories. Directory and Support continue to use
the managed directory. The response includes `dataset_total`, `dataset_usable`,
`skipped_coordinates`, `skipped_records`, `csv_count` and `distance_method`.
The chosen location is used for this request and is not added to the dataset.

## In-app walking routes

Selecting a result or map marker opens its route inside the Safe Spot details page.
The page shows a route polyline, starting and destination markers, walking distance,
estimated time and expandable walking steps where the provider supplies them. The
confirmed search location is the starting point, and can be changed through the map picker.
No route action redirects the user to Google Maps. Failed route requests offer retry.

The frontend uses `POST /api/routes/alternatives` with `context: "safe_spot"` and
coordinates for both endpoints. Configured Google/Mapbox providers are supported.
Otherwise the low-volume public FOSSGIS OpenStreetMap foot service is used without
a key or local spatial packages. Calls are serialized to respect the service's
maximum one request per second. The selected endpoints are sent to this external
routing service, which has its own logging policy. The app does not save these
route requests to its database. Service policy and attribution requirements:
https://routing.openstreetmap.de/about.html

The public service has no availability guarantee; production-scale usage needs
an appropriately hosted routing service. Routes are walking estimates, not live
GPS guidance or verified safety assessments. The original straight-line distance
remains labelled separately from the actual walking-route estimate.

## Additional supplied datasets

Two further files are retained unchanged: `delhi_safe_spots_additional.csv`
(26 records: 9 hospitals, 8 police stations, 9 restaurants), and
`delhi_public_places.csv` (34 records: 8 cafes, 7 parks, 8 monuments, 11 markets).
The loader accepts their original column names and converts each row in memory
to the existing listing shape. All 60 additional coordinate pairs are valid.
There are now 185 source records and 181 usable coordinate pairs across the three files.

Monuments and markets appear under Public spaces. No phone numbers or confidence
ratings are invented when absent. Supplied map links remain source metadata and
are not treated as verified Google Place IDs; some supplied links contain example
identifiers. Routes continue to use the supplied numeric coordinates.

All originals, including overlapping and differing positions, are preserved.
Within each search, same-name entries (including a small explicit alias list)
within 250 metres are collapsed after category/radius filtering and distance sorting.
The nearest supplied coordinate is displayed without averaging or inventing a pin.
Distinct branch/locality qualifiers and matches farther apart are retained.
A cafe/restaurant present in both categories remains searchable in either filter.
The response reports `duplicate_count` for the selected search. This is conservative
deduplication, not independent validation of the supplied locations.
