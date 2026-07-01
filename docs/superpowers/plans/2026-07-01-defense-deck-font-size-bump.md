# Defense Deck Font-Size Bump Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Increase body-text font sizes across all 44 slides of `thesis/health_rl/build_defense_v3.py` by a modest, tiered amount (~2-3pt) so the committee can read them more easily, without touching already-large text (titles, big stat numbers) and without introducing text overflow.

**Architecture:** A one-off AST-based transform script patches every font-size literal in `build_defense_v3.py` at its exact source offset (not by re-serializing the file), so formatting and comments elsewhere are untouched. It covers two distinct call-site patterns found in the file: (1) the `para()`/`new_para()`/`add_run()` helper calls (size = 3rd positional arg) and `card(..., header_size=N, body_size=N)` keyword args, and (2) raw python-pptx `<run>.font.size = Pt(N)` assignments used directly in every table-rendering block (including a couple of `Pt(N if cond else M)` ternaries). `defense_draw.py`'s `card()` function defaults get a matching one-line edit. A second one-off script re-opens the *rebuilt* `.pptx` and heuristically flags any text shape whose estimated wrapped-text height now exceeds its box — there is no PowerPoint/LibreOffice renderer in this environment, so this heuristic (not a visual render) is the verification method.

**Tech Stack:** Python, `ast` (stdlib), `python-pptx`.

## Global Constraints

- Tiered mapping (from the spec) — apply to every matched font-size literal:
  - 8pt → 11pt, 9pt → 12pt, 10pt → 13pt (below-10 sizes get +3)
  - 11pt → 13pt, 12pt → 14pt, 13pt → 15pt, 14pt → 16pt (11-14 sizes get +2)
  - ≥15pt → unchanged
