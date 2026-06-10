# Thesis Internal-Contradiction Audit — 2026-06-09

Scope: read in full — `Abstract_EN.tex`, `Executive_Summary.tex`, ch1–ch3, ch5 (all 1025 ll.), ch6.
ch4 (methodology, 785 ll.) was **cross-checked on its key parameters** against ch5 (PSI bands l.96/609–611,
EEOC 80 % l.100/652, claims noise `Uniform(0.92,1.08)` l.532, reward constants §4.7) — all consistent —
but was **not** read line-by-line. All line numbers are LaTeX source lines.

---

## Finding 1 (CENTRAL) — the "complete baseline ladder" omits the policy the reframe hinges on

**The count-it-yourself proof (no interpretation needed):**
- §5.0.1 l.15 promises the evaluation "adds a complete **baseline ladder**: a uniform-random policy, the
  **three constant policies (AlwaysSTANDARD, AlwaysRATED, AlwaysDECLINE)**, the frozen Static-XGB rule, and
  … LogisticOracle."
- §5.0.1 ll.17–21 frame **Table 9** (captioned "The baseline ladder") as "that ladder", introduced to
  answer the headline question "does a contextual bandit beat the **best simple policy** available?"
- **Table 9 (ll. 45–51) contains only ONE constant — AlwaysSTANDARD.** AlwaysRATED is absent;
  AlwaysDECLINE is absent. (`AlwaysDECLINE` occurs once in the whole chapter, at l.15, and in no table.)
- The §5.0.1 **verdict** (l.61) — "The contextual bandit beats every deployable alternative… LinUCB and
  LinTS lead the deployable-policy rankings in Table 9" — is therefore declared off a ladder that, *by
  construction*, cannot show the one simple policy (AlwaysRATED) that **does** beat the bandit.
- AlwaysRATED only appears in **Table 12** (§5.3, l.260), ranked **#1**, which is exactly what flips the
  verdict to "bandits are rank-3… beaten by AlwaysRATED" (l.288). Two tables, captioned as the same
  "baseline ladder", give opposite answers because one drops the decisive row.

**The terminology that lets the contradiction hide — `deployable` in two opposite senses:**

The word **deployable** carries two incompatible meanings, and the conflict lands exactly on the
thesis's reframed central claim.

**Sense A — "deployable" = implementable *and* admissible; AlwaysRATED is EXCLUDED:**
- §5.0.1 Table 9 (ll. 45–51) omits AlwaysRATED entirely; LinTS is labelled **"rank-1 of the deployable
  policies"** (l. 49), LinUCB **"rank-2"** (l. 48).
- §5.0.1 verdict, l. 61: **"The contextual bandit beats every deployable alternative on this problem.
  LinUCB and LinTS lead the deployable-policy rankings."**
- Figure 6 caption, l. 57: "LinUCB and LinTS lead every deployable policy."
- Executive_Summary l. 20: **"Bandits beat every deployable alternative."**
- Abstract l. 10: contribution stands "against deployable alternatives."

**Sense B — "deployable" = merely produces actions from observable features; AlwaysRATED is INCLUDED as #1:**
- §5.3 Table 12 column header (l. 246) "Rank (deployable)"; l. 260 ranks **AlwaysRATED = rank 1**,
  LinTS = 2, LinUCB = 3.
- §5.3 l. 288: **"the contextual bandits are rank-3 among deployable policies, beaten by the trivial
  AlwaysRATED constant."**
- §5.11 Table 22 / l. 937: **"AlwaysRATED is the best deployable policy in every model."**

**The clash:** "Bandits beat every deployable alternative" (l. 61 + Exec-Summary l. 20) directly
contradicts "bandits are rank-3 among deployable policies, beaten by [deployable] AlwaysRATED"
(l. 288 + l. 937). Same word, opposite verdict, same chapter. In Table 9 the bandits are the TOP
deployable policies; in Table 12 they are rank-2/3 because AlwaysRATED is counted as the #1 deployable.

**Fix (recommended):** reserve **deployable** for the technical sense (AlwaysRATED *is* deployable) and
use **admissible** / **viable** for the regulatory sense. Then the headline becomes "bandits beat every
*admissible* alternative" (true), and l. 49/48/57/61 + Exec-Summary l. 20 + Abstract l. 10 change
"deployable" → "admissible". Equivalently, add AlwaysRATED to Table 9 as a marked *inadmissible ceiling*
so §5.0.1 and §5.3 rank the same policies consistently.

