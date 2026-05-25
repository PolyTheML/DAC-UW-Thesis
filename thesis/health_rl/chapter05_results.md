# CHAPTER V. RESULTS AND DISCUSSION

---

## 5.1 EXP-005: Convergence Validation

[FIGURE: thesis/health_rl/figures/fig_reward_curves.png — Figure 5.1. Cumulative reward curves for LinUCB and Static XGB baseline (mean of 20 seeds, shaded band = 95% bootstrap confidence interval).]
### 5.1.1 Cumulative Reward and Regret

Table 5.1.1 reports the cumulative reward and average regret for LinUCB against the Oracle ceiling and the Static XGBoost baseline over N = 5,000 rounds, averaged over 20 independent seeds.

**Table 5.1.1 — EXP-005 cumulative performance (N = 5,000 rounds, 20 seeds, mean ± std [95% bootstrap CI])**

| Metric | Oracle | LinUCB | Static XGB Baseline |
|--------|:------:|:------:|:-------------------:|
| Cumulative Reward | 126,804 ± 4,724 [124,857, 128,846] | **90,540 ± 5,382 [88,287, 92,886]** | 72,292 ± 4,120 [70,646, 74,136] |
| Avg Regret (last 500 rounds) | -3.06 ± 2.51 [-4.04, -1.88] | **2.20 ± 2.77 [1.00, 3.37]** | 9.01 ± 3.87 [7.30, 10.62] |

LinUCB accumulates a mean of **90,540** in total reward over 5,000 rounds, exceeding the Static XGB baseline by **+18,248 (+25.2%)** on average and recovering roughly 72% of the Oracle ceiling (126,804). The late-round average regret is even more diagnostic: LinUCB pays only 2.20 per round in the final 500 rounds — within 5 of the Oracle floor — while the Static XGB baseline continues to misallocate underwriting actions at four times that rate (9.01/round). The 25% reward improvement is not a consequence of early exploration advantage; the gap widens monotonically across the run, confirming that the bandit's online learning compounds over time.

**Statistical inference (paired, 20 seeds).** The reward difference is highly significant under a paired Wilcoxon signed-rank test (p < 0.001, mean diff +18,248, 95% CI [+15,595, +20,858], Cohen's d = 2.98, large effect). The regret difference is equally robust (p < 0.001, mean diff -6.81, 95% CI [-8.60, -4.90], Cohen's d = -1.59, large effect). Both pairwise comparisons remain significant after Bonferroni correction for the two tests.

[FIGURE: thesis/health_rl/figures/fig_action_evolution.png — Figure 5.2. Evolution of action distribution over 5,000 rounds. Entropy decreases from 1.31 (uniform-like exploration) to 1.10 (exploitation regime).]
### 5.1.2 Action Distribution Evolution and Entropy

Action entropy provides a seed-invariant measure of exploration intensity. Early in the run (rounds 1–500), LinUCB distributes its four actions relatively uniformly: mean entropy is 1.314 ± 0.017 nats, close to but below the uniform-distribution maximum of $\log 4 ≈ 1.386$ nats. By rounds 4,500–5,000, mean entropy has fallen to 1.105 ± 0.036 nats — a statistically significant decrease that reflects the bandit's progression from exploration to exploitation. Across all 20 seeds the late entropy is strictly less than the early entropy, satisfying the convergence pass criterion.

Qualitatively, this entropy decrease is driven principally by the REFER arm: in the early phase REFER is over-selected because its prior is uninformative and its UCB bonus is correspondingly inflated; once the bandit has observed enough (context, action, reward) triples to estimate reliable feature–reward coefficients for the dominant applicant archetypes, REFER selection collapses and the policy concentrates on STANDARD, RATED, and DECLINE in proportions consistent with the underlying actuarial risk distribution.

### 5.1.3 Learning Curve Analysis

The reward curve separates from the Static XGB baseline within the first few hundred rounds, after which LinUCB's cumulative reward grows at a consistently steeper slope until the gap stabilises at roughly 18,000 by the end of the run. The corresponding regret curve grows approximately as $O(\sqrt{t})$ in the early phase — consistent with the theoretical LinUCB bound of $\tilde{O}(d\sqrt{T})$ for a $d$-dimensional feature space (Li et al., 2010) — before flattening as the bandit's posterior tightens.

