# CHAPTER IV. PROJECT ANALYSIS AND CONCEPTS

---

This chapter specifies the requirements that the proposed contextual bandit underwriting system must satisfy, identifies the technologies used to implement them, and documents the full methodology. Section 4.1 defines the functional capabilities, organised around the four operational modules of the system. Section 4.2 specifies the non-functional quality attributes. Section 4.3 enumerates the implementation tool stack. Section 4.4 closes with a focused exposition of the core technology — the contextual bandit framework — describing what it is, how it operates, its place in the overall system architecture, and the reasons it was selected over competing alternatives. Section 4.5 describes the synthetic dataset and feature engineering. Section 4.6 specifies the bandit algorithms and baselines. Section 4.7 details the reward design and actuarial simulator. Section 4.8 documents the PSI guardrails and fairness metrics. Section 4.9 presents the experimental design for the three core validation experiments (EXP-005 through EXP-007); the human-in-the-loop experiment (EXP-008) is reported in §5.4. Section 4.10 outlines the implementation and deployment roadmap.

---

## 4.1 Functional Requirements

The functional requirements are organised into four module groups, each of which addresses one or more of the three problems identified in Section 1.2: suboptimal risk selection, inability to adapt to portfolio drift, and demographic fairness violations. Table 4.1 maps each module group to the problems it resolves, providing forward traceability between requirements and motivation.

**Table 4.1 — Functional requirement groups mapped to research problems (§1.2).**

| FR Group | Module | Problem 1 (Risk selection) | Problem 2 (Drift adaptation) | Problem 3 (Fairness) |
|----------|--------|:---:|:---:|:---:|
| FR-1 | Applicant Simulation & Risk Assessment | ● | ● | — |
| FR-2 | Dynamic Premium Optimisation | ● | — | — |
| FR-3 | Bandit Algorithm Arena & Benchmarking | ● | ● | — |
| FR-4 | PSI Drift Monitor & Fairness Audit | — | ● | ● |

### 4.1.1 FR-1 — Applicant Simulation and Risk Assessment

The system generates and scores individual Cambodian health insurance applicants drawn from a synthetic 2,000-record dataset calibrated to the Cambodia Demographic and Health Survey (CDHS) 2021–22.

- **FR-1.1** Generate random applicant profiles containing demographics (age, gender, region, education, wealth quintile), health indicators (BMI, smoking, alcohol use, exercise, self-reported health, pre-existing conditions), occupational risk class, and monthly income.
- **FR-1.2** Compute deterministic expected rewards for all four underwriting actions (STANDARD, RATED, DECLINE, REFER) using the actuarial profit simulator (premium revenue, expected claims with adverse-selection adjustment, customer acceptance probability, expense load, lapse probability, customer lifetime value).
- **FR-1.3** Run stochastic realisations that draw a customer accept/reject outcome and a sampled claim cost, returning the realised profit or loss for the chosen action.

### 4.1.2 FR-2 — Dynamic Premium Optimisation

The system extends the four discrete actions with a continuous pricing layer that searches for the profit-maximising premium for a given applicant.

- **FR-2.1** Grid-search the optimal premium multiplier in the range 0.5×–3.0× of base premium for a single applicant.
- **FR-2.2** Display the resulting profit curve across all multipliers with the customer acceptance probability overlaid on a secondary axis.
- **FR-2.3** Compare the optimised continuous premium against the legacy four-action decision (STANDARD / RATED / DECLINE / REFER).
- **FR-2.4** Run batch optimisation on 100 sampled applicants and produce portfolio-level statistics (mean and median multipliers, histogram, summary table).

### 4.1.3 FR-3 — Bandit Algorithm Arena and Benchmarking

The system supports head-to-head experimental comparison of contextual bandit algorithms against the static XGBoost baseline.

- **FR-3.1** Execute single-algorithm simulations (LinUCB, Linear Thompson Sampling, Epsilon-Greedy, Static XGB) for a configurable number of rounds (100–10,000), updating bandit state after each decision.
- **FR-3.2** Visualise cumulative reward, cumulative regret, and action-distribution trajectories over time.
- **FR-3.3** Run all four algorithms head-to-head on the same random seed and render dual cumulative reward and regret charts.
- **FR-3.4** Expose hyperparameter controls (α for LinUCB, v² for LinTS, ε for Epsilon-Greedy) for sensitivity analysis.

### 4.1.4 FR-4 — PSI Drift Monitor and Fairness Audit

The system implements Population Stability Index (PSI) guardrails to detect demographic drift and verify approval-rate parity across protected segments.

- **FR-4.1** Compute PSI between the applicant pool and the approved portfolio across region, occupation, age band, and wealth quintile dimensions.
- **FR-4.2** Display traffic-light status cards classifying each PSI value as GREEN (< 0.10), AMBER (0.10–0.25), or RED (> 0.25).
- **FR-4.3** Render PSI bar charts for visual drift inspection.
- **FR-4.4** Validate the fairness constraint that no regional or occupational segment exhibits an approval rate below 50% of the maximum observed segment rate.

---

## 4.2 Non-Functional Requirements

Non-functional requirements specify the quality attributes and operational constraints under which the system must perform. The eight requirements in Table 4.2 reflect the deployment context — low-resource mobile infrastructure in an emerging market — and the academic context — reproducibility for examiner replication and regulator audit.

**Table 4.2 — Non-functional requirements.**

