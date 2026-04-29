#!/usr/bin/env python3
"""
Generate synthetic Cambodia health insurance dataset (2,000 records).

Tailored to Cambodian demographics:
- Younger population (median ~25 vs Vietnam ~32)
- Lower income, USD-denominated
- Higher TB/Hep-B prevalence
- Distinct occupation mix (garment workers, moto drivers, monks)

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

# Cambodia regions (6 major areas)
REGIONS = {
    'Phnom Penh': 0.18,
    'Siem Reap': 0.10,
    'Battambang': 0.12,
    'Preah Sihanouk': 0.08,
    'Kampong Cham': 0.14,
    'Other Rural': 0.38,
}

# Occupations (Cambodia-specific health risk proxies)
OCCUPATIONS = {
    'Rice Farmer': {'health_risk': 0.30, 'life_risk': 0.25, 'freq': 0.30, 'income_base': 120},
    'Garment Factory Worker': {'health_risk': 0.25, 'life_risk': 0.20, 'freq': 0.20, 'income_base': 180},
    'Moto/Tuk-tuk Driver': {'health_risk': 0.40, 'life_risk': 0.45, 'freq': 0.12, 'income_base': 200},
    'Market Vendor': {'health_risk': 0.20, 'life_risk': 0.15, 'freq': 0.15, 'income_base': 160},
    'Construction Worker': {'health_risk': 0.45, 'life_risk': 0.40, 'freq': 0.08, 'income_base': 220},
    'Civil Servant': {'health_risk': 0.15, 'life_risk': 0.12, 'freq': 0.08, 'income_base': 350},
    'Monk/Retired': {'health_risk': 0.35, 'life_risk': 0.55, 'freq': 0.07, 'income_base': 100},
}


def generate_record():
    """Generate single Cambodian applicant record."""

    # Age: Cambodia is very young (median ~25), heavy skew 18-45
    age = np.random.gamma(shape=5, scale=5) + 18
    age = np.clip(age, 18, 85).astype(int)

    # Region
    region = np.random.choice(list(REGIONS.keys()), p=list(REGIONS.values()))

    # Occupation
    occupation = np.random.choice(
        list(OCCUPATIONS.keys()),
        p=[OCCUPATIONS[occ]['freq'] for occ in OCCUPATIONS.keys()]
    )

    occ_health_risk = OCCUPATIONS[occupation]['health_risk']
    occ_life_risk = OCCUPATIONS[occupation]['life_risk']

    # Smoking: very high among Cambodian men (~40%), very low among women (~5%)
    # We don't model gender explicitly, so we use occupation as proxy
    smoking_prob = occ_health_risk * 0.6 + np.random.uniform(0, 0.15)
    is_smoking = np.random.random() < min(smoking_prob, 0.55)

    # Exercise: inverse to age + occupation risk
    exercise_prob = 0.55 - occ_health_risk * 0.35 - (age - 30) * 0.004
    exercise_prob = np.clip(exercise_prob, 0.05, 0.85)
    is_exercise = np.random.random() < exercise_prob

    # BMI: generally lower than Vietnam, but urban obesity rising
    base_bmi = 21.5 + (age - 30) * 0.04 + occ_health_risk * 2.5
    if region == 'Phnom Penh':
        base_bmi += 1.2  # urban obesity effect
    bmi = np.random.normal(base_bmi, 2.2)
    bmi = np.clip(bmi, 16, 40)

    # Pre-existing conditions
    pre_existing = []
    conditions_risk = occ_health_risk + (age - 30) * 0.008 + (bmi - 24) * 0.018

    if np.random.random() < np.clip(conditions_risk * 0.18, 0, 0.35):
        pre_existing.append('Hypertension')
    if np.random.random() < np.clip(conditions_risk * 0.14, 0, 0.30):
        pre_existing.append('Diabetes')
    if np.random.random() < np.clip(conditions_risk * 0.09, 0, 0.22):
        pre_existing.append('Heart Disease')
    if np.random.random() < np.clip(conditions_risk * 0.12, 0, 0.28):
        pre_existing.append('COPD/Asthma')
    if np.random.random() < np.clip(conditions_risk * 0.06, 0, 0.15):
        pre_existing.append('Arthritis')
    # Cambodia-specific: higher TB and Hep-B prevalence
    if np.random.random() < np.clip(conditions_risk * 0.10 + 0.03, 0, 0.18):
        pre_existing.append('TB')
    if np.random.random() < np.clip(0.06 + conditions_risk * 0.05, 0, 0.15):
        pre_existing.append('Hepatitis B')

    conditions_str = '; '.join(pre_existing) if pre_existing else 'None'

    # Income in USD (Cambodia is heavily dollarized)
    region_income_factor = 1.3 if region == 'Phnom Penh' else (
        1.1 if region == 'Preah Sihanouk' else 0.85
    )
    monthly_income_usd = (
        OCCUPATIONS[occupation]['income_base'] * region_income_factor
        + np.random.normal(0, 25)
    )
    monthly_income_usd = np.clip(monthly_income_usd, 60, 600)

    # Health status score (0-100, inverse of risk factors)
    health_score = 100 - (
        conditions_risk * 28
        + (bmi - 24) * 1.8
        + (age - 30) * 0.4
        + (5 if 'TB' in conditions_str else 0)
        + (3 if 'Hepatitis B' in conditions_str else 0)
    )
    health_score = np.clip(health_score, 15, 95)

    # Mortality risk multiplier
    mortality_multiplier = 1.0
    mortality_multiplier += (age - 30) * 0.018
    mortality_multiplier += occ_life_risk * 1.8
    mortality_multiplier += 0.25 if is_smoking else 0
    mortality_multiplier -= 0.12 if is_exercise else 0
    mortality_multiplier += len(pre_existing) * 0.22
    mortality_multiplier += 0.15 if 'TB' in conditions_str else 0
    mortality_multiplier += 0.10 if 'Hepatitis B' in conditions_str else 0

    mortality_multiplier = np.clip(mortality_multiplier, 0.5, 5.0)

    # Family history
    has_family_history = np.random.random() < (occ_health_risk * 0.25 + 0.08)

    return {
        'applicant_id': None,
        'age': age,
        'region': region,
        'occupation': occupation,
        'is_smoking': int(is_smoking),
        'is_exercise': int(is_exercise),
        'bmi': round(bmi, 1),
        'pre_existing_conditions': conditions_str,
        'monthly_income_usd': round(monthly_income_usd, 0),
        'health_score': round(health_score, 1),
        'has_family_history': int(has_family_history),
        'mortality_multiplier': round(mortality_multiplier, 2),
        'application_date': None,
    }


def main():
    print("Generating synthetic Cambodia health insurance dataset (2,000 records)...")

    records = []
    base_date = datetime(2024, 1, 1)

    for i in range(2000):
        record = generate_record()
        record['applicant_id'] = f'KH-{i+1:05d}'
        days_offset = np.random.randint(0, 365)
        record['application_date'] = (base_date + timedelta(days=days_offset)).strftime('%Y-%m-%d')
        records.append(record)

        if (i + 1) % 500 == 0:
            print(f"  Generated {i + 1} records...")

    df = pd.DataFrame(records)
    csv_path = ROOT / 'cambodia_dataset.csv'
    parquet_path = ROOT / 'cambodia_dataset.parquet'

    df.to_csv(csv_path, index=False)
    df.to_parquet(parquet_path, index=False)

    print(f"\nSaved to: {csv_path}")
    print(f"Saved to: {parquet_path}")

    print("\nDataset Summary:")
    print(f"  Total records: {len(df)}")
    print(f"  Age range: {df['age'].min()}-{df['age'].max()} (mean: {df['age'].mean():.1f})")
    print(f"  BMI range: {df['bmi'].min():.1f}-{df['bmi'].max():.1f} (mean: {df['bmi'].mean():.1f})")
    print(f"  Smoking rate: {df['is_smoking'].mean()*100:.1f}%")
    print(f"  Exercise rate: {df['is_exercise'].mean()*100:.1f}%")
    print(f"  Monthly income: ${df['monthly_income_usd'].min():.0f}-${df['monthly_income_usd'].max():.0f} (mean: ${df['monthly_income_usd'].mean():.0f})")
    print(f"  Mortality multiplier range: {df['mortality_multiplier'].min():.2f}-{df['mortality_multiplier'].max():.2f}")

    print("\nRegion Distribution:")
    print(df['region'].value_counts().to_string())

    print("\nOccupation Distribution:")
    print(df['occupation'].value_counts().to_string())

    print("\nPre-existing Conditions (top 10):")
    all_conditions = []
    for conds in df['pre_existing_conditions']:
        if conds != 'None':
            all_conditions.extend(conds.split('; '))
    condition_counts = pd.Series(all_conditions).value_counts().head(10)
    print(condition_counts.to_string() if len(condition_counts) > 0 else "  (None captured)")

    print("\nReady for model training!")


if __name__ == '__main__':
    main()
