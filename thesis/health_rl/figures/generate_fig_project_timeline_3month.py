"""
Generate a 3-month internship Gantt chart figure.
Output: thesis/health_rl/figures/fig_project_timeline_3month.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

OUT = Path(__file__).parent / "fig_project_timeline_3month.png"

# Color palette
BLUE = "#2E5FA3"
TEAL = "#3A9B8F"
ORANGE = "#D9782D"
GRAY = "#8C8C8C"
LIGHT_GRAY = "#E6E6E6"
DARK = "#262626"
WHITE = "#FFFFFF"

# Tasks: (label, start_week, duration_weeks, color, stream)
tasks = [
    # Month 1 — Foundation
    ("Literature review & scope freeze", 1, 2, BLUE, "A"),
    ("Dataset generation (CDHS anchored)", 2, 2, BLUE, "A"),
    ("GLM + XGB baseline training", 3, 2, BLUE, "A"),
    ("Bandit algorithms (LinUCB / LinTS)", 3.5, 2.5, BLUE, "A"),
    ("Reward simulator & PSI module", 4, 2, BLUE, "A"),

    # Month 2 — Experiments & Demos
    ("EXP-005: Convergence validation", 5, 1.5, TEAL, "B"),
    ("EXP-006: Fairness audit", 6, 1.5, TEAL, "B"),
    ("EXP-007: Benchmark comparison", 7, 1, TEAL, "B"),
    ("EXP-008: Human-in-the-loop", 7.5, 1.5, TEAL, "B"),
    ("Web demo /demo (baseline bandit)", 6.5, 2, ORANGE, "C"),
    ("Web demo /hitl (human review)", 7.5, 2, ORANGE, "C"),
    ("Web demo /drift (non-stationary)", 8.5, 2, ORANGE, "C"),
    ("Offline demo package", 9.5, 1.5, ORANGE, "C"),

    # Month 3 — Writing & Defense
    ("Ch2 Literature Review", 9, 2, GRAY, "D"),
    ("Ch3 Methodology", 9.5, 2.5, GRAY, "D"),
    ("Ch4 Results (EXP-005–008)", 10.5, 2, GRAY, "D"),
    ("Ch4 Discussion + Ch5 Conclusion", 11.5, 2, GRAY, "D"),
    ("Defense presentation (20 slides)", 11, 2, GRAY, "D"),
    ("Final review & DOCX formatting", 12, 2, GRAY, "D"),
]

# Separate into streams for ordering
stream_order = ["A", "B", "C", "D"]
stream_labels = {
    "A": "A. Research & Modeling",
    "B": "B. Experiments",
    "C": "C. Engineering",
    "D": "D. Writing & Defense",
}

fig, ax = plt.subplots(figsize=(14, 8))

y_pos = 0
tick_labels = []
tick_positions = []

for stream in stream_order:
    stream_tasks = [t for t in tasks if t[4] == stream]
    # Add stream header
    ax.barh(y_pos, 0, color="none")
    tick_labels.append(stream_labels[stream])
    tick_positions.append(y_pos)
    y_pos += 0.6

    for label, start, duration, color, _ in stream_tasks:
        ax.barh(y_pos, duration, left=start, height=0.45, color=color, edgecolor=WHITE, linewidth=0.8)
        # Label inside or next to bar
        text_x = start + duration / 2
        text_color = WHITE if color in (BLUE, TEAL, ORANGE) else DARK
        ax.text(text_x, y_pos, label, ha="center", va="center", fontsize=7.5, color=text_color, fontweight="medium")
        tick_labels.append("")
        tick_positions.append(y_pos)
        y_pos += 0.6

    y_pos += 0.3  # gap between streams

# Month separators and labels
for week in [1, 5, 9, 13]:
    ax.axvline(x=week, color=LIGHT_GRAY, linestyle="--", linewidth=0.8, zorder=0)

month_labels = ["March\n(Weeks 1–4)", "April\n(Weeks 5–8)", "May\n(Weeks 9–12)", "June\n(Defense)"]
month_centers = [2.5, 6.5, 10.5, 13.5]
for cx, ml in zip(month_centers, month_labels):
    ax.text(cx, y_pos - 0.5, ml, ha="center", va="bottom", fontsize=10, color=DARK, fontweight="bold")

# Milestone markers
milestones = [
    (4.5, "M1: Baselines ready", TEAL),
    (8.5, "M2: All exps passing", TEAL),
    (10.5, "M3: Demos ready", ORANGE),
    (13, "M4: Thesis complete", GRAY),
]
for mx, mlabel, mcolor in milestones:
    ax.plot(mx, -0.8, marker="D", color=mcolor, markersize=8, zorder=5)
    ax.text(mx, -1.4, mlabel, ha="center", va="top", fontsize=7.5, color=DARK, fontweight="bold")

# Formatting
ax.set_xlim(0.5, 14.5)
ax.set_ylim(-2.2, y_pos)
ax.set_xlabel("Week", fontsize=11, color=DARK)
ax.set_yticks(tick_positions)
ax.set_yticklabels(tick_labels, fontsize=9, color=DARK)
ax.set_xticks(range(1, 14))
ax.set_xticklabels([str(w) for w in range(1, 14)], fontsize=9, color=DARK)
ax.invert_yaxis()
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.tick_params(left=False)
ax.set_facecolor(WHITE)
fig.patch.set_facecolor(WHITE)

# Legend
legend_patches = [
    mpatches.Patch(color=BLUE, label="Research & Modeling"),
    mpatches.Patch(color=TEAL, label="Experiments"),
    mpatches.Patch(color=ORANGE, label="Engineering / Demos"),
    mpatches.Patch(color=GRAY, label="Writing & Defense"),
]
ax.legend(handles=legend_patches, loc="lower right", fontsize=9, frameon=True, fancybox=False, edgecolor=LIGHT_GRAY)

plt.title("3-Month Internship Timeline — Adaptive Health Insurance Underwriting", fontsize=13, fontweight="bold", color=DARK, pad=15)
plt.tight_layout()
plt.savefig(OUT, dpi=300, bbox_inches="tight", facecolor=WHITE)
print("Saved -> " + str(OUT))
