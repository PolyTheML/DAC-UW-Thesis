#!/usr/bin/env python3
"""
Exploratory Data Analysis for Cambodia Health Insurance Dataset.
Generates publication-quality figures for thesis Chapter 4.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Calibri', 'Arial', 'DejaVu Sans']
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.dpi'] = 150

BLUE = '#2E5FA3'
LIGHT_BLUE = '#6B9BD0'
DARK_BLUE = '#1A3A6B'
GRAY = '#7F8C8D'
LIGHT_GRAY = '#E8E8E8'
ORANGE = '#E67E22'
GREEN = '#27AE60'
RED = '#C0392B'
PURPLE = '#8E44AD'
COLORS = [BLUE, ORANGE, GREEN, RED, PURPLE, '#16A085', '#D35400', '#2980B9']

DATA_PATH = Path(r'C:\DAC-UW-Thesis\data\cambodia\cambodia_dataset.csv')
OUT_DIR = Path(r'C:\DAC-UW-Thesis\thesis\health_rl\figures')
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
df = pd.read_csv(DATA_PATH)
print(f"Loaded {len(df)} records with {len(df.columns)} features.")

# Derived features
df['n_conditions'] = df['pre_existing_conditions'].apply(lambda x: 0 if pd.isna(x) or x == 'None' else len(str(x).split('; ')))
df['bmi_category'] = pd.cut(df['bmi'], bins=[0, 18.5, 25, 30, 100], labels=['Underweight', 'Normal', 'Overweight', 'Obese'])

# ---------------------------------------------------------------------------
# Figure 1: Age Distribution by Gender
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
for gender, color in zip(['Female', 'Male'], [BLUE, ORANGE]):
    subset = df[df['gender'] == gender]['age']
    ax.hist(subset, bins=20, alpha=0.7, label=gender, color=color, edgecolor='white', linewidth=0.5)
ax.axvline(df['age'].mean(), color=DARK_BLUE, linestyle='--', linewidth=1.5, label=f"Mean: {df['age'].mean():.1f} yrs")
ax.set_xlabel('Age (years)')
ax.set_ylabel('Count')
ax.set_title('Figure 1. Age Distribution by Gender (n=2,000)')
ax.legend(frameon=False)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / 'fig_eda_01_age_distribution.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved fig_eda_01_age_distribution.png")

# ---------------------------------------------------------------------------
# Figure 2: Regional Distribution
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5))
region_counts = df['region'].value_counts().sort_values(ascending=True)
bars = ax.barh(region_counts.index, region_counts.values, color=BLUE, edgecolor='white', linewidth=0.5)
for bar, val in zip(bars, region_counts.values):
    ax.text(val + 5, bar.get_y() + bar.get_height()/2, f"{val} ({val/len(df)*100:.1f}%)", va='center', fontsize=9)
ax.set_xlabel('Number of Applicants')
ax.set_title('Figure 2. Regional Distribution of Applicants')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / 'fig_eda_02_region_distribution.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved fig_eda_02_region_distribution.png")

# ---------------------------------------------------------------------------
# Figure 3: Occupation Distribution
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5))
occ_counts = df['occupation'].value_counts().sort_values(ascending=True)
bars = ax.barh(occ_counts.index, occ_counts.values, color=ORANGE, edgecolor='white', linewidth=0.5)
for bar, val in zip(bars, occ_counts.values):
    ax.text(val + 3, bar.get_y() + bar.get_height()/2, f"{val} ({val/len(df)*100:.1f}%)", va='center', fontsize=9)
ax.set_xlabel('Number of Applicants')
ax.set_title('Figure 3. Occupational Distribution of Applicants')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / 'fig_eda_03_occupation_distribution.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved fig_eda_03_occupation_distribution.png")

# ---------------------------------------------------------------------------
# Figure 4: BMI Distribution with WHO Categories
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(df['bmi'], bins=25, color=GREEN, alpha=0.7, edgecolor='white', linewidth=0.5)
ax.axvline(18.5, color=ORANGE, linestyle='--', linewidth=1.2, label='Underweight threshold (18.5)')
ax.axvline(25, color=RED, linestyle='--', linewidth=1.2, label='Overweight threshold (25.0)')
ax.axvline(30, color=DARK_BLUE, linestyle='--', linewidth=1.2, label='Obesity threshold (30.0)')
ax.axvline(df['bmi'].mean(), color=PURPLE, linestyle='-', linewidth=1.5, label=f"Mean BMI: {df['bmi'].mean():.1f}")
ax.set_xlabel('BMI (kg/m²)')
ax.set_ylabel('Count')
ax.set_title('Figure 4. BMI Distribution with WHO Classification Thresholds')
ax.legend(frameon=False, loc='upper left')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / 'fig_eda_04_bmi_distribution.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved fig_eda_04_bmi_distribution.png")

# ---------------------------------------------------------------------------
# Figure 5: Education & Wealth Quintile (side by side)
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
edu_order = ['No education', 'Primary', 'Secondary', 'Higher']
edu_counts = df['education'].value_counts().reindex(edu_order)
axes[0].bar(edu_counts.index, edu_counts.values, color=BLUE, edgecolor='white', linewidth=0.5)
axes[0].set_ylabel('Count')
axes[0].set_title('(a) Education Level')
for i, v in enumerate(edu_counts.values):
    axes[0].text(i, v + 10, f"{v}", ha='center', fontsize=9)
axes[0].spines['top'].set_visible(False)
axes[0].spines['right'].set_visible(False)

wealth_order = ['Poorest', 'Poorer', 'Middle', 'Richer', 'Richest']
wealth_counts = df['wealth_quintile'].value_counts().reindex(wealth_order)
axes[1].bar(wealth_counts.index, wealth_counts.values, color=ORANGE, edgecolor='white', linewidth=0.5)
axes[1].set_ylabel('Count')
axes[1].set_title('(b) Wealth Quintile')
for i, v in enumerate(wealth_counts.values):
    axes[1].text(i, v + 10, f"{v}", ha='center', fontsize=9)
axes[1].spines['top'].set_visible(False)
axes[1].spines['right'].set_visible(False)

fig.suptitle('Figure 5. Socioeconomic Characteristics of Applicants', fontsize=14, fontweight='bold')
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(OUT_DIR / 'fig_eda_05_socioeconomic.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved fig_eda_05_socioeconomic.png")

# ---------------------------------------------------------------------------
# Figure 6: Lifestyle Factors by Gender
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
factors = ['is_smoking', 'alcohol_use', 'is_exercise']
factor_labels = ['Smoking', 'Alcohol Use', 'Regular Exercise']
female_vals = [df[df['gender']=='Female'][f].mean()*100 for f in factors]
male_vals = [df[df['gender']=='Male'][f].mean()*100 for f in factors]

x = np.arange(len(factor_labels))
width = 0.35
bars1 = ax.bar(x - width/2, female_vals, width, label='Female', color=BLUE, edgecolor='white')
bars2 = ax.bar(x + width/2, male_vals, width, label='Male', color=ORANGE, edgecolor='white')

for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)

ax.set_ylabel('Prevalence (%)')
ax.set_title('Figure 6. Lifestyle Risk Factors by Gender')
ax.set_xticks(x)
ax.set_xticklabels(factor_labels)
ax.legend(frameon=False)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / 'fig_eda_06_lifestyle_by_gender.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved fig_eda_06_lifestyle_by_gender.png")

# ---------------------------------------------------------------------------
# Figure 7: Monthly Income by Occupation (boxplot)
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))
occ_order = df.groupby('occupation')['monthly_income_usd'].median().sort_values(ascending=False).index
df['occupation'] = pd.Categorical(df['occupation'], categories=occ_order, ordered=True)
df_sorted = df.sort_values('occupation')

bp = ax.boxplot([df_sorted[df_sorted['occupation']==occ]['monthly_income_usd'].values for occ in occ_order],
                labels=occ_order, patch_artist=True, vert=False)
for patch, color in zip(bp['boxes'], COLORS[:len(occ_order)]):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax.set_xlabel('Monthly Income (USD)')
ax.set_title('Figure 7. Monthly Income Distribution by Occupation')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / 'fig_eda_07_income_by_occupation.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved fig_eda_07_income_by_occupation.png")

# ---------------------------------------------------------------------------
# Figure 8: Health Score vs Age (colored by BMI category)
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 6))
bmi_colors = {'Underweight': ORANGE, 'Normal': GREEN, 'Overweight': RED, 'Obese': DARK_BLUE}
for cat in ['Underweight', 'Normal', 'Overweight', 'Obese']:
    subset = df[df['bmi_category'] == cat]
    ax.scatter(subset['age'], subset['health_score'], c=bmi_colors[cat], label=cat, alpha=0.6, s=30, edgecolors='none')

ax.set_xlabel('Age (years)')
ax.set_ylabel('Health Score')
ax.set_title('Figure 8. Health Score vs Age (colored by BMI Category)')
ax.legend(title='BMI Category', frameon=False)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / 'fig_eda_08_health_score_vs_age.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved fig_eda_08_health_score_vs_age.png")

# ---------------------------------------------------------------------------
# Figure 9: Mortality Multiplier Distribution
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(df['mortality_multiplier'], bins=30, color=BLUE, alpha=0.7, edgecolor='white', linewidth=0.5)
ax.axvline(1.0, color=GREEN, linestyle='--', linewidth=1.5, label='Standard risk (1.0)')
ax.axvline(df['mortality_multiplier'].mean(), color=ORANGE, linestyle='-', linewidth=1.5, label=f"Mean: {df['mortality_multiplier'].mean():.2f}")
ax.axvline(df['mortality_multiplier'].median(), color=PURPLE, linestyle='-', linewidth=1.5, label=f"Median: {df['mortality_multiplier'].median():.2f}")
ax.set_xlabel('Mortality Multiplier')
ax.set_ylabel('Count')
ax.set_title('Figure 9. Mortality Multiplier Distribution')
ax.legend(frameon=False)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / 'fig_eda_09_mortality_multiplier.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved fig_eda_09_mortality_multiplier.png")

# ---------------------------------------------------------------------------
# Figure 10: Pre-existing Conditions Prevalence
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5))
all_conditions = []
for conds in df['pre_existing_conditions']:
    if pd.notna(conds) and conds != 'None':
        all_conditions.extend(str(conds).split('; '))
cond_counts = pd.Series(all_conditions).value_counts().sort_values(ascending=True)
bars = ax.barh(cond_counts.index, cond_counts.values / len(df) * 100, color=RED, edgecolor='white', linewidth=0.5)
for bar, val in zip(bars, cond_counts.values):
    ax.text(val/len(df)*100 + 0.2, bar.get_y() + bar.get_height()/2, f"{val/len(df)*100:.1f}%", va='center', fontsize=9)
ax.set_xlabel('Prevalence (%)')
ax.set_title('Figure 10. Pre-existing Conditions Prevalence (n=2,000)')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / 'fig_eda_10_conditions_prevalence.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved fig_eda_10_conditions_prevalence.png")

# ---------------------------------------------------------------------------
# Figure 11: Correlation Heatmap of Numeric Variables
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 7))
numeric_cols = ['age', 'is_smoking', 'alcohol_use', 'is_exercise', 'bmi', 'monthly_income_usd',
                'health_score', 'has_family_history', 'mortality_multiplier', 'n_conditions']
corr = df[numeric_cols].corr()

# Custom colormap
cmap = plt.cm.RdBu_r
im = ax.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1)

ax.set_xticks(np.arange(len(numeric_cols)))
ax.set_yticks(np.arange(len(numeric_cols)))
ax.set_xticklabels([c.replace('_', ' ').title() for c in numeric_cols], rotation=45, ha='right')
ax.set_yticklabels([c.replace('_', ' ').title() for c in numeric_cols])

for i in range(len(numeric_cols)):
    for j in range(len(numeric_cols)):
        text = ax.text(j, i, f'{corr.values[i, j]:.2f}', ha='center', va='center', color='white' if abs(corr.values[i,j]) > 0.5 else 'black', fontsize=8)

ax.set_title('Figure 11. Correlation Matrix of Numeric Features')
fig.colorbar(im, ax=ax, shrink=0.8)
fig.tight_layout()
fig.savefig(OUT_DIR / 'fig_eda_11_correlation_heatmap.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved fig_eda_11_correlation_heatmap.png")

# ---------------------------------------------------------------------------
# Figure 12: Health Score vs BMI (colored by Region)
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 6))
regions = df['region'].unique()
region_colors = dict(zip(regions, COLORS[:len(regions)]))
for region in regions:
    subset = df[df['region'] == region]
    ax.scatter(subset['bmi'], subset['health_score'], c=region_colors[region], label=region, alpha=0.6, s=25, edgecolors='none')
ax.set_xlabel('BMI (kg/m²)')
ax.set_ylabel('Health Score')
ax.set_title('Figure 12. Health Score vs BMI by Region')
ax.legend(title='Region', frameon=False, loc='lower left', ncol=2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / 'fig_eda_12_health_vs_bmi_region.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved fig_eda_12_health_vs_bmi_region.png")

# ---------------------------------------------------------------------------
# Figure 13: Risk Profile by Occupation (Health Score & Mortality)
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))
occ_order2 = df.groupby('occupation')['health_score'].median().sort_values(ascending=True).index
health_med = [df[df['occupation']==occ]['health_score'].median() for occ in occ_order2]
mort_med = [df[df['occupation']==occ]['mortality_multiplier'].median() for occ in occ_order2]

x = np.arange(len(occ_order2))
width = 0.35

ax2 = ax.twinx()
bars1 = ax.bar(x - width/2, health_med, width, label='Health Score (median)', color=GREEN, alpha=0.8, edgecolor='white')
bars2 = ax2.bar(x + width/2, mort_med, width, label='Mortality Multiplier (median)', color=RED, alpha=0.8, edgecolor='white')

ax.set_ylabel('Health Score', color=GREEN)
ax2.set_ylabel('Mortality Multiplier', color=RED)
ax.set_xticks(x)
ax.set_xticklabels(occ_order2, rotation=30, ha='right')
ax.set_title('Figure 13. Risk Profile by Occupation')
ax.tick_params(axis='y', labelcolor=GREEN)
ax2.tick_params(axis='y', labelcolor=RED)

# Combined legend
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, frameon=False, loc='upper right')
ax.spines['top'].set_visible(False)
ax2.spines['top'].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / 'fig_eda_13_risk_by_occupation.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved fig_eda_13_risk_by_occupation.png")

# ---------------------------------------------------------------------------
# Figure 14: Condition Count Distribution
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 5))
cond_dist = df['n_conditions'].value_counts().sort_index()
bars = ax.bar(cond_dist.index.astype(str), cond_dist.values, color=BLUE, edgecolor='white', linewidth=0.5)
for bar, val in zip(bars, cond_dist.values):
    ax.text(bar.get_x() + bar.get_width()/2, val + 5, f"{val} ({val/len(df)*100:.1f}%)", ha='center', fontsize=9)
ax.set_xlabel('Number of Pre-existing Conditions')
ax.set_ylabel('Count')
ax.set_title('Figure 14. Distribution of Pre-existing Condition Count')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / 'fig_eda_14_condition_count.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved fig_eda_14_condition_count.png")

# ---------------------------------------------------------------------------
# Summary statistics CSV
# ---------------------------------------------------------------------------
summary = df[numeric_cols].describe().T
summary['skewness'] = df[numeric_cols].skew()
summary['kurtosis'] = df[numeric_cols].kurtosis()
summary.to_csv(OUT_DIR / 'eda_summary_statistics.csv')
print("Saved eda_summary_statistics.csv")

print("\n=== EDA Complete ===")
print(f"All figures saved to: {OUT_DIR}")
