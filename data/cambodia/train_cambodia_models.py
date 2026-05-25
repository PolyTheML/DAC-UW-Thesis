"""
Cambodia Case Study — XGBoost + GLM Model Training
Trains two models:
  1. health_xgb  — predicts health risk score (higher = healthier, 15-95 scale)
  2. life_xgb    — predicts mortality multiplier (1.0 = standard)
Each paired with a GLM baseline.

Feature set anchored on CDHS 2021-22:
  - Demographics: age, gender, region, occupation
  - Social determinants: education, wealth_quintile (CDHS Tables 3.2, 2.10)
  - Behaviours: smoking, alcohol_use (CDHS/STEPS 2023), exercise
  - Health: BMI (CDHS mean 22.9, SD 3.9), self_reported_health (CDHS Table 3.1)
  - Clinical: 7 pre-existing conditions, condition_count, family_history

Outputs: models/cambodia_*.pkl, cambodia_shap_values.pkl, cambodia_model_results.json
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
DATA_PATH = Path(__file__).parent / "cambodia_dataset.csv"
MODELS_DIR = Path(__file__).parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

# Load & feature engineering
df = pd.read_csv(DATA_PATH)

CONDITIONS = ["Hypertension", "Diabetes", "Heart Disease", "COPD/Asthma", "Arthritis", "TB", "Hepatitis B"]
for cond in CONDITIONS:
    col_name = f"has_{cond.lower().replace('/', '_').replace(' ', '_')}"
    df[col_name] = df["pre_existing_conditions"].fillna("").str.contains(cond, regex=False).astype(int)

df["condition_count"] = df[[f"has_{c.lower().replace('/', '_').replace(' ', '_')}" for c in CONDITIONS]].sum(axis=1)

# Categorical encodings — preserve LabelEncoder objects for downstream use
le_region = LabelEncoder().fit(df["region"])
le_occ = LabelEncoder().fit(df["occupation"])
df["region_enc"] = le_region.transform(df["region"])
df["occupation_enc"] = le_occ.transform(df["occupation"])

# gender_female: 1 = female, 0 = male
df["gender_female"] = (df["gender"].str.lower() == "female").astype(int)

# education: ordinal encoding (CDHS progression)
edu_order = {'No education': 0, 'Primary': 1, 'Secondary': 2, 'Higher': 3}
df["education_enc"] = df["education"].map(edu_order)

# wealth_quintile: ordinal encoding (poorest → richest)
wealth_order = {'Poorest': 0, 'Poorer': 1, 'Middle': 2, 'Richer': 3, 'Richest': 4}
df["wealth_enc"] = df["wealth_quintile"].map(wealth_order)

# self_reported_health: ordinal (poor=0, fair=1, good=2)
health_order = {'Poor': 0, 'Fair': 1, 'Good': 2}
df["health_status_enc"] = df["self_reported_health"].map(health_order)

FEATURES = [
    "age", "gender_female", "bmi", "is_smoking", "alcohol_use", "is_exercise",
    "has_family_history", "monthly_income_usd", "condition_count",
    "has_hypertension", "has_diabetes", "has_heart_disease",
    "has_copd_asthma", "has_arthritis", "has_tb", "has_hepatitis_b",
    "region_enc", "occupation_enc",
    "education_enc", "wealth_enc", "health_status_enc",
]

FEATURE_LABELS = {
    "age": "Age", "gender_female": "Female", "bmi": "BMI",
    "is_smoking": "Smoker", "alcohol_use": "Alcohol Use", "is_exercise": "Exercises Regularly",
    "has_family_history": "Family History",
    "monthly_income_usd": "Monthly Income (USD)",
    "condition_count": "# Pre-existing Conditions",
    "has_hypertension": "Hypertension", "has_diabetes": "Diabetes",
    "has_heart_disease": "Heart Disease", "has_copd_asthma": "COPD/Asthma",
    "has_arthritis": "Arthritis", "has_tb": "TB", "has_hepatitis_b": "Hepatitis B",
    "region_enc": "Region", "occupation_enc": "Occupation",
    "education_enc": "Education", "wealth_enc": "Wealth Quintile",
    "health_status_enc": "Self-Reported Health",
}

X = df[FEATURES]
y_health = df["health_score"]
y_mortality = df["mortality_multiplier"]

X_train, X_test, yh_train, yh_test, ym_train, ym_test = train_test_split(
    X, y_health, y_mortality, test_size=0.2, random_state=SEED
)

def metrics(y_true, y_pred, name):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    return {
        "model": name,
        "rmse": round(rmse, 4),
        "mae": round(mean_absolute_error(y_true, y_pred), 4),
        "r2": round(r2_score(y_true, y_pred), 4),
    }

# Health model
print("Training health models...")
glm_df = X_train.copy()
glm_df["health_score"] = yh_train
formula = (
    "health_score ~ age + gender_female + bmi + is_smoking + alcohol_use + is_exercise"
    " + has_family_history + condition_count + monthly_income_usd"
    " + education_enc + wealth_enc + health_status_enc"
)
glm_health = smf.ols(formula, data=glm_df).fit()
glm_health_pred = glm_health.predict(X_test.assign(health_score=0))
health_glm_metrics = metrics(yh_test, glm_health_pred, "GLM (OLS)")

xgb_health = xgb.XGBRegressor(
    n_estimators=300, max_depth=5, learning_rate=0.05,
    subsample=0.8, colsample_bytree=0.8, min_child_weight=3,
    reg_alpha=0.1, random_state=SEED, verbosity=0,
)
xgb_health.fit(X_train, yh_train, eval_set=[(X_test, yh_test)], verbose=False)
xgb_health_pred = xgb_health.predict(X_test)
health_xgb_metrics = metrics(yh_test, xgb_health_pred, "XGBoost")

print(f"  GLM  — RMSE: {health_glm_metrics['rmse']:.4f}  R2: {health_glm_metrics['r2']:.4f}")
print(f"  XGBoost — RMSE: {health_xgb_metrics['rmse']:.4f}  R2: {health_xgb_metrics['r2']:.4f}")

# Mortality model
print("Training mortality models...")
glm_df2 = X_train.copy()
glm_df2["mortality_multiplier"] = ym_train
glm_life = smf.glm(
    "mortality_multiplier ~ age + gender_female + bmi + is_smoking + alcohol_use + is_exercise"
    " + has_family_history + condition_count + monthly_income_usd"
    " + education_enc + wealth_enc + health_status_enc",
    data=glm_df2,
    family=__import__("statsmodels").genmod.families.family.Gamma(
        link=__import__("statsmodels").genmod.families.links.Log()
    ),
).fit()
glm_life_pred = glm_life.predict(X_test.assign(mortality_multiplier=0))
mortality_glm_metrics = metrics(ym_test, glm_life_pred, "GLM (Gamma/log)")

xgb_life = xgb.XGBRegressor(
    n_estimators=300, max_depth=5, learning_rate=0.05,
    subsample=0.8, colsample_bytree=0.8, min_child_weight=3,
    reg_alpha=0.1, random_state=SEED, verbosity=0,
)
xgb_life.fit(X_train, ym_train, eval_set=[(X_test, ym_test)], verbose=False)
xgb_life_pred = xgb_life.predict(X_test)
mortality_xgb_metrics = metrics(ym_test, xgb_life_pred, "XGBoost")

print(f"  GLM  — RMSE: {mortality_glm_metrics['rmse']:.4f}  R2: {mortality_glm_metrics['r2']:.4f}")
print(f"  XGBoost — RMSE: {mortality_xgb_metrics['rmse']:.4f}  R2: {mortality_xgb_metrics['r2']:.4f}")

# SHAP values
print("Computing SHAP values...")
explainer_health = shap.TreeExplainer(xgb_health)
explainer_life = shap.TreeExplainer(xgb_life)
shap_health = explainer_health(X_test)
shap_life = explainer_life(X_test)

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

# Save models
print("Saving models...")
with open(MODELS_DIR / "cambodia_health_xgb.pkl", "wb") as f:
    pickle.dump(xgb_health, f)
with open(MODELS_DIR / "cambodia_life_xgb.pkl", "wb") as f:
    pickle.dump(xgb_life, f)
with open(MODELS_DIR / "cambodia_health_glm.pkl", "wb") as f:
    pickle.dump(glm_health, f)
with open(MODELS_DIR / "cambodia_life_glm.pkl", "wb") as f:
    pickle.dump(glm_life, f)

# Save label encoders for downstream use
with open(MODELS_DIR / "cambodia_encoders.pkl", "wb") as f:
    pickle.dump({
        "region": le_region,
        "occupation": le_occ,
        "edu_order": edu_order,
        "wealth_order": wealth_order,
        "health_order": health_order,
    }, f)

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
with open(MODELS_DIR / "cambodia_shap_values.pkl", "wb") as f:
    pickle.dump(shap_output, f)

# GLM coefficients export
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
    "feature_order": [
        "age", "gender_female", "bmi", "is_smoking", "alcohol_use", "is_exercise",
        "has_family_history", "condition_count", "monthly_income_usd",
        "education_enc", "wealth_enc", "health_status_enc",
    ],
}
with open(MODELS_DIR / "cambodia_glm_coefficients.json", "w") as f:
    json.dump(glm_coeff_export, f, indent=2)

# Test predictions
demo_df = X_test.copy()
demo_df["actual_health_score"] = yh_test.values
demo_df["glm_health_score"] = glm_health_pred.values
demo_df["xgb_health_score"] = xgb_health_pred
demo_df["actual_mortality_mult"] = ym_test.values
demo_df["glm_mortality_mult"] = glm_life_pred.values
demo_df["xgb_mortality_mult"] = xgb_life_pred
demo_df.to_csv(MODELS_DIR / "cambodia_test_predictions.csv", index=False)

# Results JSON
results = {
    "health_model": {
        "target": "health_score",
        "description": "Predicts health risk score (15-95). Lower = higher claim risk.",
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

with open(MODELS_DIR / "cambodia_model_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nDone. All Cambodia models saved to data/cambodia/models/")
print(json.dumps(results, indent=2))
