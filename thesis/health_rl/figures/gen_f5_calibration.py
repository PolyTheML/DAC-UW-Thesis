"""Figure F5 -- reliability/calibration of the Static-XGB (and GLM) mortality model.

Cache-only (no experiment re-run): reads the frozen offline test-set predictions
data/cambodia/models/cambodia_test_predictions.csv, which carries, per held-out
applicant, the realised mortality multiplier (actual_mortality_mult) and the model
predictions (xgb_mortality_mult, glm_mortality_mult).

The Static-XGB baseline thresholds a *predicted mortality multiplier*; this figure
asks the actuarial reviewer's question -- is that predictor calibrated before it is
thresholded? Because the target is a CONTINUOUS multiplier (not a binary event),
the honest diagnostic is regression calibration (predicted vs observed by decile,
calibration slope, RMSE), NOT a Brier score (which applies to probabilities).
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

CSV = ROOT / "data" / "cambodia" / "models" / "cambodia_test_predictions.csv"
N_BINS = 10


def deciles(pred, actual):
    """Mean predicted and mean observed per equal-count predicted-value bin."""
    order = np.argsort(pred)
    pred, actual = pred[order], actual[order]
    edges = np.linspace(0, len(pred), N_BINS + 1).astype(int)
    xp, yo = [], []
    for k in range(N_BINS):
        sl = slice(edges[k], edges[k + 1])
        if edges[k + 1] > edges[k]:
            xp.append(pred[sl].mean())
            yo.append(actual[sl].mean())
    return np.array(xp), np.array(yo)


def metrics(pred, actual):
    slope, intercept = np.polyfit(pred, actual, 1)
    rmse = float(np.sqrt(np.mean((pred - actual) ** 2)))
    r = np.corrcoef(pred, actual)[0, 1]
    return slope, intercept, rmse, r ** 2


def main():
    df = pd.read_csv(CSV)
    actual = df["actual_mortality_mult"].to_numpy(float)
    series = [
        ("Static XGB", "xgb_mortality_mult", PALETTE["static"], "o"),
        ("GLM",        "glm_mortality_mult", PALETTE["lints"],  "s"),
    ]

    apply_style()
    fig, ax = plt.subplots(figsize=(6.0, 5.2))
    lo = min(actual.min(), *[df[c].min() for _, c, _, _ in series])
    hi = max(actual.max(), *[df[c].max() for _, c, _, _ in series])
    pad = 0.05 * (hi - lo)
    ax.plot([lo - pad, hi + pad], [lo - pad, hi + pad], ls="--", lw=1.2,
            color="#333333", label="Perfect calibration ($y=x$)", zorder=1)

    print("=== F5 calibration metrics (held-out test set, n = %d) ===" % len(df))
    for name, col, color, mk in series:
        pred = df[col].to_numpy(float)
        ax.scatter(pred, actual, s=6, color=color, alpha=0.12, edgecolors="none", zorder=1)
        xp, yo = deciles(pred, actual)
        slope, intercept, rmse, r2 = metrics(pred, actual)
        ax.plot(xp, yo, color=color, marker=mk, markersize=6, linewidth=1.6,
                markeredgecolor="white", markeredgewidth=0.5, zorder=3,
                label=f"{name} (decile means; slope {slope:.2f}, RMSE {rmse:.2f}, $R^2$ {r2:.2f})")
        print(f"  {name:10s} slope {slope:.3f}  intercept {intercept:+.3f}  RMSE {rmse:.3f}  R2 {r2:.3f}")

    ax.set_xlabel("Predicted mortality multiplier")
    ax.set_ylabel("Observed mortality multiplier")
    ax.set_xlim(lo - pad, hi + pad)
    ax.set_ylim(lo - pad, hi + pad)
    ax.set_aspect("equal", adjustable="box")
    ax.legend(loc="upper left", fontsize=7.5)
    fig.tight_layout()
    save(fig, "fig_xgb_calibration")
    print("\nwrote fig_xgb_calibration (.pdf + .png)")


if __name__ == "__main__":
    main()
