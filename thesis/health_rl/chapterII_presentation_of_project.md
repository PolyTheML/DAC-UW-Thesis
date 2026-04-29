# CHAPTER II. PRESENTATION OF THE PROJECT

---

## 2.1 General Presentation of Project

This thesis develops an adaptive health insurance underwriting system using contextual bandits — a class of online learning algorithms that balance exploration and exploitation in sequential decision-making. The project is titled *"Adaptive Health Insurance Underwriting via Contextual Bandits: A Reinforcement Learning Approach for Cambodia."* It addresses the problem that traditional static rule-based underwriting is suboptimal for emerging-market health insurance because it ignores feature interactions and cannot adapt to portfolio drift.

The project produces four deliverables:

1. **Synthetic Cambodia Health Insurance Dataset**: A reproducible dataset of 2,000 applicants with realistic demographics, disease prevalence (tuberculosis, hepatitis B), regional variation, and occupational risk profiles.

2. **Contextual Bandit Underwriting Engine**: Implementations of LinUCB, LinTS, and Epsilon-Greedy algorithms that learn optimal accept / rate / decline / refer decisions from feedback.

3. **Actuarial Reward Simulator**: A profit-based simulator that computes expected reward for each underwriting action, incorporating premium levels, claims costs, adverse selection, and customer acceptance probability.

4. **Fairness Monitoring Framework**: PSI-based guardrails that ensure the approved portfolio does not drift demographically from the applicant population, maintaining regional and occupational fairness.

The project is evaluated through three controlled experiments (EXP-005, EXP-006, EXP-007) that validate convergence, fairness, and benchmark performance against a static XGBoost rule baseline.

---

## 2.2 Problematic

Current health insurance underwriting in Cambodia relies on static rule engines or pre-trained classification models that apply the same decision boundary to every applicant, regardless of how the applicant population evolves. This creates three distinct problems:

**Suboptimal Risk Selection.** Static rules ignore feature interactions. A rule that declines all applicants with BMI above thirty and age above fifty cannot learn that a fit, non-smoking fifty-five-year-old with BMI thirty-one may be a profitable standard-risk case. Similarly, a rule that rates all rural applicants equally cannot distinguish between a low-risk rural civil servant and a high-risk rural construction worker. The result is a portfolio that systematically excludes profitable applicants while underpricing genuinely elevated risks.

**Inability to Adapt to Portfolio Drift.** As the insured population changes — through economic growth, urbanization, occupational shifts, or public health interventions — the risk distribution of incoming applicants drifts away from the population on which the static model was trained. A model trained in 2023 may face a 2026 applicant pool with substantially different age, occupation, and disease prevalence profiles. Without online learning, the model cannot adapt its decision boundaries to maintain profitability.

**Fairness and Demographic Parity.** Static models optimized for aggregate accuracy can inadvertently discriminate against demographic segments. If the training data underrepresents rural applicants or garment workers, the model may learn to decline these segments at higher rates. In Cambodia, where garment workers number approximately 700,000 (85 percent women) and rural rice farmers number approximately 2.5 million, such discrimination would both deepen social inequality and exclude large addressable markets.

These three problems share a common structural cause: the underwriting system treats decision-making as a one-shot prediction task rather than a sequential learning problem. Contextual bandits reframe the task as an online optimization problem in which the algorithm explicitly balances exploration (testing uncertain applicants to learn) with exploitation (applying known good decisions), while monitoring demographic parity through Population Stability Index (PSI) guardrails.

---

## 2.3 Objective

### Primary Objective

To design, implement, and empirically validate a contextual bandit framework for health insurance underwriting that outperforms static rule-based baselines on cumulative profitability while maintaining regional and occupational fairness on a synthetic Cambodia dataset.

### Secondary Objectives

1. Develop a reproducible synthetic dataset of 2,000 Cambodian health insurance applicants with realistic demographics, disease prevalence (including tuberculosis and hepatitis B), regional variation, and occupational risk profiles.

2. Implement and compare three contextual bandit algorithms — LinUCB, LinTS, and Epsilon-Greedy — against a static XGBoost rule baseline on cumulative reward and regret metrics over 5,000 decision rounds.

3. Design and validate PSI-based fairness guardrails that ensure the approved portfolio does not drift demographically from the applicant population.

4. Conduct a fairness audit verifying that no regional or occupational segment experiences an approval rate below fifty percent of the maximum observed rate.

### Research Questions

- **RQ1.** Do contextual bandits (LinUCB, LinTS) achieve higher cumulative reward and lower cumulative regret than static XGBoost rule baselines on the Cambodia health underwriting task?

- **RQ2.** Does the bandit framework maintain demographic fairness — as measured by regional and occupational approval-rate parity and PSI — without explicit fairness constraints in the reward function?

- **RQ3.** What is the relative performance ranking of LinTS, LinUCB, Epsilon-Greedy, and Static XGB on regret and reward, and what algorithmic properties explain the ordering?

- **RQ4.** Is the proposed framework technically feasible for deployment on low-resource mobile infrastructure, and what implementation pathway is required?

---

## 2.4 Planning of Project

The project was executed according to the following schedule:

| Phase | Activities | Duration | Timeline |
|-------|-----------|----------|----------|
| Phase 1 | Literature review, dataset design, baseline model training | 4 weeks | Month 1 |
| Phase 2 | Bandit algorithm implementation, reward simulator development | 4 weeks | Month 2 |
| Phase 3 | Experiment execution (EXP-005, EXP-006, EXP-007) | 4 weeks | Month 3 |
| Phase 4 | Results analysis, fairness audit, figure generation | 3 weeks | Month 4 |
| Phase 5 | Thesis writing, presentation preparation, defense rehearsal | 5 weeks | Month 5–6 |

[INSERT GANTT CHART]

Key milestones:

- **Milestone 1**: Dataset and baseline models complete (end of Month 1)
- **Milestone 2**: Bandit engine and reward simulator operational (end of Month 2)
- **Milestone 3**: All three experiments executed with passing results (end of Month 3)
- **Milestone 4**: Figures, tables, and draft chapters complete (end of Month 4)
- **Milestone 5**: Final thesis submission and defense readiness (end of Month 6)

---

*Formatting: Chapter heading II — Size 16 Bold ALL CAPS new page. Sections 2.1–2.4 — Size 14 Bold. Body — Size 12, 1.5 spacing, justified.*
