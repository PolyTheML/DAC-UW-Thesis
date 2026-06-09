"""Figure 15 -- EXP-009 drift adaptation, re-rendered in the publication style.

FIDELITY FIX (advisor-confirmed): the figure backs the 20-seed Table 19 result, so it now
shows the CROSS-SEED MEAN rolling-100 regret per round with a 95% bootstrap CI band over
the 20 seeds -- NOT the single illustrative seed 42. A single seed's per-round regret is
too noisy to show the post-shock separation; the 20-seed mean makes it clear and matches
the established Fig 8/12 house style. This is a deliberate, *noted* exception to the §5.0
"seed = 42 for trajectory figures unless noted" convention (the §5.0 clause permits it).

Each seed's per-round regret is smoothed (rolling 100) FIRST, then averaged across seeds,
so the band is a genuine seed-to-seed spread. The plotted post-shock region reproduces
Table 19 (LinUCB 2.48, LinTS 2.42, Static 7.44 $/round). exp_009 is unmodified. Title
stripped. Band is 95% bootstrap CI; Table 19 reports ±std -- different measures.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "healthrl" / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from healthrl.underwriting_bandit import (   # noqa: E402
    LinUCB, LinTS, StaticXGBBaseline, preprocess_cambodia_data, DATA_PATH,
)
from healthrl.config import EXPERIMENT, BANDIT   # noqa: E402
import exp_009_drift_adaptation as e9            # noqa: E402
from statistical_utils import bootstrap_ci        # noqa: E402
from _style import apply_style, save, PALETTE, ci_band   # noqa: E402
import matplotlib.pyplot as plt                   # noqa: E402

N = e9.N_ROUNDS
SHOCK = e9.SHOCK_ROUND
WINDOW = e9.WINDOW


def band(curves, n_sub=200):
    """Full-res mean + bootstrap 95% CI at n_sub sampled rounds (verbatim from gen_results_curves)."""
    mean_full = curves.mean(0)
    idx = np.unique(np.linspace(0, curves.shape[1] - 1, n_sub).astype(int))
    lo = np.empty(len(idx)); hi = np.empty(len(idx))
    for j, i in enumerate(idx):
        lo[j], hi[j] = bootstrap_ci(curves[:, i])
    return mean_full, idx, lo, hi


def collect(n_seeds):
    """Per-round regret for each algo across n_seeds (mirrors exp_009.run seeding exactly)."""
    X_pre, df_pre, feats = preprocess_cambodia_data()
    stats = {c: (df_pre[c].mean(), df_pre[c].std()) for c in feats}
    df_raw = pd.read_csv(DATA_PATH)
    nf = X_pre.shape[1]
    reg = {"LinUCB": [], "LinTS": [], "StaticXGB": []}
    for seed in range(n_seeds):
        rng = np.random.default_rng(seed)
        df_post_raw = e9.create_shocked_df(df_raw, rng)
        X_post, df_post, _ = preprocess_cambodia_data(df=df_post_raw, stats=stats)
        algos = {
            "LinUCB": LinUCB(4, nf, alpha=BANDIT.linucb_alpha),
            "LinTS": LinTS(4, nf, v2=BANDIT.lints_v2, seed=seed),
            "StaticXGB": StaticXGBBaseline(),
        }
        for name, b in algos.items():
            r = e9.run_bandit_drift(name, b, X_pre.copy(), df_pre, X_post.copy(), df_post,
                                    N, SHOCK, seed=seed)
            reg[name].append(np.asarray(r["regrets"], float))
        print(f"  seed {seed + 1}/{n_seeds}", flush=True)
    return {k: np.array(v) for k, v in reg.items()}      # each (n_seeds, N)


def fig(reg):
    apply_style()
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    kernel = np.ones(WINDOW) / WINDOW
    rounds = np.arange(WINDOW - 1, N)
    for key, col, lab in (("LinTS", "lints", "LinTS"), ("LinUCB", "linucb", "LinUCB"),
                          ("StaticXGB", "static", "Static XGB")):
        # smooth each seed FIRST, then mean + CI across the smoothed curves
        smoothed = np.array([np.convolve(reg[key][s], kernel, mode="valid")
                             for s in range(reg[key].shape[0])])
        mean_full, idx, lo, hi = band(smoothed)
        ax.plot(rounds, mean_full, color=PALETTE[col], label=lab, linewidth=1.5)
        ci_band(ax, rounds[idx], lo, hi, PALETTE[col])
    ax.axvline(SHOCK, ls="--", lw=1.1, color="#333333", label="Shock (round 1,500)")
    ax.set_xlabel("Round")
    ax.set_ylabel(f"Regret per round (\\$, rolling {WINDOW}-round mean)")
    ax.set_xlim(0, N)
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper right")
    fig.tight_layout()
    save(fig, "fig_009_drift_adaptation")


def main():
    print(f"Re-running EXP-009 ({EXPERIMENT.n_seeds} seeds) for the drift trajectory ...")
    reg = collect(EXPERIMENT.n_seeds)

    print("\n=== REPRODUCTION CROSS-CHECK vs frozen Table 19 (post-shock regret/round) ===")
    frozen = {"LinUCB": 2.48, "LinTS": 2.42, "StaticXGB": 7.44}
    for name in ("LinUCB", "LinTS", "StaticXGB"):
        pre = reg[name][:, :SHOCK].mean()
        post = reg[name][:, SHOCK:].mean()
        print(f"  {name:10s} pre {pre:5.2f}  post {post:5.2f}   (frozen post: {frozen[name]})")

    fig(reg)
    print("\nwrote fig_009_drift_adaptation (.pdf + .png)")


if __name__ == "__main__":
    main()
