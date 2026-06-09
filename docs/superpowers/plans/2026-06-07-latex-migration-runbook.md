# LaTeX Migration Runbook — Health-RL Thesis

**Date:** 2026-06-07 · **Deadline:** review submission in ~2 days (≈2026-06-09)
**Origin:** `/grill-me` session, 2026-06-07. All decisions below are locked by the user.

## Decision summary
- **All-in LaTeX** this review round; **docx is the fallback** if the compile fails.
- Build on **Overleaf** (XeLaTeX) — no local TeX installed, by design.
- Content is **frozen** — port Ch.5/abstract as-is ("LinUCB/LinTS beat every *deployable* baseline, +25.2% over Static XGB; bounded by an inadmissible-constant ceiling, §6.2").
- Khmer abstract/title = **placeholder** this round; commission real translation before final.

## Working locations
- **Project (edit here):** `thesis/Thesis/`
- **Pristine template backup:** `thesis/Thesis_template_backup/`
- **Source content (markdown):** `thesis/health_rl/chapter0{1..6}_*.md`
- **Reusable front matter + bib + lists:** `thesis/health_rl/build_thesis_docx.py`

## Locked technical decisions
- **6 chapters** (template has 5) → edit the `\input` lines in `Main_content.tex`.
  Mapping: ch1 Introduction · ch2 Presentation · ch3 Literature Review · ch4 Project Analysis (methodology) · ch5 Results & Discussion · ch6 Conclusion.
- **Drop `minted`** (no code blocks anywhere) → no shell-escape/Pygments needed.
- **`apacite` + `natbib`** author-year (already in template). `reference.bib` rebuilt ✅.
- **Native LaTeX math** (markdown already has `$$…$$` source).
- **Auto-number** figures/tables/equations via LaTeX counters; strip manual "Figure 2.1." prefixes from captions.
- Figures: PNG via `\fg{width}{caption}{path}` (macro already in `Main_content.tex`).

## Risk-ordered phases
**Phase 0 — Spike (prove the toolchain) ← do FIRST.** Minimal compilable project: `Main_content.tex` (6-ch wiring, minted removed) + new `reference.bib` + 3 Khmer `.ttf` fonts + ONE converted chapter (Ch.4) + stubs for the rest + reused front matter. User uploads to Overleaf, compiler = XeLaTeX, compiles. Fix font/package/bib errors while the surface is small.
**Phase 1 — Batch convert body** (Ch.1,2,3,5,6) via Pandoc → hand-fix (gotchas below).
**Phase 2 — Front matter + cover pages.** Rewrite 4 cover pages (KH/FR/EN subcovers + main) with user identity facts; reuse EN abstract + acknowledgement; Khmer abstract placeholder; abbreviations/lists.
**Phase 3 — Polish vs professor's checklist.** Citation key ↔ reference cross-check; caption consistency; TOC depth; figure resolution/alignment; equation numbering; page numbering (roman front / arabic body — template already does this); spell/grammar. Final compile → PDF → submit.

## Conversion gotchas (apply per chapter)
1. **Currency `$`**: escape bare `$<digit>` → `\$` (43 in Ch.5 alone). Post-process after Pandoc.
2. **`[FIGURE: path — caption]`** → `\fg{0.8\textwidth}{caption}{images/<file>}`; strip "Figure N.N." prefix.
3. **`[@key]` / `[@key:n]`** → `\citep{key}` / `\citet{key}` (Pandoc `--natbib` does most; verify narrative `:n`).
4. **Tables**: Pandoc handles simple ones; multirow/CI tables (Ch.4–5) need hand-fix with `booktabs`/`tabularx`.
5. Em/en dashes, smart quotes, `&`, `%`, `_`, `#` → LaTeX-safe.
6. Known template bug to fix: `\addcontentsline{toc}{Chapters}{\bibname}` → second arg should be `chapter`.

## Bibliography status ✅
- 25 entries written to `reference.bib` from `_BIB_SOURCES`. 21/22 used keys covered.
- **`@dac`** placeholder added — CONFIRM details with user.
- Uncited extras (ILO2022, MAFF2022, SwissRe2023, WorldBank2023) won't print (natbib) — OK.

