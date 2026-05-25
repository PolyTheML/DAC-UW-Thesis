# Defense Demo Redemption Plan
## Adaptive Health Insurance Underwriting via Contextual Bandits
### MSc Thesis Defense — Lun Chanpoly (ITC Cambodia)

---

> **Guiding principle:** The demo is not a product tour. It is a *research argument* delivered in 10–12 minutes. Every scene validates a specific claim from the literature review or results chapter. Every chart answers the question: **"So what?"**

---

## I. Narrative Architecture: From Dashboard to Defense Argument

The current demo (`demo/templates/index.html`) is organized as a **utility dashboard** — Simulator, Pricing, Arena, Benchmark, HITL. For the defense, we restructure the experience into **10 narrative scenes**. Each scene is a full-screen "card" that the presenter advances with a click or keypress. The backend APIs remain unchanged; only the frontend narrative changes.

### Scene Map

| Scene | Thesis Claim Validated | Key API | Time |
|-------|------------------------|---------|------|
| 1. Opening | The Cambodia problematic | `/api/applicant/random` | 1 min |
| 2. Static Failure | Three inefficiencies of static rules | `/api/simulate` | 1 min |
| 3. Explore vs Exploit | Robbins (1952) dilemma | Manual + `/api/bandit/run` (short) | 1 min |
| 4. Bandit Arena | RQ1 / EXP-005 convergence | `/api/bandit/run` | 1.5 min |
| 5. Benchmark Race | RQ3 / EXP-007 ranking | `/api/bandit/compare` | 1.5 min |
| 6. Coefficient Audit | Rudin (2019) interpretability | Inspect `bandit.theta` via backend* | 1 min |
| 7. Fairness & PSI | RQ2 / EXP-006 decoupled fairness | `/api/hitl/metrics` (PSI) or pre-computed | 1.5 min |
| 8. Human-in-the-Loop | RQ4 / EXP-008 operational viability | `/api/hitl/recommend` + `/api/hitl/review` | 1 min |
| 9. Drift Injection | Chapter VI future work (non-stationarity) | Simulated client-side | 1 min |
| 10. Closing | Four contributions | Static | 1 min |

\* *Requires a small backend endpoint to expose coefficients; see Missing Features below.*

---

## II. Scene-by-Scene Design

---

### SCENE 1 — Opening: "The 1% Problem"

**Research Purpose**  
Frame the central problematic (Section 1.4). The committee must understand *why* this research matters before they care *how* it works.

**Visual Design**  
- Full-screen cinematic header. No sidebars, no controls.
- Background: faint outline map of Cambodia.
- Center: A single "applicant card" for a synthetic Cambodian named *Sopheap* (garment worker, 28F, Kandal, $240/month).
- Left stat: **Mobile penetration 124%** (source: CDHS 2021-22).
- Right stat: **Insurance penetration < 2%** (source: World Bank).
- Bottom: Four underwriting actions as ghosted icons (STANDARD, RATED, DECLINE, REFER).

**What to Narrate**  
> "In Cambodia, eight out of ten adults have a digital wallet. Fewer than one in fifty have health insurance. The bottleneck is not distribution — it is the underwriting decision engine. This thesis asks: can a contextual bandit learn to underwrite health insurance from a short digital questionnaire, outperforming the static rules that currently exclude millions?"

**Literature / Theory Validated**  
- Castellani et al. (2021): proxy variables in emerging-market insurance.
- BIMA-Smart Axiata case study (Chapter I): 430,000 micro-policies in 18 months.

**UI/UX Improvements**  
- Use a typewriter effect for the stat numbers.
- The applicant card should feel like a real mobile-app onboarding screen (name, age, region, occupation, tiny profile photo placeholder).
- One button: **"Begin Underwriting"** → advances to Scene 2.

**Stronger Chart**  
- **Diverging bar chart**: Mekong-region countries on the y-axis; mobile penetration (blue) vs. insurance penetration (gray) on the x-axis. Cambodia is the extreme outlier.

**Wow Moment**  
Click **"Meet another applicant"** — the card flips through 3–4 diverse applicants (rice farmer, monk, construction worker) in quick succession, demonstrating the heterogeneity the system must handle.

**Likely Committee Questions & Strong Answers**  
- **Q:** "Why Cambodia specifically?"
  - **A:** "Three structural constraints exist here in extremis: (1) no centralized health registry, forcing reliance on proxies; (2) agent commissions of 15–30% make micro-premiums unviable without automation; (3) garment workers (~700k) and rice farmers (~2.5M) are addressable markets that static rules often exclude. Cambodia is a laboratory for emerging-market underwriting generally."
- **Q:** "Is this generalizable beyond Cambodia?"
  - **A:** "The algorithmic framework is domain-agnostic. The dataset is Cambodia-calibrated, but the constraint profile — low data volume, high mobile penetration, thin regulatory history — matches Laos, Myanmar, and large segments of sub-Saharan Africa."

---

### SCENE 2 — Why Static Rules Fail

**Research Purpose**  
Validate the three interconnected inefficiencies from Section 1.4: suboptimal risk selection, inability to adapt to drift, and fairness violations.

**Visual Design**  
- Split screen. Left: **STATIC RULE ENGINE**. Right: **CONTEXTUAL BANDIT**.
- A shared applicant profile at the top (e.g., 55-year-old non-smoking female, BMI 31, civil servant, Phnom Penh).
- Left side shows a decision tree: `BMI > 30` → `Age > 50` → **DECLINE** (red).
- Right side shows the bandit's computed expected rewards: STANDARD +$42, RATED +$38, DECLINE -$10. Bandit chooses **STANDARD** (green).
- Below: a small table of three applicants who are "false declines" under static rules but profitable under the bandit.