- Do NOT touch: the footer ribbon (`defense_draw.py`'s `footer()`, always 9pt), `title_block()` (26pt), `section_divider()`'s numeral/section-name text (48pt/28pt) and its own footer block (9pt), or any literal ≥15pt in `build_defense_v3.py`.
- Do NOT touch paragraph-spacing `Pt()` calls (`p.space_before = Pt(10)` at `build_defense_v3.py:175` and `p.space_before = Pt(8)` at `build_defense_v3.py:714`) — these are spacing, not font size.
- `card()`'s defaults in `defense_draw.py:131` (`header_size=14, body_size=11`) must become `header_size=16, body_size=13` — 9 of the deck's 10 `card()` calls rely on these defaults rather than passing an explicit size.
- Per the user's explicit decision (2026-07-01): apply the bump across the *full current working-tree state* of `build_defense_v3.py`, including whatever other pending, previously-uncommitted work is already sitting in that file (a new Appendix A6 slide, deck-wide footer-total renumbering, etc.) — do not attempt to isolate this task's diff from that other content this time; some of it is genuinely inseparable (e.g. a font-size literal living inside a slide that only exists as pending, uncommitted new code). The commit message must fully and honestly disclose everything the commit contains, not just this task's font-size contribution. Do not sweep in unrelated *other files* (e.g. `generate_defense_script_v2.py`, deleted thumbnail PNGs) that aren't entangled with `build_defense_v3.py`'s font-size literals.
- No layout/positioning changes beyond what's needed to resolve a checker-flagged overflow risk — no general slide redesign.

---

### Task 1: Bump font sizes deck-wide, verify, commit

**Files:**
- Modify: `thesis/health_rl/defense_draw.py:131` (`card()` function defaults)
- Modify: `thesis/health_rl/build_defense_v3.py` (font-size literals throughout, via script)
- Create (one-off, not committed): `C:\Users\TRC\AppData\Local\Temp\claude\C--dac-uw-thesis\d58662c3-40e7-49c7-8376-725242b9734f\scratchpad\bump_font_sizes.py`
- Create (one-off, not committed): `C:\Users\TRC\AppData\Local\Temp\claude\C--dac-uw-thesis\d58662c3-40e7-49c7-8376-725242b9734f\scratchpad\check_text_overflow.py`
- Regenerate: `thesis/health_rl/Poly_defense_presentation_v3.pptx`

**Interfaces:**
- Consumes: `defense_draw.py`'s `card(slide, l, t, w, h, header=None, body_lines=None, bg=LIGHT_BG, accent=NAVY, header_size=14, body_size=11)` signature (to be changed to `header_size=16, body_size=13`); `para(tf, text, size, ...)`, `new_para(tf, text, size, ...)`, `add_run(para, text, size, ...)` signatures (size = 3rd positional arg, unchanged by this task).
- Produces: no new names — this task only changes numeric literal values, not any function signature consumed elsewhere.

- [ ] **Step 1: Update `card()`'s defaults in `defense_draw.py`**

In `thesis/health_rl/defense_draw.py`, change line 131 from:
```python
def card(slide, l, t, w, h, header=None, body_lines=None,
         bg=LIGHT_BG, accent=NAVY, header_size=14, body_size=11):
```
to:
```python
def card(slide, l, t, w, h, header=None, body_lines=None,
         bg=LIGHT_BG, accent=NAVY, header_size=16, body_size=13):
```

- [ ] **Step 2: Write the font-size transform script**

Create `C:\Users\TRC\AppData\Local\Temp\claude\C--dac-uw-thesis\d58662c3-40e7-49c7-8376-725242b9734f\scratchpad\bump_font_sizes.py`:

```python
"""One-off AST-based transform: bump font-size literals in build_defense_v3.py
per the tiered mapping in docs/superpowers/specs/2026-07-01-defense-deck-font-size-bump.md.
Patches by exact source offset (does not re-serialize the AST), so all
formatting/comments outside the touched numeric literals are preserved
byte-for-byte. One-off tool, not committed.
"""
import ast

MAPPING = {8: 11, 9: 12, 10: 13, 11: 13, 12: 14, 13: 15, 14: 16}
SRC_PATH = r"C:\dac-uw-thesis\thesis\health_rl\build_defense_v3.py"


def bump(n):
    return MAPPING.get(n, n)


def main():
    src = open(SRC_PATH, encoding="utf-8").read()
    tree = ast.parse(src)

    lines = src.splitlines(keepends=True)
    line_start_offsets = [0]
    for line in lines:
        line_start_offsets.append(line_start_offsets[-1] + len(line))

    def offset(lineno, col):
        return line_start_offsets[lineno - 1] + col

    patches = []      # (start, end, old_value, new_value)
    skipped = []       # (lineno, description) for anything that looked relevant but wasn't a plain int constant

    def maybe_patch_constant(node, context):
        if node is None:
            return
        if isinstance(node, ast.Constant) and isinstance(node.value, int) and not isinstance(node.value, bool):
            old = node.value
            new = bump(old)
            if new != old:
                start = offset(node.lineno, node.col_offset)
                end = offset(node.end_lineno, node.end_col_offset)
                patches.append((start, end, old, new))
        else:
            skipped.append((getattr(node, "lineno", "?"), context))

    class CallVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            fname = node.func.id if isinstance(node.func, ast.Name) else None

            if fname in ("para", "new_para", "add_run") and len(node.args) >= 3:
                maybe_patch_constant(node.args[2], f"{fname}() size arg")

            if fname == "card":
                for kw in node.keywords:
                    if kw.arg in ("header_size", "body_size"):
                        maybe_patch_constant(kw.value, f"card() {kw.arg}")

            self.generic_visit(node)

    class RunSizeVisitor(ast.NodeVisitor):
        """Matches `<expr>.font.size = Pt(N)` and `Pt(N if cond else M)`."""
        def visit_Assign(self, node):
            for target in node.targets:
                is_font_size = (
                    isinstance(target, ast.Attribute) and target.attr == "size"
                    and isinstance(target.value, ast.Attribute) and target.value.attr == "font"
                )
                if not is_font_size:
                    continue
                val = node.value
                if not (isinstance(val, ast.Call) and isinstance(val.func, ast.Name)
                        and val.func.id == "Pt" and len(val.args) == 1):
                    continue
                arg = val.args[0]
                if isinstance(arg, ast.IfExp):
                    maybe_patch_constant(arg.body, "font.size = Pt(ternary then-branch)")
                    maybe_patch_constant(arg.orelse, "font.size = Pt(ternary else-branch)")
                else:
                    maybe_patch_constant(arg, "font.size = Pt(...)")
            self.generic_visit(node)

    CallVisitor().visit(tree)
    RunSizeVisitor().visit(tree)

    patches.sort(key=lambda p: p[0], reverse=True)
    new_src = src
    for start, end, old, new in patches:
        assert new_src[start:end] == str(old), (
            f"offset mismatch: expected {old!r} at [{start}:{end}], found {new_src[start:end]!r}")
        new_src = new_src[:start] + str(new) + new_src[end:]

    open(SRC_PATH, "w", encoding="utf-8").write(new_src)

    from collections import Counter
    by_old = Counter(old for _, _, old, _ in patches)
    print(f"Applied {len(patches)} patch(es):")
    for old in sorted(by_old):
        print(f"  {old}pt -> {bump(old)}pt: {by_old[old]} site(s)")
    if skipped:
        print(f"\n{len(skipped)} candidate site(s) skipped (not a plain int constant -- review manually):")
        for lineno, context in skipped:
            print(f"  line {lineno}: {context}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the transform script and review its report**

Run (from repo root `C:\dac-uw-thesis`):
```bash
python "C:\Users\TRC\AppData\Local\Temp\claude\C--dac-uw-thesis\d58662c3-40e7-49c7-8376-725242b9734f\scratchpad\bump_font_sizes.py"
```
Expected: prints a per-size breakdown (e.g. `9pt -> 12pt: N site(s)`) covering sizes 8-14, totaling roughly 120-140 patches (the deck has ~100 `para()`/`new_para()`/`add_run()`/`card()` call sites plus ~30 raw `.font.size = Pt(N)` sites in table rows). If the "skipped" section reports anything, read each flagged line and confirm by hand whether it's actually a font-size site that needs a manual fix (e.g. a literal built from a variable) — do not proceed to Step 4 until every skipped item is accounted for.

- [ ] **Step 4: Confirm the file still parses and the paragraph-spacing lines were NOT touched**

Run (from repo root `C:\dac-uw-thesis`):
```bash
python -c "import ast; ast.parse(open('thesis/health_rl/build_defense_v3.py', encoding='utf-8').read()); print('parses OK')"
grep -n "space_before = Pt(10)" thesis/health_rl/build_defense_v3.py
grep -n "space_before = Pt(8)" thesis/health_rl/build_defense_v3.py
```
Expected: `parses OK`, and both `space_before` lines still show their original values (`Pt(10)` and `Pt(8)`) — confirming the transform did not touch paragraph spacing.

- [ ] **Step 5: Rebuild the deck**

Run (from repo root `C:\dac-uw-thesis`):
```bash
python thesis/health_rl/build_defense_v3.py
python -c "
from pptx import Presentation
prs = Presentation(r'thesis/health_rl/Poly_defense_presentation_v3.pptx')
print('total slides:', len(prs.slides))
"
```
Expected: builds without error; `total slides: 44` (unchanged from before this task — this task only changes font sizes, never adds/removes slides).

- [ ] **Step 6: Write the overflow-heuristic checker**

Create `C:\Users\TRC\AppData\Local\Temp\claude\C--dac-uw-thesis\d58662c3-40e7-49c7-8376-725242b9734f\scratchpad\check_text_overflow.py`:

```python
"""One-off heuristic overflow checker for the rebuilt defense deck. Estimates
whether any text shape's text now overflows its box after the font-size bump,
using a conservative avg-char-width heuristic -- there is no PowerPoint/
LibreOffice renderer available in this environment to render and inspect
directly. Not committed; a best-effort proxy, not a guarantee.
"""
import math
from pptx import Presentation

PPTX_PATH = r"C:\dac-uw-thesis\thesis\health_rl\Poly_defense_presentation_v3.pptx"
AVG_CHAR_WIDTH_FACTOR = 0.5   # conservative: avg glyph width ~= 0.5 * font-size(pt)
LINE_HEIGHT_FACTOR = 1.2      # line spacing factor
H_MARGIN_PT = 14.4            # python-pptx default left+right text-frame margin (0.1in each)
V_MARGIN_PT = 7.2             # python-pptx default top+bottom text-frame margin (0.05in each)


def main():
    prs = Presentation(PPTX_PATH)
    flagged = []
    checked = 0

    for slide_idx, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            tf = shape.text_frame
            if not tf.word_wrap:
                continue
            checked += 1
            usable_w = shape.width.pt - H_MARGIN_PT
            usable_h = shape.height.pt - V_MARGIN_PT
            if usable_w <= 0 or usable_h <= 0:
                continue
            total_est_height = 0.0
            preview_bits = []
            for para_ in tf.paragraphs:
                text = "".join(r.text for r in para_.runs)
                if not text.strip():
                    continue
                sizes = [r.font.size.pt for r in para_.runs if r.font.size is not None]
                size = max(sizes) if sizes else 12.0
                chars_per_line = max(1, int(usable_w / (AVG_CHAR_WIDTH_FACTOR * size)))
                est_lines = max(1, math.ceil(len(text) / chars_per_line))
                total_est_height += est_lines * size * LINE_HEIGHT_FACTOR
                preview_bits.append(text[:40])
            if total_est_height > usable_h:
                flagged.append({
                    "slide": slide_idx + 1,
                    "shape_id": shape.shape_id,
                    "box_wh_pt": (round(shape.width.pt, 1), round(shape.height.pt, 1)),
                    "est_height_pt": round(total_est_height, 1),
                    "usable_height_pt": round(usable_h, 1),
                    "text_preview": " | ".join(preview_bits)[:120],
                })

    print(f"Checked {checked} text shape(s) across {len(prs.slides)} slides.")
    print(f"Flagged {len(flagged)} shape(s) as potentially overflowing:\n")
    for f in flagged:
        print(f"  Slide {f['slide']}: shape#{f['shape_id']} box={f['box_wh_pt']}pt "
              f"est_height={f['est_height_pt']}pt vs usable_height={f['usable_height_pt']}pt")
        print(f"    text: {f['text_preview']!r}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 7: Run the checker and triage its output**

Run (from repo root `C:\dac-uw-thesis`):
```bash
python "C:\Users\TRC\AppData\Local\Temp\claude\C--dac-uw-thesis\d58662c3-40e7-49c7-8376-725242b9734f\scratchpad\check_text_overflow.py"
```
For every flagged shape: open `thesis/health_rl/build_defense_v3.py`, find the slide/shape by its approximate position and text preview, and judge by hand whether it's a real risk. If a fix is straightforward and localized (e.g. growing a box's height into unused whitespace already on that slide, matching the box-fit arithmetic style used elsewhere in this file), apply it and re-run Steps 5-7 until clean. If a flagged item is NOT a real risk (e.g. the heuristic's conservative character-width assumption clearly over-estimates for a short numeric label), or a fix isn't safely resolvable via arithmetic alone, record it plainly in your task report as a disclosed, unresolved risk for the user to visually check in PowerPoint before the defense — do not guess-fix something you're not confident about.

- [ ] **Step 8: Commit**

This task's change necessarily carries along other already-pending, previously-uncommitted work in the same file (per the user's explicit 2026-07-01 decision — see Global Constraints). Before committing, run `git status --porcelain -- thesis/health_rl/build_defense_v3.py thesis/health_rl/defense_draw.py thesis/health_rl/Poly_defense_presentation_v3.pptx` and `git diff --stat -- thesis/health_rl/build_defense_v3.py` to see the full scope of what's about to be committed, and describe it honestly and completely in the commit message — both this task's font-size contribution AND whatever else is riding along (e.g. footer renumbering, a new Appendix A6 slide, hyperparameter fixes — whatever `git diff --stat` actually shows). Do not commit unrelated files (e.g. `generate_defense_script_v2.py`, deleted thumbnail PNGs) that aren't entangled with these two files.

```bash
git add thesis/health_rl/build_defense_v3.py thesis/health_rl/defense_draw.py thesis/health_rl/Poly_defense_presentation_v3.pptx docs/superpowers/specs/2026-07-01-defense-deck-font-size-bump.md docs/superpowers/plans/2026-07-01-defense-deck-font-size-bump.md
git commit -m "$(cat <<'EOF'
feat(defense): bump body-text font sizes deck-wide for readability

Tiered increase (~2-3pt) across all 44 slides so the committee can
read cards/tables/bullets more easily: 8-10pt -> +3pt, 11-14pt ->
+2pt, >=15pt (titles, big stat numbers, section dividers) and the
9pt footer ribbon left untouched. card()'s defaults in
defense_draw.py bumped to match (9 of 10 card() calls rely on them).

<< describe here, from `git diff --stat`, whatever other pending
   work this commit necessarily also carries along in this file,
   per the user's 2026-07-01 decision to not attempt isolation this
   time -- e.g. footer 43->44 renumbering, a new Appendix A6 slide,
   hyperparameter fixes. Do not leave this placeholder in the actual
   commit message -- replace it with the real, specific list. >>

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review Notes

- **Spec coverage:** tiered mapping (both call-site patterns) ✅, `card()` defaults ✅, footer/title/big-number exclusion ✅, paragraph-spacing exclusion ✅, overflow-risk verification via heuristic checker (disclosed as a proxy, not a render) ✅, commit-hygiene per the user's 2026-07-01 "bump everywhere, disclose the sweep-in" decision ✅.
- **Placeholder scan:** one intentional placeholder remains — the `<< describe here... >>` block in Step 8's commit message. This is unavoidable: the exact list of "other pending work" in the file cannot be known until the implementer actually runs `git diff --stat` against the live working tree at execution time. The step's instructions make explicit that this must be replaced with real, specific content before committing, not left in verbatim.
- **Type/name consistency:** `card()`'s new defaults (`header_size=16, body_size=13`) match the tiered mapping's `14->16` and `11->13` rows exactly. The transform script's `MAPPING` dict matches the spec's table exactly. Verified against the actual file contents (not assumed) via `grep`/`sed` during planning — the two `Pt()` non-font-size call sites (`space_before`), the exact `card()` signature line, and the count/shape of `card()` call sites were all read directly from the repo.
- **Scope:** two files modified by one script + one manual one-line edit, one task — no decomposition needed.
