# Supervisor Revision Pass (Dr. Phauk) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the 25 supervisor comments from `Poly_draft_report.pdf` to the live LaTeX thesis in `thesis/Thesis/`, producing a fresh Overleaf bundle (r15) that the student compiles for GREEN sign-off.

**Architecture:** Direct edits to the XeLaTeX source tree `thesis/Thesis/` (Cover_Pages + Chapters + Main_content.tex preamble). No build pipeline change. Verification is local (grep/structural) because no local XeLaTeX exists; final verification is the student's Overleaf compile.

**Tech Stack:** XeLaTeX (report class), polyglossia + Khmer OS fonts, apacite/natbib, Pandoc-emitted longtables, TikZ (preamble dgnode styles).

## Global Constraints

- **Edit only `thesis/Thesis/`** (NOT `thesis/Thesis_template_backup/`).
- **Do NOT commit until the student confirms Overleaf GREEN** — established repo gate (commit-after-GREEN). Tasks stage with `git add` only; the single commit step is Task 11, post-GREEN.
- **Branch:** stay on `thesis/ch5-structural-pass` (not default; no new branch).
- **Preserve every frozen statistic verbatim:** `$90,540`, `$72,292`, `+25%`, `p < 0.001`, `d = 2.98`, `14.8%`, `$2.20`, `$9.01`, `85.7%`/`85.72%`, `90.1%`/`90.12%`, PSI `0.082`/`0.123`, ceiling `30–33%`. Never restate or round.
- **SDG section is intact** (`ch2-Presentation.tex` §2.4, committed `93c91ac`). The supervisor reviewed pre-SDG; do not touch SDG content except to apply the global heading/figure-reference rules to it.
- **Khmer edits require student verification** — flag each, do not assert correctness. Khmer font commands already in preamble: `\khmerfont` (Battambang), `\khmerfontmoul` (Muol Light).
- **Section references are manual text, not `\ref`** — renumbering requires editing literal "Section 4.x" strings.

### Frozen decisions (from grill, 2026-06-18)

| Q | Decision |
|---|----------|
| Q1 | Full consolidate front matter: one essay Executive Summary; delete Abstract_EN, academic Abstract_KH, Resume_FR; drop keywords |
| Q2 | Reuse verified Khmer prose as Khmer Exec Summary; English mirrors it; Khmer ABOVE English |
| Q3 | Drop enumerated Key-Contributions list from summary (covered by Ch.2 §2.3); keep one prose contributions mention in significance |
| Q4 | Insert numbered §4.1 "General Workflow" + flowchart; rename Ch.4 → "Methodology"; renumber; update all 17 manual "Section 4.x" refs |
| Q5 | Bold best ADMISSIBLE in all Ch.5 tables; mark inadmissible AlwaysRATED ceiling (underline + dagger + note) in Tables 22–25 |
| Q6a | Literature-synthesis table rows drawn from existing Ch.3 citations |
| Q6b | Plan first (this doc), then execute |
| Q6c | Build r15 bundle; hold commit until Overleaf GREEN |

---

## File Map

| File | Responsibility | Tasks |
|---|---|---|
| `Cover_Pages/Executive_Summary.tex` | Rewrite as English essay Exec Summary (de-keyworded, +significance prose) | T1 |
| `Cover_Pages/Executive_Summary_KH.tex` | **NEW** Khmer Exec Summary (from Abstract_KH prose, retitled, no keywords) | T1 |
| `Cover_Pages/Abstract_EN.tex` | **DELETE** (prose folded into Exec Summary) | T1 |
| `Cover_Pages/Abstract_KH.tex` | **DELETE** (prose moved to Executive_Summary_KH) | T1 |
| `Cover_Pages/Resume_FR.tex` | **DELETE** (no French abstract) | T1 |
| `Main_content.tex` | Front-matter `\input` order; chapter-heading preamble | T1, T2 |
| `Cover_Pages/Cover.tex`, `SubCover_KH.tex` | Khmer cover tweaks (adaptive→បត់បែន, no-translate, layout) | T10 |
| `Chapters/ch1-Introduction.tex` | Sentence-case title; DAC logo (`images/DAC.jpg`) | T2, T7 |
| `Chapters/ch2-Presentation.tex` | Sentence-case title; verify §2.3 covers contributions | T1, T2 |
| `Chapters/ch3-LiteratureReview.tex` | Sentence-case title; lit-synthesis table; citation merges | T2, T5, T6 |
| `Chapters/ch4-ProjectAnalysis.tex` | Rename→Methodology; §4.1 flowchart; renumber; ✓/✗; refs | T2, T3, T4 |
| `Chapters/ch5-Results.tex` | Sentence-case title; bold-best pass; "Section 4.x" refs | T2, T3, T8 |
| `Chapters/ch6-Conclusion.tex` | Sentence-case title; §6.1 Findings → points; "Section 4.x" refs | T2, T3, T9 |

