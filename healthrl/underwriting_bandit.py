"""
Core underwriting bandit module.

Implements contextual bandit algorithms for adaptive health insurance underwriting:
- LinUCB (Li et al. 2010)
- Linear Thompson Sampling (Agrawal & Goyal 2013)
- Epsilon-Greedy

Also includes:
- Cambodia dataset preprocessor (CDHS 2021-22 anchored features)
- Actuarial reward simulator (4 actions: standard, rated, decline, refer)
- Static XGBoost baseline for benchmarking
"""
from __future__ import annotations

import json
import pickle
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

ROOT = Path(__file__).parent.parent
DATA_PATH = ROOT / "data" / "cambodia" / "cambodia_dataset.csv"
MODELS_DIR = ROOT / "data" / "cambodia" / "models"

# ── Actions ────────────────────────────────────────────────────────────────
ACTION_STANDARD = 0
ACTION_RATED = 1
ACTION_DECLINE = 2
ACTION_REFER = 3
ACTION_NAMES = ["STANDARD", "RATED", "DECLINE", "REFER"]

# ── Data preprocessor ──────────────────────────────────────────────────────

def preprocess_cambodia_data(
    df: pd.DataFrame | None = None,
    stats: dict[str, tuple[float, float]] | None = None,
) -> tuple[np.ndarray, pd.DataFrame, list[str]]:
    """Load Cambodia dataset and return feature matrix X, raw DataFrame, feature names.

    Feature engineering mirrors the training script (train_cambodia_models.py)
    but uses one-hot encoding for region and occupation (better for linear bandits).
    Ordinal encodings are used for education, wealth, and self-reported health.

    Args:
        df: Optional DataFrame to process instead of loading from CSV.
        stats: Optional dict of {feature: (mean, std)} for consistent
               normalization across multiple datasets (e.g., drift experiments).
    """
    if df is None:
        df = pd.read_csv(DATA_PATH)

    conditions = ["Hypertension", "Diabetes", "Heart Disease", "COPD/Asthma", "Arthritis", "TB", "Hepatitis B"]
    for cond in conditions:
        col = f"has_{cond.lower().replace('/', '_').replace(' ', '_')}"
        df[col] = df["pre_existing_conditions"].fillna("").str.contains(cond, regex=False).astype(int)

    df["condition_count"] = df[[f"has_{c.lower().replace('/', '_').replace(' ', '_')}" for c in conditions]].sum(axis=1)

    # One-hot encode region and occupation (critical for linear models)
    region_dummies = pd.get_dummies(df["region"], prefix="region")
    occ_dummies = pd.get_dummies(df["occupation"], prefix="occ")
    df = pd.concat([df, region_dummies, occ_dummies], axis=1)

    # Ordinal encodings for CDHS social-determinant features
    df["gender_female"] = (df["gender"].str.lower() == "female").astype(int)
    df["education_enc"] = df["education"].map({"No education": 0, "Primary": 1, "Secondary": 2, "Higher": 3})
    df["wealth_enc"] = df["wealth_quintile"].map({"Poorest": 0, "Poorer": 1, "Middle": 2, "Richer": 3, "Richest": 4})
    df["health_status_enc"] = df["self_reported_health"].map({"Poor": 0, "Fair": 1, "Good": 2})

    features = (
        ["age", "gender_female", "bmi", "is_smoking", "alcohol_use", "is_exercise",
         "has_family_history", "monthly_income_usd", "condition_count",
         "education_enc", "wealth_enc", "health_status_enc"]
        + [f"has_{c.lower().replace('/', '_').replace(' ', '_')}" for c in conditions]
        + list(region_dummies.columns)
        + list(occ_dummies.columns)
    )

    # Normalize all features to mean 0, std 1 for linear bandits
    X = df[features].copy().astype(float)
    for col in features:
        if stats is not None:
            mean, std = stats[col]
        else:
            mean, std = X[col].mean(), X[col].std()
        X[col] = (X[col] - mean) / (std if std > 0 else 1)

    return X.values, df, features


# ── Reward simulator configuration ───────────────────────────────────────────

