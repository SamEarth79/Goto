"""
Minimal HTTP API wrapping retrieval.search() for the GoTo Bengaluru frontend.

Run:
    .venv/bin/uvicorn api:app --reload --port 8000
"""

import os

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer

from retrieval import search, EMBEDDINGS_FILE
import json

app = FastAPI(title="GoTo Bengaluru API")

_origins = os.environ.get("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

_model: SentenceTransformer | None = None


@app.on_event("startup")
def load_model():
    global _model
    model_name = json.loads(EMBEDDINGS_FILE.read_text())["model"]
    _model = SentenceTransformer(model_name)


@app.get("/api/search")
def api_search(
    q: str = Query(..., description="Free-text query, e.g. 'chill cafe with good coffee'"),
    lat: float | None = None,
    lng: float | None = None,
    top: int = 30,
):
    return search(q, user_lat=lat, user_lng=lng, top_n=top, model=_model)
