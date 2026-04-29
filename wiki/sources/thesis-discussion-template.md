# Thesis Chapter 5: Discussion & Conclusion Template

**Created**: 2026-04-17  
**Format**: ITC Cambodia standard  
**Chapter**: V (DISCUSSION AND CONCLUSIONS)  
**Pages**: Typically 4-8 pages  
**Typical Word Count**: 2,500-3,500 words

---

## Chapter 5 Structure

### Formatting Rules
- **Chapter Header**: "CHAPTER V. DISCUSSION AND CONCLUSIONS" (all caps, 16pt bold, centered)
- **Section Headers**: "5.1 [Section Title]" (12pt bold)
- **Subsection Headers**: "5.1.1 [Subsection]" (12pt, italic)
- **Font**: Times New Roman, 12pt
- **Spacing**: 1.5 or double line spacing
- **Tone**: Interpretive, analytical, forward-looking

### Five-Section Structure

1. **5.1 Interpretation of Results** — What do the findings mean?
2. **5.2 Comparison with Literature** — How do your findings relate to prior work?
3. **5.3 Limitations** — What are the constraints? What didn't you test?
4. **5.4 Practical Implications** — What should practitioners do?
5. **5.5 Future Work and Recommendations** — What comes next?

---

## Example 1: Discussion Chapter (Stress-Testing Thesis)

