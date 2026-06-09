"""Figure F6 -- decision regions: oracle vs learned LinUCB on the reward-driver plane.

The actuarial reward (expected_rewards) is an EXACT function of just two raw
variables: mortality_multiplier (mort) and monthly_income_usd (income). mort is the
latent reward driver -- it is NOT one of the bandit's 34 context features (the bandit
must infer it from age / BMI / conditions / ...). Therefore:
  * the ORACLE optimal-action map is exact over a (mort, income) grid;
  * the LEARNED LinUCB policy is shown by evaluating the trained bandit's GREEDY
    action (argmax_a theta_a . x, theta_a = A_inv[a] b[a]; no UCB bonus) on the 2,000
    REAL applicants (full 34-dim context, seed 42), plotted at their (mort, income).

Panel (a): oracle regions (filled) + real applicants -- agreement faint, disagreement
bold -- so disagreements are seen to land in panel (b)'s low-margin zones.
Panel (b): decision margin = best - 2nd-best expected reward over the grid, with the
oracle boundaries and the disagreement points overlaid.

This is an EXPLANATORY figure (not evidentiary): it shows why a near-constant policy
is hard to beat and why modest oracle-action agreement still yields ~72% of oracle
reward. It prints its OWN agreement % (greedy theta over all applicants), a different
statistic from Sec. 5.1's 37.8% live-stream value; the caption says "consistent with".
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
    LinUCB, preprocess_cambodia_data, run_bandit, expected_rewards, ACTION_NAMES,
)
from healthrl.config import EXPERIMENT, BANDIT   # noqa: E402
from _style import apply_style, save             # noqa: E402
import matplotlib.pyplot as plt                   # noqa: E402
from matplotlib.colors import ListedColormap      # noqa: E402
from matplotlib.patches import Patch              # noqa: E402
from matplotlib.lines import Line2D               # noqa: E402

# 4 distinct Okabe-Ito colours: STANDARD, RATED, DECLINE, REFER
ACTION_COLORS = ["#009E73", "#0072B2", "#D55E00", "#E69F00"]
NGRID = 200
SEED = 42


def er(m, inc):
    """expected_rewards on a (mort, income) point -- dict is enough (no pd.Series)."""
    return expected_rewards({"mortality_multiplier": m, "monthly_income_usd": inc})


def main():
    X, df_raw, features = preprocess_cambodia_data()
    nf = X.shape[1]

    # --- train LinUCB (seed 42, full horizon) ---
    print(f"Training LinUCB (seed {SEED}, {EXPERIMENT.n_rounds} rounds) ...")
    bandit = LinUCB(4, nf, alpha=BANDIT.linucb_alpha)
    run_bandit("LinUCB", bandit, X.copy(), df_raw, EXPERIMENT.n_rounds, seed=SEED)
    theta = np.array([bandit.A_inv[a] @ bandit.b[a] for a in range(4)])   # (4, nf)
    print("  theta norms per action:", {ACTION_NAMES[a]: round(float(np.linalg.norm(theta[a])), 3) for a in range(4)})

    # --- learned greedy action vs oracle action on the real applicants ---
    learned = (X @ theta.T).argmax(1)                       # (n,)
    mort = df_raw["mortality_multiplier"].to_numpy(float)
    income = df_raw["monthly_income_usd"].to_numpy(float)
    oracle = np.array([int(er(mort[i], income[i]).argmax()) for i in range(len(df_raw))])
    agree = learned == oracle
    agree_pct = 100 * agree.mean()

    print("\n=== F6 own statistics (greedy theta over all 2,000 applicants) ===")
    print(f"  oracle-agreement: {agree_pct:.1f}%  (Sec. 5.1 live-stream figure: 37.8%)")
    for a in range(4):
        print(f"  oracle action share {ACTION_NAMES[a]:9s}: {100*(oracle==a).mean():5.1f}%"
              f"   | learned share: {100*(learned==a).mean():5.1f}%")

    # --- oracle map + decision margin over the (mort, income) grid ---
    mg = np.linspace(np.percentile(mort, 1), np.percentile(mort, 99), NGRID)
    ig = np.linspace(np.percentile(income, 1), np.percentile(income, 99), NGRID)
    oracle_grid = np.zeros((NGRID, NGRID), dtype=int)        # [iy=income, ix=mort]
    margin_grid = np.zeros((NGRID, NGRID))
    for ix, m in enumerate(mg):
        for iy, inc in enumerate(ig):
            r = er(m, inc)
            srt = np.sort(r)
            oracle_grid[iy, ix] = int(r.argmax())
            margin_grid[iy, ix] = srt[-1] - srt[-2]
    grid_share = {ACTION_NAMES[a]: 100 * (oracle_grid == a).mean() for a in range(4)}
    print("  oracle grid-area share:", {k: round(v, 1) for k, v in grid_share.items()})
    print(f"  mean decision margin -- overall: {margin_grid.mean():.1f}; "
          f"at disagreement applicants: {np.mean([margin_grid[np.abs(ig-income[i]).argmin(), np.abs(mg-mort[i]).argmin()] for i in np.where(~agree)[0]]):.1f}")

    extent = [mg[0], mg[-1], ig[0], ig[-1]]
    apply_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.0, 4.0))

    # (a) oracle regions + applicants
    cmap = ListedColormap(ACTION_COLORS)
    ax1.imshow(oracle_grid, origin="lower", extent=extent, aspect="auto",
               cmap=cmap, vmin=-0.5, vmax=3.5, alpha=0.55, interpolation="nearest")
    ax1.scatter(mort[agree], income[agree], s=4, c="#666666", alpha=0.18,
                edgecolors="none", zorder=2)
    ax1.scatter(mort[~agree], income[~agree], s=20, c="black", marker="x",
                linewidths=0.7, zorder=3)
    ax1.set_xlabel("Mortality multiplier (latent reward driver)")
    ax1.set_ylabel("Monthly income (USD)")
    ax1.set_xlim(extent[0], extent[1]); ax1.set_ylim(extent[2], extent[3])
    ax1.set_title("(a) Oracle regions vs LinUCB choices", fontsize=9)
    handles = [Patch(facecolor=ACTION_COLORS[a], alpha=0.6, label=ACTION_NAMES[a]) for a in range(4)]
    handles.append(Line2D([0], [0], marker="x", color="black", lw=0, markersize=6,
                          label=f"LinUCB ≠ oracle ({100-agree_pct:.0f}%)"))
    ax1.legend(handles=handles, loc="upper right", fontsize=6.6, framealpha=0.9)

    # (b) decision margin + oracle boundaries + disagreements
    im = ax2.imshow(margin_grid, origin="lower", extent=extent, aspect="auto",
                    cmap="cividis", interpolation="nearest")
    # The oracle action boundaries coincide with the low-margin (dark) ridges of this
    # map by construction (margin -> 0 where best and 2nd-best actions tie), so no
    # separate boundary overlay is needed (and contour/contourpy is unavailable here).
    ax2.scatter(mort[~agree], income[~agree], s=14, c="white", marker="x",
                linewidths=0.6, zorder=3)
    ax2.set_xlabel("Mortality multiplier (latent reward driver)")
    ax2.set_ylabel("Monthly income (USD)")
    ax2.set_xlim(extent[0], extent[1]); ax2.set_ylim(extent[2], extent[3])
    ax2.set_title("(b) Decision margin (best $-$ 2nd-best)", fontsize=9)
    cbar = fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)
    cbar.set_label("Expected-reward margin (\\$)", fontsize=8)

    fig.tight_layout()
    save(fig, "fig_decision_regions")
    print("\nwrote fig_decision_regions (.pdf + .png)")


if __name__ == "__main__":
    main()
