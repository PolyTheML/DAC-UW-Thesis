# SDG Thesis Integration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a dedicated, cited section "Significance and Alignment with Cambodia's Sustainable Development Goals" as ch2 §2.4 of the thesis, backed by 3 new verified bibliography entries.

**Architecture:** Two-file change to the LaTeX thesis. Insert one `\section` into `ch2-Presentation.tex` between §2.3 Objective and §2.4 Planning (LaTeX auto-renumbers Planning to §2.5). Add 3 `@techreport` entries to `reference.bib`. The section reuses an existing label cross-reference and existing Cambodia-source citations; it makes no new empirical claim.

**Tech Stack:** LaTeX (XeLaTeX), BibTeX. **No local LaTeX toolchain exists** — the thesis compiles only on Overleaf. All local verification is grep/git-based; the compile is the user's.

## Global Constraints

- **Compile is Overleaf-only.** Do NOT attempt a local `xelatex`/`pdflatex`/`latexmk`. Local verification = grep + git diff. Final compile (thesis **r14 GREEN**) is the user's; never claim the compile passed.
- **Do NOT touch the locked content** of §2.2 Problematic or §2.3 Objective (O1–O4, RQ1–4). The only ch2 change is a pure insertion before `\section{Planning of Project}`.
- **Single commit, explicit paths only:** `thesis/Thesis/Chapters/ch2-Presentation.tex` and `thesis/Thesis/Chapters/reference.bib`. Never `git add .`/`-A` (the tree has many unrelated dirty files).
- **No measured-impact claims.** The section frames the work as *intended societal contribution*; the scope-caveat paragraph is mandatory and must not be dropped.
- **.bib comments:** never put an `@` in a comment line (BibTeX would misparse it). Corporate authors use double braces `{{...}}`; en-dashes are `--`.
- Commit trailer: `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.

## File Structure

| File | Responsibility | Change |
|------|----------------|--------|
| `thesis/Thesis/Chapters/reference.bib` | Bibliography database | Add `UN2015`, `RGC2018`, `WHO2023` (`@techreport`) |
| `thesis/Thesis/Chapters/ch2-Presentation.tex` | Project-presentation chapter | Insert new §2.4 section before Planning |

---

### Task 1: Add the 3 SDG-policy bibliography entries

**Files:**
- Modify: `thesis/Thesis/Chapters/reference.bib` (append after the existing `@techreport` block, before or after `@misc{dac,...}` — anywhere at top level is fine)

**Interfaces:**
- Produces: BibTeX keys `UN2015`, `RGC2018`, `WHO2023` — consumed by the `\citep{}` calls in Task 2.

- [ ] **Step 1: Verify the keys don't already exist (must print nothing)**

Run:
```bash
grep -nE "^@\w+\{(UN2015|RGC2018|WHO2023)," thesis/Thesis/Chapters/reference.bib
```
Expected: no output (keys are free; confirmed unique on 2026-06-17).

- [ ] **Step 2: Append the 3 entries**

Add this block to `thesis/Thesis/Chapters/reference.bib` (top level, e.g. immediately after the `@techreport{WorldBank2023 ...}` entry, lines ~221):

```bibtex
@techreport{UN2015,
  author      = {{United Nations General Assembly}},
  title       = {Transforming our world: The 2030 Agenda for Sustainable Development},
  institution = {United Nations},
  address     = {New York},
  number      = {A/RES/70/1},
  year        = {2015}
}

@techreport{RGC2018,
  author      = {{Royal Government of Cambodia, National Council for Sustainable Development}},
  title       = {Cambodian Sustainable Development Goals (CSDGs) Framework 2016--2030},
  institution = {Royal Government of Cambodia},
  address     = {Phnom Penh},
  year        = {2018}
}