```
CHAPTER V. DISCUSSION AND CONCLUSIONS


5.1 Interpretation of Results

5.1.1 What the Findings Tell Us

Our three experiments provide strong evidence that PSI alone is insufficient for drift monitoring 
in emerging market underwriting, and that a multi-metric framework successfully addresses PSI's 
failure modes. Specifically:

**EXP-001 and EXP-002 validate PSI's primary strength**: PSI is an effective detector of large 
population distribution shifts. The baseline validation confirms that the synthetic generator is 
stable and reproducible. The responsiveness experiment demonstrates that PSI increases 
monotonically with distortion, enabling practitioners to estimate the magnitude of drift from 
the PSI value alone. This validates decades of actuarial practice using PSI as the primary 
drift metric. We found no issues with PSI's implementation or responsiveness.

**EXP-003 reveals PSI's critical blindspots**: The three adversarial scenarios represent 
realistic situations in emerging markets. Label drift (government health programs) occurs 
regularly as policy and infrastructure improve. Feature-PSI decoupling (new cohort influx) 
happens when insurance products reach new market segments. Bin edge camouflage (occupational 
shifts) can occur rapidly in developing economies undergoing structural change. In all three 
cases, PSI failed to alert (remaining GREEN or barely AMBER) while portfolio risk composition 
changed substantially. This is not a theoretical edge case—these are practical failure modes 
that practitioners should expect and prepare for.

**Multi-metric monitoring successfully addresses all three failure modes**: Each failure mode 
has a corresponding secondary metric that correctly detects the problem:
- Label drift → feature co-occurrence PSI
- Feature-PSI decoupling → marginal age distribution PSI
- Bin edge camouflage → HITL escalation rate monitoring

All three secondary metrics triggered RED or AMBER alerts when PSI remained GREEN. This 
validates our proposed framework and provides a practical, implementable solution.

5.1.2 Magnitude of Impact

What magnitude of drift should practitioners be concerned about?

From EXP-002: A 25% population shift results in PSI = 0.0167 (GREEN, no alert). This is 
concerning because 25% is not trivial—it represents a fundamental change in the applicant 
pool composition. In Cambodia's context, a 25% influx of motorbike couriers (higher risk) or 
young professionals (lower risk) would substantially alter the portfolio's risk profile. Yet 
PSI gives no alert.

From EXP-003: A 15% shift crossing a tier boundary causes HITL escalation rates to double 
(from 14.7% to 29.4%). This has immediate operational impact: more cases requiring human 
review, longer processing times, higher costs. Yet PSI doesn't alert.

Conclusion: PSI's safety margin (GREEN threshold of 0.10) is adequate for large, obvious 
shifts (>30%), but insufficient for the medium-sized shifts (15%-30%) that represent the 
most common real-world scenarios.


5.2 Comparison with Literature

5.2.1 Consistency with Prior Work

Our findings align with and extend existing drift detection literature:

**On univariate drift monitoring**: Gama et al. (2014) noted that single-metric drift 
detection can miss concept drift. Our empirical validation in the insurance context supports 
this concern. Moniz & Bifet (2018) proposed ensemble methods for drift detection; our 
multi-metric approach is a lightweight alternative optimized for actuarial practice.

**On emerging market ML challenges**: Buolamwini & Gebru (2018) documented bias in face 
recognition systems in African markets; Bietti (2021) discusses fairness in AI for developing 
economies. Our work extends this: not just bias, but distribution shift itself is harder to 
detect reliably in emerging markets due to rapid population changes.

**On feature drift vs. label drift**: Moreno-Torres et al. (2012) formalized the distinction. 
Our Failure Mode 1 (label drift) demonstrates this concretely in insurance: features change 
but labels don't, leading to blind spots in label-based monitoring (like PSI on mortality_ratio).

5.2.2 Novel Contribution of This Work

Where does this thesis advance the field?

1. **First empirical PSI validation in emerging market context**: Existing literature assumes 
   PSI works uniformly. This is the first controlled stress-test specific to emerging market 
   conditions (sparse data, rapid changes, Cambodia-specific risk factors).

2. **Identification of realistic failure modes**: Prior work is largely theoretical. This thesis 
   provides three concrete, reproducible failure scenarios that practitioners can relate to and 
   prepare for.

3. **Practical, lightweight solution**: Rather than proposing complex ensemble methods, we propose 
   a simple multi-metric framework using PSI + 3 secondary metrics. This is immediately 
   implementable without system overhauls.

4. **Actionable thresholds and recommendations**: We provide specific alert thresholds (AMBER 
   at 0.10, RED at 0.25) and decision rules (e.g., "If age PSI > 0.10, investigate cohort shift"). 
   This is more actionable than theoretical contributions.


5.3 Limitations

5.3.1 Data and Assumptions

**Limitation 1: Synthetic data ≠ real world**
- Our stress-testing uses synthetic applicants, not real claims data
- Synthetic generator uses simplified demographic models (normal distributions, logistic curves 
  for age-dependent conditions)
- Real claims data may have fat tails, multimodal distributions, or unexpected patterns not 
  captured in the generator

Mitigation: We calibrated the generator to match Cambodia census and health survey statistics. 
Key parameters (age mean, BMI mean, occupational multipliers) are derived from real-world 
sources. However, for production deployment, validation on real data is essential.

**Limitation 2: Binary distortion scenarios**
- We tested distortions as "inject high-BMI couriers" (clean, controlled)
- Real-world distortions are messier: gradual shifts, multiple simultaneous changes, 
  hard-to-characterize patterns
- Our 40% distortion is more extreme than typical real-world drift

Mitigation: This is intentional. By testing extreme scenarios (40%-50% distortion), we create 
a "stress test" that bounds system behavior. Real distortions will likely be less extreme and 
easier to detect.

**Limitation 3: Small dataset assumption**
- Our experiments use 10K applicants (reasonably large for Cambodia market, but small for 
  mature markets)
- Conclusions may not transfer directly to markets with 100K+ annual applicant volumes

Mitigation: The relative proportions (8-bin histogram) should be stable across volumes. However, 
readers should validate findings on their own data scales.

5.3.2 Methodological Limitations

**Limitation 4: 8-bin histogram is arbitrary**
- Our PSI calculation uses 8 equally-spaced bins for mortality_ratio
- Optimal bin width depends on the true distribution shape, which we don't know
- Different binning could yield different PSI values and alert patterns

Mitigation: We tested 8 bins because it's standard in actuarial practice. Future work should 
explore adaptive binning or kernel-based density estimation for more robust drift detection.

**Limitation 5: Secondary metrics are scenario-specific**
- Feature co-occurrence PSI works for label drift but not other failure modes
- Age distribution PSI works for cohort shift but not label drift
- No single secondary metric detects all three failure modes

Implication: Practitioners must monitor all four metrics (PSI + 3 secondary) to get full coverage. 
This is more complex than single-metric monitoring but necessary given the failure modes.

**Limitation 6: No real-world validation**
- All experiments are on synthetic data with known properties
- Real-world validation would require historical claims data from a Cambodian insurer 
  (not available for this thesis)
- Real failure modes may differ from our hypothetical scenarios

Future work: Validate the framework on production insurance data.

5.3.3 Scope Limitations

**What this thesis does NOT address:**
- Model performance drift (accuracy, AUC)—only distribution drift
- Sampling bias or measurement error in underwriting process
- Adversarial data or fraud that intentionally exploits the system
- Integration with claims outcomes (we don't predict future loss ratios)
- Deployment logistics (how to implement in production systems)

These are important but beyond the scope of stress-testing the drift detection framework.


5.4 Practical Implications and Recommendations

5.4.1 For Insurers Operating in Emerging Markets

**Recommendation 1: Don't rely on PSI alone**
Adopt the multi-metric monitoring framework:
- Primary metric: PSI on mortality_ratio (as today)
- Secondary 1: Feature co-occurrence PSI (detect label drift)
- Secondary 2: Marginal age distribution PSI (detect cohort shifts)
- Secondary 3: HITL escalation rate monitoring (detect tier boundary shifts)

Implementation effort: Low. All metrics can be computed from existing data.

Cost: Minimal. Adds ~10-20 lines of code to monitoring pipeline.

Benefits: Catches 3 failure modes that PSI alone misses; enables early detection of silent 
model degradation.

**Recommendation 2: Alert on any metric, not just PSI**
Decision rule: If ANY metric triggers RED or AMBER, escalate to management.
- Benefit: Prevents "alert fatigue" from overly sensitive metrics while ensuring failures 
  aren't missed
- Downside: Correlation between metrics may cause simultaneous alerts; requires investigation 
  to distinguish false alarms

**Recommendation 3: Set metric-specific alert thresholds**
Based on our findings:
- PSI: GREEN <0.10, AMBER 0.10-0.25, RED ≥0.25 (existing)
- Feature Co-occurrence PSI: AMBER >0.15, RED >0.30 (new)
- Age Distribution PSI: AMBER >0.10, RED >0.20 (new)
- HITL Escalation Rate: AMBER >20% change from baseline, RED >35% (new)

These thresholds are empirically validated in this thesis but should be adjusted based on 
your specific risk tolerance and market conditions.

5.4.2 For Regulators and Supervisors

**Implication**: Single-metric monitoring is inadequate for emerging market AI underwriting. 
Regulators should require insurers to demonstrate multi-metric monitoring frameworks and 
provide regular drift detection reports.

Suggested regulatory requirement: "Insurers must monitor population drift using at least 4 
complementary metrics, including PSI and at least 2 secondary metrics. Monthly reports 
documenting drift alerts and management responses are required."

5.4.3 For Researchers

**Future research directions**:
1. Real-world validation on production claims data
2. Expansion to other emerging markets (India, Nigeria, Southeast Asia)
3. Time-series drift detection (current work is snapshot-based)
4. Integration with performance monitoring (does drift → performance drop?)


5.5 Optional: LangGraph Intelligent Routing Implementation

If resources permit, the multi-metric monitoring framework can be operationalized using 
intelligent routing (LangGraph Phase 1):

Instead of hard-coded decision logic:
```
if risk_level == "HIGH":
    route to HITL
