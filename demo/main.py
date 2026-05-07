"""
FastAPI web demo for the actuarial reward simulator.

Run:
    uvicorn demo.main:app --reload --port 8000

Then open http://localhost:8000
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Path setup so we can import the RL module
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from stress_testing.rl.underwriting_bandit import (  # noqa: E402
    ACTION_NAMES,
    EpsilonGreedy,
    LinTS,
    LinUCB,
    RewardConfig,
    StaticXGBBaseline,
    expected_rewards,
    make_reward_simulator,
    preprocess_cambodia_data,
    run_bandit,
)
from demo.pricing_engine import optimize_premium, batch_optimize  # noqa: E402

# ---------------------------------------------------------------------------
# Load data once at startup
# ---------------------------------------------------------------------------
X, DF_RAW, FEATURES = preprocess_cambodia_data()
N_FEATURES = X.shape[1]

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="Actuarial Reward Simulator", version="1.0.0")

DEMO_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=DEMO_DIR / "static"), name="static")
templates = Jinja2Templates(directory=DEMO_DIR / "templates")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def _applicant_to_series(data: dict[str, Any]) -> pd.Series:
    """Build a pd.Series that mirrors a row of DF_RAW so expected_rewards() works."""
    return pd.Series(data)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

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
    mortality_multiplier: float = Field(..., ge=0.5, le=5.0)
    mode: str = "simple"  # "simple" or "realistic"


class SimulateResponse(BaseModel):
    applicant: dict[str, Any]
    expected_rewards: dict[str, float]
    optimal_action: str
    stochastic_run: dict[str, Any] | None = None


class BanditRunIn(BaseModel):
    algorithm: str = Field(..., pattern="^(LinUCB|LinTS|EpsilonGreedy|StaticXGB)$")
    n_rounds: int = Field(1000, ge=100, le=10000)
    seed: int = 42
    alpha: float = 1.0
    epsilon: float = 0.1
    v2: float = 1.0


class BanditRunResponse(BaseModel):
    algorithm: str
    n_rounds: int
    cumulative_reward: float
    cumulative_regret: float
    avg_regret_last_500: float
    action_distribution: dict[str, float]
    early_action_distribution: dict[str, float]
    late_action_distribution: dict[str, float]
    trajectory: dict[str, list[float]]


class CompareResponse(BaseModel):
    results: list[dict[str, Any]]


class PricingOptimizeResponse(BaseModel):
    optimal_multiplier: float
    optimal_premium_usd: float
    optimal_expected_profit: float
    optimal_p_accept: float
    curve: list[dict[str, Any]]
    legacy: dict[str, float]


class PricingBatchResponse(BaseModel):
    n_samples: int
    results: list[dict[str, Any]]
    summary: dict[str, Any]
    histogram: dict[str, Any]
    psi: dict[str, Any]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}





@app.get("/api/applicant/random")
async def random_applicant() -> dict[str, Any]:
    """Return a random applicant from the Cambodia dataset."""
    idx = int(np.random.default_rng().integers(len(DF_RAW)))
    return {"applicant": _row_to_applicant(DF_RAW.iloc[idx]), "index": int(idx)}


@app.get("/api/applicant/fields")
async def applicant_fields() -> dict[str, Any]:
    """Return categorical field options derived from the dataset."""
    return {
        "regions": sorted(DF_RAW["region"].dropna().unique().tolist()),
        "occupations": sorted(DF_RAW["occupation"].dropna().unique().tolist()),
        "educations": ["No education", "Primary", "Secondary", "Higher"],
        "wealth_quintiles": ["Poorest", "Poorer", "Middle", "Richer", "Richest"],
        "health_statuses": ["Poor", "Fair", "Good"],
        "conditions": [
            "Hypertension",
            "Diabetes",
            "Heart Disease",
            "COPD/Asthma",
            "Arthritis",
            "TB",
            "Hepatitis B",
        ],
    }


def _get_config(mode: str) -> RewardConfig:
    if mode.lower() == "realistic":
        return RewardConfig.realistic()
    return RewardConfig()


@app.post("/api/simulate", response_model=SimulateResponse)
async def simulate_applicant(payload: ApplicantIn) -> SimulateResponse:
    """
    Compute expected rewards for all 4 underwriting actions for a given applicant.
    """
    row = _applicant_to_series(payload.model_dump())
    config = _get_config(payload.mode)
    exp = expected_rewards(row, config)
    opt_action = ACTION_NAMES[int(np.argmax(exp))]

    expected = {
        ACTION_NAMES[i]: round(float(exp[i]), 2) for i in range(len(ACTION_NAMES))
    }

    return SimulateResponse(
        applicant=payload.model_dump(),
        expected_rewards=expected,
        optimal_action=opt_action,
    )


@app.post("/api/simulate/stochastic")
async def simulate_stochastic(payload: ApplicantIn, seed: int = 42) -> dict[str, Any]:
    """Run a stochastic realisation for each of the 4 actions."""
    row = _applicant_to_series(payload.model_dump())
    config = _get_config(payload.mode)
    rng = np.random.default_rng(seed)
    reward_fn = make_reward_simulator(rng, config)

    outcomes = {}
    for a in range(4):
        r = reward_fn(a, row)
        outcomes[ACTION_NAMES[a]] = {
            "reward": round(float(r), 2),
            "outcome": _describe_outcome(a, r, row, config),
        }

    return {
        "applicant": payload.model_dump(),
        "seed": seed,
        "mode": payload.mode,
        "outcomes": outcomes,
    }


def _describe_outcome(action: int, reward: float, row: pd.Series, config: RewardConfig | None = None) -> str:
    """Human-readable description of what happened."""
    cfg = config if config is not None else RewardConfig()
    if action == 2:  # DECLINE
        return f"Application declined. Opportunity cost (${cfg.decline_cost:.0f})."
    if action == 3:  # REFER
        return f"Referred to manual underwriter. Net reward ${reward:.0f}."
    # STANDARD or RATED
    base_premium = cfg.base_premium_rate * row["mortality_multiplier"]
    monthly_premium = (base_premium * (1.0 if action == 0 else 1.25)) / 12
    monthly_income = row["monthly_income_usd"]
    ratio = monthly_premium / monthly_income
    p_acc = max(cfg.min_acceptance, cfg.acceptance_intercept - cfg.acceptance_slope * ratio)
    if reward > 0:
        extras = []
        if cfg.expense_fixed > 0 or cfg.expense_ratio > 0:
            extras.append("expenses deducted")
        if cfg.clv_multiplier > 1.0:
            extras.append(f"CLVx{cfg.clv_multiplier}")
        suffix = f" ({', '.join(extras)})" if extras else ""
        return f"Customer accepted (p={p_acc:.1%}). Net reward positive{suffix}."
    return f"Customer rejected or net negative. Walk cost applied."


@app.post("/api/bandit/run", response_model=BanditRunResponse)
async def bandit_run(payload: BanditRunIn) -> BanditRunResponse:
    """Run a single bandit algorithm for N rounds and return trajectory data."""
    algo_name = payload.algorithm

    if algo_name == "LinUCB":
        bandit = LinUCB(n_actions=4, n_features=N_FEATURES, alpha=payload.alpha)
    elif algo_name == "LinTS":
        bandit = LinTS(n_actions=4, n_features=N_FEATURES, v2=payload.v2)
    elif algo_name == "EpsilonGreedy":
        bandit = EpsilonGreedy(n_actions=4, n_features=N_FEATURES, epsilon=payload.epsilon)
    elif algo_name == "StaticXGB":
        bandit = StaticXGBBaseline()
    else:
        raise ValueError(f"Unknown algorithm: {algo_name}")

    result = run_bandit(algo_name, bandit, X.copy(), DF_RAW, payload.n_rounds, seed=payload.seed)

    n = payload.n_rounds
    early_n = min(500, n // 2)
    late_n = min(500, n // 2)

    def _dist(actions_slice: np.ndarray) -> dict[str, float]:
        counts = np.bincount(actions_slice.astype(int), minlength=4)
        total = counts.sum()
        return {ACTION_NAMES[i]: round(float(counts[i] / total), 4) for i in range(4)}

    trajectory = {
        "rounds": list(range(1, n + 1)),
        "cumulative_rewards": [round(float(v), 2) for v in result.cumulative_rewards],
        "cumulative_regrets": [round(float(v), 2) for v in result.cumulative_regrets],
        "rewards": [round(float(v), 2) for v in result.rewards],
        "regrets": [round(float(v), 2) for v in result.regrets],
        "actions": [int(v) for v in result.actions],
    }

    return BanditRunResponse(
        algorithm=algo_name,
        n_rounds=n,
        cumulative_reward=round(float(result.cumulative_rewards[-1]), 2),
        cumulative_regret=round(float(result.cumulative_regrets[-1]), 2),
        avg_regret_last_500=round(float(np.mean(result.regrets[-500:])), 2),
        action_distribution=_dist(result.actions),
        early_action_distribution=_dist(result.actions[:early_n]),
        late_action_distribution=_dist(result.actions[-late_n:]),
        trajectory=trajectory,
    )


@app.post("/api/bandit/compare")
async def bandit_compare(payload: BanditRunIn) -> CompareResponse:
    """Run all 4 algorithms with the same settings and return a comparison."""
    configs = [
        ("LinUCB", LinUCB(n_actions=4, n_features=N_FEATURES, alpha=payload.alpha)),
        ("LinTS", LinTS(n_actions=4, n_features=N_FEATURES, v2=payload.v2)),
        ("EpsilonGreedy", EpsilonGreedy(n_actions=4, n_features=N_FEATURES, epsilon=payload.epsilon)),
        ("StaticXGB", StaticXGBBaseline()),
    ]

    results = []
    for name, bandit in configs:
        res = run_bandit(name, bandit, X.copy(), DF_RAW, payload.n_rounds, seed=payload.seed)
        results.append({
            "algorithm": name,
            "cumulative_reward": round(float(res.cumulative_rewards[-1]), 2),
            "cumulative_regret": round(float(res.cumulative_regrets[-1]), 2),
            "avg_regret_last_500": round(float(np.mean(res.regrets[-500:])), 2),
            "action_distribution": {
                ACTION_NAMES[i]: int(np.bincount(res.actions, minlength=4)[i]) for i in range(4)
            },
            "trajectory": {
                "rounds": list(range(1, payload.n_rounds + 1)),
                "cumulative_rewards": [round(float(v), 2) for v in res.cumulative_rewards],
                "cumulative_regrets": [round(float(v), 2) for v in res.cumulative_regrets],
            },
        })

    return CompareResponse(results=results)


@app.post("/api/pricing/optimize", response_model=PricingOptimizeResponse)
async def pricing_optimize(payload: ApplicantIn) -> PricingOptimizeResponse:
    """Find the profit-maximising premium multiplier for a single applicant."""
    row = _applicant_to_series(payload.model_dump())
    config = _get_config(payload.mode)
    result = optimize_premium(row, config)
    return PricingOptimizeResponse(**result)


@app.post("/api/pricing/batch")
async def pricing_batch(payload: BanditRunIn) -> PricingBatchResponse:
    """Run premium optimisation on a random sample of applicants."""
    config = RewardConfig()
    result = batch_optimize(DF_RAW, n_samples=100, config=config, seed=payload.seed)
    return PricingBatchResponse(**result)


# ---------------------------------------------------------------------------
# Dev entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("demo.main:app", host="127.0.0.1", port=8000, reload=True)