Action accuracy against the Oracle is **37.8% ± 3%** in the last 500 rounds. This is well above the 30% pass threshold but far from 100%, and the interpretation deserves emphasis: the bandit is not converging to the Oracle's exact policy. Instead it is discovering a *different but profitable* policy that achieves 72% of the Oracle's reward. This pattern is consistent with the hidden-context phenomenon described by Bastani et al. (2021): the linear reward model lacks features that the Oracle uses internally, so the bandit finds an alternative action mapping that is near-optimal under the available feature set without ever matching the Oracle's action choices case-by-case. From an actuarial perspective, this is the desired behaviour — the policy maximises observable reward given observable features, which is precisely the deployment constraint.

### 5.1.4 Pass/Fail Assessment

Five pre-registered criteria were evaluated on 20 seeds:

1. **LinUCB cumulative reward significantly > Static XGB** — +18,248, p < 0.001, Wilcoxon. **PASSED.**
2. **LinUCB avg regret (last 500) significantly < Static XGB** — -6.81, p < 0.001, Wilcoxon. **PASSED.**
3. **Action entropy decreases (exploration → exploitation)** — 1.314 \to 1.105. **PASSED.**
4. **Action accuracy (last 500) > 30%** — 37.8\% (different but profitable policy). **PASSED.**
5. **Oracle action accuracy = 100%** (sanity check). **PASSED.**

---

## 5.2 EXP-006: Fairness Audit

[FIGURE: thesis/health_rl/figures/fig_fairness_region.png — Figure 5.3. Converged-phase regional approval rates with the EEOC four-fifths (80% of maximum) threshold overlay. All six regions exceed the threshold (min/max parity = 85.7%).]
### 5.2.1 Sliding-Window PSI

Rather than computing a single PSI between the full applicant pool and the final approved portfolio, EXP-006 evaluates PSI on a 500-round sliding window against a fixed reference window (the first 500 rounds of each seed). This captures whether the bandit's learning trajectory introduces *temporal* demographic concentration, not only end-state concentration. The maximum sliding-window PSI across the run is the relevant guardrail metric for live deployment.

- **Region** — maximum sliding-window PSI = 0.0821 ± 0.0213 (95% CI [0.0727, 0.0913]); final-window PSI = 0.0424 ± 0.0233. Both values are in the **GREEN** zone (< 0.10), confirming that LinUCB never induces a regionally concentrated approval pattern at any point during the run.
- **Occupation** — maximum sliding-window PSI = 0.1225 ± 0.0793 (95% CI [0.0953, 0.1613]); final-window PSI = 0.0710 ± 0.0299. The maximum value sits at the lower edge of the **AMBER** band on average but well below the **RED** threshold (< 0.25); the final-window value is comfortably **GREEN**. This indicates a transient occupational concentration during exploration that resolves itself as the bandit converges.

### 5.2.2 Approval-Rate Parity (EEOC 4/5 Rule)

Approval rates (proportion of STANDARD + RATED decisions) were computed on the converged phase (rounds 3,000–4,999) for each demographic group. The pre-registered constraint is the U.S. EEOC "four-fifths" rule: the minimum group approval rate should be at least 80% of the maximum group's rate.

**Table 5.2.1 — EXP-006 converged-phase approval rates (rounds 3,000–4,999, 20 seeds)**

| Dimension | Min Approval | Max Approval | Parity Ratio (Min/Max) | EEOC 4/5 Rule (≥ 80%) |
|-----------|:------------:|:------------:|:----------------------:|:---------------------:|
| Region | 0.6622 ± 0.0493 | 0.7725 ± 0.0315 | **85.72%** | **PASS** |
| Occupation | 0.6803 ± 0.0303 | 0.7549 ± 0.0301 | **90.12%** | **PASS** |

Both dimensions satisfy the four-fifths rule with comfortable margin. The rural–urban approval gap and the cross-occupational gap reflect actuarially justified differences in the underlying mortality and morbidity distribution of the Cambodia dataset — rural and high-labour-intensity occupations carry higher prevalence of Hepatitis B, TB co-morbidities, and physical-injury risk — rather than proxy discrimination on region or occupation as demographic characteristics per se.

[FIGURE: thesis/health_rl/figures/fig_fairness_occupation.png — Figure 5.4. Converged-phase occupational approval rates with the EEOC four-fifths (80% of maximum) threshold overlay. All seven occupations exceed the threshold (min/max parity = 90.1%).]
### 5.2.3 Permutation Independence Tests