```

Use Claude reasoning:
```
context = {
  applicant_profile: {...},
  risk_level: "HIGH",
  psi_alert: "GREEN",
  age_psi_alert: "RED",  # New!
  hitl_escalation_rate: 28%  # New!
}

claude_decision = ask_claude(
  "Given this context, should we STP, HITL, or ESCALATE?"
)
# Claude can say: "High risk + RED age PSI suggests cohort shift. 
# Recommend HITL to verify applicant profile is genuine."
```

Benefit: More nuanced, context-aware decisions. Elevates thesis from "identifies problem" to 
"solves problem."

See `LANGGRAPH_IMPLEMENTATION_EXAMPLE.py` for code sketch (Phase 1, 2-3 weeks implementation).


6. CONCLUSION

6.1 Summary of Findings

This thesis presents the first empirical validation of PSI drift detection in emerging market 
insurance underwriting. Through controlled stress-testing on synthetic Cambodian applicant data, 
we demonstrate:

1. **PSI's strength**: Correctly detects large population shifts (>25% distortion)
2. **PSI's weakness**: Misses three realistic failure modes (label drift, feature-PSI 
   decoupling, bin edge camouflage)
3. **Proposed solution**: Multi-metric monitoring framework combining PSI + 3 secondary metrics
4. **Validation**: All three failure modes are correctly detected by secondary metrics

6.2 Broader Significance

This work addresses a critical gap in AI underwriting for emerging markets. As insurers in 
Cambodia, India, and other developing economies increasingly adopt AI-driven underwriting, 
robust drift monitoring is essential. Single-metric monitoring is not sufficient given the 
rapid population changes characteristic of emerging markets.

The multi-metric framework proposed in this thesis is practical, lightweight, and immediately 
deployable. It requires no major system overhaul and integrates seamlessly with existing PSI 
monitoring infrastructure.

6.3 Vision: Safe AI Underwriting in Emerging Markets

Emerging markets represent the frontier of insurance expansion. Hundreds of millions of people 
in Cambodia, India, Nigeria, and beyond lack access to affordable, reliable life insurance. 
AI-driven underwriting offers the promise of faster decisions, lower costs, and increased 
access. But AI systems are only as good as their training data and monitoring frameworks. 
Without robust drift detection, AI can silently fail, leading to poor decisions that undermine 
consumer trust.

This thesis contributes to safe, trustworthy AI adoption in emerging markets by:
- Validating what works (PSI for large shifts)
- Exposing what doesn't (PSI for medium shifts)
- Proposing practical solutions (multi-metric monitoring)
- Providing a reusable stress-testing harness for other researchers and practitioners

6.4 Final Remarks

The journey from problem identification to validated solution takes rigor, creativity, and 
persistence. This thesis demonstrates that emerging market challenges are not unsolvable—they 
require context-specific approaches that respect local realities while leveraging global 
best practices.

To practitioners deploying AI underwriting systems: Monitor carefully. Use multiple metrics. 
Trust data, not assumptions. And remember: the cost of missing drift is measured in 
customer trust, regulatory compliance, and business sustainability.

To researchers: Emerging markets are not testing grounds; they are laboratories for 
understanding how AI behaves under real-world constraints. The insights from this work 
will inform safer AI systems globally.

---

## Discussion Writing Guidelines

### Structure
1. **Interpretation first**: What do your results mean?
2. **Comparison to literature**: How do you fit into the existing conversation?
3. **Limitations**: Be honest about constraints; show critical thinking
4. **Practical implications**: What should people do with this knowledge?
5. **Future work**: What's next? Leave doors open

### Tone
- Reflective and analytical
- Confident but not overconfident
- Acknowledging limitations without being defensive
- Forward-looking without making unsupported claims

### What to Discuss
- ✓ Interpret your findings in context of research questions
- ✓ Compare to prior work (agree/disagree)
- ✓ Discuss why your results matter
- ✓ Explain limitations candidly
- ✓ Propose practical implications

### What NOT to Include
- ❌ New results or data (all results go in Chapter 4)
- ❌ Lengthy literature reviews (summarize, don't repeat)
- ❌ Speculation beyond your data ("likely", "probably")
- ❌ Overgeneralization ("this applies to all AI systems")

---

## Discussion Checklist

- [ ] Findings are interpreted in context of research questions
- [ ] Results compared to literature (at least 3-5 prior works cited)
- [ ] Limitations are discussed honestly and in detail
- [ ] Practical implications are clear and actionable
- [ ] Future work section suggests 2-3 concrete next steps
- [ ] Conclusion ties it all together and restates significance
- [ ] Tone is confident, balanced, and appropriately humble
- [ ] No new results introduced (all results in Chapter 4)
- [ ] Page length: 4-8 pages
- [ ] All citations properly formatted

---

## After Completing Chapter 5

1. **Write Conclusion (if separate)**: 1-2 pages summarizing the entire thesis
2. **Proofread entire thesis**: Check formatting, numbering, citations
3. **Create final table of contents, list of figures, list of tables**
4. **Compile and submit PDF**

---

**Your Thesis is Complete! 🎓**

Total expected length: 40-60 pages (excluding appendices)
- Front matter: 10 pages (cover, acknowledgement, abstract, TOC, etc.)
- Chapter 1: 4 pages
- Chapter 2: 5 pages (literature review, optional)
- Chapter 3: 6 pages
- Chapter 4: 8 pages
- Chapter 5: 7 pages
- Appendices/References: 5-10 pages

Good luck with your defense!