@dataclass(frozen=True)
class RewardConfig:
    """Actuarial parameters for the underwriting reward simulator.

    Defaults reproduce the original simple model.  Use ``RewardConfig.realistic()``
    for a richer model that includes expense loadings, lapse probability, and
    customer-lifetime-value scaling.
    """

    # Revenue & risk
    base_premium_rate: float = 200.0
    expected_claims_rate: float = 150.0

    # Expense loading
    expense_fixed: float = 0.0          # fixed acquisition/admin cost per accepted policy
    expense_ratio: float = 0.0          # variable expense as fraction of premium

    # Persistency / CLV
    lapse_prob: float = 0.0             # probability of mid-year cancellation
    lapse_premium_factor: float = 0.5   # fraction of premium collected if lapse
    lapse_claims_factor: float = 0.5    # fraction of claims paid if lapse
    clv_multiplier: float = 1.0         # expected policy lifetime multiplier

    # Adverse selection
    adverse_threshold: float = 2.0
    adverse_factor: float = 1.35

    # Customer acceptance
    acceptance_intercept: float = 0.95
    acceptance_slope: float = 3.5
    min_acceptance: float = 0.05

    # Stochastic claims noise
    claims_noise_low: float = 0.92
    claims_noise_high: float = 1.08

    # Action costs
    decline_cost: float = -10.0
    refer_efficiency: float = 0.70
    refer_admin_cost: float = 35.0
    walk_cost: float = -20.0            # cost when customer walks in stochastic sim
    processing_cost: float = -25.0      # cost used in expected-value calculations

    @classmethod
    def realistic(cls) -> "RewardConfig":
        """Return a config with expense loading, lapse, and CLV enabled."""
        return cls(
            expense_fixed=25.0,
            expense_ratio=0.05,
            lapse_prob=0.08,
            clv_multiplier=2.5,
        )


# ── Reward simulator ───────────────────────────────────────────────────────

def _compute_reward(
    action: int,
    row: pd.Series,
    config: RewardConfig,
    rng: np.random.Generator | None,
    customer_accepted: bool | None,
    acceptance_draw: float | None = None,
    claims_noise_mult: float | None = None,
) -> float:
    """Shared reward computation for stochastic and deterministic modes.

    Optional *acceptance_draw* and *claims_noise_mult* enable common random
    numbers: the caller pre-generates these arrays so that multiple algorithm
    runs see identical noise conditioned on the round index.
    """
    mort = row["mortality_multiplier"]
    income = row["monthly_income_usd"]

    base_premium = config.base_premium_rate * mort
    expected_claims = config.expected_claims_rate * mort
    adverse_factor = 1.0 if mort <= config.adverse_threshold else config.adverse_factor

    def p_accept(premium: float) -> float:
        ratio = (premium / 12) / income
        return max(config.min_acceptance, config.acceptance_intercept - config.acceptance_slope * ratio)

    p_std = p_accept(base_premium)
    p_rtd = p_accept(base_premium * 1.25)

    def _claims_noise() -> float:
        if claims_noise_mult is not None:
            return claims_noise_mult
        if rng is not None:
            return rng.uniform(config.claims_noise_low, config.claims_noise_high)
        return 1.0

    def _expenses(premium: float) -> float:
        return config.expense_fixed + config.expense_ratio * premium

    def _net(premium: float, claims: float, expenses: float) -> float:
        if rng is not None:
            # Stochastic lapse draw
            if rng.random() < config.lapse_prob:
                return (
                    config.lapse_premium_factor * premium
                    - config.lapse_claims_factor * claims
                    - expenses
                ) * config.clv_multiplier
        elif config.lapse_prob > 0:
            # Expected-value mode for lapse (no rng)
            return (
                premium * (1 - config.lapse_prob * (1 - config.lapse_premium_factor))
                - claims * (1 - config.lapse_prob * (1 - config.lapse_claims_factor))
                - expenses
            ) * config.clv_multiplier
        return (premium - claims - expenses) * config.clv_multiplier

    if action == ACTION_STANDARD:
        claims = expected_claims * adverse_factor * _claims_noise()
        expenses = _expenses(base_premium)
        if customer_accepted is not None:
            accepted = customer_accepted
        elif acceptance_draw is not None:
            accepted = acceptance_draw < p_std
        elif rng is not None:
            accepted = rng.random() < p_std
        else:
            raise ValueError("Need rng, acceptance_draw, or customer_accepted for STANDARD action")
        if accepted:
            return _net(base_premium, claims, expenses)
        return config.walk_cost

    if action == ACTION_RATED:
        claims = expected_claims * _claims_noise()
        premium = base_premium * 1.25
        expenses = _expenses(premium)
        if customer_accepted is not None:
            accepted = customer_accepted
        elif acceptance_draw is not None:
            accepted = acceptance_draw < p_rtd
        elif rng is not None:
            accepted = rng.random() < p_rtd
        else:
            raise ValueError("Need rng, acceptance_draw, or customer_accepted for RATED action")
        if accepted:
            return _net(premium, claims, expenses)
        return config.walk_cost

    if action == ACTION_DECLINE:
        return config.decline_cost

    if action == ACTION_REFER:
        # REFER computes expected-value of sub-actions (deterministic)
        expenses_std = _expenses(base_premium)
        if config.lapse_prob > 0:
            net_std = (
                base_premium * (1 - config.lapse_prob * (1 - config.lapse_premium_factor))
                - expected_claims * adverse_factor * (1 - config.lapse_prob * (1 - config.lapse_claims_factor))
                - expenses_std
            ) * config.clv_multiplier
        else:
            net_std = (base_premium - expected_claims * adverse_factor - expenses_std) * config.clv_multiplier

        premium_rtd = base_premium * 1.25
        expenses_rtd = _expenses(premium_rtd)
        if config.lapse_prob > 0:
            net_rtd = (
                premium_rtd * (1 - config.lapse_prob * (1 - config.lapse_premium_factor))
                - expected_claims * (1 - config.lapse_prob * (1 - config.lapse_claims_factor))
                - expenses_rtd
            ) * config.clv_multiplier
        else:
            net_rtd = (premium_rtd - expected_claims - expenses_rtd) * config.clv_multiplier

        r_std = p_std * net_std + (1 - p_std) * config.processing_cost
        r_rtd = p_rtd * net_rtd + (1 - p_rtd) * config.processing_cost
        r_dcl = config.decline_cost
        optimal = max(r_std, r_rtd, r_dcl)
        return config.refer_efficiency * optimal - config.refer_admin_cost

    raise ValueError(f"Unknown action: {action}")


