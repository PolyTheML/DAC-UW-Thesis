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
from demo import hitl_db  # noqa: E402

# ---------------------------------------------------------------------------
# Load data once at startup
# ---------------------------------------------------------------------------
X, DF_RAW, FEATURES = preprocess_cambodia_data()
N_FEATURES = X.shape[1]

# ---------------------------------------------------------------------------
# HITL state (single underwriter, in-memory bandit that learns from overrides)
# ---------------------------------------------------------------------------
HITL_BANDIT = LinUCB(n_actions=4, n_features=N_FEATURES, alpha=1.0)
HITL_REWARD_CFG = RewardConfig()  # simple deterministic config

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


class HITLRecommendResponse(BaseModel):
    applicant: dict[str, Any]
    index: int
    bandit_action: int
    bandit_action_name: str
    expected_rewards: dict[str, float]


class HITLReviewRequest(BaseModel):
    index: int = Field(..., ge=0, lt=len(DF_RAW))
    bandit_action: int = Field(..., ge=0, le=3)
    override_action: int = Field(..., ge=0, le=2)
    underwriter: str = Field(default="Underwriter")


class HITLReviewResponse(BaseModel):
    reward: float
    saved: bool
    metrics: dict[str, Any]


class HITLMetricsResponse(BaseModel):
    total_reviews: int
    override_rate: float | None
    alignment_rate: float | None
    avg_reward: float | None
    cumulative_reward: float
    human_cost: float
    recent_rewards: list[float]
    psi: dict[str, Any] | None


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
# HITL (Human-in-the-Loop) Underwriter Review
# ---------------------------------------------------------------------------

@app.get("/api/hitl/recommend")
async def hitl_recommend() -> HITLRecommendResponse:
    """Generate a random applicant and bandit recommendation for underwriter review."""
    rng = np.random.default_rng()
    idx = int(rng.integers(len(DF_RAW)))
    row = DF_RAW.iloc[idx]
    applicant = _row_to_applicant(row)
    context = np.asarray(X[idx], dtype=float)

    bandit_action = int(HITL_BANDIT.select_action(context))
    exp = expected_rewards(row, HITL_REWARD_CFG)

    expected = {
        ACTION_NAMES[i]: round(float(exp[i]), 2) for i in range(len(ACTION_NAMES))
    }

    return HITLRecommendResponse(
        applicant=applicant,
        index=idx,
        bandit_action=bandit_action,
        bandit_action_name=ACTION_NAMES[bandit_action],
        expected_rewards=expected,
    )


@app.post("/api/hitl/review")
async def hitl_review(payload: HITLReviewRequest) -> HITLReviewResponse:
    """Record a human override, compute reward, update the bandit, and return metrics."""
    idx = payload.index
    if idx < 0 or idx >= len(DF_RAW):
        raise ValueError(f"Index {idx} out of range [0, {len(DF_RAW)})")

    override_action = payload.override_action
    if override_action not in (0, 1, 2):
        raise ValueError("override_action must be 0 (STANDARD), 1 (RATED), or 2 (DECLINE)")

    row = DF_RAW.iloc[idx]
    applicant = _row_to_applicant(row)
    context = np.asarray(X[idx], dtype=float)

    # Compute deterministic reward for the human's chosen action
    exp = expected_rewards(row, HITL_REWARD_CFG)
    reward = float(exp[override_action])

    # Update bandit on the human's decision
    HITL_BANDIT.update(override_action, context, reward)

    # Persist to sqlite
    row_id = hitl_db.save_review(
        applicant=applicant,
        bandit_action=payload.bandit_action,
        override_action=override_action,
        reward=reward,
        underwriter=payload.underwriter,
    )

    metrics = hitl_db.get_metrics(window=50)

    return HITLReviewResponse(
        reward=round(reward, 2),
        saved=row_id is not None,
        metrics=metrics,
    )


@app.get("/api/hitl/metrics")
async def hitl_metrics() -> HITLMetricsResponse:
    """Return current HITL metrics including PSI on the approved pool."""
    metrics = hitl_db.get_metrics(window=50)
    psi = hitl_db.compute_approved_psi(DF_RAW)
    return HITLMetricsResponse(
        total_reviews=metrics["total_reviews"],
        override_rate=metrics["override_rate"],
        alignment_rate=metrics["alignment_rate"],
        avg_reward=metrics["avg_reward"],
        cumulative_reward=metrics["cumulative_reward"],
        human_cost=metrics["human_cost"],
        recent_rewards=metrics["recent_rewards"],
        psi=psi,
    )


@app.get("/api/hitl/export")
async def hitl_export() -> dict[str, str]:
    """Return the review log as a CSV string."""
    csv_data = hitl_db.export_csv()
    return {"csv": csv_data}


# ---------------------------------------------------------------------------
# Dev entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("demo.main:app", host="127.0.0.1", port=8000, reload=True)