**Sequencing:** structural first (T1, T2, T3, T4), then content (T5, T8, T9, T10), then cross-cutting audits LAST so new floats exist (T6 citations, T7 figure-refs), then bundle (T11).

---

### Task 1: Front-matter consolidation

**Files:**
- Create: `thesis/Thesis/Cover_Pages/Executive_Summary_KH.tex`
- Modify: `thesis/Thesis/Cover_Pages/Executive_Summary.tex` (full rewrite)
- Modify: `thesis/Thesis/Main_content.tex:238-249` (input order)
- Delete: `Abstract_EN.tex`, `Abstract_KH.tex`, `Resume_FR.tex`
- Check: `thesis/Thesis/Chapters/ch2-Presentation.tex` §2.3 (contributions coverage)

**Interfaces:**
- Produces: front-matter order `Acknowledgement → Executive_Summary_KH → Executive_Summary → TOC → LoF → LoT → Abbrev`. No other task depends on the summary text.

- [ ] **Step 1: Create `Executive_Summary_KH.tex`** — copy the body of `Abstract_KH.tex` (the 4 Khmer paragraphs inside `\begingroup … \endgroup`) verbatim, but (a) change the heading from `អត្ថបទសង្ខេប` to the Khmer Executive-Summary heading `សេចក្ដីសង្ខេប` *(FLAG for student: confirm Khmer heading wording)*, and (b) DELETE the keyword line (`\noindent{\khmerfontmoul ពាក្យគន្លឹះ៖} …`). Keep `\addcontentsline{toc}{chapter}{…}`.

- [ ] **Step 2: Rewrite `Executive_Summary.tex`** as English essay prose mirroring the Khmer's four paragraphs. Source = `Abstract_EN.tex` paragraphs 1–4 verbatim (problem → method → results+ceiling → significance/contributions), then fold in the two prose paragraphs from the current Exec Summary's "Significance and Impact" (the `Traditional emerging-market…` and `This work is a proof of concept…` paragraphs) merged into/after paragraph 4. Heading stays `\chapter*{\centering EXECUTIVE SUMMARY}` + `\addcontentsline{toc}{chapter}{EXECUTIVE SUMMARY}`. **Remove** the `\textbf{Keywords:}` line. **Do NOT** include any `\begin{itemize}`/`\begin{enumerate}` — pure paragraphs. The contributions survive only as the existing one-sentence prose mention in paragraph 4 ("The thesis contributes a reproducible 20-seed harness, a Cambodia-calibrated synthetic dataset, …") — do not re-list them.

- [ ] **Step 3: Verify Ch.2 §2.3 covers the contributions.** Read `ch2-Presentation.tex` §2.3 (Objective / Secondary Objectives, lines 85–117). Confirm the four contributions (adaptive engine, calibrated test environment, fairness monitoring, HITL layer) are represented. If any is missing, add one sentence to §2.3.2 Secondary Objectives. *(Likely already covered — flag only if a real gap.)*

- [ ] **Step 4: Update `Main_content.tex` input order.** Replace lines 238–249 so the sequence is:
```latex
\newpage
\input{Cover_Pages/Executive_Summary_KH}

\newpage
\input{Cover_Pages/Executive_Summary}
```
Delete the `\input{Cover_Pages/Abstract_KH}`, `\input{Cover_Pages/Abstract_EN}`, and `\input{Cover_Pages/Resume_FR}` lines (and their `\newpage`/comment lines). Keep `SubCover_KH/FR/EN` (Cover Pages section, lines 220–229) untouched.

