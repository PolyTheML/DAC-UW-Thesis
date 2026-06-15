# Underwriting Desk — Clean Demo Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a clean single-page FastAPI demo (`demo/desk/`) with two views — an "Underwriting Desk" applicant→decision card and a "Watch it Learn" online-learning showcase — reusing the real `healthrl` engine, with no new modelling math.

**Architecture:** One FastAPI app (`demo/desk/app.py`) serving one HTML page (`demo/desk/static/index.html`) with two views behind a top toggle. Heavy logic lives in plain, directly-testable modules: `scoring.py` (θ-based applicant scoring + model-level fairness) and `learning.py` (bandit-vs-static trajectories). The Desk scores with a representative trained LinUCB policy (θ from `demo/static/coefficients_linucb_seed42.json`); the Learn view runs `run_bandit` live and animates the trajectory client-side. Headline claims come only from `demo/static/thesis_results.json`; live numbers are single-seed and labelled illustrative.

**Tech Stack:** FastAPI + Pydantic + Jinja-free static serving, vanilla JS + Chart.js (vendored), pytest + `fastapi.testclient.TestClient`. Reuses `healthrl.underwriting_bandit` and `demo.pricing_engine`.

**Source of truth:** `docs/superpowers/specs/2026-06-15-underwriting-desk-rebuild-design.md` (committed `448f53f`). This plan implements that spec; section references (§N) point to it.

---

## Pre-flight (read before starting)

