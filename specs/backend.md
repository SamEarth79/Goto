# Backend Spec — GoTo Bengaluru

Status snapshot for the frontend agent. This describes what currently exists
in the `Goto/` backend, the data it produces, and the retrieval pipeline the
frontend will need to call.

## What exists today

All of the following are Python scripts/files in `Goto/` (run inside the
`.venv` virtualenv):

| File | Purpose |
| --- | --- |
| `luma_scraper.py` | Scrapes upcoming Bengaluru events from luma.com → `luma_events.json` |
| `maps_cafe_scraper.py` / `maps_places_scraper.py` | Scrapes Google Maps (cafes, parks, breweries, tourist attractions) → `maps_*.json` |
| `build_dataset.py` | Merges all scraped sources into one unified schema → `dataset.json` (240 records) |
| `build_embeddings.py` | Computes a local sentence-transformer embedding for every record → `embeddings.json` |
| `retrieval.py` | The search/ranking pipeline — `search(query_text, user_lat, user_lng, top_n)` |

**No HTTP API exists yet.** `retrieval.py` is currently a CLI script
(`search()` function + `argparse` entrypoint). The frontend will need a thin
API layer (e.g. Flask/FastAPI) wrapping `search()` — this is not yet built
and is the main gap between this spec and a working app.

## Unified dataset schema (`dataset.json`)

Every record (place or event) has this shape:

```json
{
  "id": "cafe-0",                 // unique string id, format "<source>-<index>"
  "kind": "place",                 // "place" | "event"
  "source": "cafe",                // "cafe" | "park" | "brewery" | "attraction" | "luma"
  "name": "Dyu Art Cafe",
  "category": "Art cafe",          // free-text category/tag (events: comma-joined Luma categories)
  "description": "Mellow global cafe & art gallery",
  "address": "KHB MIG Colony, ...",
  "rating": 4.4,                   // 0-5 float, null for events
  "latitude": 12.9373076,
  "longitude": 77.6176544,
  "image_url": "https://...",
  "source_url": "https://maps.google.com/...",  // or luma.com/<slug> for events
  "hours": "Open · Closes 10:30 pm",  // places only, null for events; free-text, not machine-parsed
  "start_at": null,                 // events only, ISO 8601 UTC
  "end_at": null,                   // events only, ISO 8601 UTC
  "is_free": null                   // events only, bool|null
}
```

Counts: 65 cafes, 64 parks, 43 breweries, 48 attractions, 20 events = 240 total.

Notes / known gaps:
- `address` is occasionally empty for places where Google's listing only
  showed category + description on the first line.
- `hours` is a raw string (e.g. `"Open · Closes 10:30 pm"`) — not parsed into
  structured open/close times. Don't rely on it for filtering yet.
- Event `description` can be long (full Luma event body, markdown-ish plain
  text with `[media: <url>]` placeholders for embedded images).
- Re-run `build_dataset.py` + `build_embeddings.py` any time the scraped
  `*.json` source files are refreshed — `embeddings.json` must stay in sync
  with `dataset.json` (matched by `id`).

## Retrieval pipeline (`retrieval.py`)

### `search(query_text, user_lat=None, user_lng=None, top_n=30, model=None) -> list[dict]`

Returns a list of `dataset.json` records (full record dict, all fields above)
plus an added `"score"` float field, ordered for display as a swipe deck.

Pipeline steps:

1. **Embed query** — `query_text` is embedded with the same local model used
   to build `embeddings.json` (`all-MiniLM-L6-v2`, via `sentence-transformers`,
   no API key/cost).
2. **Hard filter** — events whose `end_at` (or `start_at` if no `end_at`) is
   in the past are dropped. Places are never filtered out at this stage.
3. **Scoring** — weighted blend per candidate:
   - `semantic_score` = cosine similarity between query and record embedding (0–1)
   - `proximity_score` = `1 / (1 + distance_km)` via haversine, using
     `user_lat`/`user_lng` vs record's `latitude`/`longitude`
   - `rating_score` = `(rating or 3.5) / 5`
   - If location is provided: `0.6*semantic + 0.25*proximity + 0.15*rating`
   - If location is not provided: `0.8*semantic + 0.2*rating` (proximity dropped)
4. **Rank** — sort by `score` descending, take top `top_n`.
5. **Diversity shuffle** — re-order so the same `category` doesn't appear more
   than 2 times in a row (better swipe variety without hurting overall ranking).

### Expected frontend inputs (minimal-friction UX, as discussed)

- **Free-text query** (required) — "what are you in the mood for?"
- **User location** (optional) — `lat`/`lng`, ideally via browser geolocation

### CLI usage (for testing without an API)

```bash
cd Goto
.venv/bin/python retrieval.py "chill rooftop place to read with good coffee"
.venv/bin/python retrieval.py "live music tonight" --lat 12.97 --lng 77.59 --top 8
```

## Suggested next step for an API layer

Wrap `search()` in a minimal HTTP endpoint, e.g.:

```
GET /api/search?q=<text>&lat=<float>&lng=<float>&top=<int>
→ 200 OK
[ { ...record fields..., "score": 0.563 }, ... ]
```

Loading the `SentenceTransformer` model is the slow part (~1-2s) — the API
process should load it once at startup and reuse it across requests (pass as
`model=` to `search()`), not reload per-request.
