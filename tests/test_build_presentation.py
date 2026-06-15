"""Tests for the defense presentation generator (v2 minimal-academic, 32 slides)."""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
from pptx import Presentation
from pptx.enum.text import PP_ALIGN

ROOT   = Path(__file__).parent.parent
SCRIPT = ROOT / "thesis" / "health_rl" / "build_burgundy_presentation.py"
OUTPUT = ROOT / "thesis" / "health_rl" / "burgundy_defense_presentation.pptx"
RESULTS_JSON = ROOT / "demo" / "static" / "thesis_results.json"


def _run_build():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True, text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, f"Builder failed:\n{result.stderr}"


@pytest.fixture(scope="session")
def built_presentation():
    OUTPUT.unlink(missing_ok=True)
    _run_build()
    return OUTPUT


@pytest.fixture(scope="session")
def import_builder():
    import importlib.util
    spec = importlib.util.spec_from_file_location("builder", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _all_text(prs, slide_idx: int) -> str:
    return " ".join(
        shape.text_frame.text
        for shape in prs.slides[slide_idx].shapes
        if shape.has_text_frame
    )


# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------

def test_generates_32_slides(built_presentation):
    prs = Presentation(str(built_presentation))
    assert len(prs.slides) == 32, f"Expected 32 slides, got {len(prs.slides)}"


def test_title_slide_has_presenter_name(built_presentation):
    prs = Presentation(str(built_presentation))
    combined = _all_text(prs, 0)
    assert "LUN CHANPOLY" in combined, f"Presenter name missing. Got: {combined[:200]}"


def test_title_slide_has_defense_date(built_presentation):
    prs = Presentation(str(built_presentation))
    combined = _all_text(prs, 0)
    assert "July 2026" in combined, f"Defense date missing. Got: {combined[:200]}"


def test_toc_slide_has_six_sections(built_presentation):
    prs = Presentation(str(built_presentation))
    combined = _all_text(prs, 1)
    for roman in ["i", "ii", "iii", "iv", "v", "vi"]:
        assert roman in combined, f"ToC missing section '{roman}'. Got: {combined[:300]}"


# ---------------------------------------------------------------------------
# Section tags on content slides
# ---------------------------------------------------------------------------

def test_section_tags_present_on_content_slides(built_presentation):
    """Every content slide (indices 2-20) carries an uppercase 'ROMAN · NAME' tag."""
    prs = Presentation(str(built_presentation))
    tag_pattern = re.compile(r"\b(I|II|III|IV|V|VI) · [A-Z&\s]+")
    for idx in range(2, 21):
        combined = _all_text(prs, idx)
        assert tag_pattern.search(combined), (
            f"Slide {idx + 1}: no uppercase section tag found. Got: {combined[:200]}"
        )


def test_appendix_slides_have_page_numbers(built_presentation):
    """Appendix slides (indices 24-31) must have A1-A8 page numbers."""
    prs = Presentation(str(built_presentation))
    for i, label in enumerate(["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"]):
        combined = _all_text(prs, 24 + i)
        assert label in combined, (
            f"Appendix slide {i + 1}: page number '{label}' not found. Got: {combined[:200]}"
        )


# ---------------------------------------------------------------------------
# Decimal slide titles (1.1., 4.3., ...)
# ---------------------------------------------------------------------------

EXPECTED_DECIMAL_TITLES = [
    (2,  r"1\.1"),   # 1.1. Research Background
    (3,  r"1\.2"),   # 1.2. Research Problem
    (4,  r"1\.3"),   # 1.3. Research Goal
    (5,  r"2\.1"),   # 2.1. Internship at DAC
    (6,  r"3\.1"),   # 3.1. Literature Summary
    (7,  r"4\.1"),   # 4.1. System Pipeline
    (8,  r"4\.2"),   # 4.2. Synthetic Cambodia Dataset
    (9,  r"4\.3"),   # 4.3. Bandit Formulation
    (10, r"4\.4"),   # 4.4. Algorithms & Baselines
    (11, r"4\.5"),   # 4.5. Guardrail + HITL Design
    (12, r"5\.1"),   # 5.1. Convergence
    (13, r"5\.2"),   # 5.2. Benchmark
    (14, r"5\.3"),   # 5.3. Cold-start
    (15, r"5\.4"),   # 5.4. HITL Results
    (16, r"5\.5"),   # 5.5. Fairness Audit
    (17, r"5\.6"),   # 5.6. Drift Adaptation
    (18, r"6\.1"),   # 6.1. Achievements
    (19, r"6\.2"),   # 6.2. Limitation: Baseline Ladder
    (20, r"6\.3"),   # 6.3. Other Limitations
]


def test_decimal_titles_on_content_slides(built_presentation):
    prs = Presentation(str(built_presentation))
    for idx, pattern in EXPECTED_DECIMAL_TITLES:
        combined = _all_text(prs, idx)
        assert re.search(pattern, combined), (
            f"Slide {idx + 1}: decimal title pattern '{pattern}' not found. "
            f"Got: {combined[:200]}"
        )


# ---------------------------------------------------------------------------
# Numbers match thesis_results.json
# ---------------------------------------------------------------------------

def test_headline_numbers_match_json(built_presentation):
    """Key headline numbers from JSON appear verbatim in the relevant slides."""
    prs = Presentation(str(built_presentation))
    with open(RESULTS_JSON) as f:
        results = json.load(f)

    # +25.2% lift appears in slide 13 (5.1. Convergence)
    lift_pct = str(results["exp005"]["lift_pct"])
    slide_13_text = _all_text(prs, 12)
    assert lift_pct in slide_13_text, (
        f"EXP-005 lift_pct '{lift_pct}' not found in slide 13. Got: {slide_13_text[:300]}"
    )

    # +14.8% HITL lift appears in slide 16 (5.4. HITL)
    hitl_lift = str(results["exp008"]["lift_pct"])
    slide_16_text = _all_text(prs, 15)
    assert hitl_lift in slide_16_text, (
        f"EXP-008 lift_pct '{hitl_lift}' not found in slide 16. Got: {slide_16_text[:300]}"
    )

    # AlwaysRATED reward appears in slide 20 (6.2. Ladder) -- formatted with comma
    always_rated_r = f"{results['ladder']['rows'][-3]['reward']:,}"  # "122,287"
    slide_20_text = _all_text(prs, 19)
    assert always_rated_r in slide_20_text, (
        f"AlwaysRATED reward '{always_rated_r}' not found in slide 20. "
        f"Got: {slide_20_text[:300]}"
    )

    # Cold-start LinTS p-value appears in slide 15 (5.3. Cold-start)
    lints_p = str(results["exp010"]["wilcoxon_t2000"]["lints_vs_freshxgb"]["p"])
    slide_15_text = _all_text(prs, 14)
    assert lints_p in slide_15_text, (
        f"EXP-010 LinTS p-value '{lints_p}' not found in slide 15. "
        f"Got: {slide_15_text[:300]}"
    )


# ---------------------------------------------------------------------------
# Density rule is enforced in code
# ---------------------------------------------------------------------------

def test_talking_points_helper_rejects_more_than_four():
    import importlib.util
    spec = importlib.util.spec_from_file_location("builder", SCRIPT)
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    prs = Presentation()
    prs.slide_width = builder.SLIDE_WIDTH
    prs.slide_height = builder.SLIDE_HEIGHT
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    with pytest.raises(ValueError):
        builder._add_talking_points(slide, builder.MARGIN_LEFT, builder.CONTENT_TOP,
                                    builder.CONTENT_W, ["a", "b", "c", "d", "e"])


# ---------------------------------------------------------------------------
# v2 style, density, and claim-armor guards
# ---------------------------------------------------------------------------

CONTENT_IDX = list(range(2, 21))            # slides 3-21 (01-19)
NOTED_IDX = CONTENT_IDX + [21] + list(range(24, 32))   # + demo + A1-A8


def test_presenter_notes_on_content_slides(built_presentation):
    prs = Presentation(str(built_presentation))
    for idx in NOTED_IDX:
        slide = prs.slides[idx]
        assert slide.has_notes_slide, f"Slide {idx + 1}: no notes slide"
        text = slide.notes_slide.notes_text_frame.text
        assert len(text) > 40, f"Slide {idx + 1}: notes too short ({len(text)} chars)"


def test_no_serif_display_font(built_presentation):
    """v2 is Calibri-only: Times New Roman must not appear on any slide."""
    prs = Presentation(str(built_presentation))
    for s_i, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for para in shape.text_frame.paragraphs:
                assert para.font.name != "Times New Roman", (
                    f"Slide {s_i + 1}: Times New Roman paragraph '{para.text[:40]}'"
                )
                for run in para.runs:
                    assert run.font.name != "Times New Roman", (
                        f"Slide {s_i + 1}: Times New Roman run '{run.text[:40]}'"
                    )


def test_no_inherited_shadows(built_presentation):
    """Every shape is created through a _flat()-calling helper."""
    prs = Presentation(str(built_presentation))
    for s_i, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            assert shape.shadow.inherit is False, (
                f"Slide {s_i + 1}: shape '{shape.shape_type}' inherits theme shadow"
            )


def test_claim_armor_footnotes_present(built_presentation):
    """The four claim-critical lines must survive any future density edits."""
    prs = Presentation(str(built_presentation))
    checks = [
        (12, "5.0.1"),                        # convergence: admissible scope
        (14, "0.0840"),                       # cold-start: LinUCB softened p
        (15, "AlwaysRATED"),                  # HITL: ceiling scope
        (16, "FAILED-with-interpretation"),   # fairness: criterion 6
        (19, "FALSIFIED"),                    # ladder: falsified expectation
    ]
    for idx, needle in checks:
        combined = _all_text(prs, idx)
        assert needle in combined, (
            f"Slide {idx + 1}: armor text '{needle}' missing. Got: {combined[:300]}"
        )


def test_slide_scale_figures_exist():
    slide_dir = ROOT / "thesis" / "health_rl" / "figures" / "slides"
    for stem in ["slide_reward_curves", "slide_loglog_regret", "slide_cold_start",
                 "slide_hitl", "slide_drift", "slide_ladder"]:
        p = slide_dir / f"{stem}.png"
        assert p.exists() and p.stat().st_size > 30_000, f"{p.name} missing or trivial"


def test_logos_only_on_title_and_thanks(built_presentation):
    """Content slides carry at most one picture (the chart); title/thanks carry logos."""
    prs = Presentation(str(built_presentation))
    def n_pics(idx):
        return sum(1 for sh in prs.slides[idx].shapes if sh.shape_type == 13)
    for idx in CONTENT_IDX:
        assert n_pics(idx) <= 1, f"Slide {idx + 1}: {n_pics(idx)} pictures (logo creep?)"
    assert n_pics(0) >= 2, "Title slide lost its logos"
    assert n_pics(22) >= 2, "Thanks slide lost its logos"


def test_slide_palette_is_blue_not_burgundy():
    """Figure palette must carry no retired burgundy hexes."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "slide_style", ROOT / "thesis" / "health_rl" / "figures" / "_slide_style.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    banned = {"#5d2a42", "#8a5570", "#b894a6", "#471f33"}
    used = {v.lower() for v in mod.SLIDE_PALETTE.values()}
    assert not (used & banned), f"burgundy survives in SLIDE_PALETTE: {used & banned}"
    assert mod.SLIDE_PALETTE["hero"].lower() == "#1b5697", "hero series must be steel-blue"


# ---------------------------------------------------------------------------
# v3 blue footer ribbon
# ---------------------------------------------------------------------------

def test_footer_ribbon_three_parts(import_builder):
    b = import_builder
    prs = Presentation()
    prs.slide_width = b.SLIDE_WIDTH
    prs.slide_height = b.SLIDE_HEIGHT
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    b._add_footer_ribbon(slide, "12 / 27")
    text = " ".join(s.text_frame.text for s in slide.shapes if s.has_text_frame)
    assert "DAC" in text and "ITC-AMS" in text          # left org block
    assert "12 / 27" in text                             # right page block
    assert "July 2026" in text                           # right date


def test_content_title_centered_caps(import_builder):
    b = import_builder
    prs = Presentation()
    prs.slide_width = b.SLIDE_WIDTH
    prs.slide_height = b.SLIDE_HEIGHT
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    b._add_content_title(slide, "Synthetic Cambodia Dataset")
    titled = [s for s in slide.shapes if s.has_text_frame
              and "SYNTHETIC CAMBODIA DATASET" in s.text_frame.text]
    assert titled, "title not rendered ALL-CAPS"
    p = titled[0].text_frame.paragraphs[0]
    assert p.alignment == PP_ALIGN.CENTER
