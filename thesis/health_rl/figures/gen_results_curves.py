"""Figures 8, 9, 12 -- result trajectory curves, re-rendered in the publication style.

Mirrors the canonical harnesses EXACTLY so the curves reproduce the frozen numbers:
  * Fig 8 (reward curves)   + Fig 9 (action evolution) -> EXP-005 harness (no CRN), LinUCB vs Static.
  * Fig 12 (regret curves)  -> EXP-007 harness (common random numbers), 4 algorithms.
Seeds are range(20) = 0..19 (matching experiment_utils.run_experiment_seeds_raw).

Prints reproduction cross-checks against the frozen text before saving anything.
"""
from __future__ import annotations

import sys
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "healthrl" / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from healthrl.underwriting_bandit import (   # noqa: E402
    LinUCB, LinTS, EpsilonGreedy, StaticXGBBaseline, RewardConfig,
    preprocess_cambodia_data, run_bandit, ACTION_NAMES,
)
from healthrl.config import EXPERIMENT, BANDIT   # noqa: E402
from statistical_utils import bootstrap_ci        # noqa: E402
from _style import apply_style, save, PALETTE, ci_band   # noqa: E402
import matplotlib.pyplot as plt                    # noqa: E402

N = EXPERIMENT.n_rounds
SEEDS = range(EXPERIMENT.n_seeds)          # 0..19
ROUNDS = np.arange(1, N + 1)


# ── simulation (mirrors the canonical harnesses) ─────────────────────────────

def collect():
    X, df_raw, _ = preprocess_cambodia_data()
    nf = X.shape[1]

    ucb_R, stat_R, ucb_A = [], [], []                       # EXP-005 style
    regrets = {"LinUCB": [], "LinTS": [], "EpsilonGreedy": [], "StaticXGB": []}  # EXP-007 style

    for seed in SEEDS:
        print(f"  seed {seed + 1}/{EXPERIMENT.n_seeds} ...", flush=True)

        # --- EXP-005 harness (no common random numbers) ---
        r_ucb = run_bandit("LinUCB", LinUCB(4, nf, alpha=BANDIT.linucb_alpha),
                           X.copy(), df_raw, N, seed=seed)
        r_stat = run_bandit("StaticXGB", StaticXGBBaseline(),
                            X.copy(), df_raw, N, seed=seed)
        ucb_R.append(r_ucb.cumulative_rewards)
        stat_R.append(r_stat.cumulative_rewards)
        ucb_A.append(r_ucb.actions)

        # --- EXP-007 harness (common random numbers shared across algos) ---
        rng = np.random.default_rng(seed)
        cfg = RewardConfig()
        acc = rng.random(N)
        noise = rng.uniform(cfg.claims_noise_low, cfg.claims_noise_high, size=N)
        algos = {
            "LinUCB": LinUCB(4, nf, alpha=BANDIT.linucb_alpha),
            "LinTS": LinTS(4, nf, v2=BANDIT.lints_v2, seed=seed),
            "EpsilonGreedy": EpsilonGreedy(4, nf, epsilon=BANDIT.epsilon, seed=seed),
            "StaticXGB": StaticXGBBaseline(),
        }
        for name, bandit in algos.items():
            r = run_bandit(name, bandit, X.copy(), df_raw, N, seed=seed,
                           acceptance_draws=acc, claims_noise=noise)
            regrets[name].append(r.cumulative_regrets)

    return {
        "ucb_R": np.array(ucb_R), "stat_R": np.array(stat_R), "ucb_A": np.array(ucb_A),
        "regret": {k: np.array(v) for k, v in regrets.items()},
    }


# ── helpers ──────────────────────────────────────────────────────────────────

def band(curves, n_sub=200):
    """Full-res mean + bootstrap 95% CI at n_sub sampled rounds."""
    mean_full = curves.mean(0)
    idx = np.unique(np.linspace(0, curves.shape[1] - 1, n_sub).astype(int))
    lo = np.empty(len(idx)); hi = np.empty(len(idx))
    for j, i in enumerate(idx):
        lo[j], hi[j] = bootstrap_ci(curves[:, i])
    return mean_full, idx, lo, hi


# ── figures ──────────────────────────────────────────────────────────────────