| ID | Category | Requirement | Rationale |
|----|----------|-------------|-----------|
| NFR-1 | Performance | Decision latency below 200 ms on standard CPU hardware. | Cambodian mobile distribution lacks GPU servers; the system must run on commodity infrastructure. |
| NFR-2 | Performance | A 5,000-round bandit simulation completes within 30 seconds. | Enables interactive demonstration and rapid experimentation for examiner and stakeholder sessions. |
| NFR-3 | Reproducibility | All experiments produce identical results when rerun with a fixed random seed (default SEED = 42). | Required for scientific validation and for reconstruction of the audit trail. |
| NFR-4 | Portability | Pure Python stack deployable on any VPS or Render free tier. | Avoids proprietary licences and cloud lock-in; supports adoption in markets with limited cloud budgets. |
| NFR-5 | Maintainability | Modular code structure separating data generation, algorithm implementation, API routing, and frontend assets. | Enables extension with new algorithms or PSI dimensions without rewriting unrelated subsystems. |
| NFR-6 | Accuracy | PSI computations in the demonstration interface match the values produced by experiment EXP-006 to four decimal places. | Guarantees consistency between research code and production demo so that reviewers can verify reported results. |
| NFR-7 | Interpretability | Per-action coefficient vectors θ_a remain inspectable for LinUCB and LinTS. | Linear bandits, unlike neural alternatives, expose explicit feature weights for actuarial review and regulatory explanation. |
| NFR-8 | Auditability | Every decision tuple (context, action, reward, PSI status, timestamp) is immutably logged. | The decision log is the regulator-facing artefact; auditors must be able to reconstruct any historical decision from it. |

---

## 4.3 Tool and Technology Requirements

The technology stack is selected to satisfy three constraints simultaneously: scientific reproducibility (NFR-3), low-resource deployability (NFR-1, NFR-4), and academic transparency. All components are open-source, well-documented, and widely adopted in either actuarial practice or machine learning research. The stack is grouped into three categories: backend and data science (Section 4.3.1), frontend and visualisation (Section 4.3.2), and deployment and development (Section 4.3.3).

### 4.3.1 Backend and Data Science Stack

**Table 4.3a — Backend and data science components.**

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11 | Primary implementation language; chosen for its scientific computing ecosystem and clear syntax suitable for academic reproducibility. |
| FastAPI | ≥ 0.110 | Asynchronous web framework powering the REST API; provides native async support and automatic OpenAPI documentation. |
| Uvicorn | ≥ 0.29 | ASGI server hosting the FastAPI application in development and production. |
| Pydantic | ≥ 2.6 | Request and response schema validation, ensuring applicant payloads conform to expected types and ranges. |
| NumPy | ≥ 1.26 | Dense linear algebra (matrix inversion, outer products, multivariate normal sampling) underlying LinUCB and LinTS updates. |
| Pandas | ≥ 2.2 | Tabular data manipulation for dataset generation, feature engineering, and batch scoring. |
| scikit-learn | ≥ 1.4 | Preprocessing utilities (LabelEncoder for categorical variables, scaling helpers). |
| XGBoost | ≥ 2.0 | Gradient-boosted mortality predictor used as the static baseline against which bandits are benchmarked. |
| SQLAlchemy | 2.0 (async) | Object-relational mapper for shadow-mode decision logging (NFR-8). |

### 4.3.2 Frontend and Visualisation

**Table 4.3b — Frontend and visualisation components.**

| Tool | Version | Purpose |
|------|---------|---------|
| HTML5 / CSS3 | — | Markup and styling for the single-page demonstration. |
| Vanilla JavaScript | ES6+ | Frontend interactivity, API calls, and DOM manipulation; avoids framework lock-in for a small SPA. |
| Chart.js | 4.x | Interactive line, bar, and pie charts for cumulative reward, regret, and PSI visualisation. |
| Jinja2 | ≥ 3.1 | Server-side HTML templating embedded in the FastAPI application. |
| Matplotlib | ≥ 3.8 | Generation of all static figures used in this thesis (cumulative reward curves, regret trajectories, fairness diagnostics, architecture diagrams). |

### 4.3.3 Deployment and Development

**Table 4.3c — Deployment and development components.**

| Tool | Version | Purpose |
|------|---------|---------|
| Render | Cloud PaaS | Free-tier hosting with automatic deployment on git push; meets the portability constraint (NFR-4). |
| Git | — | Version control and collaboration; underpins the reproducibility constraint (NFR-3). |
| python-dotenv | ≥ 1.0 | Environment variable management for separating development and production configuration. |
| pytest | ≥ 8.0 | Test runner for the automated suite; each experiment script (EXP-005 to EXP-008) embeds explicit pass/fail assertions and an exit code, doubling as scientific validation and regression test. |

---

## 4.4 Detail Concept — Contextual Bandits

The technology at the centre of this thesis is the contextual bandit. Because every functional and non-functional requirement above is shaped by the choice of this learning paradigm, the present section provides a focused treatment in four parts: definition, mechanism, system architecture, and selection rationale.

### 4.4.1 What is a Contextual Bandit?

A contextual bandit is a reinforcement learning framework in which an agent repeatedly observes a context vector, selects an action from a finite set, and receives a reward whose distribution depends on both the context and the chosen action. Unlike full reinforcement learning, the contextual bandit assumes no state transitions: each round is statistically independent except through the parameters the agent has learned from previous rounds. This restriction discards the modelling burden of a Markov decision process and yields algorithms that are computationally lightweight, statistically tractable, and theoretically well understood, which makes them well suited to high-stakes sequential decision problems such as health insurance underwriting.

### 4.4.2 How Does It Work?

The contextual bandit underwriting loop proceeds in five steps per applicant.

