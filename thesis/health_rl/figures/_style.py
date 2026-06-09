"""Shared publication style for all thesis result figures.

Times-serif text (matches the thesis body) + STIX math (Times-compatible).
The machine has NO local TeX, so matplotlib's usetex/pgf path is unavailable;
STIX mathtext is the robust way to get Times-like math glyphs without LaTeX.
Okabe-Ito colorblind-safe palette. Exports vector PDF (primary) + 300 dpi PNG
(fallback). No in-figure titles -- the LaTeX \\caption describes each figure.

Every result generator should:  from _style import apply_style, save, PALETTE, ci_band
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

FIG_DIR = Path(__file__).resolve().parent

# Okabe-Ito colorblind-safe palette -- shared across every result figure.
PALETTE = {
    "oracle": "#000000", "lints": "#0072B2", "linucb": "#009E73",
    "epsilon": "#E69F00", "static": "#D55E00", "logistic": "#CC79A7",
    "random": "#999999", "constant": "#56B4E9",
}
# PSI guardrail band fills (GREEN <0.10, AMBER 0.10-0.25, RED >0.25).
PSI_BANDS = {"green": "#C8E6C9", "amber": "#FFE0B2", "red": "#FFCDD2"}


def apply_style() -> None:
    """Install the publication rcParams. Idempotent; call once per process."""
    plt.rcParams.update({
        # typography: Times text + STIX (Times-compatible) math
        "font.family": "serif",
        "font.serif": ["Times New Roman", "STIXGeneral", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        # sizes tuned for 0.85\textwidth (~13.6 cm) single column
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "figure.titlesize": 11,
        # clean, journal-like spines/grid
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.30,
        "grid.linewidth": 0.5,
        "axes.linewidth": 0.8,
        "lines.linewidth": 1.5,
        "legend.frameon": False,
        # output: embed TrueType (no Type-3) so the PDF is self-contained on Overleaf
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


def save(fig, stem: str, *, also_png: bool = True) -> Path:
    """Save as vector PDF (primary) + 300 dpi PNG (fallback) into FIG_DIR."""
    pdf = FIG_DIR / f"{stem}.pdf"
    fig.savefig(pdf)
    if also_png:
        fig.savefig(FIG_DIR / f"{stem}.png")
    plt.close(fig)
    return pdf


def ci_band(ax, x, lo, hi, color, *, alpha: float = 0.20, label=None):
    """Shade a [lo, hi] confidence band (e.g. 95% bootstrap CI)."""
    ax.fill_between(x, lo, hi, color=color, alpha=alpha, linewidth=0, label=label)