## Reusable front-matter data (in `build_thesis_docx.py`)
EN abstract ≈ L1090–1102 · Acknowledgement ≈ L1056–1071 · FIGURES L399 · TABLES L417 · ABBREVIATIONS L439.

## Pending user inputs (cover pages — Phase 2, NOT blocking body)
1. Full name (EN + Khmer) · 2. Student ID · 3. Cover supervisor (Has Sothea? + Chris & Peter? role of Phauk Sokkhey?) · 4. Submission month + AY · 5. What is `[@dac]`? · 6. Degree + specialty.

## Fonts to upload to Overleaf
Khmer OS Battambang, Khmer OS Muol Light, Khmer OS Siemreap (loaded by `fontspec`). Source: `C:\Windows\Fonts` or Khmer OS / Google Noto Khmer download.

## Build tooling created
- `thesis/Thesis/convert.py` — Pandoc wrapper + post-processing (run from repo root: `python thesis/Thesis/convert.py`). Transforms: currency-`$` escaping (math-safe), `[FIGURE]`→`\fg` (manual numbers kept), heading-number strip, `[@k:n]`→`\citeyearpar`, bold `Table X.Y`→`\captionof{table}` (safe, LoT-enabled).
- `thesis/Thesis/preflight.py` — static checks (brace balance, caption placement, missing images, leftover placeholders). Re-run after every `convert.py`.

## Numbering decision (IMPORTANT)
Document uses **manual** figure/table numbers (e.g. "Figure 5.6", "Table 5.3.1") that the prose references and that are non-sequential (gaps, section-style). So: `\captionsetup[figure/table]{labelformat=empty}` hides LaTeX's auto-label; the manual number lives in the caption text; `\caption`/`\captionof` still populate `\listoffigures`/`\listoftables`. Do NOT switch to auto-numbering without fixing every in-text ref.

## DONE (2026-06-07)
- Template backed up → `thesis/Thesis_template_backup/`.
- `reference.bib` rebuilt (26 entries; `@dac` is a TODO placeholder).
- All 6 chapters converted → `Chapters/ch{1..6}-*.tex`; stale fraud chapters deleted.
- 39 figures copied → `images/`; 18 referenced, all present.
- `Main_content.tex`: 6-chapter wiring; `minted` removed; bib TOC bug fixed; `newunicodechar` glyph fallbacks; `labelformat=empty`; `List_figure`/`List_table` case fixed (Overleaf is case-sensitive); fonts bundled.
- **Fonts bundled** → `thesis/Thesis/fonts/` (Times ×4 + 3 Khmer OS); font block loads them by `Path=./fonts/` so Overleaf compiles.
- Front matter reused: `Abstract_EN.tex`, `Acknowledgement.tex` (health-RL); `appendices.tex` rewritten (fraud `lstlisting` removed).
- Pre-flight: PASS (braces ok, figs present, no leftover placeholders). 21/27 tables captioned into LoT.

## PENDING (needs user input or polish — NOT compile-blocking)
1. **Cover pages** `Cover.tex`, `SubCover_{EN,FR,KH}.tex` still show the template student (LY SOKPHENG / fraud thesis). Need: full name (EN+KH), student ID, supervisor, year, degree → then rewrite.
2. **`Abstract_KH.tex`** still the template's Khmer — replace with placeholder, real Khmer for final.
3. **`List_abreviation.tex`** still fraud abbreviations — repopulate from `ABBREVIATIONS` in `build_thesis_docx.py` (AMS, LinUCB, LinTS, PSI, RL, XGB, …).
4. **`@dac`** bib entry — confirm what `[@dac]` refers to.
5. Confirm advisor name (Has Sothea vs Phauk Sokkhey) on cover/acknowledgement.
6. 6 tables (ch1, ch2) not auto-captioned — verify/каption manually if needed.

## NEXT ACTION = first Overleaf compile (the real test)
User uploads `thesis/Thesis_overleaf.zip` → Overleaf → **Menu → Compiler → XeLaTeX** → Recompile. Fonts are bundled, so it should build. Iterate on any errors (likely apacite/natbib or a stray glyph), then do PENDING items.

## Progress log
- 2026-06-07: grill complete; full body conversion done; project self-contained + pre-flight PASS; packaged for Overleaf. NEXT = user's first XeLaTeX compile + PENDING front-matter items.
