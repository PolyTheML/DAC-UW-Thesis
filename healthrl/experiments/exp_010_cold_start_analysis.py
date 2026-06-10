"""
EXP-010: Cold-Start Analysis

Evaluates how quickly LinUCB and LinTS catch up to a freshly-trained XGBoost
static baseline when data is scarce.  For each horizon T ∈ {200, 500, 1000, 2000}:

  1. Train an XGBoost regressor on the first T observations (cold-start model).
  2. Run LinUCB, LinTS, and the fresh StaticXGB for exactly T rounds.
  3. Compare cumulative rewards.

The crossover point (smallest T where a bandit beats the fresh static model)
is annotated on the plot.

PASS criteria:
  1. Crossover point exists for LinUCB and LinTS (they eventually beat FreshXGB).
  2. At T=2000, both bandits have higher cumulative reward than FreshXGB.
"""
from __future__ import annotations

import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import xgboost as xgb

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from healthrl.underwriting_bandit import (
    LinUCB,
    LinTS,
    preprocess_cambodia_data,
    run_bandit,
    ACTION_STANDARD,
    ACTION_RATED,
    ACTION_DECLINE,
    ACTION_REFER,
    MODELS_DIR,
)
from healthrl.config import BANDIT

TS = [200, 500, 1000, 2000]


class FreshXGBBaseline:
    """Static baseline that wraps an on-the-fly trained XGBoost model."""

    def __init__(self, model: xgb.XGBRegressor):
        self.model = model
        with open(MODELS_DIR / "cambodia_encoders.pkl", "rb") as f:
            encoders = pickle.load(f)
        self.region_le = encoders["region"]
        self.occ_le = encoders["occupation"]
        self.edu_map = encoders["edu_order"]
        self.wealth_map = encoders["wealth_order"]
        self.health_map = encoders["health_order"]

    def _preprocess_row(self, row: pd.Series) -> np.ndarray:
        conds = str(row.get("pre_existing_conditions", ""))
        cond_count = sum(
            1
            for c in [
                "Hypertension",
                "Diabetes",
                "Heart Disease",
                "COPD/Asthma",
                "Arthritis",
                "TB",
                "Hepatitis B",
            ]
            if c in conds
        )
        x = np.array(
            [
                row["age"],
                1 if str(row.get("gender", "")).lower() == "female" else 0,
                row["bmi"],
                row["is_smoking"],
                row["alcohol_use"],
                row["is_exercise"],
                row["has_family_history"],
                row["monthly_income_usd"],
                cond_count,
                int("Hypertension" in conds),
                int("Diabetes" in conds),
                int("Heart Disease" in conds),
                int("COPD/Asthma" in conds),
                int("Arthritis" in conds),
                int("TB" in conds),
                int("Hepatitis B" in conds),
                self.region_le.transform([row["region"]])[0],
                self.occ_le.transform([row["occupation"]])[0],
                self.edu_map.get(row.get("education", "Primary"), 1),
                self.wealth_map.get(row.get("wealth_quintile", "Middle"), 2),
                self.health_map.get(row.get("self_reported_health", "Fair"), 1),
            ],
            dtype=float,
        )
        return x.reshape(1, -1)

    def select_action(self, context: np.ndarray, row: pd.Series | None = None) -> int:
        if row is not None:
            mort_pred = self.model.predict(self._preprocess_row(row))[0]
        else:
            mort_pred = self.model.predict(context.reshape(1, -1))[0]
        if mort_pred <= 1.5:
            return ACTION_STANDARD
        if mort_pred <= 2.2:
            return ACTION_RATED
        if mort_pred <= 2.6:
            return ACTION_REFER
        return ACTION_DECLINE

    def update(self, action: int, context: np.ndarray, reward: float) -> None:
        pass


def train_fresh_xgb(df_raw: pd.DataFrame, n: int, seed: int) -> xgb.XGBRegressor:
    """Train an XGBoost regressor on the first *n* rows of *df_raw*."""
    df = df_raw.copy()
    conditions = [
        "Hypertension",
        "Diabetes",
        "Heart Disease",
        "COPD/Asthma",
        "Arthritis",
        "TB",
        "Hepatitis B",
    ]
    for cond in conditions:
        col = f"has_{cond.lower().replace('/', '_').replace(' ', '_')}"
        df[col] = df["pre_existing_conditions"].fillna("").str.contains(cond, regex=False).astype(int)
    df["condition_count"] = df[[f"has_{c.lower().replace('/', '_').replace(' ', '_')}" for c in conditions]].sum(axis=1)

    with open(MODELS_DIR / "cambodia_encoders.pkl", "rb") as f:
        encoders = pickle.load(f)
    df["region_enc"] = encoders["region"].transform(df["region"])
    df["occupation_enc"] = encoders["occupation"].transform(df["occupation"])
    df["gender_female"] = (df["gender"].str.lower() == "female").astype(int)
    df["education_enc"] = df["education"].map(encoders["edu_order"])
    df["wealth_enc"] = df["wealth_quintile"].map(encoders["wealth_order"])
    df["health_status_enc"] = df["self_reported_health"].map(encoders["health_order"])

    features = [
        "age", "gender_female", "bmi", "is_smoking", "alcohol_use", "is_exercise",
        "has_family_history", "monthly_income_usd", "condition_count",
        "has_hypertension", "has_diabetes", "has_heart_disease",
        "has_copd_asthma", "has_arthritis", "has_tb", "has_hepatitis_b",
        "region_enc", "occupation_enc",
        "education_enc", "wealth_enc", "health_status_enc",
    ]

    X = df[features].iloc[:n].values
    y = df["mortality_multiplier"].iloc[:n].values

    # Scale tree count to data size for speed
    n_est = 50 if n <= 500 else 100
    model = xgb.XGBRegressor(
        n_estimators=n_est,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=seed,
        verbosity=0,
    )
    model.fit(X, y)
    return model