- [ ] **Step 5: Delete the three orphaned files.**
```bash
git rm "thesis/Thesis/Cover_Pages/Abstract_EN.tex" "thesis/Thesis/Cover_Pages/Abstract_KH.tex" "thesis/Thesis/Cover_Pages/Resume_FR.tex"
```

- [ ] **Step 6: Verify.**
```bash
rtk grep -nE "Abstract_EN|Abstract_KH|Resume_FR" thesis/Thesis/Main_content.tex   # expect: no matches
rtk grep -cE "Keywords:|ពាក្យគន្លឹះ" thesis/Thesis/Cover_Pages/Executive_Summary.tex thesis/Thesis/Cover_Pages/Executive_Summary_KH.tex  # expect: 0
rtk grep -cE "begin\{itemize\}|begin\{enumerate\}" thesis/Thesis/Cover_Pages/Executive_Summary.tex  # expect: 0
```
Stage: `git add -A thesis/Thesis/Cover_Pages thesis/Thesis/Main_content.tex`. **No commit.**

---

### Task 2: Global chapter-heading style → "Chapter I. Introduction"

**Files:**
- Modify: `thesis/Thesis/Main_content.tex` (preamble, after line 159 `\mychapter` block)
- Modify: chapter title strings in all 6 `Chapters/chN-*.tex:1`

**Interfaces:**
- Produces: numbered chapters render "Chapter I. <Sentence case title>" centered, one line, Roman numerals. `\chapter*` (front matter) unaffected.

- [ ] **Step 1: Add heading redefinition to the preamble.** Insert after the `\mychapter` definition (Main_content.tex ~line 159), using `\@makechapterhead` (NOT titlesec — avoids touching the front-matter `\chapter*` headings which use `\@makeschapterhead`). **CRITICAL:** do NOT `\renewcommand{\thechapter}{\Roman{chapter}}` — that cascades into `\thesection` (sections would become "IV.1" not "4.1", breaking the 17 manual refs). Render the Roman numeral in the heading text only via `\Roman{chapter}`, leaving `\thechapter` arabic:
```latex
% ── Numbered-chapter heading: "Chapter I. Title" ─────────────────────────────
% Roman numeral shown in the heading text only (via \Roman{chapter}); \thechapter
% stays arabic so section numbers remain 4.1, 4.2, … and the 17 manual
% "Section 4.x" refs stay valid. \chapter* (front matter/TOC/bib/appendix) uses
% \@makeschapterhead and is untouched.
\makeatletter
\def\@makechapterhead#1{%
  \vspace*{30\p@}%
  {\parindent \z@ \centering \normalfont
    \ifnum \c@secnumdepth >\m@ne
        \LARGE\bfseries \@chapapp\space \Roman{chapter}.\space #1%
    \else
        \LARGE\bfseries #1%
    \fi
    \par\nobreak \vskip 30\p@ }}
\makeatother
```

- [ ] **Step 2: Sentence-case the 6 chapter titles.** Edit line 1 of each chapter file (keep the `\label{...}` slug unchanged):
  - `ch1`: `\chapter{Introduction}\label{chapter-i.-introduction}`
  - `ch2`: `\chapter{Presentation of the Project}\label{chapter-ii.-presentation-of-the-project}`
  - `ch3`: `\chapter{Literature Review}\label{chapter-iii.-literature-review}`
  - `ch4`: `\chapter{Methodology}\label{chapter-iv.-project-analysis-and-concepts}` *(title done here; rename detail in T3)*
  - `ch5`: `\chapter{Results and Discussion}\label{chapter-v.-results-and-discussion}`
  - `ch6`: `\chapter{Conclusion}\label{chapter-vi.-conclusion}`