def make_reward_simulator(
    rng: np.random.Generator,
    config: RewardConfig | None = None,
    acceptance_draws: np.ndarray | None = None,
    claims_noise: np.ndarray | None = None,
) -> Callable[[int, pd.Series], float]:
    """Return a function reward(action, row) that computes stochastic reward.

    If *acceptance_draws* and *claims_noise* are provided, they are consumed
    sequentially (one per call) instead of drawing fresh random numbers. This
    enables common random numbers across multiple algorithm runs for fair
    comparison.
    """
    cfg = config if config is not None else RewardConfig()

    if acceptance_draws is not None and claims_noise is not None:
        class _PrecomputedReward:
            def __init__(self) -> None:
                self.t = 0

            def __call__(self, action: int, row: pd.Series) -> float:
                t = self.t
                self.t += 1

                # Compute acceptance probability for this action
                if action in (ACTION_STANDARD, ACTION_RATED):
                    mort = row["mortality_multiplier"]
                    income = row["monthly_income_usd"]
                    base_premium = cfg.base_premium_rate * mort

                    def p_accept(premium: float) -> float:
                        ratio = (premium / 12) / income
                        return max(cfg.min_acceptance, cfg.acceptance_intercept - cfg.acceptance_slope * ratio)

                    if action == ACTION_STANDARD:
                        p = p_accept(base_premium)
                    else:
                        p = p_accept(base_premium * 1.25)

                    accepted = acceptance_draws[t] < p
                else:
                    accepted = None

                return _compute_reward(
                    action, row, cfg, None, accepted,
                    acceptance_draw=None, claims_noise_mult=claims_noise[t],
                )

        return _PrecomputedReward()

    def reward(action: int, row: pd.Series) -> float:
        return _compute_reward(action, row, cfg, rng, customer_accepted=None)

    return reward


def compute_reward_with_outcome(
    action: int,
    row: pd.Series,
    customer_accepted: bool,
    config: RewardConfig | None = None,
    rng: np.random.Generator | None = None,
) -> float:
    """Compute reward for a known customer acceptance outcome.

    Use this in backend / feedback endpoints where the acceptance is observed
    rather than sampled.  If *rng* is provided, claims are still noisy;
    if *rng* is None, expected claims are used.
    """
    cfg = config if config is not None else RewardConfig()
    return _compute_reward(action, row, cfg, rng, customer_accepted)