1. **Context observation.** At round *t*, the algorithm observes the applicant feature vector *x_t* ∈ ℝ^d, where d = 34 in this implementation (age, BMI, region one-hot, occupation one-hot, health flags, income).
2. **Action selection.** For each action *a* ∈ {STANDARD, RATED, DECLINE, REFER}, the algorithm estimates the expected reward and adds an exploration term. LinUCB adds an upper-confidence bonus α·√(x_tᵀ A_a⁻¹ x_t); LinTS samples θ_a from its posterior; Epsilon-Greedy chooses the empirical maximum with probability 1−ε and explores uniformly otherwise.
3. **Reward observation.** The selected action is executed by the actuarial simulator, which returns a stochastic reward composed of premium revenue, expected claims, customer acceptance, and expense loadings.
4. **Parameter update.** The algorithm updates its parameter estimates using the observed (*x_t*, *a_t*, *r_t*) triple. For LinUCB and LinTS this is a rank-one update of the per-action precision matrix A_a and reward vector b_a, completed in O(d²) operations.
5. **Repeat.** Steps 1–4 continue for *T* rounds. Cumulative regret — the gap between the algorithm's total reward and the oracle optimal policy — quantifies learning quality.

### 4.4.3 Architecture

Figure 4.1 shows the end-to-end architecture of the demonstration system. The browser frontend exposes four interaction tabs (Applicant Simulator, Premium Optimiser, Bandit Arena, PSI Monitor); each issues HTTP requests to the FastAPI backend, which dispatches to one of six core modules (Actuarial Reward Simulator, Pricing Engine, Bandit Algorithms, PSI Compute, Cambodia Dataset, Static XGB Baseline). The bandit decision loop itself, isolated from infrastructural concerns, is shown in Figure 4.2.

[FIGURE 4.1: System architecture — Browser tabs → FastAPI endpoints → backend modules. Source: `figures/fig_ch4_architecture.png`.]

[FIGURE 4.2: Contextual bandit decision loop — context x_t → action selection → reward r_t → parameter update (A_a, b_a) → next round. Source: `figures/fig_ch4_bandit_loop.png`.]

### 4.4.4 Why Contextual Bandits Were Chosen

Six properties distinguish contextual bandits from competing approaches and motivate their use in this thesis.

1. **Computational efficiency.** LinUCB and LinTS perform their per-round update in milliseconds on commodity CPU hardware, satisfying the 200 ms latency budget (NFR-1).
2. **Theoretical regret guarantees.** Both algorithms achieve sublinear regret of order O(d√T), so performance improves predictably as more applicants are processed and the optimality gap shrinks asymptotically to zero.
3. **No batch retraining.** Unlike static XGBoost models that require periodic offline retraining cycles, bandits learn online from each new decision, eliminating the operational cost and stale-model risk of scheduled retraining.
4. **Interpretability.** Linear bandits maintain explicit per-action coefficient vectors θ_a, allowing actuaries and regulators to inspect which features drive each decision (NFR-7) — a property that neural bandits do not provide.
5. **Fairness compatibility.** Because the reward function need not encode demographic parity, fairness can be monitored externally via PSI guardrails (FR-4), decoupling profitability from demographic constraints and avoiding the adversarial dynamics of constrained-reward formulations.
6. **Emerging-market data fit.** With only 2,000 calibrated records available, deep neural approaches risk overfitting. Linear bandits with d = 34 features achieve strong generalisation under this sample budget while remaining flexible enough to capture the dominant feature interactions identified in the literature.

---

## 4.5 Dataset and Feature Engineering

### 4.5.1 Synthetic Cambodia Health Insurance Dataset

The empirical foundation of this thesis is a synthetic dataset of 2,000 Cambodian health-insurance applicants generated by `case-study/generate_cambodia_dataset.py`.  Every record is statistically anchored on the **Cambodia Demographic and Health Survey (CDHS) 2021–22** [National Institute of Statistics / ICF, 2023], with complementary calibration from the Cambodia STEPS Survey 2023 (MoH/WHO), the 2019 General Population Census, the ILO Cambodia Labour Force Survey 2023, and WHO disease-burden reports.

**Demographic calibration.**  Age is drawn from a gamma distribution (shape = 3.8, scale = 4.2, shifted +18) calibrated to the CDHS working-adult mean (~30.9 years for women, ~32.5 for men) but skewed slightly older to reflect the stable-income population most likely to purchase insurance.  Gender is occupation-conditional: the dataset respects documented labour-market sex ratios (e.g., 85 % female in garment factories, 90 % male in construction) rather than applying a uniform 52.2 % / 47.8 % population split.

**Regional distribution** follows the CDHS 2021–22 province-level respondent shares for adults aged 15–49, collapsed into eight macro regions: Phnom Penh (16.2 %), Kandal (7.4 %), Kampong Cham (10.3 %), Siem Reap (7.9 %), Battambang (6.9 %), Prey Veng (6.3 %), Preah Sihanouk (1.2 %), and Other Provinces (43.6 %).  Urban provinces receive higher education and wealth quintile probabilities, reproducing the well-documented rural–urban gradient in Cambodian socioeconomic indicators.

**Occupational mix** reflects the ILO 2023 sectoral composition and is parametrised by base health risk, life risk, frequency, and income base: Rice Farmer (28 %), Garment Worker (20 %), Market Vendor (15 %), Moto/Tuk-tuk Driver (12 %), Civil Servant (10 %), Construction Worker (8 %), and Monk/Retired (7 %).  Each occupation carries a distinct mortality multiplier that feeds directly into the actuarial reward simulator.

**Disease prevalence** is condition-specific and probability-linked to age, BMI, occupation risk, education, and wealth:

| Condition | Source Prevalence | Key Risk Drivers |
|-----------|-------------------|------------------|
| Hypertension | 16.8 % (STEPS 2023, ages 18–69) | Age ≥ 45, BMI ≥ 25, smoking |
| Diabetes | 7.6 % (STEPS 2023, ages 25–64) | Age ≥ 40, BMI ≥ 25, richest quintile |
| Heart Disease | ~4 % (GBD 2019) | Age ≥ 50, smoking |
| COPD/Asthma | ~3.5 % / ~4 % (WHO 2020) | Smoking |
| Arthritis | Low baseline | Age ≥ 50 |
| TB | 246 / 100k (WHO Global TB Report 2022) | Poorest quintile, rural region |
| Hepatitis B | ~7.5 % surface antigen (WHO 2019) | Baseline population risk |

