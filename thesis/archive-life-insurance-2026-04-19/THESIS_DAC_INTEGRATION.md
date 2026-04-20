# Thesis & DAC HealthPrice Platform Integration Guide

## Overview

Your thesis ("Stress-Testing AI Underwriting in Emerging Markets") directly feeds into the **DAC HealthPrice Platform**. This document explains how both projects work together and where your thesis research becomes production code.

---

## Thesis Core Contribution

### What the Thesis Proves
1. **PSI Alone is Insufficient** for emerging markets (synthetic validation on Cambodian demographics)
2. **Three Failure Modes Exist** where PSI gives false negatives
3. **Multi-Metric Monitoring Solves** all three failure modes
4. **Production-Ready Framework** with measurable thresholds

### Three Experiments
| Experiment | Status | Deliverable |
|-----------|--------|-------------|
| EXP-001: Baseline Validation | ✅ Done | PSI = 0.000000 (reproducible) |
| EXP-002: PSI Responsiveness | ✅ Done | PSI monotonicity curve |
| EXP-003: Failure Modes | Ready to run | Identifies 3 blind spots |

---

## DAC HealthPrice Platform Integration

### Where the Thesis Applies

**Medical Reader (Intake)**
- Extracts applicant health data from PDFs
- Current: Single-metric monitoring (PSI on mortality_ratio)
- **Thesis input**: Add secondary metrics (feature co-occurrence, age PSI, HITL rate)

**Underwriting Engine**
- Makes DECLINE / STP / HITL decisions
- Current: Static GLM model
- **Thesis input**: Add drift detection guards; escalate if ANY metric triggers

**Pricing Calculator**
- Calculates premium based on risk tier
- Current: Risk multiplier + assumption versioning
- **Thesis input**: Monitor assumption stability (assumption_version changes trigger recalibration)

**Monitoring Dashboard**
- Real-time health check
- Current: Basic PSI chart
- **Thesis input**: Replace with 4-metric dashboard (PSI + 3 secondary + HITL queue depth)

---

## Workflow: Thesis → Platform → Production

### Phase 1: Thesis Validation (Weeks 1-2)
```
Write Chapters 1-4 + Run EXP-003
↓
Results validate multi-metric framework
↓
Five draft chapters completed
```

### Phase 2: Implementation (Weeks 3-6)
```
Integrate 4 metrics into medical_reader/nodes/
↓
  ├─ Primary: PSI on mortality_ratio
  ├─ Secondary 1: Feature co-occurrence PSI
  ├─ Secondary 2: Marginal age PSI
  └─ Secondary 3: HITL escalation rate
↓
Deploy on DAC HealthPrice staging
↓
Test on synthetic stress scenarios (from thesis)
```

### Phase 3: Optional LangGraph (Weeks 4-8)
```
Implement intelligent routing agent
↓
Route decisions based on multi-metric signals
↓
Provide detailed reasoning for ESCALATE cases
↓
Chapter 6: "Intelligent Routing Implementation"
```

### Phase 4: Production (Post-defense)
```
Deploy multi-metric monitoring to live DAC HealthPrice
↓
Underwriters monitor 4-metric dashboard
↓
Alerts trigger when ANY metric crosses RED
↓
Audit trail for regulators (compliance)
```

---

## File Structure: Thesis Folder

```
thesis/
├── presentation.html              ← Your slides (open in browser)
├── THESIS_DAC_INTEGRATION.md      ← This file
├── chapters/                      ← Chapter drafts (you'll create these)
│   ├── 01-introduction.md
│   ├── 02-background.md
│   ├── 03-methodology.md
│   ├── 04-results.md
│   ├── 05-discussion.md
│   └── 06-langgraph-implementation.md (optional)
├── experiments/                   ← Experiment results & figures
│   ├── exp-001-baseline.json
│   ├── exp-002-responsiveness.csv
│   ├── exp-003-failure-modes.json
│   ├── figures/
│   │   ├── psi-baseline.png
│   │   ├── psi-curve.png
│   │   └── failure-modes.png
└── presentations/                 ← Versions of this presentation
    └── v1-defense.html
```

---

## Connection Points: Where Thesis Connects to Platform Code

