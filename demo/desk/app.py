"""Clean two-view actuarial demo: Underwriting Desk + Watch it Learn.

Run:
    uvicorn demo.desk.app:app --reload --port 8000
"""
from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

DESK_DIR = Path(__file__).resolve().parent
STATIC_DIR = DESK_DIR / "static"

app = FastAPI(title="Adaptive Underwriting Desk", version="1.0.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
