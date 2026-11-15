# Test coverage and results

## Run

From `backend/`:

```powershell
python -m unittest discover -s tests -v
```

The suite uses isolated workspace-local SQLite files and does not open a network socket. It covers risk input validation, missing data, normalized model coverage, route scoring and comparison; account/session revocation; report privacy; report review transitions; report aggregation only after independent validated submissions; duplicate-review signals; appeal reopening and audit; SOS delivery-state honesty and cancellation; Track Me consented location removal; Tap Me responses; admin role rejection; Safe Spot source-backed directory search; and the demo mapping disclosure.

## Verified in this workspace

- 60 Python unit/service workflow tests pass with `BEFIKR_MAPPING_PROVIDER=demo` (including 12 synthetic-dataset tests 10 CSV proximity tests and 4 Safe Spot route tests).
- `python -m compileall -q backend/app backend/tests` passes.
- `node --check web/app.js` passes.
- FastAPI OpenAPI generation succeeds, including GET and POST `/api/routes/safety-demo`.

The synthetic-dataset checks cover CSV/JSON agreement, all 135 original scores and labels,
Delhi time boundaries, missing/reversed pairs, invalid files, and isolation from live
route risk and geometry. A JavaScript VM smoke check renders all 135 demo ratings,
the 45 route selections, missing-data messaging and escaped content. These checks do
not replace a visual browser/device test. The local server on port 8001 was checked
for health, the new endpoints and the updated interface bundle.

CSV proximity tests cover known Haversine distances, invalid coordinates, all category
filters, filtering before rounding, the inclusive radius boundary, nearest-first ordering,
185 source rows with 181 usable coordinates, and independence from Google and SQLite.
JavaScript VM smoke checks cover CSV list/detail rendering, source labels, text search
and the missing-coordinate note. The original CSV bytes are preserved.

## Not yet covered

These are service-level workflow tests, not full HTTP, browser, Android/iOS, offline-device, screen-reader or load end-to-end tests. A local browser smoke check could not connect to the attempted development server in this environment. The deck’s public-data and helpline references also have not been independently validated or connected. Do not treat this as public-release acceptance testing.

Before release, add HTTP contract and concurrency tests, browser/device journeys, offline/online synchronization, permission-denial and background/battery tests, accessibility checks, security/abuse tests, provider failure simulations and database migration/backup restore tests. Use only test recipients for notification delivery verification.

Safe Spot route checks also run with `node --test web/tests/safe-spot-routing.test.cjs`.
All five frontend checks pass: normal place labels, correct endpoints, in-app path
metrics, provider failure/retry, missing origin and stale-request handling. A live
FOSSGIS foot request between two public Connaught Place points returned 0.49 km,
7 min, 43 geometry points and 10 steps. No real emergency actions were exercised.

Safe Spot frontend checks also verify removal of the source selector, Google Maps
links below the results, five searches for All and one matching search per category,
the chosen location in each URL, empty results and loading behavior.

The additional CSV checks cover both incoming header layouts, all 60 rows, map
links, missing phone handling, landmark/market mapping, Rohini searches and
deduplication without losing branch or category-specific matches.

Baat Banao recording tests cover all 20 folders and 141 local assets, numeric
ordering, character/scenario/language mapping, generated catalog consistency,
missing sequence numbers, original transcript preservation and silent user turns.
Run all seventeen frontend tests with `node --test web/tests/*.test.cjs`. Playback tests
cover supplied file URLs, user turns, end-of-script, replay, stale callbacks,
ringtone looping, and removal of pending-script canned dialogue. They use a mock
audio player; they do not claim manual listening or real-device decoding.

Transcript regression checks verify all 19 pasted scripts against their original
source text, the requested Worried Sister Hindi deletion, all ten Hindi/Hinglish
pairs and explicit silent user roles in sister-to-sister scripts. All 141 caller
turns have their supplied audio; all user turns are text-only. Frontend checks
verify Hindi/Hinglish switching for every turn without changing the audio.

Raaz adds eight isolated HTTP evidence tests and six frontend checks. Coverage
includes authenticated upload/retrieval, file format/size rejection and cleanup,
owner/reviewer isolation, transaction-bound report attachments, draft deletion,
account-file cleanup, repeatable schema upgrades, incident map confirmation,
Google Places result selection and submission failure recovery. The Windows
HTTP tests need local socket access for the test event loop and are run outside
the socket-restricted sandbox, with temporary databases and no real user reports.
The Android file-chooser addition has not been compiled or device-tested because
no Android SDK/Java toolchain is installed.
