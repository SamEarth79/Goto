"""
Weekly data refresh script for GoTo Bengaluru.

Runs all scrapers in sequence, then rebuilds dataset.json and embeddings.json.

Run:
    python3 refresh.py

Options:
    --skip-scrape   Skip scraping and only rebuild dataset + embeddings (useful
                    if the raw JSON files are already up to date).
    --skip-embed    Skip re-embedding and only re-scrape + rebuild dataset.json.
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
PYTHON = sys.executable


def run(label: str, script: Path):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    t0 = time.time()
    result = subprocess.run([PYTHON, str(script)], cwd=ROOT)
    elapsed = time.time() - t0
    if result.returncode != 0:
        print(f"\n[ERROR] {script.name} failed (exit {result.returncode}). Aborting.")
        sys.exit(result.returncode)
    print(f"\n  Done in {elapsed:.1f}s")


def main():
    parser = argparse.ArgumentParser(description="Refresh GoTo Bengaluru data.")
    parser.add_argument("--skip-scrape", action="store_true", help="Skip all scrapers")
    parser.add_argument("--skip-embed", action="store_true", help="Skip embedding step")
    args = parser.parse_args()

    t_start = time.time()

    if not args.skip_scrape:
        run("Scraping cafes (Google Maps)", ROOT / "scrapers" / "maps_cafe_scraper.py")
        run("Scraping parks, breweries & attractions (Google Maps)", ROOT / "scrapers" / "maps_places_scraper.py")
        run("Scraping Luma events", ROOT / "scrapers" / "luma_scraper.py")
        run("Building dataset.json", ROOT / "build_dataset.py")
    else:
        print("\n[--skip-scrape] Skipping all scrapers and dataset build.")

    if not args.skip_embed:
        run("Building embeddings.json", ROOT / "build_embeddings.py")
    else:
        print("\n[--skip-embed] Skipping embedding step.")

    total = time.time() - t_start
    print(f"\n{'='*60}")
    print(f"  Refresh complete in {total/60:.1f} min")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
