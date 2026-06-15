---
title: GoTo Bengaluru
emoji: 🗺️
colorFrom: red
colorTo: yellow
sdk: docker
pinned: false
---

# GoTo Bengaluru

Discover places to go in Bengaluru — cafes, parks, breweries, events, and more — via a swipe-style interface powered by semantic search.

## Project Structure

```
Goto/
├── backend/
│   ├── api.py               # FastAPI server — wraps retrieval.search()
│   ├── retrieval.py         # Semantic search + ranking pipeline
│   ├── build_dataset.py     # Merges scraped sources → data/dataset.json
│   ├── build_embeddings.py  # Computes embeddings → data/embeddings.json
│   ├── refresh.py           # Runs all scrapers + rebuild in sequence
│   ├── requirements.txt     # Python dependencies
│   ├── scrapers/
│   │   ├── maps_cafe_scraper.py
│   │   ├── maps_places_scraper.py
│   │   └── luma_scraper.py
│   └── data/
│       ├── dataset.json       # Unified place + event records
│       ├── embeddings.json    # Pre-computed sentence embeddings
│       ├── maps_cafes.json
│       ├── maps_parks.json
│       ├── maps_breweries.json
│       ├── maps_attractions.json
│       └── luma_events.json
├── frontend/                # React + Vite + Tailwind
│   └── src/
│       ├── api.ts           # Fetch wrapper (reads VITE_API_URL)
│       ├── App.tsx
│       └── components/
├── Dockerfile               # For Hugging Face Spaces deployment
└── specs/                   # Design docs
```

## Tech Stack

- **Frontend**: React, TypeScript, Vite, Tailwind CSS, Framer Motion — deployed on Vercel
- **Backend**: FastAPI + sentence-transformers (`all-MiniLM-L6-v2`) — deployed on Hugging Face Spaces (Docker)

## Local Development

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev   # proxies /api → http://127.0.0.1:8000
```

### Refreshing Data

```bash
cd backend
python refresh.py               # scrape + rebuild dataset + embeddings
python refresh.py --skip-embed  # scrape only, skip re-embedding
python refresh.py --skip-scrape # rebuild dataset + embeddings from existing raw files
```

## Deployment

### Frontend → Vercel
1. Import repo, set root directory to `frontend`
2. Add env var: `VITE_API_URL=https://your-space.hf.space`

### Backend → Hugging Face Spaces (Docker)
1. Create a new Space with SDK: **Docker**
2. Push this repo to the Space
3. Set env var in Space settings: `ALLOWED_ORIGINS=https://your-app.vercel.app`
