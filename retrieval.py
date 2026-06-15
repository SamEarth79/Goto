"""
Semantic retrieval pipeline for GoTo Bengaluru.

Pipeline:
    1. Embed the user's free-text query (same local model used offline).
    2. Hard filter: drop events that have already ended.
    3. Score candidates: weighted blend of semantic similarity,
       proximity to the user, and rating.
    4. Sort by score, then apply a light diversity shuffle so the swipe
       deck doesn't show the same category back-to-back.

Run a quick demo:
    python3 retrieval.py "chill rooftop place to read with good coffee"
    python3 retrieval.py "live music tonight" --lat 12.97 --lng 77.59
"""

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).parent
DATASET_FILE = ROOT / "dataset.json"
EMBEDDINGS_FILE = ROOT / "embeddings.json"

# Weights when the user's location IS known.
WEIGHTS_WITH_LOCATION = {"semantic": 0.6, "proximity": 0.25, "rating": 0.15}
# Weights when no location is available (proximity dropped, redistributed).
WEIGHTS_NO_LOCATION = {"semantic": 0.8, "proximity": 0.0, "rating": 0.2}

DEFAULT_RATING = 3.5  # used for items with no rating (e.g. events)


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    r = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))  # embeddings are pre-normalized


def event_has_ended(record: dict, now: datetime) -> bool:
    if record["kind"] != "event":
        return False
    end_at = record.get("end_at") or record.get("start_at")
    if not end_at:
        return False
    end_dt = datetime.fromisoformat(end_at.replace("Z", "+00:00"))
    return end_dt < now



def search(
    query_text: str,
    user_lat: float | None = None,
    user_lng: float | None = None,
    top_n: int = 30,
    model: SentenceTransformer | None = None,
) -> list[dict]:
    records = {r["id"]: r for r in json.loads(DATASET_FILE.read_text())}
    embeddings_data = json.loads(EMBEDDINGS_FILE.read_text())
    embeddings = embeddings_data["embeddings"]

    if model is None:
        model = SentenceTransformer(embeddings_data["model"])

    query_vec = model.encode([query_text], normalize_embeddings=True)[0].tolist()

    has_location = user_lat is not None and user_lng is not None
    weights = WEIGHTS_WITH_LOCATION if has_location else WEIGHTS_NO_LOCATION

    now = datetime.now(timezone.utc)
    scored = []

    for record_id, record in records.items():
        if event_has_ended(record, now):
            continue

        semantic_score = cosine(query_vec, embeddings[record_id])

        if has_location and record.get("latitude") is not None and record.get("longitude") is not None:
            distance_km = haversine_km(user_lat, user_lng, record["latitude"], record["longitude"])
            proximity_score = 1 / (1 + distance_km)
        else:
            proximity_score = 0.0

        rating_score = (record.get("rating") or DEFAULT_RATING) / 5

        final_score = (
            weights["semantic"] * semantic_score
            + weights["proximity"] * proximity_score
            + weights["rating"] * rating_score
        )

        scored.append({**record, "score": final_score})

    scored.sort(key=lambda r: r["score"], reverse=True)
    return scored[:top_n]


def main():
    parser = argparse.ArgumentParser(description="Search GoTo Bengaluru dataset.")
    parser.add_argument("query", help="What are you in the mood for?")
    parser.add_argument("--lat", type=float, default=None, help="User latitude")
    parser.add_argument("--lng", type=float, default=None, help="User longitude")
    parser.add_argument("--top", type=int, default=10, help="Number of results to show")
    args = parser.parse_args()

    results = search(args.query, args.lat, args.lng, top_n=args.top)

    for r in results:
        print(f"[{r['score']:.3f}] {r['name']} ({r['kind']}/{r['category']})")
        if r.get("address"):
            print(f"    {r['address']}")


if __name__ == "__main__":
    main()
