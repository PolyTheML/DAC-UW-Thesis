#!/usr/bin/env python3
"""
Generate synthetic Vietnam health + life insurance dataset (2,000 records).

Dataset includes:
- Health insurance factors: age, BMI, smoking, exercise, occupation, region, pre-existing conditions
- Life insurance factors: age, occupation, health status, mortality risk indicators
- Realistic Vietnam demographics and risk distributions

Output: case-study/vietnam_dataset.csv
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Vietnam regions (8 major regions)
REGIONS = {
    'Red River Delta': 0.15,
    'Northeast': 0.12,
    'Northwest': 0.08,
    'North Central': 0.10,
    'South Central Coast': 0.12,
    'Central Highlands': 0.08,
    'Southeast': 0.20,  # Ho Chi Minh area, highest density
    'Mekong Delta': 0.15
}

# Occupations (health risk proxy)
OCCUPATIONS = {
    'Farmer': {'health_risk': 0.25, 'life_risk': 0.20, 'freq': 0.25},
    'Construction Worker': {'health_risk': 0.40, 'life_risk': 0.35, 'freq': 0.10},
    'Factory Worker': {'health_risk': 0.30, 'life_risk': 0.25, 'freq': 0.15},
    'Office Worker': {'health_risk': 0.15, 'life_risk': 0.10, 'freq': 0.20},
    'Merchant/Trader': {'health_risk': 0.20, 'life_risk': 0.15, 'freq': 0.15},
    'Service Industry': {'health_risk': 0.25, 'life_risk': 0.20, 'freq': 0.10},
    'Retired': {'health_risk': 0.45, 'life_risk': 0.60, 'freq': 0.05}
}

def generate_record():
    """Generate single applicant record."""

    # Age: Vietnam population heavily skewed to working age (20-60)
    age = np.random.normal(42, 12)
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

    # Smoking: higher in rural areas, males
    smoking_prob = occ_health_risk * 0.5 + np.random.uniform(0, 0.3)
    is_smoking = np.random.random() < smoking_prob

    # Exercise: inversely correlated with age and occupation risk
    exercise_prob = 0.6 - occ_health_risk * 0.3 - (age - 40) * 0.005
    exercise_prob = np.clip(exercise_prob, 0.1, 0.9)
    is_exercise = np.random.random() < exercise_prob

    # BMI: correlated with age and sedentary occupation
    base_bmi = 22 + (age - 40) * 0.05 + occ_health_risk * 3
    bmi = np.random.normal(base_bmi, 2.5)
    bmi = np.clip(bmi, 17, 42)

    # Pre-existing conditions (multiple possible)
    pre_existing = []
    conditions_risk = occ_health_risk + (age - 40) * 0.01 + (bmi - 25) * 0.02

    if np.random.random() < np.clip(conditions_risk * 0.2, 0, 0.4):
        pre_existing.append('Hypertension')
    if np.random.random() < np.clip(conditions_risk * 0.15, 0, 0.35):
        pre_existing.append('Diabetes')
    if np.random.random() < np.clip(conditions_risk * 0.10, 0, 0.25):
        pre_existing.append('Heart Disease')
    if np.random.random() < np.clip(conditions_risk * 0.08, 0, 0.20):
        pre_existing.append('COPD/Asthma')
    if np.random.random() < np.clip(conditions_risk * 0.05, 0, 0.15):
        pre_existing.append('Arthritis')

    conditions_str = '; '.join(pre_existing) if pre_existing else 'None'

    # Income proxy (based on occupation and region)
    region_income_factor = 1.0 if region == 'Southeast' else 0.8
    occupation_income = {
        'Farmer': 100,
        'Construction Worker': 120,
        'Factory Worker': 110,
        'Office Worker': 150,
        'Merchant/Trader': 140,
        'Service Industry': 100,
        'Retired': 80
    }
    monthly_income = occupation_income[occupation] * region_income_factor + np.random.normal(0, 20)
    monthly_income = np.clip(monthly_income, 50, 300)

    # Health status score (0-100, inverse of risk factors)
    health_score = 100 - (conditions_risk * 30 + (bmi - 25) * 2 + (age - 40) * 0.5)
    health_score = np.clip(health_score, 20, 95)

    # Mortality risk multiplier (life insurance indicator)
    mortality_multiplier = 1.0
    mortality_multiplier += (age - 40) * 0.02  # Age factor
    mortality_multiplier += occ_life_risk * 2  # Occupation risk
    mortality_multiplier += 0.2 if is_smoking else 0  # Smoking surcharge
    mortality_multiplier -= 0.1 if is_exercise else 0  # Exercise discount
    mortality_multiplier += len(pre_existing) * 0.3  # Conditions surcharge

    mortality_multiplier = np.clip(mortality_multiplier, 0.5, 5.0)

    # Family history (simple proxy for genetic risk)
    has_family_history = np.random.random() < (occ_health_risk * 0.3 + 0.1)

    return {
        'applicant_id': None,  # Will be set in loop
        'age': age,
        'region': region,
        'occupation': occupation,
        'is_smoking': int(is_smoking),
        'is_exercise': int(is_exercise),
        'bmi': round(bmi, 1),
        'pre_existing_conditions': conditions_str,
        'monthly_income_millions_vnd': round(monthly_income, 1),
        'health_score': round(health_score, 1),
        'has_family_history': int(has_family_history),
        'mortality_multiplier': round(mortality_multiplier, 2),
        'application_date': None  # Will be set in loop
    }


def main():
    """Generate 2,000 synthetic Vietnam records."""

    print("Generating synthetic Vietnam dataset (2,000 records)...")

    records = []
    base_date = datetime(2024, 1, 1)

    for i in range(2000):
        record = generate_record()
        record['applicant_id'] = f'VN-{i+1:05d}'

        # Application date: spread over 12 months
        days_offset = np.random.randint(0, 365)
        record['application_date'] = (base_date + timedelta(days=days_offset)).strftime('%Y-%m-%d')

        records.append(record)

        if (i + 1) % 500 == 0:
            print(f"  Generated {i + 1} records...")

    # Create DataFrame
    df = pd.DataFrame(records)

    # Output to CSV
    csv_path = r'C:\DAC-UW-Agent\case-study\vietnam_dataset.csv'
    df.to_csv(csv_path, index=False)
    print(f"\nSaved to: {csv_path}")

    # Output to Parquet (more efficient)
    parquet_path = r'C:\DAC-UW-Agent\case-study\vietnam_dataset.parquet'
    df.to_parquet(parquet_path, index=False)
    print(f"Saved to: {parquet_path}")

    # Print summary stats
    print("\nDataset Summary:")
    print(f"  Total records: {len(df)}")
    print(f"  Age range: {df['age'].min()}-{df['age'].max()} (mean: {df['age'].mean():.1f})")
    print(f"  BMI range: {df['bmi'].min():.1f}-{df['bmi'].max():.1f} (mean: {df['bmi'].mean():.1f})")
    print(f"  Smoking rate: {df['is_smoking'].mean()*100:.1f}%")
    print(f"  Exercise rate: {df['is_exercise'].mean()*100:.1f}%")
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
