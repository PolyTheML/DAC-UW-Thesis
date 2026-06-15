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
