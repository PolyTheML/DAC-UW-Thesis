"""Build Figure 4.2 — Contextual Bandit Decision Loop for Chapter 4.

Renders a 5-node cyclic flowchart with rounded rectangular nodes:
context -> action selection -> reward -> parameter update -> next round.

Run from the repo root:
    python thesis/health_rl/scripts/build_fig_ch4_bandit_loop.py
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parents[1] / "figures" / "fig_ch4_bandit_loop.png"

NODE_FILL = "#1f77b4"
NODE_TEXT = "white"
SUB_TEXT = "#333333"
ARROW = "#222222"

NODES = [
    ("1. Observe context\n$x_t \\in \\mathbb{R}^{25}$", "applicant features"),
    ("2. Select action $a_t$\nLinUCB / LinTS / $\\varepsilon$-Greedy", "{STANDARD, RATED, DECLINE, REFER}"),
    ("3. Observe reward $r_t$", "actuarial simulator:\npremium $-$ expected claims"),
    ("4. Update parameters\n$A_{a_t}, b_{a_t}$", "rank-one update, $O(d^2)$"),
    ("5. $t \\leftarrow t + 1$", "next applicant"),
]


def _node(ax, cx, cy, label, sublabel, w=2.6, h=1.3):
    rect = mpatches.FancyBboxPatch(
        (cx - w / 2, cy - h / 2),
        w,
        h,
        boxstyle="round,pad=0.04,rounding_size=0.18",
        linewidth=1.0,
        edgecolor="black",
        facecolor=NODE_FILL,
        alpha=0.92,
    )
    ax.add_patch(rect)
    ax.text(cx, cy, label, ha="center", va="center", color=NODE_TEXT, fontsize=10)

    # sublabel placed outward from centre to avoid overlapping next node
    sub_offset = h / 2 + 0.45
    ax.text(
        cx,
        cy - sub_offset,
        sublabel,
        ha="center",
        va="center",
        color=SUB_TEXT,
        fontsize=9,
        style="italic",
    )


def main() -> None:
    fig, ax = plt.subplots(figsize=(11, 10))
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.set_aspect("equal")
    ax.set_axis_off()

    n = len(NODES)
    radius = 4.0
    positions = []
    for i in range(n):
        angle = math.pi / 2 - 2 * math.pi * i / n
        positions.append((radius * math.cos(angle), radius * math.sin(angle)))

    for (cx, cy), (label, sub) in zip(positions, NODES):
        _node(ax, cx, cy, label, sub)

    # arc arrows between consecutive nodes
    for i in range(n):
        x1, y1 = positions[i]
        x2, y2 = positions[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        ux, uy = dx / length, dy / length
        offset = 1.55  # back off enough to clear node bounding box
        sx, sy = x1 + ux * offset, y1 + uy * offset
        ex, ey = x2 - ux * offset, y2 - uy * offset
        ax.annotate(
            "",
            xy=(ex, ey),
            xytext=(sx, sy),
            arrowprops=dict(
                arrowstyle="->",
                color=ARROW,
                lw=1.6,
                connectionstyle="arc3,rad=0.18",
            ),
        )

    ax.text(
        0,
        0.4,
        "Contextual\nBandit Loop",
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold",
        color="#444444",
    )
    ax.text(
        0,
        -0.6,
        "(repeats for $t = 1, \\dots, T$)",
        ha="center",
        va="center",
        fontsize=10,
        color="#666666",
    )

    ax.set_title(
        "Figure 4.2 — Contextual Bandit Decision Loop (one round per applicant)",
        fontsize=12,
        pad=18,
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