### 1. Monitoring Module
```python
# Current: medical_reader/analytics/monitor.py
psi_score = calculate_psi(reference, actual)

# After Thesis: Add secondary metrics
psi_score = calculate_psi(reference, actual)
feature_psi = calculate_feature_co_occurrence_psi(reference, actual)
age_psi = calculate_marginal_age_psi(reference, actual)
hitl_rate = escalation_count / total_applicants

alert = any([
    psi_score >= 0.25,
    feature_psi >= 0.10,
    age_psi >= 0.10,
    hitl_rate >= 0.15
])
```

### 2. Decision Node
```python
# Current: medical_reader/nodes/decision.py
decision = route_decision(glm_score, mortality_ratio)

# After Thesis: Add drift checks
if monitoring.alert:
    decision = "ESCALATE"  # Override to human review
    reason = "Multi-metric drift detected"
else:
    decision = route_decision(glm_score, mortality_ratio)
```

### 3. Dashboard
```html
<!-- Current: React frontend shows PSI only -->
<MetricCard title="PSI" value={0.08} status="green" />

<!-- After Thesis: Show all 4 metrics -->
<MetricCard title="PSI" value={0.08} status="green" />
<MetricCard title="Feature Co-occurrence PSI" value={0.12} status="amber" />
<MetricCard title="Age Distribution PSI" value={0.04} status="green" />
<MetricCard title="HITL Escalation Rate" value={0.14} status="amber" />
```

---

## Timeline: Thesis + Platform Parallel Work

### Week 1 (Apr 21-27)
- **Thesis**: Chapters 1-2 draft, Run EXP-003
- **Platform**: No changes (thesis validation first)

### Week 2 (Apr 28-May 4)
- **Thesis**: Chapter 3-4 draft (methodology + results)
- **Platform**: Begin implementing 4-metric monitoring

### Week 3 (May 5-11)
- **Thesis**: Chapter 5 draft (discussion)
- **Platform**: Integration testing on staging

### Week 4 (May 12-18)
- **Thesis**: Finalize chapters 1-5
- **Platform**: LangGraph Phase 1-2 (optional)

### Week 5-6 (May 19-Jun 1)
- **Thesis**: Final revisions + practice defense
- **Platform**: LangGraph Phases 3-5 + full end-to-end testing

### Week 7-8 (Jun 2-15)
- **Thesis**: DEFENSE! 🎓
- **Platform**: Prepare production deployment

---

## Success Criteria: How to Know It's Working

### Thesis Success
- ✅ 5 chapters written (intro, methods, results, discussion + conclusion)
- ✅ All 3 experiments executed and documented
- ✅ Defense presentation clear and compelling
- ✅ Committee questions answered confidently

### Platform Integration Success
- ✅ 4 metrics deployed and reporting
- ✅ Alerts firing correctly on synthetic drift scenarios
- ✅ Underwriter dashboard shows all metrics
- ✅ Zero false positives on clean data
- ✅ All 3 failure modes detected on adversarial data

### End-to-End Success
- ✅ Thesis advances thesis graduation
- ✅ Platform improves DAC HealthPrice safety and compliance
- ✅ Cambodia underwriting becomes production-ready

---

## Next Steps

1. **Open presentation.html** in your browser (use arrow keys or click buttons to navigate)
2. **Start writing Chapter 1** (Introduction & Background) — use templates from wiki
3. **Run EXP-003** to identify failure modes
4. **Track progress** in this thesis folder; update THESIS_DAC_INTEGRATION.md as you implement

---

## References

**Thesis Documentation**
- Master plan: `wiki/topics/thesis-defense-stress-testing-framework.md`
- Formatting guide: `wiki/sources/thesis-formatting-guide.md`
- Chapter templates: `wiki/sources/thesis-*.md`

**Platform Code**
- Monitoring: `medical_reader/analytics/monitor.py`
- Decision node: `medical_reader/nodes/decision.py`
- Dashboard: `portfolio/` (React frontend)
- Assumptions: `medical_reader/pricing/assumptions.py`

**Experiments**
- Stress testing harness: `stress_testing/`
- Synthetic data generator: `medical_reader/generate_test_pdfs.py`
- Test workflow: `medical_reader/test_workflow.py`

---

**Last Updated**: 2026-04-17  
**Thesis Defense Target**: ~2026-06-26  
**Platform Integration Target**: Post-defense  
