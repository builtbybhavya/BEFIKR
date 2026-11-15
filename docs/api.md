# API overview

All routes are under `/api`. FastAPI OpenAPI is available at `/docs` while the local server runs. Authenticated routes use `Authorization: Bearer <access_token>`.

## Implemented route groups

- `GET /health`, `GET /capabilities`
- `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`
- `GET/PATCH/DELETE /profile`, `GET /profile/export`, `GET/PATCH /profile/preferences`
- `GET/POST /contacts`, `DELETE /contacts/{id}`
- `POST/GET /reports`, `GET /reports/status/{id}`, `POST /reports/{id}/appeal`
- `POST /evidence`, `GET/DELETE /evidence/{id}` (private report attachments)
- `POST /routes/alternatives`, `POST /routes/risk`, `GET /routes/data-status`
- `POST /sos`, `GET /sos/{id}`, `POST /sos/{id}/cancel`
- `POST /tracking/start`, `POST /tracking/{id}/location`, `GET /tracking/{id}`, `POST /tracking/{id}/stop|revoke`
- `POST /checkins/start`, `GET /checkins/{id}`, `POST /checkins/{id}/respond|cancel`
- `GET /places/categories`, `POST /places/nearby`
- `GET /voice/scripts`, `GET /voice/scripts/{id}`
- Admin: dashboard, reports/status, appeals, places, audit logs

## Important contracts

- Report submission returns `pending_review`; it never means validated or public.
- Offline drafts are stored in the browser only and are not submitted until a later confirmed POST.
- SOS response uses `delivery_state: not_configured`; this API sends no alert.
- Track Me responses include `external_sharing: false`.
- `POST /api/routes/alternatives` uses `BEFIKR_MAPPING_PROVIDER` (`demo` by default, `osmnx`, or `mapbox`). OSMnx/Mapbox can return walking-route GeoJSON, distance and an estimated duration; routes remain `navigable: false` and have no safety score. Map rendering also needs the browser to load Leaflet and OpenStreetMap tiles.
- Route risk accepts one to 100 segments, `length_km`, optional latitude/longitude, and optional normalized risk factors. Unknown fields stay missing.
- The route risk prototype has no Safetipin, Nirakshak, data.gov.in or DDA feed connected. Only validated BEFIKR reports can contribute, and only after at least three distinct owners in the same coarse two-decimal-degree cell. The response has no source report text, IDs or exact locations.
- `GET /api/routes/data-status` reports the active mapping provider and the missing external data identifiers/authorization, including that no Nirakshak feed is connected. Open data portals require a specific compatible dataset/resource; a portal URL alone is not a spatial safety feed.
- `POST /api/places/nearby` accepts `latitude`, `longitude`, optional `radius_km`, and optional `category` in JSON. It queries Google Places within the selected radius and returns the results with their source. `directory` and `support` query active BEFIKR directory listings. `source_state` distinguishes an unavailable provider, missing configuration, and a completed search. An older GET form remains available for existing clients.

## Limits before public use

There is no production rate limiter, password reset, email verification, pagination on all list endpoints, notification delivery callback, cloud object-storage integration, malware scanner, or provider-backed safety scoring. Evidence uploads use private local storage; see `docs/raaz-evidence-location.md`.
