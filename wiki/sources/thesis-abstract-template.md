# Thesis Abstract & Résumé Template

**Created**: 2026-04-17  
**Format**: ITC Cambodia standard  
**Pages**: iii (ABSTRACT), iv (RÉSUMÉ), v (Khmer Summary) — lowercase roman numerals  
**Page Count**: Typically 1 page per language

---

## Abstract Page Format (Page iii)

### Formatting Rules
- **Header**: "ABSTRACT" (all caps, centered, 12pt bold)
- **Font**: Times New Roman, 12pt, body text
- **Line Spacing**: Single or 1.5 (tighter than main text for space efficiency)
- **Alignment**: Justified
- **Margins**: 1 inch on all sides
- **Length**: 250-400 words
- **Language**: English
- **Footer**: "Page iii of [Total pages]"

### Content Structure (5 paragraphs typical)

1. **Problem/Context** (40-60 words): What problem does this thesis address?
2. **Motivation** (40-60 words): Why is this problem important?
3. **Methodology** (80-120 words): How did you approach the problem? What methods/data?
4. **Results/Findings** (50-80 words): What did you discover? Quantitative results?
5. **Implications** (30-50 words): What is the impact? How does this contribute to the field?

**Do NOT include**:
- ❌ Citations or references
- ❌ Tables, figures, or equations
- ❌ Personal opinions
- ❌ Future work (save for conclusion)
- ❌ First-person pronouns ("I", "we")

**DO include**:
- ✓ Problem statement
- ✓ Research question/objective
- ✓ Methodology (briefly)
- ✓ Key findings/results
- ✓ Significance and impact

---

## Example 1: Abstract (Stress-Testing Thesis)

```
ABSTRACT

Life insurance underwriting in emerging markets faces unique challenges stemming from limited 
historical outcomes, high population volatility, and rapid distribution shifts. While Population 
Stability Index (PSI) is an industry standard for drift detection, its effectiveness in emerging 
market underwriting contexts remains understudied. This thesis addresses the critical gap by 
empirically validating PSI's robustness in detecting population distribution shifts specific to 
Cambodia.

This research developed a synthetic applicant generator producing 10,000 demographically authentic 
Cambodian insurance applicants calibrated with real mortality ratios and Cambodia-specific risk 
multipliers (occupational, endemic, healthcare tier). Three controlled experiments were conducted: 
(1) baseline validation confirming synthetic distribution stability, (2) PSI responsiveness testing 
by injecting distortions ranging from 0% to 50%, and (3) adversarial scenario testing to identify 
failure modes where PSI provides false negatives.

Key findings reveal that PSI successfully detects large population shifts (>25% distortion triggers 
RED alert), and increases monotonically with distortion magnitude. However, the research identified 
three critical failure modes where PSI remains GREEN despite significant model performance degradation: 
(1) label drift from feature distribution changes without mortality ratio shifts, (2) feature-PSI 
decoupling from new low-risk cohort influxes matching baseline bins, and (3) bin edge camouflage 
where applicants cross decision boundaries without substantial PSI movement.

The thesis proposes multi-metric monitoring combining PSI with secondary metrics: feature 
co-occurrence PSI (label drift detection), age distribution PSI (cohort shift detection), and 
HITL escalation rate (boundary sensitivity). This framework successfully addresses all three 
failure modes and enables safer AI underwriting in emerging market contexts.

This work de-risks AI adoption in Cambodia and other emerging markets by providing empirical 
evidence that PSI alone is insufficient, and proposing a practical solution validated on synthetic 
stress-test scenarios. Optional LangGraph implementation demonstrates intelligent routing integration 
for context-aware decision-making.

Page iii of [Total pages]
```

---

## Example 2: Abstract (General Research Project)