- [ ] **Step 3: Verify.**
```bash
rtk grep -nE "^\\\\chapter\{" thesis/Thesis/Chapters/ch*.tex   # 6 lines, sentence case
rtk grep -nE "Roman\{chapter\}|@makechapterhead" thesis/Thesis/Main_content.tex  # present
```
**FLAG for Overleaf check (highest-risk item):** confirm (a) numbered chapter pages show "Chapter I. Introduction", (b) front-matter headings (EXECUTIVE SUMMARY, TABLE OF CONTENTS) are unchanged, (c) TOC chapter lines acceptable (Roman numerals). Stage. **No commit.**

---

### Task 3: Ch.4 → "Methodology" + §4.1 General Workflow flowchart + renumber 17 refs

**Files:**
- Modify: `thesis/Thesis/Chapters/ch4-ProjectAnalysis.tex` (title line, intro paragraph, insert §4.1, internal "Section 4.x" refs)
- Modify: `thesis/Thesis/Chapters/ch5-Results.tex`, `ch3-LiteratureReview.tex`, `ch6-Conclusion.tex` ("Section 4.x" refs)

**Interfaces:**
- Consumes: ch4 title already set to `Methodology` in T2.
- Produces: new auto-numbered §4.1; old §4.1–§4.10 auto-shift to §4.2–§4.11; all manual "Section 4.x" text references +1.

- [ ] **Step 1: Insert §4.1 "General Workflow" with master flowchart** immediately after the chapter intro paragraph (after ch4 line 3, before `\section{Functional Requirements}`). Uses preamble `procnode`/`flowarrow`/`feedbackarrow` styles:
```latex
\section{General Workflow}\label{general-workflow}

Figure 2 presents the end-to-end methodology as a single pipeline. Each node is detailed in a dedicated section of this chapter: the synthetic dataset and feature engineering in §4.6, the bandit algorithms and the static baseline in §4.7, the profit-based actuarial reward simulator in §4.8, the PSI and EEOC fairness guardrails in §4.9, the three validation experiments in §4.10, and the deployment roadmap in §4.11. Sections §4.2–§4.4 first establish the functional and non-functional requirements, the implementation tool stack, and the contextual-bandit concept that the pipeline operationalises.

\begin{figure}[H]
\centering
\begin{tikzpicture}[node distance=7mm and 0mm]
  \node[procnode] (data) {Synthetic Cambodia Dataset\\\footnotesize 2{,}000 applicants, CDHS 2021--22 calibrated (§4.6)};
  \node[procnode, below=of data] (feat) {Feature Engineering\\\footnotesize 34-dimensional context vector (§4.6)};
  \node[procnode, below=of feat] (algo) {Bandit Algorithms + Baseline\\\footnotesize LinUCB / LinTS / $\varepsilon$-Greedy vs Static XGB (§4.7)};
  \node[procnode, below=of algo] (rew) {Actuarial Reward Simulator\\\footnotesize profit-based, 4 actions: standard/rated/decline/refer (§4.8)};
  \node[procnode, below=of rew] (fair) {PSI + EEOC Fairness Guardrails\\\footnotesize sliding-window drift + four-fifths audit (§4.9)};
  \node[procnode, below=of fair] (exp) {Experimental Validation\\\footnotesize EXP-005/006/007; HITL in §5.4 (§4.10)};
  \node[procnode, below=of exp] (dep) {Deployment Roadmap\\\footnotesize shadow $\rightarrow$ assisted $\rightarrow$ automated (§4.11)};
  \draw[flowarrow] (data) -- (feat);
  \draw[flowarrow] (feat) -- (algo);
  \draw[flowarrow] (algo) -- (rew);
  \draw[flowarrow] (rew) -- (fair);
  \draw[flowarrow] (fair) -- (exp);
  \draw[flowarrow] (exp) -- (dep);
  \draw[feedbackarrow] (rew.east) to[out=20,in=-20] node[subnote, right=2mm]{online update} (algo.east);
\end{tikzpicture}
\caption{Figure 2 --- End-to-end methodology workflow. Each node maps to a section of this chapter.}
\label{fig:methodology-workflow}
\end{figure}
```
*(NOTE: this takes figure number "Figure 2"; verify the next free in-body figure number when executing — the current "Figure 1" is the DAC org chart in Ch.1. If Figure 2 is already used downstream, renumber this and the downstream body figures consistently, OR give the flowchart the correct next number. Confirm via `rtk grep -nE "Figure [0-9]+\." thesis/Thesis/Chapters/*.tex` before finalizing.)*

