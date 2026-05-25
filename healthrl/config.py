"""Central configuration for healthrl experiments.

All experiment-wide constants live here so that:
1. Methodology changes (e.g., N_ROUNDS, n_seeds) require editing one file.
2. Cross-chapter consistency is mechanical: chapters quote these constants
   by name and the actual numbers stay synchronized with code.

Add new constants here rather than introducing module-level constants in
individual exp_*.py scripts.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExperimentConfig:
    """Common settings for every multi-seed experiment."""
    n_rounds: int = 5000
    n_seeds: int = 20
    primary_seed: int = 42
    psi_window: int = 500
    drift_shock_round: int = 1500


@dataclass(frozen=True)
class BanditConfig:
    """Default bandit hyperparameters.

    These match the methodology declarations in thesis Ch IV §§4.6.1-4.6.3.
    Override per-experiment if the experiment is intentionally exploring
    a different setting (e.g., exp_012 sensitivity sweep over alpha).
    """
    linucb_alpha: float = 1.0
    lints_v2: float = 1.0
    epsilon: float = 0.15


EXPERIMENT = ExperimentConfig()
BANDIT = BanditConfig()
