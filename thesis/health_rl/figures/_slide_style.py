"""Slide-scale figure style for the defense deck (v2 Minimal Academic).

Sans type >= 14 pt, thick lines, deck palette, PNG-only into figures/slides/.
Companion to _style.py (publication style) -- thesis report figures are NOT touched.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SLIDE_DIR = Path(__file__).resolve().parent / "slides"

SLIDE_PALETTE = {
    "hero":    "#5D2A42",   # burgundy -- headline series (LinUCB unless noted)
    "hero2":   "#8A5570",   # lighter burgundy variants (HITL conservatism cells)
    "hero3":   "#B894A6",
    "lints":   "#3B6EA5",   # blue -- only when a third series is unavoidable
    "compare": "#9AA0A6",   # warm gray -- the baseline being beaten
    "amber":   "#E6A62E",
    "green":   "#2E8B57",
    "red":     "#D93B3B",   # inadmissible / failure semantics
    "dark":    "#1A1A1A",
}


def apply_slide_style() -> None:
    """Projection-scale rcParams. Call before building each figure."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Calibri", "Arial", "DejaVu Sans"],
        "mathtext.fontset": "dejavusans",
        "font.size": 16,
        "axes.labelsize": 18,
        "xtick.labelsize": 14,
        "ytick.labelsize": 14,
        "legend.fontsize": 16,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.22,
        "grid.linewidth": 0.8,
        "axes.linewidth": 1.2,
        "lines.linewidth": 3.5,
        "legend.frameon": False,
        "figure.dpi": 110,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
    })


def save_slide(fig, stem: str) -> Path:
    SLIDE_DIR.mkdir(exist_ok=True)
    out = SLIDE_DIR / f"{stem}.png"
    fig.savefig(out)
    plt.close(fig)
    return out
