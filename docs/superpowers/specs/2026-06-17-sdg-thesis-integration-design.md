# Design — Integrating Cambodia's SDGs into the Thesis (new §2.4)

**Date:** 2026-06-17
**Branch:** `thesis/ch5-structural-pass`
**Status:** Approved (brainstorming). Next: writing-plans.

## Background & motivation

The defense deck gained an Introduction panel framing the work as a *contribution toward*
Cambodia's SDGs (SDG 3 / 1 / 10), softened this session from "ALIGNMENT" to "CONTRIBUTION
TOWARD" precisely because **the thesis names no SDGs anywhere**. To let the deck's claim stand
under examination — and to add genuine scholarly framing — the thesis should itself discuss the
SDGs. The user chose a **dedicated, cited subsection** (over a one-liner or a framing-only
paragraph).

This is the **thesis** workstream (Overleaf/XeLaTeX, currently at r13, GREEN, closed). It is
separate from the defense-deck commit `8ea8852` shipped earlier today.

## Goal

Add one new cited section to `ch2-Presentation.tex` that situates the project within Cambodia's
Sustainable Development Goals, synthesizing motivation **already present** in the thesis (the
coverage/penetration gap in §2.1; the garment-worker/rice-farmer fairness argument in §2.2.3)
under the SDG umbrella — **introducing no new empirical claims** and **claiming no measured SDG
impact**.

## Non-goals / out of scope

- No new experiments, results, or metrics. The thesis evaluates **no** SDG indicators.
- No edits to the verbatim-locked §2.2 Problematic / §2.3 Objective (O1–O4, RQ1–4) content.
- No fix here for the ch4 "four categories" Table-7 bug (tracked separately).
- The deck "CONTRIBUTION TOWARD" → "ALIGNMENT WITH" change is a **follow-up**, gated on r14
  compiling green (see below).

## Design

### Placement & structure

New `\section{Significance and Alignment with Cambodia's Sustainable Development Goals}` inserted
in `ch2-Presentation.tex` **after §2.3 Objective, before Planning** (Planning becomes §2.5).

Shape: intro ¶ → SDG 3 ¶ → SDG 1 ¶ → SDG 10 ¶ → honesty-caveat ¶. Matches ch2's existing
academic register and `\citep{}` style.

### Draft content (for review — implementation may refine wording)

> **Intro.** Beyond its immediate actuarial contribution, this project speaks to Cambodia's
> broader development agenda. In 2015 the Royal Government endorsed the United Nations 2030
> Agenda for Sustainable Development \citep{UN2015}, and in 2018 adopted a localized framework —
> the Cambodian Sustainable Development Goals (CSDGs) 2016–2030 \citep{RGC2018} — adapting the
> global goals to national priorities and feeding the National Strategic Development Plan. An
> adaptive, fairness-aware health-insurance underwriting system contributes, in distinct ways, to
> three of these goals: good health and well-being (SDG 3), no poverty (SDG 1), and reduced
> inequalities (SDG 10).
>
> **SDG 3 — Good Health and Well-being.** Target 3.8 calls for universal health coverage,
> including financial-risk protection \citep{WHO2023}. In Cambodia, mandatory coverage through the
> National Social Security Fund reaches mainly formal-sector workers, leaving informal workers,
> farmers, and the self-employed largely without health insurance \citep{ILO2022}. By making
> private voluntary underwriting more accurate and adaptive — and deployable over the country's
> near-universal mobile infrastructure — the framework lowers the cost of extending voluntary
> coverage to under-served segments, advancing SDG 3.8's financial-protection objective.
>
> **SDG 1 — No Poverty.** Out-of-pocket health payments are a documented driver of impoverishment:
> globally, catastrophic spending (out-of-pocket costs exceeding ten percent of a household
> budget) affects roughly one in seven people and pushes or deepens poverty for over a billion
> \citep{WHO2023}. Where insurance penetration is low, a single hospitalization can exhaust a
> household's savings. Broadening access to affordable risk pooling helps shield Cambodian
> households from catastrophic medical expenditure, supporting SDG 1's social-protection target
> (1.3).
>
> **SDG 10 — Reduced Inequalities.** Unmonitored algorithmic underwriting risks entrenching
> demographic exclusion. The Population Stability Index guardrails over region and occupation
> developed in this thesis (§\ref{fairness-and-demographic-parity}) are designed to prevent the
> systematic decline of vulnerable segments — including the country's large garment-sector and
> rural agricultural workforces \citep{ILO2022} — by holding algorithmic profitability to an
> explicit demographic-parity standard, supporting SDG 10's aim of economic inclusion regardless
> of occupation or status.
>
> **Scope caveat.** This study does not measure SDG indicators directly; no health, poverty, or
> inequality outcome is evaluated empirically. The alignment above is the project's *intended
> societal contribution*, grounded in the access and fairness motivations of this chapter rather
> than an impact evaluation — measured SDG impact would require the field deployment identified as
> future work in Chapter VI.