def fig_reward(d):
    apply_style()
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    for key, col, lab in (("ucb_R", "linucb", "LinUCB"), ("stat_R", "static", "Static XGB")):
        m, idx, lo, hi = band(d[key])
        ax.plot(ROUNDS, m, color=PALETTE[col], label=lab)
        ci_band(ax, ROUNDS[idx], lo, hi, PALETTE[col])
    ax.set_xlabel("Round"); ax.set_ylabel("Cumulative reward (\\$)")
    ax.set_xlim(0, N); ax.legend(loc="upper left")
    fig.tight_layout(); save(fig, "fig_reward_curves")


def fig_regret(d):
    apply_style()
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    order = [("LinTS", "lints"), ("LinUCB", "linucb"),
             ("EpsilonGreedy", "epsilon"), ("StaticXGB", "static")]
    for name, col in order:
        m, idx, lo, hi = band(d["regret"][name])
        lab = "Static XGB" if name == "StaticXGB" else (r"$\varepsilon$-Greedy" if name == "EpsilonGreedy" else name)
        ax.plot(ROUNDS, m, color=PALETTE[col], label=lab)
        ci_band(ax, ROUNDS[idx], lo, hi, PALETTE[col])
    ax.set_xlabel("Round"); ax.set_ylabel("Cumulative regret (\\$)")
    ax.set_xlim(0, N); ax.legend(loc="upper left")
    fig.tight_layout(); save(fig, "fig_regret_curves")


def fig_action(d):
    apply_style()
    acts = d["ucb_A"]                       # (n_seeds, N)
    n_bins = 50; bs = N // n_bins
    centers = (np.arange(n_bins) + 0.5) * bs
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    act_cols = ["static", "linucb", "epsilon", "lints"]   # 4 distinct palette keys
    for k in range(4):
        prop = np.array([(acts[:, b * bs:(b + 1) * bs] == k).mean() for b in range(n_bins)])
        ax.plot(centers, prop, color=PALETTE[act_cols[k]], label=ACTION_NAMES[k], marker="", linewidth=1.6)
    # entropy annotation (20-seed early/late, frozen 1.31 -> 1.10)
    def ent(a):
        p = np.bincount(a, minlength=4) / len(a)
        return -np.sum(p * np.log(p + 1e-12))
    e_early = np.mean([ent(a[:500]) for a in acts])
    e_late = np.mean([ent(a[-500:]) for a in acts])
    ax.annotate(f"Action entropy: {e_early:.2f} (early) $\\rightarrow$ {e_late:.2f} (late)",
                xy=(0.5, 0.94), xycoords="axes fraction", ha="center", fontsize=9, color="#444444")
    ax.set_xlabel("Round"); ax.set_ylabel("Action proportion (250-round bins)")
    ax.set_xlim(0, N); ax.set_ylim(0, 1); ax.legend(loc="center right", ncol=1)
    fig.tight_layout(); save(fig, "fig_action_evolution")
    return e_early, e_late


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    print("Running EXP-005 + EXP-007 harnesses (20 seeds each)...")
    d = collect()

    ucb = d["ucb_R"][:, -1]; stat = d["stat_R"][:, -1]
    print("\n=== REPRODUCTION CROSS-CHECK vs frozen text ===")
    print(f"  Fig 8  LinUCB final reward  {ucb.mean():11,.0f}   (frozen Table 10: 90,540)")
    print(f"  Fig 8  Static final reward  {stat.mean():11,.0f}   (frozen Table 10: 72,292)")
    print("  Fig 12 final cumulative regret (frozen ch6: LinTS 21,149 | LinUCB 22,774 | eG 38,281 | Static 42,548):")
    for name in ("LinTS", "LinUCB", "EpsilonGreedy", "StaticXGB"):
        print(f"         {name:14s} {d['regret'][name][:, -1].mean():11,.0f}")

    fig_reward(d)
    fig_regret(d)
    e_early, e_late = fig_action(d)
    print(f"  Fig 9  entropy early->late  {e_early:.3f} -> {e_late:.3f}   (frozen 1.314 -> 1.105)")

    rec = {
        "ucb_final_reward": float(ucb.mean()), "static_final_reward": float(stat.mean()),
        "regret_final": {k: float(d["regret"][k][:, -1].mean()) for k in d["regret"]},
        "entropy_early": float(e_early), "entropy_late": float(e_late),
    }
    out = Path(__file__).resolve().parent / "_results_curves_repro.json"
    out.write_text(json.dumps(rec, indent=2))
    print(f"\nwrote fig_reward_curves / fig_regret_curves / fig_action_evolution (.pdf+.png) + {out.name}")


if __name__ == "__main__":
    main()
