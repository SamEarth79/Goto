"""
Compute embeddings for every record in dataset.json using a local,
free sentence-transformers model (no API key, runs on CPU).

Run:
    python3 build_embeddings.py
"""

import json
from pathlib import Path

from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).parent
DATASET_FILE = ROOT / "data" / "dataset.json"
OUTPUT_FILE = ROOT / "data" / "embeddings.json"

MODEL_NAME = "all-MiniLM-L6-v2"


def record_text(record: dict) -> str:
    parts = [record.get("name"), record.get("category"), record.get("description")]
    return ". ".join(p for p in parts if p)


def main():
    records = json.loads(DATASET_FILE.read_text())

    print(f"Loading model '{MODEL_NAME}' ...")
    model = SentenceTransformer(MODEL_NAME)

    texts = [record_text(r) for r in records]
    print(f"Embedding {len(texts)} records ...")
    vectors = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)

    embeddings = {r["id"]: vec.tolist() for r, vec in zip(records, vectors)}

    OUTPUT_FILE.write_text(json.dumps({
        "model": MODEL_NAME,
        "embeddings": embeddings,
    }))
    print(f"Saved {len(embeddings)} embeddings to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
