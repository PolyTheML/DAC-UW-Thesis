"""Figure F3 -- exploration scheme x operating regime. Thesis appendix.

Juxtaposes the stationary and drift regimes to show what does (and does not) drive
the bandit's behaviour. Reuses the canonical harnesses so the curves reproduce the
frozen numbers:
  (a) stationary (EXP-007, common random numbers): cumulative regret of the three
      learners -- LinUCB, LinTS, eps-Greedy. LinUCB ~ LinTS; both far below eps-Greedy.
  (b) drift (EXP-009): rolling 100-round regret of LinUCB, LinTS, Static XGB around
      the round-1,500 shock (reuses gen_fig15_drift.collect).

HONEST FRAMING (Sec. 5.7 and Sec. 5.9.5 -- NOT the 2026-06-03 pre-reframe plan):
the stationary panel shows the penalty is for *uninformed* (uniform) exploration,
not for the UCB bonus, which Sec. 5.7 finds is not load-bearing; the drift panel
shows adaptation beats the *frozen rule* but, per Sec. 5.9.5, no adaptive policy
beats the best constant even under drift.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "healthrl" / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from healthrl.underwriting_bandit import (   # noqa: E402
    LinUCB, LinTS, EpsilonGreedy, RewardConfig,
    preprocess_cambodia_data, run_bandit,
)
from healthrl.config import EXPERIMENT, BANDIT   # noqa: E402
from statistical_utils import bootstrap_ci        # noqa: E402
import gen_fig15_drift as g15                      # noqa: E402  (reuse the EXP-009 drift collection)
from _style import apply_style, save, PALETTE, ci_band   # noqa: E402
import matplotlib.pyplot as plt                    # noqa: E402

N = EXPERIMENT.n_rounds
SEEDS = range(EXPERIMENT.n_seeds)
ROUNDS = np.arange(1, N + 1)


def band(curves, n_sub=200):
    mean_full = curves.mean(0)
    idx = np.unique(np.linspace(0, curves.shape[1] - 1, n_sub).astype(int))
    lo = np.empty(len(idx)); hi = np.empty(len(idx))
    for j, i in enumerate(idx):
        lo[j], hi[j] = bootstrap_ci(curves[:, i])
    return mean_full, idx, lo, hi


def collect_stationary():
    """EXP-007 harness (common random numbers) -- cumulative regret per learner."""
    X, df_raw, _ = preprocess_cambodia_data()
    nf = X.shape[1]
    reg = {"LinUCB": [], "LinTS": [], "EpsilonGreedy": []}
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        cfg = RewardConfig()
        acc = rng.random(N)
        noise = rng.uniform(cfg.claims_noise_low, cfg.claims_noise_high, size=N)
        algos = {
            "LinUCB": LinUCB(4, nf, alpha=BANDIT.linucb_alpha),
            "LinTS": LinTS(4, nf, v2=BANDIT.lints_v2, seed=seed),
            "EpsilonGreedy": EpsilonGreedy(4, nf, epsilon=BANDIT.epsilon, seed=seed),
        }
        for name, b in algos.items():
            r = run_bandit(name, b, X.copy(), df_raw, N, seed=seed,
                           acceptance_draws=acc, claims_noise=noise)
            reg[name].append(r.cumulative_regrets)
        print(f"  [stationary] seed {seed + 1}/{EXPERIMENT.n_seeds}", flush=True)
    return {k: np.array(v) for k, v in reg.items()}


def main():
    print("F3 (a): stationary EXP-007 harness ...")
    stat = collect_stationary()
    print("F3 (b): drift EXP-009 harness ...")
    drift = g15.collect(EXPERIMENT.n_seeds)

    print("\n=== F3 reproduction cross-check ===")
    print("  stationary final cum. regret (frozen: LinTS 21,149 | LinUCB 22,774 | eG 38,281):")
    for k in ("LinTS", "LinUCB", "EpsilonGreedy"):
        print(f"    {k:14s} {stat[k][:, -1].mean():11,.0f}")
    print("  drift post-shock regret/round (frozen: LinUCB 2.48 | LinTS 2.42 | Static 7.44):")
    for k in ("LinUCB", "LinTS", "StaticXGB"):
        print(f"    {k:10s} {drift[k][:, g15.SHOCK:].mean():.2f}")

    apply_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.8, 3.7))

    # (a) stationary cumulative regret
    for name, col, lab in (("LinTS", "lints", "LinTS"), ("LinUCB", "linucb", "LinUCB"),
                           ("EpsilonGreedy", "epsilon", r"$\varepsilon$-Greedy")):
        m, idx, lo, hi = band(stat[name])
        ax1.plot(ROUNDS, m, color=PALETTE[col], label=lab, linewidth=1.5)
        ci_band(ax1, ROUNDS[idx], lo, hi, PALETTE[col])
    ax1.set_xlabel("Round")
    ax1.set_ylabel("Cumulative regret (\\$)")
    ax1.set_xlim(0, N)
    ax1.legend(loc="upper left", fontsize=8)
    ax1.set_title("(a) Stationary regime (EXP-007)", fontsize=9)

    # (b) drift rolling per-round regret
    WIN = g15.WINDOW
    SHOCK = g15.SHOCK
    kernel = np.ones(WIN) / WIN
    dr_rounds = np.arange(WIN - 1, N)
    for key, col, lab in (("LinTS", "lints", "LinTS"), ("LinUCB", "linucb", "LinUCB"),
                          ("StaticXGB", "static", "Static XGB")):
        smoothed = np.array([np.convolve(drift[key][s], kernel, mode="valid")
                             for s in range(drift[key].shape[0])])
        m, idx, lo, hi = band(smoothed)
        ax2.plot(dr_rounds, m, color=PALETTE[col], label=lab, linewidth=1.5)
        ci_band(ax2, dr_rounds[idx], lo, hi, PALETTE[col])
    ax2.axvline(SHOCK, ls="--", lw=1.1, color="#333333", label="Shock (round 1,500)")
    ax2.set_xlabel("Round")
    ax2.set_ylabel(f"Regret / round (\\$, rolling {WIN})")
    ax2.set_xlim(0, N)
    ax2.set_ylim(bottom=0)
    ax2.legend(loc="upper right", fontsize=8)
    ax2.set_title("(b) Drift regime (EXP-009)", fontsize=9)

    fig.tight_layout()
    save(fig, "fig_exploration_regime")
    print("\nwrote fig_exploration_regime (.pdf + .png)")


if __name__ == "__main__":
    main()