Multiple conditions can co-occur in a single applicant; the mean condition count is approximately 1.1.  A composite **health score** (0–100, inverse of risk) and a **mortality multiplier** (1.0 = standard actuarial rate) are computed deterministically from the full feature vector and serve as the primary inputs to premium pricing and underwriting decisions.

### 4.5.2 Feature Categories and Encoding

After one-hot encoding of categorical variables and normalisation, each applicant is represented by a 34-dimensional real-valued context vector $x_t \in \mathbb{R}^{34}$.  Table 4.5.2 breaks the raw features into four categories.

**Table 4.5.2 — Feature categories and encoding scheme**

| Category | Raw Features | Encoded Dim. | Encoding |
|----------|-------------|--------------|----------|
| Demographics & vitals | age, gender, BMI | 3 | Numeric, z-scored |
| Lifestyle behaviours | is_smoking, alcohol_use, is_exercise | 3 | Binary, z-scored |
| Social determinants | education, wealth_quintile, self_reported_health | 3 | Ordinal 0–3 / 0–4 / 0–2, z-scored |
| Economic | monthly_income_usd, has_family_history | 2 | Numeric / binary, z-scored |
| Clinical flags | Hypertension, Diabetes, Heart Disease, COPD/Asthma, Arthritis, TB, Hepatitis B | 7 | Binary, z-scored |
| Clinical aggregate | condition_count | 1 | Numeric, z-scored |
| Region | Phnom Penh, Kandal, Kampong Cham, Siem Reap, Battambang, Prey Veng, Preah Sihanouk, Other Provinces | 8 | One-hot, z-scored |
| Occupation | Rice Farmer, Garment Worker, Market Vendor, Moto/Tuk-tuk Driver, Civil Servant, Construction Worker, Monk/Retired | 7 | One-hot, z-scored |
| **Total** | | **34** | |

A critical design choice is the **one-hot encoding of region and occupation** for the bandit preprocessor, versus the **label encoding** used for the static XGBoost baseline.  Linear bandit algorithms (LinUCB, LinTS, Epsilon-Greedy) assume a linear relationship between context features and expected reward; assigning arbitrary integer labels (e.g., 0–7) to regions would impose an artificial ordinal structure (Phnom Penh < Kandal < ...) that does not exist geographically.  One-hot encoding removes this false ordering, at the cost of increasing dimensionality from 21 to 34.  The static XGB baseline, being a tree ensemble, is insensitive to ordinal encoding and therefore uses the more compact 21-feature representation (label-encoded region and occupation) on which it was originally trained.  All 34 features are standardised to zero mean and unit variance before entering the bandit algorithms.

### 4.5.3 Train-Test Split and Reference Distribution

The static XGBoost baseline requires a separate training phase.  The full 2,000-record dataset is split 80 / 20 (train / test) with `random_state = 42` via `sklearn.model_selection.train_test_split`.  The training fold (1,600 records) is used to fit the XGBoost mortality-predictor and the accompanying GLM baseline; the hold-out fold (400 records) is reserved for out-of-sample performance diagnostics (MAE, RMSE, $R^2$).  Feature statistics (mean and standard deviation) are computed on the full dataset so that the bandit preprocessor applies consistent normalisation across all rounds.

The contextual bandit experiments do *not* use a train-test split in the conventional sense.  Instead, the bandit interacts with the full 2,000-record pool sequentially: at round $t$ the next applicant is sampled uniformly without replacement until the pool is exhausted, at which point the indices are reshuffled and sampling resumes.  Over $N = 5,000$ rounds each applicant is seen 2.5 times on average, mimicking a steady stream of new applications drawn from the same underlying population distribution.  This design ensures that the bandit's learning curve is not confounded by a finite-sample exhaustion effect, while preserving the empirical joint distribution of features observed in the Cambodia dataset.

---

## 4.6 Bandit Algorithms and Baselines

### 4.6.1 LinUCB

LinUCB (Li et al., 2010) is a frequentist algorithm that maintains, for each action $a$, a ridge-regression estimate of the unknown parameter vector $\theta_a$ and adds an exploration bonus proportional to the standard deviation of that estimate.  At round $t$ the learner observes context $x_t \in \mathbb{R}^d$ and selects the action that maximises the upper confidence bound:

$$a_t = \arg\max_{a \in \mathcal{A}} \Bigl( \hat\theta_a(t)^\top x_t + \alpha \sqrt{x_t^\top A_a(t)^{-1} x_t} \Bigr)$$

where $\hat\theta_a(t) = A_a(t)^{-1} b_a(t)$ is the regularised least-squares estimate, $A_a(t) = I_d + \sum_{s: a_s = a} x_s x_s^\top$ is the design matrix, and $b_a(t) = \sum_{s: a_s = a} r_s x_s$ is the response vector.  The scalar $\alpha = 1.0$ controls the width of the confidence ellipsoid and therefore the exploration–exploitation trade-off; larger $\alpha$ encourages more exploration.

After observing reward $r_t$, the sufficient statistics for the chosen action are updated via rank-one increments:

$$A_{a_t} \leftarrow A_{a_t} + x_t x_t^\top, \qquad b_{a_t} \leftarrow b_{a_t} + r_t x_t.$$

To avoid the $O(d^3)$ cost of explicitly inverting $A_a$ at every round, the implementation uses the Sherman–Morrison formula to maintain $A_a^{-1}$ in $O(d^2)$ time:

$$A_a^{-1} \leftarrow A_a^{-1} - \frac{A_a^{-1} x_t x_t^\top A_a^{-1}}{1 + x_t^\top A_a^{-1} x_t}.$$

