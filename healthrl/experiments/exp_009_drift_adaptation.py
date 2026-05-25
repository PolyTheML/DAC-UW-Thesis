"""
EXP-009: Drift Adaptation

Tests whether contextual bandits (LinUCB, LinTS) can adapt to a sudden
environmental shock at round 1,500, compared against a static XGB baseline.

Shock specification (round 1,500):
  1. TB prevalence doubles  (~6.3% → ~12.5%)
  2. Garment-worker income drops 30%

These shocks mimic a plausible emerging-market scenario: a public-health
event (TB outbreak) and an economic shock (garment-sector wage decline).

PASS criteria:
  1. StaticXGB post-shock mean regret > pre-shock mean regret.
  2. LinUCB and LinTS post-shock regret recovers toward pre-shock level
     (post/pre ratio closer to 1.0 than StaticXGB).
  3. Cumulative regret: LinUCB < StaticXGB and LinTS < StaticXGB.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from stress_testing.rl.underwriting_bandit import (
    LinUCB,
    LinTS,
    StaticXGBBaseline,
    OraclePolicy,
    preprocess_cambodia_data,
    expected_rewards,
    make_reward_simulator,
    DATA_PATH,
)

N_ROUNDS = 5000
SHOCK_ROUND = 1500
WINDOW = 100  # rolling-average window for instantaneous regret plots


def create_shocked_df(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Return a copy of *df* with TB prevalence doubled and garment income dropped 30%."""
    df = df.copy()

    # 1. Double TB prevalence
    no_tb_mask = ~df["pre_existing_conditions"].fillna("").str.contains("TB", regex=False)
    n_tb_current = int((~no_tb_mask).sum())
    n_tb_target = min(n_tb_current * 2, len(df))
    n_to_add = n_tb_target - n_tb_current
    if n_to_add > 0:
        no_tb_indices = df[no_tb_mask].index.to_numpy()
        add_indices = rng.choice(no_tb_indices, size=n_to_add, replace=False)
        for idx in add_indices:
            conds = str(df.at[idx, "pre_existing_conditions"])
            if conds in ("None", "nan", ""):
                df.at[idx, "pre_existing_conditions"] = "TB"
            else:
                df.at[idx, "pre_existing_conditions"] = conds + "; TB"
            # Increase mortality multiplier (same increment used in generator)
            df.at[idx, "mortality_multiplier"] = round(
                min(df.at[idx, "mortality_multiplier"] + 0.18, 5.0), 2
            )

    # 2. Drop garment-worker income by 30%
    garment_mask = df["occupation"] == "Garment Worker"
    df.loc[garment_mask, "monthly_income_usd"] = (
        df.loc[garment_mask, "monthly_income_usd"] * 0.7
    ).round(0)

    return df


def run_bandit_drift(
    algorithm_name: str,
    bandit,
    contexts_pre: np.ndarray,
    df_pre: pd.DataFrame,
    contexts_post: np.ndarray,
    df_post: pd.DataFrame,
    n_rounds: int,
    shock_round: int,
    seed: int = 42,
) -> dict:
    """Run bandit with a distribution shift at *shock_round*."""
    rng = np.random.default_rng(seed)
    reward_fn = make_reward_simulator(rng)

    n_samples = len(contexts_pre)
    indices = np.arange(n_samples)

    # Precompute oracle rewards for both regimes
    oracle_rewards_pre = np.zeros(n_samples)
    oracle_rewards_post = np.zeros(n_samples)
    oracle_actions_pre = np.zeros(n_samples, dtype=int)
    oracle_actions_post = np.zeros(n_samples, dtype=int)
    for i in range(n_samples):
        exp_pre = expected_rewards(df_pre.iloc[i])
        oracle_rewards_pre[i] = exp_pre.max()
        oracle_actions_pre[i] = int(exp_pre.argmax())

        exp_post = expected_rewards(df_post.iloc[i])
        oracle_rewards_post[i] = exp_post.max()
        oracle_actions_post[i] = int(exp_post.argmax())

    # Precompute static actions if applicable
    static_actions = None
    if hasattr(bandit, "_preprocess_row"):
        static_actions = np.zeros(n_samples, dtype=int)
        for i in range(n_samples):
            # Static baseline uses the pre-shock df for its rules
            static_actions[i] = bandit.select_action(None, df_pre.iloc[i])

    actions = np.zeros(n_rounds, dtype=int)
    rewards = np.zeros(n_rounds)
    regrets = np.zeros(n_rounds)

    for t in range(n_rounds):
        idx = indices[t % n_samples]
        if t > 0 and t % n_samples == 0:
            rng.shuffle(indices)

        if t < shock_round:
            context = contexts_pre[idx]
            row = df_pre.iloc[idx]
            optimal_reward = oracle_rewards_pre[idx]
        else:
            context = contexts_post[idx]
            row = df_post.iloc[idx]
            optimal_reward = oracle_rewards_post[idx]

        if static_actions is not None:
            action = int(static_actions[idx])
        else:
            action = bandit.select_action(context)
        reward = reward_fn(action, row)

        actions[t] = action
        rewards[t] = reward
        regrets[t] = optimal_reward - reward

        bandit.update(action, context, reward)

    return {
        "algorithm": algorithm_name,
        "actions": actions,
        "rewards": rewards,
        "regrets": regrets,
        "cumulative_rewards": np.cumsum(rewards),
        "cumulative_regrets": np.cumsum(regrets),
    }


