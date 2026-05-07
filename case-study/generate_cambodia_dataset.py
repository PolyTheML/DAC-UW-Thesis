#!/usr/bin/env python3
"""
Generate synthetic Cambodia health/life insurance dataset (2,000 records).

Deeply anchored on Cambodia Demographic and Health Survey (CDHS) 2021-22
[National Institute of Statistics / ICF, 2023] and companion sources:

  CDHS 2021-22 Key Statistics (from Final Report and DHS Program PR136):
  ─────────────────────────────────────────────────────────────────────
  • Region:     Province-level respondent shares (women 15-49 n=19,496;
                men 15-49 n=8,825) — Tables 2.3, 2.4, A.1
  • Age:        Working-adult gamma calibrated to CDHS 15-49 distribution
                (mean ~30.9 women, ~32.5 men) with insurance-applicant skew
  • Gender:     52.2% female / 47.8% male in adult survey population
  • Education:  Women — No ed 11.6%, Primary 38.7%, Secondary 42.5%,
                Higher 7.2%; Men — No ed 5.8%, Primary 36.5%,
                Secondary 48.4%, Higher 9.3% (Tables 3.2.1, 3.2.2)
  • Wealth:     Q1 17.4%, Q2 18.1%, Q3 19.6%, Q4 21.9%, Q5 23.0%
                (Table 2.10)
  • BMI:        Women 15-49 mean 22.9 (SD 3.9); underweight 10.8%,
                normal 61.1%, overweight 22.6%, obese 5.6%
                (CDHS Table 12.18.1 / STEPS 2023)
  • Smoking:    Women 15-49 1.4% smoker; Men ~29.6% current smoking
                (CDHS Table 3.10 / Cambodia STEPS 2023)
  • Alcohol:    64% men, 16% women consume regularly (CDHS 2022)
  • Self-rated health: 72% women, 73% men good/very good; 3% women,
                2% men bad/very bad (CDHS Table 3.1)
  • Physical activity: 36% inactive, 64% active (LCA of CDHS 2021-22)

  Companion Sources:
  ─────────────────────────────────────────────────────────────────────
  • Cambodia STEPS Survey 2023 (MoH/WHO):
      Hypertension 16.8% (raised BP), Diabetes ~7.6% (ages 25-64),
      Overweight 19.4%, Obese 4.3%, Raised cholesterol 25.5%
  • Cambodia General Population Census 2019 (NIS):
      Male life expectancy 67.5 vs female 71.8
  • ILO Cambodia Labour Force Survey 2023:
      Occupation distribution and wage baselines
  • WHO Global TB Report 2022:
      Cambodia 246/100k TB incidence (high burden)
  • WHO Cambodia 2019:
      Hepatitis B surface antigen prevalence ~7.5%

New features vs. previous version:
  - education           (CDHS Tables 3.2.1, 3.2.2)
  - wealth_quintile     (CDHS Table 2.10)
  - alcohol_use         (CDHS 2022 alcohol module)
  - self_reported_health (CDHS Table 3.1)
  - Region shares recalibrated to exact CDHS province weights
  - BMI recalibrated to CDHS mean 22.9, SD 3.9
  - Smoking recalibrated to CDHS 1.4% women, STEPS 29.6% men

Output: case-study/cambodia_dataset.csv + .parquet
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from pathlib import Path

np.random.seed(42)
random.seed(42)

ROOT = Path(__file__).parent

# ---------------------------------------------------------------------------
# REGION DISTRIBUTION
# Source: CDHS 2021-22 Final Report, Tables 2.3 & 2.4 — Province sample
#         distribution of women and men age 15-49.
# Province counts (women 15-49) are summed into 7 macro regions.
# ---------------------------------------------------------------------------
# CDHS province counts (women 15-49):
#   Phnom Penh 3,160 | Kandal 1,445 | Kampong Cham 1,163 | Tboung Khmum 851
#   Siem Reap 1,548 | Battambang 1,347 | Prey Veng 1,233 | Preah Sihanouk 243
#   Other 16 provinces 8,506  →  Total 19,496
REGIONS = {
    'Phnom Penh':       0.1621,  # 3,160 / 19,496  (CDHS 2021-22)
    'Kandal':           0.0741,  # 1,445 / 19,496
    'Kampong Cham':     0.1033,  # (1,163 + 851) / 19,496  [incl. Tboung Khmum]
    'Siem Reap':        0.0794,  # 1,548 / 19,496
    'Battambang':       0.0691,  # 1,347 / 19,496
    'Prey Veng':        0.0632,  # 1,233 / 19,496
    'Preah Sihanouk':   0.0125,  # 243 / 19,496
    'Other Provinces':  0.4363,  # 8,506 / 19,496  (16 remaining provinces)
}

# ---------------------------------------------------------------------------
# OCCUPATION DISTRIBUTION
# Source: ILO Cambodia Labour Force Survey 2023 + CDHS 2021-22 employment data
# Frequencies reflect the 5 segments highlighted in the RL literature
# (adaptive_underwriting_cambodia.md) plus supporting categories.
# ---------------------------------------------------------------------------
OCCUPATIONS = {
    #                     health_risk  life_risk  freq   income_base(USD/mo)
    'Rice Farmer':         {'health_risk': 0.30, 'life_risk': 0.25, 'freq': 0.28, 'income_base': 125},
    'Garment Worker':      {'health_risk': 0.25, 'life_risk': 0.20, 'freq': 0.20, 'income_base': 210},
    'Moto/Tuk-tuk Driver': {'health_risk': 0.40, 'life_risk': 0.45, 'freq': 0.12, 'income_base': 210},
    'Market Vendor':       {'health_risk': 0.20, 'life_risk': 0.15, 'freq': 0.15, 'income_base': 165},
    'Construction Worker': {'health_risk': 0.45, 'life_risk': 0.40, 'freq': 0.08, 'income_base': 230},
    'Civil Servant':       {'health_risk': 0.15, 'life_risk': 0.12, 'freq': 0.10, 'income_base': 360},
    'Monk/Retired':        {'health_risk': 0.35, 'life_risk': 0.50, 'freq': 0.07, 'income_base': 90},
}

# ---------------------------------------------------------------------------
# GENDER × OCCUPATION PROBABILITIES  P(female | occupation)
# Source: CDHS 2021-22 Table 3 (employment by sex); ILO 2023
#   - Garment: ~85% female (Better Factories Cambodia annual report 2023)
#   - Moto/tuk-tuk: ~85% male (Phnom Penh transport survey data)
#   - Construction: ~90% male (ILO Cambodia 2023)
#   - Rice farmer: ~55% female (GPC 2019, agricultural employment by sex)
#   - Market vendor: ~62% female (CDHS 2021-22)
#   - Civil servant: ~40% female (Ministry of Civil Service 2022 report)
#   - Monk/Retired: monks are male by convention; retired ~40% female
# ---------------------------------------------------------------------------
OCCUPATION_FEMALE_PROB = {
    'Rice Farmer':         0.55,
    'Garment Worker':      0.85,
    'Moto/Tuk-tuk Driver': 0.15,
    'Market Vendor':       0.62,
    'Construction Worker': 0.10,
    'Civil Servant':       0.40,
    'Monk/Retired':        0.38,
}

# ---------------------------------------------------------------------------
# EDUCATION DISTRIBUTION
# Source: CDHS 2021-22 Tables 3.2.1 (women) & 3.2.2 (men), age 15-49.
# Weighted pooled distribution (women n=19,496; men n=8,825).
# For insurance-applicant pool we retain the raw CDHS proportions.
# ---------------------------------------------------------------------------
EDUCATION_LEVELS = ['No education', 'Primary', 'Secondary', 'Higher']
EDUCATION_DIST = [0.098, 0.379, 0.441, 0.079]

# Education effect on health risk (literature-based):
# Higher education → lower NCD risk in Cambodia (CDHS Table 12.x patterns)
EDUCATION_HEALTH_FACTOR = {
    'No education': 0.12,
    'Primary':      0.06,
    'Secondary':    0.00,
    'Higher':      -0.08,
}

# ---------------------------------------------------------------------------
# WEALTH QUINTILE DISTRIBUTION
# Source: CDHS 2021-22 Table 2.10 — Household wealth index.
# ---------------------------------------------------------------------------
WEALTH_QUINTILES = ['Poorest', 'Poorer', 'Middle', 'Richer', 'Richest']
WEALTH_DIST = [0.174, 0.181, 0.196, 0.219, 0.230]

# Wealth effect on health risk:
# Poorest quintile shows higher undernutrition and infectious disease burden;
# Richest shows higher NCD prevalence (obesity, diabetes) in urban Cambodia.
WEALTH_HEALTH_FACTOR = {
    'Poorest':  0.06,
    'Poorer':   0.03,
    'Middle':   0.00,
    'Richer':  -0.02,
    'Richest':  0.04,  # urban NCD transition effect
}


def generate_record():
    """Generate single Cambodian applicant record anchored on CDHS 2021-22."""

    # --- Age ---
    # CDHS 2021-22 women 15-49: mean ~30.9 years (SD ~9.6).
    # For life/health insurance applicants (working adults 18-65):
    #   gamma(shape=3.8, scale=4.2) + 18 → mean ~34, median ~33
    # calibrated to skew slightly older than general population (stable income).
    age = np.random.gamma(shape=3.8, scale=4.2) + 18
    age = int(np.clip(age, 18, 65))

    # --- Region ---
    region = np.random.choice(list(REGIONS.keys()), p=list(REGIONS.values()))

    # --- Occupation ---
    occupation = np.random.choice(
        list(OCCUPATIONS.keys()),
        p=[OCCUPATIONS[occ]['freq'] for occ in OCCUPATIONS.keys()]
    )
    occ_health_risk = OCCUPATIONS[occupation]['health_risk']
    occ_life_risk   = OCCUPATIONS[occupation]['life_risk']

    # --- Gender ---
    # Occupation-specific female probability (see OCCUPATION_FEMALE_PROB above)
    is_female = np.random.random() < OCCUPATION_FEMALE_PROB[occupation]
    gender = 'Female' if is_female else 'Male'

    # --- Education ---
    # CDHS 2021-22 pooled distribution with slight urban premium
    edu_probs = np.array(EDUCATION_DIST.copy())
    if region == 'Phnom Penh':
        edu_probs += np.array([-0.04, -0.08, 0.08, 0.04])
    elif region in ('Preah Sihanouk', 'Siem Reap'):
        edu_probs += np.array([-0.02, -0.04, 0.04, 0.02])
    edu_probs = np.clip(edu_probs, 0.01, 0.99)
    edu_probs = edu_probs / edu_probs.sum()
    education = np.random.choice(EDUCATION_LEVELS, p=edu_probs)

    # --- Wealth Quintile ---
    # CDHS 2021-22 exact quintile shares; urban = richer
    wealth_probs = np.array(WEALTH_DIST.copy())
    if region == 'Phnom Penh':
        wealth_probs += np.array([-0.06, -0.04, -0.02, 0.04, 0.08])
    elif region in ('Preah Sihanouk', 'Siem Reap'):
        wealth_probs += np.array([-0.03, -0.02, 0.00, 0.02, 0.03])
    else:
        wealth_probs += np.array([0.03, 0.02, 0.00, -0.02, -0.03])
    wealth_probs = np.clip(wealth_probs, 0.01, 0.99)
    wealth_probs = wealth_probs / wealth_probs.sum()
    wealth_quintile = np.random.choice(WEALTH_QUINTILES, p=wealth_probs)

    # --- Smoking ---
    # Source: CDHS 2021-22 Table 3.10 (women 15-49 smoker 1.4%);
    #         Cambodia STEPS 2023 (men 18-69 current smoking 29.6%).
    # Adjusted upward for high-risk occupations (moto, construction).
    base_smoking = 0.014 if is_female else 0.296
    smoking_prob = base_smoking + occ_health_risk * 0.06 + np.random.uniform(-0.03, 0.03)
    is_smoking = int(np.random.random() < np.clip(smoking_prob, 0.01, 0.65))

    # --- Alcohol Use ---
    # Source: CDHS 2022 — 64% men, 16% women consume alcohol regularly.
    # Heavy episodic drinking: 49.5% men aged 18-69 (STEPS 2023).
    base_alcohol = 0.16 if is_female else 0.64
    alcohol_prob = base_alcohol + occ_health_risk * 0.08 + np.random.uniform(-0.05, 0.05)
    alcohol_use = int(np.random.random() < np.clip(alcohol_prob, 0.02, 0.80))

    # --- Exercise ---
    # CDHS-based LCA: 36% inactive, 64% active (mostly work-related).
    # Lower for sedentary/aging; higher for active occupations (farmers, drivers).
    exercise_base = 0.55 - occ_health_risk * 0.25 - (age - 30) * 0.005
    exercise_prob = np.clip(exercise_base + np.random.uniform(-0.05, 0.05), 0.05, 0.80)
    is_exercise = int(np.random.random() < exercise_prob)

    # --- BMI ---
    # CDHS 2021-22 women 15-49: mean 22.9, SD 3.9.
    # Cambodia STEPS 2023: overweight 19.4%, obese 4.3% (both sexes 18-69).
    # Men tend slightly lower BMI at working age in Cambodia.
    base_bmi = 22.0 if is_female else 21.5
    base_bmi += (age - 30) * 0.05
    base_bmi += occ_health_risk * 1.8
    if region == 'Phnom Penh':
        base_bmi += 1.2  # urban obesity transition (STEPS 2023)
    if wealth_quintile == 'Richest':
        base_bmi += 0.8
    elif wealth_quintile == 'Poorest':
        base_bmi -= 0.5
    bmi = float(np.clip(np.random.normal(base_bmi, 3.5), 16.0, 40.0))
    bmi = round(bmi, 1)

    # --- Self-Reported Health ---
    # CDHS 2021-22 Table 3.1: 72% women, 73% men good/very good;
    # 3% women, 2% men bad/very bad. Insurance applicants skew healthier.
    health_probs = [0.03, 0.20, 0.77]  # Poor, Fair, Good
    if is_smoking:
        health_probs = [0.08, 0.30, 0.62]
    if age > 50:
        health_probs = [0.06, 0.28, 0.66]
    if occ_health_risk > 0.35:
        health_probs = [0.07, 0.32, 0.61]
    self_reported_health = np.random.choice(['Poor', 'Fair', 'Good'], p=health_probs)

    # --- Pre-existing Conditions ---
    # Base risk index combining age, BMI, occupation, education, wealth
    edu_factor = EDUCATION_HEALTH_FACTOR[education]
    wealth_factor = WEALTH_HEALTH_FACTOR[wealth_quintile]
    conditions_risk = (
        occ_health_risk
        + (age - 30) * 0.009
        + (bmi - 22) * 0.018
        + edu_factor
        + wealth_factor
    )

    pre_existing = []

    # Hypertension: STEPS 2023 — 16.8% adults 18-69 had raised BP
    # Rises sharply with age: men 45-59 33.8%, 60-69 46.0%
    htn_prob = conditions_risk * 0.20
    if age >= 45:
        htn_prob += 0.12
    if age >= 60:
        htn_prob += 0.15
    if bmi >= 25:
        htn_prob += 0.08
    if is_smoking:
        htn_prob += 0.04
    if np.random.random() < np.clip(htn_prob, 0.03, 0.50):
        pre_existing.append('Hypertension')

    # Diabetes: STEPS 2023 / Health Strategic Plan 2025-2034 — 7.6% ages 25-64
    dm_prob = conditions_risk * 0.14
    if age >= 40:
        dm_prob += 0.04
    if bmi >= 25:
        dm_prob += 0.06
    if wealth_quintile == 'Richest':
        dm_prob += 0.03  # urban NCD transition
    if np.random.random() < np.clip(dm_prob, 0.02, 0.30):
        pre_existing.append('Diabetes')

    # Heart Disease: GBD 2019 Cambodia — ~4% adult prevalence
    hd_prob = conditions_risk * 0.09
    if age >= 50:
        hd_prob += 0.05
    if is_smoking:
        hd_prob += 0.04
    if np.random.random() < np.clip(hd_prob, 0.01, 0.20):
        pre_existing.append('Heart Disease')

    # COPD/Asthma: WHO Cambodia 2020 — ~3.5% COPD; ~4% asthma
    copd_prob = conditions_risk * 0.11
    if is_smoking:
        copd_prob += 0.08
    if np.random.random() < np.clip(copd_prob, 0.02, 0.22):
        pre_existing.append('COPD/Asthma')

    # Arthritis: low in young Cambodian population; rises 50+
    arth_prob = conditions_risk * 0.06
    if age >= 50:
        arth_prob += 0.06
    if np.random.random() < np.clip(arth_prob, 0.01, 0.18):
        pre_existing.append('Arthritis')

    # TB: WHO Global TB Report 2022 — Cambodia 246/100k incidence (high burden)
    #   Active/known TB among insurance applicants estimated ~2-4%
    #   Higher in poorest quintile and rural areas
    tb_prob = conditions_risk * 0.07 + 0.02
    if wealth_quintile == 'Poorest':
        tb_prob += 0.02
    if region != 'Phnom Penh':
        tb_prob += 0.01
    if np.random.random() < np.clip(tb_prob, 0.02, 0.14):
        pre_existing.append('TB')

    # Hepatitis B: WHO Cambodia 2019 — ~7.5% surface antigen prevalence
    hep_prob = 0.075 + conditions_risk * 0.03
    if np.random.random() < np.clip(hep_prob, 0.03, 0.14):
        pre_existing.append('Hepatitis B')

    conditions_str = '; '.join(pre_existing) if pre_existing else 'None'

    # --- Monthly Income (USD) ---
    # Source: ILO Labour Force Survey Cambodia 2023; World Bank data
    #   Cambodia is heavily USD-dollarized for formal sector wages
    #   Garment minimum wage 2023: $202/month
    #   Civil servant base: $250-450/month; variations by grade
    region_factor = 1.30 if region == 'Phnom Penh' else (
                    1.15 if region in ('Preah Sihanouk', 'Siem Reap') else
                    1.05 if region == 'Kandal' else 0.82
    )
    edu_income_boost = {'No education': 0.85, 'Primary': 0.95,
                        'Secondary': 1.05, 'Higher': 1.25}
    monthly_income_usd = float(np.clip(
        OCCUPATIONS[occupation]['income_base'] * region_factor * edu_income_boost[education]
        + np.random.normal(0, 28),
        55, 750
    ))
    monthly_income_usd = round(monthly_income_usd, 0)

    # --- Health Score (0–100, inverse of risk) ---
    # Composite index: lower = higher claim risk; basis for RL reward signal
    health_score = 100 - (
        conditions_risk * 26
        + (bmi - 22) * 1.4
        + (age - 30) * 0.42
        + (5.0 if 'TB' in conditions_str else 0)
        + (3.0 if 'Hepatitis B' in conditions_str else 0)
        + (2.5 if is_smoking else 0)
        + (2.0 if alcohol_use else 0)
        + (2.0 if self_reported_health == 'Poor' else
           0.5 if self_reported_health == 'Fair' else 0)
        + (1.5 if not is_exercise else 0)
    )
    health_score = round(float(np.clip(health_score, 15, 95)), 1)

    # --- Family History ---
    has_family_history = int(np.random.random() < np.clip(occ_health_risk * 0.22 + 0.08, 0.08, 0.38))

    # --- Mortality Multiplier ---
    # 1.0 = standard actuarial rate; >1 = rated or decline territory
    # Male excess mortality: Cambodia male life expectancy 67.5 vs female 71.8 (GPC 2019)
    mortality_multiplier = 1.0
    mortality_multiplier += (age - 30) * 0.020
    mortality_multiplier += occ_life_risk * 1.8
    mortality_multiplier += 0.08 if not is_female else 0.0   # male excess mortality
    mortality_multiplier += 0.28 if is_smoking else 0
    mortality_multiplier += 0.15 if alcohol_use else 0
    mortality_multiplier -= 0.10 if is_exercise else 0
    mortality_multiplier += len(pre_existing) * 0.22
    mortality_multiplier += 0.18 if 'TB' in conditions_str else 0
    mortality_multiplier += 0.12 if 'Hepatitis B' in conditions_str else 0
    mortality_multiplier += 0.06 if self_reported_health == 'Poor' else 0
    mortality_multiplier = round(float(np.clip(mortality_multiplier, 0.5, 5.0)), 2)

    return {
        'applicant_id':            None,
        'age':                     age,
        'gender':                  gender,
        'region':                  region,
        'occupation':              occupation,
        'education':               education,
        'wealth_quintile':         wealth_quintile,
        'is_smoking':              is_smoking,
        'alcohol_use':             alcohol_use,
        'is_exercise':             is_exercise,
        'bmi':                     bmi,
        'self_reported_health':    self_reported_health,
        'pre_existing_conditions': conditions_str,
        'monthly_income_usd':      monthly_income_usd,
        'health_score':            health_score,
        'has_family_history':      has_family_history,
        'mortality_multiplier':    mortality_multiplier,
        'application_date':        None,
    }


def main():
    print("Generating synthetic Cambodia health/life insurance dataset (2,000 records)...")
    print("Primary anchor: Cambodia Demographic and Health Survey (CDHS) 2021-22 [NIS/ICF]")
    print("Companion: STEPS 2023, GPC 2019, ILO 2023, WHO TB Report 2022")

    records = []
    base_date = datetime(2024, 1, 1)

    for i in range(2000):
        record = generate_record()
        record['applicant_id'] = f'KH-{i+1:05d}'
        record['application_date'] = (
            base_date + timedelta(days=np.random.randint(0, 365))
        ).strftime('%Y-%m-%d')
        records.append(record)
        if (i + 1) % 500 == 0:
            print(f"  Generated {i + 1} records...")

    df = pd.DataFrame(records)

    # --- Output ---
    csv_path     = ROOT / 'cambodia_dataset.csv'
    parquet_path = ROOT / 'cambodia_dataset.parquet'
    df.to_csv(csv_path, index=False)
    df.to_parquet(parquet_path, index=False)

    print(f"\nSaved: {csv_path}")
    print(f"Saved: {parquet_path}")

    # --- Validation Summary ---
    print("\n=== Dataset Validation Summary ===")
    print(f"Total records : {len(df)}")
    print(f"Age           : {df['age'].min()}–{df['age'].max()} (mean {df['age'].mean():.1f}, median {df['age'].median():.0f})")
    print(f"BMI           : {df['bmi'].min():.1f}–{df['bmi'].max():.1f} (mean {df['bmi'].mean():.1f}, SD {df['bmi'].std():.1f})")
    print(f"Smoking rate  : {df['is_smoking'].mean()*100:.1f}%")
    print(f"  Male        : {df.loc[df['gender']=='Male','is_smoking'].mean()*100:.1f}%  (target ~29.6%)")
    print(f"  Female      : {df.loc[df['gender']=='Female','is_smoking'].mean()*100:.1f}%  (target ~1.4%)")
    print(f"Alcohol use   : {df['alcohol_use'].mean()*100:.1f}%")
    print(f"  Male        : {df.loc[df['gender']=='Male','alcohol_use'].mean()*100:.1f}%  (target ~64%)")
    print(f"  Female      : {df.loc[df['gender']=='Female','alcohol_use'].mean()*100:.1f}%  (target ~16%)")
    print(f"Exercise rate : {df['is_exercise'].mean()*100:.1f}%")
    print(f"Monthly income: ${df['monthly_income_usd'].min():.0f}–${df['monthly_income_usd'].max():.0f} (mean ${df['monthly_income_usd'].mean():.0f})")
    print(f"Mortality mult: {df['mortality_multiplier'].min():.2f}–{df['mortality_multiplier'].max():.2f}")

    print("\nGender Distribution:")
    print(df['gender'].value_counts(normalize=True).mul(100).round(1).to_string())

    print("\nRegion Distribution (vs. CDHS 2021-22 target):")
    rd = df['region'].value_counts(normalize=True).mul(100).round(1)
    targets = {k: round(v*100, 1) for k, v in REGIONS.items()}
    for r, pct in rd.items():
        print(f"  {r:<22} {pct:5.1f}%  (target {targets.get(r, '?')}%)")

    print("\nEducation Distribution (vs. CDHS pooled target):")
    ed = df['education'].value_counts(normalize=True).mul(100).round(1)
    edu_targets = {e: round(p*100, 1) for e, p in zip(EDUCATION_LEVELS, EDUCATION_DIST)}
    for e, pct in ed.reindex(EDUCATION_LEVELS).items():
        print(f"  {e:<22} {pct:5.1f}%  (target {edu_targets.get(e, '?')}%)")

    print("\nWealth Quintile Distribution (vs. CDHS target):")
    wq = df['wealth_quintile'].value_counts(normalize=True).mul(100).round(1)
    w_targets = {w: round(p*100, 1) for w, p in zip(WEALTH_QUINTILES, WEALTH_DIST)}
    for w, pct in wq.reindex(WEALTH_QUINTILES).items():
        print(f"  {w:<22} {pct:5.1f}%  (target {w_targets.get(w, '?')}%)")

    print("\nSelf-Reported Health:")
    print(df['self_reported_health'].value_counts(normalize=True).mul(100).round(1).to_string())

    print("\nOccupation Distribution:")
    print(df['occupation'].value_counts().to_string())

    print("\nGender × Occupation (% female):")
    go = df.groupby('occupation')['gender'].apply(lambda x: (x=='Female').mean()*100).round(1)
    for occ, pct in go.items():
        print(f"  {occ:<25} {pct:.1f}%  (target {OCCUPATION_FEMALE_PROB.get(occ,0)*100:.0f}%)")

    print("\nPre-existing Conditions (prevalence %):")
    all_conditions = []
    for conds in df['pre_existing_conditions']:
        if conds != 'None':
            all_conditions.extend(conds.split('; '))
    cond_pcts = pd.Series(all_conditions).value_counts()
    for cond, cnt in cond_pcts.items():
        print(f"  {cond:<20} {cnt/len(df)*100:.1f}%")

    print("\nReady for model training.")


if __name__ == '__main__':
    main()