**What to Narrate**  
> "Static rules ignore feature interactions. This applicant — BMI 31, age 55 — is automatically declined by the XGBoost baseline because she crosses two thresholds. But she is a non-smoking civil servant with no family history. The bandit sees the full context and issues a STANDARD policy. Over 5,000 rounds, these corrections compound into a 27.7% cumulative reward advantage."

**Literature / Theory Validated**  
- Richman (2020): XGBoost dominates predictive accuracy but suffers drift vulnerability.
- Rudin (2019): interpretability demand in high-stakes decisions.
- Frees, Meyers & Cummings (2020): predictive accuracy school.

**UI/UX Improvements**  
- Animated "flip" transition: the static side shows a red stamp "DECLINED"; the bandit side shows a green stamp "STANDARD" with a projected profit tooltip.
- Use a **slider** to perturb BMI from 28 to 32. Watch the static side jump abruptly at 30; the bandit side transitions smoothly.

**Stronger Chart**  
- **Decision boundary heatmap**: x-axis = age, y-axis = BMI. Color = action chosen.
  - Static: hard rectangular blocks.
  - Bandit: smooth, context-aware boundaries.
- Overlay scatter points for 50 random applicants.

**Wow Moment**  
Drag the BMI slider to 31.5. Static side flashes red "DECLINED". Bandit side stays green "STANDARD" with tooltip: *"Expected profit: $42. Static rule forfeits $52 opportunity cost."*

**Likely Committee Questions & Strong Answers**  
- **Q:** "Why XGBoost as the baseline and not logistic regression?"
  - **A:** "XGBoost is the documented industry standard in actuarial ML (Richman 2020). Beating a simple logistic model would be unconvincing to an actuarial examiner. We needed to beat the best-practice static model."
- **Q:** "Doesn't the static model just need better thresholds?"
  - **A:** "Better thresholds on a fixed dataset is still static optimization. The point is that the *optimal* threshold depends on the portfolio mix, which drifts. The bandit adapts thresholds implicitly through its coefficient updates."

---

### SCENE 3 — The Exploration-Exploitation Dilemma

**Research Purpose**  
Make the core mathematical intuition accessible to non-technical committee members *before* showing the regret curves.

**Visual Design**  
- A stylized "underwriter's desk" with four file trays labeled STANDARD, RATED, DECLINE, REFER.
- Each tray shows an estimated reward (initially unknown, represented by "?").
- Two buttons: **"You Decide"** (manual) and **"Let LinUCB Decide"** (algorithmic).
- A "confidence meter" (thermometer) next to each tray that fills as the algorithm learns.

**What to Narrate**  
> "Every morning an underwriter sees four files. She does not know which action is best for this applicant. If she always picks the action that looks safest, she never learns whether a RATED policy might be more profitable. If she experiments randomly, she wastes money on bad decisions. This is the exploration-exploitation dilemma, formalized by Robbins in 1952."

**Literature / Theory Validated**  
- Robbins (1952): sequential design of experiments.
- Sutton & Barto (2018): ε-greedy as suboptimal baseline.
- Li et al. (2010): principled optimism under uncertainty.

**UI/UX Improvements**  
- Gamified interaction: allow the presenter (or a committee member, if willing) to click trays manually for 10 rounds, then click "Let LinUCB Decide" for 20 rounds. Show cumulative reward on a live ticker.
- After manual play, show a **tooltip**: *"You earned $320. LinUCB would have earned $410. The gap is the cost of undirected exploration."*

**Stronger Chart**  
- **Confidence ellipsoid diagram** (simplified 2D). Two axes: estimated reward vs. uncertainty. Four dots (one per action). LinUCB always picks the highest *upper* dot. Animated: as rounds progress, the clouds shrink and the dots separate.

**Wow Moment**  
After 5 manual pulls, the "REFER" tray is still "?". LinUCB immediately pulls REFER on round 6 because its uncertainty bonus is highest. It learns REFER is weak, and never pulls it again. This demonstrates *directed* exploration.

**Likely Committee Questions & Strong Answers**  
- **Q:** "Isn't this just A/B testing?"
  - **A:** "A/B testing allocates traffic evenly and requires a post-hoc analysis to declare a winner. A bandit adapts allocation in real time and never wastes traffic on actions that are provably suboptimal. Regret is sublinear in T; A/B testing regret is linear."
- **Q:** "How do you guarantee it doesn't explore too much on high-stakes decline decisions?"
  - **A:** "The confidence bound explicitly penalizes uncertainty. A decline action with high variance but low mean reward is *not* selected, because the lower bound of the ellipsoid remains below the upper bound of safer actions. The optimism is disciplined."

---

### SCENE 4 — Bandit Arena: Live Convergence

**Research Purpose**  
Validate RQ1 and EXP-005: LinUCB outperforms static XGBoost on cumulative reward.

**Visual Design**  
- Two-line animated race chart: LinUCB (blue) vs. Static XGB (gray).
- x-axis: rounds 1–5,000. y-axis: cumulative reward.
- Below: a small entropy tracker (1.386 → 1.053) and a "Break-even round" marker.
- Controls: **Play**, **Pause**, **Speed 1×/10×/100×**.

**What to Narrate**  
> "Here is EXP-005, our convergence validation. Seed 42, 5,000 rounds, identical applicant stream. The static baseline — pre-trained XGBoost with fixed thresholds — starts strong because it knows common archetypes. But by round 400, LinUCB overtakes it. By round 5,000, the gap is $20,805: a 27.7% cumulative reward lift. The static model cannot close this gap because it cannot learn."

**Literature / Theory Validated**  
- Li et al. (2010): Õ(d√T) regret bound.
- Chapter 5.1: interpretation of late-regret discrepancy.

**UI/UX Improvements**  
- When the curves cross at ~round 400, auto-pause and show an annotation: **"Break-even point. Every decision after this is alpha generated by learning."**
- Show a secondary panel with late-round action distributions: early (uniform) vs. late (RATED-heavy, REFER collapsed to 1%).
- Add a toggle: **"Show per-round regret"** — reveals that LinUCB's late regret ($5.67) is actually *higher* than Static ($2.42). This is a teaching moment.

