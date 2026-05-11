# CHAPTER IV. PROJECT ANALYSIS AND CONCEPTS

---

This chapter specifies the requirements that the proposed contextual bandit underwriting system must satisfy and identifies the technologies used to implement them. Section 4.1 defines the functional capabilities, organised around the four operational modules of the system. Section 4.2 specifies the non-functional quality attributes. Section 4.3 enumerates the implementation tool stack. Section 4.4 closes with a focused exposition of the core technology — the contextual bandit framework — describing what it is, how it operates, its place in the overall system architecture, and the reasons it was selected over competing alternatives.

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

1. **Context observation.** At round *t*, the algorithm observes the applicant feature vector *x_t* ∈ ℝ^d, where d = 25 in this implementation (age, BMI, region one-hot, occupation one-hot, health flags, income).
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
6. **Emerging-market data fit.** With only 2,000 calibrated records available, deep neural approaches risk overfitting. Linear bandits with d = 25 features achieve strong generalisation under this sample budget while remaining flexible enough to capture the dominant feature interactions identified in the literature.

---

*Word count: approximately 1,500 words.*
