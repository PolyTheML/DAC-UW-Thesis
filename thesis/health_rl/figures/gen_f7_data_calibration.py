"""Figure F7 -- synthetic-data calibration against published national sources.

Cache-only (no experiment): reads data/cambodia/cambodia_dataset.csv and compares
the produced marginal of each load-bearing feature against the published value its
generator was anchored on. Published targets are quoted VERBATIM from the anchor
docstring in data/cambodia/generate_cambodia_dataset.py (CDHS 2021-22, Cambodia
STEPS 2023, WHO). Only proportion-valued features with a clean published prevalence
are shown; e.g. TB is omitted because the WHO figure (246/100k) is an *incidence*
rate, not a prevalence the dataset's condition flag can be compared against.

Any mismatch is reported honestly (the bars show both numbers) -- this is a
calibration check, not a fit.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _style import apply_style, save, PALETTE   # noqa: E402
import matplotlib.pyplot as plt                  # noqa: E402
from matplotlib.patches import Patch             # noqa: E402

CSV = ROOT / "data" / "cambodia" / "cambodia_dataset.csv"


def main():
    df = pd.read_csv(CSV)
    cond = df["pre_existing_conditions"].fillna("")
    female = df["gender"] == "Female"
    male = df["gender"] == "Male"

    # (label, dataset %, published %, source)  -- published quoted verbatim from the generator docstring.
    rows = [
        ("Female (overall)",      100 * female.mean(),                        52.2, "CDHS 2021-22"),
        ("Smoking (men)",         100 * df.loc[male, "is_smoking"].mean(),    29.6, "STEPS 2023"),
        ("Smoking (women)",       100 * df.loc[female, "is_smoking"].mean(),   1.4, "CDHS/STEPS"),
        ("Alcohol (men)",         100 * df.loc[male, "alcohol_use"].mean(),   64.0, "CDHS 2022"),
        ("Alcohol (women)",       100 * df.loc[female, "alcohol_use"].mean(), 16.0, "CDHS 2022"),
        ("Hypertension",          100 * cond.str.contains("Hypertension").mean(), 16.8, "STEPS 2023"),
        ("Diabetes",              100 * cond.str.contains("Diabetes").mean(),  7.6, "STEPS 2023"),
        ("Hepatitis B",           100 * cond.str.contains("Hepatitis B").mean(), 7.5, "WHO 2019"),
    ]

    print(f"=== F7 data calibration (dataset n = {len(df)}) ===")
    print(f"  {'feature':18s} {'dataset%':>9s} {'published%':>11s}  source")
    for lab, d, p, src in rows:
        print(f"  {lab:18s} {d:9.1f} {p:11.1f}  {src}")

    apply_style()
    labels = [r[0] for r in rows]
    data_v = np.array([r[1] for r in rows])
    pub_v = np.array([r[2] for r in rows])
    srcs = [r[3] for r in rows]

    y = np.arange(len(rows))[::-1]   # first feature at top
    h = 0.38
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    ax.barh(y + h / 2, data_v, height=h, color=PALETTE["linucb"], alpha=0.92,
            edgecolor="white", linewidth=0.5, label="Synthetic dataset")
    ax.barh(y - h / 2, pub_v, height=h, color=PALETTE["random"], alpha=0.95,
            edgecolor="white", linewidth=0.5, label="Published source")
    for yi, d, p in zip(y, data_v, pub_v):
        ax.text(d + 0.6, yi + h / 2, f"{d:.1f}", va="center", ha="left", fontsize=7.5)
        ax.text(p + 0.6, yi - h / 2, f"{p:.1f}", va="center", ha="left", fontsize=7.5,
                color="#555555")

    ax.set_yticks(y)
    ax.set_yticklabels([f"{lab}\n({src})" for lab, src in zip(labels, srcs)], fontsize=8)
    ax.set_xlabel("Prevalence / share (%)")
    ax.set_xlim(0, max(data_v.max(), pub_v.max()) * 1.16)
    ax.grid(True, axis="x", alpha=0.30)
    ax.grid(False, axis="y")
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    save(fig, "fig_data_calibration")
    print("\nwrote fig_data_calibration (.pdf + .png)")


if __name__ == "__main__":
    main()
