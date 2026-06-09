"""Figure F2 -- ablation forest plot (EXP-011), thesis Sec. 5.7 (body).

Re-runs the four EXP-011 ablations (Full 4-arm LinUCB, No-REFER 3-arm,
Greedy-only alpha=0, Static XGB) across 20 seeds by importing the *exact*
ablation functions from exp_011_ablation_study, then draws a horizontal forest
of the paired cumulative-reward difference (ablation - Full LinUCB) centred at
zero, with Full LinUCB as the reference line.

Reproduces frozen Table 15 (Sec. 5.7) to the dollar:
    Full        90,540 +/- 5,382 [88,287, 92,886]
    No-REFER    94,481  -> delta +3,941  CI[+373,+7,348]  d=+0.49
    Greedy(a=0) 91,261  -> delta   +721  CI[-1,459,+3,191] d=+0.13
    Static XGB  72,292  -> delta -18,248 CI[-20,858,-15,595] d=-2.98

HONEST-FRAMING NOTES (see memory thesis_reframe_status):
* Sign = ablation - Full, so Static sits far LEFT (large negative effect) while
  the two LinUCB variants sit near zero -- the visual headline is "online
  adaptive estimation is load-bearing; the exploration bonus and the REFER arm
  are not."
* The figure carries the bootstrap 95% CI + the per-seed paired differences (as
  faint dots) + Cohen's d. It deliberately prints NO significance star, because
  exp_011 / Table 15 use a ONE-SIDED Wilcoxon ("less", i.e. is-the-ablation-
  WORSE?). For No-REFER, which scored +3,941 HIGHER, that one-sided p=0.978 is
  the wrong tail and would misread as "ns" beside a CI that lies entirely right
  of zero. Both one-sided and two-sided p are printed below for the record /
  for reconciling the Sec. 5.7 prose; they are not stamped on the plot.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]                 # C:\DAC-UW-Thesis
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "healthrl" / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import exp_011_ablation_study as e11                        # noqa: E402
from experiment_utils import run_experiment_seeds_raw       # noqa: E402
from statistical_utils import format_comparison, paired_wilcoxon  # noqa: E402
from _style import apply_style, save, PALETTE, FIG_DIR      # noqa: E402
import matplotlib.pyplot as plt                             # noqa: E402
from matplotlib.lines import Line2D                         # noqa: E402

# Frozen Table 15 means (Sec. 5.7) for the reproduction gate.
FROZEN = {
    "Full (4-arm)":        90540,
    "No REFER (3-arm)":    94481,
    "Greedy-only (a=0)":   91261,
    "Static XGB":          72292,
}
TOL = 50.0  # dollars; the experiment is deterministic so drift should be ~0.


def run_all():
    ablations = {
        "Full (4-arm)":      e11.ablation_full,
        "No REFER (3-arm)":  e11.ablation_no_refer,
        "Greedy-only (a=0)": e11.ablation_greedy,
        "Static XGB":        e11.ablation_static,
    }
    stats = {}
    for name, fn in ablations.items():
        print(f"\n{name}:")
        stats[name] = run_experiment_seeds_raw(fn, n_seeds=e11.N_SEEDS)
    return stats


def verify(stats):
    """Gate: every reward mean must match frozen Table 15 within TOL dollars."""
    print("\n=== F2 REPRODUCTION CHECK vs frozen Table 15 (Sec. 5.7) ===")
    ok = True
    for name, frozen in FROZEN.items():
        m = stats[name]["reward"]["mean"]
        hit = abs(m - frozen) <= TOL
        ok &= hit
        print(f"  {name:20s} reward {m:11,.0f}   (frozen {frozen:,})   {'OK' if hit else 'DRIFT!'}")
    if not ok:
        raise SystemExit("F2 GATE FAILED: ablation reward drifted from frozen Table 15.")
    return ok


def comparisons(stats):
    """Paired (ablation - Full) stats for the three non-Full variants."""
    full = stats["Full (4-arm)"]["reward"]["values"]
    rows = []
    for name in ("No REFER (3-arm)", "Greedy-only (a=0)", "Static XGB"):
        treat = stats[name]["reward"]["values"]
        # alternative="less" matches exp_011 / Table 15 (one-sided inferiority test).
        c = format_comparison(full, treat, metric_name="Cum. Reward",
                              baseline_name="Full (4-arm)", treatment_name=name,
                              alternative="less")
        _, p_two = paired_wilcoxon(full, treat, alternative="two-sided")
        rows.append({
            "name": name,
            "diffs": treat - full,                 # per-seed paired differences
            "mean_diff": c["mean_diff"],
            "ci": c["diff_ci_95"],                 # bootstrap 95% CI of the mean diff
            "d": c["cohens_d"],
            "p_oneside_less": c["wilcoxon_p"],     # the (wrong-tail) value Table 15 reports
            "p_twoside": p_two,
        })
    return rows


def report(rows):
    print("\n=== PAIRED DIFFERENCES vs Full LinUCB (reward) ===")
    print(f"  {'variant':20s} {'mean delta':>11s} {'95% CI':>22s} "
          f"{'d':>6s} {'p(1-sided<)':>11s} {'p(2-sided)':>11s}")
    for r in rows:
        ci = f"[{r['ci'][0]:+,.0f}, {r['ci'][1]:+,.0f}]"
        print(f"  {r['name']:20s} {r['mean_diff']:>+11,.0f} {ci:>22s} "
              f"{r['d']:>+6.2f} {r['p_oneside_less']:>11.4f} {r['p_twoside']:>11.4f}")
    print("  NOTE: Table 15 reports the 1-sided 'less' p. For No-REFER the 2-sided p is the")
    print("  honest two-tailed value; the Sec. 5.7 wording is being surfaced to the user.")


def draw(rows):
    apply_style()
    # Top-to-bottom: No-REFER, Greedy, Static (ascending y plots Static at bottom).
    order = ["Static XGB", "Greedy-only (a=0)", "No REFER (3-arm)"]
    ylab = {
        "No REFER (3-arm)":  "No REFER\n(3-arm)",
        "Greedy-only (a=0)": r"Greedy-only" + "\n" + r"($\alpha=0$)",
        "Static XGB":        "Static XGB",
    }
    color = {
        "No REFER (3-arm)":  PALETTE["linucb"],   # LinUCB variant
        "Greedy-only (a=0)": PALETTE["linucb"],   # LinUCB variant
        "Static XGB":        PALETTE["static"],   # the frozen rule
    }
    by_name = {r["name"]: r for r in rows}

    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    ax.axvline(0, color="#333333", lw=1.2, ls="--", zorder=2)
    ax.text(0, len(order) - 0.40, "Full LinUCB\n(reference)", ha="center", va="bottom",
            fontsize=7.5, color="#333333")

    rng = np.random.default_rng(0)
    for y, name in enumerate(order):
        r = by_name[name]
        c = color[name]
        # faint per-seed paired differences
        jit = (rng.random(len(r["diffs"])) - 0.5) * 0.16
        ax.scatter(r["diffs"], np.full_like(r["diffs"], y) + jit, s=13,
                   color=c, alpha=0.28, edgecolors="none", zorder=1)
        # mean +/- bootstrap 95% CI
        lo_err = r["mean_diff"] - r["ci"][0]
        hi_err = r["ci"][1] - r["mean_diff"]
        ax.errorbar(r["mean_diff"], y, xerr=[[lo_err], [hi_err]], fmt="o",
                    color=c, ecolor=c, elinewidth=1.6, capsize=4, markersize=7,
                    markeredgecolor="white", markeredgewidth=0.6, zorder=3)
        # delta + Cohen's d above the point
        ax.annotate(r"$\Delta$" + f" = {r['mean_diff']:+,.0f}    " + r"$d$" + f" = {r['d']:+.2f}",
                    (r["mean_diff"], y + 0.20), ha="center", va="bottom", fontsize=8)

    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([ylab[n] for n in order])
    ax.set_ylim(-0.6, len(order) - 0.1)
    ax.set_xlabel("Cumulative-reward difference vs Full LinUCB (\\$)")
    xs = np.concatenate([by_name[n]["diffs"] for n in order] +
                        [[by_name[n]["ci"][0], by_name[n]["ci"][1]] for n in order])
    ax.set_xlim(xs.min() - 2500, xs.max() + 3500)
    ax.grid(True, axis="x", alpha=0.30)
    ax.grid(False, axis="y")

    handles = [
        Line2D([0], [0], marker="o", color="#777777", lw=1.6, markersize=7,
               markeredgecolor="white", label="Mean ± 95% bootstrap CI"),
        Line2D([0], [0], marker="o", color="#777777", lw=0, alpha=0.35, markersize=6,
               label="Per-seed difference (20 seeds)"),
    ]
    ax.legend(handles=handles, loc="lower left", fontsize=7.5)
    fig.tight_layout()
    save(fig, "fig_ablation_forest")
    print("\nwrote fig_ablation_forest (.pdf + .png)")


def main():
    print("=" * 70)
    print("F2: ablation forest (EXP-011 re-run, 20 seeds)")
    print("=" * 70)
    stats = run_all()
    verify(stats)
    rows = comparisons(stats)
    report(rows)
    np.savez(
        FIG_DIR / "fig_ablation_forest_cache.npz",
        full=stats["Full (4-arm)"]["reward"]["values"],
        no_refer=stats["No REFER (3-arm)"]["reward"]["values"],
        greedy=stats["Greedy-only (a=0)"]["reward"]["values"],
        static=stats["Static XGB"]["reward"]["values"],
    )
    draw(rows)


if __name__ == "__main__":
    main()