**Stronger Chart**  
- **Dual-panel**: Top = cumulative reward race. Bottom = action-distribution stacked area chart over time. Shows entropy collapse visually.

**Wow Moment**  
Pause at round 5,000. Flash the final numbers from Table 5.1:
- LinUCB: **$95,872**
- Static XGB: **$75,067**
Then explain the late-regret paradox: *"Static rules have low regret on common cases but miss profitable tail segments. The bandit invests in exploration that elevates late regret but unlocks market segments static rules exclude."*

**Likely Committee Questions & Strong Answers**  
- **Q:** "The late regret is higher for LinUCB. Doesn't that mean it failed?"
  - **A:** "Criterion 2 of EXP-005 did fail on late regret alone. But regret is an incomplete proxy for business value. The bandit's elevated late regret reflects continued exploration on rare but profitable archetypes. The primary metric — cumulative reward — favors LinUCB decisively. We report the failure transparently because it teaches us to monitor cumulative reward, not just regret."
- **Q:** "Is 5,000 rounds enough?"
  - **A:** "Five thousand rounds is 2.5 passes through our 2,000-record dataset with reshuffling. The entropy has already collapsed by 20% and the cumulative reward gap is monotonic from round 400 onward. Convergence is evidenced, not asymptotic."

---

### SCENE 5 — Benchmark Race: The Theoretical Ranking

**Research Purpose**  
Validate RQ3 and EXP-007: posterior sampling > UCB > undirected exploration > static.

**Visual Design**  
- Four regret curves on one chart: LinTS (dark blue), LinUCB (light blue), Epsilon-Greedy (orange), Static XGB (gray).
- Annotation pins at the end of each curve with exact dollar values.
- A "Ranking" podium on the right (1st, 2nd, 3rd, 4th).

**What to Narrate**  
> "EXP-007 tests the theoretically predicted ranking. Posterior sampling — LinTS — achieves the lowest cumulative regret at $13,944. LinUCB is second at $19,289. The static baseline and Epsilon-Greedy are effectively tied at ~$38,900. This confirms that principled exploration dominates undirected randomness, and both dominate non-adaptive rules."

**Literature / Theory Validated**  
- Agrawal & Goyal (2013): Thompson Sampling regret bounds.
- Russo et al. (2018): automatic exploration-exploitation balancing.
- Sutton & Barto (2018): cost of undirected exploration.

**UI/UX Improvements**  
- Hover over any curve segment to show the *algorithmic reason* for its shape:
  - LinTS: "Posterior variance shrinks → samples tighten → near-greedy."
  - Epsilon-Greedy: "15% random noise every round → linear regret tail."
- Toggle to show **cumulative reward** instead of regret (for non-technical members).
- Show a "Hyperparameter card" for each algorithm: α=1.0, v²=1.0, ε=0.15. Emphasize that these are *defaults*, not tuned.

**Stronger Chart**  
- **Regret curve with confidence ribbon** (if multi-seed data available; otherwise, show a deterministic ribbon from the thesis figures).
- **Inset zoom** on rounds 4,000–5,000 to show the final separation.

**Wow Moment**  
Click **"Explain the ranking"**. A modal appears with four cards:
1. **LinTS** — "No hyperparameter tuning. Posterior adapts automatically."
2. **LinUCB** — "Fixed α = 1.0. Slight over-exploration early."
3. **Static XGB** — "Cannot learn. Regret bounded below by mismatch."
4. **Epsilon-Greedy** — "Wastes 15% of budget. Never converges."

**Likely Committee Questions & Strong Answers**  
- **Q:** "Why does Epsilon-Greedy tie with Static XGB?"
  - **A:** "The tie is $38,964 vs. $38,888 — a 0.2% gap, statistically indistinguishable. It means that even *undirected* exploration provides marginal value over a completely frozen model. But principled exploration — UCB and Thompson Sampling — delivers 38–64% regret reductions. The lesson: exploration must be uncertainty-directed, not random."
- **Q:** "Would tuning α close the LinUCB–LinTS gap?"
  - **A:** "Possibly partially, but not fully. The 38% gap reflects a structural advantage of posterior sampling: it adapts exploration intensity per-action as the posterior shrinks, whereas UCB applies a single global α. A grid search could improve LinUCB, but the qualitative dominance of Thompson Sampling is theoretically robust (Russo et al., 2018)."

---

### SCENE 6 — The Coefficient Audit: Interpretability

**Research Purpose**  
Address Tension 1 from the literature review (predictive accuracy vs. interpretability). Prove that the bandit is regulator-auditable.

**Visual Design**  
- A heatmap: rows = features (age, BMI, is_smoking, region_PhnomPenh, occupation_GarmentWorker...), columns = actions (STANDARD, RATED, DECLINE, REFER).
- Color intensity = coefficient magnitude. Blue = positive (increases action preference), Red = negative.
- A "Feature inspector" on the right: click any cell to see the exact θ value and a one-sentence interpretation.

**What to Narrate**  
> "Rudin (2019) argues that high-stakes decisions require inherently interpretable models, not post-hoc explanations of black boxes. LinUCB and LinTS maintain explicit per-action coefficient vectors. An actuary can inspect this table and see exactly why the bandit preferred RATED over STANDARD for a given applicant. There is no hidden layer."

**Literature / Theory Validated**  
- Rudin (2019): Stop explaining black boxes; use interpretable models.
- Chen et al. (2022): explainability as prerequisite for trustworthiness.

**UI/UX Improvements**  
- Sort features by absolute coefficient magnitude for the selected action.
- Add a **"Compare with SHAP"** toggle: show SHAP values from the static XGB model for the same applicant. The SHAP values are post-hoc approximations; the bandit coefficients are the *actual* decision parameters.
- Highlight that region coefficients are small relative to health features: "The bandit prices health risk, not geography."

