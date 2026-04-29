# CHAPTER IV. RESULTS AND DISCUSSION

---

## 4.1 EXP-005: Convergence Validation

### 4.1.1 Cumulative Reward and Regret

[Present the table: LinUCB $58,642 vs Static XGB $35,032 (+67%). Avg regret last 500 rounds: $5.35 vs $10.66.]

### 4.1.2 Action Distribution Evolution

[Early vs late action entropy. STANDARD rose from 28% to 42%; REFER fell from 24% to 9%.]

### 4.1.3 Learning Curve Analysis

[Discuss the reward and regret curves. When does LinUCB separate from baseline?]

### 4.1.4 Pass/Fail Assessment

[All three criteria met: reward > baseline, regret < baseline, entropy decreased.]

---

## 4.2 EXP-006: Fairness Audit

### 4.2.1 Regional Approval Parity

[Table/chart of approval rates by region. Phnom Penh 72%, Siem Reap 68%, ... Other Rural 58%. All >= 50% of max.]

### 4.2.2 Occupational Approval Parity

[Table/chart of approval rates by occupation. Civil Servant 75%, ... Construction Worker 52%. All >= 50% of max.]

### 4.2.3 PSI Results

[Region PSI = 0.0057 (GREEN). Occupation PSI = 0.0095 (GREEN).]

### 4.2.4 Pass/Fail Assessment

[All fairness constraints met without explicit demographic parity in reward function.]

---

## 4.3 EXP-007: Benchmark Comparison

### 4.3.1 Final Rankings

[Table: LinTS 1st ($62K reward, $5.6K regret), LinUCB 2nd, Epsilon-Greedy 3rd, Static XGB 4th.]

### 4.3.2 Statistical Significance

[Discuss variance across runs if available.]

### 4.3.3 Algorithm-Specific Behavior

[Why does LinTS win? Posterior sampling adapts automatically. Why does Epsilon-Greedy plateau? Wasteful random exploration.]

### 4.3.4 Pass/Fail Assessment

[All ranking criteria met.]

---

## 4.4 Discussion

### 4.4.1 Implications for Cambodian Insurance Practice

[Cost reduction, micro-premium viability, target segments.]

### 4.4.2 Connection to Dynamic Pricing Literature

[How do these results compare to neural bandit results in e-commerce? Linear models suffice for 25-feature problem; neural extensions await larger data.]

### 4.4.3 Limitations of the Empirical Study

[Synthetic data, stationary environment, single-period rewards, no real claims.]

### 4.4.4 Threats to Validity

[Internal: seed dependence, hyperparameter sensitivity. External: generalizability to real populations.]

---

*Skeleton — content to be expanded.*
