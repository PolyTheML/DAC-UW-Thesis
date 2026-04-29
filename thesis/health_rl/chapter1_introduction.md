# CHAPTER I. INTRODUCTION

---

## 1.1 Research Context and Motivation

Health insurance underwriting in emerging markets operates under conditions fundamentally different from those in developed economies. In Cambodia, the combination of extremely low insurance penetration, rapid demographic change, fragmented healthcare infrastructure, and a nascent regulatory environment creates unique pressures on both traditional actuarial models and modern data-driven underwriting systems. According to World Bank estimates, only approximately one percent of Cambodian households hold any form of insurance coverage. This stands in stark contrast to regional peers: Vietnam reports roughly eight percent life insurance penetration, while Thailand approaches forty percent. The gap is not merely a measure of market maturity; it reflects structural barriers in distribution, affordability, and risk assessment that static underwriting systems have been unable to overcome.

The traditional underwriting model in Cambodia relies on human agents who conduct face-to-face interviews, collect paper-based health declarations, and apply deterministic rule sets calibrated to regional proxy data. This model suffers from three interconnected inefficiencies. First, agent commissions consume fifteen to thirty percent of premium revenue, making micro-premium products economically unviable. Second, deterministic rules — age thresholds, BMI cutoffs, and condition-based declinations — cannot adapt to local risk heterogeneity or learn from feedback. Third, the model scales linearly with underwriter headcount, creating a hard ceiling on market expansion.

Digital distribution offers a plausible path around these barriers. Mobile penetration in Cambodia exceeds one hundred percent of the population, and digital payment platforms such as Wing have reached fourteen million users, approximately eighty percent of the country's population. The success of BIMA-Smart Axiata, which issued 430,000 mobile life policies in eighteen months at micro-premium levels, demonstrates that Cambodian consumers will purchase insurance if the transaction cost is low enough. The critical bottleneck is no longer distribution channel access; it is the underwriting decision engine that must evaluate risk instantaneously, accurately, and fairly from a short digital questionnaire.

This thesis investigates whether **contextual bandits** — a class of online learning algorithms for sequential decision-making under uncertainty — can replace static rule-based underwriting in emerging-market health insurance. Contextual bandits are particularly suited to this problem because each applicant represents an independent decision with immediate feedback (acceptance, premium payment, eventual claim), and the algorithm improves continuously as new experience arrives. Unlike full reinforcement learning, contextual bandits do not require modeling state transitions, making them computationally lightweight and interpretable enough for regulatory environments.

The central research question follows naturally: can a contextual bandit system learn risk-appropriate underwriting decisions — accept, rate, decline, or refer — that outperform static rules on both profitability and fairness, while remaining deployable on low-resource mobile infrastructure?

---

## 1.2 Problem Statement

Current health insurance underwriting in Cambodia relies on static rule engines or pre-trained classification models that apply the same decision boundary to every applicant, regardless of how the applicant population evolves. This creates three distinct problems that motivate the research.

**Problem 1 — Suboptimal Risk Selection.** Static rules ignore feature interactions. A rule that declines all applicants with BMI above thirty and age above fifty cannot learn that a fit, non-smoking fifty-five-year-old with BMI thirty-one may be a profitable standard-risk case. Similarly, a rule that rates all rural applicants equally cannot distinguish between a low-risk rural civil servant and a high-risk rural construction worker. The result is a portfolio that systematically excludes profitable applicants while underpricing genuinely elevated risks.

**Problem 2 — Inability to Adapt to Portfolio Drift.** As the insured population changes — through economic growth, urbanization, occupational shifts, or public health interventions — the risk distribution of incoming applicants drifts away from the population on which the static model was trained. A model trained in 2023 may face a 2026 applicant pool with substantially different age, occupation, and disease prevalence profiles. Without online learning, the model cannot adapt its decision boundaries to maintain profitability.

**Problem 3 — Fairness and Demographic Parity.** Static models optimized for aggregate accuracy can inadvertently discriminate against demographic segments. If the training data underrepresents rural applicants or garment workers, the model may learn to decline these segments at higher rates. In Cambodia, where garment workers number approximately 700,000 (85 percent women) and rural rice farmers number approximately 2.5 million, such discrimination would both deepen social inequality and exclude large addressable markets.

These three problems share a common structural cause: the underwriting system treats decision-making as a one-shot prediction task rather than a sequential learning problem. Contextual bandits reframe the task as an online optimization problem in which the algorithm explicitly balances exploration (testing uncertain applicants to learn) with exploitation (applying known good decisions), while monitoring demographic parity through Population Stability Index (PSI) guardrails.

---

## 1.3 Research Objectives

**Primary Objective.** To design, implement, and empirically validate a contextual bandit framework for health insurance underwriting that outperforms static rule-based baselines on cumulative profitability while maintaining regional and occupational fairness on a synthetic Cambodia dataset.

**Secondary Objectives.**

1. Develop a reproducible synthetic dataset of 2,000 Cambodian health insurance applicants with realistic demographics, disease prevalence (including tuberculosis and hepatitis B), regional variation, and occupational risk profiles.

2. Implement and compare three contextual bandit algorithms — LinUCB, LinTS, and Epsilon-Greedy — against a static XGBoost rule baseline on cumulative reward and regret metrics over 5,000 decision rounds.

3. Design and validate PSI-based fairness guardrails that ensure the approved portfolio does not drift demographically from the applicant population.

