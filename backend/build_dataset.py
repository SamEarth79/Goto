"""
Merge all scraped sources (cafes, parks, breweries, attractions, Luma events)
into a single dataset with a unified schema, ready for embedding.

Run:
    python3 build_dataset.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
OUTPUT_FILE = DATA_DIR / "dataset.json"

PLACE_FILES = {
    "cafe": "maps_cafes.json",
    "park": "maps_parks.json",
    "brewery": "maps_breweries.json",
    "attraction": "maps_attractions.json",
}


def load(filename: str) -> list[dict]:
    return json.loads((DATA_DIR / filename).read_text())


def build_place_record(source: str, item: dict, index: int) -> dict:
    return {
        "id": f"{source}-{index}",
        "kind": "place",
        "source": source,
        "name": item.get("name"),
        "category": item.get("category"),
        "description": item.get("description"),
        "address": item.get("address"),
        "rating": item.get("rating"),
        "latitude": item.get("latitude"),
        "longitude": item.get("longitude"),
        "image_url": item.get("image_url"),
        "source_url": item.get("maps_url"),
        "hours": item.get("hours"),
        "start_at": None,
        "end_at": None,
        "is_free": None,
    }


def build_event_record(item: dict, index: int) -> dict:
    location = item.get("location") or {}
    categories = item.get("categories") or []
    ticket_info = item.get("ticket_info") or {}

    return {
        "id": f"event-{index}",
        "kind": "event",
        "source": "luma",
        "name": item.get("name"),
        "category": ", ".join(c.get("name") for c in categories if c.get("name")) or None,
        "description": item.get("description"),
        "address": location.get("address") or location.get("short_address"),
        "rating": None,
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
        "image_url": item.get("cover_url"),
        "source_url": item.get("url"),
        "hours": None,
        "start_at": item.get("start_at"),
        "end_at": item.get("end_at"),
        "is_free": ticket_info.get("is_free"),
    }


def main():
    records = []

    for source, filename in PLACE_FILES.items():
        for i, item in enumerate(load(filename)):
            records.append(build_place_record(source, item, i))

    for i, item in enumerate(load("luma_events.json")):
        records.append(build_event_record(item, i))

    OUTPUT_FILE.write_text(json.dumps(records, indent=2, ensure_ascii=False))
    print(f"Saved {len(records)} records to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