Initialisation follows the standard choice $A_a(0) = I_d$ and $b_a(0) = \mathbf{0}$, which corresponds to a zero-mean Gaussian prior with unit covariance.

### 4.6.2 LinTS

Linear Thompson Sampling (Agrawal & Goyal, 2013) replaces the deterministic confidence bonus of LinUCB with randomised posterior sampling.  It maintains the same sufficient statistics $(A_a, b_a)$ but treats them as the posterior parameters of a Gaussian distribution over $\theta_a$.  At each round it samples a candidate parameter vector from the posterior and acts greedily with respect to that sample:

$$\tilde\theta_a \sim \mathcal{N}\bigl( \hat\theta_a,\; v^2 A_a^{-1} \bigr), \qquad a_t = \arg\max_{a \in \mathcal{A}} \tilde\theta_a^\top x_t.$$

The hyperparameter $v^2 = 1.0$ scales the posterior covariance and therefore the amplitude of exploration.  When the posterior is wide (early rounds or rarely selected actions), samples are dispersed and the algorithm explores; when the posterior narrows (late rounds or well-understood contexts), samples concentrate near $\hat\theta_a$ and the algorithm exploits.  Unlike LinUCB, Thompson Sampling requires no tuning of an explicit exploration parameter such as $\alpha$; the variance $v^2$ can be fixed or calibrated offline via empirical Bayes.

The update of $(A_a, b_a)$ is identical to LinUCB.  To avoid the expensive singular-value decomposition required by `numpy.random.multivariate_normal`, the implementation pre-computes and caches the Cholesky factor of $v^2 A_a^{-1} + 10^{-6} I_d$, yielding sampling in $O(d^2)$ time.

### 4.6.3 Epsilon-Greedy

Epsilon-Greedy serves as a simple baseline that separates exploration and exploitation explicitly rather than through a statistically principled confidence measure.  With probability $\varepsilon = 0.15$ it selects a uniformly random action; with probability $1 - \varepsilon$ it selects the action with highest estimated expected reward:

$$a_t = \begin{cases} \text{Uniform}(\mathcal{A}) & \text{with probability } \varepsilon, \\ \arg\max_a \hat\theta_a^\top x_t & \text{otherwise}. \end{cases}$$

The parameter estimates $\hat\theta_a = A_a^{-1} b_a$ are maintained via the same online least-squares update as LinUCB and LinTS.  Epsilon-Greedy is included to illustrate the cost of *non-adaptive* exploration: it continues to randomise 15 % of decisions even after thousands of rounds have been observed, whereas UCB and Thompson Sampling automatically shrink exploration as confidence grows.

### 4.6.4 Static XGBoost Baseline

The static baseline combines a pre-trained XGBoost regressor with a fixed deterministic rule engine.  The model is trained on 1,600 records (80 % split) to predict the **mortality multiplier** from 21 label-encoded features (region and occupation are encoded as integers 0–7 rather than one-hot vectors).  At decision time, the model outputs a predicted mortality multiplier $\hat{m}$ for the applicant, and the rule engine maps this to one of four underwriting actions:

| Rule | Condition | Action |
|------|-----------|--------|
| R1 | $\hat{m} \le 1.5$ | STANDARD |
| R2 | $1.5 < \hat{m} \le 2.2$ | RATED (+25 %) |
| R3 | $2.2 < \hat{m} \le 2.6$ | REFER |
| R4 | $\hat{m} > 2.6$ | DECLINE |

The thresholds (1.5, 2.2, 2.6) were chosen to partition the mortality distribution into actuarially meaningful segments: low standard risk, moderate rated risk, elevated risk requiring manual review, and unacceptably high risk.  Because the static baseline does not learn from feedback, its `update()` method is a no-op; it serves as a fixed-policy benchmark against which the adaptive algorithms' regret is measured.

---

## 4.7 Reward Design and Actuarial Simulator

### 4.7.1 Profit-Based Reward Formulation

The actuarial reward simulator computes the profit or loss associated with each underwriting action for a given applicant.  All monetary values are expressed in US dollars, reflecting the heavily dollarised Cambodian formal-sector economy.

**Base premium and expected claims.**  The annual base premium is proportional to the applicant's mortality multiplier $m$:

$$P_{\text{base}} = 200 \times m \quad \text{(USD/year)}.$$

Expected claims are similarly scaled:

$$C_{\text{exp}} = 150 \times m \quad \text{(USD/year)}.$$

**Adverse-selection adjustment.**  Applicants with $m > 2.0$ are assumed to represent an adverse-selection pool: if offered standard terms, their expected claims are inflated by a factor of 1.35 to reflect the informational advantage held by high-risk applicants who self-select into standard coverage:

$$C_{\text{std}} = C_{\text{exp}} \times \begin{cases} 1.0 & m \le 2.0, \\ 1.35 & m > 2.0. \end{cases}$$

The RATED action (+25 % premium) does not incur this adverse-selection penalty because the higher price is assumed to screen out the worst risks.

**Customer acceptance model.**  Not every quoted premium results in a bound policy.  The probability that an applicant accepts a monthly premium $p_{\text{monthly}} = P / 12$ decreases linearly with the premium-to-income ratio:

$$p_{\text{accept}} = \max\Bigl(0.05,\; 0.95 - 3.5 \times \frac{p_{\text{monthly}}}{\text{income}}\Bigr).$$

The intercept 0.95 captures near-universal acceptance when the premium is negligible; the slope 3.5 ensures that a premium exceeding ~27 % of monthly income drives acceptance below 5 %, at which point the applicant is effectively lost.  In the stochastic simulator, if the customer rejects the offer the insurer incurs a **walk cost** of $-\$20$ (acquisition marketing sunk cost); in the expected-value formulation used for the bandit reward, the corresponding **processing cost** is $-\$25$, representing the deterministic underwriting staff time and system overhead consumed for every quoted applicant whether or not they accept.

