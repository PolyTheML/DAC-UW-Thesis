# ITC Thesis Formatting Guide (from Template)

## Font & Typography
- **Font**: Times New Roman throughout
- **Chapter headings (I, II, III...)**: Size 16, Bold, ALL CAPS
- **Section headings (1.1, 2.1...)**: Size 14, Bold
- **Subsection headings (1.1.1, 1.1.2...)**: Size 12, Bold, indent only once
- **Body text**: Size 12, line spacing 1.5, justified alignment (Ctrl+J)
- **Spacing**: Left=0cm, Right=0cm, Before=0pt, After=12pt

## Page Layout
- **New page rule**: Every new Roman numeral chapter (I, II, III, IV, V) must start on a new page
- Margins, line space, font size follow standard ITC memoire format

## Citation Style
- **APA 7th edition** recommended
- Tools: citefast.com, Google Scholar

## Structure Mapping (Research Thesis → ITC Template)

| ITC Template Section | Research Thesis Content | Notes |
|---------------------|------------------------|-------|
| I. INTRODUCTION | Ch1: Introduction | Skip internship/org subsections; replace with research context |
| II. PRESENTATION OF THE PROJECT / LITERATURE REVIEW | Ch2: Literature Review | Combine template sections II and III |
| III. PROJECT ANALYSIS AND CONCEPTS | Ch3: Methodology | Functional req = experimental design; Tools = algorithms/dataset |
| IV. DETAIL CONCEPT | — | Absorbed into Ch3 Methodology |
| V. IMPLEMENTATION | Ch4: Results and Discussion | Experiments, figures, analysis |
| VI. CONCLUSION | Ch5: Conclusion | Summary, limitations, future work |
| REFERENCES | References | APA 7 |
| Appendices | Appendices | Code listings, extra figures |

## Drafting Convention (Markdown → Word)
- Write chapters as `.md` files
- Use markdown headers (`#`, `##`, `###`) corresponding to chapter/section/subsection
- Insert `[FIGURE: caption]` placeholders where figures belong
- Insert `[TABLE: caption]` placeholders where tables belong
- Insert `[CITATION: Author Year]` placeholders for references to be filled