### Penetration-metric correctness

§2.1 states insurance penetration "below two percent" (premium/GDP, Swiss Re); the deck states
health-insurance population coverage "<10%" — **different metrics**. §2.4 frames SDG 3 around the
**coverage gap qualitatively** (NSSF/informal-sector exclusion) and asserts **no conflicting
percentage**, so it cannot contradict §2.1. (Deck-vs-thesis metric labeling is a separate,
untouched matter.)

### Citations

**3 new `reference.bib` entries** (web-verified 2026-06-17; keys follow the `AuthorYear`
convention; confirmed no collision with existing keys):

| Key | Entry |
|-----|-------|
| `UN2015` | United Nations General Assembly. (2015). *Transforming our world: the 2030 Agenda for Sustainable Development* (A/RES/70/1). New York: United Nations. |
| `RGC2018` | Royal Government of Cambodia, National Council for Sustainable Development. (2018). *Cambodian Sustainable Development Goals (CSDGs) Framework 2016–2030*. Phnom Penh. |
| `WHO2023` | World Health Organization & World Bank. (2023). *Tracking Universal Health Coverage: 2023 Global Monitoring Report*. Geneva: WHO. ISBN 978-92-4-008037-9. |

**Reuse (already in `reference.bib`, no new entries):** `ILO2022` (informal-sector/garment
workforce); optionally `SwissRe2023` / `WorldBank2023` / `NIS2023` as supporting if needed.
Note: do **not** attach a citation to a specific headcount the cited source does not support;
the garment/rice-farmer figures live (uncited) in §2.2.3 and are cross-referenced, not re-cited.

## Verification (Overleaf-only constraint)

- **Local (Claude):** grep-confirm every `\citep` key in the new section resolves to a
  `reference.bib` entry; confirm existing ch2 `\citep{Li2010}`/`{Agrawal2013}` still resolve;
  confirm the 3 new keys are unique. No local XeLaTeX exists.
- **Compile (user):** runs on Overleaf → this is thesis **r14**. Claude will **not** claim the
  compile is done; success = user confirms r14 GREEN (0 errors, refs resolve, §2.4 renders, no
  "??" undefined citations).

## Files touched (2)

- `thesis/Thesis/Chapters/ch2-Presentation.tex` — new §2.4 + Planning renumber to §2.5.
- `thesis/Thesis/Chapters/reference.bib` — 3 new entries.

## Commit discipline

Own commit on `thesis/ch5-structural-pass`, **explicit paths only** (`ch2-Presentation.tex`,
`reference.bib`) — not bundled with deck work. Trailer
`Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.

## Follow-up (authorized, gated)

After the user confirms **r14 GREEN on Overleaf**: change the deck Introduction panel header from
"CONTRIBUTION TOWARD CAMBODIA'S SDGs" → "ALIGNMENT WITH CAMBODIA'S SDGs" in
`build_burgundy_presentation.py`, rebuild, eyeball idx4, and commit. Separate, later task.

## Success criteria

1. New cited §2.4 present in `ch2-Presentation.tex` with the 4-paragraph + caveat structure.
2. 3 new accurate `reference.bib` entries; all `\citep` keys resolve (local grep).
3. No edits to locked §2.2/§2.3; Planning correctly renumbered to §2.5.
4. No contradiction with §2.1's penetration figure.
5. User confirms **r14 GREEN** on Overleaf.