@techreport{WHO2023,
  author      = {{World Health Organization and World Bank}},
  title       = {Tracking Universal Health Coverage: 2023 Global Monitoring Report},
  institution = {World Health Organization},
  address     = {Geneva},
  year        = {2023}
}
```

- [ ] **Step 3: Verify the 3 entries are present exactly once each**

Run:
```bash
grep -cE "^@techreport\{(UN2015|RGC2018|WHO2023)," thesis/Thesis/Chapters/reference.bib
```
Expected: `3`

- [ ] **Step 4: Do NOT commit yet** — the single commit lands at the end of Task 2 (both files together).

---

### Task 2: Insert the §2.4 section and commit both files

**Files:**
- Modify: `thesis/Thesis/Chapters/ch2-Presentation.tex` (insert before `\section{Planning of Project}\label{planning-of-project}`, currently line ~118)
- Commit: both `ch2-Presentation.tex` and `reference.bib`

**Interfaces:**
- Consumes: BibTeX keys `UN2015`, `RGC2018`, `WHO2023` (Task 1) and existing keys `ILO2022`; existing label `fairness-and-demographic-parity` (defined at §2.2.3).
- Produces: section label `significance-and-sdg-alignment`.

- [ ] **Step 1: Confirm the insertion anchor exists (must print one line)**

Run:
```bash
grep -n '\\section{Planning of Project}\\label{planning-of-project}' thesis/Thesis/Chapters/ch2-Presentation.tex
```
Expected: one match (~line 118).

- [ ] **Step 2: Confirm the cross-ref label target exists (must print one line)**

Run:
```bash
grep -n '\\label{fairness-and-demographic-parity}' thesis/Thesis/Chapters/ch2-Presentation.tex
```
Expected: one match (the §2.2.3 subsection). If absent, STOP — the cross-reference would dangle.

- [ ] **Step 3: Insert the new section**

Insert the following block immediately **before** the line `\section{Planning of Project}\label{planning-of-project}` (use an exact-match Edit: `old_string` = that `\section{Planning...}` line; `new_string` = the block below + a blank line + that same `\section{Planning...}` line):

```latex
\section{Significance and Alignment with Cambodia's Sustainable Development Goals}\label{significance-and-sdg-alignment}

Beyond its immediate actuarial contribution, this project speaks to Cambodia's broader development agenda. In 2015 the Royal Government endorsed the United Nations 2030 Agenda for Sustainable Development \citep{UN2015}, and in 2018 it adopted a localized framework --- the Cambodian Sustainable Development Goals (CSDGs) 2016--2030 \citep{RGC2018} --- that adapts the global goals to national priorities and feeds the National Strategic Development Plan. An adaptive, fairness-aware health insurance underwriting system contributes, in distinct ways, to three of these goals: good health and well-being (SDG~3), no poverty (SDG~1), and reduced inequalities (SDG~10).

\textbf{SDG~3 --- Good Health and Well-being.} Target 3.8 calls for universal health coverage, including financial-risk protection and access to quality essential services \citep{WHO2023}. In Cambodia, mandatory coverage through the National Social Security Fund reaches mainly formal-sector workers, leaving informal workers, farmers, and the self-employed largely without health insurance \citep{ILO2022}. By making private voluntary underwriting more accurate and adaptive --- and by targeting low-latency decisions deployable over the country's near-universal mobile infrastructure --- the proposed framework lowers the operational cost of extending voluntary health coverage to these under-served segments, advancing the financial-protection objective at the heart of SDG~3.8.

\textbf{SDG~1 --- No Poverty.} Out-of-pocket health payments are a well-documented driver of impoverishment: globally, catastrophic health spending --- out-of-pocket costs exceeding ten percent of a household budget --- affects roughly one in seven people, and such payments push or deepen poverty for well over a billion individuals \citep{WHO2023}. Where insurance penetration is low, a single hospitalization can exhaust a household's savings. By broadening access to affordable risk pooling, adaptive underwriting helps shield Cambodian households from catastrophic medical expenditure, directly supporting the social-protection target (1.3) of SDG~1.

\textbf{SDG~10 --- Reduced Inequalities.} Algorithmic underwriting carries a risk of entrenching demographic exclusion if left unmonitored. The fairness-monitoring framework developed in this thesis --- Population Stability Index guardrails over region and occupation (\S\ref{fairness-and-demographic-parity}) --- is designed precisely to prevent the systematic decline of vulnerable segments such as the country's garment-sector and rural agricultural workforces \citep{ILO2022}. By holding algorithmic profitability to an explicit demographic-parity standard, the system supports SDG~10's aim of economic inclusion irrespective of occupation or economic status.

This study does not measure SDG indicators directly; no health, poverty, or inequality outcome is evaluated empirically. The alignment described here is articulated as the project's \emph{intended societal contribution}, grounded in the access and fairness motivations developed throughout this chapter rather than in an impact evaluation. Establishing measured SDG impact would require the field deployment and longitudinal outcome data identified as future work in Chapter~VI.
```

- [ ] **Step 4: Verify the section was inserted and Planning still follows it**

Run:
```bash
grep -nE '\\section\{(Significance and Alignment|Planning of Project)' thesis/Thesis/Chapters/ch2-Presentation.tex
```
Expected: two lines — `Significance and Alignment...` appears **before** `Planning of Project`.

- [ ] **Step 5: Verify every `\citep` key in the new section resolves in reference.bib**

Run:
```bash
for k in UN2015 RGC2018 WHO2023 ILO2022; do
  printf "%-10s " "$k"; grep -qE "^@\w+\{$k," thesis/Thesis/Chapters/reference.bib && echo OK || echo MISSING
done
```
Expected: all four print `OK`.

- [ ] **Step 6: Verify the locked sections are untouched (diff is a pure insertion)**

Run:
```bash
git diff --stat -- thesis/Thesis/Chapters/ch2-Presentation.tex
git diff -- thesis/Thesis/Chapters/ch2-Presentation.tex | grep -E '^-' | grep -v '^---'
```
Expected: the stat shows only insertions (e.g. `+N` lines, `-0`); the second command prints **nothing** (no deleted lines → §2.2/§2.3 and all prior content untouched).

- [ ] **Step 7: Commit both files (single commit, explicit paths)**

```bash
git add -- thesis/Thesis/Chapters/ch2-Presentation.tex thesis/Thesis/Chapters/reference.bib
git commit -F - <<'EOF'
feat(thesis): add ch2 §2.4 Significance & Cambodia SDG alignment

New cited section after §2.3 Objective framing the work as contribution toward
SDG 3 (UHC/financial protection), SDG 1 (medical impoverishment), and SDG 10
(demographic-parity via PSI). Synthesizes existing motivation; claims no measured
SDG impact (explicit scope caveat). Adds 3 verified bib entries: UN2015 (2030
Agenda A/RES/70/1), RGC2018 (Cambodian SDG Framework 2016-2030), WHO2023 (UHC
2023 Global Monitoring Report); reuses ILO2022. Planning auto-renumbers to §2.5.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
git log -1 --oneline
```

- [ ] **Step 8: Hand the compile back to the user (do NOT claim done)**

State to the user: the edits are committed; **they must compile on Overleaf** and confirm thesis **r14 is GREEN** — specifically: 0 errors, §2.4 renders after §2.3 with Planning as §2.5, and the bibliography shows the 3 new references with **no `[?]`/"undefined citation"** warnings for `UN2015`/`RGC2018`/`WHO2023`. Push only if the user asks.

---

## Follow-up (separate task, gated — NOT part of this plan's commit)

After the user confirms **r14 GREEN on Overleaf**, harden the defense deck: in `thesis/health_rl/build_burgundy_presentation.py`, change the Introduction panel header `"CONTRIBUTION TOWARD CAMBODIA'S SDGs"` → `"ALIGNMENT WITH CAMBODIA'S SDGs"` (now backed by §2.4), rebuild, eyeball idx4 (watch header wrap), run `pytest tests/test_build_presentation.py`, and commit the builder + rebuilt pptx. User pre-authorized this on 2026-06-17.

## Self-Review

- **Spec coverage:** placement (§2.4 after Objective) ✓ Task 2 Step 3; 3 verified bib entries ✓ Task 1; reuse ILO2022 ✓; penetration-metric (qualitative, no conflicting %) ✓ prose makes no numeric penetration claim; scope caveat ✓ mandatory paragraph; grep-only local verification ✓ Steps; single commit explicit paths ✓ Task 2 Step 7; deck-hardening follow-up ✓ gated section. All spec success criteria mapped.
- **Placeholder scan:** none — full LaTeX, full bib entries, exact grep commands with expected output.
- **Type/name consistency:** keys `UN2015`/`RGC2018`/`WHO2023` defined in Task 1 and consumed verbatim in Task 2; label `fairness-and-demographic-parity` checked-before-use (Step 2); produced label `significance-and-sdg-alignment` matches the file's kebab-case label convention.
