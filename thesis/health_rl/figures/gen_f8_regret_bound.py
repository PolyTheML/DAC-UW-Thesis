"""Figure F8 -- regret-bound validation: the empirical LinUCB exponent vs the
theoretical O(sqrt T) RATE (not the constant). Thesis appendix.

Reuses EXP-013's exact harness (run_single_seed, fit_loglog_slope) so the numbers
reproduce Sec. 5.6 / Table 14. Two panels:
  (a) mean-curve log-log slope as the early-round burn-in is increased -> the
      empirical exponent falls monotonically toward the theoretical 0.5 as the
      finite-T terms wash out (reproduces Table 14).
  (b) the 20 per-seed slopes (t_min = 200) against the theoretical 0.5 and the
      pre-registered plausibility band [0.30, 0.80].

HONEST FRAMING (Sec. 5.6 caveat): this validates the *T-dependence* (the exponent),
NOT the constant or the d-factor (d = 34). No constant-calibrated d*sqrt(T) envelope
is drawn -- that would over-claim "inside the proven envelope," which Sec. 5.6
explicitly disclaims.

Caches the 20 per-seed cumulative-regret curves to fig_regret_bound_cache.npz so
cosmetic re-renders do not repeat the EXP-013 run.
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
from _style import apply_style, save             # noqa: E402
import matplotlib.pyplot as plt                   # noqa: E402

BURN_INS = [50, 100, 200, 500, 1000]
T_MIN_SEED = 200          # exp_013 default -> reproduces the Sec. 5.6 per-seed mean 0.564
BAND = (0.30, 0.80)
CACHE = Path(__file__).resolve().parent / "fig_regret_bound_cache.npz"


def get_curves():
    if CACHE.exists():
        print("loaded cached EXP-013 curves")
        return list(np.load(CACHE)["curves"])
    curves = []
    for s in range(e13.N_SEEDS):
        print(f"  seed {s + 1}/{e13.N_SEEDS} ...", flush=True)
        curves.append(e13.run_single_seed(s))
    np.savez(CACHE, curves=np.array(curves))
    return curves


def main():
    curves = get_curves()
    mean_curve = np.mean(curves, axis=0)

    slopes_bi = [e13.fit_loglog_slope(mean_curve, t_min=bi)["slope"] for bi in BURN_INS]
    per_seed = np.array([e13.fit_loglog_slope(c, t_min=T_MIN_SEED)["slope"] for c in curves])
    mean_ps = float(per_seed.mean())
    frac_band = float(np.mean((per_seed >= BAND[0]) & (per_seed <= BAND[1])))

    print("\n=== F8 reproduction vs Sec. 5.6 / Table 14 ===")
    print("  burn-in -> mean-curve slope (frozen: 0.621/0.598/0.572/0.537/0.511):")
    for bi, sl in zip(BURN_INS, slopes_bi):
        print(f"    {bi:5d}: {sl:.3f}")
    print(f"  per-seed mean slope {mean_ps:.3f} (frozen 0.564); "
          f"in-band {frac_band*100:.0f}% (frozen 85%)")

    apply_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.7))

    # (a) burn-in convergence ------------------------------------------------
    ax1.axhline(0.5, ls="--", lw=1.3, color="#333333",
                label=r"Theoretical $O(\sqrt{T})$: $0.5$")
    ax1.plot(BURN_INS, slopes_bi, color="#009E73", marker="o", markersize=6,
             markeredgecolor="white", markeredgewidth=0.5, linewidth=1.6,
             label="Mean-curve slope")
    for bi, sl in zip(BURN_INS, slopes_bi):
        ax1.annotate(f"{sl:.3f}", (bi, sl), textcoords="offset points", xytext=(0, 7),
                     ha="center", fontsize=7.5)
    ax1.set_xscale("log")
    ax1.set_xticks(BURN_INS)
    ax1.set_xticklabels([str(b) for b in BURN_INS])
    ax1.set_xlabel("Burn-in window (rounds discarded)")
    ax1.set_ylabel(r"Log--log slope of $R_T$")
    ax1.set_ylim(0.45, 0.66)
    ax1.legend(loc="upper right", fontsize=7.5)
    ax1.set_title("(a) Exponent vs burn-in", fontsize=9)

    # (b) per-seed slope distribution ---------------------------------------
    ax2.axvspan(BAND[0], BAND[1], color="#56B4E9", alpha=0.16, zorder=0,
                label=f"Pre-registered band [{BAND[0]:.2f}, {BAND[1]:.2f}]")
    ax2.axvline(0.5, ls="--", lw=1.3, color="#333333", zorder=2, label="Theoretical 0.5")
    ax2.axvline(mean_ps, ls="-", lw=1.4, color="#D55E00", zorder=2, label=f"Mean {mean_ps:.3f}")
    rng = np.random.default_rng(0)
    jit = (rng.random(len(per_seed)) - 0.5) * 0.6
    inb = (per_seed >= BAND[0]) & (per_seed <= BAND[1])
    ax2.scatter(per_seed[inb], jit[inb], s=24, color="#009E73", alpha=0.85,
                edgecolors="white", linewidths=0.4, zorder=3, label="Per-seed slope")
    ax2.scatter(per_seed[~inb], jit[~inb], s=30, color="#E69F00", alpha=0.95,
                edgecolors="white", linewidths=0.4, marker="D", zorder=3, label="Outside band")
    ax2.set_ylim(-1.0, 1.5)
    ax2.set_yticks([])
    ax2.set_xlabel(r"Per-seed log--log slope ($t_{\min}=200$)")
    ax2.annotate(f"{int(round(frac_band*len(per_seed)))}/{len(per_seed)} seeds within band",
                 xy=(0.5, 0.93), xycoords="axes fraction", ha="center", fontsize=8, color="#444444")
    ax2.legend(loc="lower center", fontsize=6.3, ncol=2, framealpha=0.9)
    ax2.set_title("(b) Per-seed spread", fontsize=9)

    fig.tight_layout()
    save(fig, "fig_regret_bound_overlay")
    print("\nwrote fig_regret_bound_overlay (.pdf + .png)")


if __name__ == "__main__":
    main()