- [ ] **Step 2: Rewrite the ch4 intro paragraph** (line 3) so the section roll-call matches the new numbering: §4.1 general workflow; §4.2 functional requirements; §4.3 non-functional; §4.4 tool stack; §4.5 contextual-bandit concept; §4.6 dataset/features; §4.7 algorithms/baselines; §4.8 reward/simulator; §4.9 PSI/fairness; §4.10 experimental design (EXP-005–007; HITL in §5.4); §4.11 deployment roadmap.

- [ ] **Step 3: Update all 17 manual section references (+1 shift).** Locate and increment each "Section 4.x"/"§4.x". Run first to enumerate, then edit each:
```bash
rtk grep -nE "(Section|§)\s*~?\s*4\.[0-9]+" thesis/Thesis/Chapters/ch3-LiteratureReview.tex thesis/Thesis/Chapters/ch4-ProjectAnalysis.tex thesis/Thesis/Chapters/ch5-Results.tex thesis/Thesis/Chapters/ch6-Conclusion.tex
```
Mapping: 4.1→4.2, 4.2→4.3, 4.3→4.4, 4.4→4.5, 4.5→4.6, 4.6→4.7, 4.7→4.8, 4.8→4.9, 4.9→4.10, 4.10→4.11. **Edit highest-numbered first** (4.10→4.11, then 4.9→4.10, …) to avoid double-incrementing. Leave §4.1 references that genuinely point to the new workflow as-is (there should be none pre-existing).

- [ ] **Step 4: Verify renumber.** Re-run the grep; confirm the set of referenced numbers now spans 4.2–4.11 (and the new 4.1 only where the workflow is cited). Spot-check 3 references against their intended section semantics. Stage. **No commit.**

---

### Task 4: Replace ●/— with ✓/✗ in comparison tables

**Files:**
- Modify: `thesis/Thesis/Chapters/ch4-ProjectAnalysis.tex` (Table 2, FR-mapping, ~lines 32–38)
- Audit: all chapters for other `●`/`---`-as-marker tables

**Interfaces:** none.

- [ ] **Step 1: Locate dot/dash marker cells.**
```bash
rtk grep -nE "●|&\s*---\s*(&|\\\\\\\\)" thesis/Thesis/Chapters/ch4-ProjectAnalysis.tex
```
- [ ] **Step 2: Replace markers.** In the FR-mapping table, `●` → `\checkmark` (amssymb, already loaded) and the `---` used as a "no" marker → `$\times$`. Do NOT touch `---` used as an em-dash in prose or numeric ranges — only cells that are a standalone yes/no marker. Add a one-line key under the caption if helpful: "(\checkmark\ = addresses; $\times$ = does not.)"
- [ ] **Step 3: Verify.** `rtk grep -nE "●" thesis/Thesis/Chapters/ch4-ProjectAnalysis.tex` → expect 0 in marker cells. Stage. **No commit.**

---

### Task 5: Ch.3 literature-synthesis table

**Files:**
- Modify: `thesis/Thesis/Chapters/ch3-LiteratureReview.tex` (insert before `\section{Summary}` at line 161, or at the head of §Gap Analysis)

**Interfaces:** none. Adds one numbered table (verify next free Table number — Ch.4 starts at Table 2, so a Ch.3 table is lower; confirm with `rtk grep -nE "Table [0-9]+ ---|Table~?[0-9]+" thesis/Thesis/Chapters/ch1*.tex thesis/Thesis/Chapters/ch2*.tex thesis/Thesis/Chapters/ch3*.tex`).

