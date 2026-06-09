"""Generate Figure 2.1 — Adaptive Underwriting System Architecture (Chapter II).

Deterministic block-and-arrow flow diagram. No randomness, no data dependency.
Five components: Applicant Input → Bandit Engine → Underwriting Action;
Underwriting Action → Reward Simulator → PSI Monitor → Bandit Engine (feedback).

Outputs PNG (300 dpi) and SVG. Designed for thesis docx embedding and clean PDF.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT_DIR = Path(__file__).parent
OUT_PNG = OUT_DIR / "fig_ch2_system_architecture.png"
OUT_SVG = OUT_DIR / "fig_ch2_system_architecture.svg"

# --- Palette ---------------------------------------------------------------
BLUE = "#2E5FA3"      # core component
RED = "#C0392B"       # decision output
GREEN = "#27AE60"     # simulator
ORANGE = "#E67E22"    # fairness guardrail
DARK = "#262626"
LIGHT = "#666666"
WHITE = "#FFFFFF"

# --- Layout ----------------------------------------------------------------
# Component coordinates (centre x, centre y) and category for colouring.
BOXES = {
    "Applicant\nInput":      {"xy": (1.4, 4.5), "color": BLUE,   "category": "Core Component"},
    "Bandit\nEngine":        {"xy": (5.0, 4.5), "color": BLUE,   "category": "Core Component"},
    "Underwriting\nAction":  {"xy": (8.6, 4.5), "color": RED,    "category": "Decision Output"},
    "Reward\nSimulator":     {"xy": (8.6, 1.7), "color": GREEN,  "category": "Simulator"},
    "PSI\nMonitor":          {"xy": (5.0, 1.7), "color": ORANGE, "category": "Fairness Guardrail"},
}

BOX_W = 2.1
BOX_H = 1.1

ARROWS = [
    # (from_box, to_box, label, label_offset_x, label_offset_y)
    ("Applicant\nInput",     "Bandit\nEngine",       "Age, BMI, Region,\nOccupation, Health Conditions", 0.0,  0.55),
    ("Bandit\nEngine",       "Underwriting\nAction", "LinUCB / LinTS /\nEpsilon-Greedy",                  0.0,  0.55),
    ("Underwriting\nAction", "Reward\nSimulator",    "Standard / Rated\n(+25%) / Decline / Refer",        0.95, 0.0),
    ("Reward\nSimulator",    "PSI\nMonitor",         "Premium - Claims\nx Acceptance Prob",               0.0, -0.55),
    ("PSI\nMonitor",         "Bandit\nEngine",       "Region & Occupation\nDistribution Drift",          -0.95, 0.0),
    ("Applicant\nInput",     "PSI\nMonitor",         "Reference\ndistribution",                          -0.95, 0.0),
]


def _box_edge(center, side):
    """Return the boundary point on the side of a box."""
    cx, cy = center
    if side == "right":  return (cx + BOX_W / 2, cy)
    if side == "left":   return (cx - BOX_W / 2, cy)
    if side == "top":    return (cx,            cy + BOX_H / 2)
    if side == "bottom": return (cx,            cy - BOX_H / 2)
    raise ValueError(side)


def _arrow_endpoints(src_center, dst_center):
    """Choose box-edge attachment points based on relative position."""
    sx, sy = src_center
    dx, dy = dst_center
    horizontal = abs(dx - sx) >= abs(dy - sy)
    if horizontal:
        if dx > sx:
            return _box_edge(src_center, "right"), _box_edge(dst_center, "left")
        return _box_edge(src_center, "left"), _box_edge(dst_center, "right")
    if dy > sy:
        return _box_edge(src_center, "top"), _box_edge(dst_center, "bottom")
    return _box_edge(src_center, "bottom"), _box_edge(dst_center, "top")


def main() -> None:
    fig, ax = plt.subplots(figsize=(12, 7))

    # Draw boxes
    for label, spec in BOXES.items():
        cx, cy = spec["xy"]
        box = FancyBboxPatch(
            (cx - BOX_W / 2, cy - BOX_H / 2),
            BOX_W, BOX_H,
            boxstyle="round,pad=0.04,rounding_size=0.18",
            linewidth=1.2, edgecolor=DARK, facecolor=spec["color"], zorder=2,
        )
        ax.add_patch(box)
        ax.text(cx, cy, label, ha="center", va="center",
                color=WHITE, fontsize=12, fontweight="bold", zorder=3)

    # Draw arrows + labels
    for src, dst, label, dxoff, dyoff in ARROWS:
        s_xy, d_xy = _arrow_endpoints(BOXES[src]["xy"], BOXES[dst]["xy"])
        arrow = FancyArrowPatch(
            s_xy, d_xy,
            arrowstyle="-|>", mutation_scale=16,
            color=DARK, linewidth=1.4, zorder=1,
        )
        ax.add_patch(arrow)
        mx = (s_xy[0] + d_xy[0]) / 2 + dxoff
        my = (s_xy[1] + d_xy[1]) / 2 + dyoff
        ax.text(mx, my, label, ha="center", va="center",
                fontsize=8.5, color=LIGHT, zorder=4,
                bbox=dict(boxstyle="round,pad=0.18", facecolor=WHITE, edgecolor="none"))

    # Feedback annotation
    ax.text(5.0, 0.35, "Feedback loop: reward updates bandit parameters",
            ha="center", va="center", fontsize=9.5, color=DARK, style="italic")

    # Title
    ax.text(5.0, 6.3, "Adaptive Underwriting System Architecture",
            ha="center", va="center", fontsize=15, fontweight="bold", color=DARK)

    # Legend
    legend_patches = [
        mpatches.Patch(color=BLUE,   label="Core component"),
        mpatches.Patch(color=RED,    label="Decision output"),
        mpatches.Patch(color=GREEN,  label="Simulator"),
        mpatches.Patch(color=ORANGE, label="Fairness guardrail"),
    ]
    ax.legend(handles=legend_patches, loc="lower right", fontsize=9.5,
              frameon=True, fancybox=False, edgecolor="#BFBFBF")

    # Axis formatting
    ax.set_xlim(-0.4, 10.4)
    ax.set_ylim(-0.4, 6.9)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(WHITE)

    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=300, bbox_inches="tight", facecolor=WHITE)
    plt.savefig(OUT_SVG, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    print(f"Saved PNG -> {OUT_PNG}")
    print(f"Saved SVG -> {OUT_SVG}")


if __name__ == "__main__":
    main()
