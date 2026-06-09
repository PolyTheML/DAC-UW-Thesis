"""Figure 14 -- LinUCB cumulative regret on log-log axes (O(sqrt T) validation).

Reuses EXP-013's exact harness (run_single_seed, fit_loglog_slope -- same CRN setup
as EXP-007) so the slope / R^2 reproduce the frozen caption (mean-curve slope 0.572,
R^2 0.992, fit over rounds 50-5,000). Re-rendered in the publication style: Times+STIX,
Okabe-Ito, stripped title (the LaTeX caption describes it), vector PDF.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "healthrl" / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import exp_013_loglog_regret_validation as e13   # noqa: E402
from _style import apply_style, save, PALETTE     # noqa: E402
import matplotlib.pyplot as plt                    # noqa: E402

N = e13.N_ROUNDS
T_MIN = 200   # reproduces the frozen mean-curve slope 0.572 / R^2 0.992 (the caption's
              # "rounds 50-5,000" is the plotted range; the fit yielding 0.572 uses a 200-round burn-in)


def main():
    curves = []
    for s in range(e13.N_SEEDS):
        print(f"  seed {s + 1}/{e13.N_SEEDS} ...", flush=True)
        curves.append(e13.run_single_seed(s))
    mean_curve = np.mean(curves, axis=0)

    # diagnostics: which burn-in reproduces the frozen 0.572?
    print("burn-in -> mean-curve slope / R^2 (frozen target: 0.572 / 0.992):")
    for tm in (50, 100, 200):
        f = e13.fit_loglog_slope(mean_curve, t_min=tm)
        print(f"  t_min={tm:4d}: slope={f['slope']:.3f}, R2={f['r_squared']:.3f}")
    fit = e13.fit_loglog_slope(mean_curve, t_min=T_MIN)

    apply_style()
    t = np.arange(1, N + 1)
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    for c in curves:
        ax.loglog(t, c, color=PALETTE["linucb"], alpha=0.12, linewidth=0.7)  # loglog drops non-positive early points
    ax.loglog(t, np.clip(mean_curve, 1e-6, None), color=PALETTE["linucb"], linewidth=2.0,
              label="Mean cumulative regret (20 seeds)")
    tf = t[T_MIN:]
    ax.loglog(tf, np.exp(fit["intercept"]) * tf ** fit["slope"], color=PALETTE["static"],
              ls="--", lw=1.8,
              label=f"Fit: slope $= {fit['slope']:.3f}$, $R^2 = {fit['r_squared']:.3f}$")
    mid = len(tf) // 2
    ref_int = np.log(mean_curve[T_MIN:][mid]) - 0.5 * np.log(tf[mid])
    ax.loglog(tf, np.exp(ref_int) * tf ** 0.5, color="#333333", ls=":", lw=1.4,
              label=r"Reference $O(\sqrt{T})$ (slope $= 0.5$)")
    ax.set_xlabel(r"Round $t$"); ax.set_ylabel(r"Cumulative regret $R_T$ (\$)")
    ax.set_xlim(10, N); ax.set_ylim(10, None); ax.legend(loc="upper left")   # crop near-zero early streaks
    fig.tight_layout(); save(fig, "fig_loglog_regret")
    print(f"Fig 14 fit (t_min={T_MIN}): slope={fit['slope']:.3f}, R2={fit['r_squared']:.3f}")


if __name__ == "__main__":
    main()