def expected_rewards(
    row: pd.Series,
    config: RewardConfig | None = None,
) -> np.ndarray:
    """Compute expected rewards for all 4 actions (deterministic, for oracle/baseline)."""
    cfg = config if config is not None else RewardConfig()
    mort = row["mortality_multiplier"]
    income = row["monthly_income_usd"]

    base_premium = cfg.base_premium_rate * mort
    expected_claims = cfg.expected_claims_rate * mort
    adverse_factor = 1.0 if mort <= cfg.adverse_threshold else cfg.adverse_factor

    def p_accept(premium: float) -> float:
        ratio = (premium / 12) / income
        return max(cfg.min_acceptance, cfg.acceptance_intercept - cfg.acceptance_slope * ratio)

    p_std = p_accept(base_premium)
    p_rtd = p_accept(base_premium * 1.25)

    def _expenses(premium: float) -> float:
        return cfg.expense_fixed + cfg.expense_ratio * premium

    def _net(premium: float, claims: float, expenses: float) -> float:
        if cfg.lapse_prob > 0:
            return (
                premium * (1 - cfg.lapse_prob * (1 - cfg.lapse_premium_factor))
                - claims * (1 - cfg.lapse_prob * (1 - cfg.lapse_claims_factor))
                - expenses
            ) * cfg.clv_multiplier
        return (premium - claims - expenses) * cfg.clv_multiplier

    expenses_std = _expenses(base_premium)
    net_std = _net(base_premium, expected_claims * adverse_factor, expenses_std)

    premium_rtd = base_premium * 1.25
    expenses_rtd = _expenses(premium_rtd)
    net_rtd = _net(premium_rtd, expected_claims, expenses_rtd)

    r_std = p_std * net_std + (1 - p_std) * cfg.processing_cost
    r_rtd = p_rtd * net_rtd + (1 - p_rtd) * cfg.processing_cost
    r_dcl = cfg.decline_cost
    optimal = max(r_std, r_rtd, r_dcl)
    r_ref = cfg.refer_efficiency * optimal - cfg.refer_admin_cost

    return np.array([r_std, r_rtd, r_dcl, r_ref])


# ── Bandit algorithms ──────────────────────────────────────────────────────

class LinUCB:
    """Linear Upper Confidence Bound for contextual bandits.

    Uses the Sherman-Morrison formula to maintain A^{-1} in O(d^2) time
    per update rather than recomputing the full matrix inverse.
    """

    def __init__(self, n_actions: int, n_features: int, alpha: float = 1.0):
        self.n_actions = n_actions
        self.n_features = n_features
        self.alpha = alpha
        # One A matrix and b vector per action
        self.A = [np.eye(n_features) for _ in range(n_actions)]
        self.A_inv = [np.eye(n_features) for _ in range(n_actions)]
        self.b = [np.zeros(n_features) for _ in range(n_actions)]
        self.theta = [np.zeros(n_features) for _ in range(n_actions)]

    def select_action(self, context: np.ndarray) -> int:
        p = np.zeros(self.n_actions)
        for a in range(self.n_actions):
            A_inv = self.A_inv[a]
            self.theta[a] = A_inv @ self.b[a]
            p[a] = self.theta[a] @ context + self.alpha * np.sqrt(context @ A_inv @ context)
        return int(np.argmax(p))

    def update(self, action: int, context: np.ndarray, reward: float) -> None:
        # Rank-one update of A and b
        self.A[action] += np.outer(context, context)
        self.b[action] += reward * context
        # Sherman-Morrison update of A_inv: O(d^2)
        A_inv = self.A_inv[action]
        Ax = A_inv @ context
        denom = 1.0 + context @ Ax
        self.A_inv[action] = A_inv - np.outer(Ax, Ax) / denom