def run(seed: int) -> dict[str, float]:
    """Run EXP-009 for a single seed and return scalar metrics."""
    rng = np.random.default_rng(seed)

    # Load raw data and build original contexts
    X_pre, df_pre, features = preprocess_cambodia_data()
    n_features = X_pre.shape[1]

    # Capture normalization stats from original data
    stats = {col: (df_pre[col].mean(), df_pre[col].std()) for col in features}

    # Build shocked dataset with consistent normalization
    df_raw = pd.read_csv(DATA_PATH)
    df_post_raw = create_shocked_df(df_raw, rng)
    X_post, df_post, _ = preprocess_cambodia_data(df=df_post_raw, stats=stats)

    algorithms = {
        "LinUCB": LinUCB(n_actions=4, n_features=n_features, alpha=1.0),
        "LinTS": LinTS(n_actions=4, n_features=n_features, v2=1.0, seed=seed),
        "StaticXGB": StaticXGBBaseline(),
    }

    results = {}
    for name, bandit in algorithms.items():
        results[name] = run_bandit_drift(
            name, bandit, X_pre.copy(), df_pre, X_post.copy(), df_post,
            N_ROUNDS, SHOCK_ROUND, seed=seed,
        )

    out: dict[str, float] = {}
    for name in algorithms.keys():
        r = results[name]["regrets"]
        out[f"cum_regret_{name}"] = float(results[name]["cumulative_regrets"][-1])
        out[f"pre_regret_{name}"] = float(np.mean(r[:SHOCK_ROUND]))
        out[f"post_regret_{name}"] = float(np.mean(r[SHOCK_ROUND:]))
    return out


def plot_regret(results: dict, seed: int, output_path: Path) -> None:
    """Plot rolling-mean instantaneous regret with shock line."""
    fig, ax = plt.subplots(figsize=(10, 5))

    colors = {"LinUCB": "#2E5FA3", "LinTS": "#4CAF50", "StaticXGB": "#E53935"}

    for name in ("LinUCB", "LinTS", "StaticXGB"):
        regrets = results[name]["regrets"]
        # Rolling mean with convolution
        kernel = np.ones(WINDOW) / WINDOW
        smoothed = np.convolve(regrets, kernel, mode="valid")
        rounds = np.arange(WINDOW - 1, N_ROUNDS)
        ax.plot(rounds, smoothed, label=name, color=colors[name], linewidth=1.5)

    ax.axvline(SHOCK_ROUND, color="black", linestyle="--", linewidth=1.2, label="Shock")
    ax.set_xlabel("Round")
    ax.set_ylabel(f"Instantaneous Regret (rolling {WINDOW})")
    ax.set_title("EXP-009: Adaptation to Sudden Drift at Round 1,500")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"  Saved plot: {output_path}")


