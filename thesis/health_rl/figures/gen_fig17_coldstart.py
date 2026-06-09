"""Figure 17 -- EXP-010 cold-start analysis, re-rendered in the publication style.

Plots the **10-seed mean ± std** cumulative reward at horizons T in {200, 500, 1000, 2000}
for LinUCB, LinTS, and FreshXGB -- reproducing Table 21 exactly and matching the chapter05
caption ("mean of 10 seeds"). NOTE: the prior plot_cold_start rendered a single seed (42);
this corrects it to the 10-seed mean the caption claims. exp_010's only uncommitted change
is a cosmetic print-string fix, so the numbers reproduce. Title stripped.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "healthrl" / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import exp_010_cold_start_analysis as e10            # noqa: E402
from experiment_utils import run_experiment_seeds    # noqa: E402
from _style import apply_style, save, PALETTE         # noqa: E402
import matplotlib.pyplot as plt                       # noqa: E402

TS = e10.TS
SPEC = [("LinUCB", "linucb", "o"), ("LinTS", "lints", "s"), ("FreshXGB", "static", "^")]
# frozen Table 21 means for the cross-check
FROZEN = {
    "LinUCB":   {200: 1313, 500: 5593, 1000: 13033, 2000: 31227},
    "LinTS":    {200: 1206, 500: 5570, 1000: 13496, 2000: 31401},
    "FreshXGB": {200: 2812, 500: 7048, 1000: 13692, 2000: 29267},
}


def fig(stats):
    apply_style()
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    # shade the operational crossover band (bandits overtake FreshXGB between 1,000 and 2,000)
    ax.axvspan(1000, 2000, color=PALETTE["linucb"], alpha=0.06, zorder=0)
    for name, col, mk in SPEC:
        means = np.array([stats[f"cum_reward_{name}_t{t}"][0] for t in TS])
        stds = np.array([stats[f"cum_reward_{name}_t{t}"][1] for t in TS])
        lab = "Fresh XGB" if name == "FreshXGB" else name
        ax.errorbar(TS, means, yerr=stds, color=PALETTE[col], marker=mk, markersize=6,
                    linewidth=1.6, capsize=3, elinewidth=0.8, label=lab)
    ax.annotate("bandits overtake\nFresh XGB", xy=(2000, stats["cum_reward_LinTS_t2000"][0]),
                xytext=(1180, stats["cum_reward_FreshXGB_t2000"][0] + 6500),
                fontsize=8.5, color="#444444",
                arrowprops=dict(arrowstyle="->", color="#444444", lw=0.8))
    ax.set_xlabel("Horizon $T$ (rounds)")
    ax.set_ylabel("Cumulative reward (\\$), mean ± std (10 seeds)")
    ax.set_xticks(TS)
    ax.set_xlim(TS[0] - 80, TS[-1] + 120)
    ax.legend(loc="upper left")
    fig.tight_layout()
    save(fig, "fig_010_cold_start")


def main():
    print("Re-running EXP-010 cold-start (10 seeds, repeated XGB refits) ...")
    stats = run_experiment_seeds(e10.run, n_seeds=10)
    print("\n=== REPRODUCTION CROSS-CHECK vs frozen Table 21 (mean cumulative reward) ===")
    for name, _, _ in SPEC:
        for t in TS:
            m = stats[f"cum_reward_{name}_t{t}"][0]
            print(f"  {name:9s} T={t:<5d} {m:9,.0f}   (frozen {FROZEN[name][t]:,})")
    fig(stats)
    print("\nwrote fig_010_cold_start (.pdf + .png)")


if __name__ == "__main__":
    main()
