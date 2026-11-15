# Raahi synthetic route examples

The user-provided JSON and CSV files are stored unchanged in
`backend/fixtures/delhi_synthetic_route_safety_dataset.{json,csv}`. The JSON is the
runtime source; the CSV is the matching original for review. These are project
fixtures, separate from the private runtime database under `backend/data/`.

The supplied version has 135 records: 45 directed area pairs, each with Day,
Evening and Night examples. It contains 65 GREEN and 70 YELLOW labels, and **no
RED records**. Every record explicitly declares
`SYNTHETIC_DEMO_NOT_REAL_INCIDENT_OR_POLICE_DATA`.

## Meaning and matching

- The supplied `safety_label` is displayed directly. No label or missing RED
  example is invented. A higher `safety_score_synthetic_0_100` means higher
  *synthetic safety*, unlike the existing risk engine where higher means worse.
- `Day` is 06:00–18:00, `Evening` is 18:00–22:00, and `Night` is 22:00–06:00 in
  Delhi time (UTC+05:30). Start times are inclusive and end times exclusive.
  The `current` choice uses the current time in Delhi, regardless of server timezone.
- Matching is by complete directed area pair and time band, ignoring case and
  repeated whitespace. A name followed only by comma-separated Delhi/New Delhi/
  NCT of Delhi/India suffixes can also match. Postal codes may follow those suffixes.
  There is no fuzzy matching, reverse-route inference, coordinate-based guessing,
  or partial-name matching.
- Unknown places, arbitrary map pins and missing pairs produce `matched: false`
  and `record: null`, never a guessed safety colour.
- Files with missing fields, invalid numeric ranges, nonfinite numbers, invalid
  labels/status, duplicate pairs, inconsistent identifiers or incomplete time
  bands fail closed. An unavailable dataset returns `available: false`.

The dataset supplies no coordinates, street geometry, collection dates or verified
incident evidence. An area-pair match cannot establish which Google Maps alternative
is safer, nor colour individual road segments. Synthetic distance and duration are
retained only in the labelled demo response; provider distance, duration and geometry remain
unchanged. Live `risk_score`, `confidence`, `classification`, `comparison_score`,
navigation and Tap Me inputs do not receive synthetic ratings.

## API

Both endpoints use the normal BEFIKR sign-in token and work without Google keys or
external map requests:

- `GET /api/routes/safety-demo` returns `source`, `available`, `notice`,
  `route_pairs`, `time_bands` and `counts` (rows, pairs, and label counts).
- `POST /api/routes/safety-demo` accepts `origin`, `destination` and `time_band`
  (`current`, `Day`, `Evening`, or `Night`). It returns `source`, `available`,
  `matched`, `notice`, the resolved `time_band` / `time_window`, and the original
  matched `record` or `null`.
- `POST /api/routes/alternatives` accepts optional `demo_time_band` with the same
  choices and adds a separate top-level `safety_demo` lookup result. It does not
  add synthetic ratings to the actual `routes` array.
- `GET /api/routes/data-status` includes a `synthetic_demo` summary while keeping
  the verified safety-data state as `not configured`.

Example request:

```json
{"origin":"Connaught Place","destination":"India Gate","time_band":"Night"}
```

The supplied example is YELLOW with synthetic safety score 56. During Day, the same
pair is GREEN with score 81. These are illustrative labels, not current Delhi
safety observations.

To update examples, replace both fixture files with consistent exports, preserving
the explicit synthetic status. Live route safety will require a separate validated
geospatial source that can be matched to actual road segments.

In the app, open Raahi and scroll to **Preview route safety colours**. Choose a
route pair and Delhi time band, then select **Show demo colour**. Matching named
route searches also display an area-pair demo result beside the real route options.
The route polylines retain their normal selection colours because these files
contain no street geometry. The demo preview requires sign-in but no Google key.
