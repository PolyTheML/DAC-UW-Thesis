"""Figure 13 -- EXP-008 HITL four-panel diagnostic, re-rendered in the publication style.

Reuses exp_008's run_hitl_bandit + run_refer_baseline at the experiment's own SEED (42).
Four panels: (a) cumulative reward, (b) cumulative regret, (c) human-review queue depth,
(d) rolling policy alignment. Per-panel titles + suptitle stripped (spec); (a)-(d) tags +
the LaTeX caption identify the panels. Prints the Table 13 cross-check (HITL c=0.7 reward
102,100; c=0.3/0.5 101,646; baseline math-REFER 95,872). exp_008 is unmodified, so the
re-run reproduces the frozen numbers.
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

from healthrl.underwriting_bandit import LinUCB, preprocess_cambodia_data   # noqa: E402
from healthrl.config import BANDIT                                          # noqa: E402
import exp_008_human_in_the_loop as e8                                      # noqa: E402
from _style import apply_style, save, PALETTE                               # noqa: E402
import matplotlib.pyplot as plt                                             # noqa: E402

CONS = [0.3, 0.5, 0.7]
CONS_COL = {0.3: "epsilon", 0.5: "linucb", 0.7: "lints"}


def collect():
    X, df, _ = preprocess_cambodia_data()
    nf = X.shape[1]
    hitl = {}
    for c in CONS:
        b = LinUCB(4, nf, alpha=BANDIT.linucb_alpha)
        hitl[c] = e8.run_hitl_bandit(b, X, df, n_rounds=e8.N_ROUNDS, conservatism=c, seed=e8.SEED)
    base_b = LinUCB(4, nf, alpha=BANDIT.linucb_alpha)
    base = e8.run_refer_baseline("linucb", base_b, X, df, n_rounds=e8.N_ROUNDS, seed=e8.SEED)
    return hitl, base


def _tag(ax, t):
    ax.text(0.02, 0.97, t, transform=ax.transAxes, fontweight="bold", va="top", ha="left", fontsize=10)


def fig(hitl, base):
    apply_style()
    fig, axes = plt.subplots(2, 2, figsize=(7.4, 5.6))

    ax = axes[0, 0]
    ax.plot(base.cumulative_rewards, color=PALETTE["random"], ls="--", label="Baseline (math REFER)")
    for c in CONS:
        ax.plot(hitl[c].cumulative_rewards, color=PALETTE[CONS_COL[c]], label=f"HITL $c$={c}")
    ax.set_xlabel("Round"); ax.set_ylabel("Cumulative reward (\\$)")
    ax.set_xlim(0, e8.N_ROUNDS); ax.legend(loc="lower right", fontsize=7.0); _tag(ax, "(a)")

    ax = axes[0, 1]
    ax.plot(base.cumulative_regrets, color=PALETTE["random"], ls="--", label="Baseline (math REFER)")
    for c in CONS:
        ax.plot(hitl[c].cumulative_regrets, color=PALETTE[CONS_COL[c]], label=f"HITL $c$={c}")
    ax.set_xlabel("Round"); ax.set_ylabel("Cumulative regret (\\$)")
    ax.set_xlim(0, e8.N_ROUNDS); ax.legend(loc="lower right", fontsize=7.0); _tag(ax, "(b)")

    ax = axes[1, 0]
    for c in CONS:
        ax.plot(hitl[c].queue_depths, color=PALETTE[CONS_COL[c]], label=f"HITL $c$={c}", alpha=0.85)
    ax.set_xlabel("Round"); ax.set_ylabel("Pending reviews (queue depth)")
    ax.set_xlim(0, e8.N_ROUNDS)
    ymax = max((max(hitl[c].queue_depths) if hitl[c].queue_depths else 0) for c in CONS)
    ax.set_ylim(-0.5, max(ymax, 1) + 0.5)
    if ymax == 0:
        ax.text(0.5, 0.5, "queue depth stays at 0\n(zero review latency)", transform=ax.transAxes,
                ha="center", va="center", fontsize=8.5, color="#666666", style="italic")
    _tag(ax, "(c)")

    ax = axes[1, 1]
    for c in CONS:
        aw = hitl[c].alignment_window
        if len(aw) > 0:
            w = min(50, len(aw) // 4 + 1)
            sm = pd.Series(aw).rolling(window=w, min_periods=1).mean()
            ax.plot(sm.to_numpy(), color=PALETTE[CONS_COL[c]], label=f"HITL $c$={c}")
    ax.set_xlabel("Override number"); ax.set_ylabel("Policy alignment (rolling mean)")
    ax.set_ylim(0, 1); ax.legend(loc="lower left", fontsize=7.0); _tag(ax, "(d)")

    fig.tight_layout()
    save(fig, "fig_hitl_experiment")


def main():
    hitl, base = collect()
    print("\n=== REPRODUCTION CROSS-CHECK vs frozen Table 13 ===")
    frozen_reward = {0.3: 101646, 0.5: 101646, 0.7: 102100}
    frozen_regret = {0.3: 13009, 0.5: 13009, 0.7: 12555}
    frozen_cost = {0.3: 2555, 0.5: 2555, 0.7: 2625}
    for c in CONS:
        r = hitl[c]
        print(f"  HITL c={c}: reward {r.cumulative_rewards[-1]:11,.0f} (frozen {frozen_reward[c]:,})"
              f"  regret {r.cumulative_regrets[-1]:9,.0f} (frozen {frozen_regret[c]:,})"
              f"  cost {r.total_human_cost:7,.0f} (frozen {frozen_cost[c]:,})")
    print(f"  Baseline:   reward {base.cumulative_rewards[-1]:11,.0f} (frozen 95,872)"
          f"  regret {base.cumulative_regrets[-1]:9,.0f} (frozen 19,289)")
    fig(hitl, base)
    print("\nwrote fig_hitl_experiment (.pdf + .png)")


if __name__ == "__main__":
    main()