### 4.7.2 Action-Specific Reward Functions

Table 4.7.2 summarises the reward computation for each of the four underwriting actions.  All expressions use the expected-value formulation (deterministic oracle); the stochastic simulator adds claims noise $\nu_t \sim \text{Uniform}(0.92, 1.08)$ and a Bernoulli acceptance draw.

**Table 4.7.2 — Action-specific reward functions (expected value)**

| Action | Premium | Claims | Acceptance | Net Reward Formula |
|--------|---------|--------|------------|-------------------|
| STANDARD | $P_{\text{base}}$ | $C_{\text{exp}} \times \gamma_{\text{adv}}$ | $p_{\text{std}}$ | $r_{\text{std}} = p_{\text{std}}(P_{\text{base}} - C_{\text{std}}) + (1-p_{\text{std}})(-25)$ |
| RATED | $1.25 \, P_{\text{base}}$ | $C_{\text{exp}}$ | $p_{\text{rtd}}$ | $r_{\text{rtd}} = p_{\text{rtd}}(1.25 P_{\text{base}} - C_{\text{exp}}) + (1-p_{\text{rtd}})(-25)$ |
| DECLINE | — | — | — | $r_{\text{dcl}} = -10$ |
| REFER | — | — | — | $r_{\text{ref}} = 0.70 \times \max(r_{\text{std}}, r_{\text{rtd}}, r_{\text{dcl}}) - 35$ |

The $-\$25$ term in the STANDARD and RATED rows is the **processing cost** (`config.processing_cost` in `underwriting_bandit.py`) charged whenever the applicant is quoted but does not bind a policy: it covers underwriting staff time and system overhead.  In the stochastic simulator, claims are multiplied by $\nu_t$, acceptance is drawn from $\text{Bernoulli}(p_{\text{accept}})$, and the unbound case incurs the slightly different walk cost of $-\$20$ (`config.walk_cost`); the two values differ because the expected-value formula amortises a deterministic overhead while the stochastic walk cost models the acquisition-marketing sunk cost only.

### 4.7.3 Design Rationale

The reward design encodes three actuarial intuitions beyond simple profit maximisation.

**Opportunity cost of DECLINE ($-$10$).**  Declining an applicant is not costless: underwriting staff have already reviewed the file, IT systems have processed the data, and the insurer forgoes the upside of a potentially profitable policy.  The $-$10$ figure represents an administrative opportunity cost rather than a cash outflow.  Without this penalty, a myopic algorithm might decline every borderline applicant to avoid claims variance; the small negative reward forces the bandit to compare the certain loss of $-$10$ against the uncertain but potentially positive expected profit of STANDARD or RATED.

**Net cost of REFER ($-$35$ admin + 70 % efficiency).**  The REFER action models the real-world practice of routing complex cases to a senior underwriter or medical reviewer.  The 70 % efficiency factor captures the reality that human review is imperfect: some profitable cases are declined out of conservatism, and some risky cases are approved through oversight.  The $-$35$ fixed administrative cost covers the senior underwriter's salary time per case.  Consequently, REFER is optimal only when the bandit is genuinely uncertain (the expected values of STANDARD, RATED, and DECLINE are close) or when the applicant's mortality multiplier is so high that even the penalised REFER reward exceeds the negative expected profit of direct issuance.

**Claims noise reduction.**  The stochastic simulator adds uniform multiplicative noise $\nu_t \in [0.92, 1.08]$ to claims.  This narrow band (±8 %) represents the irreducible uncertainty in claim costs for a single policy year; it is intentionally small so that the bandit learns from signal rather than noise, while still preventing degenerate solutions in which the oracle policy is trivially identifiable.  Early experiments with wider noise bands (±20 %) produced excessive variance in regret curves without altering the relative ranking of algorithms.

---

## 4.8 PSI Guardrails and Fairness Metrics

### 4.8.1 PSI Computation

The Population Stability Index measures the divergence between the demographic distribution of the approved portfolio and the reference applicant population. For categorical features (region, occupation, wealth quintile), each distinct category serves as a bin. For continuous features (age), the reference distribution is divided into four actuarially meaningful bands: 18–30, 31–45, 46–60, and 61+, consistent with standard life-insurance age grading.

The PSI is computed as:

$$\text{PSI} = \sum_{i=1}^{B} (A_i - E_i) \times \ln\left(\frac{A_i}{E_i}\right)$$

where $E_i$ is the expected proportion (reference applicant pool) and $A_i$ is the actual proportion (approved portfolio) in bin $i$. Zero-frequency bins are handled by adding a small epsilon ($10^{-8}$) before normalization, following standard practice to avoid division-by-zero in the logarithm term (Siddiqi, 2006).

The traffic-light thresholds originate with Lewis (1994), were codified in credit-scoring textbooks by Thomas et al. (2002), and are statistically validated by Yurdakul and Naranjo (2020):

| Level | PSI Range | Interpretation |
|-------|-----------|----------------|
| GREEN | $<$ 0.10   | Little or no shift; portfolio is demographically stable |
| AMBER | 0.10 – 0.25 | Moderate shift; trigger manual review of segment exclusion |
| RED   | $>$ 0.25   | Significant shift; freeze auto-approval and escalate to actuarial team |

These thresholds are applied independently to each monitored dimension. A RED alert on any dimension overrides the bandit's decision for the corresponding segment until the drift is investigated.

### 4.8.2 Fairness Constraints

In addition to PSI drift monitoring, the fairness audit evaluates **approval-rate parity** across demographic subgroups.  An applicant is considered "approved" if the bandit selects STANDARD or RATED (i.e., a policy is issued).  For each protected dimension (region and occupation), the approval rate of every subgroup is computed and divided by the maximum subgroup approval rate.  The pre-registered fairness constraint is the U.S. Equal Employment Opportunity Commission **"four-fifths" rule**: the minimum subgroup approval rate must be at least 80 % of the maximum:

$$\frac{\text{ApprovalRate}(g)}{\max_{g'} \text{ApprovalRate}(g')} \ge 0.80 \quad \forall \, g \in \{\text{regions}\} \cup \{\text{occupations}\}.$$

The 80 % floor (EEOC 4/5 rule) is the widely cited regulatory benchmark for disparate-impact analysis. It allows actuarially justified variation (rural applicants may legitimately have higher morbidity) while drawing a bright line against systematic exclusion of any single group. The threshold is evaluated on the converged-phase decision trace (rounds 3,000–4,999), because fairness is a portfolio-level property and early-round exploration noise would inflate apparent disparity.

### 4.8.3 Integration with Bandit Loop

PSI is computed after each batch of 500 decisions (a sliding window) by comparing the demographic distribution of the *approved* portfolio (STANDARD + RATED actions only) against the reference distribution of the full 2,000-record applicant pool.  The reference proportions $E_i$ are fixed at the dataset generation stage; the actual proportions $A_i$ are updated incrementally as new decisions accumulate.

In the experimental pipeline, PSI is treated as a **diagnostic metric** rather than a hard constraint: the bandit is allowed to continue learning regardless of the PSI value, and the experiment reports the maximum PSI observed across all windows.  In a production deployment (§4.10), PSI would trigger escalation rules: a GREEN reading permits normal bandit operation; an AMBER reading routes new applications from the affected subgroup to junior underwriter review; a RED reading freezes automated decisions for that subgroup and escalates to the actuarial team for investigation.  This layered response ensures that demographic drift is caught before it compounds into portfolio-level concentration risk.

---

## 4.9 Experimental Design

### 4.9.1 EXP-005: Convergence Validation

EXP-005 tests whether LinUCB learns a profitable underwriting policy that dominates the static XGB baseline.

**Hypothesis.**  LinUCB will achieve higher cumulative reward and lower late-round average regret than the Static XGB baseline, and its action distribution will converge from high entropy (exploration) to lower entropy (exploitation).

**Setup.**  LinUCB ($\alpha = 1.0$), Static XGB, and an Oracle policy (always selects the action with highest expected reward) are evaluated over $N = 5,000$ rounds on the full 2,000-record Cambodia dataset.  The experiment is repeated across 20 independent random seeds (1–20).  For each seed, bootstrap 95 % confidence intervals are computed for cumulative reward and late-round regret, and paired Wilcoxon signed-rank tests compare LinUCB against Static XGB.

**Pass criteria.**
1. LinUCB cumulative reward significantly exceeds Static XGB ($p < 0.05$, Wilcoxon).
2. LinUCB average regret in the last 500 rounds is significantly lower than Static XGB ($p < 0.05$, Wilcoxon).
3. Action entropy decreases from early (rounds 1–500) to late (rounds 4,501–5,000), confirming convergence from exploration to exploitation.
4. Action accuracy versus the oracle in the last 500 rounds exceeds 30 % (the bandit is expected to learn a profitable policy within its feature subspace rather than converge to the oracle exactly; theoretical support for the broader claim that simple bandit methods can be rate-optimal under heterogeneous contexts is provided by Bastani, Bayati & Khosravi (2021), who prove that covariate diversity alone can make exploration-free greedy near-optimal).
5. Oracle action accuracy equals 100 % (sanity check).

### 4.9.2 EXP-006: Fairness Audit

EXP-006 evaluates whether LinUCB introduces demographic bias into the approved portfolio.

**Hypothesis.**  LinUCB will satisfy the EEOC 4/5 (≥ 80 %) approval-rate parity constraint for every region and occupation subgroup, and the maximum PSI across all 500-round windows will remain below the 0.25 RED threshold for both region and occupation.

**Setup.**  LinUCB ($\alpha = 1.0$) is run for $N = 5,000$ rounds over 20 seeds.  After each run, approval rates are computed per region and per occupation, and PSI is evaluated on a sliding window of 500 decisions (10 windows total).  Permutation tests assess whether approval is independent of region and occupation.  Bonferroni correction is applied for multiple comparisons.

**Pass criteria.**
1. Minimum region approval rate ≥ 80 % of maximum region approval rate (EEOC 4/5 rule).
2. Minimum occupation approval rate ≥ 80 % of maximum occupation approval rate (EEOC 4/5 rule).
3. Maximum region sliding-window PSI < 0.25.
4. Maximum occupation sliding-window PSI < 0.25.
5. Permutation test $p > 0.025$ for region (Bonferroni-corrected).
6. Permutation test $p > 0.025$ for occupation (Bonferroni-corrected).

### 4.9.3 EXP-007: Benchmark Comparison

EXP-007 compares all candidate algorithms on cumulative regret and reward using common random numbers to ensure fairness.

**Hypothesis.**  LinTS will achieve the lowest cumulative regret, followed by LinUCB, then Epsilon-Greedy, then Static XGB.  All adaptive algorithms will significantly outperform the static baseline.

**Setup.**  LinUCB ($\alpha = 1.0$), LinTS ($v^2 = 1.0$), Epsilon-Greedy ($\varepsilon = 0.15$), Static XGB, and Oracle are evaluated over $N = 5,000$ rounds on 20 seeds.  **Common random numbers** are enforced: a single stream of acceptance draws and claims noise is pre-generated per seed and shared across all algorithms, so that performance differences stem solely from decision quality, not from stochastic reward variation.

