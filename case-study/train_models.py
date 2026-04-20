"""
Vietnam Case Study — XGBoost + GLM Model Training
Trains two models:
  1. health_xgb  — predicts health risk score (higher = healthier, 48-95 scale)
  2. life_xgb    — predicts mortality multiplier (1.0 = standard, >1 = substandard)
Each paired with a GLM baseline for side-by-side demo comparison.
Outputs: models/*.pkl, shap_values.pkl, model_results.json
"""
import json
import pickle
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import shap
import statsmodels.formula.api as smf
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings("ignore")

SEED = 42
DATA_PATH = Path(__file__).parent / "vietnam_dataset.csv"
MODELS_DIR = Path(__file__).parent / "models"
MODELS_DIR.mkdir(exist_ok=True)


# ── 1. Load & feature engineering ──────────────────────────────────────────

df = pd.read_csv(DATA_PATH)

# Pre-existing conditions → binary flags (multi-label, separator = '; ')
CONDITIONS = ["Hypertension", "Diabetes", "Heart Disease", "COPD/Asthma", "Arthritis"]
for cond in CONDITIONS:
    df[f"has_{cond.lower().replace('/', '_').replace(' ', '_')}"] = (
        df["pre_existing_conditions"].fillna("").str.contains(cond, regex=False).astype(int)
    )
df["condition_count"] = df[[f"has_{c.lower().replace('/', '_').replace(' ', '_')}" for c in CONDITIONS]].sum(axis=1)

# Encode categoricals for XGBoost (label encode — tree models handle this fine)
le_region = LabelEncoder().fit(df["region"])
le_occ = LabelEncoder().fit(df["occupation"])
df["region_enc"] = le_region.transform(df["region"])
df["occupation_enc"] = le_occ.transform(df["occupation"])

FEATURES = [
    "age", "bmi", "is_smoking", "is_exercise", "has_family_history",
    "monthly_income_millions_vnd", "condition_count",
    "has_hypertension", "has_diabetes", "has_heart_disease",
    "has_copd_asthma", "has_arthritis",
    "region_enc", "occupation_enc",
]

FEATURE_LABELS = {
    "age": "Age",
    "bmi": "BMI",
    "is_smoking": "Smoker",
    "is_exercise": "Exercises Regularly",
    "has_family_history": "Family History",
    "monthly_income_millions_vnd": "Monthly Income (MVND)",
    "condition_count": "# Pre-existing Conditions",
    "has_hypertension": "Hypertension",
    "has_diabetes": "Diabetes",
    "has_heart_disease": "Heart Disease",
    "has_copd_asthma": "COPD/Asthma",
    "has_arthritis": "Arthritis",
    "region_enc": "Region",
    "occupation_enc": "Occupation",
}

X = df[FEATURES]
y_health = df["health_score"]
y_mortality = df["mortality_multiplier"]

X_train, X_test, yh_train, yh_test, ym_train, ym_test = train_test_split(
    X, y_health, y_mortality, test_size=0.2, random_state=SEED
)


# ── 2. Helper: metrics dict ─────────────────────────────────────────────────

def metrics(y_true, y_pred, name):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    return {
        "model": name,
        "rmse": round(rmse, 4),
        "mae": round(mean_absolute_error(y_true, y_pred), 4),
        "r2": round(r2_score(y_true, y_pred), 4),
    }


# ── 3. Health model ─────────────────────────────────────────────────────────

print("Training health models...")

# GLM baseline (OLS — Gaussian family, log-link not needed for score range 48-95)
glm_df = X_train.copy()
glm_df["health_score"] = yh_train
formula = "health_score ~ age + bmi + is_smoking + is_exercise + has_family_history + condition_count + monthly_income_millions_vnd"
glm_health = smf.ols(formula, data=glm_df).fit()
glm_health_pred = glm_health.predict(X_test.assign(health_score=0))
health_glm_metrics = metrics(yh_test, glm_health_pred, "GLM (OLS)")

# XGBoost
xgb_health = xgb.XGBRegressor(
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=3,
    reg_alpha=0.1,
    random_state=SEED,
    verbosity=0,
)
xgb_health.fit(X_train, yh_train, eval_set=[(X_test, yh_test)], verbose=False)
xgb_health_pred = xgb_health.predict(X_test)
health_xgb_metrics = metrics(yh_test, xgb_health_pred, "XGBoost")

print(f"  GLM  — RMSE: {health_glm_metrics['rmse']:.4f}  R²: {health_glm_metrics['r2']:.4f}")
print(f"  XGBoost — RMSE: {health_xgb_metrics['rmse']:.4f}  R²: {health_xgb_metrics['r2']:.4f}")


# ── 4. Mortality model ──────────────────────────────────────────────────────

print("Training mortality models...")

# GLM baseline (Gamma with log-link — mortality multiplier is positive, right-skewed)
glm_df2 = X_train.copy()
glm_df2["mortality_multiplier"] = ym_train
glm_life = smf.glm(
    "mortality_multiplier ~ age + bmi + is_smoking + is_exercise + has_family_history + condition_count + monthly_income_millions_vnd",
    data=glm_df2,
    family=__import__("statsmodels").genmod.families.family.Gamma(
        link=__import__("statsmodels").genmod.families.links.Log()
    ),
).fit()
glm_life_pred = glm_life.predict(X_test.assign(mortality_multiplier=0))
mortality_glm_metrics = metrics(ym_test, glm_life_pred, "GLM (Gamma/log)")

