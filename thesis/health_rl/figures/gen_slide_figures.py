"""Slide-scale variants of the six defense-deck charts.

Reuses the data harnesses of the existing publication generators (gen_fig07/13/14/15/17,
gen_results_curves) so every curve reproduces the frozen thesis numbers, then re-plots
with _slide_style (sans >= 14 pt, thick lines, deck palette) into figures/slides/.

Data collection is expensive (full run ~45-75 min); each collector caches to
slides/_cache_*.npz|.json so re-rendering is instant.

Run:
    python thesis/health_rl/figures/gen_slide_figures.py            # all six
    python thesis/health_rl/figures/gen_slide_figures.py --figs ladder,reward
    python thesis/health_rl/figures/gen_slide_figures.py --no-cache # force re-run
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "healthrl" / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from healthrl.underwriting_bandit import (                      # noqa: E402
    LinUCB, StaticXGBBaseline, preprocess_cambodia_data, run_bandit,
)
from healthrl.config import EXPERIMENT, BANDIT                  # noqa: E402
from statistical_utils import bootstrap_ci                      # noqa: E402
from _slide_style import apply_slide_style, save_slide, SLIDE_PALETTE, SLIDE_DIR  # noqa: E402
import matplotlib.pyplot as plt                                 # noqa: E402
from matplotlib.patches import Patch                            # noqa: E402

import exp_010_cold_start_analysis as e10                       # noqa: E402
import exp_013_loglog_regret_validation as e13                  # noqa: E402
from experiment_utils import run_experiment_seeds               # noqa: E402
import gen_fig07_ladder                                         # noqa: E402
import gen_fig13_hitl                                           # noqa: E402
import gen_fig15_drift                                          # noqa: E402
import gen_fairness_exp006                                          # noqa: E402

N = EXPERIMENT.n_rounds
ROUNDS = np.arange(1, N + 1)
USE_CACHE = True


def _band(curves, n_sub=200):
    """Mean + bootstrap 95% CI at n_sub sampled rounds (same as gen_results_curves)."""
    mean_full = curves.mean(0)
    idx = np.unique(np.linspace(0, curves.shape[1] - 1, n_sub).astype(int))
    lo = np.empty(len(idx)); hi = np.empty(len(idx))
    for j, i in enumerate(idx):
        lo[j], hi[j] = bootstrap_ci(curves[:, i])
    return mean_full, idx, lo, hi


def _cached_npz(name, collect_fn):
    """Load slides/_cache_<name>.npz or run collect_fn() -> dict[str, ndarray] and save."""
    SLIDE_DIR.mkdir(exist_ok=True)
    path = SLIDE_DIR / f"_cache_{name}.npz"
    if USE_CACHE and path.exists():
        print(f"  [{name}] cache hit: {path.name}")
        with np.load(path) as z:
            return {k: z[k] for k in z.files}
    data = collect_fn()
    np.savez_compressed(path, **data)
    return data


# -- collectors (mirror the publication harnesses) --

def collect_reward():
    """EXP-005 harness half of gen_results_curves.collect(): LinUCB vs Static, 20 seeds."""
    X, df_raw, _ = preprocess_cambodia_data()
    nf = X.shape[1]
    ucb_R, stat_R = [], []
    for seed in range(EXPERIMENT.n_seeds):
        print(f"  [reward] seed {seed + 1}/{EXPERIMENT.n_seeds}", flush=True)
        r_ucb = run_bandit("LinUCB", LinUCB(4, nf, alpha=BANDIT.linucb_alpha),
                           X.copy(), df_raw, N, seed=seed)
        r_stat = run_bandit("StaticXGB", StaticXGBBaseline(),
                            X.copy(), df_raw, N, seed=seed)
        ucb_R.append(r_ucb.cumulative_rewards)
        stat_R.append(r_stat.cumulative_rewards)
    return {"ucb_R": np.array(ucb_R), "stat_R": np.array(stat_R)}


def collect_loglog():
    curves = []
    for s in range(e13.N_SEEDS):
        print(f"  [loglog] seed {s + 1}/{e13.N_SEEDS}", flush=True)
        curves.append(e13.run_single_seed(s))
    return {"curves": np.array(curves)}


def collect_hitl():
    hitl, base = gen_fig13_hitl.collect()
    out = {"base": np.asarray(base.cumulative_rewards, float)}
    for c in gen_fig13_hitl.CONS:
        out[f"c{int(c * 10):02d}"] = np.asarray(hitl[c].cumulative_rewards, float)
    return out


def collect_drift():
    reg = gen_fig15_drift.collect(EXPERIMENT.n_seeds)
    return {k: v for k, v in reg.items()}


def collect_psi():
    """Reuses gen_fairness_exp006's EXP-006 harness (sliding-window PSI vs the
    first-500-round reference window). Same 20-seed data as fig_psi_timeseries."""
    d = gen_fairness_exp006.collect(EXPERIMENT.n_seeds)
    return {"centers": d["centers"], "reg_psis": d["reg_psis"], "occ_psis": d["occ_psis"]}


def coldstart_stats():
    """EXP-010 stats; cached as JSON (dict of (mean, std) tuples)."""
    path = SLIDE_DIR / "_cache_coldstart.json"
    if USE_CACHE and path.exists():
        print("  [coldstart] cache hit")
        return {k: tuple(v) for k, v in json.loads(path.read_text()).items()}
    stats = run_experiment_seeds(e10.run, n_seeds=10)
    path.write_text(json.dumps({k: list(v) for k, v in stats.items()}))
    return stats


# -- figures --

def fig_reward():
    d = _cached_npz("reward", collect_reward)
    apply_slide_style()
    fig, ax = plt.subplots(figsize=(12.2, 5.0))
    for key, col, lab in (("ucb_R", "hero", "LinUCB"), ("stat_R", "compare", "Static XGB")):
        m, idx, lo, hi = _band(d[key])
        ax.plot(ROUNDS, m, color=SLIDE_PALETTE[col], label=lab)
        ax.fill_between(ROUNDS[idx], lo, hi, color=SLIDE_PALETTE[col], alpha=0.18, lw=0)
    ax.set_xlabel("Round"); ax.set_ylabel("Cumulative reward ($)")
    ax.set_xlim(0, N); ax.legend(loc="upper left")
    save_slide(fig, "slide_reward_curves")
    print(f"  [reward] final LinUCB {d['ucb_R'][:, -1].mean():,.0f} (frozen 90,540) | "
          f"Static {d['stat_R'][:, -1].mean():,.0f} (frozen 72,292)")


def fig_loglog():
    d = _cached_npz("loglog", collect_loglog)
    curves = d["curves"]
    mean_curve = curves.mean(0)
    fit = e13.fit_loglog_slope(mean_curve, t_min=200)   # reproduces frozen 0.572 / 0.992
    apply_slide_style()
    t = np.arange(1, e13.N_ROUNDS + 1)
    fig, ax = plt.subplots(figsize=(6.8, 5.2))
    ax.loglog(t, np.clip(mean_curve, 1e-6, None), color=SLIDE_PALETTE["hero"],
              label="Mean regret (20 seeds)")
    tf = t[200:]
    ax.loglog(tf, np.exp(fit["intercept"]) * tf ** fit["slope"],
              color=SLIDE_PALETTE["dark"], ls="--", lw=2.5,
              label=f"Fit: slope {fit['slope']:.3f}")
    mid = len(tf) // 2
    ref_int = np.log(mean_curve[200:][mid]) - 0.5 * np.log(tf[mid])
    ax.loglog(tf, np.exp(ref_int) * tf ** 0.5, color=SLIDE_PALETTE["compare"],
              ls=":", lw=2.5, label="O(sqrt T) reference")
    ax.set_xlabel("Round t"); ax.set_ylabel("Cumulative regret ($)")
    ax.set_xlim(10, e13.N_ROUNDS); ax.set_ylim(10, None)
    ax.legend(loc="upper left")
    save_slide(fig, "slide_loglog_regret")
    print(f"  [loglog] slope {fit['slope']:.3f} R2 {fit['r_squared']:.3f} (frozen 0.572/0.992)")


def fig_coldstart():
    stats = coldstart_stats()
    apply_slide_style()
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    ax.axvspan(1000, 2000, color=SLIDE_PALETTE["hero"], alpha=0.05, zorder=0)
    spec = [("LinUCB", "hero", "o"), ("LinTS", "lints", "s"), ("FreshXGB", "compare", "^")]
    for name, col, mk in spec:
        means = np.array([stats[f"cum_reward_{name}_t{t}"][0] for t in e10.TS])
        stds = np.array([stats[f"cum_reward_{name}_t{t}"][1] for t in e10.TS])
        lab = "Fresh XGB" if name == "FreshXGB" else name
        ax.errorbar(e10.TS, means, yerr=stds, color=SLIDE_PALETTE[col], marker=mk,
                    markersize=11, capsize=5, elinewidth=1.6, label=lab)
    ax.annotate("bandits overtake", xy=(2000, stats["cum_reward_LinTS_t2000"][0]),
                xytext=(1150, stats["cum_reward_FreshXGB_t2000"][0] + 7000),
                fontsize=14, color="#444444",
                arrowprops=dict(arrowstyle="->", color="#444444", lw=1.6))
    ax.set_xlabel("Horizon T (rounds)"); ax.set_ylabel("Cumulative reward ($)")
    ax.set_xticks(e10.TS); ax.set_xlim(e10.TS[0] - 90, e10.TS[-1] + 140)
    ax.legend(loc="upper left")
    save_slide(fig, "slide_cold_start")
    for name, _, _ in spec:
        print(f"  [coldstart] {name} T=2000: {stats[f'cum_reward_{name}_t2000'][0]:,.0f}")


def fig_hitl():
    d = _cached_npz("hitl", collect_hitl)
    apply_slide_style()
    fig, ax = plt.subplots(figsize=(7.4, 5.0))
    ax.plot(d["base"], color=SLIDE_PALETTE["compare"], ls="--", label="Vanilla bandit")
    for c, col in ((0.3, "hero3"), (0.5, "hero2"), (0.7, "hero")):
        ax.plot(d[f"c{int(c * 10):02d}"], color=SLIDE_PALETTE[col], label=f"HITL c = {c}")
    ax.set_xlabel("Round"); ax.set_ylabel("Cumulative reward ($)")
    ax.set_xlim(0, len(d["base"])); ax.legend(loc="upper left")
    save_slide(fig, "slide_hitl")
    print(f"  [hitl] c=0.7 final {d['c07'][-1]:,.0f} (frozen seed-42 trace 102,100)")


def fig_drift():
    d = _cached_npz("drift", collect_drift)
    apply_slide_style()
    fig, ax = plt.subplots(figsize=(7.4, 5.0))
    kernel = np.ones(gen_fig15_drift.WINDOW) / gen_fig15_drift.WINDOW
    rounds = np.arange(gen_fig15_drift.WINDOW - 1, gen_fig15_drift.N)
    for key, col, lab in (("LinTS", "lints", "LinTS"), ("LinUCB", "hero", "LinUCB"),
                          ("StaticXGB", "compare", "Static XGB")):
        smoothed = np.array([np.convolve(d[key][s], kernel, mode="valid")
                             for s in range(d[key].shape[0])])
        m, idx, lo, hi = _band(smoothed)
        ax.plot(rounds, m, color=SLIDE_PALETTE[col], label=lab)
        ax.fill_between(rounds[idx], lo, hi, color=SLIDE_PALETTE[col], alpha=0.15, lw=0)
    ax.axvline(gen_fig15_drift.SHOCK, ls="--", lw=2.0, color=SLIDE_PALETTE["dark"],
               label="Shock (round 1,500)")
    ax.set_xlabel("Round"); ax.set_ylabel("Regret per round ($)")
    ax.set_xlim(0, gen_fig15_drift.N); ax.set_ylim(bottom=0)
    ax.legend(loc="upper right")
    save_slide(fig, "slide_drift")


def fig_psi():
    d = _cached_npz("psi", collect_psi)
    apply_slide_style()
    fig, ax = plt.subplots(figsize=(9.6, 2.5))
    x = d["centers"]; top = 0.28
    ax.axhspan(0, 0.10, color=SLIDE_PALETTE["green"], alpha=0.12, zorder=0)
    ax.axhspan(0.10, 0.25, color=SLIDE_PALETTE["amber"], alpha=0.14, zorder=0)
    ax.axhspan(0.25, top, color=SLIDE_PALETTE["red"], alpha=0.14, zorder=0)
    ax.axhline(0.10, color=SLIDE_PALETTE["amber"], ls="--", lw=1.2, alpha=0.7)
    ax.axhline(0.25, color=SLIDE_PALETTE["red"], ls="--", lw=1.2, alpha=0.7)
    for key, col, lab in (("reg_psis", "hero", "Region"), ("occ_psis", "amber", "Occupation")):
        p = d[key]
        m = p.mean(0)
        lo = np.array([bootstrap_ci(p[:, j])[0] for j in range(p.shape[1])])
        hi = np.array([bootstrap_ci(p[:, j])[1] for j in range(p.shape[1])])
        ax.plot(x, m, color=SLIDE_PALETTE[col], marker="o", markersize=7,
                linewidth=3.0, label=lab)
        ax.fill_between(x, lo, hi, color=SLIDE_PALETTE[col], alpha=0.18, lw=0)
    for yb, txt, col in ((0.05, "GREEN < 0.10", "green"), (0.175, "AMBER 0.10–0.25", "amber"),
                         (0.265, "RED > 0.25", "red")):
        ax.text(N, yb, txt, ha="right", va="center", fontsize=12,
                 color=SLIDE_PALETTE[col], fontweight="bold")
    ax.set_xlabel("Round (sliding-window centre)")
    ax.set_ylabel("PSI vs first-500-\nround snapshot", fontsize=15)
    ax.set_xlim(0, N); ax.set_ylim(0, top)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=2, frameon=False)
    save_slide(fig, "slide_psi")
    print(f"  [psi] Region max {d['reg_psis'].max(axis=1).mean():.4f} GREEN | "
          f"Occupation max {d['occ_psis'].max(axis=1).mean():.4f} AMBER "
          f"(frozen 0.0821/0.1225)")


def fig_ladder():
    d = gen_fig07_ladder.load()                      # cheap CSV read; no cache needed
    apply_slide_style()
    color_map = {"LinTS": "hero", "LinUCB": "hero2", "AlwaysRATED": "red",
                 "LogisticPolicy": "dark", "Oracle": "dark"}
    rows = []
    for pol, (name, _, deploy) in gen_fig07_ladder.SPEC.items():
        v = np.array(d[pol])
        lo, hi = bootstrap_ci(v)
        rows.append((name, color_map.get(pol, "compare"), deploy, v.mean(), lo, hi))
    rows.sort(key=lambda r: r[3])
    names = [r[0] for r in rows]
    means = np.array([r[3] for r in rows])
    lo_err = means - np.array([r[4] for r in rows])
    hi_err = np.array([r[5] for r in rows]) - means
    fig, ax = plt.subplots(figsize=(7.4, 5.4))
    y = np.arange(len(names))
    for i, r in enumerate(rows):
        dep = r[2]
        ax.barh(y[i], means[i], color=SLIDE_PALETTE[r[1]], alpha=0.95 if dep else 0.45,
                hatch=None if dep else "///",
                edgecolor="white" if dep else SLIDE_PALETTE[r[1]], linewidth=1.0,
                xerr=[[lo_err[i]], [hi_err[i]]],
                error_kw={"ecolor": "#333333", "elinewidth": 1.4, "capsize": 4})
        ax.text(max(means[i], 0) + hi_err[i] + max(means) * 0.015, y[i],
                f"${means[i]:,.0f}", va="center", ha="left", fontsize=13)
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=14)
    for lbl in ax.get_yticklabels():
        if lbl.get_text() in ("LinUCB", "LinTS"):
            lbl.set_fontweight("bold")
    ax.set_xlabel("Cumulative reward ($), mean +/- 95% CI")
    ax.set_xlim(min(0, means.min() * 1.15), max(means + hi_err) * 1.24)
    legend = [Patch(facecolor="#777777", alpha=0.95, label="Deployable"),
              Patch(facecolor="#777777", alpha=0.45, hatch="///", edgecolor="#777777",
                    label="Not deployable / ceiling")]
    ax.legend(handles=legend, loc="lower right", fontsize=13)
    save_slide(fig, "slide_ladder")


FIGS = {"reward": fig_reward, "loglog": fig_loglog, "coldstart": fig_coldstart,
        "hitl": fig_hitl, "drift": fig_drift, "ladder": fig_ladder, "psi": fig_psi}


def main():
    global USE_CACHE
    ap = argparse.ArgumentParser()
    ap.add_argument("--figs", default=",".join(FIGS),
                    help="comma list of: " + ",".join(FIGS))
    ap.add_argument("--no-cache", action="store_true")
    args = ap.parse_args()
    USE_CACHE = not args.no_cache
    for name in args.figs.split(","):
        print(f"== {name} ==", flush=True)
        FIGS[name.strip()]()
    done = sorted(p.name for p in SLIDE_DIR.glob("slide_*.png"))
    print(f"\nwrote {len(done)} slide figures: {', '.join(done)}")


if __name__ == "__main__":
    main()
