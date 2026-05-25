"""Dynamic premium optimisation engine.

Searches a fine grid of premium multipliers (0.5× – 3.0×) and returns the
profit-maximising price for a given applicant profile.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# Path setup so we can import the RL module when this file is imported standalone
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from healthrl.underwriting_bandit import (  # noqa: E402
    RewardConfig,
    expected_rewards,
)


def compute_psi(expected_dist: np.ndarray, actual_dist: np.ndarray) -> float:
    """Population Stability Index between two distributions.

    Same formula used in EXP-006 fairness audit.
    """
    eps = 1e-8
    expected_dist = expected_dist / (expected_dist.sum() + eps)
    actual_dist = actual_dist / (actual_dist.sum() + eps)
    psi = 0.0
    for e, a in zip(expected_dist, actual_dist):
        if e > eps:
            psi += (a - e) * np.log((a + eps) / (e + eps))
        elif a > eps:
            psi += a - e
    return float(psi)


def _age_bin(age: int) -> str:
    if age <= 30:
        return "18–30"
    if age <= 45:
        return "31–45"
    if age <= 60:
        return "46–60"
    return "61+"


def compute_batch_psi(
    batch_df: pd.DataFrame,
    reference_df: pd.DataFrame,
) -> dict[str, Any]:
    """Compute PSI for key features comparing batch vs. full reference dataset."""
    features = {
        "region": "Region",
        "occupation": "Occupation",
        "wealth_quintile": "Wealth Quintile",
    }
    psi_results = {}

    for col, label in features.items():
        ref_counts = reference_df[col].value_counts().sort_index()
        act_counts = batch_df[col].value_counts().reindex(ref_counts.index, fill_value=0)
        psi = compute_psi(ref_counts.values, act_counts.values)
        psi_results[col] = {
            "label": label,
            "psi": round(psi, 4),
            "status": "GREEN" if psi < 0.10 else "AMBER" if psi < 0.25 else "RED",
        }

    # Age bins
    ref_age = reference_df["age"].apply(_age_bin).value_counts().reindex(["18–30", "31–45", "46–60", "61+"], fill_value=0)
    act_age = batch_df["age"].apply(_age_bin).value_counts().reindex(["18–30", "31–45", "46–60", "61+"], fill_value=0)
    age_psi = compute_psi(ref_age.values, act_age.values)
    psi_results["age_bin"] = {
        "label": "Age Bin",
        "psi": round(age_psi, 4),
        "status": "GREEN" if age_psi < 0.10 else "AMBER" if age_psi < 0.25 else "RED",
    }

    return psi_results


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


def _adverse_for_multiplier(m: float, base_adverse: float, rated_m: float = 1.25) -> float:
    """Adverse-selection factor as a function of premium multiplier.

    At the standard rate (m=1.0) the full adverse factor applies.
    At the rated threshold (m=rated_m) and above it drops to 1.0.
    Below 1.0 it increases linearly (underpricing attracts worse risk).
    """
    if m >= rated_m:
        return 1.0
    return base_adverse - (base_adverse - 1.0) * (m - 1.0) / (rated_m - 1.0)


def optimize_premium(
    row: pd.Series,
    config: RewardConfig | None = None,
    multipliers: np.ndarray | None = None,
) -> dict[str, Any]:
    """Grid-search the optimal premium multiplier for a single applicant.

    Parameters
    ----------
    row : pd.Series
        Applicant profile (mirrors a row of DF_RAW).
    config : RewardConfig, optional
        Actuarial parameters. Defaults to simple config.
    multipliers : np.ndarray, optional
        Grid of multipliers to search. Defaults to 0.5–3.0 in 0.05 steps.

    Returns
    -------
    dict
        optimal_multiplier, optimal_premium_usd, optimal_expected_profit,
        optimal_p_accept, full curve, and legacy 4-action comparison.
    """
    cfg = config if config is not None else RewardConfig()
    mort = float(row["mortality_multiplier"])
    income = float(row["monthly_income_usd"])

    base_premium = cfg.base_premium_rate * mort
    expected_claims = cfg.expected_claims_rate * mort
    base_adverse = 1.0 if mort <= cfg.adverse_threshold else cfg.adverse_factor

    if multipliers is None:
        multipliers = np.arange(0.5, 3.01, 0.05)

    def _expenses(premium: float) -> float:
        return cfg.expense_fixed + cfg.expense_ratio * premium

    def _net(premium: float, claims: float, expenses: float) -> float:
        if cfg.lapse_prob > 0:
            return (
                premium * (1 - cfg.lapse_prob * (1 - cfg.lapse_premium_factor))
                - claims * (1 - cfg.lapse_prob * (1 - cfg.lapse_claims_factor))
                - expenses
            ) * cfg.clv_multiplier
        return (premium - claims - expenses) * cfg.clv_multiplier

    curve = []
    for m in multipliers:
        premium = base_premium * m
        adverse = _adverse_for_multiplier(float(m), base_adverse)
        claims = expected_claims * adverse
        expenses = _expenses(premium)
        ratio = (premium / 12.0) / income
        p_acc = max(cfg.min_acceptance, cfg.acceptance_intercept - cfg.acceptance_slope * ratio)
        net_val = _net(premium, claims, expenses)
        exp_profit = p_acc * net_val + (1.0 - p_acc) * cfg.walk_cost
        curve.append({
            "multiplier": round(float(m), 2),
            "premium_usd": round(float(premium), 2),
            "p_accept": round(float(p_acc), 4),
            "expected_profit": round(float(exp_profit), 2),
        })

    profits = np.array([c["expected_profit"] for c in curve])
    opt_idx = int(np.argmax(profits))
    optimal = curve[opt_idx]

    # Legacy 4-action comparison (uses the original underwriting_bandit logic)
    legacy = expected_rewards(row, cfg)

    return {
        "optimal_multiplier": optimal["multiplier"],
        "optimal_premium_usd": optimal["premium_usd"],
        "optimal_expected_profit": optimal["expected_profit"],
        "optimal_p_accept": optimal["p_accept"],
        "curve": curve,
        "legacy": {
            "STANDARD": round(float(legacy[0]), 2),
            "RATED": round(float(legacy[1]), 2),
            "DECLINE": round(float(legacy[2]), 2),
            "REFER": round(float(legacy[3]), 2),
        },
    }


def batch_optimize(
    df_raw: pd.DataFrame,
    n_samples: int = 100,
    config: RewardConfig | None = None,
    seed: int = 42,
) -> dict[str, Any]:
    """Run premium optimisation on a random sample of applicants.

    Returns a list of per-applicant results plus aggregate statistics
    and PSI drift metrics against the full reference dataset.
    """
    rng = np.random.default_rng(seed)
    indices = rng.choice(len(df_raw), size=min(n_samples, len(df_raw)), replace=False)

    batch_df = df_raw.iloc[indices]

    results = []
    for idx in indices:
        row = df_raw.iloc[idx]
        opt = optimize_premium(row, config)
        results.append({
            "applicant": _row_to_applicant(row),
            "optimal_multiplier": opt["optimal_multiplier"],
            "optimal_premium_usd": opt["optimal_premium_usd"],
            "optimal_expected_profit": opt["optimal_expected_profit"],
            "optimal_p_accept": opt["optimal_p_accept"],
        })

    multipliers = np.array([r["optimal_multiplier"] for r in results])
    profits = np.array([r["optimal_expected_profit"] for r in results])

    psi = compute_batch_psi(batch_df, df_raw)

    return {
        "n_samples": len(results),
        "results": results,
        "summary": {
            "avg_multiplier": round(float(np.mean(multipliers)), 3),
            "median_multiplier": round(float(np.median(multipliers)), 3),
            "std_multiplier": round(float(np.std(multipliers)), 3),
            "min_multiplier": round(float(np.min(multipliers)), 3),
            "max_multiplier": round(float(np.max(multipliers)), 3),
            "avg_expected_profit": round(float(np.mean(profits)), 2),
            "median_expected_profit": round(float(np.median(profits)), 2),
        },
        "histogram": {
            "bins": [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0],
            "counts": [
                int(np.sum((multipliers >= 0.5) & (multipliers < 0.75))),
                int(np.sum((multipliers >= 0.75) & (multipliers < 1.0))),
                int(np.sum((multipliers >= 1.0) & (multipliers < 1.25))),
                int(np.sum((multipliers >= 1.25) & (multipliers < 1.5))),
                int(np.sum((multipliers >= 1.5) & (multipliers < 1.75))),
                int(np.sum((multipliers >= 1.75) & (multipliers < 2.0))),
                int(np.sum((multipliers >= 2.0) & (multipliers < 2.5))),
                int(np.sum((multipliers >= 2.5) & (multipliers <= 3.0))),
            ],
        },
        "psi": psi,
    }
