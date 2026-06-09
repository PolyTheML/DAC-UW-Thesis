"""Figure 7 -- baseline ladder, re-rendered in the publication style.

Authoritative source: research/results/reward_sensitivity_results.csv, model=ORIGINAL,
20 seeds -- reproduces frozen Table 9 exactly. Encodes the HONEST framing: the bandits
(LinUCB, LinTS) lead every DEPLOYABLE policy; AlwaysRATED (inadmissible constant),
LogisticOracle (optimistic ceiling, in-sample), and Oracle (upper bound) are
non-deployable reference ceilings, drawn hatched.

Also renders a throwaway _mathtext_probe.png to confirm Times+STIX math glyphs render
(Greek, sqrt, subscripts, superscripts) before the long experiment re-runs.
"""
from __future__ import annotations

import sys
import csv
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]            # C:\DAC-UW-Thesis
sys.path.insert(0, str(ROOT / "healthrl" / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from statistical_utils import bootstrap_ci             # noqa: E402
from _style import apply_style, save, PALETTE          # noqa: E402
import matplotlib.pyplot as plt                         # noqa: E402
from matplotlib.patches import Patch                    # noqa: E402

CSV = ROOT / "research" / "results" / "reward_sensitivity_results.csv"

# csv policy key -> (display name, palette key, deployable?)
SPEC = {
    "Random":         ("Random",         "random",   True),
    "AlwaysSTANDARD": ("AlwaysSTANDARD", "epsilon",  True),
    "StaticXGB":      ("Static XGB",     "static",   True),
    "LinUCB":         ("LinUCB",         "linucb",   True),
    "LinTS":          ("LinTS",          "lints",    True),
    "AlwaysRATED":    ("AlwaysRATED",    "constant", False),
    "LogisticPolicy": ("LogisticOracle", "logistic", False),
    "Oracle":         ("Oracle",         "oracle",   False),
}


def load():
    d = defaultdict(list)
    for r in csv.DictReader(open(CSV)):
        if r["model"] == "ORIGINAL":
            d[r["policy"]].append(float(r["reward"]))
    return d


def ladder():
    apply_style()
    d = load()
    rows = []
    for pol, (name, key, deploy) in SPEC.items():
        v = np.array(d[pol])
        lo, hi = bootstrap_ci(v)
        rows.append((name, key, deploy, v.mean(), lo, hi))
    rows.sort(key=lambda r: r[3])

    names = [r[0] for r in rows]
    means = np.array([r[3] for r in rows])
    lo_err = means - np.array([r[4] for r in rows])
    hi_err = np.array([r[5] for r in rows]) - means

    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    y = np.arange(len(names))
    for i, r in enumerate(rows):
        dep = r[2]
        ax.barh(y[i], means[i], color=PALETTE[r[1]], alpha=0.92 if dep else 0.50,
                hatch=None if dep else "////",
                edgecolor="white" if dep else PALETTE[r[1]], linewidth=0.6,
                xerr=[[lo_err[i]], [hi_err[i]]],
                error_kw={"ecolor": "#333333", "elinewidth": 0.8, "capsize": 2.5})
        ax.text(means[i] + hi_err[i] + max(means) * 0.012, y[i],
                f"\\${means[i]:,.0f}", va="center", ha="left", fontsize=8.5)

    ax.set_yticks(y)
    ax.set_yticklabels(names)
    for lbl in ax.get_yticklabels():
        if lbl.get_text() in ("LinUCB", "LinTS"):
            lbl.set_fontweight("bold")
    ax.set_xlabel("Cumulative reward (\\$), mean ± 95% bootstrap CI")
    ax.set_xlim(0, max(means + hi_err) * 1.20)

    legend = [
        Patch(facecolor="#777777", alpha=0.92, label="Deployable policy"),
        Patch(facecolor="#777777", alpha=0.50, hatch="////", edgecolor="#777777",
              label="Reference ceiling (not deployable)"),
    ]
    ax.legend(handles=legend, loc="lower right", fontsize=8)
    fig.tight_layout()
    save(fig, "fig_exp_014_baseline_ladder")

    print("Figure 7 re-render -- reproduction check vs frozen Table 9:")
    for name, key, dep, m, lo, hi in rows:
        tag = "" if dep else "  (reference ceiling)"
        print(f"  {name:16s} {m:11,.0f}{tag}")


def mathtext_probe():
    """Render a card of math-bearing strings to eyeball Times+STIX coverage."""
    apply_style()
    fig, ax = plt.subplots(figsize=(6.6, 2.4))
    ax.axis("off")
    tests = [
        r"Greek: $\alpha$, $\beta$, $\gamma$, $\varepsilon$, $\lambda$, $\theta$, $\sigma$, $\pi$",
        r"Regret bound: $R_T = O(d\sqrt{T})$,  slope $= 0.572$,  $R^2 = 0.99$",
        r"Update: $A_a \leftarrow A_a + x_t x_t^{\top}$,  $\hat\theta_a = A_a^{-1} b_a$",
        r"Stats: $p < 0.001$,  Cohen's $d = 2.98$,  $\mathbb{R}^{34}$,  $\pm$, $\leq$, $\geq$",
        r"Currency (escaped \$): \$90{,}540 vs \$72{,}292  ($+25.2\%$)",
    ]
    for i, t in enumerate(tests):
        ax.text(0.02, 0.92 - i * 0.20, t, fontsize=12, va="top", transform=ax.transAxes)
    ax.text(0.02, 0.0, "Times New Roman text + STIX math (no local TeX)", fontsize=8,
            style="italic", color="#666666", va="bottom", transform=ax.transAxes)
    save(fig, "_mathtext_probe", also_png=True)
    print("wrote _mathtext_probe.png")


if __name__ == "__main__":
    mathtext_probe()
    ladder()
