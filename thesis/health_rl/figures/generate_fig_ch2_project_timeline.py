"""Generate Figure 2.2 — Project Timeline, 6-month execution plan (Chapter II).

Deterministic Gantt chart for the thesis project. Phase durations and milestone
labels are sourced from chapter02_presentation.md section 2.4 and are hard-coded
here for full reproducibility.

Outputs PNG (300 dpi) and SVG. Designed for thesis docx embedding and clean PDF.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

OUT_DIR = Path(__file__).parent
OUT_PNG = OUT_DIR / "fig_ch2_project_timeline.png"
OUT_SVG = OUT_DIR / "fig_ch2_project_timeline.svg"

# --- Palette ---------------------------------------------------------------
BLUE = "#2E5FA3"     # research / data
GREEN = "#27AE60"    # engineering
ORANGE = "#E67E22"   # experiments
RED = "#C0392B"      # results / audit
GRAY = "#5C6770"     # writing / defense
LIGHT_GRAY = "#D8DDE1"
DARK = "#262626"
WHITE = "#FFFFFF"

# --- Phase definitions (label, start_week, duration_weeks, color) ----------
# Source: chapter02_presentation.md, section 2.4 (Planning of Project).
PHASES = [
    ("Phase 1: Literature Review & Dataset",     1,  4, BLUE),    # Month 1
    ("Phase 2: Bandit Engine & Reward Simulator", 5,  4, GREEN),   # Month 2
    ("Phase 3: Experiment Execution (EXP-005-007)", 9,  4, ORANGE), # Month 3
    ("Phase 4: Results, Fairness Audit, Figures", 13, 3, RED),     # Month 4
    ("Phase 5: Thesis Writing, Presentation, Defense", 16, 5, GRAY), # Months 5-6
]

# --- Milestones (week, label) ----------------------------------------------
MILESTONES = [
    (4,  "M1: Dataset & baselines"),
    (8,  "M2: Bandit engine ready"),
    (12, "M3: All experiments passing"),
    (15, "M4: Chapter drafts complete"),
    (20, "M5: Defense ready"),
]

# --- Month boundaries -------------------------------------------------------
MONTH_BOUNDARIES = [(1, "Month 1"), (5, "Month 2"), (9, "Month 3"),
                    (13, "Month 4"), (17, "Month 5"), (21, "Month 6")]


def main() -> None:
    fig, ax = plt.subplots(figsize=(13, 6.5))

    y_positions = list(range(len(PHASES)))[::-1]  # top phase on top

    # Vertical month separators
    for week, _ in MONTH_BOUNDARIES:
        ax.axvline(x=week, color=LIGHT_GRAY, linestyle="--", linewidth=0.9, zorder=0)

    # Phase bars
    for y, (label, start, dur, color) in zip(y_positions, PHASES):
        ax.barh(
            y, dur, left=start, height=0.6,
            color=color, edgecolor=DARK, linewidth=0.8, zorder=2,
        )
        bar_label = f"Week {start}-{start + dur - 1}"
        ax.text(
            start + dur / 2.0, y, bar_label,
            ha="center", va="center",
            fontsize=10, fontweight="bold", color=WHITE, zorder=3,
        )

    # Milestone diamonds + labels at bottom. Labels are staggered on two rows
    # to avoid horizontal collision when adjacent milestones are close together
    # (e.g. M3 at week 12 and M4 at week 15).
    milestone_y = -1.0
    for idx, (week, mlabel) in enumerate(MILESTONES):
        ax.plot(week, milestone_y, marker="D", color=DARK, markersize=9, zorder=4)
        label_dy = -0.55 if idx % 2 == 0 else -1.15
        ax.text(
            week, milestone_y + label_dy, mlabel,
            ha="center", va="top", fontsize=8.5, color=DARK, fontweight="bold",
        )

    # Month labels at top
    month_y = len(PHASES) - 0.2
    for (start, mlabel), (next_start, _) in zip(MONTH_BOUNDARIES, MONTH_BOUNDARIES[1:] + [(21, "")]):
        center = (start + next_start) / 2.0
        ax.text(
            center, month_y + 0.55, mlabel,
            ha="center", va="bottom", fontsize=10, color=DARK, fontweight="bold",
        )

    # Y-axis: phase labels
    ax.set_yticks(y_positions)
    ax.set_yticklabels([phase[0] for phase in PHASES], fontsize=10, color=DARK)
    ax.tick_params(axis="y", length=0)

    # X-axis: weeks (ticks below milestone rows)
    ax.set_xlim(0.5, 21)
    ax.set_xticks(list(range(2, 21, 2)))
    ax.set_xticklabels([str(w) for w in range(2, 21, 2)], fontsize=10, color=DARK)
    ax.set_xlabel("Week", fontsize=11, color=DARK, labelpad=8)

    # Y-axis range: extra room below for two milestone-label rows AND x-axis label;
    # extra room above for month labels and the legend.
    ax.set_ylim(milestone_y - 2.5, month_y + 1.8)

    # Hide spines
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.set_facecolor(WHITE)
    fig.patch.set_facecolor(WHITE)

    # Legend placed above the chart, between the title and the month labels.
    legend_patches = [
        mpatches.Patch(color=BLUE,   label="Research and data"),
        mpatches.Patch(color=GREEN,  label="Engineering"),
        mpatches.Patch(color=ORANGE, label="Experiments"),
        mpatches.Patch(color=RED,    label="Results and audit"),
        mpatches.Patch(color=GRAY,   label="Writing and defense"),
    ]
    ax.legend(
        handles=legend_patches, loc="upper center",
        bbox_to_anchor=(0.5, 1.10),
        ncol=5, fontsize=9, frameon=False, handlelength=1.2,
    )

    # Title (above legend)
    ax.set_title(
        "Project Timeline - 6-Month Execution Plan",
        fontsize=14, fontweight="bold", color=DARK, pad=42,
    )

    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=300, bbox_inches="tight", facecolor=WHITE)
    plt.savefig(OUT_SVG, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    print(f"Saved PNG -> {OUT_PNG}")
    print(f"Saved SVG -> {OUT_SVG}")


if __name__ == "__main__":
    main()
