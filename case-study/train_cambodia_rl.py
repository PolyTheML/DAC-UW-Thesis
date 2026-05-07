"""
Cambodia Case Study — Contextual Bandit RL Training
Algorithms: LinTS (Linear Thompson Sampling), LinUCB, EpsilonGreedy (baseline)
Environment: 3-arm insurance underwriting — Standard / Rated / Decline
Reward: profit-based with competitive-market acceptance probability on Rated arm
Outputs: models/cambodia_rl_results.json, cambodia_bandit_ts.pkl,
         cambodia_rl_trajectory.parquet
"""
import json
import pickle
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

warnings.filterwarnings("ignore")

SEED = 42
DATA_PATH = Path(__file__).parent / "cambodia_dataset.csv"
MODELS_DIR = Path(__file__).parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

# ── Environment parameters ──────────────────────────────────────────────────
# Reward calibrated so oracle gives ~20% Standard / 60% Rated / 20% Decline
# across Cambodia dataset (mean mortality_multiplier = 1.699).
# Acceptance on Rated arm follows a competitive-market response curve:
#   p(m) = clip(-0.30 + 0.55*m, 0.05, 0.85)
# Low-risk applicants (small m) have outside options → low acceptance of surcharge;
# high-risk applicants need coverage → high acceptance. See thesis Ch3 §3.4.
STANDARD, RATED, DECLINE = 0, 1, 2
N_ARMS = 3
P_STD        = 35.0   # standard premium
P_RATED      = 43.4   # rated premium
CLAIMS_COEFF = 20.0   # expected claims = CLAIMS_COEFF × mortality_multiplier
C_ACQ        = 3.0    # per-decision acquisition cost
CONV_STD     = 0.90   # standard-terms conversion rate
NOISE_BASE   = 2.0    # heteroskedastic noise floor
NOISE_SLOPE  = 1.5    # noise increases with risk

N_SEEDS = 10

# ── Feature definitions (must match train_cambodia_models.py) ────────────────
CONDITIONS = [
    "Hypertension", "Diabetes", "Heart Disease",
    "COPD/Asthma", "Arthritis", "TB", "Hepatitis B",
]

FEATURES = [
    "age", "gender_female", "bmi", "is_smoking", "is_exercise",
    "has_family_history", "monthly_income_usd", "condition_count",
    "has_hypertension", "has_diabetes", "has_heart_disease",
    "has_copd_asthma", "has_arthritis", "has_tb", "has_hepatitis_b",
    "region_enc", "occupation_enc",
]

CONTINUOUS_FEATURES = ["age", "bmi", "monthly_income_usd", "condition_count"]


# ── Feature engineering ──────────────────────────────────────────────────────

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    for cond in CONDITIONS:
        col = "has_" + cond.lower().replace("/", "_").replace(" ", "_")
        df[col] = (
            df["pre_existing_conditions"]
            .fillna("")
            .str.contains(cond, regex=False)
            .astype(int)
        )
    df["condition_count"] = df[
        ["has_" + c.lower().replace("/", "_").replace(" ", "_") for c in CONDITIONS]
    ].sum(axis=1)

    le_region = LabelEncoder().fit(df["region"])
    le_occ = LabelEncoder().fit(df["occupation"])
    df["region_enc"] = le_region.transform(df["region"])
    df["occupation_enc"] = le_occ.transform(df["occupation"])
    df["gender_female"] = (df["gender"].str.lower() == "female").astype(int)
    return df


# ── Environment ──────────────────────────────────────────────────────────────

def expected_reward(action: int, mort_mult: np.ndarray) -> np.ndarray:
    """Vectorized expected (noiseless) reward for one arm."""
    claims = CLAIMS_COEFF * mort_mult
    if action == STANDARD:
        return CONV_STD * (P_STD - claims) - C_ACQ
    if action == RATED:
        p = np.clip(-0.30 + 0.55 * mort_mult, 0.05, 0.85)
        return p * (P_RATED - claims) - C_ACQ
    return np.full_like(mort_mult, -1.0, dtype=float)  # DECLINE


def oracle_action(mort_mult_arr: np.ndarray) -> np.ndarray:
    """Clairvoyant optimal arm per applicant (uses true mortality_multiplier)."""
    R = np.stack([expected_reward(a, mort_mult_arr) for a in range(N_ARMS)], axis=1)
    return R.argmax(axis=1)


def oracle_expected_rewards(mort_mult_arr: np.ndarray) -> np.ndarray:
    """Expected reward of the oracle action for each applicant."""
    R = np.stack([expected_reward(a, mort_mult_arr) for a in range(N_ARMS)], axis=1)
    return R.max(axis=1)