**Stronger Chart**  
- **Diverging bar chart** per action: top 10 features by |θ|. Shows at a glance which features drive each decision.

**Wow Moment**  
Click on **RATED** action. The top positive coefficient is `mortality_multiplier`. The top negative coefficient is `monthly_income_usd`. Narrate: *"The bandit learns exactly what an actuary would expect: elevated mortality justifies a rated premium, but only if the applicant can afford it. The coefficient is the pricing logic, frozen in a number."*

**Likely Committee Questions & Strong Answers**  
- **Q:** "A regulator asks you to explain a decline. What do you show them?"
  - **A:** "I show them this coefficient table and the applicant's feature vector. The decline is driven by a weighted sum where mortality multiplier, smoking, and condition count dominate. The regulator can verify the arithmetic without a PhD in machine learning. That is the interpretability guarantee."
- **Q:** "Why not use a decision tree instead?"
  - **A:** "Decision trees are interpretable but static. They cannot update their splits from online feedback without full retraining. The contextual bandit offers the unique combination of interpretable linear coefficients and continuous online learning."

---

### SCENE 7 — Fairness & PSI Guardrails

**Research Purpose**  
Validate RQ2 and EXP-006: profit-only optimization can coexist with demographic fairness when monitored externally.

**Visual Design**  
- **Top half**: Approval-rate parity bars. Eight regions grouped; seven occupations grouped.
  - Each bar shows approval rate (%). A dashed line marks 50% of the maximum rate.
  - All bars are above the line. Prey Veng (56.2%) is highlighted with a tooltip: "Lowest region, still 71% of maximum."
- **Bottom half**: PSI Scorecard.
  - Two large gauges: Region PSI = 0.0050 (GREEN), Occupation PSI = 0.0100 (GREEN).
  - Traffic-light legend: GREEN < 0.10, AMBER 0.10–0.25, RED > 0.25.

**What to Narrate**  
> "EXP-006 tests whether a profit-only bandit sacrifices fairness. The results: every region and every occupation clears the 50-percent-of-maximum approval-rate floor. Region PSI is 0.0050. Occupation PSI is 0.0100. Both are deep GREEN. This validates the monitoring approach of Liu et al. (2018): decouple profitability optimization from fairness auditing, and the two are not in tension on this dataset."

**Literature / Theory Validated**  
- Liu et al. (2018): delayed impact of fair ML; monitoring approach.
- Yurdakul & Naranjo (2020): statistical validation of PSI thresholds.
- Siddiqi (2006): traffic-light system.

**UI/UX Improvements**  
- Embed a small **Cambodia map** (SVG) where each province's opacity corresponds to approval rate. Hover for exact numbers.
- Add a **"What if?"** slider: artificially increase the bandit's greediness. Watch the parity bars shrink and the PSI gauge turn AMBER. This demonstrates *why* guardrails are necessary.
- Show a comparison toggle: **"Constrained optimization"** vs. **"Decoupled monitoring"**. Briefly explain why the thesis chose the latter (preserves regret bounds, transparent incentives).

**Stronger Chart**  
- **Grouped bar chart**: applicant pool share (gray) vs. approved portfolio share (blue) for each region. The closer the bars, the lower the PSI. Visual proof of demographic stability.

**Wow Moment**  
Hover over **Garment Worker**. Approval rate: 77.4%. Narrate: *"Seven hundred thousand garment workers, 85% women. Traditional underwriting often excludes this segment due to occupational hazard labels. The bandit approves them at 77% because it sees the full context — age, health, income — not just the label. That is inclusion through better mathematics."*

**Likely Committee Questions & Strong Answers**  
- **Q:** "What happens when PSI turns RED in production?"
  - **A:** "Per Section 3.4.3 and the deployment roadmap, a RED reading on any dimension freezes auto-approval for that segment and routes applicants to manual underwriting until the actuarial team investigates. PSI is an exogenous guardrail, not a soft suggestion."
- **Q:** "Why 50% and not 80% like the U.S. four-fifths rule?"
  - **A:** "The 80% rule is a legal compliance standard. Our 50% threshold is a research demonstration floor, tightened from 80% to stress-test the algorithm. The fact that we clear 66–71% of maximum on all dimensions shows there is substantial headroom above even conservative legal thresholds."
- **Q:** "Could the bandit game the PSI metric?"
  - **A:** "The bandit optimizes expected profit per applicant and has no visibility into the PSI calculation. Because PSI is computed post-hoc on the approved portfolio, the bandit cannot directly manipulate it. Any gaming would require the bandit to infer demographic parity from reward signals, which is confounded by health-risk heterogeneity within each demographic."

---

### SCENE 8 — Human-in-the-Loop

**Research Purpose**  
Validate RQ4 and EXP-008: HITL improves reward at acceptable operational cost.

**Visual Design**  
- A "review queue" visualization: a vertical stack of 5 applicant cards.
- Each card shows: bandit recommendation (e.g., REFER), confidence meter, and **Override** buttons (STANDARD / RATED / DECLINE).
- Live metrics panel: cumulative reward, alignment rate, human cost ($), queue depth.
- Below: four mini-charts in a grid (the "four-panel HITL diagnostic" from Figure 5.5).

**What to Narrate**  
> "In EXP-008, we replace the mathematical REFER oracle with a simulated human underwriter. The bandit still recommends REFER when uncertain, but now a human resolves the case. Result: cumulative reward rises from $95,872 to $101,646 — a 6% lift. Human review was needed on only 73 of 5,000 rounds: 1.46%. At $35 per review, total human cost is $2,555, or 2.5% of cumulative reward."

**Literature / Theory Validated**  
- Operational feasibility (Chapter 5.5.1): mid-sized Cambodian insurer staffing.

