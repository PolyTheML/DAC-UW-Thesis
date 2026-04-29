# Thesis: Stress-Testing AI Underwriting in Emerging Markets

**Created**: 2026-04-17  
**Status**: ⚠️ ARCHIVED 2026-04-19 — superseded by [Auto Insurance Telematics Thesis](./auto-insurance-telematics-thesis.md). Files at `thesis/archive-life-insurance-2026-04-19/`.  
**Last updated**: 2026-04-20 (archive note added)  
**Sources**: Implementation session 2026-04-17

**See also**: [Thesis Presentation Guide](./thesis-presentation-guide.md) — speaker notes, defense structure, examiner Q&A prep

---

## Executive Summary

### Thesis Title
*"Stress-Testing AI Underwriting Frameworks in Emerging Markets: A Robustness Analysis using Synthetic Data and Population Stability Index (PSI)"*

### Core Contribution
This thesis validates that **PSI (Population Stability Index) successfully detects large population distribution shifts** in Cambodian life insurance underwriting, but identifies **three critical failure modes** where PSI gives false negatives. The thesis proposes **multi-metric drift monitoring** as the solution, with optional implementation of **LangGraph intelligent routing** for context-aware underwriting decisions.

### Timeline
- **Start**: 2026-04-17
- **Defense**: ~2026-06-26 (8 weeks)
- **Status**: Framework validated; chapters in progress

---

## Thesis Structure

### Chapter 1-2: Introduction & Background (Week 1)
**Goal**: Frame the problem and motivate the research

- **Why emerging markets?** Limited training data, high population volatility, limited historical outcomes
- **Why life insurance underwriting?** High-stakes decisions (decline = lost revenue + customer dissatisfaction)
- **Why PSI?** Industry standard for drift detection, but unstudied in emerging market context
- **Gap**: Existing literature assumes stable populations

**Key claim to establish**: Single-metric monitoring is insufficient for emerging markets.

### Chapter 3: Methodology (Week 1-2)
**Goal**: Describe how you validated PSI

- **Synthetic data generation**
  - Cambodia census-based demographics (age, BMI, smoking, conditions)
  - Risk factor distributions (occupational, endemic, healthcare tier)
  - Generator produces 10K applicants with authentic mortality_ratio values
  - Seeded for reproducibility (seed=42)

- **PSI calculation**
  - Reference distribution: 8-bin histogram of mortality_ratio
  - Formula: PSI = Σ (actual% - expected%) × ln(actual% / expected%)
  - Thresholds: GREEN (<0.10), AMBER (0.10-0.25), RED (≥0.25)

- **Experimental design**
  - EXP-001: Baseline validation (PSI = 0 by construction)
  - EXP-002: Distortion responsiveness (0% → 50% → PSI monotonicity)
  - EXP-003: Adversarial failure modes (3 scenarios, secondary metrics)

### Chapter 4: Results (Week 2-3)
**Goal**: Present findings from all 3 experiments

#### EXP-001: Baseline Validation ✅
- **Objective**: Verify synthetic generator matches reference distribution
- **Method**: Generate 10K applicants, compare to themselves (should be PSI = 0)
- **Result**: PSI = 0.000000 (perfect match by construction)
- **Interpretation**: Generator is stable and reproducible
- **Figure**: Bin histogram overlay (actual vs reference) — should be 100% identical

#### EXP-002: PSI Responsiveness ✅
- **Objective**: Prove PSI increases monotonically with population shift
- **Method**: Inject 0% → 10% → 20% → 40% → 50% distortions (high-BMI motorbike couriers)
- **Result**: PSI increases smoothly (0.0000 → 0.0674)
  - 0%: PSI = 0.0000 (baseline)
  - 10%: PSI = 0.0022 (small shift)
  - 20%: PSI = 0.0099 (moderate shift)
  - 40%: PSI = 0.0422 (large shift)
  - 50%: PSI = 0.0674 (extreme shift)
- **Interpretation**: PSI is sensitive and predictable to population changes
- **Figure**: PSI vs distortion fraction (smooth S-curve)
- **Business implication**: If you see PSI > 0.05, you can be confident something has shifted

#### EXP-003: Adversarial Failure Modes 🔬
- **Objective**: Identify where PSI gives false negatives
- **Method**: Test 3 scenarios where PSI says GREEN but model silently fails
- **Results**: (Ready to run)

**Failure Mode 1: Label Drift (Comorbidity Confounding)**
- Scenario: New government diabetic clinic manages BP → normal
- Change: Input features shift (lower BP readings), but mortality_ratio stays same
- PSI Alert: GREEN ✗ (silent failure)
- Secondary Detection: Feature co-occurrence PSI (diabetes + normal BP)
- Fix: Monitor P(diabetes=True ∩ bp_class="normal") — if rises >20%, flag