def sample_reward(action: int, mort_mult: float, rng: np.random.Generator) -> float:
    """Stochastic observed reward with heteroskedastic Gaussian noise."""
    base = float(expected_reward(action, np.array([mort_mult]))[0])
    sigma = NOISE_BASE + NOISE_SLOPE * mort_mult
    return base + rng.normal(0.0, sigma)


# ── Bandit algorithms ────────────────────────────────────────────────────────

class LinTS:
    """
    Linear Thompson Sampling.
    Posterior: theta_a ~ N(A_a^{-1} b_a, A_a^{-1}).
    A_a^{-1} updated via Sherman-Morrison rank-1 formula (O(d²) per step).
    """

    def __init__(self, d: int, n_arms: int = N_ARMS, lam: float = 1.0):
        self.d = d
        self.n_arms = n_arms
        self.A_inv = [np.eye(d) / lam for _ in range(n_arms)]
        self.b = [np.zeros(d) for _ in range(n_arms)]

    def select(self, x: np.ndarray, rng: np.random.Generator) -> int:
        best_val, best_arm = -np.inf, 0
        for a in range(self.n_arms):
            mu = self.A_inv[a] @ self.b[a]
            try:
                L = np.linalg.cholesky(self.A_inv[a])
                theta = mu + L @ rng.standard_normal(self.d)
            except np.linalg.LinAlgError:
                theta = mu
            val = float(theta @ x)
            if val > best_val:
                best_val, best_arm = val, a
        return best_arm

    def update(self, a: int, x: np.ndarray, r: float) -> None:
        u = self.A_inv[a] @ x
        denom = 1.0 + float(x @ u)
        self.A_inv[a] -= np.outer(u, u) / denom
        self.b[a] += r * x


class LinUCB:
    """
    Linear UCB.
    UCB(a) = (A_a^{-1} b_a)^T x + alpha * sqrt(x^T A_a^{-1} x).
    """

    def __init__(
        self, d: int, n_arms: int = N_ARMS, alpha: float = 1.0, lam: float = 1.0
    ):
        self.d = d
        self.n_arms = n_arms
        self.alpha = alpha
        self.A_inv = [np.eye(d) / lam for _ in range(n_arms)]
        self.b = [np.zeros(d) for _ in range(n_arms)]

    def select(self, x: np.ndarray, rng: np.random.Generator = None) -> int:
        best_val, best_arm = -np.inf, 0
        for a in range(self.n_arms):
            mu = self.A_inv[a] @ self.b[a]
            bonus = self.alpha * np.sqrt(max(0.0, float(x @ self.A_inv[a] @ x)))
            val = float(mu @ x) + bonus
            if val > best_val:
                best_val, best_arm = val, a
        return best_arm

    def update(self, a: int, x: np.ndarray, r: float) -> None:
        u = self.A_inv[a] @ x
        denom = 1.0 + float(x @ u)
        self.A_inv[a] -= np.outer(u, u) / denom
        self.b[a] += r * x


class EpsilonGreedy:
    """
    Epsilon-greedy with per-arm online ridge regression.
    Greedy action = argmax mu_a^T x; explores with probability eps.
    """

    def __init__(
        self, d: int, n_arms: int = N_ARMS, eps: float = 0.10, lam: float = 1.0
    ):
        self.d = d
        self.n_arms = n_arms
        self.eps = eps
        self.A_inv = [np.eye(d) / lam for _ in range(n_arms)]
        self.b = [np.zeros(d) for _ in range(n_arms)]

    def select(self, x: np.ndarray, rng: np.random.Generator) -> int:
        if rng.random() < self.eps:
            return int(rng.integers(self.n_arms))
        means = [float((self.A_inv[a] @ self.b[a]) @ x) for a in range(self.n_arms)]
        return int(np.argmax(means))

    def update(self, a: int, x: np.ndarray, r: float) -> None:
        u = self.A_inv[a] @ x
        denom = 1.0 + float(x @ u)
        self.A_inv[a] -= np.outer(u, u) / denom
        self.b[a] += r * x


# ── Training loop ────────────────────────────────────────────────────────────