class LinTS:
    """Linear Thompson Sampling with Gaussian priors.

    Uses Sherman-Morrison to maintain A^{-1} in O(d^2) time per update,
    and caches the Cholesky factor of the posterior covariance so that
    sampling avoids the expensive SVD used by multivariate_normal.
    """

    def __init__(self, n_actions: int, n_features: int, v2: float = 1.0, seed: int = 42):
        self.n_actions = n_actions
        self.n_features = n_features
        self.v2 = v2
        self.A = [np.eye(n_features) for _ in range(n_actions)]
        self.A_inv = [np.eye(n_features) for _ in range(n_actions)]
        self.b = [np.zeros(n_features) for _ in range(n_actions)]
        self.rng = np.random.default_rng(seed=seed)
        # Cache Cholesky factors; recompute only when A_inv changes
        self._cov_chol = [None] * n_actions
        self._cov_dirty = [True] * n_actions

    def _sample_theta(self, a: int) -> np.ndarray:
        """Sample a parameter vector from N(mu_hat, v^2 * A_inv)."""
        if self._cov_dirty[a]:
            cov = self.v2 * self.A_inv[a] + 1e-6 * np.eye(self.n_features)
            self._cov_chol[a] = np.linalg.cholesky(cov)
            self._cov_dirty[a] = False
        mu_hat = self.A_inv[a] @ self.b[a]
        z = self.rng.standard_normal(self.n_features)
        return mu_hat + self._cov_chol[a] @ z

    def select_action(self, context: np.ndarray) -> int:
        p = np.zeros(self.n_actions)
        for a in range(self.n_actions):
            mu_tilde = self._sample_theta(a)
            p[a] = mu_tilde @ context
        return int(np.argmax(p))

    def update(self, action: int, context: np.ndarray, reward: float) -> None:
        self.A[action] += np.outer(context, context)
        self.b[action] += reward * context
        A_inv = self.A_inv[action]
        Ax = A_inv @ context
        denom = 1.0 + context @ Ax
        self.A_inv[action] = A_inv - np.outer(Ax, Ax) / denom
        self._cov_dirty[action] = True


class EpsilonGreedy:
    """Epsilon-greedy with linear regression per action.

    Uses Sherman-Morrison to maintain A^{-1} in O(d^2) time per update.
    """

    def __init__(self, n_actions: int, n_features: int, epsilon: float = 0.1, seed: int = 42):
        self.n_actions = n_actions
        self.n_features = n_features
        self.epsilon = epsilon
        self.A = [np.eye(n_features) for _ in range(n_actions)]
        self.A_inv = [np.eye(n_features) for _ in range(n_actions)]
        self.b = [np.zeros(n_features) for _ in range(n_actions)]
        self.theta = [np.zeros(n_features) for _ in range(n_actions)]
        self.rng = np.random.default_rng(seed=seed)

    def select_action(self, context: np.ndarray) -> int:
        if self.rng.random() < self.epsilon:
            return self.rng.integers(self.n_actions)
        p = np.zeros(self.n_actions)
        for a in range(self.n_actions):
            A_inv = self.A_inv[a]
            self.theta[a] = A_inv @ self.b[a]
            p[a] = self.theta[a] @ context
        return int(np.argmax(p))

    def update(self, action: int, context: np.ndarray, reward: float) -> None:
        self.A[action] += np.outer(context, context)
        self.b[action] += reward * context
        A_inv = self.A_inv[action]
        Ax = A_inv @ context
        denom = 1.0 + context @ Ax
        self.A_inv[action] = A_inv - np.outer(Ax, Ax) / denom


# ── Static baseline ────────────────────────────────────────────────────────

class StaticXGBBaseline:
    """Pre-trained XGBoost model + deterministic rule baseline.

    Produces the exact 21 features the XGB model was trained on:
      age, gender_female, bmi, is_smoking, alcohol_use, is_exercise,
      has_family_history, monthly_income_usd, condition_count,
      has_hypertension, has_diabetes, has_heart_disease,
      has_copd_asthma, has_arthritis, has_tb, has_hepatitis_b,
      region_enc, occupation_enc, education_enc, wealth_enc, health_status_enc
    """

    def __init__(self):
        with open(MODELS_DIR / "cambodia_life_xgb.pkl", "rb") as f:
            self.model = pickle.load(f)

        # Load saved encoders to guarantee exact mapping consistency
        with open(MODELS_DIR / "cambodia_encoders.pkl", "rb") as f:
            encoders = pickle.load(f)
        self.region_le = encoders["region"]
        self.occ_le = encoders["occupation"]
        self.edu_map = encoders["edu_order"]
        self.wealth_map = encoders["wealth_order"]
        self.health_map = encoders["health_order"]

    def _preprocess_row(self, row: pd.Series) -> np.ndarray:
        """Create the original 21 features the XGB model was trained on."""
        conds = str(row.get("pre_existing_conditions", ""))
        cond_count = sum(1 for c in ["Hypertension", "Diabetes", "Heart Disease", "COPD/Asthma", "Arthritis", "TB", "Hepatitis B"] if c in conds)

        x = np.array([
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
        ], dtype=float)
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
        pass  # Static baseline does not learn


