"""
Scraper for Bengaluru events listed on Luma (https://luma.com/bengaluru).

Strategy:
1. Fetch the Bengaluru discovery page and pull the embedded __NEXT_DATA__ JSON,
   which contains a list of events with most metadata already filled in.
2. For each event, fetch its individual event page (https://luma.com/<slug>)
   and pull its __NEXT_DATA__ JSON to get the full description and any
   additional details not present on the listing page.
3. Merge everything into a single dict per event and dump the full list to
   luma_events.json.

Run:
    python3 luma_scraper.py
"""

import json
import re
import time
import sys
from pathlib import Path

import requests

BENGALURU_URL = "https://luma.com/bengaluru"
OUTPUT_FILE = Path(__file__).parent / "luma_events.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}

NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S
)


def fetch_next_data(url: str) -> dict:
    """Download a Luma page and return its __NEXT_DATA__ JSON payload."""
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    match = NEXT_DATA_RE.search(resp.text)
    if not match:
        raise ValueError(f"Could not find __NEXT_DATA__ in {url}")
    return json.loads(match.group(1))


def doc_to_text(node) -> str:
    """Flatten a Luma rich-text 'description_mirror' doc into plain text."""
    if node is None:
        return ""

    if isinstance(node, list):
        return "\n".join(filter(None, (doc_to_text(child) for child in node)))

    if isinstance(node, dict):
        node_type = node.get("type")
        content = node.get("content")

        if node_type == "text":
            return node.get("text", "")

        if node_type in ("image", "video"):
            src = node.get("attrs", {}).get("src", "")
            return f"[media: {src}]" if src else ""

        if node_type in ("hardBreak", "horizontalRule"):
            return ""

        text = doc_to_text(content) if content else ""

        if node_type in ("paragraph", "heading", "blockquote",
                         "listItem", "bulletList", "orderedList"):
            return text

        return text

    return ""


def get_listing_events() -> list[dict]:
    """Get the events embedded on the Bengaluru discovery page."""
    data = fetch_next_data(BENGALURU_URL)
    return data["props"]["pageProps"]["initialData"]["data"]["events"]


def get_event_detail(slug: str) -> dict:
    """Get the full __NEXT_DATA__ payload for a single event page."""
    data = fetch_next_data(f"https://luma.com/{slug}")
    return data["props"]["pageProps"]["initialData"]["data"]


def build_event_record(listing_entry: dict, detail: dict) -> dict:
    event = detail.get("event", {})
    calendar = detail.get("calendar", {})
    geo = event.get("geo_address_info") or {}
    coordinate = event.get("coordinate") or {}
    ticket_info = detail.get("ticket_info") or {}

    hosts = []
    for host in detail.get("hosts") or []:
        hosts.append({
            "name": host.get("name"),
            "username": host.get("username"),
            "bio_short": host.get("bio_short"),
            "website": host.get("website"),
            "avatar_url": host.get("avatar_url"),
            "twitter_handle": host.get("twitter_handle"),
            "instagram_handle": host.get("instagram_handle"),
            "linkedin_handle": host.get("linkedin_handle"),
            "tiktok_handle": host.get("tiktok_handle"),
            "youtube_handle": host.get("youtube_handle"),
            "is_verified": host.get("is_verified"),
        })

    categories = [
        {"name": c.get("name"), "slug": c.get("slug")}
        for c in detail.get("categories") or []
    ]

    return {
        "api_id": event.get("api_id"),
        "url": f"https://luma.com/{event.get('url')}" if event.get("url") else None,
        "name": event.get("name"),
        "description": doc_to_text(detail.get("description_mirror")),
        "event_type": event.get("event_type"),
        "location_type": event.get("location_type"),
        "visibility": event.get("visibility"),
        "start_at": event.get("start_at"),
        "end_at": event.get("end_at"),
        "timezone": event.get("timezone"),
        "cover_url": event.get("cover_url"),
        "social_image_url": event.get("social_image_url"),
        "location": {
            "address": geo.get("full_address"),
            "short_address": geo.get("short_address"),
            "venue_name": geo.get("address"),
            "city": geo.get("city"),
            "region": geo.get("region"),
            "country": geo.get("country"),
            "sublocality": geo.get("sublocality"),
            "latitude": coordinate.get("latitude"),
            "longitude": coordinate.get("longitude"),
        },
        "calendar": {
            "name": calendar.get("name"),
            "slug": calendar.get("slug"),
            "description_short": calendar.get("description_short"),
            "website": calendar.get("website"),
            "avatar_url": calendar.get("avatar_url"),
            "twitter_handle": calendar.get("twitter_handle"),
            "instagram_handle": calendar.get("instagram_handle"),
            "linkedin_handle": calendar.get("linkedin_handle"),
        },
        "hosts": hosts,
        "categories": categories,
        "ticket_info": {
            "is_free": ticket_info.get("is_free"),
            "price": ticket_info.get("price"),
            "max_price": ticket_info.get("max_price"),
            "is_sold_out": ticket_info.get("is_sold_out"),
            "spots_remaining": ticket_info.get("spots_remaining"),
            "require_approval": ticket_info.get("require_approval"),
        },
        "guest_count": detail.get("guest_count"),
        "registration_availability": detail.get("registration_availability"),
        "waitlist_active": detail.get("waitlist_active"),
    }


def main():
    print(f"Fetching event listing from {BENGALURU_URL} ...")
    listing_events = get_listing_events()
    print(f"Found {len(listing_events)} events on the listing page.")

    results = []
    for i, entry in enumerate(listing_events, start=1):
        slug = entry.get("event", {}).get("url")
        name = entry.get("event", {}).get("name")
        if not slug:
            continue

        print(f"[{i}/{len(listing_events)}] Fetching details for '{name}' (/{slug}) ...")
        try:
            detail = get_event_detail(slug)
        except Exception as exc:
            print(f"  -> failed: {exc}", file=sys.stderr)
            continue

        results.append(build_event_record(entry, detail))

        # Be polite to Luma's servers.
        time.sleep(1)

    OUTPUT_FILE.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"Saved {len(results)} events to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