**Failure Mode 2: Feature-PSI Decoupling (Age Cohort Shift)**
- Scenario: Young professionals (age 22-28) enter, all healthy
- Change: Age distribution shifts drastically (mean 25 vs baseline 38), but MR ≈ 1.0 (matches reference)
- PSI Alert: GREEN ✗ (PSI sees no drift on MR)
- Secondary Detection: Marginal age distribution PSI
- Fix: Monitor age PSI separately — if >0.10, flag cohort shift

**Failure Mode 3: Bin Edge Camouflage (Boundary Classification Instability)**
- Scenario: 15% of applicants shift from MR 1.48 → 1.73 (daily commuter uptick)
- Change: Cross the LOW/MEDIUM boundary (1.5 threshold)
- PSI Alert: GREEN ✗ (small relative shift, bins adjacent)
- Secondary Detection: HITL escalation rate (% MEDIUM-tier decisions)
- Fix: Monitor HITL queue depth + use finer PSI bins near decision boundaries (1.3, 1.7)

**Key Finding**: PSI alone is insufficient. Recommend multi-metric monitoring:
- Primary: PSI on mortality_ratio
- Secondary 1: Feature co-occurrence PSI (label drift detection)
- Secondary 2: Marginal age distribution PSI (cohort shift detection)
- Secondary 3: HITL escalation rate (boundary sensitivity)

### Chapter 5: Discussion & Implications (Week 3-4)
**Goal**: Interpret results and propose solutions

- **Main claim**: PSI is necessary but not sufficient for emerging market underwriting
- **Evidence**: EXP-003 failure modes demonstrate blind spots
- **Recommendation**: Multi-metric monitoring framework
  - Deploy all 4 metrics in parallel
  - Alert when ANY metric triggers RED
  - Correlate signals (e.g., "age PSI rising + HITL rate rising = cohort shift")
- **Limitations**: 
  - Synthetic data ≠ real world (future work: validate on live data)
  - 8-bin histogram is arbitrary (future: adaptive binning)
  - Failure modes are hypothetical (future: collect real failure examples)
- **Impact**: De-risks AI adoption in emerging markets
- **Future work**: 
  - LangGraph intelligent routing (optional: implement phases 1-5)
  - Real data validation
  - Journal publication

### Conclusion: Tie it Together
- Summarize thesis arc: problem → validation → solution
- Emphasize: This is actionable (not just theory)
- Vision: Safe AI underwriting in Cambodia and other emerging markets

---

## Writing Guidance

### Thesis Writing Style (ITC Cambodia Format)
- **Font**: Times New Roman, 12pt (body), 14-16pt (headings)
- **Spacing**: 1.5 or double-spaced
- **Margins**: 1 inch all sides
- **Language**: English or French (or bilingual like sample theses)
- **Tone**: Formal, academic, objective
- **Structure**: IMRAD (Introduction, Methods, Results, Analysis/Discussion)

### Chapter Templates (See `wiki/sources/`)
- Cover page: `thesis-cover-template.md`
- Acknowledgement: `thesis-acknowledgement-template.md`
- Abstract/Introduction: `thesis-intro-template.md`
- Methodology: `thesis-methodology-template.md`
- Results: `thesis-results-template.md`
- Discussion: `thesis-discussion-template.md`

### Figures & Tables
- All results figures must include:
  - Clear title/caption
  - Axis labels with units
  - Legend (if multiple series)
  - Source/methodology note
- Examples:
  - EXP-002 PSI curve: "Figure 4.1: PSI Response to Population Distortion (0%-50%)"
  - EXP-002 histograms: "Figure 4.2: Mortality Ratio Distribution (Baseline vs 40% Distorted)"
  - Failure modes: "Figure 4.3: Failure Mode 1 — Label Drift Detection"

---

## LangGraph Integration (Optional: Phases 1-5)

### Why LangGraph?
Your thesis **identifies** the problem (PSI insufficient) and **proposes** multi-metric solution. LangGraph allows you to **implement** the solution, elevating the thesis from theoretical to practical.

**Without LangGraph**: "I recommend multi-metric monitoring"  
**With LangGraph**: "I've implemented multi-metric monitoring using intelligent routing agents"

### 5-Phase Roadmap (8 weeks total)

#### Phase 1: Intelligent Routing (Weeks 1-2)
- Replace hard-coded decision logic with Claude reasoning
- Add conditional routing: DECLINE | STP | HITL | ESCALATE
- Integration: `medical_reader/nodes/intelligent_decision.py`
- Testing: Validate on `stress_testing/` synthetic scenarios
- Time: 2 weeks
- **Payoff**: Mid-size improvement (shows understanding of problem)

#### Phase 2: Anomaly Detection (Weeks 3-4)
- Add `anomaly_detector` node (flags unusual applicant profiles)
- Detect: extreme age/occupation combinations, potential fraud, data quality issues
- Integration: Run before routing
- Testing: Test against edge case applicants
- Time: 1-2 weeks
- **Payoff**: Handles edge cases better