def run(seed: int) -> dict[str, float]:
    """Run EXP-010 for a single seed and return scalar metrics."""
    X, df_raw, _features = preprocess_cambodia_data()
    n_features = X.shape[1]

    out: dict[str, float] = {}
    for t in TS:
        fresh_model = train_fresh_xgb(df_raw, t, seed)
        fresh_xgb = FreshXGBBaseline(fresh_model)

        algorithms = {
            "LinUCB": LinUCB(n_actions=4, n_features=n_features, alpha=BANDIT.linucb_alpha),
            "LinTS": LinTS(n_actions=4, n_features=n_features, v2=BANDIT.lints_v2, seed=seed),
            "FreshXGB": fresh_xgb,
        }

        for name, bandit in algorithms.items():
            result = run_bandit(name, bandit, X.copy(), df_raw, t, seed=seed)
            out[f"cum_reward_{name}_t{t}"] = float(result.cumulative_rewards[-1])
    return out


def plot_cold_start(results_by_t: dict, output_path: Path) -> None:
    """Plot cumulative reward vs T with crossover annotation."""
    fig, ax = plt.subplots(figsize=(8, 5))

    colors = {"LinUCB": "#2E5FA3", "LinTS": "#4CAF50", "FreshXGB": "#E53935"}
    markers = {"LinUCB": "o", "LinTS": "s", "FreshXGB": "^"}

    for name in ("LinUCB", "LinTS", "FreshXGB"):
        rewards = [results_by_t[t][name].cumulative_rewards[-1] for t in TS]
        ax.plot(
            TS, rewards, label=name, color=colors[name],
            marker=markers[name], markersize=8, linewidth=2,
        )

    # Find and annotate crossover points
    for bandit_name in ("LinUCB", "LinTS"):
        for i, t in enumerate(TS):
            if results_by_t[t][bandit_name].cumulative_rewards[-1] > results_by_t[t]["FreshXGB"].cumulative_rewards[-1]:
                cross_t = t
                cross_reward = results_by_t[t][bandit_name].cumulative_rewards[-1]
                ax.axvline(cross_t, color=colors[bandit_name], linestyle="--", alpha=0.4)
                break
        else:
            continue
        # Stagger annotations to avoid overlap
        if bandit_name == "LinUCB":
            xytext = (cross_t + 120, cross_reward - 2200)
        else:
            xytext = (cross_t - 350, cross_reward - 4500)
        ax.annotate(
            f"{bandit_name} crossover  T={cross_t}",
            xy=(cross_t, cross_reward),
            xytext=xytext,
            fontsize=9,
            arrowprops=dict(arrowstyle="->", color=colors[bandit_name]),
        )

    ax.set_xlabel("Horizon T (rounds)")
    ax.set_ylabel("Cumulative Reward ($)")
    ax.set_title("EXP-010: Cold-Start Analysis — Bandits vs Fresh Static XGB")
    ax.set_xticks(TS)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"  Saved plot: {output_path}")


