# CHAPTER III. METHODOLOGY

---

## 3.1 Dataset and Feature Engineering

### 3.1.1 Synthetic Cambodia Health Insurance Dataset

[Describe the 2,000-record synthetic dataset. Source: `case-study/generate_cambodia_dataset.py`. Include demographic calibration, disease prevalence (TB, Hepatitis B), regional distribution, occupational mix.]

### 3.1.2 Feature Categories and Encoding

[Table of feature categories: Demographics (7 numeric), Health Conditions (7 binary flags), Region (6 one-hot), Occupation (7 one-hot), Economic (income). Total 25 features. Explain the critical design choice of one-hot vs label encoding.]

### 3.1.3 Train-Test Split and Reference Distribution

[Describe the data split used for the static XGB baseline and the bandit simulation design.]

---

## 3.2 Bandit Algorithms and Baselines

### 3.2.1 LinUCB

[Formal description of the algorithm, update rules, hyperparameters (alpha = 1.0).]

### 3.2.2 LinTS

[Bayesian formulation, posterior sampling procedure, hyperparameters (v2 = 1.0).]

### 3.2.3 Epsilon-Greedy

[Simple random exploration baseline, epsilon = 0.15.]

### 3.2.4 Static XGBoost Baseline

[Pre-trained XGBoost classifier + deterministic rule engine. Explain how it maps predicted risk to actions.]

---

## 3.3 Reward Design and Actuarial Simulator

### 3.3.1 Profit-Based Reward Formulation

[Base premium formula, expected claims, adverse selection factor, customer acceptance model.]

### 3.3.2 Action-Specific Reward Functions

[Table: STANDARD, RATED, DECLINE, REFER with formulas and constraints.]

### 3.3.3 Design Rationale

[Why opportunity cost for DECLINE (-$10), why REFER net cost (-$42), claims noise reduction.]

---

## 3.4 PSI Guardrails and Fairness Metrics

### 3.4.1 PSI Computation

[Binning strategy, formula, thresholds.]

### 3.4.2 Fairness Constraints

[50% of max approval rate rule.]

### 3.4.3 Integration with Bandit Loop

[How PSI is computed after each batch of decisions and how alerts would trigger intervention.]

---

## 3.5 Experimental Design

### 3.5.1 EXP-005: Convergence Validation

[Hypothesis, setup, pass criteria.]

### 3.5.2 EXP-006: Fairness Audit

[Hypothesis, setup, pass criteria.]

### 3.5.3 EXP-007: Benchmark Comparison

[Hypothesis, setup, pass criteria.]

### 3.5.4 Reproducibility Protocol

[Random seeds, software versions, exit codes.]

---

*Skeleton — content to be expanded.*
