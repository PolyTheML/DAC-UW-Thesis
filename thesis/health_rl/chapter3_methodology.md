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

The Population Stability Index measures the divergence between the demographic distribution of the approved portfolio and the reference applicant population. For categorical features (region, occupation, wealth quintile), each distinct category serves as a bin. For continuous features (age), the reference distribution is divided into four actuarially meaningful bands: 18–30, 31–45, 46–60, and 61+, consistent with standard life-insurance age grading.

The PSI is computed as:

$$\text{PSI} = \sum_{i=1}^{B} (A_i - E_i) \times \ln\left(\frac{A_i}{E_i}\right)$$

where $E_i$ is the expected proportion (reference applicant pool) and $A_i$ is the actual proportion (approved portfolio) in bin $i$. Zero-frequency bins are handled by adding a small epsilon ($10^{-8}$) before normalization, following standard practice to avoid division-by-zero in the logarithm term [CITATION: Siddiqi 2006].

The traffic-light thresholds originate with Lewis (1994), were codified in credit-scoring textbooks by Thomas et al. (2002), and are statistically validated by Yurdakul and Naranjo (2020):

| Level | PSI Range | Interpretation |
|-------|-----------|----------------|
| GREEN | $<$ 0.10   | Little or no shift; portfolio is demographically stable |
| AMBER | 0.10 – 0.25 | Moderate shift; trigger manual review of segment exclusion |
| RED   | $>$ 0.25   | Significant shift; freeze auto-approval and escalate to actuarial team |

These thresholds are applied independently to each monitored dimension. A RED alert on any dimension overrides the bandit's decision for the corresponding segment until the drift is investigated.

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

## 3.6 Implementation and Deployment Roadmap

While the experiments validate the algorithmic core, moving from a research prototype to a production actuarial system requires additional engineering layers. The deployment strategy is structured in three phases that progressively reduce human oversight while maintaining regulatory compliance.

### 3.6.1 Phase 1 — Shadow Mode (Months 1–3)

In shadow mode, the contextual bandit runs alongside the existing static rule engine without making live decisions. Every incoming application is scored by both systems simultaneously. The bandit's recommendation is logged and compared against the static rule outcome, but the static rule remains the binding decision. This phase serves three purposes:

1. **Calibration validation.** Verify that the bandit's action distribution aligns with actuarial expectations for different risk segments.
2. **Hyperparameter tuning.** Adjust $\alpha$ (LinUCB), $v^2$ (LinTS), or $\varepsilon$ (Epsilon-Greedy) based on observed disagreement rates between the bandit and the static baseline.
3. **PSI baseline establishment.** Compute PSI for the shadow-approved portfolio against the historical applicant reference to confirm that the bandit does not introduce demographic drift even before it controls live decisions.

During shadow mode, sufficient statistics ($A_a$, $b_a$ matrices for each action) are updated in real time using the static rule's outcome as a proxy reward. This warm-starts the bandit with several thousand observations before Phase 2.

### 3.6.2 Phase 2 — Assisted Underwriting (Months 4–6)

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

### 3.6.3 Phase 3 — Automated Underwriting with Escalation (Months 7–12)

In full automation, low-confidence or low-risk cases are processed without human intervention, while borderline cases continue to route through the assisted queue. The escalation logic is:

| Condition | Routing |
|-----------|---------|
| Bandit confidence > 95% AND PSI = GREEN AND action ∈ {STANDARD, DECLINE} | Fully automated |
| Bandit confidence 80–95% OR PSI = AMBER | Junior underwriter review queue |
| Bandit confidence < 80% OR PSI = RED OR action = REFER | Senior underwriter / actuarial team |

Confidence is defined as the posterior probability (LinTS) or the relative gap between the best and second-best arm's UCB score (LinUCB). The automated stream is typically 60–70% of applicants, with the remainder requiring human judgment.

### 3.6.4 Technical Infrastructure for Production

The current FastAPI prototype is designed to slot into a standard microservices architecture. The production extensions required are:

1. **Persistent state layer.** PostgreSQL stores the bandit's $A_a$ and $b_a$ matrices, enabling warm restarts and multi-instance scaling.
2. **Feedback integration.** A `/feedback` endpoint receives post-decision outcomes from the PAS: policy accepted, lapsed, claims paid, final profit/loss.
3. **Audit logging.** Every `(context, action, reward, PSI, user_id, timestamp)` tuple is immutably logged for regulatory review.
4. **Authentication and RBAC.** OAuth2 with role-based access control (Underwriter, Senior Underwriter, Actuary, Admin).
5. **Batch upload.** CSV/Excel endpoints for portfolio-level pricing runs and quarterly PSI monitoring.
6. **BI dashboard integration.** PSI time-series and cumulative regret curves exposed via REST for Power BI or Tableau consumption.

These additions do not require rewriting the core algorithms; they wrap the existing `LinUCB`, `LinTS`, `expected_rewards`, and `compute_psi` functions in enterprise-grade infrastructure.

---

[FIGURE: thesis/health_rl/figures/fig_framework.png — Figure 3.1. System architecture of the adaptive underwriting framework.]

*Skeleton — content to be expanded.*
