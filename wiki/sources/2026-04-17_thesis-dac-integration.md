# Thesis & DAC HealthPrice Platform Integration

**Created**: 2026-04-17  
**Location**: `thesis/THESIS_DAC_INTEGRATION.md`  
**Status**: ✅ Complete — Detailed roadmap for parallel thesis + platform work

---

## Overview

Your thesis ("Stress-Testing AI Underwriting in Emerging Markets") directly feeds into the **DAC HealthPrice Platform**. This document explains how both projects work together and where thesis research becomes production code.

---

## Thesis Core Contribution

### What the Thesis Proves
1. **PSI Alone is Insufficient** for emerging markets
2. **Three Failure Modes Exist** where PSI gives false negatives
3. **Multi-Metric Monitoring Solves** all three failure modes
4. **Production-Ready Framework** with measurable thresholds

### Three Experiments
| Experiment | Status | Deliverable |
|-----------|--------|-------------|
| EXP-001: Baseline Validation | ✅ Done | PSI = 0.000000 |
| EXP-002: PSI Responsiveness | ✅ Done | PSI monotonicity curve |
| EXP-003: Failure Modes | Ready to run | 3 blind spots identified |

---

## DAC HealthPrice Platform Integration

### Where Thesis Applies

**Medical Reader (Intake)**
- Current: Single-metric monitoring (PSI on mortality_ratio)
- **After Thesis**: Add secondary metrics

**Underwriting Engine**
- Current: Static GLM model
- **After Thesis**: Add drift detection guards

**Pricing Calculator**
- Current: Risk multiplier + assumption versioning
- **After Thesis**: Monitor assumption stability

**Monitoring Dashboard**
- Current: Basic PSI chart
- **After Thesis**: 4-metric dashboard

---

## Workflow: Thesis → Platform → Production

### Phase 1: Thesis Validation (Weeks 1-2)
Write Chapters 1-4 + Run EXP-003 → Results validate multi-metric framework

### Phase 2: Implementation (Weeks 3-6)
Integrate 4 metrics into medical_reader → Test on synthetic scenarios

### Phase 3: Optional LangGraph (Weeks 4-8)
Implement intelligent routing agent → Add to thesis as Chapter 6

### Phase 4: Production (Post-defense)
Deploy multi-metric monitoring to live DAC HealthPrice

---

## File Structure

```
thesis/
├── presentation.html                    ← 10-slide deck
├── THESIS_DAC_INTEGRATION.md           ← This roadmap
├── chapters/                           ← Chapter drafts
│   ├── 01-introduction.md
│   ├── 02-background.md
│   ├── 03-methodology.md
│   ├── 04-results.md
│   ├── 05-discussion.md
│   └── 06-langgraph-implementation.md (optional)
├── experiments/
│   ├── exp-001-baseline.json
│   ├── exp-002-responsiveness.csv
│   ├── exp-003-failure-modes.json
│   └── figures/
└── presentations/
    └── v1-defense.html
```

---

## Connection Points: Code Changes

### 1. Monitoring Module
**File**: `medical_reader/analytics/monitor.py`

Current:
```python
psi_score = calculate_psi(reference, actual)
```

After thesis:
```python
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
**File**: `medical_reader/nodes/decision.py`

Current:
```python
decision = route_decision(glm_score, mortality_ratio)
```

After thesis:
```python
if monitoring.alert:
    decision = "ESCALATE"
    reason = "Multi-metric drift detected"
else:
    decision = route_decision(glm_score, mortality_ratio)
```

### 3. Dashboard
**File**: Frontend (React)

Current: PSI only  
After thesis: All 4 metrics displayed

---

## Timeline: Thesis + Platform Parallel

| Week | Thesis | Platform |
|------|--------|----------|
| 1 (Apr 21-27) | Chapters 1-2, Run EXP-003 | No changes |
| 2 (Apr 28-May 4) | Chapters 3-4 | Begin 4-metric implementation |
| 3 (May 5-11) | Chapter 5 | Integration testing |
| 4 (May 12-18) | Finalize chapters | LangGraph Phase 1-2 |
| 5-6 (May 19-Jun 1) | Final revisions | LangGraph Phases 3-5 |
| 7-8 (Jun 2-15) | DEFENSE | Production deployment |

---

## Success Criteria

**Thesis**:
- ✅ 5 chapters written
- ✅ All 3 experiments executed
- ✅ Defense presentation clear
- ✅ Committee questions answered confidently

**Platform**:
- ✅ 4 metrics deployed
- ✅ Alerts firing correctly
- ✅ Dashboard shows all metrics
- ✅ Zero false positives on clean data
- ✅ All 3 failure modes detected on adversarial data

**End-to-End**:
- ✅ Thesis advances graduation
- ✅ Platform improves DAC HealthPrice safety
- ✅ Cambodia underwriting production-ready

---

**Status**: ✅ Complete  
**Last Updated**: 2026-04-17