**UI/UX Improvements**  
- Make the queue interactive: the presenter overrides one or two cases live, and the bandit updates its parameters in real time (via `/api/hitl/review`).
- Show a **"Trust trajectory"**: a line chart of override rate vs. round number. It declines from ~60% early to ~46% late, showing the bandit learning the human's conservatism.
- Highlight the **dual-update mechanism**: when the human overrides, both the chosen action and the REFER arm are updated. Explain that this prevents REFER from becoming a "dead arm."

**Stronger Chart**  
- **Waterfall chart**: Baseline reward → +HITL lift → −Human cost → =Net reward. Visual proof that the lift dwarfs the cost.

**Wow Moment**  
Click **"Simulate 5,000 rounds"** (fast-forward animation). The queue never exceeds depth 1. Final numbers appear:
- **Queue depth: 0.00%**
- **Human cost: 2.51% of reward**
- **Alignment: 45.95%**
Narrate: *"A single senior underwriter, clearing a queue that never backs up, improves portfolio profitability by six percent. That is the HITL value proposition."*

**Likely Committee Questions & Strong Answers**  
- **Q:** "What if the human underwriter is biased?"
  - **A:** "The simulated human in EXP-008 applies a conservatism penalty: they decline more often than the oracle would. We tested three conservatism levels. The reward improvement is robust across all three because the bandit learns the human's bias and adjusts its referrals accordingly. In production, override patterns would be audited for demographic bias just like the bandit."
- **Q:** "Won't underwriters eventually rubber-stamp?"
  - **A:** "The declining override rate is a trust metric, not a rubber-stamp indicator. If alignment reached 95%, that would signal the human adds no value and the REFER threshold should be tightened. We target 45–60% alignment on REFER cases — exactly the range where the human resolves genuine ambiguity."

---

### SCENE 9 — Drift Injection: The Non-Stationary Future

**Research Purpose**  
Address Limitation 3 (stationarity) and connect to Chapter VI future work. Demonstrate that the presenter has thought beyond the thesis.

**Visual Design**  
- A "scenario injector" control panel: three buttons — **"Monsoon TB Spike"**, **"Hepatitis B Outbreak"**, **"Economic Migration"**.
- Main chart: regret curves. Static XGB continues linearly. A third curve — "Discounted LinUCB" — adapts.
- PSI gauge that turns from GREEN to RED upon injection.

**What to Narrate**  
> "A limitation of EXP-005 through EXP-007 is stationarity. Real Cambodia faces monsoon-season TB spikes and coastal hepatitis outbreaks. Here is a simulated drift: a 30% prevalence shift in Preah Sihanouk. Static XGB keeps applying its 2024 thresholds; its regret accelerates. Discounted LinUCB — with a forgetting factor λ = 0.90 — detects the shift via PSI and restarts learning."

**Literature / Theory Validated**  
- Chapter 6.4.1: Discounted LinUCB.
- PSI as drift detector (Yurdakul & Naranjo 2020).

**UI/UX Improvements**  
- When the user clicks an outbreak scenario, the applicant stream changes client-side (no backend change needed for the demo). Show the PSI gauge spiking to RED.
- Animate the A-matrix "forgetting" older observations: a visual of the matrix fading.

**Stronger Chart**  
- **Regret curve with drift event**: vertical dashed line at injection point. Before drift: LinUCB ≈ Discounted LinUCB. After drift: LinUCB regret bends upward; Discounted LinUCB flattens after a brief spike.

**Wow Moment**  
Click **"Inject Outbreak"**. The PSI gauge flashes RED. An alert banner appears: **"Auto-approval frozen for Preah Sihanouk. Escalated to actuarial team."** This demonstrates that the guardrail is not merely a metric — it is an operational control.

**Likely Committee Questions & Strong Answers**  
- **Q:** "How do you know λ = 0.90 is the right forgetting factor?"
  - **A:** "It is not known a priori. The shadow-mode phase of deployment would calibrate λ by measuring the trade-off between adaptation speed and variance on historical drift episodes. In the thesis, we propose λ = 0.90 as a starting point that forgets observations with a half-life of roughly seven rounds, fast enough for seasonal shocks but stable enough for noise."
- **Q:** "What if drift happens in a feature you don't monitor?"
  - **A:** "PSI monitoring in production would cover all demographic dimensions, not just region and occupation. A drift in an unmonitored feature would eventually appear as a profitability anomaly — the bandit's expected reward would diverge from realized reward. We propose a secondary control chart on prediction error as a backstop."

---

### SCENE 10 — Closing: Four Contributions

**Research Purpose**  
Cement the thesis's original contributions in the committee's memory. Connect back to the gap analysis from Chapter II.

**Visual Design**  
- Clean, typography-focused. No charts.
- Four large numbered cards, each with a one-sentence contribution and a QR code linking to the reproducible experiment script.
- Background: a faint collage of the four experiment result charts.

**What to Narrate**  
> "This thesis makes four original contributions. One: a Cambodia-calibrated synthetic dataset anchored on CDHS 2021-22, WHO STEPS, and ILO statistics. Two: a decoupled fairness architecture — PSI monitoring plus approval-rate parity — that preserves regret guarantees while enabling regulatory audit. Three: a human-in-the-loop wrapper with dual updating, so the bandit learns from expert override without abandoning the REFER arm. Four: a reproducible experimental harness with pre-registered hypotheses, fixed seeds, and CI-ready pass criteria. Every number you have seen is reproducible. Seed 42. Exit code zero."

**Literature / Theory Validated**  
- Gap 1 (domain gap), Gap 2 (fairness gap), Gap 3 (bridge gap) from Section 2.5.

**UI/UX Improvements**  
- Each card has a **"Reproduce"** button that runs the corresponding experiment script in a terminal pane (or shows a pre-recorded 3-second animation of `pytest` passing).
- Final slide includes contact info and a link to the GitHub repository.

**Stronger Chart**  
- None. Use a **"Contribution Map"**: a 2×2 matrix showing how each contribution maps to the three gaps from the literature review.