def run_bandit(
    agent_cls,
    agent_kwargs: dict,
    X: np.ndarray,
    mort_mult_arr: np.ndarray,
    n_seeds: int = N_SEEDS,
) -> dict:
    """
    Run bandit over n_seeds independent seeds.
    Each seed shuffles the dataset and processes all applicants once.
    Returns per-seed cumulative regret, reward, and action log.
    """
    d = X.shape[1]
    n = len(X)
    oracle_rew = oracle_expected_rewards(mort_mult_arr)

    cum_regret_all, cum_reward_all, action_log_all = [], [], []

    for seed in range(n_seeds):
        rng = np.random.default_rng(SEED + seed)
        agent = agent_cls(d=d, **agent_kwargs)

        order = rng.permutation(n)
        cum_regret, cum_reward = 0.0, 0.0
        regret_curve, reward_curve, actions = [], [], []

        for i in order:
            x = X[i]
            m = mort_mult_arr[i]

            a = agent.select(x, rng)
            r = sample_reward(a, m, rng)
            agent.update(a, x, r)

            # Instantaneous regret = oracle expected reward minus chosen expected reward
            regret = oracle_rew[i] - float(expected_reward(a, np.array([m]))[0])
            cum_regret += regret
            cum_reward += r
            regret_curve.append(cum_regret)
            reward_curve.append(cum_reward)
            actions.append(a)

        cum_regret_all.append(regret_curve)
        cum_reward_all.append(reward_curve)
        action_log_all.append(actions)

    return {
        "cum_regret": np.array(cum_regret_all),   # (n_seeds, n)
        "cum_reward": np.array(cum_reward_all),
        "action_log": np.array(action_log_all),
    }


