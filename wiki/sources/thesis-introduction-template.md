# Thesis Chapter 1: Introduction Template

**Created**: 2026-04-17  
**Format**: ITC Cambodia standard  
**Chapter**: I (INTRODUCTION)  
**Pages**: Typically 3-5 pages  
**Typical Word Count**: 1,500-2,000 words

---

## Chapter 1 Structure

### Formatting Rules
- **Chapter Header**: "CHAPTER I. INTRODUCTION" (all caps, 16pt bold, centered)
- **Section Headers**: "1.1 [Section Title]" (12pt bold)
- **Subsection Headers**: "1.1.1 [Subsection]" (12pt, italic)
- **Font**: Times New Roman, 12pt throughout
- **Spacing**: 1.5 or double line spacing
- **Alignment**: Justified
- **Margins**: 1 inch on all sides
- **Page breaks**: New chapter starts on new page

### Five-Section Structure

1. **1.1 Motivation and Context** — Why does this problem matter?
2. **1.2 Problem Statement** — What specific problem are you solving?
3. **1.3 Research Objectives/Questions** — What do you aim to achieve?
4. **1.4 Main Contributions** — How is your work novel?
5. **1.5 Thesis Organization** — What comes next?

---

## Example 1: Introduction (Stress-Testing Thesis)

```
CHAPTER I. INTRODUCTION


1.1 Motivation and Context

Life insurance underwriting in emerging markets operates under conditions fundamentally different 
from developed markets. Limited historical outcome data, high population volatility, rapid economic 
changes, and fragmented health infrastructure create unique challenges for both traditional and 
AI-driven underwriting systems (Cambodia Risk Profile, 2025). Cambodia in particular faces these 
pressures acutely: the insurance market is nascent with <30% population penetration, mortality 
assumptions are based on small datasets, and occupational/endemic risk factors vary significantly 
by province (Mondulkiri endemic malaria prevalence 15x higher than urban centers).

The global insurance industry increasingly relies on Population Stability Index (PSI) as the 
de facto standard for monitoring distribution drift in underwriting systems. PSI is interpretable, 
computationally efficient, and well-documented in actuarial practice. However, PSI was developed 
and validated primarily in stable, data-rich markets (North America, Europe) where training datasets 
are large, historical outcomes comprehensive, and population distributions relatively static. There 
is a significant gap in the literature regarding PSI's robustness in emerging market contexts where 
populations are volatile and training data sparse.

This thesis is motivated by three observations:

First, a single-metric approach to drift monitoring is risky. Many AI underwriting failures stem 
not from overall distribution shift, but from concept drift, feature shift, or label shift—phenomena 
not always visible in a single aggregated metric. Cambodia's rapidly evolving healthcare infrastructure 
(government diabetes clinics normalizing BP readings, mobile health programs changing risk exposure) 
exemplifies scenarios where input features and labels shift without large changes in mortality ratio.

Second, emerging market underwriting decisions are high-stakes. Each decline costs revenue and 
customer trust; each over-priced approval erodes margin. An AI system that approves low-risk 
applicants at high premiums (due to undetected distribution shift) can trigger adverse selection 
and portfolio deterioration.

Third, AI adoption in emerging markets is accelerating, but without adequate validation frameworks. 
Cambodia's insurance industry lacks established stress-testing harnesses for validating model 
robustness. This thesis fills that gap by providing empirical evidence of PSI's strengths and 
weaknesses in an emerging market context.


1.2 Problem Statement

Current drift detection in underwriting relies on single-metric monitoring (PSI on mortality ratio). 
While PSI successfully detects large population distribution shifts, our hypothesis is that PSI 
misses three critical failure modes:

1. Label Drift: Input features change (e.g., BP distribution normalizes), but the target outcome 
   (mortality_ratio) remains similar by coincidence, masking a model assumption breach.

2. Feature-PSI Decoupling: A new cohort (young, healthy applicants) enters the portfolio with 
   mortality_ratio matching the baseline distribution, triggering no PSI alert despite dramatic 
   demographic shifts.

3. Bin Edge Camouflage: Applicants cross decision boundaries (e.g., LOW→MEDIUM risk tier) without 
   triggering a large PSI movement, causing HITL escalation rates to rise silently.

These failure modes matter because they lead to silent model degradation: the system appears stable 
(PSI is GREEN) while performance silently erodes. The practical consequence is under-detection of 
model performance drift, leading to:
- Systematic under/over-pricing
- Adverse selection (healthy applicants self-select out at high premiums)
- Portfolio A/E ratio distortion
- Regulatory non-compliance if drift is not detected

This problem is particularly acute in emerging markets like Cambodia where population shifts are 
frequent and often undocumented (e.g., migration patterns, occupational changes, disease epidemiology).


1.3 Research Objectives

This thesis aims to:

**Primary Objective**: Empirically validate whether PSI alone is sufficient for drift detection in 
emerging market underwriting, and identify scenarios where PSI provides false negatives.

**Secondary Objectives**:
1. Develop a synthetic data generator producing authentic Cambodian applicant profiles with 
   calibrated mortality ratios
2. Conduct three controlled experiments (baseline, responsiveness, adversarial) to stress-test PSI
3. Propose a multi-metric monitoring framework addressing PSI's failure modes
4. (Optional) Implement intelligent routing using LangGraph to operationalize multi-metric decisions

**Research Questions**:
- RQ1: How well does PSI detect population distribution shifts of varying magnitudes (0%-50% 
  distortion)?
- RQ2: In what scenarios does PSI fail to alert despite significant model performance degradation?
- RQ3: What secondary metrics successfully detect the three failure modes that PSI misses?
- RQ4: Can a multi-metric monitoring framework outperform single-metric PSI?


1.4 Main Contributions

This thesis makes the following novel contributions:

1. **First Empirical Validation of PSI in Emerging Market Context**: Prior literature assumes PSI 
   works universally. This is the first rigorous stress-test of PSI in an emerging market setting 
   (Cambodia), with results specific to population volatility and limited historical data.

2. **Identification of Three Critical PSI Failure Modes**: The thesis empirically demonstrates 
   three scenarios where PSI gives false negatives. These are not theoretical edge cases—they are 
   realistic scenarios (healthcare reform, occupational influx, tier boundary shifts) that can occur 
   in practice.

3. **Multi-Metric Monitoring Framework**: Rather than replacing PSI (which is sound), the thesis 
   proposes a practical framework combining PSI + 3 secondary metrics. This is immediately deployable 
   and requires no major system overhaul.

4. **Synthetic Stress-Testing Harness**: The thesis provides a reusable harness for testing 
   underwriting systems against controlled population distortions. This can be adapted for other 
   emerging markets or other underwriting contexts.

5. **LangGraph Integration (Optional)**: If time permits, implementing intelligent routing 
   demonstrates how multi-metric monitoring can be operationalized at decision time, elevating the 
   thesis from theoretical to practical.

These contributions de-risk AI adoption in emerging markets by providing evidence-based guidance 
on drift monitoring.


1.5 Thesis Organization

The remainder of this thesis is organized as follows:

**Chapter II: Background and Literature Review** provides context on life insurance underwriting, 
drift detection methods, and the specific challenges of emerging market risk modeling. We review 
existing approaches to concept drift, feature shift, and label shift, and explain why single-metric 
monitoring is insufficient.

**Chapter III: Methodology** describes the synthetic data generation process, PSI calculation 
procedures, and the design of three controlled experiments. We detail the Cambodia risk factors 
(occupational, endemic, healthcare tier multipliers) and explain our experimental hypotheses.

**Chapter IV: Results** presents findings from all three experiments. EXP-001 validates the 
synthetic generator (PSI ≈ 0 by construction). EXP-002 demonstrates PSI monotonicity (PSI increases 
smoothly with distortion). EXP-003 presents the three failure modes and secondary metric detection.

**Chapter V: Discussion and Implications** interprets the results, discusses limitations, and 
proposes the multi-metric monitoring framework. We outline business implications for insurance 
companies operating in emerging markets and suggest future research directions.

**Chapter VI: Conclusion** summarizes contributions and reinforces the main message: PSI is 
necessary but not sufficient; multi-metric monitoring enables safer AI underwriting in emerging 
markets.

---

## Example 2: Introduction (General Technical Project)

```
CHAPTER I. INTRODUCTION