# XGBoost
xgb_life = xgb.XGBRegressor(
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=3,
    reg_alpha=0.1,
    random_state=SEED,
    verbosity=0,
)
xgb_life.fit(X_train, ym_train, eval_set=[(X_test, ym_test)], verbose=False)
xgb_life_pred = xgb_life.predict(X_test)
mortality_xgb_metrics = metrics(ym_test, xgb_life_pred, "XGBoost")

print(f"  GLM  — RMSE: {mortality_glm_metrics['rmse']:.4f}  R²: {mortality_glm_metrics['r2']:.4f}")
print(f"  XGBoost — RMSE: {mortality_xgb_metrics['rmse']:.4f}  R²: {mortality_xgb_metrics['r2']:.4f}")


# ── 5. SHAP values ──────────────────────────────────────────────────────────

print("Computing SHAP values...")

explainer_health = shap.TreeExplainer(xgb_health)
explainer_life = shap.TreeExplainer(xgb_life)

# Use test set (400 rows) for SHAP — sufficient for demo
shap_health = explainer_health(X_test)
shap_life = explainer_life(X_test)

# Top 5 features by mean |SHAP| for each model
def top_features(shap_values, feature_names, labels, n=5):
    mean_abs = np.abs(shap_values.values).mean(axis=0)
    idx = np.argsort(mean_abs)[::-1][:n]
    return [
        {"feature": feature_names[i], "label": labels.get(feature_names[i], feature_names[i]), "importance": round(float(mean_abs[i]), 4)}
        for i in idx
    ]

health_top_features = top_features(shap_health, FEATURES, FEATURE_LABELS)
life_top_features = top_features(shap_life, FEATURES, FEATURE_LABELS)

print("  Top health drivers:", [f["label"] for f in health_top_features])
print("  Top mortality drivers:", [f["label"] for f in life_top_features])


# ── 6. Save models ──────────────────────────────────────────────────────────

print("Saving models...")

with open(MODELS_DIR / "health_xgb.pkl", "wb") as f:
    pickle.dump(xgb_health, f)

with open(MODELS_DIR / "life_xgb.pkl", "wb") as f:
    pickle.dump(xgb_life, f)

with open(MODELS_DIR / "health_glm.pkl", "wb") as f:
    pickle.dump(glm_health, f)

with open(MODELS_DIR / "life_glm.pkl", "wb") as f:
    pickle.dump(glm_life, f)

# Save SHAP values + test set for demo use
shap_output = {
    "health": {
        "values": shap_health.values.tolist(),
        "base_values": shap_health.base_values.tolist(),
        "data": shap_health.data.tolist(),
        "feature_names": FEATURES,
        "feature_labels": FEATURE_LABELS,
    },
    "life": {
        "values": shap_life.values.tolist(),
        "base_values": shap_life.base_values.tolist(),
        "data": shap_life.data.tolist(),
        "feature_names": FEATURES,
        "feature_labels": FEATURE_LABELS,
    },
}
with open(MODELS_DIR / "shap_values.pkl", "wb") as f:
    pickle.dump(shap_output, f)

# Export GLM coefficients for lightweight production inference (no statsmodels needed)
ols_params = glm_health.params.to_dict()
gamma_params = glm_life.params.to_dict()
glm_coeff_export = {
    "health_ols": {
        "intercept": ols_params.get("Intercept", 0.0),
        "params": {k: v for k, v in ols_params.items() if k != "Intercept"},
        "method": "OLS (Gaussian, identity link)",
    },
    "mortality_gamma": {
        "intercept": gamma_params.get("Intercept", 0.0),
        "params": {k: v for k, v in gamma_params.items() if k != "Intercept"},
        "method": "GLM (Gamma, log link) — predict = exp(X @ params)",
    },
    "feature_order": ["age", "bmi", "is_smoking", "is_exercise", "has_family_history",
                      "condition_count", "monthly_income_millions_vnd"],
}
with open(MODELS_DIR / "glm_coefficients.json", "w") as f:
    json.dump(glm_coeff_export, f, indent=2)

# Save test set predictions for demo comparison table
demo_df = X_test.copy()
demo_df["actual_health_score"] = yh_test.values
demo_df["glm_health_score"] = glm_health_pred.values
demo_df["xgb_health_score"] = xgb_health_pred
demo_df["actual_mortality_mult"] = ym_test.values
demo_df["glm_mortality_mult"] = glm_life_pred.values
demo_df["xgb_mortality_mult"] = xgb_life_pred
demo_df.to_csv(MODELS_DIR / "test_predictions.csv", index=False)


# ── 7. Save results JSON ────────────────────────────────────────────────────

results = {
    "health_model": {
        "target": "health_score",
        "description": "Predicts health risk score (48-95). Lower = higher claim risk.",
        "glm": health_glm_metrics,
        "xgboost": health_xgb_metrics,
        "top_features": health_top_features,
        "train_size": len(X_train),
        "test_size": len(X_test),
    },
    "mortality_model": {
        "target": "mortality_multiplier",
        "description": "Predicts mortality risk multiplier. 1.0 = standard rate.",
        "glm": mortality_glm_metrics,
        "xgboost": mortality_xgb_metrics,
        "top_features": life_top_features,
        "train_size": len(X_train),
        "test_size": len(X_test),
    },
    "feature_names": FEATURES,
    "feature_labels": FEATURE_LABELS,
}

with open(MODELS_DIR / "model_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nDone. All models saved to case-study/models/")
print(json.dumps(results, indent=2))
