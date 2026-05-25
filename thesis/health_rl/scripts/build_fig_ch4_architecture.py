"""Build Figure 4.1 — System Architecture for Chapter 4.

Renders a 3-layer block diagram (Browser tabs -> FastAPI endpoints -> Backend
modules + dataset) and writes the PNG to thesis/health_rl/figures/.

Run from the repo root:
    python thesis/health_rl/scripts/build_fig_ch4_architecture.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parents[1] / "figures" / "fig_ch4_architecture.png"

LAYER_FRONTEND = "#1f77b4"
LAYER_API = "#2ca02c"
LAYER_BACKEND = "#ff7f0e"
EDGE = "#222222"
TEXT = "#111111"


def _box(ax, x, y, w, h, label, fill, *, fontsize=9):
    rect = mpatches.FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=1.0,
        edgecolor=EDGE,
        facecolor=fill,
        alpha=0.85,
    )
    ax.add_patch(rect)
    ax.text(
        x + w / 2,
        y + h / 2,
        label,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=TEXT,
        wrap=True,
    )


def _layer_label(ax, y, text, color):
    ax.text(
        0.15,
        y,
        text,
        ha="right",
        va="center",
        fontsize=10,
        fontweight="bold",
        color=color,
    )


def main() -> None:
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.set_axis_off()

    # Layer 1: Browser tabs
    _layer_label(ax, 7.0, "Browser\n(SPA)", LAYER_FRONTEND)
    tabs = [
        "Applicant\nSimulator",
        "Premium\nOptimiser",
        "Bandit\nArena",
        "PSI\nMonitor",
    ]
    for i, label in enumerate(tabs):
        _box(ax, 1.0 + i * 2.7, 6.4, 2.3, 1.1, label, LAYER_FRONTEND)

    # Layer 2: FastAPI endpoints
    _layer_label(ax, 4.5, "FastAPI\nREST API", LAYER_API)
    endpoints = [
        "/api/simulate",
        "/api/pricing\n/optimize",
        "/api/bandit/run\n/compare",
        "/api/psi\n/audit",
    ]
    for i, label in enumerate(endpoints):
        _box(ax, 1.0 + i * 2.7, 3.9, 2.3, 1.1, label, LAYER_API)

    # Layer 3: Backend modules
    _layer_label(ax, 1.7, "Python\nBackend", LAYER_BACKEND)
    modules = [
        "Actuarial\nReward Sim",
        "Pricing\nEngine",
        "Bandit\nAlgorithms\n(LinUCB / LinTS / EG)",
        "PSI\nCompute",
    ]
    for i, label in enumerate(modules):
        _box(ax, 1.0 + i * 2.7, 1.1, 2.3, 1.3, label, LAYER_BACKEND)

    # Shared data / model row at the very bottom
    _box(ax, 1.0, -0.3, 5.0, 1.1, "Cambodia synthetic dataset (2,000 applicants)", "#dddddd")
    _box(ax, 6.7, -0.3, 4.6, 1.1, "Static XGBoost baseline (mortality model)", "#dddddd")
    ax.set_ylim(-0.6, 8)

    # Vertical connector arrows between layers
    for i in range(4):
        cx = 1.0 + i * 2.7 + 1.15
        ax.annotate(
            "",
            xy=(cx, 5.05),
            xytext=(cx, 6.35),
            arrowprops=dict(arrowstyle="->", color=EDGE, lw=1.0),
        )
        ax.annotate(
            "",
            xy=(cx, 2.45),
            xytext=(cx, 3.85),
            arrowprops=dict(arrowstyle="->", color=EDGE, lw=1.0),
        )

    # Bottom data dependency arrows
    ax.annotate(
        "",
        xy=(3.5, 0.85),
        xytext=(3.5, 1.05),
        arrowprops=dict(arrowstyle="-", color=EDGE, lw=0.6, ls="dashed"),
    )
    ax.annotate(
        "",
        xy=(9.0, 0.85),
        xytext=(9.0, 1.05),
        arrowprops=dict(arrowstyle="-", color=EDGE, lw=0.6, ls="dashed"),
    )

    ax.set_title(
        "Figure 4.1 — System Architecture of the Contextual Bandit Underwriting Demo",
        fontsize=11,
        pad=14,
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