# ── Oracle baseline ────────────────────────────────────────────────────────

class OraclePolicy:
    """Deterministic oracle that always selects the action with highest expected reward.

    This policy uses the actuarial reward simulator's ``expected_rewards`` to pick
    the optimal action for each applicant. It provides an upper bound on cumulative
    reward and a lower bound on cumulative regret for any learning algorithm.
    """

    def __init__(self, config: RewardConfig | None = None):
        self.config = config

    # Marker so ``run_bandit`` routes row data to ``select_action``
    def _preprocess_row(self, row: pd.Series) -> np.ndarray:
        return np.array([])

    def select_action(self, context: np.ndarray, row: pd.Series | None = None) -> int:
        if row is None:
            raise ValueError("OraclePolicy needs row to compute expected rewards")
        expected = expected_rewards(row, self.config)
        return int(expected.argmax())

    def update(self, action: int, context: np.ndarray, reward: float) -> None:
        pass  # Oracle does not learn


# ── Runner ─────────────────────────────────────────────────────────────────

@dataclass
class RunResult:
    algorithm: str
    actions: np.ndarray
    rewards: np.ndarray
    regrets: np.ndarray
    cumulative_rewards: np.ndarray
    cumulative_regrets: np.ndarray
    oracle_actions: np.ndarray | None = None


def run_bandit(
    algorithm_name: str,
    bandit,
    contexts: np.ndarray,
    df_raw: pd.DataFrame,
    n_rounds: int,
    seed: int = 42,
    acceptance_draws: np.ndarray | None = None,
    claims_noise: np.ndarray | None = None,
    config: RewardConfig | None = None,
) -> RunResult:
    """Run a bandit algorithm for n_rounds and return metrics.

    Args:
        config: Optional RewardConfig override for sensitivity analysis.
                If None, uses default RewardConfig().
    """
    rng = np.random.default_rng(seed)
    reward_fn = make_reward_simulator(rng, config=config, acceptance_draws=acceptance_draws, claims_noise=claims_noise)

    n_samples = len(contexts)
    indices = np.arange(n_samples)

    # Precompute oracle optimal rewards and actions for all unique samples
    oracle_rewards = np.zeros(n_samples)
    oracle_actions_arr = np.zeros(n_samples, dtype=int)
    for i in range(n_samples):
        expected = expected_rewards(df_raw.iloc[i], config=config)
        oracle_rewards[i] = expected.max()
        oracle_actions_arr[i] = int(expected.argmax())

    # Precompute static baseline actions if applicable (saves repeated XGB predict calls)
    static_actions = None
    if hasattr(bandit, '_preprocess_row'):
        static_actions = np.zeros(n_samples, dtype=int)
        for i in range(n_samples):
            static_actions[i] = bandit.select_action(None, df_raw.iloc[i])

    actions = np.zeros(n_rounds, dtype=int)
    rewards = np.zeros(n_rounds)
    regrets = np.zeros(n_rounds)
    oracle_actions_seq = np.zeros(n_rounds, dtype=int)

    for t in range(n_rounds):
        idx = indices[t % n_samples]
        if t > 0 and t % n_samples == 0:
            rng.shuffle(indices)  # Reshuffle indices each epoch

        context = contexts[idx]
        row = df_raw.iloc[idx]

        if static_actions is not None:
            action = int(static_actions[idx])
        else:
            action = bandit.select_action(context)
        reward = reward_fn(action, row)

        optimal_reward = oracle_rewards[idx]

        actions[t] = action
        rewards[t] = reward
        regrets[t] = optimal_reward - reward
        oracle_actions_seq[t] = oracle_actions_arr[idx]

        bandit.update(action, context, reward)

    return RunResult(
        algorithm=algorithm_name,
        actions=actions,
        rewards=rewards,
        regrets=regrets,
        cumulative_rewards=np.cumsum(rewards),
        cumulative_regrets=np.cumsum(regrets),
        oracle_actions=oracle_actions_seq,
    )


if __name__ == "__main__":
    X, df_raw, features = preprocess_cambodia_data()
    print(f"Features: {features}")
    print(f"Dataset shape: {X.shape}")
    print(f"Sample expected rewards: {expected_rewards(df_raw.iloc[0])}")
