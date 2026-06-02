"""Tests for equation matching library."""
from audit.lib.match_equations import match_equation, extract_math_tokens


def _make_paper_eq(text: str, page: int = 1) -> dict:
    """Helper to create paper equation dict."""
    return {"text": text, "page": page, "context_before": "", "context_after": ""}


def test_fuzzy_match_linucb():
    """Test fuzzy matching of LinUCB confidence bound."""
    thesis_latex = r"\hat\theta_a^\top x_t + \alpha \sqrt{x_t^\top A_a^{-1} x_t}"
    paper_text = "θ̂_a x_t + α sqrt(x_t A_a^{-1} x_t)"
    result = match_equation(thesis_latex, [_make_paper_eq(paper_text)])
    assert result["confidence"] > 0.4
    assert result["status"] != "FAIL"


def test_no_match_returns_fail():
    """Test that unrelated text returns FAIL status."""
    thesis_latex = r"\frac{a}{b}"
    paper_texts = [_make_paper_eq("completely unrelated sentence about insurance premiums")]
    result = match_equation(thesis_latex, paper_texts)
    assert result["status"] == "FAIL"
    assert result["confidence"] < 0.4


def test_confidence_in_range():
    """Test that confidence is always in [0, 1]."""
    thesis_latex = r"R_T = \sum_t r_t"
    paper_texts = [_make_paper_eq("R_T = sum r_t cumulative regret")]
    result = match_equation(thesis_latex, paper_texts)
    assert 0.0 <= result["confidence"] <= 1.0


def test_extract_math_tokens_greek():
    """Test token extraction handles Greek letters."""
    tokens = extract_math_tokens(r"\theta_a + \alpha \sqrt{x}")
    assert "theta" in tokens or "\\theta" in tokens
    assert "alpha" in tokens or "\\alpha" in tokens


def test_exact_match_gives_high_confidence():
    """Test that exact matches get high confidence."""
    latex = r"A_a \leftarrow A_a + x_t x_t^\top"
    norm = "A_a = A_a + x_t x_t"   # normalised form
    result = match_equation(latex, [_make_paper_eq(norm)])
    assert result["confidence"] >= 0.6
