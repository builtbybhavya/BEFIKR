# Raaz evidence and location

Step 2 accepts up to three JPEG/PNG/WebP photos or MP4/WebM videos, each up to
10 MiB. A selected file can be previewed or removed before submission. Files
remain in the in-memory draft while moving between steps. Uploads happen only
when the user chooses Submit report at the review step. A failed upload keeps
the draft; evidence is not silently added to the text-only offline queue.

Step 3 offers current location, an adjustable map pin, and Google Places name
search. A Places result opens the incident map picker for confirmation. Selecting
an incident point never modifies Raahi's pickup/drop-off. The confirmed label,
coordinates and optional Google Place ID are sent only with report submission.
Manual coordinates remain available. Both latitude and longitude must be supplied
together; zero-valued coordinates are valid.

Name suggestions reuse `/api/places/autocomplete` and `/api/places/resolve` with
the existing session-token flow. Live searches require `GOOGLE_MAPS_SERVER_KEY`
with Places API (New) enabled. Google maps/embedded previews use their existing
browser/embed keys. The map pin fallback works with the existing Leaflet map.
Missing-key errors are shown in the search suggestions panel.

## Private storage and API

- `POST /api/evidence` accepts a raw file body, a supported Content-Type and an
  optional URL-encoded `X-Filename` header. It requires a sign-in bearer token.
- Uploads are bounded while streaming. Image contents are checked by Pillow;
  videos receive container-header checks. These are format checks, not malware
  scanning, forensic verification or full video decoding.
- File bytes live under the configured `BEFIKR_DATA_DIR/evidence/` (normally
  `backend/data/evidence/`), outside the public web root. Random IDs are used as
  disk names, with safe original filenames in SQLite metadata. No encryption at
  rest or cloud object storage is claimed.
- Up to twelve unsubmitted attachments per owner can be staged. Draft removal
  deletes that owner's unsubmitted file. A submitted file cannot be removed by
  the draft delete operation. Account deletion removes its private files too.
- `GET /api/evidence/{id}` permits the owner, or admin/moderator review of a
  submitted attachment. Other accounts and unauthenticated requests are denied.
  Responses use no-store, nosniff and attachment content disposition. The frontend
  retrieves authenticated blobs for image/video preview, then revokes object URLs.
- `DELETE /api/evidence/{id}` removes an owned unsubmitted attachment.
- `POST /api/reports` accepts up to three unique `evidence_ids`. Ownership,
  existence and unattached state are checked, then attachment links and report
  creation commit in the same transaction. Named-location fields are
  `location_label` and `location_place_id`.
- `GET /api/reports` returns the owner's attachment metadata and selected location
  label; it does not expose the raw coordinates in that list. Authorised report
  review includes attachment controls. Reports remain private and pending review.

Schema additions preserve existing reports and are repeatable. Files are excluded
from Git through the existing runtime-data ignore rule. A local deployment must
retain its data directory when restarting or moving servers. Staged files from
an abandoned/refreshed draft may need operational cleanup; they are never public.

## Android wrapper

`MainActivity` now handles the WebView file chooser, validates the top-level
BEFIKR origin and accepts user-selected content URIs. File URL access remains
disabled. No broad storage permission is added. The implementation follows the
[Android file chooser API](https://developer.android.com/reference/android/webkit/WebChromeClient.FileChooserParams).
The APK must be rebuilt to include this wrapper change. No Android SDK/Java
toolchain is available in this workspace, so this Android change is not compiled
or device-tested here.

## Verification

Eight isolated HTTP tests cover upload/link/read/delete, file validation/size,
cross-account access, reviewer access, duplicate/foreign attachment IDs, location
pair validation, account deletion and repeatable schema upgrade. Six frontend
checks cover file selection across steps, upload/submission ordering, failure
recovery, map confirmation and Places selection into Raaz. These checks do not
replace real-device geolocation or live Google Places testing with a valid key.