```
ABSTRACT

This thesis presents the design and implementation of a real-time video-based violence detection 
system that leverages deep learning techniques to enhance public safety through automated surveillance. 
Violence in public spaces such as schools, hospitals, and streets has become a critical concern, 
requiring intelligent systems that can detect and respond to threats immediately. Traditional 
surveillance heavily relies on human monitoring, which is inefficient and prone to error.

The system utilizes a combination of ResNet-18, a pretrained Convolutional Neural Network (CNN), 
and Long Short-Term Memory (LSTM) networks to capture spatial and temporal features from video 
frames. The RWF-2000 and Real Life Violence dataset was used for model training and evaluation, 
supported by preprocessing techniques such as frame extraction, resizing, and feature normalization. 
A sliding window mechanism enhances temporal context during classification.

The model is trained and evaluated using accuracy, precision, recall, and F1-score to ensure 
reliability and minimize false detections. In the final application, OpenCV handles real-time 
video capture while the Telegram Bot API delivers alert messages and recorded video segments 
when violence is detected. Performance testing on a mid-range NVIDIA GPU demonstrates promising 
real-time detection accuracy with practical deployment potential.

Results conclusively demonstrate that the YOLOv8m model paired with the ByteTrack tracker provides 
optimal balance of performance characteristics, delivering real-time processing speeds (27-29 FPS) 
while maintaining competitive and stable counting accuracy. This system demonstrates practical, 
scalable, and cost-effective detection capabilities suitable for high-risk area deployment.

The research establishes a foundation for future enhancements, including edge deployment, 
multi-camera integration, and advanced attention mechanisms to further improve detection accuracy 
and speed.

Page iii of [Total pages]
```

---

## Résumé Page Format (Page iv)

### Formatting Rules
- **Header**: "RÉSUMÉ" (all caps, centered, 12pt bold)
- **Font**: Times New Roman, 12pt
- **Line Spacing**: Single or 1.5
- **Alignment**: Justified
- **Margins**: 1 inch on all sides
- **Length**: 250-400 words (equivalent to English Abstract)
- **Language**: French
- **Footer**: "Page iv of [Total pages]"

### Structure
Same 5-paragraph structure as English Abstract, but in French:
1. Contexte/Problème
2. Motivation
3. Méthodologie
4. Résultats
5. Implications

---

## Example 1: Résumé (Stress-Testing Thesis)

```
RÉSUMÉ

La souscription d'assurance-vie dans les marchés émergents fait face à des défis uniques 
découlant des données historiques limitées, de la volatilité démographique élevée et des 
changements rapides de la distribution. Bien que l'Indice de Stabilité de la Population (PSI) 
soit une norme industrielle pour la détection de la dérive, son efficacité dans les contextes 
de souscription des marchés émergents reste peu étudiée. Cette thèse aborde cette lacune critique 
en validant empiriquement la robustesse du PSI dans la détection des changements de distribution 
de la population spécifiques au Cambodge.

Cette recherche a développé un générateur de candidats synthétiques produisant 10 000 candidats 
d'assurance cambodgiens démographiquement authentiques calibrés avec des ratios de mortalité réels 
et des multiplicateurs de risque spécifiques au Cambodge (occupationnels, endémiques, niveau de 
soins de santé). Trois expériences contrôlées ont été menées : (1) validation de base confirmant 
la stabilité de la distribution synthétique, (2) test de sensibilité du PSI en injectant des 
distorsions allant de 0% à 50%, et (3) test de scénarios adversariaux pour identifier les modes 
de défaillance où le PSI donne des faux négatifs.

Les résultats clés révèlent que le PSI détecte avec succès les changements importants de la 
population (distorsion >25% déclenche une alerte RED) et augmente de manière monotone avec 
l'ampleur de la distorsion. Cependant, la recherche a identifié trois modes de défaillance critiques 
où le PSI reste GREEN malgré une dégradation significative des performances du modèle : (1) la 
dérive des étiquettes due à des changements de distribution des caractéristiques sans changement 
du ratio de mortalité, (2) le découplage caractéristique-PSI des afflux de nouvelles cohortes à 
faible risque correspondant aux bacs de base, et (3) le camouflage des bords de bac où les 
candidats traversent des limites de décision sans mouvement PSI substantiel.

La thèse propose une surveillance multi-métriques combinant le PSI avec des métriques secondaires : 
co-occurrence de caractéristiques PSI (détection de dérive d'étiquettes), distribution d'âge PSI 
(détection de changement de cohorte) et taux d'escalade HITL (sensibilité des limites). Ce cadre 
répond avec succès aux trois modes de défaillance et permet une souscription IA plus sûre dans 
les contextes des marchés émergents.

Ce travail réduit les risques d'adoption de l'IA au Cambodge et dans d'autres marchés émergents 
en fournissant des preuves empiriques que le PSI seul est insuffisant, et en proposant une 
solution pratique validée sur des scénarios de test de stress synthétiques.

Page iv of [Total pages]
```

