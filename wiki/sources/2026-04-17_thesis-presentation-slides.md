# Thesis Defense: Presentation Slides (HTML)

**Created**: 2026-04-17  
**Source**: `thesis/presentation.html`  
**Status**: ✅ Complete — 10 interactive slides with speaker notes

---

## Overview

Comprehensive interactive HTML presentation for thesis defense, covering the core thesis topic and connection to DAC HealthPrice platform. Designed for 45-minute defense talk.

**URL**: Open `C:\DAC-UW-Agent\thesis\presentation.html` in any web browser

---

## Slides (10 Total)

### Slide 1: Title Slide
- **Title**: Stress-Testing AI Underwriting in Emerging Markets
- **Subtitle**: A Robustness Analysis using Synthetic Data and Population Stability Index (PSI)
- **Context**: ITC Cambodia Thesis Defense 2026
- **Badge**: 🏥 DAC HealthPrice Platform — Real-World Application

### Slide 2: The Problem — Why Emerging Markets?
- Limited training data
- High population volatility
- Unreliable health records
- Rapid demographic shifts

**Why Life Insurance?**
- High-stakes decisions
- Decline = lost revenue
- No recourse for errors
- Compliance critical

**Gap**: Existing drift detection (PSI) assumes stable populations. What when populations shift rapidly?

### Slide 3: Population Stability Index (PSI)
- **Formula**: PSI = Σ (actual% - expected%) × ln(actual% / expected%)
- **Interpretation**:
  - 🟢 GREEN: PSI < 0.10 (stable)
  - 🟡 AMBER: PSI 0.10–0.25 (warning)
  - 🔴 RED: PSI ≥ 0.25 (critical drift)

**Question**: Is PSI alone enough for Cambodian life insurance?

### Slide 4: Three Controlled Experiments
1. **EXP-001: Baseline Validation** ✅
   - Verify synthetic generator matches reference
   - Result: PSI = 0.000000

2. **EXP-002: Responsiveness** ✅
   - Prove PSI increases monotonically (0% → 50%)
   - Result: PSI 0.0000 → 0.0674

3. **EXP-003: Adversarial Failure Modes** 🔬
   - Identify where PSI gives false negatives

### Slide 5: Three Critical Failure Modes
Where PSI says "GREEN" but model silently fails:

1. **Failure Mode 1: Label Drift (Comorbidity Confounding)**
   - New clinic → normal BP, but mortality unchanged
   - Fix: Monitor feature co-occurrence PSI

2. **Failure Mode 2: Feature-PSI Decoupling (Age Cohort Shift)**
   - Young professionals enter (age 22–28)
   - PSI sees no drift on mortality
   - Fix: Monitor marginal age distribution PSI

3. **Failure Mode 3: Bin Edge Camouflage (Boundary Classification)**
   - 15% shift from 1.48 → 1.73 (crosses decision boundary)
   - PSI = GREEN (small relative shift)
   - Fix: Monitor HITL escalation rate

### Slide 6: Multi-Metric Monitoring Solution
**PSI is necessary but NOT sufficient.**

Deploy 4 metrics in parallel:
1. **Primary**: PSI on mortality_ratio
2. **Secondary 1**: Feature co-occurrence PSI (label drift detection)
3. **Secondary 2**: Marginal age distribution PSI (cohort shift detection)
4. **Secondary 3**: HITL escalation rate (boundary sensitivity detection)

**Alert Policy**: Trigger RED when ANY metric crosses threshold

### Slide 7: Connection to DAC HealthPrice
**Thesis Impact**:
- Validates multi-metric monitoring
- De-risks AI adoption
- Improves decision quality
- Production-ready compliance

**Platform Integration**:
- Deploy 4 metrics on live data
- Real-time drift monitoring
- Automated alerts to underwriters
- Audit trail for regulators

**Path**: Thesis → Implementation → Production Deployment

### Slide 8: Optional LangGraph Intelligent Routing
Elevate from "multi-metric monitoring" to "intelligent underwriting agent":

- **Phase 1**: Intelligent Routing (2 weeks)
- **Phase 2**: Anomaly Detection (1-2 weeks)
- **Phase 3**: Expert Agent (1 week)
- **Phase 4**: Persistent Memory (1-2 weeks)
- **Phase 5**: Version-Aware Workflow (1 week)

**Payoff**: Thesis demonstrates end-to-end solution, not just theory

### Slide 9: 8-Week Timeline to Defense
- **Week 1**: Draft Chapters 1–3, Run EXP-003
- **Week 2**: Complete EXP-003, Draft Chapter 4
- **Week 3**: Draft Chapter 5, Start LangGraph Phase 1
- **Week 4**: Complete LangGraph Phases 1–3, Finalize chapters
- **Week 5–6**: Complete LangGraph Phases 4–5, Full testing
- **Week 7–8**: Final revisions, practice defense, DEFEND! 🎓

### Slide 10: Key Takeaways
✅ **Problem**: Emerging markets face rapid population shifts; single-metric monitoring fails

✅ **Solution**: Multi-metric framework detects all 3 failure modes; production-ready

✅ **Impact**: De-risks AI in insurance; enables safe underwriting in Cambodia + beyond

**Questions?**

---

## Design Features

- **Responsive**: Works on desktop, tablet, mobile
- **Keyboard Navigation**: Arrow keys to navigate slides
- **Navigation Dots**: Click any dot to jump to that slide
- **Smooth Transitions**: CSS animations between slides
- **Gradient Backgrounds**: Each slide has distinct color scheme for visual interest
- **Professional Typography**: Segoe UI font, clear hierarchy

---

## How to Use

1. **Open in Browser**: Double-click `thesis/presentation.html` or drag into browser
2. **Full Screen**: Press F11 or browser's full-screen button
3. **Navigate**: 
   - Arrow keys (left/right)
   - Click Previous/Next buttons
   - Click navigation dots
4. **Present**: Open on projector; speaker can use browser's developer tools for speaker notes (F12)

---

## Technical Details

- **File Size**: ~35 KB (single HTML file, no dependencies)
- **Dependencies**: None (pure HTML + CSS + JavaScript)
- **Browser Compatibility**: Chrome, Firefox, Safari, Edge (all modern versions)
- **Offline**: Works completely offline; no CDN required

---

## Integration with Wiki

This presentation accompanies:
- [Thesis Master Plan](../topics/thesis-defense-stress-testing-framework.md)
- [Thesis-DAC Integration Guide](./2026-04-17_thesis-dac-integration.md)
- [Thesis Formatting Guide](./thesis-formatting-guide.md)
- [Chapter Templates](./thesis-introduction-template.md) (and others)

---

## Next Steps

1. **Review**: Open presentation.html in browser; navigate through slides
2. **Customize**: Edit HTML file to add your name, advisor, defense date
3. **Practice**: Use for rehearsal talks with advisors
4. **Present**: Use for actual defense presentation (target: 45 minutes)

---

**Status**: ✅ Ready to use  
**Last Updated**: 2026-04-17  
**Location**: `C:\DAC-UW-Agent\thesis/presentation.html`