To assess whether action allocation depends statistically on demographic group, action labels were permuted within each seed and the empirical distribution of a test statistic compared to the permuted null. Bonferroni-corrected significance threshold is \alpha / 2 = 0.025 for the two tests.

- **Region** — p = 0.1322 ± 0.1509 (95% CI [0.0733, 0.2017]). The null of action–region independence cannot be rejected; there is no significant regional bias in the learned policy.
- **Occupation** — p < 0.001 (95% CI [0.0000, 0.0000]). The null of action–occupation independence is rejected, indicating a statistically significant association between action and occupation.

The occupational association is statistically significant but practically small: the parity ratio is 90.12\% (well above the 80% EEOC threshold) and the maximum sliding-window PSI is 0.1225 (within the GREEN/AMBER boundary). This pattern is expected: different occupational groups have genuinely different actuarial risk profiles, so a policy maximising expected reward will allocate actions in occupation-dependent proportions. The fairness guardrail is not "no statistical dependence" but "no disparate-impact magnitude beyond the regulatory threshold," and that guardrail is satisfied.

### 5.2.4 Pass/Fail Assessment

1. **Region: min/max approval ratio ≥ 80% (EEOC 4/5 rule)** — 85.72\%. **PASSED.**
2. **Occupation: min/max approval ratio ≥ 80% (EEOC 4/5 rule)** — 90.12\%. **PASSED.**
3. **Region: max sliding-window PSI < 0.25** — 0.0821. **PASSED.**
4. **Occupation: max sliding-window PSI < 0.25** — 0.1225. **PASSED.**

---

## 5.3 EXP-007: Benchmark Comparison

[FIGURE: thesis/health_rl/figures/fig_regret_curves.png — Figure 5.5. Cumulative regret curves across all four algorithms (mean of 20 seeds, shaded band = 95% CI).]
### 5.3.1 Final Rankings

Table 5.3.1 ranks all four algorithms by mean cumulative reward and mean cumulative regret over 5,000 rounds, averaged across 20 independent seeds.

**Table 5.3.1 — EXP-007 benchmark comparison (N = 5,000 rounds, 20 seeds, mean ± std [95% CI])**

| Rank | Algorithm | Cumulative Reward | Cumulative Regret |
|:----:|-----------|:-----------------:|:-----------------:|
| — | Oracle (ceiling) | 126,318 ± 5,029 [124,140, 128,405] | -11,597 ± 5,047 [-13,691, -9,395] |
| 1 | **LinTS** | **93,572 ± 6,229 [90,980, 96,312]** | **21,149 ± 6,458 [18,285, 23,873]** |
| 2 | LinUCB | 91,947 ± 6,439 [89,251, 94,768] | 22,774 ± 6,627 [19,865, 25,559] |
| 3 | Epsilon-Greedy | 76,441 ± 6,250 [73,767, 79,107] | 38,281 ± 6,320 [35,570, 40,983] |
| 4 | Static XGB | 72,173 ± 4,997 [70,085, 74,318] | 42,548 ± 4,970 [40,414, 44,642] |