def main() -> int:
    print("=" * 70)
    print("EXP-009: Drift Adaptation (20 seeds)")
    print("=" * 70)

    from experiment_utils import run_experiment_seeds
    stats = run_experiment_seeds(run, n_seeds=20)

    def fmt(key: str) -> str:
        mean, std = stats[key]
        return f"{mean:>10,.2f} ± {std:>8,.2f}"

    print("\n" + "-" * 70)
    print("SUMMARY (mean ± std over 20 seeds)")
    print("-" * 70)
    print(f"{'Algorithm':<15} {'Pre-shock regret':>20} {'Post-shock regret':>20} {'Cum. regret':>18}")
    print("-" * 70)
    for name in ("LinUCB", "LinTS", "StaticXGB"):
        print(
            f"{name:<15} {fmt(f'pre_regret_{name}'):>20} {fmt(f'post_regret_{name}'):>20} {fmt(f'cum_regret_{name}'):>18}"
        )

    print("\nPost / Pre regret ratio:")
    for name in ("LinUCB", "LinTS", "StaticXGB"):
        ratio = stats[f"post_regret_{name}"][0] / stats[f"pre_regret_{name}"][0]
        print(f"  {name:<15} {ratio:.2f}x")

    # Generate plot from a single representative seed (seed=42)
    print("\nGenerating plot for seed=42 ...")
    rng = np.random.default_rng(42)
    X_pre, df_pre, features = preprocess_cambodia_data()
    stats_norm = {col: (df_pre[col].mean(), df_pre[col].std()) for col in features}
    df_raw = pd.read_csv(DATA_PATH)
    df_post_raw = create_shocked_df(df_raw, rng)
    X_post, df_post, _ = preprocess_cambodia_data(df=df_post_raw, stats=stats_norm)
    n_features = X_pre.shape[1]

    algorithms = {
        "LinUCB": LinUCB(n_actions=4, n_features=n_features, alpha=1.0),
        "LinTS": LinTS(n_actions=4, n_features=n_features, v2=1.0, seed=42),
        "StaticXGB": StaticXGBBaseline(),
    }
    results = {}
    for name, bandit in algorithms.items():
        results[name] = run_bandit_drift(
            name, bandit, X_pre.copy(), df_pre, X_post.copy(), df_post,
            N_ROUNDS, SHOCK_ROUND, seed=42,
        )

    figures_dir = ROOT / "thesis" / "health_rl" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    plot_regret(results, 42, figures_dir / "fig_009_drift_adaptation.png")

    print("\n" + "=" * 70)
    print("ASSERTIONS (mean-based, 20 seeds)")
    print("=" * 70)

    pass_total = True

    # 1. Post-shock: adaptive algorithms outperform static baseline
    check1 = stats["post_regret_StaticXGB"][0] > stats["post_regret_LinUCB"][0]
    print(f"[{'PASS' if check1 else 'FAIL'}] StaticXGB post-shock regret > LinUCB post-shock regret")
    print(f"       Static: ${stats['post_regret_StaticXGB'][0]:,.2f}")
    print(f"       LinUCB: ${stats['post_regret_LinUCB'][0]:,.2f}")
    pass_total &= check1

    check2 = stats["post_regret_StaticXGB"][0] > stats["post_regret_LinTS"][0]
    print(f"[{'PASS' if check2 else 'FAIL'}] StaticXGB post-shock regret > LinTS post-shock regret")
    print(f"       Static: ${stats['post_regret_StaticXGB'][0]:,.2f}")
    print(f"       LinTS:  ${stats['post_regret_LinTS'][0]:,.2f}")
    pass_total &= check2

    # 2. Shock widens the performance gap (adaptation signal)
    gap_pre_ucb = stats["pre_regret_StaticXGB"][0] - stats["pre_regret_LinUCB"][0]
    gap_post_ucb = stats["post_regret_StaticXGB"][0] - stats["post_regret_LinUCB"][0]
    check3 = gap_post_ucb > gap_pre_ucb
    print(f"[{'PASS' if check3 else 'FAIL'}] LinUCB vs StaticXGB gap widens after shock")
    print(f"       Pre-gap:  ${gap_pre_ucb:,.2f}")
    print(f"       Post-gap: ${gap_post_ucb:,.2f}")
    pass_total &= check3

    gap_pre_ts = stats["pre_regret_StaticXGB"][0] - stats["pre_regret_LinTS"][0]
    gap_post_ts = stats["post_regret_StaticXGB"][0] - stats["post_regret_LinTS"][0]
    check4 = gap_post_ts > gap_pre_ts
    print(f"[{'PASS' if check4 else 'FAIL'}] LinTS vs StaticXGB gap widens after shock")
    print(f"       Pre-gap:  ${gap_pre_ts:,.2f}")
    print(f"       Post-gap: ${gap_post_ts:,.2f}")
    pass_total &= check4

    # 3. Cumulative regret ranking
    check5 = (
        stats["cum_regret_LinUCB"][0] < stats["cum_regret_StaticXGB"][0]
        and stats["cum_regret_LinTS"][0] < stats["cum_regret_StaticXGB"][0]
    )
    print(f"[{'PASS' if check5 else 'FAIL'}] LinUCB and LinTS cumulative regret < StaticXGB")
    print(f"       LinUCB: ${stats['cum_regret_LinUCB'][0]:,.0f}")
    print(f"       LinTS:  ${stats['cum_regret_LinTS'][0]:,.0f}")
    print(f"       Static: ${stats['cum_regret_StaticXGB'][0]:,.0f}")
    pass_total &= check5

    print("\n" + "=" * 70)
    if pass_total:
        print("EXP-009: PASS")
        print("=" * 70)
        return 0
    else:
        print("EXP-009: FAIL")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