---

## Khmer Summary Page (Page v) [Optional for Bilingual Theses]

### Formatting Rules
- **Header**: "សង្ខេប" (Khmer word for "summary" in large font, centered, 12pt bold)
- **Font**: Times New Roman or Khmer-supporting font, 12pt
- **Line Spacing**: 1.5
- **Alignment**: Justified
- **Margins**: 1 inch on all sides
- **Length**: 250-400 words (equivalent to English Abstract)
- **Language**: Khmer
- **Footer**: "ទំព័រ v នៃ [ចំនួនសរុប]" (Page v of [Total pages] in Khmer)

### Structure
Same as Abstract/Résumé but presented in Khmer script.

---

## Abstract Writing Tips

### Sentence Structure
- Use clear, direct sentences
- Avoid jargon unless necessary (define if used)
- Use past tense for completed work, present tense for established facts
- Vary sentence length for readability

### Verb Tense
- **Past tense**: For methodology and results ("This thesis developed...", "Results revealed...")
- **Present tense**: For established facts ("PSI is an industry standard...", "This work demonstrates...")

### Common Openings
- "This thesis addresses..."
- "This research investigates..."
- "This work presents..."
- "This paper develops..."
- "The primary contribution of this research..."

### Common Closing Statements
- "...enabling practical deployment in [domain]"
- "...paving the way for future research in..."
- "...with implications for [field/industry]"
- "...providing a foundation for [next steps]"
- "...advancing the state of practice in..."

---

## Keywords Section (Optional)

Some ITC theses include a "Keywords" line below the abstract:

```
Keywords: Population Stability Index, Drift Detection, Emerging Markets, Synthetic Data, 
          AI Underwriting, Multi-Metric Monitoring, Robustness Analysis

Page iii of [Total pages]
```

**Guidelines for keywords**:
- 5-10 key terms
- Separated by commas
- Listed in order of importance
- Include both technical and domain terms

---

## Before You Write

### Checklist
- [ ] Understand your complete thesis findings (don't write abstract until done)
- [ ] Identify 3-5 key contributions
- [ ] Note main results and numbers
- [ ] Review your methodology section for accurate representation
- [ ] Prepare French/Khmer translations if bilingual
- [ ] Identify 5-10 keywords

### Don't Include
- ❌ References or citations (e.g., "Smith (2020) found...")
- ❌ Figures, tables, or equations
- ❌ Abbreviations on first use (define inline or expect reader to know)
- ❌ "This thesis will discuss..." (focus on what you did, not what you'll discuss)
- ❌ Excessive hedging ("might", "possibly", "perhaps")
- ❌ Future work ("Future research will...")

---

## Word Count Tool

| Section | Approximate Words |
|---------|------------------|
| Problem/Context | 50 |
| Motivation | 50 |
| Methodology | 100 |
| Results | 75 |
| Implications | 40 |
| **Total** | **315** |

Aim for 250-400 total. If closer to 250, expand methodology section. If closer to 400, trim methodology.

---

## Revision Checklist

After writing your first draft, review:

- [ ] Does the abstract accurately reflect the thesis content?
- [ ] Are the key findings clearly stated?
- [ ] Is the tone formal and objective?
- [ ] Is the methodology sufficiently explained (in brief)?
- [ ] Are there any unsupported claims?
- [ ] Can a reader understand the work without reading the full thesis?
- [ ] Is the length between 250-400 words?
- [ ] Are there any spelling, grammar, or punctuation errors?
- [ ] Does the Résumé accurately translate the Abstract?

---

**Next Step**: After completing Abstract and Résumé, move to Table of Contents, then start Chapter 1 using `thesis-introduction-template.md`.