4. Conduct a fairness audit verifying that no regional or occupational segment experiences an approval rate below fifty percent of the maximum observed rate.

**Research Questions.**

- **RQ1.** Do contextual bandits (LinUCB, LinTS) achieve higher cumulative reward and lower cumulative regret than static XGBoost rule baselines on the Cambodia health underwriting task?

- **RQ2.** Does the bandit framework maintain demographic fairness — as measured by regional and occupational approval-rate parity and PSI — without explicit fairness constraints in the reward function?

- **RQ3.** What is the relative performance ranking of LinTS, LinUCB, Epsilon-Greedy, and Static XGB on regret and reward, and what algorithmic properties explain the ordering?

- **RQ4.** Is the proposed framework technically feasible for deployment on low-resource mobile infrastructure, and what implementation pathway is required?

---

## 1.4 Main Contributions

This thesis makes the following contributions to the literature on algorithmic underwriting and reinforcement learning in insurance:

**Contribution 1 — First Contextual Bandit Underwriting System Calibrated for Cambodian Health Insurance.** Prior work on bandit-based underwriting has focused on credit scoring and advertising in developed markets. This thesis is the first to frame Cambodian health insurance underwriting as a contextual bandit problem, with a reward simulator calibrated to local premium levels, disease burden, and income distributions.

**Contribution 2 — Empirical Regret and Reward Benchmark.** The thesis provides the first head-to-head comparison of LinUCB, LinTS, Epsilon-Greedy, and a static XGBoost baseline on an insurance underwriting task with a profit-based reward function. The results establish a clear performance ranking (LinTS < LinUCB < Epsilon-Greedy < Static XGB on regret) and quantify the magnitude of improvement (LinUCB achieves +67% cumulative reward over static rules).

**Contribution 3 — PSI Guardrails for Fairness in Adaptive Underwriting.** While PSI is widely used in actuarial model monitoring, its application as a fairness guardrail within an online learning underwriting system is novel. The thesis demonstrates that PSI monitoring on region and occupation dimensions can detect demographic drift without degrading profitability, and that all fairness constraints are satisfied without baking demographic parity into the reward function.

**Contribution 4 — Reproducible Experimental Harness.** The thesis delivers a fully reproducible experimental pipeline (`stress_testing/rl/experiments/`) with fixed random seeds, self-contained pass/fail assertions, and exit-code reporting suitable for continuous integration. All three experiments (EXP-005, EXP-006, EXP-007) are designed to be rerun independently by other researchers.

**Contribution 5 — Neural Contextual Bandits in the Literature Review.** The thesis situates linear contextual bandits within the broader landscape of neural bandit approaches (NeuralUCB, NeuralTS, EE-Net) that are gaining traction in dynamic pricing literature. While the empirical experiments focus on linear models appropriate for the dataset size, the literature review provides the theoretical bridge to deep bandit methods for future researchers with larger datasets.

---

## 1.5 Thesis Organization

The remainder of this thesis is structured as follows:

**Chapter II: Literature Review** establishes the theoretical and empirical context. It reviews health insurance underwriting fundamentals, introduces contextual bandits (LinUCB, LinTS, Epsilon-Greedy), surveys neural contextual bandit extensions and their application in dynamic pricing, discusses algorithmic fairness and PSI monitoring, and identifies the gap that this thesis addresses.

**Chapter III: Methodology** describes the research design in detail. It covers the synthetic Cambodia dataset generation process, the four-action policy space, the profit-based reward simulator, the three bandit algorithms and the static baseline, the PSI fairness guardrails, and the design of experiments EXP-005 through EXP-007.

**Chapter IV: Results and Discussion** presents the empirical findings. EXP-005 validates convergence and learning; EXP-006 validates fairness; EXP-007 provides the benchmark comparison. The discussion interprets the results in the context of Cambodian insurance practice and connects them to the broader dynamic pricing literature.

**Chapter V: Conclusion** synthesizes the findings, restates the contributions, acknowledges limitations (synthetic data, stationary environment, single-period rewards), and proposes directions for future work including non-stationary drift, neural bandit extensions, and live A/B testing with a Cambodian insurer.

---

## 1.6 Scope and Limitations

**Scope.** This thesis focuses on the underwriting decision layer — the algorithm that selects among accept, rate, decline, and refer actions given an applicant's features. It does not address premium pricing optimization (the base premium formula is fixed at $200 multiplied by a mortality multiplier), claims prediction modeling, or customer acquisition marketing. The experiments are conducted on synthetic data rather than real insurance portfolios, and the bandit simulator uses a stylized claims model with reduced noise (+/-8%) rather than historical claims experience.

**Limitations.** Three limitations bound the generalizability of the results. First, the synthetic dataset, while calibrated to Cambodian demographics and disease prevalence, cannot perfectly replicate the joint distributions of real applicant populations. Second, the environment is stationary: the underlying risk distributions do not change over the 5,000 rounds. Real insurance markets experience non-stationary drift (seasonal disease outbreaks, economic shocks) that would require more sophisticated algorithms. Third, the reward function uses a single-period profit metric and does not incorporate multi-period customer lifetime value, retention probability, or cross-selling potential.

Despite these limitations, the thesis provides a rigorous, reproducible proof of concept that establishes the viability of contextual bandits for emerging-market health insurance underwriting and supplies a modular framework upon which future researchers can build.

---

*Word count: approximately 1,450 words. Length: ~3.5 pages at 1.5 spacing, Times New Roman 12pt.*