**Pass criteria.**
1. Oracle regret $\le$ all learning algorithms (sanity check).
2. LinUCB and LinTS regret are significantly lower than both Epsilon-Greedy and Static XGB ($p < 0.05$, pairwise Wilcoxon with Bonferroni correction).
3. LinUCB and LinTS reward are significantly higher than Static XGB ($p < 0.05$).
4. Oracle reward $\ge$ all learning algorithms (sanity check).
5. Regret ordering matches theoretical prediction: $\text{LinTS} \le \text{LinUCB} \le \text{EpsilonGreedy} \le \text{StaticXGB}$.

### 4.9.4 Reproducibility Protocol

All experiments are designed to be fully reproducible.  The primary random seed is **42**; for statistical inference, experiments are repeated across 20 independent seeds (1–20) and reported with bootstrap 95 % confidence intervals.

**Software stack.**  Python 3.11, NumPy 1.24+, pandas 2.0+, scikit-learn 1.3+, XGBoost 2.0+, statsmodels 0.14+.  No GPU acceleration is required; all experiments run on a standard CPU in under five minutes per seed.

**Feature normalisation.**  Before each run, the bandit preprocessor recomputes feature means and standard deviations on the full 2,000-record dataset.  Because the dataset is fixed, these statistics are deterministic; any drift experiment that modifies the dataset must supply an external `stats` dictionary to guarantee consistent scaling.

**Exit codes.**  Every experiment script exits with code `0` if all pass criteria are satisfied and code `1` if any criterion fails.  This design allows the experiments to be run in continuous-integration pipelines as self-validating tests.

---

## 4.10 Implementation and Deployment Roadmap

While the experiments validate the algorithmic core, moving from a research prototype to a production actuarial system requires additional engineering layers. The deployment strategy is structured in three phases that progressively reduce human oversight while maintaining regulatory compliance.

### 4.10.1 Phase 1 — Shadow Mode (Months 1–3)

In shadow mode, the contextual bandit runs alongside the existing static rule engine without making live decisions. Every incoming application is scored by both systems simultaneously. The bandit's recommendation is logged and compared against the static rule outcome, but the static rule remains the binding decision. This phase serves three purposes:

1. **Calibration validation.** Verify that the bandit's action distribution aligns with actuarial expectations for different risk segments.
2. **Hyperparameter tuning.** Adjust $\alpha$ (LinUCB), $v^2$ (LinTS), or $\varepsilon$ (Epsilon-Greedy) based on observed disagreement rates between the bandit and the static baseline.
3. **PSI baseline establishment.** Compute PSI for the shadow-approved portfolio against the historical applicant reference to confirm that the bandit does not introduce demographic drift even before it controls live decisions.

During shadow mode, sufficient statistics ($A_a$, $b_a$ matrices for each action) are updated in real time using the static rule's outcome as a proxy reward. This warm-starts the bandit with several thousand observations before Phase 2.

### 4.10.2 Phase 2 — Assisted Underwriting (Months 4–6)

In assisted mode, the bandit makes recommendations that human underwriters must confirm or override. The workflow is:

1. Applicant data enter the system via the Policy Administration System (PAS) API or manual web form.
2. The bandit selects the action with highest estimated expected reward.
3. The PSI guardrail validates demographic parity; if any dimension is AMBER or RED, the case is automatically escalated to a senior underwriter regardless of the bandit's recommendation.
4. The underwriter reviews the recommendation, context, and PSI status, then approves, modifies, or overrides.
5. The final human decision is logged as the observed reward and fed back to update the bandit's parameters.

Key metrics tracked in Phase 2 include:
- **Override rate:** The percentage of bandit recommendations that underwriters change. A declining override rate indicates growing trust and alignment.
- **Reward lift:** The difference in average profit per application between bandit-recommended actions and the static baseline on the same applicant pool.
- **Fairness KPIs:** Regional and occupational approval-rate parity, plus PSI status distribution.

### 4.10.3 Phase 3 — Automated Underwriting with Escalation (Months 7–12)

In full automation, low-confidence or low-risk cases are processed without human intervention, while borderline cases continue to route through the assisted queue. The escalation logic is:

| Condition | Routing |
|-----------|---------|
| Bandit confidence > 95% AND PSI = GREEN AND action ∈ {STANDARD, DECLINE} | Fully automated |
| Bandit confidence 80–95% OR PSI = AMBER | Junior underwriter review queue |
| Bandit confidence < 80% OR PSI = RED OR action = REFER | Senior underwriter / actuarial team |

Confidence is defined as the posterior probability (LinTS) or the relative gap between the best and second-best arm's UCB score (LinUCB). The automated stream is typically 60–70% of applicants, with the remainder requiring human judgment.

### 4.10.4 Technical Infrastructure for Production

The current FastAPI prototype is designed to slot into a standard microservices architecture. The production extensions required are:

1. **Persistent state layer.** PostgreSQL stores the bandit's $A_a$ and $b_a$ matrices, enabling warm restarts and multi-instance scaling.
2. **Feedback integration.** A `/feedback` endpoint receives post-decision outcomes from the PAS: policy accepted, lapsed, claims paid, final profit/loss.
3. **Audit logging.** Every `(context, action, reward, PSI, user_id, timestamp)` tuple is immutably logged for regulatory review.
4. **Authentication and RBAC.** OAuth2 with role-based access control (Underwriter, Senior Underwriter, Actuary, Admin).
5. **Batch upload.** CSV/Excel endpoints for portfolio-level pricing runs and quarterly PSI monitoring.
6. **BI dashboard integration.** PSI time-series and cumulative regret curves exposed via REST for Power BI or Tableau consumption.

These additions do not require rewriting the core algorithms; they wrap the existing `LinUCB`, `LinTS`, `expected_rewards`, and `compute_psi` functions in enterprise-grade infrastructure.

---

[FIGURE: thesis/health_rl/figures/fig_framework.png — Figure 4.3. System architecture of the adaptive underwriting framework.]


*Word count: approximately 3,500 words.*
