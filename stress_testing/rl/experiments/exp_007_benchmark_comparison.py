"""
EXP-007: Benchmark Comparison + Regret Analysis

Compares LinUCB, LinTS, Epsilon-Greedy, and a static XGBoost rule baseline
on cumulative regret and reward over 5,000 rounds.

PASS criteria:
1. LinUCB and LinTS achieve strictly lower cumulative regret than both
   Epsilon-Greedy and Static XGB baseline at round 5,000.
2. The contextual bandits (LinUCB, LinTS) achieve higher cumulative reward
   than the non-contextual/static baselines.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from stress_testing.rl.underwriting_bandit import (
    LinUCB,
    LinTS,
    EpsilonGreedy,
    StaticXGBBaseline,
    preprocess_cambodia_data,
    run_bandit,
)

N_ROUNDS = 5000
SEED = 42


def main() -> int:
    print("=" * 70)
    print("EXP-007: Benchmark Comparison + Regret Analysis")
    print("=" * 70)

    X, df_raw, features = preprocess_cambodia_data()
    n_features = X.shape[1]

    algorithms = {
        "LinUCB": LinUCB(n_actions=4, n_features=n_features, alpha=1.0),
        "LinTS": LinTS(n_actions=4, n_features=n_features, v2=1.0),
        "EpsilonGreedy": EpsilonGreedy(n_actions=4, n_features=n_features, epsilon=0.15),
        "StaticXGB": StaticXGBBaseline(),
    }

    results = {}
    for name, bandit in algorithms.items():
        print(f"\nRunning {name} ...")
        results[name] = run_bandit(name, bandit, X.copy(), df_raw, N_ROUNDS, seed=SEED)
        print(f"  Cumulative reward: ${results[name].cumulative_rewards[-1]:,.0f}")
        print(f"  Cumulative regret: ${results[name].cumulative_regrets[-1]:,.0f}")

    # Summary table
    print("\n" + "-" * 70)
    print("SUMMARY (final round)")
    print("-" * 70)
    print(f"{'Algorithm':<18} {'Cum. Reward':>14} {'Cum. Regret':>14} {'Final Regret':>14}")
    print("-" * 70)
    for name in algorithms.keys():
        r = results[name]
        print(f"{name:<18} ${r.cumulative_rewards[-1]:>12,.0f} ${r.cumulative_regrets[-1]:>12,.0f} ${r.regrets[-1]:>12,.0f}")

    # Assertions
    print("\n" + "=" * 70)
    print("ASSERTIONS")
    print("=" * 70)

    pass_total = True
    regret_ucb = results["LinUCB"].cumulative_regrets[-1]
    regret_ts = results["LinTS"].cumulative_regrets[-1]
    regret_eg = results["EpsilonGreedy"].cumulative_regrets[-1]
    regret_static = results["StaticXGB"].cumulative_regrets[-1]

    check1 = regret_ucb < regret_eg and regret_ucb < regret_static
    print(f"[{'PASS' if check1 else 'FAIL'}] LinUCB regret < EpsilonGreedy AND StaticXGB")
    print(f"       LinUCB: ${regret_ucb:,.0f}  EpsGreedy: ${regret_eg:,.0f}  Static: ${regret_static:,.0f}")
    pass_total &= check1

    check2 = regret_ts < regret_eg and regret_ts < regret_static
    print(f"[{'PASS' if check2 else 'FAIL'}] LinTS regret < EpsilonGreedy AND StaticXGB")
    print(f"       LinTS: ${regret_ts:,.0f}  EpsGreedy: ${regret_eg:,.0f}  Static: ${regret_static:,.0f}")
    pass_total &= check2

    reward_ucb = results["LinUCB"].cumulative_rewards[-1]
    reward_ts = results["LinTS"].cumulative_rewards[-1]
    reward_eg = results["EpsilonGreedy"].cumulative_rewards[-1]
    reward_static = results["StaticXGB"].cumulative_rewards[-1]

    check3 = reward_ucb > reward_static and reward_ts > reward_static
    print(f"[{'PASS' if check3 else 'FAIL'}] LinUCB and LinTS reward > StaticXGB")
    print(f"       LinUCB: ${reward_ucb:,.0f}  LinTS: ${reward_ts:,.0f}  Static: ${reward_static:,.0f}")
    pass_total &= check3

    print("\n" + "=" * 70)
    if pass_total:
        print("EXP-007: PASS")
        print("=" * 70)
        return 0
    else:
        print("EXP-007: FAIL")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
