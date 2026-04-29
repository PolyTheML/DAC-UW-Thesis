# Thesis Defense Presentation Guide

**Created**: 2026-04-17  
**Last Updated**: 2026-04-17  
**Related**: [Master Thesis Plan](./thesis-defense-stress-testing-framework.md) | [DAC Integration](../sources/2026-04-17_thesis-dac-integration.md)

---

## Overview

Interactive 10-slide HTML presentation for your thesis defense. Designed for 45-minute talk covering the core research (PSI failure modes + multi-metric solution) and connection to DAC HealthPrice platform production deployment.

**File**: `C:\DAC-UW-Agent\thesis/presentation.html`  
**Type**: Single HTML file (no dependencies; works offline)  
**Browser**: Any modern browser (Chrome, Firefox, Safari, Edge)

---

## Content Summary

### The Narrative Arc (45 minutes)

**Slide 1-2: The Problem (5 min)**
- Why emerging markets need special consideration
- Why life insurance is high-stakes
- Gap: existing drift detection assumes stable populations

**Slide 3-4: How We Validated (15 min)**
- What PSI is and how it works
- Three controlled experiments (EXP-001, EXP-002, EXP-003)
- Baseline validation (perfect) and responsiveness (smooth curve)

**Slide 5-6: The Finding (15 min)**
- Three failure modes where PSI gives false negatives
  - Label drift (comorbidity confounding)
  - Feature-PSI decoupling (age cohort shift)
  - Bin edge camouflage (boundary instability)
- Multi-metric solution (4 metrics in parallel)

**Slide 7-8: The Impact (7 min)**
- Connection to DAC HealthPrice production platform
- Optional LangGraph intelligent routing (if implemented)
- Practical deployment roadmap

**Slide 9-10: Timeline & Conclusion (3 min)**
- 8-week path to defense
- Key takeaways

---

## How to Navigate

**In Browser**:
- **Arrow keys**: Left/right to move between slides
- **Click buttons**: "Previous" / "Next" buttons below slides
- **Click dots**: Navigation dots jump directly to any slide
- **Full screen**: F11 for presentation mode (remove browser chrome)

**Recommended Setup**:
1. Open in full-screen mode (F11)
2. Use arrow keys during defense
3. Have speaker notes printed separately (see "Speaker Notes" section below)

---

## Speaker Notes (Detailed Talking Points)

### Slide 1: Title Slide (30 sec)
**What to say**: "Good [morning/afternoon]. I'm [Name], and today I'm presenting my thesis: Stress-Testing AI Underwriting Frameworks in Emerging Markets. This work directly connects to DAC HealthPrice, the life insurance platform we've been building for Cambodia."

**Key points to emphasize**:
- Emerging markets are different (volatile populations)
- AI underwriting is expanding rapidly
- But drift detection is understudied in emerging markets

### Slide 2: The Problem (2 min)
**What to say**: "Why is this work important? Two reasons. First, emerging markets like Cambodia have unique challenges: limited training data, volatile populations, and unreliable records. Second, life insurance decisions are high-stakes—you can't undo a decline once sent to a customer."

**Pause for emphasis**: "The gap in literature is simple: everyone assumes stable populations when designing drift detection. But Cambodia's population is shifting rapidly. What happens when existing tools fail?"

### Slide 3: PSI Explained (1 min)
**What to say**: "Population Stability Index, or PSI, is the industry standard for drift detection in banking and insurance. The formula is [point to slide]. Interpretation is simple: GREEN is stable, AMBER is warning, RED is critical drift."

**Key question to pose**: "But here's the question I set out to answer: Is PSI alone enough for emerging markets like Cambodia?"

### Slide 4: Experiments (2 min)
**What to say**: "To answer that question, I designed three controlled experiments. The first, EXP-001, was a sanity check—can our synthetic generator produce data that matches itself? Yes, PSI equals zero by construction. The second, EXP-002, tested responsiveness—if we artificially shift the population, does PSI increase smoothly? Yes, from zero to 0.0674, a nice S-curve."

**Pause**: "But the third experiment, EXP-003, is where things get interesting."

### Slide 5: Failure Modes (3 min)
**What to say**: "EXP-003 tested three scenarios where PSI says 'everything is fine' but the model is silently failing."

**Scenario 1**: "A new government clinic opens and normalizes blood pressure for diabetic patients. Their input features shift—normal BP readings instead of elevated—but their actual mortality risk doesn't change. PSI sees no drift on mortality. It says GREEN. But we've lost a predictive signal."

**Scenario 2**: "Young professionals—age 22 to 28—start applying. They're all healthy, so mortality ratios look fine. But the age distribution has shifted dramatically from our baseline of age 38. PSI on mortality says GREEN. But we're now in a fundamentally different risk pool."

**Scenario 3**: "A spike in motorbike couriers shifts 15% of applicants from a mortality ratio of 1.48 to 1.73. This crosses our decision boundary at 1.5. But the relative shift is small, so PSI says GREEN. Meanwhile, our human underwriters see a surge of HITL escalations."

**Key point**: "In all three cases, PSI says 'no drift,' but the underwriting model is failing in different ways."

### Slide 6: The Solution (2 min)
**What to say**: "So what's the answer? PSI is necessary but not sufficient. We need to monitor four metrics in parallel."

**Walk through each**:
1. "Primary: PSI on mortality_ratio—the standard check"
2. "Secondary 1: Feature co-occurrence PSI—catches when input features and output mortality become decoupled"
3. "Secondary 2: Marginal age distribution PSI—catches when the age pool shifts"
4. "Secondary 3: HITL escalation rate—catches when decision boundaries become unstable"

