"""θ-based scoring for the Underwriting Desk (spec §6).

Uses a representative *trained* LinUCB policy (θ from
demo/static/coefficients_linucb_seed42.json). No new modelling math: the
applicant is preprocessed by reusing healthrl.preprocess_cambodia_data on the
applicant row concatenated to the raw dataset (so the one-hot columns align and
normalization uses the dataset's training-basis statistics).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from healthrl.underwriting_bandit import (
    ACTION_NAMES,
    DATA_PATH,
    RewardConfig,
    StaticXGBBaseline,
    preprocess_cambodia_data,
)
from demo.pricing_engine import compute_psi, optimize_premium

ROOT = Path(__file__).resolve().parent.parent.parent
COEFFS_PATH = ROOT / "demo" / "static" / "coefficients_linucb_seed42.json"

# Presentation constant for the confidence aid (spec §6/§13): softmax temperature
# on the dollar reward scale. Calibrated to ≈ the median top1-vs-top2 reward gap
# (~6) so the typical case is discriminating without saturating clear-cut cases.
# NOT a calibrated probability — labelled illustrative.
CONFIDENCE_TEMP = 6.0

# Human-readable labels for the 34 model features (spec §6 "drivers").
FEATURE_LABELS = {
    "age": "Age",
    "gender_female": "Female",
    "bmi": "BMI",
    "is_smoking": "Smoker",
    "alcohol_use": "Alcohol use",
    "is_exercise": "Exercises",
    "has_family_history": "Family history",
    "monthly_income_usd": "Monthly income",
    "condition_count": "Number of conditions",
    "education_enc": "Education level",
    "wealth_enc": "Wealth quintile",
    "health_status_enc": "Self-reported health",
    "has_hypertension": "Hypertension",
    "has_diabetes": "Diabetes",
    "has_heart_disease": "Heart disease",
    "has_copd_asthma": "COPD/Asthma",
    "has_arthritis": "Arthritis",
    "has_tb": "Tuberculosis",
    "has_hepatitis_b": "Hepatitis B",
    "region_Battambang": "Region: Battambang",
    "region_Kampong Cham": "Region: Kampong Cham",
    "region_Kandal": "Region: Kandal",
    "region_Other Provinces": "Region: Other Provinces",
    "region_Phnom Penh": "Region: Phnom Penh",
    "region_Preah Sihanouk": "Region: Preah Sihanouk",
    "region_Prey Veng": "Region: Prey Veng",
    "region_Siem Reap": "Region: Siem Reap",
    "occ_Civil Servant": "Occupation: Civil Servant",
    "occ_Construction Worker": "Occupation: Construction Worker",
    "occ_Garment Worker": "Occupation: Garment Worker",
    "occ_Market Vendor": "Occupation: Market Vendor",
    "occ_Monk/Retired": "Occupation: Monk/Retired",
    "occ_Moto/Tuk-tuk Driver": "Occupation: Moto/Tuk-tuk Driver",
    "occ_Rice Farmer": "Occupation: Rice Farmer",
}


def _label(feature: str) -> str:
    return FEATURE_LABELS.get(feature, feature.replace("_", " ").capitalize())


class DeskScorer:
    """Holds the trained θ, dataset stats, and the raw base for concat-scoring."""

    def __init__(self) -> None:
        coeffs = json.loads(COEFFS_PATH.read_text(encoding="utf-8"))
        self.theta = np.asarray(coeffs["theta"], dtype=float)  # (4, 34)
        self.coeff_features: list[str] = coeffs["features"]

        self.X_full, self.df_raw, self.features = preprocess_cambodia_data()
        assert self.coeff_features == self.features, "θ feature order mismatch"

        # Dataset normalization stats (df carries un-normalized feature columns).
        self.stats = {
            c: (float(self.df_raw[c].mean()), float(self.df_raw[c].std()))
            for c in self.features
        }
        # Original raw columns, for concatenating a new applicant row.
        self.raw_base = pd.read_csv(DATA_PATH)
        self.config = RewardConfig()
        self.static_xgb = StaticXGBBaseline()  # loads cambodia_life_xgb.pkl + encoders

        self._canonical_zones = self._load_canonical_zones()
        self.fairness = self._compute_model_fairness()  # cached at startup

    def _load_canonical_zones(self) -> dict[str, Any]:
        """Authoritative EXP-006 PSI zones from thesis_results.json (spec §8)."""
        path = ROOT / "demo" / "static" / "thesis_results.json"
        data = json.loads(path.read_text(encoding="utf-8"))["exp006"]
        return {
            "region_zone": data["region"]["psi_zone"],
            "occupation_zone": data["occupation"]["psi_zone"],
            "region_psi": data["region"]["psi_final_window"],
            "occupation_psi": data["occupation"]["psi_final_window"],
        }

    def _compute_model_fairness(self) -> dict[str, Any]:
        """Standing model-level PSI: trained policy's approved pool vs population.

        Approved = the policy issues a policy (STANDARD or RATED). PSI compares
        the approved subpopulation's group distribution against the full
        population (spec §3.5/§6). Cached; never per-applicant.
        """
        actions = np.argmax(self.X_full @ self.theta.T, axis=1)  # (N,)
        approved = np.isin(actions, [0, 1])  # STANDARD, RATED
        out: dict[str, Any] = {}
        zones = []
        for col, label in (("region", "Region"), ("occupation", "Occupation")):
            ref = self.df_raw[col].value_counts().sort_index()
            act = self.df_raw.loc[approved, col].value_counts().reindex(
                ref.index, fill_value=0
            )
            psi = compute_psi(ref.values.astype(float), act.values.astype(float))
            status = "GREEN" if psi < 0.10 else "AMBER" if psi < 0.25 else "RED"
            out[col] = {"label": label, "psi": round(psi, 4), "status": status}
            zones.append(status)
        order = {"GREEN": 0, "AMBER": 1, "RED": 2}
        out["badge_status"] = max(zones, key=lambda z: order[z])
        out["canonical"] = self._canonical_zones
        out["note"] = (
            "Model-level guardrail: trained-policy approved pool vs population "
            "(illustrative). Authoritative zones: EXP-006, 20 seeds."
        )
        return out

    def featurize(self, applicant: dict[str, Any]) -> np.ndarray:
        """Normalized 34-dim feature vector for a single applicant (spec §6)."""
        combined = pd.concat(
            [self.raw_base, pd.DataFrame([applicant])], ignore_index=True
        )
        x_comb, _, feats = preprocess_cambodia_data(df=combined, stats=self.stats)
        assert feats == self.features, "feature alignment broke during scoring"
        return np.asarray(x_comb[-1], dtype=float)

    def _premium(self, decision: str, applicant: dict[str, Any]) -> dict[str, Any]:
        """Recommended premium consistent with the decision (spec §6)."""
        row = pd.Series(applicant)
        mort = float(applicant.get("mortality_multiplier", 1.0))
        base_premium = round(self.config.base_premium_rate * mort, 2)
        if decision == "DECLINE":
            return {"display": "— (declined)", "amount": None,
                    "multiplier": None, "status": "declined", "p_accept": None}
        if decision == "REFER":
            return {"display": "Pending review", "amount": None,
                    "multiplier": None, "status": "refer", "p_accept": None}
        if decision == "STANDARD":
            return {"display": f"${base_premium:,.2f} /yr", "amount": base_premium,
                    "multiplier": 1.0, "status": "base", "p_accept": None}
        # RATED → profit-optimal loaded premium.
        opt = optimize_premium(row, self.config)
        return {
            "display": f"${opt['optimal_premium_usd']:,.2f} /yr",
            "amount": opt["optimal_premium_usd"],
            "multiplier": opt["optimal_multiplier"],
            "status": "loaded",
            "p_accept": opt["optimal_p_accept"],
        }

    def _score_static_xgb(self, applicant: dict[str, Any]) -> dict[str, Any]:
        """Static XGB's decision + its real, explainable mechanics.

        The baseline predicts a mortality multiplier from the raw applicant row and
        applies frozen thresholds (<=1.5 STANDARD, <=2.2 RATED, <=2.6 REFER, else
        DECLINE) - underwriting_bandit.py StaticXGBBaseline.select_action.
        """
        row = pd.Series(applicant)
        mort_pred = float(self.static_xgb.model.predict(
            self.static_xgb._preprocess_row(row))[0])
        action = self.static_xgb.select_action(np.zeros(1), row=row)
        bands = "≤1.5 STANDARD · ≤2.2 RATED · ≤2.6 REFER · >2.6 DECLINE"
        return {
            "action": ACTION_NAMES[action],
            "mortality_pred": round(mort_pred, 2),
            "reasoning": (
                f"Predicted mortality ×{mort_pred:.2f} → "
                f"{ACTION_NAMES[action]} band (frozen thresholds: {bands})"
            ),
        }

    def score(self, applicant: dict[str, Any]) -> dict[str, Any]:
        x = self.featurize(applicant)
        r = self.theta @ x  # (4,) estimated reward per action
        a_star = int(np.argmax(r))
        decision = ACTION_NAMES[a_star]

        # Confidence aid: softmax over r / τ (presentation-only, illustrative).
        z = r / CONFIDENCE_TEMP
        z = z - z.max()
        soft = np.exp(z) / np.exp(z).sum()
        confidence = float(soft[a_star])

        # Top-3 drivers by |θ_{a*,i} · x_i|, signed.
        contrib = self.theta[a_star] * x
        top = np.argsort(np.abs(contrib))[::-1][:3]
        drivers = [
            {
                "feature": self.features[i],
                "label": _label(self.features[i]),
                "direction": "up" if contrib[i] >= 0 else "down",
                "contribution": round(float(contrib[i]), 3),
            }
            for i in top
        ]

        return {
            "decision": decision,
            "decision_index": a_star,
            "confidence": round(confidence, 4),
            "estimated_rewards": {
                ACTION_NAMES[i]: round(float(r[i]), 2) for i in range(len(ACTION_NAMES))
            },
            "drivers": drivers,
            "premium": self._premium(decision, applicant),
            "static_xgb": self._score_static_xgb(applicant),
            "fairness": self.fairness,
            "illustrative_note": (
                "Illustrative · single seed (42) · representative trained LinUCB policy"
            ),
        }


# Module-level singleton (load θ + data once).
SCORER = DeskScorer()
