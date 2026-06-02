# Thesis Equation Audit Pipeline — Design Spec
**Date**: 2026-06-02  
**Status**: Approved for implementation  

---

## Overview

A single-script Python pipeline (`audit/run_audit.py`) that audits every mathematical expression in the thesis for correctness, citation, source traceability, notation consistency, and literature-claim consistency. Produces a single unified HTML dashboard (`audit/dashboard.html`).

---

## Decisions Made

| Question | Decision |
|---|---|
| Equation matching strategy | Hybrid: symbolic (SymPy) first, LLM prompts written to file for unresolved cases |
| Document sources | Markdown chapters + DOCX (cross-checked against each other) |
| Output format | Single unified HTML dashboard |
| LLM API integration | No direct API calls — write prompt files to `audit/llm_review_queue/` for manual review |
| Pipeline architecture | Single script, 10 sequential phase functions, JSON cache between phases |

---

## Repository Context

- **Thesis source**: `thesis/health_rl/chapter0{1..6}_*.md` — inline LaTeX math (`$...$`, `$$...$$`)
- **Thesis DOCX**: `thesis/build/I5_ITC_Thesis_Submission_Final_fig21_fig22.docx` (primary submission)
- **Papers**: 5 PDFs in `thesis/papers/` (Li et al. 2010, Robbins 1952, Agrawal & Goyal 2013, Zhou et al. 2020, Ensign et al. 2018)
- **No `.bib` file** — citations are inline text patterns like `(Author, Year)`

---

## File Layout

```
audit/
  run_audit.py                  ← single entry point
  cache/
    paper_index.json            ← index of all 5 papers
    papers/                     ← per-paper JSON
    thesis_equations.json       ← all extracted thesis equations
    phase_results/              ← intermediate JSON output per phase (4–9)
  llm_review_queue/             ← prompt .txt files for manual LLM review
  repository_inventory.md       ← Phase 1 output
  dashboard.html                ← Phase 10 output (unified HTML report)
```

`audit/cache/` is deleted and recreated on each run (fully reproducible).  
`audit/llm_review_queue/` is **preserved** across runs so manual reviews are not lost.

---

## Phase Specifications

### Phase 1 — Repository Inventory
Walk the repo. Record all thesis documents, bibliography files, paper PDFs, figures, and tables.  
**Output**: `audit/repository_inventory.md`  
**Failure modes**: none — read-only filesystem walk.

### Phase 2 — Paper Ingestion
For each PDF in `thesis/papers/`, use `pymupdf` (fitz) to extract:
- Title, authors, year (from first 2 pages)
- Section headings (heuristic: short all-caps or numbered lines)
- Mathematical content: lines containing LaTeX-like tokens (`\frac`, `\theta`, `\sum`, `\arg`, etc.) or dense symbol characters
- Raw text by page (for context lookup in Phase 4)

**Output**: `audit/cache/papers/<paper_name>.json` per paper, `audit/cache/paper_index.json`

**JSON structure**:
```json
{
  "title": "",
  "authors": [],
  "year": "",
  "filename": "",
  "sections": [{"heading": "", "page": 0}],
  "equations": [{"text": "", "page": 0, "context_before": "", "context_after": ""}],
  "raw_pages": {"1": "..."}
}
```

### Phase 3 — Thesis Ingestion
Extract equations from two sources and cross-check them.

**Markdown extraction**: regex on `$...$` (inline) and `$$...$$` (display) blocks. For each equation record:
- Chapter and section (from preceding headings)
- 3 sentences of context before and after
- Nearby citation patterns (`(Author[,]? \d{4})`) within a 500-character window

**DOCX extraction**: `python-docx` to locate OMML (`<m:oMath>`) XML nodes. Convert OMML to LaTeX using a lightweight `lxml`-based OMML→LaTeX mapper (handling the most common constructs: fractions, superscripts, subscripts, square roots, summations).

**Cross-check**: For each DOCX equation, find its markdown counterpart by position heuristic (chapter + approximate paragraph index). Flag any DOCX equation with no markdown match as `BUILD_DIVERGENCE`.

**Output**: `audit/cache/thesis_equations.json`

**Per-equation record**:
```json
{
  "equation_id": "ch03_eq_001",
  "chapter": "03",
  "section": "3.3.2",
  "latex_md": "...",
  "latex_docx": "...",
  "source": "both|md_only|docx_only",
  "build_divergence": false,
  "nearby_text_before": "...",
  "nearby_text_after": "...",
  "citations": ["Li et al., 2010"]
}
```

### Phase 4 — Equation Traceability
For each thesis equation, find the best-matching paper equation.

**Match pipeline** (in order, stop at first success):
1. **Exact LaTeX string match** (after whitespace normalization)
2. **SymPy symbolic equivalence**: parse both sides with `sympy.sympify` / `sympy.latex` round-trip; check `sympy.simplify(a - b) == 0`
3. **Token overlap heuristic**: `rapidfuzz.fuzz.token_set_ratio` on LaTeX token sequences; threshold ≥ 75

**Citation-guided search**: If the equation has a nearby citation, search that paper first before others.

**Outcomes**:
- `PASS` — matched in cited source (confidence ≥ 0.75)
- `WARNING` — matched in a non-cited source
- `FAIL` — no match in any paper (confidence < 0.40)
- `LLM_QUEUE` — partial match (0.40–0.74), write structured prompt to `audit/llm_review_queue/eq_<id>.txt`

**Output**: `audit/cache/phase_results/phase4_traceability.json`