def summarize(results: dict, name: str) -> dict:
    reg = results["cum_regret"]   # (seeds, n)
    rew = results["cum_reward"]
    acts = results["action_log"]

    final_reg = reg[:, -1]
    final_rew = rew[:, -1]

    # Action distribution over convergence window (last 20% of steps)
    n = acts.shape[1]
    tail = acts[:, int(0.80 * n):]
    action_dist = np.bincount(tail.flatten(), minlength=3) / tail.size

    return {
        "algorithm": name,
        "final_cumulative_regret": {
            "mean": round(float(final_reg.mean()), 2),
            "std":  round(float(final_reg.std()),  2),
            "min":  round(float(final_reg.min()),  2),
            "max":  round(float(final_reg.max()),  2),
        },
        "final_cumulative_reward": {
            "mean": round(float(final_rew.mean()), 2),
            "std":  round(float(final_rew.std()),  2),
        },
        "converged_action_dist": {
            "standard_pct": round(float(action_dist[0] * 100), 1),
            "rated_pct":    round(float(action_dist[1] * 100), 1),
            "decline_pct":  round(float(action_dist[2] * 100), 1),
        },
        "n_seeds": N_SEEDS,
    }


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Loading and preparing features...")
    df = pd.read_csv(DATA_PATH)
    df = build_features(df)

    mort_mult = df["mortality_multiplier"].values

    scaler = StandardScaler()
    X_raw = df[FEATURES].values.astype(float)
    cont_idx = [FEATURES.index(f) for f in CONTINUOUS_FEATURES]
    X_raw[:, cont_idx] = scaler.fit_transform(X_raw[:, cont_idx])

    # Append bias term → feature vector dimension = len(FEATURES) + 1
    X = np.hstack([X_raw, np.ones((len(X_raw), 1))])
    d = X.shape[1]
    n = len(X)

    print(f"  feature dim d={d}  applicants n={n}")

    oracle = oracle_action(mort_mult)
    oracle_counts = np.bincount(oracle, minlength=3)
    print(
        f"  Oracle: Standard={oracle_counts[0]} ({100*oracle_counts[0]/n:.1f}%)  "
        f"Rated={oracle_counts[1]} ({100*oracle_counts[1]/n:.1f}%)  "
        f"Decline={oracle_counts[2]} ({100*oracle_counts[2]/n:.1f}%)"
    )

    print(f"\nTraining {N_SEEDS} seeds per algorithm...")

    print("  LinTS...")
    ts_res = run_bandit(LinTS, {"lam": 1.0}, X, mort_mult)
    ts_sum = summarize(ts_res, "LinTS")

    print("  LinUCB...")
    ucb_res = run_bandit(LinUCB, {"alpha": 1.0, "lam": 1.0}, X, mort_mult)
    ucb_sum = summarize(ucb_res, "LinUCB")

    print("  EpsilonGreedy (eps=0.10)...")
    eg_res = run_bandit(EpsilonGreedy, {"eps": 0.10, "lam": 1.0}, X, mort_mult)
    eg_sum = summarize(eg_res, "EpsilonGreedy")

    print()
    for s in [ts_sum, ucb_sum, eg_sum]:
        print(
            f"  {s['algorithm']:16s}  regret={s['final_cumulative_regret']['mean']:7.1f}"
            f"  (+/-{s['final_cumulative_regret']['std']:.1f})"
            f"  converged: S={s['converged_action_dist']['standard_pct']:.1f}%"
            f"  R={s['converged_action_dist']['rated_pct']:.1f}%"
            f"  D={s['converged_action_dist']['decline_pct']:.1f}%"
        )

    # ── Save trained LinTS model (seed 0) ────────────────────────────────────
    print("\nSaving trained LinTS model (seed 0)...")
    rng0 = np.random.default_rng(SEED)
    final_ts = LinTS(d=d, lam=1.0)
    for i in rng0.permutation(n):
        x = X[i]; m = mort_mult[i]
        a = final_ts.select(x, rng0)
        r = sample_reward(a, m, rng0)
        final_ts.update(a, x, r)

    with open(MODELS_DIR / "cambodia_bandit_ts.pkl", "wb") as f:
        pickle.dump(
            {
                "model": final_ts,
                "scaler": scaler,
                "features": FEATURES,
                "continuous_features": CONTINUOUS_FEATURES,
                "feature_dim_with_bias": d,
                "env_params": {
                    "P_std": P_STD, "P_rated": P_RATED,
                    "claims_coeff": CLAIMS_COEFF, "c_acq": C_ACQ,
                    "conv_std": CONV_STD,
                },
            },
            f,
        )

    # ── Save per-step trajectory (seed 0, all 3 algorithms) ──────────────────
    print("Saving trajectory parquet (seed 0)...")
    traj_df = pd.DataFrame(
        {
            "step":          list(range(n)),
            "cum_regret_ts":  ts_res["cum_regret"][0].tolist(),
            "cum_regret_ucb": ucb_res["cum_regret"][0].tolist(),
            "cum_regret_eg":  eg_res["cum_regret"][0].tolist(),
            "cum_reward_ts":  ts_res["cum_reward"][0].tolist(),
            "cum_reward_ucb": ucb_res["cum_reward"][0].tolist(),
            "cum_reward_eg":  eg_res["cum_reward"][0].tolist(),
            "action_ts":  ts_res["action_log"][0].tolist(),
            "action_ucb": ucb_res["action_log"][0].tolist(),
            "action_eg":  eg_res["action_log"][0].tolist(),
        }
    )
    traj_df.to_parquet(MODELS_DIR / "cambodia_rl_trajectory.parquet", index=False)

    # ── Also save mean ± std regret curves (all seeds, for Ch4 figure) ───────
    mean_std_df = pd.DataFrame(
        {
            "step": list(range(n)),
            "ts_mean":  ts_res["cum_regret"].mean(axis=0).tolist(),
            "ts_std":   ts_res["cum_regret"].std(axis=0).tolist(),
            "ucb_mean": ucb_res["cum_regret"].mean(axis=0).tolist(),
            "ucb_std":  ucb_res["cum_regret"].std(axis=0).tolist(),
            "eg_mean":  eg_res["cum_regret"].mean(axis=0).tolist(),
            "eg_std":   eg_res["cum_regret"].std(axis=0).tolist(),
        }
    )
    mean_std_df.to_parquet(MODELS_DIR / "cambodia_rl_regret_curves.parquet", index=False)

    # ── Results JSON ─────────────────────────────────────────────────────────
    oracle_rew_total = float(oracle_expected_rewards(mort_mult).sum())
    eg_regret = eg_sum["final_cumulative_regret"]["mean"]
    ts_regret = ts_sum["final_cumulative_regret"]["mean"]
    regret_reduction = round((eg_regret - ts_regret) / max(eg_regret, 1) * 100, 1)

    results_out = {
        "environment": {
            "n_applicants": n,
            "n_arms": N_ARMS,
            "arm_labels": {0: "Standard", 1: "Rated", 2: "Decline"},
            "feature_dim_with_bias": d,
            "reward_params": {
                "P_std": P_STD, "P_rated": P_RATED,
                "claims_coeff": CLAIMS_COEFF, "c_acq": C_ACQ,
                "conv_std": CONV_STD,
                "noise_base": NOISE_BASE, "noise_slope": NOISE_SLOPE,
                "acceptance_curve": "p = clip(-0.30 + 0.55*m, 0.05, 0.85)",
                "s_to_r_boundary_mortality": 1.34,
                "r_to_d_boundary_mortality": 2.05,
            },
            "oracle_action_dist": {
                "standard_pct": round(100 * oracle_counts[0] / n, 1),
                "rated_pct":    round(100 * oracle_counts[1] / n, 1),
                "decline_pct":  round(100 * oracle_counts[2] / n, 1),
            },
            "oracle_total_expected_reward": round(oracle_rew_total, 2),
        },
        "algorithms": [ts_sum, ucb_sum, eg_sum],
        "regret_reduction_ts_vs_eg_pct": regret_reduction,
    }

    with open(MODELS_DIR / "cambodia_rl_results.json", "w") as f:
        json.dump(results_out, f, indent=2)

    print("\nDone. RL outputs saved to case-study/models/")
    print(json.dumps(results_out, indent=2))