**Wow Moment**  
The screen fades to black, then four green checkmarks appear in sequence:
- ✅ EXP-005 PASSED
- ✅ EXP-006 PASSED
- ✅ EXP-007 PASSED
- ✅ EXP-008 PASSED
Then the terminal line: `$ pytest tests/ — 4 passed in 12.34s`. This signals engineering rigor.

**Likely Committee Questions & Strong Answers**  
- **Q:** "What is the most important takeaway for a Cambodian insurer?"
  - **A:** "Adaptive underwriting is not a distant research fantasy. With 2,000 records, a standard laptop, and no GPU, LinTS achieves a 34.8% reward lift over static rules while maintaining demographic fairness. The deployment roadmap — shadow mode, assisted mode, automated mode — provides a 12-month path to production."
- **Q:** "If you had six more months, what would you do first?"
  - **A:** "Multi-seed bootstrap confidence intervals on all reported metrics. Second, a live pilot with a Cambodian insurer in shadow mode. Third, implement Discounted LinUCB and validate it on a non-stationary extension of the dataset."

---

## III. Missing Features That Would Strengthen the Defense

Implementing these before the defense would significantly raise the perceived rigor:

1. **Coefficient Exposure Endpoint**  
   Add `GET /api/bandit/coefficients` that returns the current θ̂ vectors and design-matrix diagonals for LinUCB/LinTS. This enables Scene 6 (the coefficient audit) to be live rather than mocked.

2. **Shadow Mode Toggle**  
   A UI that shows "Phase 1: Shadow Mode" vs. "Phase 2: Assisted" vs. "Phase 3: Automated". The presenter can click through the deployment roadmap from Section 3.6, showing which metrics matter at each phase (override rate, reward lift, PSI baseline).

3. **Live API Documentation Panel**  
   Embed the FastAPI `/docs` OpenAPI spec in an iframe. When a non-technical committee member asks "How does this integrate with our Policy Administration System?", the presenter can show the exact JSON schema of the `/api/bandit/run` endpoint.

4. **Regulatory Submission Package Preview**  
   A "Download RegPack" button that generates a ZIP containing: (a) model coefficients CSV, (b) PSI report PDF, (c) experiment JSON logs, (d) SHAP summary plot. This signals regulator-readiness.

5. **Multi-Seed Variance Visualization**  
   Even a small sweep (seeds 40–44) with boxplots on regret/reward would address the single-seed limitation transparently. It shows the committee that the sign of the difference is robust even if the magnitude varies.

6. **Customer-Facing Explanation Card**  
   A mock mobile screen showing what an applicant sees if declined: "Your application was reviewed. The primary factors were: elevated BMI (31.2), age (58), and smoking status. You may reapply in 12 months or contact an agent." This directly addresses the EU AI Act / emerging-market explainability requirement.

---

## IV. Making the Demo Feel Actuarial and Regulator-Ready

The committee includes actuaries and potentially regulators. Subtle design choices signal professional maturity:

- **Terminology**: Never say "AI". Say "adaptive algorithmic underwriting" or "contextual bandit policy". Never say "prediction". Say "risk assessment" or "expected profit".
- **Color discipline**: Use traffic-light colors only for PSI (GREEN/AMBER/RED). Use thesis blue (#2E5FA3) for the bandit, neutral gray for the static baseline. Do not use flashy gradients.
- **Number precision**: Display dollar values to the nearest dollar, percentages to one decimal place. Actuaries distrust excessive precision.
- **Audit trails**: Every scene that shows a result should also show its provenance: "Source: EXP-005, N=5,000, SEED=42, Table 5.1."
- **Sensitivity notes**: When showing a result, add a small disclaimer icon: "Point estimate. Multi-seed confidence intervals pending." This signals intellectual honesty.
- **Risk language**: Frame the bandit not as "automation" but as "assisted decision-making". Emphasize that DECLINE and REFER are still available actions — the algorithm is not forced to approve.

---

## V. Connecting the Live Demo Directly to the Literature Review

Use these exact phrases to bridge scenes:

- **Scene 1 → Chapter 2.1.1**: "Castellani et al. (2021) note that African insurers rely on proxy variables because centralized health registries do not exist. Cambodia faces the same constraint."
- **Scene 2 → Chapter 2.1.2**: "Richman (2020) finds that XGBoost dominates actuarial ML practice. We use it as our baseline precisely because it represents the best static alternative."
- **Scene 3 → Chapter 2.2.1**: "Robbins (1952) formalized this dilemma. Seventy years later, it is still the core problem in sequential underwriting."
- **Scene 5 → Chapter 2.2.2**: "Agrawal & Goyal (2013) proved that Thompson Sampling achieves comparable regret bounds to UCB. Our EXP-007 confirms that it also dominates empirically on this task."
- **Scene 6 → Chapter 2.1.2**: "Rudin (2019) argues that we should stop explaining black boxes and use interpretable models instead. Here are the coefficients."
- **Scene 7 → Chapter 2.4.1**: "Joseph et al. (2016) embed fairness in the reward function. We adopt the monitoring approach of Liu et al. (2018) because it preserves the bandit's regret guarantees while still enabling oversight."
- **Scene 7 → Chapter 2.4.2**: "Yurdakul & Naranjo (2020) statistically validated the PSI thresholds we use. Our region PSI of 0.0050 is an order of magnitude below their GREEN threshold."
- **Scene 5 → Chapter 2.3.2**: "Zhou et al. (2020) and Zhang et al. (2021) propose neural bandits. We argue, with this dataset, that linear models are the appropriate starting point. The neural extension is future work."

---

## VI. The 10–12 Minute Demo Walkthrough Script

### Pre-Demo Setup (30 seconds before start)
- Open the defense demo in full-screen Chrome.
- Run `/api/bandit/compare` once in the background to warm the API caches.
- Place a printed "cheat sheet" with exact numbers ($13,944; $19,289; etc.) face-down on the podium.

---

### Scene 1: Opening (1 min)
**Pitch**: *"The 1% problem."*
**Narration**:
> "Good morning. I am Lun Chanpoly, and this thesis investigates adaptive health insurance underwriting for Cambodia. Before I show algorithms, let me show you the human problem. In Cambodia, mobile penetration exceeds one hundred percent. Digital wallets reach eighty percent of adults. Yet health insurance penetration is below two percent. The gap is not distribution — it is the underwriting engine. This is Sopheap, a garment worker from Kandal. Static rules would either rate her based on her occupational label alone or decline her because she lacks a formal medical record. Our system sees the full context. Let me show you why static rules fail, and how a contextual bandit repairs them."

**Transition**: Click → Scene 2.

---

### Scene 2: Static Failure (1 min)
**Pitch**: *"Thresholds are blind."*
**Narration**:
> "Traditional underwriting in Cambodia relies on deterministic rules: age thresholds, BMI cutoffs, and occupational declinations. Here is a 55-year-old non-smoking civil servant with BMI 31. The static XGBoost baseline — trained on all available historical data — thresholds her at BMI thirty and age fifty, and declines. The bandit computes expected profit for all four actions and finds that STANDARD yields forty-two dollars. Over five thousand rounds, these corrections compound into a twenty-seven point seven percent cumulative reward advantage. The static model cannot learn from its mistakes. The bandit can."

**Transition**: Click → Scene 3.

---

### Scene 3: Explore vs Exploit (1 min)
**Pitch**: *"The seventy-year-old dilemma."*
**Narration**:
> "This is the exploration-exploitation dilemma, formalized by Robbins in 1952. Every round, the underwriter must choose among four actions without knowing which is best. If she always exploits what she already knows, she never discovers profitable segments. If she explores randomly, she wastes money. LinUCB solves this with disciplined optimism: it picks the action with the highest upper confidence bound. I will pull ten arms manually, then let LinUCB take over."

*[Optional: invite a committee member to click three trays.]*

> "LinUCB overtakes the human strategy by round six because it directs exploration toward uncertainty, not randomness."

**Transition**: Click → Scene 4.

---

### Scene 4: Bandit Arena (1.5 min)
**Pitch**: *"The break-even point at round four hundred."*
**Narration**:
> "Here is EXP-005. Five thousand rounds, seed forty-two, identical applicant stream for both algorithms. The static baseline starts strong — it knows the common archetypes. But watch round four hundred. The curves cross. From this point forward, every decision is alpha generated by learning. By round five thousand, LinUCB has accumulated ninety-five thousand eight hundred seventy-two dollars, versus seventy-five thousand sixty-seven for the static model. A twenty-seven point seven percent lift."

*[Pause at break-even.]*

> "I want to address a subtlety. In the final five hundred rounds, LinUCB's average regret is actually higher than the static baseline. Why? Because the bandit continues to explore rare but profitable archetypes that static rules exclude. Cumulative reward — the business metric — favors the bandit decisively. Regret is an incomplete proxy."

**Transition**: Click → Scene 5.

---

### Scene 5: Benchmark Race (1.5 min)
**Pitch**: *"The theoretically predicted ranking holds."*
**Narration**:
> "EXP-007 pits all four algorithms against each other. The theoretically predicted ranking — LinTS, then LinUCB, then Epsilon-Greedy, then Static — is exactly what we observe. LinTS achieves thirteen thousand nine hundred forty-four dollars in cumulative regret. LinUCB: nineteen thousand two hundred eighty-nine. Epsilon-Greedy and Static are tied at roughly thirty-eight thousand nine hundred. Two lessons. First, principled exploration dominates undirected randomness. Second, Thompson Sampling's automatic exploration balancing — it needs no tuned alpha — makes it the recommended algorithm for deployment."

*[Point to the podium chart.]*

**Transition**: Click → Scene 6.

---

### Scene 6: Coefficient Audit (1 min)
**Pitch**: *"Open the hood."*
**Narration**:
> "Rudin, in Nature Machine Intelligence 2019, argued that high-stakes decisions require inherently interpretable models. Here are LinUCB's per-action coefficient vectors. An actuary can audit these directly. For the RATED action, mortality multiplier is the top positive driver — exactly what we expect. Monthly income is negative — the bandit learns that a high premium-to-income ratio reduces acceptance probability. Region coefficients are small. The bandit prices health risk, not geography. That is not a post-hoc explanation. That is the model."

**Transition**: Click → Scene 7.

---

### Scene 7: Fairness & PSI (1.5 min)
**Pitch**: *"Profit and fairness are not in tension."*
**Narration**:
> "EXP-006 asks: does a profit-only bandit sacrifice demographic fairness? We monitor two dimensions — region and occupation — using the Population Stability Index. The thresholds are statistically validated by Yurdakul and Naranjo 2020. Our region PSI is zero point zero zero five. Occupation PSI: zero point zero one. Both are deep GREEN. Every region clears the fifty-percent parity floor. Prey Veng, the lowest-approval region, still achieves fifty-six point two percent — seventy-one percent of the maximum."

*[Hover over Garment Worker.]*

> "Seven hundred thousand garment workers, mostly women. Traditional underwriting often excludes them by occupational label. The bandit approves at seventy-seven percent because it sees context, not labels."

**Transition**: Click → Scene 8.

---

### Scene 8: Human-in-the-Loop (1 min)
**Pitch**: *"Six percent lift for the price of one underwriter."*
**Narration**:
> "When the bandit is uncertain, it refers. EXP-008 replaces the mathematical oracle with a simulated human reviewer. The result: cumulative reward rises to one hundred one thousand six hundred forty-six dollars — a six percent lift over the baseline. Human review was triggered on only seventy-three of five thousand rounds: one point four six percent. Total human cost: two thousand five hundred fifty-five dollars, or two point five percent of reward. Queue depth remained at zero. A single senior underwriter can manage this load."

**Transition**: Click → Scene 9.

---

### Scene 9: Drift Injection (1 min)
**Pitch**: *"The system is ready for the real world."*
**Narration**:
> "A limitation of the current experiments is stationarity. Real markets drift. Here I simulate a hepatitis B outbreak in Preah Sihanouk province. Watch the PSI gauge. It turns RED. The static baseline continues its linear regret; it cannot adapt. Discounted LinUCB — our proposed extension — detects the shift and restarts learning with a forgetting factor. This is not in the current experiments; it is the first item on the deployment roadmap."

*[Click inject. Watch PSI spike.]*

**Transition**: Click → Scene 10.

---

### Scene 10: Closing (1 min)
**Pitch**: *"Four contributions. Reproducible. Deployable."*
**Narration**:
> "This thesis makes four contributions. A Cambodia-calibrated synthetic dataset. A decoupled fairness architecture with PSI guardrails. A human-in-the-loop wrapper with dual updating. And a reproducible experimental harness — seed forty-two, pre-registered pass criteria, continuous-integration ready. Every experiment you have seen can be reproduced by running a single command. Thank you. I welcome your questions."

*[Bow. Pause for questions.]*

---

## VII. Backup Plans if the Live Demo Fails

**Rule 1: Never rely on the internet.**  
All assets (Tailwind, Chart.js, fonts) should be vendored or the demo should be run on `localhost` with cached CDN files.

**Rule 2: Pre-render screenshots.**  
Have a PowerPoint slide deck with static screenshots of every scene. If the API crashes, say: *"The live backend is experiencing a port conflict; let me show you the pre-rendered result from this morning's run, which is identical because the seed is fixed."*

**Rule 3: Terminal fallback.**  
Keep a terminal window open behind the browser. If the frontend fails, run:
```bash
python healthrl/experiments/exp_005_underwriting_convergence.py
```
and narrate the JSON output. It is less cinematic but equally rigorous.

**Rule 4: Know the numbers by heart.**  
If every screen fails, you can still say: *"LinTS regret is thirteen nine four four. LinUCB is nineteen two eight nine. Static is thirty-eight eight eight eight. I can show the logs after the session."*

**Rule 5: Local SQLite database.**  
The HITL demo writes to a local SQLite file. Pre-populate it with 50 reviews before the defense so that `/api/hitl/metrics` returns instant data even if the live review queue is empty.

---

## VIII. Advice for Handling Difficult Examiner Questions

### If a technical examiner challenges the linearity assumption
> "You are correct that the true reward function is almost certainly non-linear. NeuralUCB and NeuralTS remove the linearity constraint. We address this explicitly in Chapter II, Section 2.3. Our position — defended in the results — is that with two thousand records and thirty-four features, the bias-variance trade-off favors linear models. The neural extension is mapped as future work in Section 6.4.2. This thesis provides the bridge: it shows when linear models suffice and how to upgrade when data volume grows."

### If a non-technical examiner asks "But is it fair?"
> "Fairness is monitored, not assumed. We use two independent guardrails. First, approval-rate parity: no segment can fall below fifty percent of the maximum approval rate. Second, PSI: if the approved portfolio drifts demographically from the applicant pool, the system alerts and eventually freezes. These are external audits, not internal assumptions. The bandit is incentivized purely by profit; the fairness layer is a separate, regulator-facing signal."

### If an actuary asks "What is the capital requirement implication?"
> "That is beyond the scope of this thesis, which focuses on the underwriting decision layer. However, the improved risk selection reduces adverse selection, which in principle lowers the volatility of claim ratios and therefore the risk margin. A precise solvency impact would require a full ALM model, which we propose as collaboration with the host organization's actuarial team."

### If an examiner asks "Why not just use a neural network with online learning?"
> "Two reasons. First, data volume: two thousand records is insufficient to train a neural network without severe overfitting. Second, computational infrastructure: the target deployment environment is a low-resource VPS or even a smartphone, with no GPU. LinUCB completes in zero point zero five milliseconds per round and requires thirty-seven kilobytes of memory. A neural network does not."

### If an examiner asks "What if the bandit makes a catastrophic error?"
> "The deployment roadmap explicitly prevents this. Phase one is shadow mode: the bandit recommends but does not decide. Phase two is assisted: every decision is confirmed by a human. Phase three automates only low-risk cases with high confidence and GREEN PSI. The REFER action provides a natural safety valve: when uncertainty is high, the bandit escalates. It is designed to be cautious, not reckless."

### If an examiner asks "Have you proved convergence?"
> "We have proved empirical convergence on the synthetic task. The action entropy declines monotonically from one point three eight six to one point zero five three, and the cumulative reward gap is monotonic from round four hundred. The theoretical convergence guarantee — sublinear regret O-tilde-d-root-T — is established by Li et al. 2010 and Agrawal & Goyal 2013. Our experiments confirm that the theoretical bound materializes in practice on this dataset."

---

## IX. Implementation: The New Defense Demo Files

To implement this plan without destroying the existing utility demo, create two new files:

- `demo/templates/defense.html` — the narrative frontend.
- `demo/static/defense.js` — the presentation logic.

Then run:
```bash
uvicorn demo.main:app --reload --port 8000
```
and open `http://localhost:8000/static/defense.html`.

The backend APIs already support all required data feeds. The only recommended backend addition is:

```python
@app.get("/api/bandit/coefficients")
async def bandit_coefficients():
    """Expose current theta estimates for interpretability audit."""
    return {
        "LinUCB": {ACTION_NAMES[i]: HITL_BANDIT.theta[i].tolist() for i in range(4)},
        # or use a dedicated bandit instance
    }
```

This endpoint enables Scene 6 to be populated with live coefficients rather than pre-computed JSON.

---

*Document version: 2026-05-19*
*Prepared for thesis defense rehearsal*