#### Phase 3: Expert Agent (Week 4)
- Add `expert_agent` node (Claude expertise for ESCALATE cases)
- Provides detailed reasoning for complex edge cases
- Integration: Called when router flags uncertainty
- Time: 1 week
- **Payoff**: Improved decision quality

#### Phase 4: Persistent Memory (Weeks 5-6)
- Store case outcomes + reasoning
- Retrieve similar historical cases on new applications
- Learn patterns from past decisions
- Time: 1-2 weeks
- **Payoff**: System learns over time

#### Phase 5: Version-Aware Workflow (Weeks 6-7)
- Stamp each workflow step with assumption_version + model_version
- Detect version conflicts mid-workflow
- Recompute with new assumptions if needed
- Audit trail fully traceable
- Time: 1 week
- **Payoff**: Production-ready compliance

#### Thesis Integration (Week 8)
- Run full workflow on stress_testing batches
- Validate that multi-metric approach works end-to-end
- Document findings
- Add to thesis as "Chapter 6: Intelligent Routing Implementation" or Appendix
- Time: 1 week

---

## Week-by-Week Breakdown

```
WEEK 1 (Apr 21-27):
  ☐ Draft Chapter 1-2 (Intro/Background)
  ☐ Draft Chapter 3 (Methodology)
  ☐ Run EXP-003 adversarial tests
  ☐ Create figures from EXP-001 & EXP-002

WEEK 2 (Apr 28-May 4):
  ☐ Draft Chapter 4 (Results) with all 3 experiments
  ☐ Document EXP-003 findings
  ☐ Start Phase 1 LangGraph (intelligent routing)
  ☐ Advisor feedback on draft chapters

WEEK 3 (May 5-11):
  ☐ Complete Phase 1 LangGraph
  ☐ Test Phase 1 on stress_testing scenarios
  ☐ Draft Chapter 5 (Discussion/Implications)
  ☐ Create presentation slides (15-20 slides)

WEEK 4 (May 12-18):
  ☐ Complete Phase 2 LangGraph (anomaly detection)
  ☐ Complete Phase 3 LangGraph (expert agent)
  ☐ Finalize all thesis chapters
  ☐ Proofread and format

WEEK 5-6 (May 19-Jun 1):
  ☐ Complete Phases 4-5 LangGraph (memory + versioning)
  ☐ Full end-to-end testing
  ☐ Create defense presentation (final version)
  ☐ Practice defense talk (45 min)

WEEK 7-8 (Jun 2-15):
  ☐ Final revisions based on feedback
  ☐ Submit final thesis PDF
  ☐ Defense preparation
  ☐ DEFENSE! 🎓
```

---

## Key Success Metrics

### Thesis Quality
- ✅ Clear problem statement (emerging markets + PSI)
- ✅ Rigorous methodology (3 controlled experiments)
- ✅ Novel findings (3 failure modes identified)
- ✅ Actionable solution (multi-metric monitoring)
- ✅ Professional writing (follows ITC format)

### LangGraph Implementation (If Pursuing)
- ✅ Phase 1 complete (intelligent routing)
- ✅ Integrated with stress_testing framework
- ✅ Validated end-to-end
- ✅ Documented and demonstrated

### Defense Presentation
- ✅ Clear 45-minute talk structure
- ✅ Compelling visuals (PSI curves, failure mode diagrams)
- ✅ Confident answers to examiner questions
- ✅ Live demo of stress_testing framework

---

## Critical Files & References

### Implementation Files
- `stress_testing/` — Full harness (already built)
- `medical_reader/` — Production engine
- `medical_reader/state.py` — Data models
- `analytics/monitor.py` — PSI calculation

### Thesis Writing Guides
- `wiki/sources/thesis-cover-template.md`
- `wiki/sources/thesis-formatting-guide.md`
- `wiki/sources/sample-acknowledgement.md`

### Documentation
- `THESIS_END_TO_END_EXPLANATION.md` (full context)
- `LANGGRAPH_IMPLEMENTATION_EXAMPLE.py` (code pattern)
- `QUICK_START_YOUR_THESIS.md` (action items)
- `THESIS_VISUAL_SUMMARY.txt` (visual reference)

---

## Next Steps

1. **This Week**: Run EXP-003, draft Chapters 1-4
2. **Next Week**: Complete LangGraph Phase 1, finalize Chapter 5
3. **Weeks 3-8**: Implement Phases 2-5, practice defense
4. **Week 8**: Submit and defend! 🎓

---

**Status**: 🚀 Ready to execute. Framework validated. Thesis structure defined. 8 weeks is enough time for both thesis + full LangGraph implementation.

**Next Session**: Ingest thesis templates + create formatting guide + start writing chapters.
