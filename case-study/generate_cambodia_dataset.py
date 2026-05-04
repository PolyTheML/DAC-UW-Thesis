#!/usr/bin/env python3
"""
Generate synthetic Cambodia health/life insurance dataset (2,000 records).

Calibrated to official demographic sources:
  - Cambodia General Population Census (GPC) 2019 [NIS Cambodia]:
      province population shares, full age/sex distribution (all ages)
  - Cambodia Demographic and Health Survey (CDHS) 2021-22 [NIS/ICF]:
      province shares for adult males 15-49, wealth quintiles, education
  - Cambodia Tobacco Atlas 2023 / WHO STEPS Survey 2016:
      gender-stratified smoking rates
  - ILO Cambodia Labour Force Survey 2023:
      occupation distribution and wages
  - WHO Cambodia Country Profile + IDF Diabetes Atlas 2021:
      disease prevalence rates

Key fixes vs. previous version:
  - Kandal province added (~7.1% GPC 2019, was 0%)
  - Preah Sihanouk corrected 8% → 1.8% (GPC 2019)
  - Kampong Cham corrected 14% → 10% (Kampong Cham + Tboung Khmum)
  - Age distribution corrected: mean ~35 (was 43); GPC 2019 adult median ~30
  - Gender field added with occupation-specific probabilities (ILO 2023)
  - Gender-stratified smoking rates (male 36%, female 4%; Tobacco Atlas 2023)
  - BMI calibrated to Cambodia STEPS Survey 2010 (mean ~22.0, lower than Vietnam)

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
# Source: GPC 2019 Final Report, Table 1 — Province Population Summary
# (NIS Cambodia, 2020; total population 16,718,965)
# Note: Kampong Cham figure includes Tboung Khmum province (split 2013);
#       "Other Provinces" aggregates remaining 17 provinces.
# ---------------------------------------------------------------------------
REGIONS = {
    'Phnom Penh':       0.137,  # 2,282k / 16,719k
    'Kandal':           0.071,  # 1,187k — borders capital, semi-urban
    'Kampong Cham':     0.103,  # 894k + Tboung Khmum 803k
    'Siem Reap':        0.064,  # 1,063k — tourism hub
    'Battambang':       0.061,  # 1,012k — rice belt NW
    'Prey Veng':        0.057,  # 948k  — rice farming SE
    'Preah Sihanouk':   0.018,  # 304k  — coastal port city
    'Other Provinces':  0.489,  # 14 remaining provinces
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


def generate_record():
    """Generate single Cambodian applicant record."""

    # --- Age ---
    # GPC 2019: Cambodia national median age 25.8 years; adult (18+) median ~30
    # For life/health insurance applicants: working-age skew, max 65
    # gamma(shape=3.5, scale=4.5) + 18 → mean ~34, median ~32
    # Source: GPC 2019 Table B.1 — Population by Single Year of Age
    age = np.random.gamma(shape=3.5, scale=4.5) + 18
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

    # --- Smoking ---
    # Source: Cambodia Tobacco Atlas 2023; WHO STEPS Survey Cambodia 2016
    #   Male adults: 36% current smoker; Female adults: 4%
    #   Adjusted slightly upward for high-risk occupations (moto, construction)
    base_smoking = 0.04 if is_female else 0.36
    smoking_prob = base_smoking + occ_health_risk * 0.06 + np.random.uniform(-0.03, 0.03)
    is_smoking = int(np.random.random() < np.clip(smoking_prob, 0.02, 0.65))

    # --- Exercise ---
    # WHO NCD Progress Monitor Cambodia 2022: ~38% meet physical activity guidelines
    # Lower for sedentary/aging; higher for active occupations (farmers, drivers)
    exercise_base = 0.50 - occ_health_risk * 0.25 - (age - 30) * 0.005
    exercise_prob = np.clip(exercise_base + np.random.uniform(-0.05, 0.05), 0.05, 0.80)
    is_exercise = int(np.random.random() < exercise_prob)

    # --- BMI ---
    # Cambodia STEPS Survey 2010 + WHO NCD country profile:
    #   Mean BMI ~22.0 (lower than Vietnam ~22.5), std ~3.0
    #   Urban (Phnom Penh) adds ~1.0 (rising obesity trend)
    #   Female tends slightly lower BMI at working age in Cambodia
    base_bmi = 21.5 + (age - 30) * 0.045 + occ_health_risk * 2.0
    if region == 'Phnom Penh':
        base_bmi += 1.0
    if is_female:
        base_bmi -= 0.5
    bmi = float(np.clip(np.random.normal(base_bmi, 2.8), 16.0, 40.0))
    bmi = round(bmi, 1)

    # --- Pre-existing Conditions ---
    # Base risk index combining age, BMI, occupation
    conditions_risk = occ_health_risk + (age - 30) * 0.009 + (bmi - 22) * 0.020

    pre_existing = []

    # Hypertension: WHO Cambodia 2019 — ~24% adult prevalence; rises with age/BMI
    if np.random.random() < np.clip(conditions_risk * 0.22, 0.03, 0.40):
        pre_existing.append('Hypertension')

    # Diabetes: IDF Diabetes Atlas 2021 SEA — Cambodia ~8% prevalence (adults 20-79)
    if np.random.random() < np.clip(conditions_risk * 0.16, 0.02, 0.28):
        pre_existing.append('Diabetes')

    # Heart Disease: GBD 2019 Cambodia — ~4% adult prevalence
    if np.random.random() < np.clip(conditions_risk * 0.10, 0.01, 0.18):
        pre_existing.append('Heart Disease')

    # COPD/Asthma: WHO Cambodia 2020 — ~3.5% COPD; ~4% asthma
    if np.random.random() < np.clip(conditions_risk * 0.13, 0.02, 0.22):
        pre_existing.append('COPD/Asthma')

    # Arthritis: low in young Cambodian population; rises 50+
    if np.random.random() < np.clip(conditions_risk * 0.07, 0.01, 0.15):
        pre_existing.append('Arthritis')

    # TB: WHO Global TB Report 2022 — Cambodia 246/100k incidence (high burden)
    #   Active/known TB among insurance applicants estimated ~2-4%
    if np.random.random() < np.clip(conditions_risk * 0.08 + 0.02, 0.02, 0.12):
        pre_existing.append('TB')

    # Hepatitis B: WHO Cambodia 2019 — ~7.5% surface antigen prevalence
    if np.random.random() < np.clip(0.075 + conditions_risk * 0.04, 0.03, 0.14):
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
    monthly_income_usd = float(np.clip(
        OCCUPATIONS[occupation]['income_base'] * region_factor + np.random.normal(0, 28),
        55, 650
    ))
    monthly_income_usd = round(monthly_income_usd, 0)

    # --- Health Score (0–100, inverse of risk) ---
    # Composite index: lower = higher claim risk; basis for RL reward signal
    health_score = 100 - (
        conditions_risk * 26
        + (bmi - 22) * 1.6
        + (age - 30) * 0.45
        + (5.0 if 'TB' in conditions_str else 0)
        + (3.0 if 'Hepatitis B' in conditions_str else 0)
        + (2.0 if is_smoking else 0)
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
    mortality_multiplier -= 0.10 if is_exercise else 0
    mortality_multiplier += len(pre_existing) * 0.22
    mortality_multiplier += 0.18 if 'TB' in conditions_str else 0
    mortality_multiplier += 0.12 if 'Hepatitis B' in conditions_str else 0
    mortality_multiplier = round(float(np.clip(mortality_multiplier, 0.5, 5.0)), 2)

    return {
        'applicant_id':            None,
        'age':                     age,
        'gender':                  gender,
        'region':                  region,
        'occupation':              occupation,
        'is_smoking':              is_smoking,
        'is_exercise':             is_exercise,
        'bmi':                     bmi,
        'pre_existing_conditions': conditions_str,
        'monthly_income_usd':      monthly_income_usd,
        'health_score':            health_score,
        'has_family_history':      has_family_history,
        'mortality_multiplier':    mortality_multiplier,
        'application_date':        None,
    }


def main():
    print("Generating synthetic Cambodia health/life insurance dataset (2,000 records)...")
    print("Calibration sources: GPC 2019 (NIS), CDHS 2021-22 (NIS/ICF), WHO, ILO, Tobacco Atlas 2023")

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
    print(f"BMI           : {df['bmi'].min():.1f}–{df['bmi'].max():.1f} (mean {df['bmi'].mean():.1f})")
    print(f"Smoking rate  : {df['is_smoking'].mean()*100:.1f}%")
    print(f"  Male        : {df.loc[df['gender']=='Male','is_smoking'].mean()*100:.1f}%  (target ~36%)")
    print(f"  Female      : {df.loc[df['gender']=='Female','is_smoking'].mean()*100:.1f}%  (target ~4%)")
    print(f"Exercise rate : {df['is_exercise'].mean()*100:.1f}%")
    print(f"Monthly income: ${df['monthly_income_usd'].min():.0f}–${df['monthly_income_usd'].max():.0f} (mean ${df['monthly_income_usd'].mean():.0f})")
    print(f"Mortality mult: {df['mortality_multiplier'].min():.2f}–{df['mortality_multiplier'].max():.2f}")

    print("\nGender Distribution:")
    print(df['gender'].value_counts(normalize=True).mul(100).round(1).to_string())

    print("\nRegion Distribution (vs. GPC 2019 target):")
    rd = df['region'].value_counts(normalize=True).mul(100).round(1)
    targets = {k: round(v*100, 1) for k, v in REGIONS.items()}
    for r, pct in rd.items():
        print(f"  {r:<22} {pct:5.1f}%  (target {targets.get(r, '?')}%)")

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
