# BEFIKR

**Bhool ja apne sare dar, Ban Befikr.**

BEFIKR is a mobile-first safety support application with five connected modules: RAAHI, RAAZ, BAAT BANAO, BACKUP, and SAFE SPOT. This workspace contains a runnable progressive web app (PWA), a FastAPI modular-monolith development backend, local SQLite persistence, a privacy-gated moderation pipeline, an explainable prototype risk engine, a PostGIS production schema reference, and workflow tests.

The web client is a responsive PWA and caches its interface for offline access. A native Android Studio project is also available in [`android-app`](android-app/README.md); it reuses the five modules and adds Android SOS SMS and location permissions. Its backend URL must be configured to a deployed HTTPS host before it can serve multiple phones. An APK has not been built in this workspace because Android Studio, Java, and the Android SDK are not installed here. There is no native iOS client.

## Start locally

Python 3.12+ is recommended. From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
$env:BEFIKR_TOKEN_SECRET = [Convert]::ToBase64String([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
$env:BEFIKR_DATA_DIR = "$PWD\backend\data"
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Create a user account in the app. The SQLite database is created at `backend/data/befikr.db` and is ignored by Git.

The manual map picker and Google Maps handoff work without an API key. To enable live Raahi pickup and drop-off suggestions and Safe Spot results, enable [Places API (New)](https://developers.google.com/maps/documentation/places/web-service/get-api-key) in a Google Cloud project with billing and set the server key before starting the API. Raahi searches India and prioritizes Delhi and NCR. Enable [Maps Embed API](https://developers.google.com/maps/documentation/embed/get-api-key) for in-app previews of typed places, walking directions, and nearby place searches. Enable Maps JavaScript API for movable Google place pins and maps that draw the route returned by Routes API.

```powershell
# Enable Places API (New) for Raahi suggestions and Safe Spot. Enable Routes API for Google walking routes.
$env:GOOGLE_MAPS_SERVER_KEY = "your-server-key"

# This key is sent to the browser. Enable Maps JavaScript API and restrict it to your app's HTTP referrers.
$env:GOOGLE_MAPS_BROWSER_KEY = "your-referrer-restricted-browser-key"

# Optional dedicated website key restricted to Maps Embed API.
# If omitted, allow Maps Embed API on GOOGLE_MAPS_BROWSER_KEY to use it for iframes.
$env:GOOGLE_MAPS_EMBED_KEY = "your-referrer-restricted-embed-key"
$env:BEFIKR_MAPPING_PROVIDER = "auto"
```

Restrict the server key to the Google APIs you enable and the browser key to your site's referrers and Maps JavaScript API. Keep the server key out of Git and frontend code. If Places is unavailable, Safe Spot offers an external Google Maps search near the confirmed pin. The map picker can use OpenStreetMap tiles. OSMnx is the automatic walking-route fallback and needs internet access to OpenStreetMap services.

You can also select a provider explicitly:

```powershell
# OpenStreetMap walking network
$env:BEFIKR_MAPPING_PROVIDER = "osmnx"

# Or Mapbox Directions (keep the token server-side)
$env:BEFIKR_MAPPING_PROVIDER = "mapbox"
$env:MAPBOX_ACCESS_TOKEN = "your-server-side-token"
```

OSMnx, Google Routes, and Mapbox provide walking geometry and estimates, not a safety rating. The user can pin either endpoint on the map or type a place name. Tap Me takes its journey duration from the selected Raahi route and applies the original illustrative equation `Rₜ = 0.25R + 0.15P + 0.10T + 0.15I + 0.10V + 0.10E + 0.15M`, then `N = min(12, max(1, ceil(ceil(D / 120) × (1 + Rₜ / 100))))`. Until route risk data is connected, missing factors use disclosed neutral defaults; Tap Me reminders run only while the app is open and do not contact anyone.

The other listed sources need separate configuration before they can inform route risk. Safetipin requires an authorized IUDX resource ID and token, or an approved spatial data export with usable audit fields. `data.gov.in` requires a specific resource ID and API key, and the selected dataset must contain suitable location/time fields. DDA GIS can provide infrastructure context, not personal-safety audits. Google Places provides nearby place information, not a safety rating. The Nirakshak feed/API was not supplied or connected. Until a relevant authorized audit feed is configured, route safety scoring remains unavailable; the manual calculator is only a prototype.

To enable the role-gated admin console, set these variables **before** starting the API. Admin bootstrap happens only when the email is not already in the database:

```powershell
$env:BEFIKR_ADMIN_EMAIL = "moderator@example.org"
$env:BEFIKR_ADMIN_PASSWORD = "use-a-unique-password-with-14-or-more-characters"
```

Sign in with that account, then open **Profile → Open admin console**. Keep development credentials local and use a managed secret store for hosted environments.

For Delhi place imports and Raahi source research, see the [TinyFish workflow](docs/raahi-tinyfish-data.md).

## Verify the project

```powershell
Set-Location backend
python -m unittest discover -s tests -v
```

API reference: `http://127.0.0.1:8000/docs`. Health: `http://127.0.0.1:8000/api/health`.

## What works in this build

| Area | State | What is implemented |
|---|---|---|
| Account | Functional local flow | Registration, login, password hashing, signed short-lived sessions, logout revocation, profile edit/delete, data export |
| RAAHI | Partial | Typed or map-pinned pickup/drop-off, real walking distance/time and route alternatives via Google Routes when configured or OSMnx fallback, and Google Maps directions handoff. No Safetipin/Nirakshak route-risk score is shown until an authorized audit feed is configured |
| Map access | Partial | Interactive map pinning uses Google Maps when configured and OpenStreetMap otherwise; location access is requested only after the user asks. Google Maps search/directions URLs work without an API key |
| RAAZ | Functional local workflow | Private submissions, status history, duplicate warning for same-account submissions, status view, appeal, offline local draft queue |
| Report evidence | Unavailable | Secure object storage, malware scanning, attachment upload, and retention jobs are not configured |
| Moderation | Functional local workflow | Role-gated report review, status history, appeal decisions, audit logs; human decisions are required for validation |
| BAAT BANAO | Local simulation | Preset dialogues, caller choices, and controls. Only supplied MP3 recordings play; other lines stay transcript-only until recordings are added. No synthesized/device voices or real calls are used |
| BACKUP / SOS | Manual phone handoff | Saves/cancels an event, opens the phone dialer for India 112, and prepares a text to a saved contact. The user must place the call/send the text; there is no automatic dispatch or escalation |
| Track Me | Partial | Consent-started session, optional user-requested last location, expiry, stop/revoke and location deletion; no contact sharing |
| Tap Me | Partial | Starts from a Raahi route and derives check-in count from route duration and the original risk equation; reminders run only while the app is open, with no external escalation |
| SAFE SPOT | Nearby search | Google Places results for hospitals, police stations, parks, public spaces, restaurants, and cafes after the user confirms a pin. The BEFIKR directory is available as a separate filter. Users can open listings in Google Maps for current details and directions. |
| Offline | Partial | PWA shell caching, explicit local-only report drafts, browser-local script UI; API actions need a connection |
| Admin | Functional local tools | Report moderation, appeal handling, Safe Spot administration, aggregate counts, audit log, role gate |

**This build is a development foundation, not a production emergency service.** The app labels all demo and unavailable behavior. A local event record and a prepared text are not a dispatched SOS; a route is not certified safe; a blank map is not evidence of safety.

## Project map

- `web/` — responsive PWA, design system, module screens and offline shell.
- `backend/app/main.py` — FastAPI routes, access controls and service orchestration.
- `backend/app/risk.py` — configurable segment/route scoring and comparisons.
- `backend/app/db.py` — local SQLite schema and connection lifecycle.
- `backend/tests/` — risk and API workflow tests.
- `database/postgresql/001_initial_schema.sql` — PostGIS production-schema reference; not wired to the development API adapter.
- `docs/` — architecture, API, database, privacy, setup, testing and rollout notes.

## Operational and security notes

- Never expose the API publicly with the development token secret or an ephemeral SQLite disk.
- Configure HTTPS, a managed PostgreSQL/PostGIS database, backups, rate limiting, monitoring, secrets, retention workers and an operational incident response process before any real users.
- Set a strict `BEFIKR_CORS_ORIGINS` value when hosting. The local default only allows `http://localhost:8000`.
- Data is sensitive even when a report is anonymous to other users. Restrict staff accounts, audit access and define retention with qualified privacy/legal review.
- Indian privacy and emergency-service obligations require qualified legal review for the specific release and operating model. This repository does not claim compliance certification.

Read [the deployment and limitations guide](docs/deployment.md) before putting this on a network.