1.1 Motivation and Context

Public transportation is critical infrastructure for urban development, particularly in developing 
cities like Phnom Penh where manual fare collection and human headcount methods remain dominant. 
Current passenger counting methods rely on (a) manual tally by bus conductors, prone to error and 
inconsistent, or (b) optical sensors and fare gates, expensive to install and maintain across large 
fleets. Accurate, real-time passenger counting is essential for route planning, revenue optimization, 
and demand forecasting, yet Phnom Penh City Bus Authority (CBA) currently lacks reliable granular 
data on passenger flows.

Recent advances in computer vision and deep learning offer a path to scalable, cost-effective 
automated passenger counting (APC). CCTV infrastructure already exists on most public buses, and 
modern object detection models (YOLO, DETR) can detect and track passengers at high frame rates. 
However, deploying computer vision for real-time counting faces challenges: (1) occlusion (passengers 
crowding), (2) variable lighting (daytime, nighttime), (3) computational constraints (GPU availability 
on buses), and (4) domain adaptation (model trained on one bus type may fail on another).

This thesis is motivated by the opportunity to provide CBA with an accurate, low-cost automated 
passenger counting system leveraging existing CCTV infrastructure.


1.2 Problem Statement

Phnom Penh City Bus Authority needs an Automated Passenger Counting (APC) system that:
- Counts boarding and alighting passengers with >90% accuracy
- Operates in real-time on mid-range GPU (GeForce RTX 2080 or equivalent)
- Handles various lighting conditions and crowding scenarios
- Integrates seamlessly with existing bus CCTV systems
- Produces actionable data (passenger count per route, per time window)