- [ ] **Step 1: Insert the synthesis longtable** with columns Author / Key methods / Key findings / Limitations / Future directions, rows drawn from existing Ch.3 citations. Use a `booktabs` `longtable` (consistent with the chapter's other tables). Rows:
  - `\citet{Li2010}` — LinUCB; disjoint linear UCB with confidence ellipsoid; sublinear regret on news recommendation; assumes linear reward / fixed features; → richer feature maps.
  - `\citet{Agrawal2013}` — LinTS / Thompson Sampling; posterior sampling; matches UCB regret, often better empirically; sampling cost, prior sensitivity; → scalable posteriors.
  - NeuralUCB — neural UCB; DNN reward + NTK confidence; handles non-linear reward; compute-heavy, theory under NTK; → efficient uncertainty.
  - NeuralTS — neural Thompson; DNN posterior approximation; non-linear, strong empirics; variance estimation cost; → calibrated posteriors.
  - EE-Net — separate exploration network; learns exploration directly; beats UCB/TS on some benchmarks; two-network overhead; → theory + efficiency.
  - `\citet{Lewis1994}` — PSI thresholds; population stability binning; standard drift benchmarks (0.10/0.25); heuristic cutoffs; → adaptive thresholds.
  - Algorithmic fairness in insurance — parity metrics / four-fifths; audits demographic disparity; mostly static models; → fairness under online adaptation.
  - Emerging-market underwriting — rule-based / GLM transfer; documents penetration + data gaps; not adaptive; → learning-based underwriting (this thesis).

  *(Pull exact `\citeyearpar` keys/years from the existing `\citep{...}` in ch3 §3.4 for the neural rows; if a cite key is absent, use the author-year text already present in the prose and do NOT invent a `\bibitem`.)*

- [ ] **Step 2: Add the in-text reference** (satisfies T7's rule): one sentence introducing the table in §Gap Analysis or §Summary, e.g. "Table N synthesises the works most directly related to this thesis along five dimensions."
- [ ] **Step 3: Verify.** `rtk grep -nE "synthesis|Author.*Key methods" thesis/Thesis/Chapters/ch3-LiteratureReview.tex`. Stage. **No commit.**

---

### Task 6: Citation hygiene — merge adjacent brackets

**Files:** audit all `Chapters/ch*.tex`.

**Interfaces:** none.

- [ ] **Step 1: Find adjacent citation brackets** (his p.32, p.36 "Don't cite this way"):
```bash
rtk grep -nE "\\\\cite[a-z]*\{[^}]*\}[ ~]*\\\\cite" thesis/Thesis/Chapters/ch2-Presentation.tex thesis/Thesis/Chapters/ch3-LiteratureReview.tex thesis/Thesis/Chapters/ch4-ProjectAnalysis.tex
```
- [ ] **Step 2: Merge** each `\citep{A}\citep{B}` (or with space/`~`) into `\citep{A,B}` → renders "(A, year; B, year)". Only merge when both are the *same* command family and both are parenthetical; do NOT merge a narrative `\citet`/`\citeyearpar` with a parenthetical `\citep`. For the p.36 case (two adjacent parenthetical cites), confirm by reading the line context first.
- [ ] **Step 3: Verify.** Re-run the grep → expect 0 adjacent-bracket pairs. Stage. **No commit.**

---

### Task 7: Figure/table in-text reference audit + DAC logo

**Files:**
- Modify: `thesis/Thesis/Chapters/ch1-Introduction.tex` (§1.2 — add `images/DAC.jpg`)
- Audit: all chapters for unaddressed floats (incl. SDG §2.4, new flowchart Fig 2, new lit table)

**Interfaces:** consumes the new floats from T3 (flowchart) and T5 (lit table).

- [ ] **Step 1: Add the DAC company logo** in Ch.1 §1.2.1 "General Information of Company" (line ~17) or §1.2.2 "Services of Company" (line ~23):
```latex
\begin{figure}[H]
\centering
\includegraphics[width=0.35\textwidth]{images/DAC.jpg}
\caption{Figure 1 --- Logo of Decent Actuarial Consultants (DAC).}
\label{fig:dac-logo}
\end{figure}
```
*(If "Figure 1" is the existing DAC org chart, give the logo the correct sequence number and reconcile — see T3 Step 1 note. Add an in-text sentence referencing it.)*

- [ ] **Step 2: Enumerate every float and its reference.**
```bash
rtk grep -nE "\\\\caption\{|captionof\{(table|figure)\}|\\\\fg\[" thesis/Thesis/Chapters/ch*.tex
```
For each Figure N / Table N, confirm an in-text "Figure N"/"Table N" mention exists in the same section (above or below). Add a one-sentence reference where missing. Pay special attention to: the SDG section (§2.4) floats, EDA figures, and any appendix floats.
- [ ] **Step 3: Verify.** Spot-check 5 floats have in-text references. Stage. **No commit.**

---

### Task 8: Ch.5 bold-best pass

**Files:** Modify `thesis/Thesis/Chapters/ch5-Results.tex` (Tables 9–25).

**Interfaces:** none.

- [ ] **Step 1: Admissible tables (9–21).** For each comparison table, wrap the winning admissible policy's cumulative-reward/regret cell in `\textbf{...}`. The winner is LinUCB/LinTS/HITL as the surrounding prose states. Do NOT bold header or label cells.
- [ ] **Step 2: Ceiling tables (22–25).** Bold the best *admissible* learner's cell. For the AlwaysRATED / best-constant cell (numerically highest), apply `\underline{...}` + a trailing `\textsuperscript{\dag}` and add a table note: `\dag~inadmissible constant-policy ceiling (§5.0.1)`. Never `\textbf` the constant.
- [ ] **Step 3: Verify.** `rtk grep -cE "textbf|underline|dag" thesis/Thesis/Chapters/ch5-Results.tex` increased; read Tables 23 & 24 to confirm the constant is daggered, not bolded. Stage. **No commit.**

---

### Task 9: Ch.6 §6.1 Findings → points

**Files:** Modify `thesis/Thesis/Chapters/ch6-Conclusion.tex:5-15`.

**Interfaces:** none.

- [ ] **Step 1: Convert the four `\textbf{Finding N --- …}` paragraphs (lines 7, 9, 11, 13) into an enumerated list.** Keep the intro sentence (line 5) and the closing synthesis paragraph (line 15) as prose. Each list item retains its bold lead-in and all statistics verbatim:
```latex
\begin{enumerate}[label=\textbf{Finding \arabic*.},leftmargin=*]
  \item \textbf{Bandits substantially outperform static underwriting (EXP-005).} <existing line 7 body verbatim>
  \item \textbf{Adaptive underwriting does not introduce demographic bias (EXP-006).} <line 9 body>
  \item \textbf{Online adaptive linear estimation … beats the Static XGB baseline (EXP-007, EXP-011).} <line 11 body>
  \item \textbf{Human-in-the-loop underwriting improves reward at low cost (EXP-008).} <line 13 body>
\end{enumerate}
```
*(`enumitem` is loaded in the preamble — `[label=…]` is available.)*
- [ ] **Step 2: Verify.** `rtk grep -nE "begin\{enumerate\}" thesis/Thesis/Chapters/ch6-Conclusion.tex` present in §6.1; statistics unchanged (`rtk grep -c "90,540\|85.72\|14.8" ch6`). Stage. **No commit.**

---

### Task 10: Khmer cover tweaks

**Files:** Modify `thesis/Thesis/Cover_Pages/Cover.tex`, `SubCover_KH.tex`.

**Interfaces:** none. **All edits FLAGGED for student Khmer verification.**

- [ ] **Step 1: Read both files.** Identify the Khmer rendering of "Adaptive" in the title and the term marked "no need to translate" (p.2), and the line flagged "don't let it drop below" (p.5, likely "Institute of Technology of Cambodia" wrapping/overflow).
- [ ] **Step 2: Apply** (a) the supervisor's suggested បត់បែន for "adaptive" where the current Khmer differs; (b) leave the English technical term untranslated where he marked "no need to translate"; (c) fix the p.5 layout drop (tighten line break / `\\`/`\mbox` so the flagged line does not fall below). Make minimal changes.
- [ ] **Step 3: FLAG to student** in the handoff: list each Khmer string changed and ask for confirmation (consistent with the prior `ON Radet` transliteration verification pattern). Stage. **No commit.**

---

### Task 11: Build r15 Overleaf bundle, hand off for GREEN, then commit

**Files:** none in source; produces `thesis/Thesis_overleaf_2026-06-18_r15.zip`.

- [ ] **Step 1: Structural pre-flight (local, no compile available).**
```bash
rtk grep -nE "Abstract_EN|Abstract_KH|Resume_FR" thesis/Thesis/Main_content.tex   # 0
rtk grep -nE "(Section|§)\s*~?\s*4\.1\b" thesis/Thesis/Chapters/ch4-ProjectAnalysis.tex  # workflow refs only
rtk grep -nE "^\\\\chapter\{" thesis/Thesis/Chapters/ch*.tex   # 6 sentence-case titles
```
- [ ] **Step 2: Build the bundle** with the same packer used for r14 (`%TEMP%\zip_thesis_r14.py` analog) over `thesis/Thesis/`, EXCLUDING the deleted three files and INCLUDING `Executive_Summary_KH.tex` + `images/DAC.jpg` + fonts. Confirm file count and that the three deleted files are absent.
- [ ] **Step 3: Hand off to student** with: (a) the r15 zip path; (b) the Overleaf-check list — chapter-heading rendering (T2), front-matter order + Khmer-above-English (T1), §4.1 flowchart (T3), bold/dagger ceiling tables (T8); (c) the Khmer strings to verify (T10) + Khmer Exec-Summary heading (T1); (d) confirm Ch.2 §2.3 contribution coverage if a sentence was added.
- [ ] **Step 4: AFTER student confirms Overleaf GREEN — commit** (grouped, on `thesis/ch5-structural-pass`):
```bash
rtk git add -A thesis/Thesis docs/superpowers/plans/2026-06-18-supervisor-revision-plan.md
rtk git commit -m "$(cat <<'EOF'
feat(thesis): apply supervisor (Dr. Phauk) revision pass

Front matter consolidated to one essay Executive Summary (Khmer above
English); academic Abstract_EN/KH + Resume_FR removed; keywords dropped.
Ch.4 renamed Methodology with new §4.1 workflow flowchart (+17 ref
renumber). Chapter headings -> "Chapter I." style. Ch.3 literature
synthesis table. Adjacent citations merged. Figures/tables addressed
in text + DAC logo. Ch.5 best-admissible bolded, AlwaysRATED ceiling
daggered. Ch.6 findings as points. Khmer cover tweaks.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review

**Spec coverage** (25 comments → tasks):
- Essay summary / Khmer-above-English / combine abstract+summary / drop keywords / drop French / "points belong in intro" → **T1** ✓
- Khmer OS font (p.9) → already satisfied (preamble); verified in T1/T11 ✓
- Chapter heading style (p.23, p.26) → **T2** ✓
- Ch.4 → Methodology + §4.1 workflow flowchart (p.38) → **T3** ✓
- ✓/✗ not ●/— (p.38) → **T4** ✓
- Literature synthesis table (p.37) → **T5** ✓
- Adjacent citation brackets (p.32, p.36) → **T6** ✓
- Figures/tables must be addressed (p.25) + company logo (p.24) → **T7** ✓
- Bold best performance (p.90) → **T8** ✓
- "make points" Ch.6 (p.92) → **T9** ✓
- Cover Khmer: adaptive/no-translate/layout (p.2, p.5) → **T10** ✓
- Examiner-name / "leave blank" annotations (p.4) → student's own (committee fields), NOT student-editable content; **excluded** (note in handoff).

**Placeholder scan:** flowchart TikZ, heading redef, front-matter order, Ch.6 enumerate are concrete code. Lit-table rows and prose-rewrite specify exact source lines + constraints rather than re-pasting prose (avoids drift from the live text). Audits (T6, T7) specify the exact grep + transformation rule.

**Number-consistency risks flagged for execution:** (1) next free Figure number for the flowchart + logo (T3/T7); (2) next free Table number for the lit table (T5); (3) renumber highest-first to avoid double-increment (T3). All have an enumerating grep before the edit.