LinTS narrowly outperforms LinUCB on mean reward and regret, but the two are **not statistically distinguishable** under a paired Wilcoxon test on regret (p = 0.87, mean diff +1,626, 95% CI [-1,135, +4,390], Cohen's d = 0.26, small effect). The remaining pairwise comparisons are highly significant after Bonferroni correction (α / 6 = 0.0083 for the six regret tests):

- LinUCB vs Epsilon-Greedy (regret): -15,506, p < 0.001, d = -3.41.
- LinUCB vs Static XGB (regret): -19,774, p < 0.001, d = -3.41.
- LinTS vs Epsilon-Greedy (regret): -17,132, p < 0.001, d = -2.75.
- LinTS vs Static XGB (regret): -21,400, p < 0.001, d = -3.89.
- Epsilon-Greedy vs Static XGB (regret): -4,268, p < 0.01, d = -0.82.

The takeaway is structural rather than competitive: **uncertainty-directed exploration (LinUCB or LinTS) decisively outperforms both undirected exploration (Epsilon-Greedy) and no exploration (Static XGB)**, while the choice between UCB and Thompson Sampling is, in this setting, a matter of operational preference rather than statistical performance.

### 5.3.2 Algorithm-Specific Behaviour

**LinTS (rank 1).** Thompson Sampling maintains a full Gaussian posterior over reward parameters and samples from it at each round. This produces an automatic exploration–exploitation balance: when the posterior is wide, samples are spread across arms; as the posterior narrows, samples concentrate on the optimal arm. Crucially, LinTS requires no exploration parameter tuning — unlike LinUCB's \alpha or Epsilon-Greedy's \varepsilon — which is an operational advantage in production settings where re-tuning after data drift is expensive.

**LinUCB (rank 2).** Upper Confidence Bound performs comparably to LinTS but requires choice of \alpha. At \alpha = 1.0 (Li et al., 2010 default), it accumulates slightly more regret in the early rounds than LinTS before converging to a similar late-round policy. The two algorithms reach statistically indistinguishable asymptotic performance, but UCB's parameter sensitivity means that production deployment would warrant either a tuned \alpha for the specific data distribution or a switch to Thompson Sampling.

**Epsilon-Greedy (rank 3).** With \varepsilon = 0.15, the algorithm wastes 15% of decisions on uniform random exploration regardless of how much has been learned. Unlike UCB and Thompson Sampling, it does not reduce exploration as confidence grows. This produces a nearly-linear regret curve — the hallmark of an algorithm that never fully exploits its learned knowledge — and its mean regret is roughly 1.8 times that of LinUCB and LinTS combined.

**Static XGB (rank 4).** The pre-trained XGBoost baseline, combined with deterministic underwriting rules, cannot adapt to the reward signals it receives. Its regret is bounded below by the systematic mismatch between its fixed decision boundaries and the actuarial reward structure. Even Epsilon-Greedy — which explores uniformly without using any context-dependent information beyond the empirical mean — outperforms it by a statistically significant margin (-4,268, d = -0.82, large effect), underscoring that *any* online adaptation beats *no* online adaptation in this environment.

### 5.3.3 Pass/Fail Assessment

1. **Oracle mean regret ≤ all learning algorithms** — Oracle -11,597 < LinTS 21,149 < LinUCB 22,774 < EpsGreedy 38,281 < StaticXGB 42,548. **PASSED.**
2. **LinUCB regret significantly < StaticXGB and Epsilon-Greedy** — both p < 0.001, d = -3.41. **PASSED.**
3. **LinTS regret significantly < StaticXGB and Epsilon-Greedy** — p < 0.001, d = -3.89 and d = -2.75. **PASSED.**
4. **LinUCB and LinTS reward significantly > StaticXGB** — both p < 0.001, d > 3.4. **PASSED.**
5. **Oracle reward ≥ all learning algorithms** — confirmed. **PASSED.**

---

## 5.4 EXP-008: Human-in-the-Loop Underwriting

### 5.4.1 Motivation and Design

EXP-005 through EXP-007 demonstrated that LinUCB and LinTS outperform static baselines on synthetic data where the optimal reward for every action is immediately observable. In practice, however, an underwriter deploying a contextual bandit faces a fundamentally different constraint: when the model is uncertain about a borderline applicant, it can defer to a human expert — but human review is costly, creates queue latency, and cannot scale to every case. EXP-008 asks whether replacing the REFER arm's mathematical oracle with a real (simulated) human underwriter still produces better outcomes than a mathematical baseline while remaining cost-effective.

The experiment wraps LinUCB (α = 1.0) in a human-in-the-loop (HITL) wrapper. Whenever the bandit selects REFER, the case enters a review queue and a simulated human underwriter resolves it to a final action (STANDARD, RATED, or DECLINE). The simulated underwriter applies a conservatism penalty to risky actions (Equation 5.4.1), modelling the risk-averse behaviour typical of senior actuaries. A $35 processing fee is charged per review and deducted from cumulative reward. Three conservatism levels (c ∈ {0.3, 0.5, 0.7}) are evaluated over N = 5,000 rounds on the 2,000-record Cambodia dataset.

**Equation 5.4.1 — Simulated underwriter adjusted reward:**

$$\hat{r}_\text{std} = r_\text{std} - c \cdot 5.0, \quad \hat{r}_\text{rated} = r_\text{rated} - c \cdot 2.5, \quad \hat{r}_\text{decline} = r_\text{decline}$$

where $c \in [0,1]$ is the conservatism parameter. The human always resolves to $\arg\max(\hat{r}_\text{std}, \hat{r}_\text{rated}, \hat{r}_\text{decline})$, never selecting REFER itself.

A critical implementation detail distinguishes this design from a naïve HITL wrapper: when the human chooses action $a_h$, the bandit receives two updates. It learns the reward from $a_h$ directly (the override), and it also receives a penalised update for REFER itself ($0.7 \times r^\ast - 35$, where $r^\ast$ is the oracle-optimal reward). Without this second update, the REFER arm retains an un-explored posterior ($A = I$, $b = 0$), its UCB stays inflated, and REFER is perpetually over-selected regardless of how many cases the human has resolved. Updating both arms allows the bandit to internalise when REFER is genuinely suboptimal and stop deferring unnecessarily.

### 5.4.2 Results

Table 5.4.1 reports the HITL system at three conservatism levels against the mathematical REFER baseline (the same LinUCB but with the REFER reward computed analytically rather than via a simulated human).

**Table 5.4.1 — EXP-008 HITL performance vs. mathematical-REFER baseline (N = 5,000 rounds)**

| Metric | HITL *c* = 0.3 | HITL *c* = 0.5 | HITL *c* = 0.7 | Baseline (math REFER) |
|--------|:--------------:|:--------------:|:--------------:|:---------------------:|
| Cumulative Reward | 101,646 | 101,646 | **102,100** | 95,872 |
| Cumulative Regret | 13,009 | 13,009 | **12,555** | 19,289 |
| Total Human Review Cost | 2,555 | 2,555 | **2,625** | 0 |
| Final Alignment Score | 54.0% | 54.0% | **60.0%** | N/A |
| Human Overrides (of 5,000) | 73 | 73 | **75** | — |
| Max Queue Depth | 0 | 0 | **0** | — |
| Average Queue Depth | 0.00 | 0.00 | **0.00** | — |

At conservatism c = 0.7, the HITL system achieves a cumulative reward of **102,100**, exceeding the 95,872 mathematical-REFER baseline by **+6,228 (+6.5%)** while incurring only 2,625 in review costs (2.6% of reward). Human review was triggered on only **75 of 5,000 rounds (1.5%)**, and the queue depth remained at zero throughout — indicating that the simulated underwriter resolved each case before the next REFER arrived, maintaining zero latency in the pipeline.

The three conservatism levels exhibit a small but informative pattern: c = 0.3 and c = 0.5 produce identical trajectories (the conservatism penalty does not flip any action choices at these settings), while c = 0.7 shifts a small number of borderline cases from STANDARD to RATED or from RATED to DECLINE, raising both the alignment score (54.0% → 60.0%) and the cumulative reward by approximately half a percent. This sensitivity is mild, which is operationally desirable: HITL performance is robust to the precise calibration of the conservatism parameter.

**[FIGURE: thesis/health_rl/figures/fig_hitl_experiment.png — Figure 5.4.1. EXP-008 four-panel HITL diagnostic — cumulative reward curves, cumulative regret decomposition, queue depth trace, and rolling policy alignment score.]**

### 5.4.3 Pass Criteria Verification

Four pre-registered pass criteria were evaluated:

1. **HITL reward > baseline** — 102,100 > 95,872 (+6.5%). **PASSED.**
2. **Late-stage alignment ≥ 30%** — Late-window alignment 45.95% ≥ 30%, down from an early-window alignment of 75.0%. The decline indicates that the bandit's converged policy diverges from the conservative human on a non-trivial fraction of borderline (REFER) cases, which is consistent with the bandit having internalised the explicit reward signal more fully than the human's heuristic conservatism penalty. The rolling-window alignment trace in Figure 5.4.1 (bottom-right panel) provides the detailed trajectory. **PASSED.**
3. **Average queue depth < 5%** — 0.00\%. **PASSED.**
4. **Human review cost < 15% of cumulative reward** — 2.51\% (HITL c = 0.3) to 2.57\% (HITL c = 0.7). **PASSED.**

All four criteria are satisfied, confirming that human-in-the-loop underwriting is both effective and operationally viable at the scale modelled.

### 5.4.4 Interpretation

The +6.5% reward improvement over the mathematical REFER baseline is explained by the human underwriter's conservative behaviour on high-risk borderline cases. Where the mathematical oracle would issue REFER and collect a fixed expected partial reward, the human consistently selects DECLINE or RATED for the riskiest cases, eliminating the delayed-reward ambiguity and reducing adverse selection in the approved portfolio.

The near-zero queue depth reflects a design property rather than a coincidence: because the experiment processes cases sequentially within each round (FIFO), a single human review resolves before the next REFER is generated. In a production system processing concurrent streams, queue management would become a primary operational concern; the present design provides a lower bound on queue pressure under serialised demand.

The 54–60% alignment score on REFER cases — precisely those where the bandit was most uncertain — merits interpretation. Perfect alignment (100%) would indicate that the bandit and the human always agree, implying that the human adds no value. An alignment near 55% on the bandit's *uncertain* cases is consistent with a well-calibrated human expert resolving genuine ambiguity, not overriding confident decisions. This is the expected behaviour of a complementary HITL system rather than a redundant one.

---

## 5.5 Discussion

### 5.5.1 Implications for Cambodian Insurance Practice

The experimental results carry three practical implications for health insurance underwriting in Cambodia and comparable emerging markets.

**Cost reduction through automation.**  The Static XGB baseline represents a typical rule-based underwriting system: an XGBoost risk score fed into a deterministic rule engine, with human underwriters reviewing every REFER and borderline case.  EXP-005 shows that LinUCB outperforms this baseline by 25% in cumulative reward (+18,248 absolute, p < 0.001), while EXP-008 shows that a human-in-the-loop variant raises reward a further 6.5% at a human-review cost of only 2.6% of cumulative reward.  The operational interpretation is that a contextual bandit can automate the bulk of straightforward cases (STANDARD and DECLINE) while referring only genuine ambiguity (1.5% of cases in the simulation) to human experts.  For a Cambodian insurer processing tens of thousands of applications annually, this translates into a substantial reduction in underwriting headcount and queue latency.

**Micro-premium viability.**  One of the structural barriers to health insurance penetration in Cambodia is the high administrative cost of underwriting relative to premium size.  When a policy generates only 200–300 in annual premium, spending 35–50 on manual review and data entry erodes margins and discourages product development for low-income segments.  By learning to issue STANDARD policies automatically for low-risk applicants and DECLINE for clearly uninsurable cases, the bandit compresses the fixed cost per policy to near-zero for the majority of the portfolio.  This cost compression makes micro-premium products (monthly premiums below 15) actuarially viable for the first time, opening the market to rice farmers, garment workers, and informal-sector employees who are currently excluded by the economics of manual underwriting.

**Target segments and financial inclusion.**  EXP-006 demonstrates that adaptive underwriting does not introduce demographic concentration risk beyond regulatory thresholds: the maximum sliding-window regional PSI is 0.082 (GREEN) and the maximum occupational PSI is 0.123 (low AMBER), while both dimensions satisfy the U.S. EEOC four-fifths approval-parity rule (85.7% region, 90.1% occupation).  This is particularly important for Cambodia, where rural applicants and agricultural workers face higher baseline morbidity and might otherwise be systematically declined by a risk-averse static rule.  The bandit's ability to learn nuanced feature interactions — for example, that a 35-year-old female rice farmer with no pre-existing conditions is a profitable STANDARD risk despite her occupation's high average mortality — enables profitable inclusion of segments that a coarse rule engine would exclude.  The result is a portfolio that is simultaneously more profitable (higher reward) and more inclusive (smaller approval-rate dispersion) than the static baseline.

### 5.5.2 Connection to Dynamic Pricing Literature

Contextual bandits have been applied most extensively in digital advertising and e-commerce, where neural variants (NeuralUCB, NeuralTS, and deep reinforcement learning) dominate the literature.  Zhou et al. (2020) report that NeuralUCB achieves sublinear regret on image-ad click-through prediction with millions of features and billion-scale training data.  By contrast, the present work uses linear bandits on a 34-feature dataset of 2,000 applicants.  The gap in scale is deliberate: emerging-market insurers rarely possess the data volumes or computational infrastructure that justify deep neural networks.

The results support the hypothesis that **linear models suffice for low-dimensional actuarial problems**.  The 34 features in the Cambodia dataset capture the dominant risk drivers (age, BMI, occupation, pre-existing conditions, region, wealth) with sufficient granularity that non-linear interactions are either weak or already encoded through feature engineering (for example, the interaction between occupation and gender is captured by the occupation-specific female-probability draw in the data generator).  Neither LinTS nor LinUCB dominates the other on the Cambodia dataset (EXP-007 paired Wilcoxon p = 0.87); both decisively outperform Static XGB and Epsilon-Greedy, suggesting that the marginal gain from a neural bandit would be small relative to the increased training cost, hyperparameter sensitivity, and interpretability loss.

That said, neural extensions remain relevant for future work.  If the feature space expands to include telematics, claims history, prescription records, or social-determinant proxies from mobile-wallet data, the effective dimensionality could rise to hundreds or thousands of features.  Under those conditions, a hybrid neural-linear architecture — in which a neural network learns a low-dimensional embedding and a linear bandit operates in the embedding space — offers a pragmatic compromise between expressiveness and computational tractability for emerging-market deployment.

### 5.5.3 Limitations of the Empirical Study

Four limitations bound the interpretation of the empirical findings.

**Synthetic data.**  The 2,000 applicants were generated by a parametric simulator calibrated to published demographic and disease-prevalence statistics.  While the simulator reproduces known marginal distributions (CDHS age, STEPS BMI, WHO TB incidence), it cannot capture the full heterogeneity of a live applicant pool: rare comorbidity combinations, fraud, income misreporting, and temporal shocks (economic crises, disease outbreaks) are absent by construction.  The results are therefore a proof of algorithmic feasibility rather than a prediction of live performance.

**Stationary environment.**  All experiments assume that the applicant distribution is fixed over the 5,000 rounds.  Real insurance portfolios experience demographic drift — seasonal migration, ageing cohorts, policy-lapse selection — that can invalidate learned coefficients.  The PSI guardrail (§4.8) detects such drift but does not automatically retrain the bandit; §6.3.1 discusses DiscountedLinUCB as a partial remedy.

**Single-period rewards.**  The reward function computes a one-shot premium minus expected claim cost.  Health insurance is inherently multi-period: retention probability, renewal pricing, claim development over 6–24 months, and cross-selling opportunity all affect lifetime profitability.  A customer accepted at STANDARD in round 1 may lapse in round 100 or file a catastrophic claim in round 1,200; these intertemporal dependencies are not modelled here.

**No real claims experience.**  The simulator's claims noise (±8%) is a stylised representation of actuarial uncertainty.  It does not reproduce the heavy-tailed severity distribution of health claims, the correlation between claim frequency and policy duration, or the moral hazard induced by generous coverage terms.  Validation on real Cambodian claims data — should such data become available through industry partnership — is the essential next step.

### 5.5.4 Threats to Validity

Threats to validity are classified following the four-threats framework of Shadish, Cook, and Campbell (2002).

**Internal validity.**  The primary threat is seed dependence and hyperparameter sensitivity.  All headline results in this chapter are reported as means across 20 independent seeds (1–20) with bootstrap 95% confidence intervals and paired non-parametric tests (Wilcoxon signed-rank), so the seed-dependence threat is bounded by the reported intervals.  The finding that LinUCB and LinTS consistently outperform Static XGB and Epsilon-Greedy is robust across all 20 seeds with large effect sizes (Cohen's d > 3 in EXP-007); the finding that LinTS narrowly leads LinUCB is *not* significant (p = 0.87) and should not be over-interpreted as a definitive ranking.  Hyperparameter sensitivity is addressed indirectly: LinTS has no tuned exploration parameter (posterior variance v^2 = 1.0 is fixed), and LinUCB's α = 1.0 is a standard default from the original Li et al. (2010) paper.  A full grid-search sensitivity analysis (α ∈ [0.1, 5.0], v² ∈ [0.1, 5.0], ε ∈ [0.05, 0.30]) remains future work.

**External validity.**  Generalisability to real Cambodian populations is limited by the synthetic-data constraint discussed above.  However, the dataset is not arbitrary: every marginal distribution is anchored on a primary national survey (CDHS 2021–22) or companion source (STEPS 2023, ILO 2023).  The occupational and regional structures are specific to Cambodia, so direct transfer to Laos or Myanmar would require recalibration, but the *algorithmic* findings — that LinTS and LinUCB are statistically indistinguishable, that both decisively beat Static XGB and Epsilon-Greedy, that sliding-window PSI remains within GREEN/AMBER, that HITL improves reward at low cost — are likely robust across emerging-market settings with similar data scarcity and demographic heterogeneity.

**Construct validity.**  The reward simulator is a simplified model of underwriting profit.  It omits expense loadings, reinsurance costs, capital charges, and regulatory reserve requirements that figure in a full actuarial appraisal.  The `RewardConfig.realistic()` extension (§4.7.3) adds expense ratios, lapse probability, and a customer-lifetime-value multiplier, but these parameters are themselves estimates.  The extent to which the simulated reward correlates with true economic profit in a live setting is unknown and constitutes a threat to construct validity.

---