The core problem: existing commercial APC systems are proprietary and expensive ($10K-50K per bus); 
open-source approaches often fail under real-world conditions (variable lighting, occlusion). This 
thesis develops a practical, open-source solution optimized for the Cambodian context.


1.3 Research Objectives

**Primary**: Develop and validate a real-time APC system using computer vision that achieves ≥90% 
counting accuracy on Phnom Penh buses.

**Secondary**:
1. Compare object detection architectures (YOLO, Faster R-CNN, DETR) for bus passenger detection
2. Implement tracking algorithms (ByteTrack, DeepSORT) for counting passengers
3. Handle real-world challenges: occlusion, crowding, variable lighting
4. Deploy on realistic GPU hardware with latency <50ms per frame


1.4 Main Contributions

1. **First APC system validated on Phnom Penh bus data**: Prior work focuses on US/European buses; 
   this is the first system adapted for Southeast Asian urban buses.

2. **Data augmentation approach for limited labeled data**: We develop synthetic data generation 
   techniques to overcome the lack of labeled passenger counting datasets.

3. **Real-time performance optimization**: We identify YOLO + ByteTrack as the optimal balance of 
   accuracy and speed, achieving 27-29 FPS on mid-range GPU.

4. **Open-source deployment harness**: Code and model are made available for replication and 
   adaptation to other cities.


1.5 Thesis Organization

Chapter II reviews computer vision for passenger counting. Chapter III describes the dataset, 
model architectures, and experimental setup. Chapter IV presents results. Chapter V discusses 
implications and future work.

---

## Writing Guidelines for Chapter 1

### Paragraph Structure
- **Opening paragraph**: Hook the reader. Why should they care about this problem?
- **Middle paragraphs**: Build the case. Provide evidence, examples, context.
- **Closing paragraph**: Transition to next section or reiterate key point.

### Section Tips

**1.1 Motivation and Context**
- Start with a compelling observation or statistic
- Provide domain-specific context (e.g., Cambodia insurance market facts)
- Explain why existing solutions are insufficient
- End with: "This thesis addresses..."

**1.2 Problem Statement**
- State the specific problem clearly (not just "problem exists")
- Be concrete: numbers, metrics, failure modes
- Explain why it matters (business impact, safety, performance)
- Define scope: what are you NOT solving?

**1.3 Research Objectives/Questions**
- Use numbered lists
- State primary objective first, secondary objectives after
- Research questions should be answerable, specific, measurable
- Format: "RQ1: How does X affect Y under conditions Z?"

**1.4 Main Contributions**
- Number them (1, 2, 3...)
- Lead with novelty: "First", "Novel approach", "First empirical validation"
- Explain why each contribution matters (impact)
- Connect to research questions

**1.5 Thesis Organization**
- Brief 1-2 sentence summary of each remaining chapter
- Format: "Chapter II: [Title] discusses [topic] and explains [key concept]."
- Help reader understand the logical flow
- Optional: "Throughout this thesis, we assume [assumptions]."

### Common Pitfalls to Avoid

❌ **Don't**:
- Overstate claims ("This solves all drift detection problems")
- Make promises you don't keep ("We will implement LangGraph"—only if you do)
- Use vague language ("related work", "previous studies")
- Include citations with no context
- Mix problem description with solutions
- Exceed 5-6 pages (Chapter 1 should be concise)

✅ **Do**:
- Be specific and concrete
- Use examples and evidence
- Clearly delineate what you're doing vs. not doing
- Anticipate reader questions
- Use clear, direct language
- Keep tone formal but engaging

---

## Checklist Before Moving to Chapter 2

- [ ] Chapter 1 is 3-5 pages
- [ ] Motivation section has 2-3 compelling reasons why this work matters
- [ ] Problem statement is concrete and specific
- [ ] Research objectives are measurable and aligned with problem
- [ ] Main contributions are clearly numbered and novel
- [ ] Thesis organization preview helps reader understand the flow
- [ ] No forward-looking promises (LangGraph, etc.) unless you commit to them
- [ ] All section numbers are correct (1.1, 1.2, 1.3, etc.)
- [ ] Page numbers and headers are properly formatted
- [ ] No spelling, grammar, or punctuation errors

---

**Next Step**: After completing Chapter 1 (Introduction), move to Chapter 3 using `thesis-methodology-template.md`.

Note: Chapter II (Literature Review/Background) would typically come between Chapter 1 and Chapter 3. If you need a Chapter 2 template, see your advisor or consult your institution's guidelines. This template focuses on Chapters 1, 3, 4, and 5 (the core experimental structure).