**Rule**: "Trigger a RED alert when ANY metric crosses its threshold. Correlate signals—if age PSI and HITL rate both rise, that's cohort shift."

### Slide 7: DAC HealthPrice Connection (1.5 min)
**What to say**: "Now, why does this matter beyond academia? Because this thesis directly informs DAC HealthPrice, the production platform Peter and I have been building."

**Thesis impact**:
- "This thesis validates that multi-metric monitoring works on synthetic Cambodia-like data"
- "It de-risks our platform from silent drift failures"
- "It improves decision quality by catching failures earlier"

**Platform impact**:
- "We'll deploy all 4 metrics in real-time on live quote data"
- "Underwriters get automatic alerts if drift is detected"
- "Every decision is audited and traceable for regulators"

**Vision**: "Thesis validates theory. Platform implements it. Cambodia gets safe, AI-assisted underwriting."

### Slide 8: Optional LangGraph (1 min)
**What to say** (if you implement this): "As an optional enhancement, I've also implemented LangGraph intelligent routing. This takes the multi-metric monitoring and uses it to make routing decisions automatically—STP for standard risks, HITL for complex cases, ESCALATE when drift is detected."

**If not implemented**: "This is something we could add as a future enhancement to the platform."

### Slide 9: Timeline (30 sec)
**What to say**: "I'm on an 8-week timeline to defense. Weeks 1-2 focus on drafting chapters and running the full EXP-003. Weeks 2-4 are implementing the findings into the platform. Weeks 5-8 are final revisions and defense prep. We're on track."

### Slide 10: Conclusion (30 sec)
**What to say**: "To summarize: Single-metric drift detection fails in emerging markets. Multi-metric monitoring solves all three failure modes we identified. This enables safe, high-confidence AI underwriting in Cambodia and beyond. Thank you. Questions?"

---

## Anticipated Examiner Questions

### Q1: "Why synthetic data instead of real claims?"
**Answer**: "We don't have real claims yet—DAC's platform is pre-launch. Synthetic data lets us validate the framework now. When claims data arrives, we'll validate on real data and publish a follow-up study."

### Q2: "How do you know your failure modes are realistic?"
**Answer**: "These are based on common patterns in underwriting. Comorbidity confounding (Failure Mode 1) happens when healthcare access changes. Cohort shift (Failure Mode 2) happens with seasonal hiring or demographic campaigns. Boundary sensitivity (Failure Mode 3) is inevitable with any classification system. I can cite specific insurance examples for each."

### Q3: "Why four metrics? Couldn't you use more?"
**Answer**: "Four is a tradeoff between comprehensiveness and operational burden. Each metric has a clear interpretation and actionable fix. Beyond four, you hit diminishing returns and create alert fatigue. But the framework is extensible—you could add a fifth if needed."

### Q4: "How do these metrics perform on real data?"
**Answer**: "That's future work. We're currently in the process of collecting claims data from DAC's live platform. We'll validate these findings and publish results quarterly starting [date]."

### Q5: "What's the business impact?"
**Answer**: "For every 1% we can automate without increasing risk, we save [X] in underwriting costs and improve customer experience. Multi-metric monitoring reduces silent failures, which directly impacts underwriter confidence and adoption of AI systems."

---

## Customization

To personalize the presentation:

1. **Edit the HTML file** with a text editor (Notepad, VS Code, etc.)
2. **Line 64**: Change "ITC Cambodia Thesis Defense 2026" to your defense date
3. **Line 66**: Add your institution/advisor information
4. **Slides 2-10**: Add your name, advisor name, or other details as needed

**Example edit**:
```html
<!-- Before -->
<p style="margin-top: 60px; font-size: 1.2em;">ITC Cambodia Thesis Defense 2026</p>

<!-- After -->
<p style="margin-top: 60px; font-size: 1.2em;">ITC Cambodia Thesis Defense — June 26, 2026</p>
<p style="font-size: 1.1em; opacity: 0.9;">Advisor: Prof. [Name] | Committee: [Names]</p>
```

---

## Best Practices for Defense

1. **Practice once**: Run through all 10 slides out loud before defense day
2. **Time yourself**: Aim for 45 minutes total (including Q&A)
3. **Slides 1-2 (5 min)**: Intro + problem statement
4. **Slides 3-6 (20 min)**: Methodology + results (the core contribution)
5. **Slides 7-8 (7 min)**: Impact + platform connection
6. **Slides 9-10 (3 min)**: Timeline + conclusion
7. **Q&A (10 min)**: Budget time for questions

---

## Technical Troubleshooting

| Issue | Fix |
|-------|-----|
| Slides not displaying | Use modern browser; test in Chrome first |
| Keyboard shortcuts not working | Click in the presentation area first; then use arrow keys |
| Printing | Print to PDF for best results (File → Print → Save as PDF) |
| Fullscreen not working | Press F11 (may vary by browser) |

---

## Integration with Thesis

This presentation serves as the **oral defense** component. It pairs with:
- [Master Thesis Plan](./thesis-defense-stress-testing-framework.md) — your written 5 chapters
- [Chapter Templates](../sources/thesis-introduction-template.md) — guidance for each chapter
- [DAC Integration Guide](../sources/2026-04-17_thesis-dac-integration.md) — how thesis feeds into platform

---

**Status**: ✅ Ready for defense  
**Last Updated**: 2026-04-17  
**Location**: `C:\DAC-UW-Agent\thesis/presentation.html`
