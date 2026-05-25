"""Multi-seed experiment runner for bandit experiments.

Provides two aggregation modes:

* ``run_experiment_seeds`` — classic mean ± std (backward-compatible).
* ``run_experiment_seeds_raw`` — returns full distributions for statistical
  inference (bootstrap CIs, Wilcoxon tests, effect sizes).
"""
from __future__ import annotations

from typing import Callable, Any
import numpy as np


def run_experiment_seeds(
    exp_fn: Callable[[int], dict[str, float]],
    n_seeds: int = 20,
) -> dict[str, tuple[float, float]]:
    """Run *exp_fn(seed)* for seeds 0 … n_seeds-1 and aggregate scalar metrics.

    Args:
        exp_fn: Callable that takes a seed (int) and returns a dict of
                {metric_name: float}.
        n_seeds: Number of independent seeds (default 20).

    Returns:
        Dict of {metric_name: (mean, std)}.
    """
    results: list[dict[str, float]] = []
    for seed in range(n_seeds):
        print(f"  Seed {seed + 1}/{n_seeds} ...", flush=True)
        results.append(exp_fn(seed))

    keys = results[0].keys()
    aggregated: dict[str, tuple[float, float]] = {}
    for key in keys:
        vals = np.array([r[key] for r in results])
        aggregated[key] = (float(vals.mean()), float(vals.std()))
    return aggregated


def run_experiment_seeds_raw(
    exp_fn: Callable[[int], dict[str, float]],
    n_seeds: int = 20,
) -> dict[str, dict[str, Any]]:
    """Run *exp_fn(seed)* and return full distributions for inference.

    Unlike ``run_experiment_seeds``, this returns every raw observation
    so that downstream statistical tests (bootstrap CIs, Wilcoxon signed-rank,
    effect sizes) can be applied.

    Args:
        exp_fn: Callable that takes a seed (int) and returns a dict of
                {metric_name: float}.
        n_seeds: Number of independent seeds (default 20).

    Returns:
        Dict of {metric_name: {"values": np.ndarray, "mean": float,
        "std": float, "median": float, "q25": float, "q75": float}}.
    """
    results: list[dict[str, float]] = []
    for seed in range(n_seeds):
        print(f"  Seed {seed + 1}/{n_seeds} ...", flush=True)
        results.append(exp_fn(seed))

    keys = results[0].keys()
    aggregated: dict[str, dict[str, Any]] = {}
    for key in keys:
        vals = np.array([r[key] for r in results])
        aggregated[key] = {
            "values": vals,
            "mean": float(vals.mean()),
            "std": float(vals.std(ddof=1)),
            "median": float(np.median(vals)),
            "q25": float(np.percentile(vals, 25)),
            "q75": float(np.percentile(vals, 75)),
            "min": float(vals.min()),
            "max": float(vals.max()),
        }
    return aggregated