### Phase 5 — Mathematical Validation
Detect claimed derivations via text cues ("therefore", "substituting", "which gives", "simplifying", "it follows that", "from Eq.").

For each detected derivation pair (Eq A → Eq B), attempt SymPy verification:
- Parse both LaTeX expressions via `sympy.parsing.latex`
- Check `sympy.simplify(A - B) == 0` or `sympy.equals(A, B)`
- On parse failure or timeout (>5s): mark `MANUAL REVIEW`

**Output**: `audit/cache/phase_results/phase5_validation.json`

### Phase 6 — Notation Consistency Audit
Build a **symbol table** across all thesis equations.

For each LaTeX token that is a variable name (single letter, Greek letter, or named symbol), record:
- All chapters/equations where it appears
- The surrounding definition context (text matching `"where <symbol> is ..."`, `"let <symbol> denote ..."`)

**Flags**:
- `REUSE_CONFLICT`: same symbol, different definitions in different chapters
- `UNDEFINED`: symbol used in equation with no definition found nearby
- `INCONSISTENT_INDEX`: same concept indexed differently across chapters (e.g., `\theta_a` vs `\theta_k`)

**Output**: `audit/cache/phase_results/phase6_notation.json`

### Phase 7 — Literature Review Consistency Audit
Extract claim sentences from `chapter03_literature_review.md` — sentences containing epistemic verbs ("achieves", "shows", "proves", "outperforms", "is bounded by", "guarantees", "demonstrates").

For each claim:
1. Find the nearest citation within the sentence or paragraph
2. Locate that paper in `audit/cache/papers/`
3. Search paper text for supporting evidence using keyword overlap (rapidfuzz)

**Outcomes**: `SUPPORTED` / `PARTIALLY_SUPPORTED` / `UNSUPPORTED` / `NO_CITED_PAPER`

**Output**: `audit/cache/phase_results/phase7_literature.json`

### Phase 8 — Citation Audit
Scan all thesis equations and claim sentences for missing citations.

**Missing citation**: equation or claim sentence with no `(Author[,]? \d{4})` pattern within 500 characters in either direction.

**Citation quality check**: for each cited paper, verify it exists in `thesis/papers/` and has been indexed in Phase 2.

**Output**: `audit/cache/phase_results/phase8_citations.json`

### Phase 9 — RL & Fairness Special Audit
Hardcoded canonical checks for the thesis's core domain equations.

| Check ID | Equation | Canonical Form | Source |
|---|---|---|---|
| RL-01 | LinUCB action selection | `\arg\max_a (\hat\theta_a^\top x + \alpha \sqrt{x^\top A_a^{-1} x})` | Li et al. 2010, Eq. 4 |
| RL-02 | LinTS posterior | `\tilde\theta_a \sim \mathcal{N}(\hat\theta_a, v^2 A_a^{-1})` | Agrawal & Goyal 2013 |
| RL-03 | LinUCB design matrix update | `A_a \leftarrow A_a + x_t x_t^\top` | Li et al. 2010 |
| RL-04 | Sherman-Morrison formula | `A^{-1} \leftarrow A^{-1} - \frac{A^{-1} x x^\top A^{-1}}{1 + x^\top A^{-1} x}` | Standard linear algebra |
| RL-05 | Cumulative regret definition | `R_T = \sum_t (r^*_t - r_t)` | Lattimore & Szepesvári 2020 |
| RL-06 | PSI formula | `\text{PSI} = \sum_i (A_i - E_i) \ln(A_i / E_i)` | Standard actuarial |
| RL-07 | Four-fifths rule | `\min_g(\text{rate}_g) / \max_g(\text{rate}_g) \geq 0.80` | EEOC guideline |

Each check: locate matching thesis equation → symbolic comparison → PASS / FAIL / MANUAL REVIEW.

**Output**: `audit/cache/phase_results/phase9_rl_fairness.json`

### Phase 10 — HTML Dashboard
Aggregate all phase results from `audit/cache/phase_results/` and render `audit/dashboard.html`.

**Dashboard structure**:
1. **Executive Summary**: counts table (total equations, PASS/WARNING/FAIL/MANUAL REVIEW/LLM_QUEUE), overall health indicator
2. **High-Priority Issues**: any FAIL items from any phase, sorted by severity
3. Collapsible section per phase with color-coded findings table
4. **LLM Review Queue**: list of equations needing manual Claude review, with links to prompt files

**Status badge colors**: 🟢 PASS · 🟡 WARNING · 🔴 FAIL · 🔵 MANUAL REVIEW · ⬜ LLM_QUEUE

---

## Dependencies

**New packages to add to `requirements.txt`**:
```
pymupdf>=1.24.0
python-docx>=1.1.0
sympy>=1.12
rapidfuzz>=3.6.0
lxml>=5.0.0
```

**Already in repo**: `numpy`, `pandas`

**Dropped from original spec**: `sentence-transformers`, `faiss`, `pdfplumber`, `pytesseract`, `pdf2image`, `unstructured` — unnecessary given 5 known papers and markdown-source equations.

---

## Running

```bash
python audit/run_audit.py
# Produces: audit/dashboard.html
# Produces: audit/llm_review_queue/*.txt  (equations needing manual review)
# Produces: audit/repository_inventory.md
```

Re-runnable: `audit/cache/` is fully regenerated each run.  
`audit/llm_review_queue/` is preserved — existing prompt files are not overwritten.

---

## Constraints

- Do NOT modify any thesis files.
- Do NOT modify any paper PDFs.
- All output goes under `audit/`.
- When uncertain, prefer `MANUAL REVIEW` over guessing.
- Confidence scores must be included for all equation matches.