def main() -> int:
    print("=" * 70)
    print("EXP-010: Cold-Start Analysis (10 seeds)")
    print("=" * 70)

    from experiment_utils import run_experiment_seeds_raw
    from scipy.stats import wilcoxon as _wilcoxon
    stats = run_experiment_seeds_raw(run, n_seeds=10)  # 10 by design — cold-start sweep is expensive

    def fmt(key: str) -> str:
        s = stats[key]
        return f"${s['mean']:>10,.0f} ± {s['std']:>8,.0f}"

    print("\n" + "-" * 70)
    print("Cumulative Reward by Horizon T (mean ± std over 10 seeds)")
    print("-" * 70)
    print(f"{'T':>6} {'LinUCB':>22} {'LinTS':>22} {'FreshXGB':>22}")
    print("-" * 70)
    for t in TS:
        print(
            f"{t:>6} {fmt(f'cum_reward_LinUCB_t{t}'):>22} "
            f"{fmt(f'cum_reward_LinTS_t{t}'):>22} {fmt(f'cum_reward_FreshXGB_t{t}'):>22}"
        )

    # Generate plot from seed=42
    print("\nGenerating plot for seed=42 ...")
    X, df_raw, _features = preprocess_cambodia_data()
    n_features = X.shape[1]
    results_by_t: dict[int, dict] = {}
    seed = 42
    for t in TS:
        fresh_model = train_fresh_xgb(df_raw, t, seed)
        fresh_xgb = FreshXGBBaseline(fresh_model)
        algorithms = {
            "LinUCB": LinUCB(n_actions=4, n_features=n_features, alpha=BANDIT.linucb_alpha),
            "LinTS": LinTS(n_actions=4, n_features=n_features, v2=BANDIT.lints_v2, seed=seed),
            "FreshXGB": fresh_xgb,
        }
        results_by_t[t] = {}
        for name, bandit in algorithms.items():
            results_by_t[t][name] = run_bandit(name, bandit, X.copy(), df_raw, t, seed=seed)

    figures_dir = ROOT / "thesis" / "health_rl" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    plot_cold_start(results_by_t, figures_dir / "fig_010_cold_start.png")

    print("\n" + "=" * 70)
    print("ASSERTIONS (mean-based, 10 seeds)")
    print("=" * 70)

    pass_total = True

    # Crossover: find first T where bandit mean reward > FreshXGB mean reward
    cross_ucb = None
    cross_ts = None
    for t in TS:
        if stats[f"cum_reward_LinUCB_t{t}"]["mean"] > stats[f"cum_reward_FreshXGB_t{t}"]["mean"]:
            cross_ucb = t
            break
    for t in TS:
        if stats[f"cum_reward_LinTS_t{t}"]["mean"] > stats[f"cum_reward_FreshXGB_t{t}"]["mean"]:
            cross_ts = t
            break

    check1 = cross_ucb is not None
    print(
        f"[{'PASS' if check1 else 'FAIL'}] LinUCB crossover exists "
        f"(beats FreshXGB at T={cross_ucb})"
    )
    pass_total &= check1

    check2 = cross_ts is not None
    print(
        f"[{'PASS' if check2 else 'FAIL'}] LinTS crossover exists "
        f"(beats FreshXGB at T={cross_ts})"
    )
    pass_total &= check2

    check3 = stats["cum_reward_LinUCB_t2000"]["mean"] > stats["cum_reward_FreshXGB_t2000"]["mean"]
    print(
        f"[{'PASS' if check3 else 'FAIL'}] LinUCB cumulative reward > FreshXGB at T=2000"
    )
    print(
        f"       LinUCB: ${stats['cum_reward_LinUCB_t2000']['mean']:,.0f}  "
        f"FreshXGB: ${stats['cum_reward_FreshXGB_t2000']['mean']:,.0f}"
    )
    pass_total &= check3

    check4 = stats["cum_reward_LinTS_t2000"]["mean"] > stats["cum_reward_FreshXGB_t2000"]["mean"]
    print(
        f"[{'PASS' if check4 else 'FAIL'}] LinTS cumulative reward > FreshXGB at T=2000"
    )
    print(
        f"       LinTS:  ${stats['cum_reward_LinTS_t2000']['mean']:,.0f}  "
        f"FreshXGB: ${stats['cum_reward_FreshXGB_t2000']['mean']:,.0f}"
    )
    pass_total &= check4

    # Paired Wilcoxon test on T=2000 crossover (10 CRN seeds)
    ucb_vals  = stats["cum_reward_LinUCB_t2000"]["values"]
    ts_vals   = stats["cum_reward_LinTS_t2000"]["values"]
    fresh_vals = stats["cum_reward_FreshXGB_t2000"]["values"]

    _, p_ucb = _wilcoxon(ucb_vals - fresh_vals)
    _, p_ts  = _wilcoxon(ts_vals  - fresh_vals)
    d_ucb = (ucb_vals - fresh_vals).mean() / (ucb_vals - fresh_vals).std(ddof=1)
    d_ts  = (ts_vals  - fresh_vals).mean() / (ts_vals  - fresh_vals).std(ddof=1)
    alpha_bc = 0.025  # Bonferroni-corrected for 2 comparisons

    print(f"\nPaired Wilcoxon T=2000 crossover significance (10 CRN seeds, alpha=0.025):")
    print(f"  LinUCB vs FreshXGB: p={p_ucb:.4f}, d={d_ucb:.2f}")
    print(f"  LinTS  vs FreshXGB: p={p_ts:.4f},  d={d_ts:.2f}")
    if p_ucb >= alpha_bc:
        print("  NOTE: LinUCB crossover not significant — soften 'Yes — bandits cross over' to 'bandits draw level' in Table 21")
    if p_ts >= alpha_bc:
        print("  NOTE: LinTS crossover not significant — soften similarly")

    print("\n" + "=" * 70)
    if pass_total:
        print("EXP-010: PASS")
        print("=" * 70)
        return 0
    else:
        print("EXP-010: FAIL")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
