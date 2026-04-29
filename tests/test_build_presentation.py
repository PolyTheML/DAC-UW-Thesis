"""Tests for the defense presentation generator."""
import subprocess
import sys
from pathlib import Path

import pytest
from pptx import Presentation

SCRIPT = Path("thesis/health_rl/build_presentation.py")
OUTPUT = Path(__file__).parent.parent / "thesis/health_rl/health_rl_defense_presentation.pptx"


def _run_build():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True, text=True,
        cwd=Path(__file__).parent.parent,
    )
    assert result.returncode == 0, f"Script failed:\n{result.stderr}"


@pytest.fixture(scope="session")
def built_presentation():
    OUTPUT.unlink(missing_ok=True)
    _run_build()
    return OUTPUT


def test_generates_20_slides(built_presentation):
    assert built_presentation.exists()
    prs = Presentation(str(built_presentation))
    assert len(prs.slides) == 20, f"Expected 20 slides, got {len(prs.slides)}"


def test_title_slide_has_presenter_name(built_presentation):
    prs = Presentation(str(built_presentation))
    texts = [
        shape.text_frame.text
        for shape in prs.slides[0].shapes
        if shape.has_text_frame
    ]
    combined = " ".join(texts)
    assert "LUN CHANPOLY" in combined, f"Presenter name missing. Got: {combined}"


def test_slide_titles_present(built_presentation):
    prs = Presentation(str(built_presentation))
    expected = [
        ("Adaptive Underwriting", 0),
        ("Agenda",                1),
        ("Cambodia",              2),
        ("Research Claim",        3),
        ("Bandit",                4),
        ("Dataset",               5),
        ("Algorithms",            6),
        ("Reward",                7),
        ("Methodology",           8),
        ("EXP-005",               9),
        ("Learning Curves",      10),
        ("Fairness",             11),
        ("EXP-007",              12),
        ("PSI",                  13),
        ("Proposed Adaptive",    14),
        ("Implementation",       15),
        ("Social Impact",        16),
        ("Discussion",           17),
        ("Conclusion",           18),
        ("Thank You",            19),
    ]
    for keyword, idx in expected:
        texts = [
            shape.text_frame.text
            for shape in prs.slides[idx].shapes
            if shape.has_text_frame
        ]
        combined = " ".join(texts)
        assert keyword in combined, (
            f"Slide {idx + 1}: '{keyword}' not found. Got: {combined[:200]}"
        )
