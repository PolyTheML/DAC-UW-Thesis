"""Figures 10, 11, and F4 -- EXP-006 fairness audit, from ONE 20-seed re-run.

Fig 10  fig_fairness_region.pdf      converged (rounds 3,000-4,999) regional approval
                                     rates, EEOC four-fifths (80%-of-max) overlay.
Fig 11  fig_fairness_occupation.pdf  same, by occupation.
F4      fig_psi_timeseries.pdf       sliding-window PSI(t) for region + occupation with
                                     GREEN/AMBER/RED guardrail bands.

Mirrors exp_006.run exactly (seeds 0..19, LinUCB, approved = STANDARD|RATED, converged
phase >= 3,000, PSI ref = window 0). Permutation tests are skipped (figures don't use
them). Reproduces Table 11 + the §5.2.1 PSI values. exp_006 is unmodified.
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
    LinUCB, run_bandit, preprocess_cambodia_data, ACTION_STANDARD, ACTION_RATED,
)
from healthrl.config import EXPERIMENT, BANDIT   # noqa: E402
import exp_006_fairness_audit as e6              # noqa: E402
from statistical_utils import bootstrap_ci        # noqa: E402
from _style import apply_style, save, PALETTE, PSI_BANDS, ci_band   # noqa: E402
import matplotlib.pyplot as plt                   # noqa: E402
from matplotlib.patches import Patch              # noqa: E402

N = e6.N_ROUNDS
WINDOW = e6.WINDOW
N_WINDOWS = e6.N_WINDOWS
CONV_START = 3000


def psi_series(dec, col, labels):
    ref = dec[(dec["round"] >= 0) & (dec["round"] < WINDOW)]
    ref_dist = np.array([ref[ref["approved"]][col].value_counts().get(l, 0) for l in labels])
    centers, psis = [], []
    for w in range(1, N_WINDOWS):
        s = w * WINDOW
        win = dec[(dec["round"] >= s) & (dec["round"] < s + WINDOW)]
        win_dist = np.array([win[win["approved"]][col].value_counts().get(l, 0) for l in labels])
        psis.append(e6.compute_psi(ref_dist, win_dist))
        centers.append(s + WINDOW / 2)
    return np.array(centers), np.array(psis)


def conv_rates(dec, col, labels):
    conv = dec[dec["round"] >= CONV_START]
    return np.array([(conv[conv[col] == l]["approved"].sum() / max(len(conv[conv[col] == l]), 1))
                     for l in labels])


def collect(n_seeds):
    X, df_raw, _ = preprocess_cambodia_data()
    nf = X.shape[1]; ns = len(df_raw)
    region_labels = sorted(df_raw["region"].unique())
    occ_labels = sorted(df_raw["occupation"].unique())
    region_arr = [df_raw.iloc[i % ns]["region"] for i in range(N)]
    occ_arr = [df_raw.iloc[i % ns]["occupation"] for i in range(N)]

    reg_rates, occ_rates, reg_psis, occ_psis = [], [], [], []
    centers = None
    for seed in range(n_seeds):
        b = LinUCB(4, nf, alpha=BANDIT.linucb_alpha)
        res = run_bandit("LinUCB", b, X.copy(), df_raw, N, seed=seed)
        dec = pd.DataFrame({"round": np.arange(N), "action": res.actions,
                            "region": region_arr, "occupation": occ_arr})
        dec["approved"] = dec["action"].isin([ACTION_STANDARD, ACTION_RATED])
        reg_rates.append(conv_rates(dec, "region", region_labels))
        occ_rates.append(conv_rates(dec, "occupation", occ_labels))
        c, rp = psi_series(dec, "region", region_labels); centers = c
        _, op = psi_series(dec, "occupation", occ_labels)
        reg_psis.append(rp); occ_psis.append(op)
        print(f"  seed {seed + 1}/{n_seeds}", flush=True)
    return {"region_labels": region_labels, "occ_labels": occ_labels,
            "reg_rates": np.array(reg_rates), "occ_rates": np.array(occ_rates),
            "centers": centers, "reg_psis": np.array(reg_psis), "occ_psis": np.array(occ_psis)}


def verify(d):
    print("\n=== REPRODUCTION CROSS-CHECK vs frozen Table 11 + §5.2.1 ===")
    for dim, key, fz in (("Region", "reg_rates", (0.6622, 0.7725, 85.72)),
                         ("Occupation", "occ_rates", (0.6803, 0.7549, 90.12))):
        a = d[key]
        mn, mx = a.min(axis=1).mean(), a.max(axis=1).mean()
        print(f"  {dim:10s} per-seed min {mn:.4f} max {mx:.4f} parity {100*mn/mx:5.2f}%"
              f"   (frozen {fz[0]}/{fz[1]}/{fz[2]}%)"
              f"   | per-group-mean parity {100*a.mean(0).min()/a.mean(0).max():5.2f}%")
    for dim, key, fz in (("Region", "reg_psis", (0.0821, 0.0424)),
                         ("Occupation", "occ_psis", (0.1225, 0.0710))):
        p = d[key]
        print(f"  {dim:10s} PSI per-seed-max {p.max(axis=1).mean():.4f} final {p[:, -1].mean():.4f}"
              f"   (frozen {fz[0]}/{fz[1]})   | mean-curve peak {p.mean(0).max():.4f}")


def fig_rates(d, dim_key, labels_key, stem, color):
    apply_style()
    a = d[dim_key]; labels = d[labels_key]
    means = a.mean(0)
    cis = np.array([bootstrap_ci(a[:, j]) for j in range(a.shape[1])])
    order = np.argsort(means)
    means, labels = means[order], [labels[i] for i in order]
    lo_err = means - cis[order, 0]; hi_err = cis[order, 1] - means
    thr = 0.8 * means.max()

    fig, ax = plt.subplots(figsize=(6.6, 0.55 * len(labels) + 1.6))
    y = np.arange(len(labels))
    ax.barh(y, means, color=color, alpha=0.90, edgecolor="white", linewidth=0.6,
            xerr=[lo_err, hi_err], error_kw={"ecolor": "#333333", "elinewidth": 0.8, "capsize": 2.5})
    ax.axvline(thr, ls="--", lw=1.1, color="#D55E00",
               label=f"EEOC four-fifths threshold (80% of max = {thr:.2f})")
    for i, m in enumerate(means):
        ax.text(m + hi_err[i] + 0.006, y[i], f"{m:.2f}", va="center", ha="left", fontsize=8.0)
    ax.set_yticks(y); ax.set_yticklabels(labels)
    ax.set_xlabel("Converged-phase approval rate (rounds 3,000–4,999)")
    ax.set_xlim(0, min(1.0, means.max() + max(hi_err) + 0.10))
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout(); save(fig, stem)


def fig_psi(d):
    apply_style()
    fig, ax = plt.subplots(figsize=(6.6, 4.1))
    x = d["centers"]
    top = 0.28
    ax.axhspan(0, 0.10, color=PSI_BANDS["green"], alpha=0.55, zorder=0)
    ax.axhspan(0.10, 0.25, color=PSI_BANDS["amber"], alpha=0.55, zorder=0)
    ax.axhspan(0.25, top, color=PSI_BANDS["red"], alpha=0.55, zorder=0)
    for key, col, lab in (("reg_psis", "lints", "Region"), ("occ_psis", "epsilon", "Occupation")):
        p = d[key]
        m = p.mean(0)
        lo = np.array([bootstrap_ci(p[:, j])[0] for j in range(p.shape[1])])
        hi = np.array([bootstrap_ci(p[:, j])[1] for j in range(p.shape[1])])
        ax.plot(x, m, color=PALETTE[col], marker="o", markersize=4, linewidth=1.5, label=lab)
        ci_band(ax, x, lo, hi, PALETTE[col])
    for yb, txt in ((0.06, "GREEN < 0.10"), (0.175, "AMBER 0.10–0.25"), (0.265, "RED > 0.25")):
        ax.text(x[-1], yb, txt, ha="right", va="center", fontsize=7.5, color="#555555")
    ax.set_xlabel("Round (sliding-window centre)")
    ax.set_ylabel("Sliding-window PSI vs reference window")
    ax.set_xlim(0, N); ax.set_ylim(0, top)
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout(); save(fig, "fig_psi_timeseries")


def main():
    print(f"Re-running EXP-006 ({EXPERIMENT.n_seeds} seeds, LinUCB) ...")
    d = collect(EXPERIMENT.n_seeds)
    verify(d)
    fig_rates(d, "reg_rates", "region_labels", "fig_fairness_region", PALETTE["linucb"])
    fig_rates(d, "occ_rates", "occ_labels", "fig_fairness_occupation", PALETTE["linucb"])
    fig_psi(d)
    print("\nwrote fig_fairness_region / fig_fairness_occupation / fig_psi_timeseries (.pdf + .png)")


if __name__ == "__main__":
    main()
