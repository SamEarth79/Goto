"""
Scraper for cafes in Bengaluru on Google Maps, using Playwright.

Google Maps' search-results panel is rendered client-side (no clean JSON API
response for the list itself in a logged-out session), so this script drives
a headless Chromium browser, scrolls the results feed to load more places,
and parses each result card's DOM for all visible details.

Run:
    python3 maps_cafe_scraper.py
"""

import json
import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

SEARCH_URL = "https://www.google.com/maps/search/cafes+in+bengaluru?hl=en"
OUTPUT_FILE = Path(__file__).parent / "maps_cafes.json"

# Stop once we've collected roughly this many cafes (Google Maps keeps
# loading more as you scroll, but the list isn't infinite).
TARGET_COUNT = 60
MAX_SCROLL_ATTEMPTS = 40


def parse_card(article) -> dict:
    name = article.get_attribute("aria-label") or ""

    link = article.query_selector("a.hfpxzc")
    href = link.get_attribute("href") if link else None

    place_id = None
    latitude = None
    longitude = None
    if href:
        coord_match = re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", href)
        if coord_match:
            latitude = float(coord_match.group(1))
            longitude = float(coord_match.group(2))
        cid_match = re.search(r"!1s(0x[0-9a-fA-F]+:0x[0-9a-fA-F]+)", href)
        if cid_match:
            place_id = cid_match.group(1)

    rating = None
    rating_el = article.query_selector(".MW4etd")
    if rating_el:
        try:
            rating = float(rating_el.inner_text().strip())
        except ValueError:
            pass

    image_url = None
    img_el = article.query_selector(".SpFAAb img, img")
    if img_el:
        src = img_el.get_attribute("src") or ""
        image_url = (src + "=w800") if "googleusercontent.com" in src else src or None

    # Top-level detail rows (category/address, description, hours) are each
    # a direct-child ".W4Efsd" of the info container. The first row also
    # holds the star rating, so skip it. The category/address row itself
    # contains two nested ".W4Efsd" blocks.
    info = article.query_selector(".UaQhfb")
    top_rows = info.query_selector_all(":scope > .W4Efsd") if info else []

    text_lines = []
    for row in top_rows:
        if row.query_selector(".AJB7ye"):
            continue
        sub_rows = row.query_selector_all(":scope > .W4Efsd")
        if sub_rows:
            for sub in sub_rows:
                text = sub.inner_text().strip()
                if text:
                    text_lines.append(text)
        else:
            text = row.inner_text().strip()
            if text:
                text_lines.append(text)

    category = None
    address = None
    description = None
    hours = None

    if text_lines:
        # First line is typically "Category · [a11y icon] · Address"
        parts = [p.strip() for p in text_lines[0].split("·") if p.strip()]
        if parts:
            category = parts[0]
        if len(parts) > 1:
            address = parts[-1]

        remaining = text_lines[1:]
        if remaining:
            # Last remaining line is usually the open/closed + hours status.
            if any(keyword in remaining[-1] for keyword in
                   ("Open", "Closed", "Closes", "Opens", "24 hours")):
                hours = remaining[-1]
                remaining = remaining[:-1]
            if remaining:
                description = " ".join(remaining)

    return {
        "name": name,
        "rating": rating,
        "category": category,
        "address": address,
        "description": description,
        "hours": hours,
        "image_url": image_url,
        "maps_url": href,
        "place_id": place_id,
        "latitude": latitude,
        "longitude": longitude,
    }


def main():
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(locale="en-US")
        page.goto(SEARCH_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)

        feed = page.query_selector('div[role="feed"]')
        if feed is None:
            raise RuntimeError("Could not find the results feed on the page.")

        for attempt in range(1, MAX_SCROLL_ATTEMPTS + 1):
            articles = feed.query_selector_all('div[role="article"]')
            for article in articles:
                card = parse_card(article)
                if card["name"] and card["name"] not in results:
                    results[card["name"]] = card

            print(f"Scroll {attempt}: {len(results)} unique cafes collected so far.")
            if len(results) >= TARGET_COUNT:
                break

            feed.evaluate("el => el.scrollBy(0, el.scrollHeight)")
            time.sleep(2)

        browser.close()

    cafes = list(results.values())
    OUTPUT_FILE.write_text(json.dumps(cafes, indent=2, ensure_ascii=False))
    print(f"Saved {len(cafes)} cafes to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