**Verified facts (do not re-derive):**
- θ matrix is `(4, 34)`; `coefficients_linucb_seed42.json["features"]` equals `preprocess_cambodia_data()`'s returned `FEATURES` **exactly and in order**. Actions order: `["STANDARD","RATED","DECLINE","REFER"]`.
- `preprocess_cambodia_data()` returns `(X, df, features)` where the returned **`df` contains the un-normalized feature columns** (normalization is applied to a copy). So dataset normalization stats can be read straight off it: `STATS[c] = (df[c].mean(), df[c].std())` (pandas default `ddof=1`, matching the function's internal `X[col].std()`).
- `httpx` and `xgboost` are installed → `TestClient` and `StaticXGBBaseline` work; **no `requirements.txt` change needed**.
- `DATA_PATH` is exported from `healthrl.underwriting_bandit` (= `ROOT/data/cambodia/cambodia_dataset.csv`).
- `compute_psi(expected_dist, actual_dist)` is exported from `demo.pricing_engine`.

**Scoring approach (the one non-obvious technical decision — §6):**
Passing a *single-row* frame to `preprocess_cambodia_data` is wrong (its `get_dummies` would produce only that row's region/occupation columns, giving a short, misaligned vector). Instead, **concatenate the applicant row onto the raw dataset, re-run `preprocess_cambodia_data(df=combined, stats=STATS)`, and take the last row**. With `stats=STATS` the normalization exactly matches θ's training basis, and because all categories are present the returned `features` equals `FEATURES`. Cost is one ~2001-row preprocess per `/api/score` (~10–30 ms) — acceptable for a demo, and pure reuse.

**Two documented spec interpretations (flag at plan review):**
1. **Confidence τ (§6/§13):** spec's literal "τ=1.0 on the reward scale" saturates softmax (Θ·x is dollar-scale; gaps ≥ 50) → always ~100%. Spec calls τ tunable/illustrative, so this plan uses `confidence = softmax(r/τ)[a*]` with `CONFIDENCE_TEMP = 50.0`, verified non-degenerate, labelled illustrative — **not** a calibrated probability.
2. **Fairness badge (§3.5/§6/§8):** computed as the trained policy's **approved-pool** (actions STANDARD/RATED across the full dataset) region & occupation distribution vs the **population**, via `compute_psi`, cached at startup — model-level, standing, never per-applicant. The canonical EXP-006 zones (region GREEN 0.042 / occupation AMBER 0.071) are read from `thesis_results.json` and shown as the authoritative footnote.

**Constraints (from handoff):**
- Do **not** touch `demo/main.py`, `demo/templates/index.html`, or `demo/static/defense.{html,js}` (they back Render + PPTX screenshots). Cutover is a later, separate step (§10) — out of scope here.
- Stage **explicit paths** only (never `git add .`/`-A`). Use `rtk git …`. Commit trailer:
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`
- Branch: `thesis/ch5-structural-pass` (work in the main tree).

**TDD note:** Tasks 1–6 (backend) are strict TDD (failing test → code → pass). Tasks 7–9 (frontend) have no pytest unit tests in spec §11; they use complete code + a manual/uvicorn smoke verification. Task 10 is final whole-system verification.

---

## File Structure

```
demo/desk/
  __init__.py        # empty package marker
  app.py             # FastAPI app + all routes + canonical loader
  scoring.py         # θ load, STATS, score_applicant(), compute_model_fairness() (cached)
  learning.py        # run_learn(): adaptive + static trajectories + early/late action mix
  static/
    index.html       # two-view shell + top toggle
    api.js           # fetch wrappers for the endpoints
    main.js          # view toggle + shared bootstrap
    desk.js          # applicant form + result card
    learn.js         # Chart.js divergence + Play/Reset + action-mix bars
    chart.umd.min.js # vendored (copied from demo/static/)
tests/
  test_desk_app.py   # spec §11 backend tests
```

Responsibilities: `app.py` is thin wiring + Pydantic models; all numeric logic is in `scoring.py`/`learning.py` so it is unit-testable without HTTP. Frontend is split by view; `api.js`/`main.js` are shared.

---

### Task 1: Package scaffold + FastAPI skeleton (`/`, `/api/health`)

**Files:**
- Create: `demo/desk/__init__.py`
- Create: `demo/desk/app.py`
- Create: `demo/desk/static/index.html` (minimal placeholder; replaced in Task 7)
- Create: `tests/test_desk_app.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_desk_app.py`:

```python
"""Backend tests for the clean Underwriting Desk demo (spec §11)."""
from __future__ import annotations

from fastapi.testclient import TestClient

from demo.desk.app import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_desk_app.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'demo.desk'`.

- [ ] **Step 3: Create the package + minimal app**

Create `demo/desk/__init__.py` (empty file — `# Underwriting Desk demo package`).

Create `demo/desk/static/index.html`:

```html
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Underwriting Desk</title></head>
<body><h1>Underwriting Desk</h1><p>Loading…</p></body>
</html>
```

Create `demo/desk/app.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_desk_app.py -q`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
rtk git add demo/desk/__init__.py demo/desk/app.py demo/desk/static/index.html tests/test_desk_app.py
rtk git commit -m "$(cat <<'EOF'
feat(desk): scaffold clean two-view demo app (health + index)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Applicant field options + random applicant

**Files:**
- Modify: `demo/desk/app.py` (add helpers + 2 routes)
- Test: `tests/test_desk_app.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_desk_app.py`:

```python
def test_applicant_fields_nonempty():
    r = client.get("/api/applicant/fields")
    assert r.status_code == 200
    data = r.json()
    for key in ("regions", "occupations", "educations", "wealth_quintiles",
                "health_statuses", "conditions"):
        assert isinstance(data[key], list) and len(data[key]) > 0


def test_random_applicant_valid():
    r = client.get("/api/applicant/random")
    assert r.status_code == 200
    data = r.json()
    app_ = data["applicant"]
    assert 18 <= app_["age"] <= 85
    assert app_["gender"] in ("Male", "Female")
    assert isinstance(app_["region"], str) and app_["region"]
    assert "mortality_multiplier" in app_
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_desk_app.py -q`
Expected: FAIL — 404 on `/api/applicant/fields` and `/api/applicant/random`.

- [ ] **Step 3: Add data loading + routes (port from `demo/main.py`)**

In `demo/desk/app.py`, add imports under the existing ones:

```python
from typing import Any

import numpy as np
import pandas as pd

from healthrl.underwriting_bandit import preprocess_cambodia_data
```

After `app.mount(...)`, add the shared data load + helper:

```python
# Load dataset once at startup (df carries un-normalized feature columns).
X_FULL, DF_RAW, FEATURES = preprocess_cambodia_data()


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
```

Add the two routes (after `index`):

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_desk_app.py -q`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
rtk git add demo/desk/app.py tests/test_desk_app.py
rtk git commit -m "$(cat <<'EOF'
feat(desk): applicant field options + random CDHS applicant endpoints

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Canonical headline loader + `/api/canonical`

Reads the authoritative 20-seed headline from `demo/static/thesis_results.json` (the existing canonical file — not duplicated). Spec §8 + §11 ("reads from thesis_results.json, no hardcoded fallback").

**Files:**
- Modify: `demo/desk/app.py`
- Test: `tests/test_desk_app.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_desk_app.py`:

```python
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THESIS_RESULTS = ROOT / "demo" / "static" / "thesis_results.json"


def test_canonical_reads_from_file():
    r = client.get("/api/canonical")
    assert r.status_code == 200
    data = r.json()
    on_disk = json.loads(THESIS_RESULTS.read_text(encoding="utf-8"))
    # Value must come from the file, not a hardcoded literal.
    assert data["lift_pct"] == on_disk["exp005"]["lift_pct"]
    assert data["cohen_d"] == on_disk["exp005"]["reward_cohen_d"]
    assert data["p_value"] == on_disk["exp005"]["reward_p"]
    assert data["n_seeds"] == 20
    # Admissible-scope ceiling carried alongside the headline (_meta.scope).
    assert data["ceiling_policy"] == "AlwaysRATED"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_desk_app.py::test_canonical_reads_from_file -q`
Expected: FAIL — 404 on `/api/canonical`.

- [ ] **Step 3: Add the loader + route**

In `demo/desk/app.py`, add `import json` to the top imports, then add near the data load:

```python
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
```

Add the route:

```python
@app.get("/api/canonical")
async def canonical() -> dict[str, Any]:
    return CANONICAL_HEADLINE
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_desk_app.py::test_canonical_reads_from_file -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add demo/desk/app.py tests/test_desk_app.py
rtk git commit -m "$(cat <<'EOF'
feat(desk): canonical 20-seed headline loader from thesis_results.json

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Scoring module + `/api/score` (decision, bars, confidence, drivers, premium)

**Files:**
- Create: `demo/desk/scoring.py`
- Modify: `demo/desk/app.py` (Pydantic models + route)
- Test: `tests/test_desk_app.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_desk_app.py`:

```python
from healthrl.underwriting_bandit import ACTION_NAMES

# A fixed manual applicant (mortality_multiplier defaults to neutral 1.0).
SAMPLE_APPLICANT = {
    "age": 45, "gender": "Female", "bmi": 24.5,
    "is_smoking": 0, "alcohol_use": 0, "is_exercise": 1,
    "has_family_history": 0, "monthly_income_usd": 350.0,
    "pre_existing_conditions": "", "region": "Phnom Penh",
    "occupation": "Civil Servant", "education": "Secondary",
    "wealth_quintile": "Middle", "self_reported_health": "Good",
}


def test_score_card_well_formed():
    r = client.post("/api/score", json=SAMPLE_APPLICANT)
    assert r.status_code == 200, r.text
    data = r.json()
    # Decision is a valid action.
    assert data["decision"] in ACTION_NAMES
    assert data["decision_index"] == ACTION_NAMES.index(data["decision"])
    # Four numeric estimated rewards, one per action.
    er = data["estimated_rewards"]
    assert set(er.keys()) == set(ACTION_NAMES)
    assert all(isinstance(v, (int, float)) for v in er.values())
    # Confidence is a probability-like scalar, non-degenerate range enforced elsewhere.
    assert 0.0 <= data["confidence"] <= 1.0
    # Exactly three drivers, each signed.
    assert len(data["drivers"]) == 3
    for d in data["drivers"]:
        assert d["direction"] in ("up", "down")
        assert isinstance(d["label"], str) and d["label"]
    # Premium consistent with the decision.
    prem = data["premium"]
    if data["decision"] == "DECLINE":
        assert prem["amount"] is None and prem["status"] == "declined"
    elif data["decision"] == "REFER":
        assert prem["amount"] is None and prem["status"] == "refer"
    else:
        assert isinstance(prem["amount"], (int, float)) and prem["amount"] > 0


def test_score_decision_matches_theta_argmax():
    r = client.post("/api/score", json=SAMPLE_APPLICANT).json()
    er = r["estimated_rewards"]
    best = max(er, key=er.get)
    assert r["decision"] == best


def test_score_validation_rejects_bad_age():
    bad = dict(SAMPLE_APPLICANT, age=5)
    r = client.post("/api/score", json=bad)
    assert r.status_code == 422
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_desk_app.py -k score -q`
Expected: FAIL — 404 on `/api/score`.

- [ ] **Step 3: Create `demo/desk/scoring.py`**

```python
"""θ-based scoring for the Underwriting Desk (spec §6).

Uses a representative *trained* LinUCB policy (θ from
demo/static/coefficients_linucb_seed42.json). No new modelling math: the
applicant is preprocessed by reusing healthrl.preprocess_cambodia_data on the
applicant row concatenated to the raw dataset (so the one-hot columns align and
normalization uses the dataset's training-basis statistics).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from healthrl.underwriting_bandit import (
    ACTION_NAMES,
    DATA_PATH,
    RewardConfig,
    preprocess_cambodia_data,
)
from demo.pricing_engine import optimize_premium

ROOT = Path(__file__).resolve().parent.parent.parent
COEFFS_PATH = ROOT / "demo" / "static" / "coefficients_linucb_seed42.json"

# Presentation constant for the confidence aid (spec §6/§13): softmax temperature
# on the dollar reward scale. NOT a calibrated probability — labelled illustrative.
CONFIDENCE_TEMP = 50.0

# Human-readable labels for the 34 model features (spec §6 "drivers").
FEATURE_LABELS = {
    "age": "Age",
    "gender_female": "Female",
    "bmi": "BMI",
    "is_smoking": "Smoker",
    "alcohol_use": "Alcohol use",
    "is_exercise": "Exercises",
    "has_family_history": "Family history",
    "monthly_income_usd": "Monthly income",
    "condition_count": "Number of conditions",
    "education_enc": "Education level",
    "wealth_enc": "Wealth quintile",
    "health_status_enc": "Self-reported health",
    "has_hypertension": "Hypertension",
    "has_diabetes": "Diabetes",
    "has_heart_disease": "Heart disease",
    "has_copd_asthma": "COPD/Asthma",
    "has_arthritis": "Arthritis",
    "has_tb": "Tuberculosis",
    "has_hepatitis_b": "Hepatitis B",
    "region_Battambang": "Region: Battambang",
    "region_Kampong Cham": "Region: Kampong Cham",
    "region_Kandal": "Region: Kandal",
    "region_Other Provinces": "Region: Other Provinces",
    "region_Phnom Penh": "Region: Phnom Penh",
    "region_Preah Sihanouk": "Region: Preah Sihanouk",
    "region_Prey Veng": "Region: Prey Veng",
    "region_Siem Reap": "Region: Siem Reap",
    "occ_Civil Servant": "Occupation: Civil Servant",
    "occ_Construction Worker": "Occupation: Construction Worker",
    "occ_Garment Worker": "Occupation: Garment Worker",
    "occ_Market Vendor": "Occupation: Market Vendor",
    "occ_Monk/Retired": "Occupation: Monk/Retired",
    "occ_Moto/Tuk-tuk Driver": "Occupation: Moto/Tuk-tuk Driver",
    "occ_Rice Farmer": "Occupation: Rice Farmer",
}


def _label(feature: str) -> str:
    return FEATURE_LABELS.get(feature, feature.replace("_", " ").capitalize())


class DeskScorer:
    """Holds the trained θ, dataset stats, and the raw base for concat-scoring."""

    def __init__(self) -> None:
        coeffs = json.loads(COEFFS_PATH.read_text(encoding="utf-8"))
        self.theta = np.asarray(coeffs["theta"], dtype=float)  # (4, 34)
        self.coeff_features: list[str] = coeffs["features"]

        self.X_full, self.df_raw, self.features = preprocess_cambodia_data()
        assert self.coeff_features == self.features, "θ feature order mismatch"

        # Dataset normalization stats (df carries un-normalized feature columns).
        self.stats = {
            c: (float(self.df_raw[c].mean()), float(self.df_raw[c].std()))
            for c in self.features
        }
        # Original raw columns, for concatenating a new applicant row.
        self.raw_base = pd.read_csv(DATA_PATH)
        self.config = RewardConfig()

    def featurize(self, applicant: dict[str, Any]) -> np.ndarray:
        """Normalized 34-dim feature vector for a single applicant (spec §6)."""
        combined = pd.concat(
            [self.raw_base, pd.DataFrame([applicant])], ignore_index=True
        )
        x_comb, _, feats = preprocess_cambodia_data(df=combined, stats=self.stats)
        assert feats == self.features, "feature alignment broke during scoring"
        return np.asarray(x_comb[-1], dtype=float)

    def _premium(self, decision: str, applicant: dict[str, Any]) -> dict[str, Any]:
        """Recommended premium consistent with the decision (spec §6)."""
        row = pd.Series(applicant)
        mort = float(applicant.get("mortality_multiplier", 1.0))
        base_premium = round(self.config.base_premium_rate * mort, 2)
        if decision == "DECLINE":
            return {"display": "— (declined)", "amount": None,
                    "multiplier": None, "status": "declined", "p_accept": None}
        if decision == "REFER":
            return {"display": "Pending review", "amount": None,
                    "multiplier": None, "status": "refer", "p_accept": None}
        if decision == "STANDARD":
            return {"display": f"${base_premium:,.2f} /yr", "amount": base_premium,
                    "multiplier": 1.0, "status": "base", "p_accept": None}
        # RATED → profit-optimal loaded premium.
        opt = optimize_premium(row, self.config)
        return {
            "display": f"${opt['optimal_premium_usd']:,.2f} /yr",
            "amount": opt["optimal_premium_usd"],
            "multiplier": opt["optimal_multiplier"],
            "status": "loaded",
            "p_accept": opt["optimal_p_accept"],
        }

    def score(self, applicant: dict[str, Any]) -> dict[str, Any]:
        x = self.featurize(applicant)
        r = self.theta @ x  # (4,) estimated reward per action
        a_star = int(np.argmax(r))
        decision = ACTION_NAMES[a_star]

        # Confidence aid: softmax over r / τ (presentation-only, illustrative).
        z = r / CONFIDENCE_TEMP
        z = z - z.max()
        soft = np.exp(z) / np.exp(z).sum()
        confidence = float(soft[a_star])

        # Top-3 drivers by |θ_{a*,i} · x_i|, signed.
        contrib = self.theta[a_star] * x
        top = np.argsort(np.abs(contrib))[::-1][:3]
        drivers = [
            {
                "feature": self.features[i],
                "label": _label(self.features[i]),
                "direction": "up" if contrib[i] >= 0 else "down",
                "contribution": round(float(contrib[i]), 3),
            }
            for i in top
        ]

        return {
            "decision": decision,
            "decision_index": a_star,
            "confidence": round(confidence, 4),
            "estimated_rewards": {
                ACTION_NAMES[i]: round(float(r[i]), 2) for i in range(len(ACTION_NAMES))
            },
            "drivers": drivers,
            "premium": self._premium(decision, applicant),
            "illustrative_note": (
                "Illustrative · single seed (42) · representative trained LinUCB policy"
            ),
        }


# Module-level singleton (load θ + data once).
SCORER = DeskScorer()
```

- [ ] **Step 4: Add Pydantic model + route in `demo/desk/app.py`**

Add imports:

```python
from pydantic import BaseModel, Field

from demo.desk import scoring
```

Add the request model (after the imports / before routes):

```python
class ApplicantIn(BaseModel):
    age: int = Field(..., ge=18, le=85)
    gender: str = Field(..., pattern="^(Male|Female)$")
    bmi: float = Field(..., ge=10.0, le=60.0)
    is_smoking: int = Field(..., ge=0, le=1)
    alcohol_use: int = Field(..., ge=0, le=1)
    is_exercise: int = Field(..., ge=0, le=1)
    has_family_history: int = Field(..., ge=0, le=1)
    monthly_income_usd: float = Field(..., ge=50.0, le=5000.0)
    pre_existing_conditions: str = ""
    region: str
    occupation: str
    education: str = "Primary"
    wealth_quintile: str = "Middle"
    self_reported_health: str = "Fair"
    # Hidden from the form: loaded sample carries its real value; manual = neutral 1.0.
    mortality_multiplier: float = Field(1.0, ge=0.5, le=5.0)
```

Add the route:

```python
@app.post("/api/score")
async def score(payload: ApplicantIn) -> dict[str, Any]:
    return scoring.SCORER.score(payload.model_dump())
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_desk_app.py -k score -q`
Expected: PASS (3 passed).

- [ ] **Step 6: Verify confidence is non-degenerate (calibration check)**

Run:

```bash
python -c "
from demo.desk.scoring import SCORER
import numpy as np
rng = np.random.default_rng(0)
confs = []
for i in rng.integers(0, len(SCORER.df_raw), 15):
    from demo.desk.app import _row_to_applicant
    a = _row_to_applicant(SCORER.df_raw.iloc[int(i)])
    confs.append(SCORER.score(a)['confidence'])
print('confidence min/median/max:', round(min(confs),3), round(float(np.median(confs)),3), round(max(confs),3))
assert max(confs) < 0.999, 'CONFIDENCE_TEMP too small (saturated) — raise it'
assert min(confs) > 0.30, 'CONFIDENCE_TEMP too large (flat) — lower it'
print('OK: non-degenerate')
"
```

Expected: prints a spread inside (0.30, 0.999) and `OK: non-degenerate`. If it fails, adjust `CONFIDENCE_TEMP` in `scoring.py` (raise to flatten, lower to sharpen) and re-run.

- [ ] **Step 7: Commit**

```bash
rtk git add demo/desk/scoring.py demo/desk/app.py tests/test_desk_app.py
rtk git commit -m "$(cat <<'EOF'
feat(desk): θ scoring endpoint — decision, bars, confidence, drivers, premium

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Model-level fairness badge (wired into `/api/score`)

**Files:**
- Modify: `demo/desk/scoring.py` (`compute_model_fairness`, cached; add to `score()` output)
- Test: `tests/test_desk_app.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_desk_app.py`:

```python
def test_score_includes_model_fairness():
    data = client.post("/api/score", json=SAMPLE_APPLICANT).json()
    fair = data["fairness"]
    assert fair["badge_status"] in ("GREEN", "AMBER", "RED")
    for key in ("region", "occupation"):
        assert fair[key]["status"] in ("GREEN", "AMBER", "RED")
        assert isinstance(fair[key]["psi"], (int, float))
    # Canonical EXP-006 footnote (read from thesis_results.json, not invented).
    assert fair["canonical"]["region_zone"] == "GREEN"
    assert fair["canonical"]["occupation_zone"] == "AMBER"


def test_model_fairness_is_constant_across_applicants():
    """Model-level (not per-applicant): identical for any applicant."""
    a = client.post("/api/score", json=SAMPLE_APPLICANT).json()["fairness"]
    other = dict(SAMPLE_APPLICANT, region="Siem Reap", occupation="Rice Farmer", age=70)
    b = client.post("/api/score", json=other).json()["fairness"]
    assert a["region"]["psi"] == b["region"]["psi"]
    assert a["occupation"]["psi"] == b["occupation"]["psi"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_desk_app.py -k fairness -q`
Expected: FAIL — `KeyError: 'fairness'`.

- [ ] **Step 3: Add fairness computation to `demo/desk/scoring.py`**

Add import at top of `scoring.py`:

```python
from demo.pricing_engine import compute_psi, optimize_premium
```

(replace the existing `from demo.pricing_engine import optimize_premium` line).

Add a canonical-zone loader + fairness method. In `DeskScorer.__init__`, after `self.config = RewardConfig()`, add:

```python
        self._canonical_zones = self._load_canonical_zones()
        self.fairness = self._compute_model_fairness()  # cached at startup
```

Add these methods to `DeskScorer`:

```python
    def _load_canonical_zones(self) -> dict[str, str]:
        """Authoritative EXP-006 PSI zones from thesis_results.json (spec §8)."""
        path = ROOT / "demo" / "static" / "thesis_results.json"
        data = json.loads(path.read_text(encoding="utf-8"))["exp006"]
        return {
            "region_zone": data["region"]["psi_zone"],
            "occupation_zone": data["occupation"]["psi_zone"],
            "region_psi": data["region"]["psi_final_window"],
            "occupation_psi": data["occupation"]["psi_final_window"],
        }

    def _compute_model_fairness(self) -> dict[str, Any]:
        """Standing model-level PSI: trained policy's approved pool vs population.

        Approved = the policy issues a policy (STANDARD or RATED). PSI compares
        the approved subpopulation's group distribution against the full
        population (spec §3.5/§6). Cached; never per-applicant.
        """
        actions = np.argmax(self.X_full @ self.theta.T, axis=1)  # (N,)
        approved = np.isin(actions, [0, 1])  # STANDARD, RATED
        out: dict[str, Any] = {}
        zones = []
        for col, label in (("region", "Region"), ("occupation", "Occupation")):
            ref = self.df_raw[col].value_counts().sort_index()
            act = self.df_raw.loc[approved, col].value_counts().reindex(
                ref.index, fill_value=0
            )
            psi = compute_psi(ref.values.astype(float), act.values.astype(float))
            status = "GREEN" if psi < 0.10 else "AMBER" if psi < 0.25 else "RED"
            out[col] = {"label": label, "psi": round(psi, 4), "status": status}
            zones.append(status)
        order = {"GREEN": 0, "AMBER": 1, "RED": 2}
        out["badge_status"] = max(zones, key=lambda z: order[z])
        out["canonical"] = self._canonical_zones
        out["note"] = (
            "Model-level guardrail: trained-policy approved pool vs population "
            "(illustrative). Authoritative zones: EXP-006, 20 seeds."
        )
        return out
```

In `score()`, add `"fairness": self.fairness,` to the returned dict (e.g., right after `"premium": ...`).

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_desk_app.py -k fairness -q`
Expected: PASS (2 passed).

- [ ] **Step 5: Sanity-check the computed zones are not RED**

Run:

```bash
python -c "
from demo.desk.scoring import SCORER
f = SCORER.fairness
print('region:', f['region'], '| occupation:', f['occupation'], '| badge:', f['badge_status'])
assert f['badge_status'] in ('GREEN','AMBER'), 'Unexpected RED — investigate before defense'
print('OK')
"
```

Expected: prints region/occupation PSI + badge, asserts not RED. (If RED, stop and surface it — it would contradict EXP-006 and must be understood, not shipped.)

- [ ] **Step 6: Commit**

```bash
rtk git add demo/desk/scoring.py tests/test_desk_app.py
rtk git commit -m "$(cat <<'EOF'
feat(desk): standing model-level fairness badge (approved-pool PSI + EXP-006 zones)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: Learning module + `/api/learn/run`

**Files:**
- Create: `demo/desk/learning.py`
- Modify: `demo/desk/app.py` (model + route)
- Test: `tests/test_desk_app.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_desk_app.py`:

```python
def test_learn_run_trajectories():
    payload = {"algorithm": "LinUCB", "seed": 42, "n_rounds": 300}
    r = client.post("/api/learn/run", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["algorithm"] == "LinUCB"
    assert data["n_rounds"] == 300
    assert len(data["adaptive"]["cumulative"]) == 300
    assert len(data["static"]["cumulative"]) == 300
    assert len(data["rounds"]) == 300
    # Early/late action mixes are distributions over the 4 actions.
    for mix in (data["adaptive"]["early_mix"], data["adaptive"]["late_mix"]):
        assert abs(sum(mix.values()) - 1.0) < 1e-6
        assert set(mix.keys()) == set(ACTION_NAMES)
    # Illustrative lift readout present and labelled.
    assert "lift_pct" in data and isinstance(data["lift_pct"], (int, float))


def test_learn_run_rejects_bad_algorithm():
    r = client.post("/api/learn/run", json={"algorithm": "Nope", "n_rounds": 300})
    assert r.status_code == 422
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_desk_app.py -k learn -q`
Expected: FAIL — 404 on `/api/learn/run`.

- [ ] **Step 3: Create `demo/desk/learning.py`**

```python
"""Online-learning showcase: adaptive policy vs static baseline (spec §7.2).

Reuses healthrl.run_bandit. Returns full trajectories; the client animates
them (no server streaming). Live numbers are single-seed and illustrative.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from healthrl.underwriting_bandit import (
    ACTION_NAMES,
    LinTS,
    LinUCB,
    StaticXGBBaseline,
    preprocess_cambodia_data,
    run_bandit,
)

X_FULL, DF_RAW, FEATURES = preprocess_cambodia_data()
N_FEATURES = X_FULL.shape[1]


def _mix(actions: np.ndarray) -> dict[str, float]:
    counts = np.bincount(actions.astype(int), minlength=4)
    total = int(counts.sum()) or 1
    return {ACTION_NAMES[i]: round(float(counts[i] / total), 4) for i in range(4)}


def run_learn(algorithm: str, seed: int = 42, n_rounds: int = 2000) -> dict[str, Any]:
    if algorithm == "LinUCB":
        adaptive = LinUCB(n_actions=4, n_features=N_FEATURES, alpha=1.0)
    elif algorithm == "LinTS":
        adaptive = LinTS(n_actions=4, n_features=N_FEATURES, v2=1.0, seed=seed)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    adaptive_res = run_bandit(
        algorithm, adaptive, X_FULL.copy(), DF_RAW, n_rounds, seed=seed
    )
    static_res = run_bandit(
        "StaticXGB", StaticXGBBaseline(), X_FULL.copy(), DF_RAW, n_rounds, seed=seed
    )

    early_n = max(1, min(500, n_rounds // 2))
    late_n = max(1, min(500, n_rounds // 2))
    adaptive_final = float(adaptive_res.cumulative_rewards[-1])
    static_final = float(static_res.cumulative_rewards[-1])
    lift_pct = (
        round((adaptive_final - static_final) / abs(static_final) * 100, 1)
        if static_final
        else 0.0
    )

    return {
        "algorithm": algorithm,
        "seed": seed,
        "n_rounds": n_rounds,
        "rounds": list(range(1, n_rounds + 1)),
        "adaptive": {
            "cumulative": [round(float(v), 2) for v in adaptive_res.cumulative_rewards],
            "final": round(adaptive_final, 2),
            "early_mix": _mix(adaptive_res.actions[:early_n]),
            "late_mix": _mix(adaptive_res.actions[-late_n:]),
        },
        "static": {
            "cumulative": [round(float(v), 2) for v in static_res.cumulative_rewards],
            "final": round(static_final, 2),
        },
        "lift_pct": lift_pct,
        "illustrative_note": f"Illustrative · single seed ({seed})",
    }
```

- [ ] **Step 4: Add model + route in `demo/desk/app.py`**

Add `from demo.desk import learning` to imports. Add request model:

```python
class LearnRunIn(BaseModel):
    algorithm: str = Field("LinUCB", pattern="^(LinUCB|LinTS)$")
    seed: int = Field(42, ge=0, le=10_000)
    n_rounds: int = Field(2000, ge=300, le=5000)
```

Add the route:

```python
@app.post("/api/learn/run")
async def learn_run(payload: LearnRunIn) -> dict[str, Any]:
    return learning.run_learn(payload.algorithm, payload.seed, payload.n_rounds)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_desk_app.py -k learn -q`
Expected: PASS (2 passed).

- [ ] **Step 6: Run the full backend suite**

Run: `python -m pytest tests/test_desk_app.py -q`
Expected: ALL PASS (13 tests).

- [ ] **Step 7: Commit**

```bash
rtk git add demo/desk/learning.py demo/desk/app.py tests/test_desk_app.py
rtk git commit -m "$(cat <<'EOF'
feat(desk): /api/learn/run — bandit-vs-static trajectories + action mix

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: Frontend shell — `index.html` + `main.js` + `api.js`

No pytest (spec §11); verify by serving and inspecting. Visual reference (gitignored, optional): `.superpowers/brainstorm/820-1781509020/content/{desk,watch-learn}.html`.

**Files:**
- Modify: `demo/desk/static/index.html` (replace placeholder)
- Create: `demo/desk/static/api.js`
- Create: `demo/desk/static/main.js`

- [ ] **Step 1: Replace `demo/desk/static/index.html`**

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Adaptive Underwriting Desk</title>
  <style>
    :root {
      --bg:#0f1419; --panel:#1a2230; --panel2:#222c3c; --ink:#e8edf4;
      --muted:#93a1b5; --line:#2c3a4e; --accent:#3b82f6; --accent2:#22d3ee;
      --green:#22c55e; --amber:#f59e0b; --red:#ef4444;
    }
    * { box-sizing:border-box; }
    body { margin:0; font-family:"Segoe UI",Calibri,system-ui,sans-serif;
           background:var(--bg); color:var(--ink); }
    header { display:flex; align-items:center; gap:1.5rem; padding:1rem 1.5rem;
             border-bottom:1px solid var(--line); background:var(--panel); }
    header h1 { font-size:1.1rem; margin:0; font-weight:600; }
    header .sub { color:var(--muted); font-size:.8rem; }
    .toggle { margin-left:auto; display:flex; gap:.25rem; background:var(--panel2);
              padding:.25rem; border-radius:999px; }
    .toggle button { border:0; background:transparent; color:var(--muted);
                     padding:.5rem 1rem; border-radius:999px; cursor:pointer;
                     font-size:.85rem; font-weight:600; }
    .toggle button.active { background:var(--accent); color:#fff; }
    main { padding:1.5rem; max-width:1200px; margin:0 auto; }
    .view { display:none; }
    .view.active { display:block; }
    .grid { display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; }
    .card { background:var(--panel); border:1px solid var(--line);
            border-radius:12px; padding:1.25rem; }
    .card h2 { margin:0 0 1rem; font-size:.95rem; font-weight:600; }
    label { display:block; font-size:.75rem; color:var(--muted); margin:.6rem 0 .2rem; }
    input, select { width:100%; padding:.5rem; background:var(--panel2);
                    border:1px solid var(--line); border-radius:8px; color:var(--ink); }
    .row { display:grid; grid-template-columns:1fr 1fr; gap:.75rem; }
    .group-title { font-size:.7rem; text-transform:uppercase; letter-spacing:.05em;
                   color:var(--accent2); margin:1rem 0 .25rem; }
    .chips { display:flex; flex-wrap:wrap; gap:.4rem; }
    .chip { padding:.3rem .6rem; border:1px solid var(--line); border-radius:999px;
            font-size:.75rem; cursor:pointer; user-select:none; }
    .chip.on { background:var(--accent); border-color:var(--accent); color:#fff; }
    .btn { padding:.6rem 1rem; border:0; border-radius:8px; background:var(--accent);
           color:#fff; font-weight:600; cursor:pointer; }
    .btn.ghost { background:var(--panel2); color:var(--ink); border:1px solid var(--line); }
    .btn-row { display:flex; gap:.5rem; margin-top:1rem; }
    .badge { display:inline-block; padding:.25rem .6rem; border-radius:6px;
             font-weight:700; font-size:.8rem; }
    .decision-badge { font-size:1.5rem; padding:.5rem 1rem; }
    .b-STANDARD { background:rgba(34,197,94,.15); color:var(--green); }
    .b-RATED { background:rgba(245,158,11,.15); color:var(--amber); }
    .b-DECLINE { background:rgba(239,68,68,.15); color:var(--red); }
    .b-REFER { background:rgba(59,130,246,.15); color:var(--accent); }
    .z-GREEN { background:rgba(34,197,94,.15); color:var(--green); }
    .z-AMBER { background:rgba(245,158,11,.15); color:var(--amber); }
    .z-RED { background:rgba(239,68,68,.15); color:var(--red); }
    .bar { height:22px; border-radius:5px; background:var(--accent2); }
    .bar-track { background:var(--panel2); border-radius:5px; }
    .bar-row { display:grid; grid-template-columns:90px 1fr 70px; gap:.5rem;
               align-items:center; margin:.35rem 0; font-size:.8rem; }
    .bar-row.win .bar { background:var(--accent); }
    .driver { display:flex; justify-content:space-between; padding:.35rem 0;
              border-bottom:1px solid var(--line); font-size:.85rem; }
    .up { color:var(--green); } .down { color:var(--red); }
    .note { color:var(--muted); font-size:.72rem; margin-top:.75rem; font-style:italic; }
    .headline { display:flex; gap:1.5rem; flex-wrap:wrap; align-items:baseline;
                background:var(--panel2); border-radius:10px; padding:1rem 1.25rem;
                margin-bottom:1.25rem; }
    .headline .big { font-size:1.8rem; font-weight:800; color:var(--accent2); }
    .headline .tag { color:var(--muted); font-size:.78rem; }
    canvas { background:var(--panel2); border-radius:8px; padding:.5rem; }
    .muted { color:var(--muted); font-size:.8rem; }
    .err { color:var(--red); font-size:.85rem; }
    .mix-wrap { display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-top:1rem; }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Adaptive Underwriting Desk</h1>
      <div class="sub">Contextual-bandit underwriting · Cambodia (CDHS-anchored)</div>
    </div>
    <div class="toggle">
      <button id="tab-desk" class="active">Underwriting Desk</button>
      <button id="tab-learn">Watch it Learn</button>
    </div>
  </header>

  <main>
    <!-- VIEW 1: UNDERWRITING DESK -->
    <section id="view-desk" class="view active">
      <div class="grid">
        <div class="card" id="form-card">
          <h2>Applicant</h2>
          <div class="btn-row">
            <button class="btn ghost" id="btn-load">⟳ Load CDHS sample</button>
            <button class="btn ghost" id="btn-clear">Clear</button>
          </div>
          <div id="form"></div>
          <div class="btn-row">
            <button class="btn" id="btn-score">Score applicant →</button>
          </div>
          <div id="form-err" class="err"></div>
        </div>
        <div class="card" id="result-card">
          <h2>Underwriting decision</h2>
          <div id="result"><p class="muted">Load a sample or fill the form, then
            score.</p></div>
        </div>
      </div>
    </section>

    <!-- VIEW 2: WATCH IT LEARN -->
    <section id="view-learn" class="view">
      <div id="headline" class="headline"><span class="muted">Loading headline…</span></div>
      <div class="card">
        <h2>Cumulative reward — adaptive policy vs Static XGB</h2>
        <div class="btn-row">
          <select id="algo"><option>LinUCB</option><option>LinTS</option></select>
          <button class="btn" id="btn-play">▶ Play</button>
          <button class="btn ghost" id="btn-reset">Reset</button>
          <span class="muted" id="round-readout">round 0</span>
          <span class="muted" id="lift-readout"></span>
        </div>
        <canvas id="chart" height="120"></canvas>
        <div class="note" id="learn-note"></div>
        <div class="mix-wrap">
          <div><div class="group-title">Early (exploring)</div><div id="mix-early"></div></div>
          <div><div class="group-title">Late (exploiting)</div><div id="mix-late"></div></div>
        </div>
      </div>
    </section>
  </main>

  <script src="/static/chart.umd.min.js"></script>
  <script src="/static/api.js"></script>
  <script src="/static/desk.js"></script>
  <script src="/static/learn.js"></script>
  <script src="/static/main.js"></script>
</body>
</html>
```

- [ ] **Step 2: Create `demo/desk/static/api.js`**

```javascript
// Thin fetch wrappers for the four desk endpoints.
const API = {
  async fields() { return (await fetch('/api/applicant/fields')).json(); },
  async random() { return (await fetch('/api/applicant/random')).json(); },
  async canonical() { return (await fetch('/api/canonical')).json(); },
  async score(applicant) {
    const res = await fetch('/api/score', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(applicant),
    });
    if (!res.ok) {
      const detail = await res.json().catch(() => ({}));
      throw new Error(detail.detail ? JSON.stringify(detail.detail) : `HTTP ${res.status}`);
    }
    return res.json();
  },
  async learn(payload) {
    const res = await fetch('/api/learn/run', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },
};
```

- [ ] **Step 3: Create `demo/desk/static/main.js`**

```javascript
// View toggle + bootstrap. Desk/Learn render functions live in desk.js / learn.js.
(function () {
  const tabDesk = document.getElementById('tab-desk');
  const tabLearn = document.getElementById('tab-learn');
  const viewDesk = document.getElementById('view-desk');
  const viewLearn = document.getElementById('view-learn');
  let learnInitialized = false;

  function show(which) {
    const desk = which === 'desk';
    tabDesk.classList.toggle('active', desk);
    tabLearn.classList.toggle('active', !desk);
    viewDesk.classList.toggle('active', desk);
    viewLearn.classList.toggle('active', !desk);
    if (!desk && !learnInitialized) { Learn.init(); learnInitialized = true; }
  }
  tabDesk.addEventListener('click', () => show('desk'));
  tabLearn.addEventListener('click', () => show('learn'));

  Desk.init();
})();
```

- [ ] **Step 4: Verify the shell serves (manual)**

Start the app in the background:

```bash
python -m uvicorn demo.desk.app:app --port 8011 &
sleep 3
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8011/
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8011/static/api.js
```

Expected: `200` and `200`. (`desk.js`/`learn.js` 404 until Tasks 8–9 — `chart.umd.min.js` until Task 10. That is expected now.) Leave the server for the next task or stop it: `kill %1`.

- [ ] **Step 5: Commit**

```bash
rtk git add demo/desk/static/index.html demo/desk/static/api.js demo/desk/static/main.js
rtk git commit -m "$(cat <<'EOF'
feat(desk): two-view UI shell, top toggle, and API client

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

### Task 8: Frontend — `desk.js` (applicant form + result card)

**Files:**
- Create: `demo/desk/static/desk.js`

- [ ] **Step 1: Create `demo/desk/static/desk.js`**

```javascript
// Underwriting Desk view: grouped applicant form + result card.
const Desk = (function () {
  let FIELDS = null;
  let selectedConditions = new Set();
  let loadedMortality = 1.0; // carried from a loaded CDHS sample; manual = 1.0

  const ACTIONS = ['STANDARD', 'RATED', 'DECLINE', 'REFER'];

  function opt(list, val) {
    return list.map(v => `<option ${v === val ? 'selected' : ''}>${v}</option>`).join('');
  }

  function renderForm(values) {
    const v = values || {};
    const f = FIELDS;
    document.getElementById('form').innerHTML = `
      <div class="group-title">Demographics</div>
      <div class="row">
        <div><label>Age</label><input id="f-age" type="number" value="${v.age ?? 35}"></div>
        <div><label>Gender</label><select id="f-gender">${opt(['Male','Female'], v.gender ?? 'Male')}</select></div>
      </div>
      <div class="row">
        <div><label>Region</label><select id="f-region">${opt(f.regions, v.region)}</select></div>
        <div><label>Occupation</label><select id="f-occupation">${opt(f.occupations, v.occupation)}</select></div>
      </div>
      <div class="group-title">Health &amp; lifestyle</div>
      <div class="row">
        <div><label>BMI</label><input id="f-bmi" type="number" step="0.1" value="${v.bmi ?? 23}"></div>
        <div><label>Self-reported health</label><select id="f-health">${opt(f.health_statuses, v.self_reported_health ?? 'Fair')}</select></div>
      </div>
      <div class="chips" id="lifestyle">
        ${[['is_smoking','Smoker'],['alcohol_use','Alcohol'],['is_exercise','Exercises'],['has_family_history','Family history']]
          .map(([k,lab]) => `<span class="chip ${v[k] ? 'on' : ''}" data-k="${k}">${lab}</span>`).join('')}
      </div>
      <label>Pre-existing conditions</label>
      <div class="chips" id="conditions">
        ${f.conditions.map(c => `<span class="chip ${selectedConditions.has(c) ? 'on' : ''}" data-c="${c}">${c}</span>`).join('')}
      </div>
      <div class="group-title">Socioeconomic</div>
      <div class="row">
        <div><label>Monthly income (USD)</label><input id="f-income" type="number" value="${v.monthly_income_usd ?? 250}"></div>
        <div><label>Education</label><select id="f-education">${opt(f.educations, v.education ?? 'Primary')}</select></div>
      </div>
      <label>Wealth quintile</label>
      <select id="f-wealth">${opt(f.wealth_quintiles, v.wealth_quintile ?? 'Middle')}</select>
    `;
    // Toggle handlers for binary lifestyle chips + condition chips.
    document.querySelectorAll('#lifestyle .chip').forEach(ch =>
      ch.addEventListener('click', () => ch.classList.toggle('on')));
    document.querySelectorAll('#conditions .chip').forEach(ch =>
      ch.addEventListener('click', () => {
        ch.classList.toggle('on');
        const c = ch.dataset.c;
        if (selectedConditions.has(c)) selectedConditions.delete(c); else selectedConditions.add(c);
      }));
  }

  function readForm() {
    const lifestyle = {};
    document.querySelectorAll('#lifestyle .chip').forEach(ch =>
      lifestyle[ch.dataset.k] = ch.classList.contains('on') ? 1 : 0);
    return {
      age: parseInt(document.getElementById('f-age').value, 10),
      gender: document.getElementById('f-gender').value,
      bmi: parseFloat(document.getElementById('f-bmi').value),
      is_smoking: lifestyle.is_smoking || 0,
      alcohol_use: lifestyle.alcohol_use || 0,
      is_exercise: lifestyle.is_exercise || 0,
      has_family_history: lifestyle.has_family_history || 0,
      monthly_income_usd: parseFloat(document.getElementById('f-income').value),
      pre_existing_conditions: Array.from(selectedConditions).join(', '),
      region: document.getElementById('f-region').value,
      occupation: document.getElementById('f-occupation').value,
      education: document.getElementById('f-education').value,
      wealth_quintile: document.getElementById('f-wealth').value,
      self_reported_health: document.getElementById('f-health').value,
      mortality_multiplier: loadedMortality,
    };
  }

  function bar(name, val, lo, hi, win) {
    const span = (hi - lo) || 1;
    const pct = Math.max(2, Math.round(((val - lo) / span) * 100));
    return `<div class="bar-row ${win ? 'win' : ''}">
      <span>${name}</span>
      <div class="bar-track"><div class="bar" style="width:${pct}%"></div></div>
      <span>$${val.toFixed(0)}</span></div>`;
  }

  function renderResult(d) {
    const er = d.estimated_rewards;
    const vals = ACTIONS.map(a => er[a]);
    const lo = Math.min(...vals), hi = Math.max(...vals);
    const fair = d.fairness;
    const prem = d.premium;
    document.getElementById('result').innerHTML = `
      <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
        <span class="badge decision-badge b-${d.decision}">${d.decision}</span>
        <span class="muted">confidence ${(d.confidence * 100).toFixed(0)}%
          <span style="font-size:.7rem">(illustrative)</span></span>
        <span class="badge z-${fair.badge_status}" title="${fair.note}">
          Guardrail: ${fair.badge_status}</span>
      </div>
      <div class="group-title">Estimated reward by action</div>
      ${ACTIONS.map(a => bar(a, er[a], lo, hi, a === d.decision)).join('')}
      <div class="group-title">Recommended premium</div>
      <div style="font-size:1.2rem;font-weight:700">${prem.display}
        ${prem.multiplier ? `<span class="muted" style="font-size:.8rem">×${prem.multiplier}</span>` : ''}</div>
      <div class="group-title">Why this decision</div>
      ${d.drivers.map(dr => `<div class="driver"><span>${dr.label}</span>
        <span class="${dr.direction}">${dr.direction === 'up' ? '▲' : '▼'}
        ${Math.abs(dr.contribution).toFixed(1)}</span></div>`).join('')}
      <div class="group-title">Fairness guardrail (model-level)</div>
      <div class="muted">Region ${fair.region.psi} (${fair.region.status}) ·
        Occupation ${fair.occupation.psi} (${fair.occupation.status})<br>
        Canonical EXP-006 (20-seed): region ${fair.canonical.region_zone} ·
        occupation ${fair.canonical.occupation_zone}</div>
      <div class="note">${d.illustrative_note}</div>`;
  }

  async function score() {
    document.getElementById('form-err').textContent = '';
    try {
      const data = await API.score(readForm());
      renderResult(data);
    } catch (e) {
      document.getElementById('form-err').textContent = 'Could not score: ' + e.message;
    }
  }

  async function loadSample() {
    const { applicant } = await API.random();
    loadedMortality = applicant.mortality_multiplier ?? 1.0;
    selectedConditions = new Set(
      (applicant.pre_existing_conditions || '').split(',').map(s => s.trim()).filter(Boolean));
    renderForm(applicant);
  }

  function clearForm() {
    loadedMortality = 1.0;
    selectedConditions = new Set();
    renderForm({});
  }

  async function init() {
    FIELDS = await API.fields();
    renderForm({});
    document.getElementById('btn-load').addEventListener('click', loadSample);
    document.getElementById('btn-clear').addEventListener('click', clearForm);
    document.getElementById('btn-score').addEventListener('click', score);
  }

  return { init };
})();
```

- [ ] **Step 2: Verify the Desk works end-to-end (manual)**

If the server isn't running: `python -m uvicorn demo.desk.app:app --port 8011 &` then `sleep 3`.

```bash
curl -s -o /dev/null -w "desk.js %{http_code}\n" http://127.0.0.1:8011/static/desk.js
```

Expected: `desk.js 200`. Then open `http://127.0.0.1:8011/` in a browser: click **⟳ Load CDHS sample** → fields populate → **Score applicant →** → a decision badge, four reward bars (winner highlighted), premium, three drivers, and the model-level guardrail badge render. (Chart view is Task 9.)

- [ ] **Step 3: Commit**

```bash
rtk git add demo/desk/static/desk.js
rtk git commit -m "$(cat <<'EOF'
feat(desk): applicant form + underwriting result card

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

### Task 9: Frontend — `learn.js` (divergence chart + Play/Reset + action mix)

**Files:**
- Create: `demo/desk/static/learn.js`

- [ ] **Step 1: Create `demo/desk/static/learn.js`**

```javascript
// Watch it Learn view: canonical headline + animated divergence chart + action mix.
const Learn = (function () {
  let chart = null;
  let data = null;       // last /api/learn/run payload
  let timer = null;
  let frame = 0;
  const ACTIONS = ['STANDARD', 'RATED', 'DECLINE', 'REFER'];

  async function renderHeadline() {
    const c = await API.canonical();
    document.getElementById('headline').innerHTML = `
      <div><div class="big">+${c.lift_pct}%</div><div class="tag">vs ${c.comparator}</div></div>
      <div class="tag">${c.n_seeds} seeds · p ${c.p_value} · d = ${c.cohen_d}</div>
      <div class="tag" title="${c.ceiling_note}">scope: admissible policies
        (ceiling: ${c.ceiling_policy})</div>
      <div class="tag">thesis Ch.5</div>`;
  }

  function buildChart() {
    const ctx = document.getElementById('chart').getContext('2d');
    chart = new Chart(ctx, {
      type: 'line',
      data: { labels: [], datasets: [
        { label: 'Adaptive policy', data: [], borderColor: '#3b82f6',
          borderWidth: 2, pointRadius: 0, tension: .1 },
        { label: 'Static XGB', data: [], borderColor: '#93a1b5',
          borderWidth: 2, pointRadius: 0, borderDash: [5, 4], tension: .1 },
      ]},
      options: {
        animation: false, responsive: true,
        scales: { x: { ticks: { color: '#93a1b5', maxTicksLimit: 8 } },
                  y: { ticks: { color: '#93a1b5' } } },
        plugins: { legend: { labels: { color: '#e8edf4' } } },
      },
    });
  }

  function mixRows(mix) {
    return ACTIONS.map(a => {
      const pct = Math.round((mix[a] || 0) * 100);
      return `<div class="bar-row"><span>${a}</span>
        <div class="bar-track"><div class="bar" style="width:${Math.max(2,pct)}%"></div></div>
        <span>${pct}%</span></div>`;
    }).join('');
  }

  function drawTo(n) {
    chart.data.labels = data.rounds.slice(0, n);
    chart.data.datasets[0].data = data.adaptive.cumulative.slice(0, n);
    chart.data.datasets[1].data = data.static.cumulative.slice(0, n);
    chart.update();
    document.getElementById('round-readout').textContent = `round ${n}`;
    if (n >= data.rounds.length) {
      document.getElementById('lift-readout').textContent =
        `+${data.lift_pct}% (illustrative, seed ${data.seed})`;
    }
  }

  function stop() { if (timer) { clearInterval(timer); timer = null; } }

  function play() {
    if (!data) return;
    stop();
    const total = data.rounds.length;
    const stepSize = Math.max(1, Math.floor(total / 80)); // ~80 frames
    timer = setInterval(() => {
      frame = Math.min(total, frame + stepSize);
      drawTo(frame);
      if (frame >= total) {
        stop();
        document.getElementById('mix-early').innerHTML = mixRows(data.adaptive.early_mix);
        document.getElementById('mix-late').innerHTML = mixRows(data.adaptive.late_mix);
      }
    }, 40);
  }

  async function loadAndReset() {
    stop(); frame = 0;
    document.getElementById('lift-readout').textContent = '';
    document.getElementById('learn-note').textContent = 'Running…';
    const algo = document.getElementById('algo').value;
    data = await API.learn({ algorithm: algo, seed: 42, n_rounds: 2000 });
    document.getElementById('learn-note').textContent = data.illustrative_note;
    document.getElementById('mix-early').innerHTML = '';
    document.getElementById('mix-late').innerHTML = '';
    drawTo(1);
  }

  async function init() {
    await renderHeadline();
    buildChart();
    document.getElementById('btn-play').addEventListener('click', play);
    document.getElementById('btn-reset').addEventListener('click', loadAndReset);
    document.getElementById('algo').addEventListener('change', loadAndReset);
    await loadAndReset();
  }

  return { init };
})();
```

- [ ] **Step 2: Verify the Learn view (manual)**

With the server running, open `http://127.0.0.1:8011/` → click **Watch it Learn**:
- The canonical headline strip shows `+25.2% vs Static XGB · 20 seeds · p < 0.001 · d = 2.98` with the admissible-scope tag.
- A run kicks off (≈2–4 s); **▶ Play** animates the adaptive line diverging above Static XGB; the round counter advances; at the end the `+X% (illustrative, seed 42)` readout and early/late action-mix bars appear.
- **Reset** and switching **LinUCB/LinTS** reruns.

- [ ] **Step 3: Commit**

```bash
rtk git add demo/desk/static/learn.js
rtk git commit -m "$(cat <<'EOF'
feat(desk): Watch-it-Learn divergence chart, animation, action-mix

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

### Task 10: Vendor Chart.js + full-system verification (verification-before-completion)

**Files:**
- Create: `demo/desk/static/chart.umd.min.js` (copied)

- [ ] **Step 1: Vendor Chart.js from the existing demo**

```bash
cp demo/static/chart.umd.min.js demo/desk/static/chart.umd.min.js
ls -la demo/desk/static/chart.umd.min.js
```

Expected: file copied, non-zero size. (If `demo/static/chart.umd.min.js` is absent, locate the vendored copy: `ls demo/static/*.js` — the 7-tab demo loads Chart.js, so it exists under `demo/static/`.)

- [ ] **Step 2: Run the full backend test suite**

Run: `python -m pytest tests/test_desk_app.py -q`
Expected: ALL PASS (13 tests). Capture the summary line.

- [ ] **Step 3: Confirm the existing demo is untouched (no regressions)**

Run: `python -m pytest tests/ -q`
Expected: no new failures vs baseline; the old demo tests still pass. Also confirm by inspection that `git status --porcelain demo/main.py demo/templates/index.html demo/static/defense.html demo/static/defense.js` prints nothing (those files were not modified).

```bash
rtk git status
```

- [ ] **Step 4: Full uvicorn smoke test (real server, all assets)**

```bash
python -m uvicorn demo.desk.app:app --port 8011 &
sleep 4
for p in / /static/index.html /static/api.js /static/main.js /static/desk.js /static/learn.js /static/chart.umd.min.js; do
  echo -n "$p -> "; curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8011$p
done
curl -s http://127.0.0.1:8011/api/health
echo
curl -s -X POST http://127.0.0.1:8011/api/score -H "Content-Type: application/json" \
  -d '{"age":45,"gender":"Female","bmi":24.5,"is_smoking":0,"alcohol_use":0,"is_exercise":1,"has_family_history":0,"monthly_income_usd":350,"region":"Phnom Penh","occupation":"Civil Servant","education":"Secondary","wealth_quintile":"Middle","self_reported_health":"Good"}' \
  | python -c "import sys,json; d=json.load(sys.stdin); print('decision:', d['decision'], '| confidence:', d['confidence'], '| drivers:', len(d['drivers']), '| badge:', d['fairness']['badge_status'])"
kill %1
```

Expected: every path returns `200`; `/api/health` → `{"status":"ok"}`; the score call prints a valid decision, a non-degenerate confidence, 3 drivers, and a GREEN/AMBER badge.

- [ ] **Step 5: Manual browser walkthrough (defense dry-run)**

Open `http://127.0.0.1:8011/` and confirm both flows end-to-end:
- **Desk:** Load sample → Score → full card. Clear → manual entry → Score.
- **Learn:** toggle → headline → Play animates divergence → action-mix populates; Reset + LinUCB/LinTS switch work.
- Offline-safe: no network/CDN requests (Chart.js is vendored).

- [ ] **Step 6: Commit + update memory**

```bash
rtk git add demo/desk/static/chart.umd.min.js
rtk git commit -m "$(cat <<'EOF'
feat(desk): vendor Chart.js; full two-view demo verified end-to-end

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

Then update `MEMORY.md` / `demo_rebuild_status.md`: mark the Underwriting Desk **implemented + verified** (13/13 backend tests; uvicorn smoke green; old demo untouched). Note the deferred **cutover** (§10: repoint `render.yaml` → `demo.desk.app:app`, delete old demo) as the next, separate step.

---

## Self-Review (against the spec)

**Spec coverage:**
- §5 endpoints: `/` (T1), `/api/applicant/fields` + `/api/applicant/random` (T2), `/api/score` (T4–T5), `/api/learn/run` (T6), `/api/health` (T1). Canonical loader (§7.2/§8) → `/api/canonical` (T3). ✓
- §6 scoring: bars `Θ·x`, argmax decision, softmax confidence (τ documented), top-3 signed drivers via `FEATURES`, action↔premium mapping, hidden `mortality_multiplier` default 1.0 → T4. ✓
- §3.5/§6 model-level fairness (cached, region+occupation, GREEN/AMBER/RED, never per-applicant) + §8 canonical zones → T5. ✓
- §7.1 Desk UI (grouped form, Load/Clear, result card) → T7–T8. §7.2 Learn UI (headline, animated divergence, Play/Reset, LinUCB/LinTS, action-mix) → T9. ✓
- §8 canonical-vs-illustrative discipline: headline only from `thesis_results.json`; every live number labelled illustrative → T3, T4, T6, T8, T9. ✓
- §9 error handling: Pydantic validation (422 tested T4/T6), inline form errors, JSON error surfaced as card text (T8). ✓
- §10 layout (`demo/desk/{app,scoring,learning}.py + static/`) → all tasks; cutover explicitly deferred (T10 note). ✓
- §11 tests: fields, random, score card shape, learn trajectories+mix, canonical loader-from-file, boot/health smoke → all in `tests/test_desk_app.py`. ✓
- §12 out-of-scope (HITL, batch, arena, deck, cutover) — none added. ✓
- §13 risks (mortality default, confidence τ, representative θ, model-level PSI wording) — handled + documented. ✓

**Placeholder scan:** every code step contains complete, runnable code; no TBD/"similar to"/"add validation" stubs. ✓

**Type/name consistency:** `ACTION_NAMES` order `[STANDARD,RATED,DECLINE,REFER]` used consistently; `score()` returns `decision/decision_index/confidence/estimated_rewards/drivers/premium/fairness/illustrative_note` — every key is asserted by a test and read by `desk.js`. `run_learn()` returns `algorithm/seed/n_rounds/rounds/adaptive{cumulative,final,early_mix,late_mix}/static{cumulative,final}/lift_pct/illustrative_note` — keys match `learn.js` and the tests. `/api/canonical` keys (`lift_pct/cohen_d/p_value/n_seeds/comparator/scope/ceiling_policy/ceiling_note`) match T3 test + `learn.js`. ✓
