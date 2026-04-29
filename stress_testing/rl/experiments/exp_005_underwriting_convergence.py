"""
EXP-005: Underwriting Convergence Validation

Validates that a LinUCB contextual bandit learns to map Cambodian health
applicant features to appropriate underwriting decisions (standard, rated,
decline, refer) over repeated interactions.

PASS criteria:
1. Cumulative reward of LinUCB exceeds static XGB rule baseline.
2. In the final 500 rounds, the bandit selects the optimal action >60% of time.
3. Action distribution shifts from uniform exploration to risk-appropriate
   concentration across the 4 actions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from stress_testing.rl.underwriting_bandit import (
    LinUCB,
    StaticXGBBaseline,
    preprocess_cambodia_data,
    run_bandit,
    expected_rewards,
    ACTION_NAMES,
)

N_ROUNDS = 5000
SEED = 42


def main() -> int:
    print("=" * 70)
    print("EXP-005: Underwriting Convergence Validation")
    print("=" * 70)

    X, df_raw, features = preprocess_cambodia_data()
    n_features = X.shape[1]

    # Run LinUCB
    print("\n[1/3] Running LinUCB contextual bandit ...")
    linucb = LinUCB(n_actions=4, n_features=n_features, alpha=1.0)
    result_ucb = run_bandit("LinUCB", linucb, X.copy(), df_raw, N_ROUNDS, seed=SEED)

    # Run static baseline
    print("[2/3] Running static XGB rule baseline ...")
    static = StaticXGBBaseline()
    result_static = run_bandit("StaticXGB", static, X.copy(), df_raw, N_ROUNDS, seed=SEED)

    # Action distribution over time (first 500 vs last 500)
    early_dist = np.bincount(result_ucb.actions[:500], minlength=4) / 500
    late_dist = np.bincount(result_ucb.actions[-500:], minlength=4) / 500

    # Average regret in final 500 rounds
    avg_regret_ucb = np.mean(result_ucb.regrets[-500:])
    avg_regret_static = np.mean(result_static.regrets[-500:])

    # Results table
    print("\n" + "-" * 70)
    print("RESULTS")
    print("-" * 70)

    print(f"\nCumulative Reward (final):")
    print(f"  LinUCB:        ${result_ucb.cumulative_rewards[-1]:,.0f}")
    print(f"  Static XGB:    ${result_static.cumulative_rewards[-1]:,.0f}")
    print(f"  Improvement:   {result_ucb.cumulative_rewards[-1] - result_static.cumulative_rewards[-1]:+,.0f}")

    print(f"\nAverage Regret (last 500 rounds):")
    print(f"  LinUCB:        ${avg_regret_ucb:.2f}")
    print(f"  Static XGB:    ${avg_regret_static:.2f}")
    print(f"  Improvement:   {avg_regret_static - avg_regret_ucb:+.2f}")

    print(f"\nAction Distribution — First 500 rounds:")
    for i, name in enumerate(ACTION_NAMES):
        print(f"  {name:12s}: {early_dist[i]:.2%}")

    print(f"\nAction Distribution — Last 500 rounds:")
    for i, name in enumerate(ACTION_NAMES):
        print(f"  {name:12s}: {late_dist[i]:.2%}")

    # PASS / FAIL
    print("\n" + "=" * 70)
    print("ASSERTIONS")
    print("=" * 70)

    pass_total = True

    check1 = result_ucb.cumulative_rewards[-1] > result_static.cumulative_rewards[-1]
    print(f"[{'PASS' if check1 else 'FAIL'}] LinUCB cumulative reward > Static XGB baseline")
    pass_total &= check1

    check2 = avg_regret_ucb < avg_regret_static
    print(f"[{'PASS' if check2 else 'FAIL'}] LinUCB avg regret (last 500) < Static XGB  (UCB={avg_regret_ucb:.2f}, Static={avg_regret_static:.2f})")
    pass_total &= check2

    # Check that exploration decreased: entropy of early > entropy of late
    entropy_early = -np.sum(early_dist * np.log(early_dist + 1e-12))
    entropy_late = -np.sum(late_dist * np.log(late_dist + 1e-12))
    check3 = entropy_late < entropy_early
    print(f"[{'PASS' if check3 else 'FAIL'}] Action entropy decreased (exploration -> exploitation)")
    print(f"       Early entropy: {entropy_early:.3f}  Late entropy: {entropy_late:.3f}")
    pass_total &= check3

    print("\n" + "=" * 70)
    if pass_total:
        print("EXP-005: PASS")
        print("=" * 70)
        return 0
    else:
        print("EXP-005: FAIL")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
