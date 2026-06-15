"""Clean two-view actuarial demo: Underwriting Desk + Watch it Learn.

Run:
    uvicorn demo.desk.app:app --reload --port 8000
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from healthrl.underwriting_bandit import preprocess_cambodia_data  # noqa: E402

DESK_DIR = Path(__file__).resolve().parent
STATIC_DIR = DESK_DIR / "static"

app = FastAPI(title="Adaptive Underwriting Desk", version="1.0.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Load dataset once at startup (df carries un-normalized feature columns).
X_FULL, DF_RAW, FEATURES = preprocess_cambodia_data()

THESIS_RESULTS_PATH = ROOT / "demo" / "static" / "thesis_results.json"


def load_canonical_headline() -> dict[str, Any]:
    """Authoritative 20-seed headline, read from thesis_results.json (no fallback)."""
    data = json.loads(THESIS_RESULTS_PATH.read_text(encoding="utf-8"))
    exp005 = data["exp005"]
    ceiling = next(r for r in data["ladder"]["rows"] if r["policy"] == "AlwaysRATED")
    return {
        "lift_pct": exp005["lift_pct"],
        "cohen_d": exp005["reward_cohen_d"],
        "p_value": exp005["reward_p"],
        "n_seeds": 20,
        "comparator": "Static XGB",
        "source": exp005["source"],
        "scope": data["_meta"]["scope"],
        "ceiling_policy": ceiling["policy"],
        "ceiling_note": ceiling["note"],
    }


CANONICAL_HEADLINE = load_canonical_headline()


def _row_to_applicant(row: pd.Series) -> dict[str, Any]:
    """Convert a DataFrame row to a JSON-serialisable applicant dict."""
    conds = str(row.get("pre_existing_conditions", "") or "")
    if conds.lower() == "nan":
        conds = ""
    return {
        "age": int(row["age"]),
        "gender": str(row["gender"]),
        "bmi": float(row["bmi"]),
        "is_smoking": int(row["is_smoking"]),
        "alcohol_use": int(row["alcohol_use"]),
        "is_exercise": int(row["is_exercise"]),
        "has_family_history": int(row["has_family_history"]),
        "monthly_income_usd": float(row["monthly_income_usd"]),
        "pre_existing_conditions": conds,
        "region": str(row["region"]),
        "occupation": str(row["occupation"]),
        "education": str(row.get("education", "Primary")),
        "wealth_quintile": str(row.get("wealth_quintile", "Middle")),
        "self_reported_health": str(row.get("self_reported_health", "Fair")),
        "mortality_multiplier": float(row["mortality_multiplier"]),
    }


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/applicant/fields")
async def applicant_fields() -> dict[str, Any]:
    return {
        "regions": sorted(DF_RAW["region"].dropna().unique().tolist()),
        "occupations": sorted(DF_RAW["occupation"].dropna().unique().tolist()),
        "educations": ["No education", "Primary", "Secondary", "Higher"],
        "wealth_quintiles": ["Poorest", "Poorer", "Middle", "Richer", "Richest"],
        "health_statuses": ["Poor", "Fair", "Good"],
        "conditions": [
            "Hypertension", "Diabetes", "Heart Disease", "COPD/Asthma",
            "Arthritis", "TB", "Hepatitis B",
        ],
    }


@app.get("/api/applicant/random")
async def random_applicant() -> dict[str, Any]:
    idx = int(np.random.default_rng().integers(len(DF_RAW)))
    return {"applicant": _row_to_applicant(DF_RAW.iloc[idx]), "index": int(idx)}


@app.get("/api/canonical")
async def canonical() -> dict[str, Any]:
    return CANONICAL_HEADLINE
