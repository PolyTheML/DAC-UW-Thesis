"""Online-learning showcase: adaptive policy vs static baseline (spec §7.2).

Reuses healthrl.run_bandit. Returns full trajectories; the client animates
them (no server streaming). Live numbers are single-seed and illustrative.
"""
from __future__ import annotations

from functools import lru_cache
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


# Exploration presets (spec §4): behaviour label → resolved engine knob per algorithm.
# LinUCB reads `alpha` (UCB bonus scale); LinTS reads `v2` (posterior variance).
# Balanced = the thesis default (today's behaviour). Anchors are thesis-grounded but
# deliberately tunable constants — adjust here to sharpen the on-screen contrast.
EXPLORATION_PRESETS: dict[str, dict[str, float]] = {
    "Greedy": {"alpha": 0.0, "v2": 0.25},
    "Balanced": {"alpha": 1.0, "v2": 1.0},
    "Exploratory": {"alpha": 3.0, "v2": 4.0},
}


def _mix(actions: np.ndarray) -> dict[str, float]:
    counts = np.bincount(actions.astype(int), minlength=4)
    total = int(counts.sum()) or 1
    return {ACTION_NAMES[i]: round(float(counts[i] / total), 4) for i in range(4)}


@lru_cache(maxsize=32)
def _run_learn_cached(
    algorithm: str, seed: int, n_rounds: int, exploration: str
) -> str:
    """Cached JSON string (immutable) of a deterministic learn run."""
    import json
    return json.dumps(_run_learn_impl(algorithm, seed, n_rounds, exploration))


def run_learn(
    algorithm: str,
    seed: int = 42,
    n_rounds: int = 2000,
    exploration: str = "Balanced",
) -> dict[str, Any]:
    import json
    return json.loads(_run_learn_cached(algorithm, seed, n_rounds, exploration))


def _run_learn_impl(
    algorithm: str,
    seed: int = 42,
    n_rounds: int = 2000,
    exploration: str = "Balanced",
) -> dict[str, Any]:
    if exploration not in EXPLORATION_PRESETS:
        raise ValueError(f"Unknown exploration preset: {exploration}")
    preset = EXPLORATION_PRESETS[exploration]

    if algorithm == "LinUCB":
        adaptive = LinUCB(n_actions=4, n_features=N_FEATURES, alpha=preset["alpha"])
        param = {"name": "alpha", "value": preset["alpha"]}
    elif algorithm == "LinTS":
        adaptive = LinTS(n_actions=4, n_features=N_FEATURES, v2=preset["v2"], seed=seed)
        param = {"name": "v2", "value": preset["v2"]}
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
        "exploration": exploration,
        "param": param,
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