---

## Finding 2 (NUMERIC, verified) — the $91,947 phantom in §5.0.1

- §5.0.1 l. 21 reconciliation: "the reimplemented reward harness reproduces the headline LinUCB reward
  to within rounding — **$91,864 here vs $91,947 in §5.3 (EXP-007)** — confirming the two pipelines agree."
- But §5.3 reports LinUCB = **$91,864** everywhere: Table 12 l. 262 and Pass/Fail l. 323.
- `$91,947` appears **nowhere else in the thesis** (grep: 1 hit, l. 21).
- So the reconciliation cites a value the section it cites never states. Either l. 21 should read
  "$91,864 … = $91,864" (and the "agree to within rounding" sentence is mis-stated), or §5.3's number
  is wrong. Pick one. As written it is an internal numeric inconsistency.

---

## Finding 3 (NUMERIC clarity) — $90,540 vs $91,864 unreconciled *inside the conclusion*

- ch6 Finding 1, l. 7: LinUCB earns **$90,540**.
- ch6 §6.2, l. 29: "LinUCB's **$91,864**."
- The ~1.4 % difference *is* explained in §5.0.1 l. 21 (EXP-005 pipeline vs CRN reward-sensitivity
  harness), but that explanation is **not** repeated in ch6. A reader of the conclusion alone sees the
  same algorithm earning two different totals four paragraphs apart.
- Fix: one-clause footnote in §6.2 — "$91,864 on the 20-seed common-random-number harness; cf. $90,540
  from EXP-005's own pipeline (§5.0.1)."

---

## Finding 4 (TABLE-INTERNAL, supports Finding 1)

Table 12 "Rank (deployable)" gives Oracle and LogisticOracle rank "—" (correctly excluded as
non-deployable) but gives **AlwaysRATED rank "1"** — inconsistent handling of three policies the thesis
elsewhere uniformly calls non-deployable/inadmissible ceilings (§5.0.1 l. 63; §6.2 l. 29).

---

## Finding 5 (SOFT — motivation vs. finding) — ch2 was not updated for the reframe

- ch2 motivates the whole project on static rules being suboptimal because they **"ignore feature
  interactions"** (l.5; §2.2.1 "Suboptimal Risk Selection", l.73; Primary Objective l.89).
- ch5 concludes the opposite about *why*: the optimal policy is **near-constant with little contextual
  structure to exploit** (§5.12 l.997; §5.7 l.589), a feature-blind constant wins, and Static XGB's real
  failure is **not updating online**, not ignoring interactions (§5.7).
- The author half-owns this in §5.3.4 (l.424: "narrower than earlier drafts claimed… 'a frozen rule
  leaves money on the table,' **not** 'deploy a contextual bandit'"), but **ch2's framing was never
  revised**. Not a hard numeric contradiction — a motivation-vs-conclusion tension worth one reconciling
  sentence in ch2.

---

## Minor / loose end

- Figure 17 caption (l. 825) names a `.png` companion file ("fig_drift_rescue_ladder_severe.png") — a
  leftover after the figure overhaul repointed all `\fg` figures to `.pdf`. Cosmetic, prose-only.

---

## Checked and CONSISTENT (no action)

- PSI bands GREEN<0.10 / AMBER 0.10–0.25 / RED>0.25; parity 85.72 % (region) / 90.12 % (occupation);
  max sliding-window PSI 0.082 / 0.123 — identical across Abstract, §5.2, ch6.
- HITL: 102,100 vs 95,872 = +6.5 %; review cost $2,625 = 75 × $35; 75/5,000 = 1.5 % — all self-consistent.
- Cross-experiment LinUCB reward $90,540 (EXP-005) vs $91,864 (CRN ladder / §5.11) — explicitly
  reconciled in §5.0.1 l. 21 (modulo Finding 2's phantom number).
- Bandit-vs-constant fractions 74–82 % (§5.11 ll. 937/962) and 77–88 % (§5.12 l. 993) match their tables.
- AlwaysRATED "97.6 % of oracle" appears only as an explicitly *superseded* figure (l. 962); live text
  uses 96.8 % (ll. 100, 962). Not a live contradiction.
- "+25 %" (Abstract/Exec/ch6) vs "+25.2 %" (ch5) is rounding of the same 90,540/72,292 gap, not a conflict.
