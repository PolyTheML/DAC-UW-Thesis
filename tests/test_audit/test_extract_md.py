import pytest
from audit.lib.extract_md import extract_equations_from_markdown


SAMPLE_MD = """
## 3.3.2. LinUCB and LinTS

**LinUCB** (Li et al., 2010) selects the action maximising:

$$a_t = \\arg\\max_{a \\in \\mathcal{A}} \\left( \\hat{\\theta}_a^T x_t + \\alpha \\sqrt{x_t^T A_a^{-1} x_t} \\right)$$

where $A_a$ is the design matrix and $\\alpha$ controls exploration (Li et al., 2010).

### 3.3.3. Regret

Regret is $R_T = \\sum_t (r^*_t - r_t)$ (Lattimore & Szepesvári, 2020).
"""


def test_extract_display_equations():
    eqs = extract_equations_from_markdown(SAMPLE_MD, chapter="03")
    display = [e for e in eqs if e["display"]]
    assert len(display) == 1
    assert r"\arg\max" in display[0]["latex_md"]
    assert display[0]["chapter"] == "03"
    assert display[0]["section"] == "3.3.2"


def test_extract_inline_equations():
    eqs = extract_equations_from_markdown(SAMPLE_MD, chapter="03")
    inline = [e for e in eqs if not e["display"]]
    assert len(inline) == 3   # A_a, \alpha, and R_T = sum...
    symbols = {e["latex_md"] for e in inline}
    assert any("A_a" in s for s in symbols)


def test_citation_captured():
    eqs = extract_equations_from_markdown(SAMPLE_MD, chapter="03")
    display = [e for e in eqs if e["display"]]
    assert "Li et al., 2010" in display[0]["citations"]


def test_context_captured():
    eqs = extract_equations_from_markdown(SAMPLE_MD, chapter="03")
    display = [e for e in eqs if e["display"]]
    assert "selects the action" in display[0]["nearby_text_before"]
    assert "design matrix" in display[0]["nearby_text_after"]


def test_equation_ids_unique():
    eqs = extract_equations_from_markdown(SAMPLE_MD, chapter="03")
    ids = [e["equation_id"] for e in eqs]
    assert len(ids) == len(set(ids))
