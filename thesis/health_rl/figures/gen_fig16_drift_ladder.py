"""Figure 16 -- drift-rescue ladder, re-rendered in the publication style.

Cache-only (no re-run): reads research/results/drift_rescue_summary{,_severe}.json,
whose total_mean / total_ci are the frozen 95% bootstrap aggregates that reproduce
Table 20 of chapter05 to the dollar (best_const AlwaysRATED 99,321; LinTS 71,429; etc.).

HONEST NEGATIVE-RESULT FRAMING (chapter05 caption: "AlwaysRATED dominates every
learner"): under the EXP-009 drift shock, NO adaptive policy -- LinUCB, LinTS, or the
forgetting bandit DiscountedLinUCB at any gamma -- beats the trivial constant. Mirrors
Fig 7's deployable/reference encoding (AlwaysRATED + Oracle hatched), BUT separates the
two hatched bars in the legend so AlwaysRATED reads as "a trivial one-liner that beats
every learner" (sharpens the result), NOT "an oracle we are not expected to reach".

No recomputable percentage is drawn on the figure: the "-39%" in Table 20 is
gap/learner, which a reader would mis-recompute as 28% off the bar tops. The figure
states the denominator-free absolute gap; the effect sizes live in Table 20 / the prose.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]                  # C:\DAC-UW-Thesis
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _style import apply_style, save, PALETTE                # noqa: E402
import matplotlib.pyplot as plt                              # noqa: E402
from matplotlib.patches import Patch                         # noqa: E402

RESULTS = ROOT / "research" / "results"

# summary key -> (display name, palette key, deployable?)
SPEC = {
    "AlwaysSTANDARD": ("AlwaysSTANDARD",          "epsilon",  True),
    "AlwaysDECLINE":  ("AlwaysDECLINE",           "random",   True),
    "StaticXGB":      ("Static XGB",              "static",   True),
    "DLinUCB@.99":    (r"DLinUCB ($\gamma$=.99)",  "logistic", True),
    "DLinUCB@.995":   (r"DLinUCB ($\gamma$=.995)", "logistic", True),
    "DLinUCB@.999":   (r"DLinUCB ($\gamma$=.999)", "logistic", True),
    "LinUCB":         ("LinUCB",                  "linucb",   True),
    "LinTS":          ("LinTS",                   "lints",    True),
    "AlwaysRATED":    ("AlwaysRATED",             "constant", False),  # reference ceiling
    "Oracle":         ("Oracle",                  "oracle",   False),  # upper bound
}
# learners + the deployable rule -- used only to size the "best learner trails by" gap
LEARNERS = ["StaticXGB", "DLinUCB@.99", "DLinUCB@.995", "DLinUCB@.999", "LinUCB", "LinTS"]


def money(v: float) -> str:
    """Currency label: escaped \\$ (literal, not mathtext) + plain thousands commas."""
    return ("-\\$" if v < 0 else "\\$") + f"{abs(v):,.0f}"


def ladder(summary_path: Path, stem: str) -> None:
    apply_style()
    data = json.loads(summary_path.read_text())
    summary = data["summary"]
    best_total = float(data["best_constant_total"])
    best_name = SPEC[data["best_constant"]][0]

    rows = []
    for key, (name, pkey, deploy) in SPEC.items():
        if key not in summary:
            continue
        s = summary[key]
        rows.append((key, name, pkey, deploy,
                     float(s["total_mean"]), float(s["total_ci"][0]), float(s["total_ci"][1])))
    rows.sort(key=lambda r: r[4])

    means = np.array([r[4] for r in rows])
    lo_err = means - np.array([r[5] for r in rows])
    hi_err = np.array([r[6] for r in rows]) - means

    fig, ax = plt.subplots(figsize=(6.8, 4.7))
    y = np.arange(len(rows))

    xmin = min(r[5] for r in rows)
    xmax = max(r[6] for r in rows)
    span = xmax - xmin
    pad = span * 0.012

    # best-constant threshold + zero divider (drawn behind the bars)
    ax.axvline(best_total, ls="--", lw=1.0, color=PALETTE["constant"], alpha=0.9, zorder=0)
    if xmin < 0:
        ax.axvline(0, lw=0.8, color="#888888", alpha=0.7, zorder=0)

    for i, r in enumerate(rows):
        dep = r[3]
        ax.barh(y[i], means[i], color=PALETTE[r[2]], alpha=0.92 if dep else 0.50,
                hatch=None if dep else "////",
                edgecolor="white" if dep else PALETTE[r[2]], linewidth=0.6, zorder=3,
                xerr=[[lo_err[i]], [hi_err[i]]],
                error_kw={"ecolor": "#333333", "elinewidth": 0.8, "capsize": 2.5, "zorder": 4})
        if means[i] >= 0:
            ax.text(means[i] + hi_err[i] + pad, y[i], money(means[i]),
                    va="center", ha="left", fontsize=8.0)
        else:
            ax.text(means[i] - lo_err[i] - pad, y[i], money(means[i]),
                    va="center", ha="right", fontsize=8.0)

    ax.set_yticks(y)
    ax.set_yticklabels([r[1] for r in rows])
    for lbl in ax.get_yticklabels():
        if lbl.get_text() in ("LinUCB", "LinTS"):
            lbl.set_fontweight("bold")
    ax.set_xlabel("Total reward (\\$), mean ± 95% bootstrap CI")
    ax.set_xlim(xmin - span * 0.20, xmax + span * 0.18)

    # threshold label above the top bar
    ax.text(best_total, len(rows) - 0.35, f"{best_name}\nbest constant — unbeaten",
            ha="center", va="bottom", fontsize=7.5, color=PALETTE["constant"], linespacing=1.1)

    # denominator-free gap note (absolute $, no recomputable %) in the empty upper-left
    best_learner = max(summary[k]["total_mean"] for k in LEARNERS if k in summary)
    gap = best_total - best_learner
    ax.text(0.02, 0.97, f"No learner reaches the best constant\n(closest trails by {money(gap)})",
            transform=ax.transAxes, va="top", ha="left", fontsize=8.0, color="#333333",
            linespacing=1.2)

    legend = [
        Patch(facecolor="#777777", alpha=0.92, label="Deployable policy"),
        Patch(facecolor=PALETTE["constant"], alpha=0.50, hatch="////", edgecolor=PALETTE["constant"],
              label="AlwaysRATED — trivial constant, unbeaten"),
        Patch(facecolor=PALETTE["oracle"], alpha=0.50, hatch="////", edgecolor=PALETTE["oracle"],
              label="Oracle — upper bound"),
    ]
    ax.legend(handles=legend, loc="lower right", fontsize=7.5)
    fig.tight_layout()
    save(fig, stem)

    print(f"\n{stem}  ({data['scenario']}, {data['seeds']} seeds, shock@{data['shock_round']}):")
    for key, name, pkey, dep, m, lo, hi in rows:
        tag = "" if dep else "  (reference ceiling)"
        print(f"  {name:24s} {m:11,.0f}{tag}")
    print(f"  best constant = {best_name} ({money(best_total)}); closest learner trails by {money(gap)}")


if __name__ == "__main__":
    ladder(RESULTS / "drift_rescue_summary.json", "fig_drift_rescue_ladder")
    ladder(RESULTS / "drift_rescue_summary_severe.json", "fig_drift_rescue_ladder_severe")
