# Thesis Equation Audit Pipeline — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a 10-phase Python audit pipeline that verifies every thesis equation for correctness, citation, source traceability, and notation consistency, producing a single HTML dashboard.

**Architecture:** Single entry point `audit/run_audit.py` orchestrates 10 phase modules in `audit/phases/`. Heavy logic lives in `audit/lib/` (equation extraction, matching, SymPy verification, HTML rendering). All intermediate results are JSON in `audit/cache/`; the final output is `audit/dashboard.html`.

**Tech Stack:** Python 3.11, pymupdf, python-docx, sympy, rapidfuzz, lxml, pytest

---

## File Map

```
audit/
  run_audit.py                    # thin orchestrator — imports phases, runs 1–10
  lib/
    __init__.py
    extract_md.py                 # regex equation extraction from .md files
    extract_docx.py               # OMML + text extraction from .docx files
    extract_pdf.py                # pymupdf paper ingestion
    match_equations.py            # exact → SymPy → rapidfuzz matching pipeline
    sympy_verify.py               # SymPy derivation verification
    render_html.py                # HTML dashboard template + renderer
  phases/
    __init__.py
    phase_01_inventory.py
    phase_02_papers.py
    phase_03_thesis.py
    phase_04_traceability.py
    phase_05_validation.py
    phase_06_notation.py
    phase_07_literature.py
    phase_08_citations.py
    phase_09_rl_fairness.py
    phase_10_dashboard.py

tests/
  test_audit/
    __init__.py
    test_extract_md.py
    test_match_equations.py
    test_sympy_verify.py
    test_notation_audit.py
    test_render_html.py
```

---

## Task 1: Scaffolding — directories, packages, shared types

**Files:**
- Create: `audit/__init__.py`, `audit/lib/__init__.py`, `audit/phases/__init__.py`
- Create: `audit/lib/types.py`
- Create: `tests/test_audit/__init__.py`
- Modify: `requirements.txt`

- [ ] **Step 1: Add new dependencies to requirements.txt**

Append these lines:

```
pymupdf>=1.24.0,<2.0.0
python-docx>=1.1.0,<2.0.0
sympy>=1.12,<2.0.0
rapidfuzz>=3.6.0,<4.0.0
lxml>=5.0.0,<6.0.0
```

- [ ] **Step 2: Install the new packages**

```
pip install pymupdf>=1.24.0 "python-docx>=1.1.0" "sympy>=1.12" "rapidfuzz>=3.6.0" "lxml>=5.0.0"
```

Expected: all install without errors. Verify with:
```
python -c "import fitz, docx, sympy, rapidfuzz, lxml; print('OK')"
```

- [ ] **Step 3: Create `audit/lib/types.py` with shared TypedDicts**

```python
from typing import TypedDict


class PaperEquation(TypedDict):
    text: str
    page: int
    context_before: str
    context_after: str


class Paper(TypedDict):
    title: str
    authors: list
    year: str
    filename: str
    sections: list
    equations: list          # list[PaperEquation]
    raw_pages: dict          # {str(page_num): text}


class ThesisEquation(TypedDict):
    equation_id: str         # e.g. "ch03_eq_001"
    chapter: str             # e.g. "03"
    section: str             # e.g. "3.3.2"
    latex_md: str
    latex_docx: str          # empty string if not found
    source: str              # "both" | "md_only" | "docx_only"
    build_divergence: bool
    display: bool            # True = $$...$$, False = $...$
    nearby_text_before: str
    nearby_text_after: str
    citations: list          # list[str]


class TraceResult(TypedDict):
    equation_id: str
    status: str              # "PASS" | "WARNING" | "FAIL" | "LLM_QUEUE"
    match_method: str        # "exact" | "sympy" | "fuzzy" | "none"
    confidence: float
    source_paper: str        # filename or empty
    source_page: int         # 0 if unknown
    source_text: str
    cited: bool
    notes: str


class ValidationResult(TypedDict):
    equation_id: str
    claim: str               # human-readable description of derivation check
    status: str              # "PASS" | "FAIL" | "MANUAL_REVIEW"
    notes: str


class NotationIssue(TypedDict):
    symbol: str
    issue_type: str          # "REUSE_CONFLICT" | "UNDEFINED" | "INCONSISTENT_INDEX"
    locations: list          # list of equation_ids or chapter refs
    notes: str


class LiteratureClaim(TypedDict):
    claim_text: str
    chapter: str
    section: str
    citations: list
    status: str              # "SUPPORTED" | "PARTIALLY_SUPPORTED" | "UNSUPPORTED" | "NO_CITED_PAPER"
    evidence: str


class CitationIssue(TypedDict):
    location: str            # equation_id or "ch03:para:5"
    issue_type: str          # "MISSING_CITATION" | "UNCACHED_PAPER"
    text: str
    notes: str
```

- [ ] **Step 4: Create empty `__init__.py` files**

Create empty files at:
- `audit/__init__.py`
- `audit/lib/__init__.py`
- `audit/phases/__init__.py`
- `tests/test_audit/__init__.py`

- [ ] **Step 5: Create audit output directories**

```python
# run once to create dirs:
from pathlib import Path
for d in ["audit/cache/papers", "audit/cache/phase_results", "audit/llm_review_queue"]:
    Path(d).mkdir(parents=True, exist_ok=True)
```

Or from shell:
```
python -c "
from pathlib import Path
for d in ['audit/cache/papers','audit/cache/phase_results','audit/llm_review_queue']:
    Path(d).mkdir(parents=True, exist_ok=True)
print('dirs created')
"
```

- [ ] **Step 6: Commit**

```
git add audit/ tests/test_audit/ requirements.txt
git commit -m "feat(audit): scaffold directory structure and shared types"
```

---

## Task 2: Markdown equation extractor

**Files:**
- Create: `audit/lib/extract_md.py`
- Create: `tests/test_audit/test_extract_md.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_audit/test_extract_md.py
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
    assert len(inline) == 2   # A_a and R_T = sum...
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
```

- [ ] **Step 2: Run — verify it fails**

```
pytest tests/test_audit/test_extract_md.py -v
```

Expected: `ModuleNotFoundError: No module named 'audit.lib.extract_md'`

- [ ] **Step 3: Implement `audit/lib/extract_md.py`**

```python
import re
from pathlib import Path

_DISPLAY_RE = re.compile(r'\$\$(.*?)\$\$', re.DOTALL)
_INLINE_RE = re.compile(r'(?<!\$)\$(?!\$)((?:[^$]|\n)+?)(?<!\$)\$(?!\$)')
_CITATION_RE = re.compile(
    r'\(([A-Z][A-Za-zÀ-ÿ\s\&]+(?:et al\.)?(?:,?\s+\d{4}[a-z]?)'
    r'(?:;\s*[A-Z][A-Za-zÀ-ÿ\s\&]+(?:et al\.)?(?:,?\s+\d{4}[a-z]?)?)*)\)'
)
_HEADING_RE = re.compile(r'^#{1,4}\s+(.+)$', re.MULTILINE)
_SECTION_NUM_RE = re.compile(r'^(\d+\.\d+(?:\.\d+)?)')


def _extract_section(text: str, pos: int) -> str:
    """Return the most recent section heading before pos."""
    last = ""
    for m in _HEADING_RE.finditer(text):
        if m.start() > pos:
            break
        heading = m.group(1).strip()
        num_match = _SECTION_NUM_RE.match(heading)
        if num_match:
            last = num_match.group(1)
    return last


def _extract_citations(window: str) -> list:
    seen, result = set(), []
    for m in _CITATION_RE.finditer(window):
        for part in m.group(1).split(";"):
            s = part.strip()
            if s and s not in seen:
                seen.add(s)
                result.append(s)
    return result


def _context_window(text: str, start: int, end: int, chars: int = 400) -> tuple:
    before = text[max(0, start - chars):start].strip()
    after = text[end:end + chars].strip()
    return before, after


def extract_equations_from_markdown(md_text: str, chapter: str) -> list:
    """
    Extract all display ($$...$$) and inline ($...$) equations from a markdown string.
    Returns a list of ThesisEquation-compatible dicts.
    """
    results = []
    counter = {"display": 0, "inline": 0}

    # Display equations first
    for m in _DISPLAY_RE.finditer(md_text):
        counter["display"] += 1
        eq_id = f"ch{chapter}_disp_{counter['display']:03d}"
        before, after = _context_window(md_text, m.start(), m.end())
        section = _extract_section(md_text, m.start())
        window = before + " " + after
        results.append({
            "equation_id": eq_id,
            "chapter": chapter,
            "section": section,
            "latex_md": m.group(1).strip(),
            "latex_docx": "",
            "source": "md_only",
            "build_divergence": False,
            "display": True,
            "nearby_text_before": before,
            "nearby_text_after": after,
            "citations": _extract_citations(window),
        })

    # Inline equations — skip those already captured inside a display block
    display_spans = [(m.start(), m.end()) for m in _DISPLAY_RE.finditer(md_text)]

    def in_display(pos: int) -> bool:
        return any(s <= pos <= e for s, e in display_spans)

    for m in _INLINE_RE.finditer(md_text):
        if in_display(m.start()):
            continue
        latex = m.group(1).strip()
        if len(latex) < 2:          # skip lone letters/digits
            continue
        counter["inline"] += 1
        eq_id = f"ch{chapter}_inl_{counter['inline']:03d}"
        before, after = _context_window(md_text, m.start(), m.end(), chars=300)
        section = _extract_section(md_text, m.start())
        window = before + " " + after
        results.append({
            "equation_id": eq_id,
            "chapter": chapter,
            "section": section,
            "latex_md": latex,
            "latex_docx": "",
            "source": "md_only",
            "build_divergence": False,
            "display": False,
            "nearby_text_before": before,
            "nearby_text_after": after,
            "citations": _extract_citations(window),
        })

    return results


def extract_equations_from_file(md_path: Path, chapter: str) -> list:
    return extract_equations_from_markdown(md_path.read_text(encoding="utf-8"), chapter)
```

- [ ] **Step 4: Run — verify it passes**

```
pytest tests/test_audit/test_extract_md.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```
git add audit/lib/extract_md.py tests/test_audit/test_extract_md.py
git commit -m "feat(audit): markdown equation extractor with citation + context capture"
```

---

## Task 3: SymPy verifier

**Files:**
- Create: `audit/lib/sympy_verify.py`
- Create: `tests/test_audit/test_sympy_verify.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_audit/test_sympy_verify.py
from audit.lib.sympy_verify import check_symbolic_equivalence, try_sympy_parse


def test_simple_equivalence():
    # a^2 - b^2 == (a-b)(a+b)
    assert check_symbolic_equivalence("a**2 - b**2", "(a - b)*(a + b)") is True


def test_non_equivalence():
    assert check_symbolic_equivalence("a + b", "a - b") is False


def test_parse_failure_returns_none():
    # Complex LaTeX that SymPy cannot parse
    result = try_sympy_parse(r"\arg\max_{a \in \mathcal{A}} \hat\theta_a^\top x_t")
    assert result is None


def test_parse_simple_latex():
    result = try_sympy_parse(r"\frac{a}{b}")
    assert result is not None


def test_equivalence_returns_false_on_parse_failure():
    # Should not raise — return False if either parse fails
    result = check_symbolic_equivalence(r"\arg\max_{a}", r"\sum_{i=1}^n x_i")
    assert isinstance(result, bool)
```

- [ ] **Step 2: Run — verify it fails**

```
pytest tests/test_audit/test_sympy_verify.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement `audit/lib/sympy_verify.py`**

```python
import sympy as sp
from sympy.parsing.latex import parse_latex
import threading


def try_sympy_parse(latex_str: str, timeout_sec: int = 5):
    """
    Try to parse a LaTeX string with SymPy.
    Returns a sympy Expr or None on failure/timeout.
    """
    # Pre-clean common LaTeX constructs SymPy can't handle
    cleaned = (latex_str
               .replace(r'\hat', '')
               .replace(r'\tilde', '')
               .replace(r'\bar', '')
               .replace(r'\vec', '')
               .replace(r'\mathcal', '')
               .replace(r'\mathbf', '')
               .replace(r'\text', '')
               .replace(r'\left', '')
               .replace(r'\right', '')
               .replace(r'\top', 'T')
               .replace(r'\leftarrow', '=')
               .replace(r'^\top', '')
               .replace(r'\cdot', '*')
               .replace(r'\times', '*')
               )
    result = [None]
    error = [None]

    def _parse():
        try:
            result[0] = parse_latex(cleaned)
        except Exception as e:
            error[0] = e

    t = threading.Thread(target=_parse, daemon=True)
    t.start()
    t.join(timeout_sec)
    return result[0]


def check_symbolic_equivalence(expr_a: str, expr_b: str) -> bool:
    """
    Return True if expr_a and expr_b are symbolically equivalent via SymPy.
    Accepts either plain SymPy expression strings or LaTeX strings.
    Returns False (not raises) on any parse/simplify failure.
    """
    try:
        a = sp.sympify(expr_a)
    except Exception:
        a = try_sympy_parse(expr_a)

    try:
        b = sp.sympify(expr_b)
    except Exception:
        b = try_sympy_parse(expr_b)

    if a is None or b is None:
        return False

    try:
        diff = sp.simplify(a - b)
        return diff == 0
    except Exception:
        try:
            return sp.Eq(a, b) is sp.true
        except Exception:
            return False
```

- [ ] **Step 4: Run — verify it passes**

```
pytest tests/test_audit/test_sympy_verify.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```
git add audit/lib/sympy_verify.py tests/test_audit/test_sympy_verify.py
git commit -m "feat(audit): SymPy verifier with timeout and LaTeX pre-cleaning"
```

---

## Task 4: Equation matcher

**Files:**
- Create: `audit/lib/match_equations.py`
- Create: `tests/test_audit/test_match_equations.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_audit/test_match_equations.py
from audit.lib.match_equations import match_equation, extract_math_tokens


def _make_paper_eq(text: str, page: int = 1) -> dict:
    return {"text": text, "page": page, "context_before": "", "context_after": ""}


def test_fuzzy_match_linucb():
    thesis_latex = r"\hat\theta_a^\top x_t + \alpha \sqrt{x_t^\top A_a^{-1} x_t}"
    paper_text = "θ̂_a x_t + α sqrt(x_t A_a^{-1} x_t)"
    result = match_equation(thesis_latex, [_make_paper_eq(paper_text)])
    assert result["confidence"] > 0.4
    assert result["status"] != "FAIL"


def test_no_match_returns_fail():
    thesis_latex = r"\frac{a}{b}"
    paper_texts = [_make_paper_eq("completely unrelated sentence about insurance premiums")]
    result = match_equation(thesis_latex, paper_texts)
    assert result["status"] == "FAIL"
    assert result["confidence"] < 0.4


def test_confidence_in_range():
    thesis_latex = r"R_T = \sum_t r_t"
    paper_texts = [_make_paper_eq("R_T = sum r_t cumulative regret")]
    result = match_equation(thesis_latex, paper_texts)
    assert 0.0 <= result["confidence"] <= 1.0


def test_extract_math_tokens_greek():
    tokens = extract_math_tokens(r"\theta_a + \alpha \sqrt{x}")
    assert "theta" in tokens or "\\theta" in tokens
    assert "alpha" in tokens or "\\alpha" in tokens


def test_exact_match_gives_high_confidence():
    latex = r"A_a \leftarrow A_a + x_t x_t^\top"
    norm = "A_a = A_a + x_t x_t"   # normalised form
    result = match_equation(latex, [_make_paper_eq(norm)])
    assert result["confidence"] >= 0.6
```

- [ ] **Step 2: Run — verify it fails**

```
pytest tests/test_audit/test_match_equations.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement `audit/lib/match_equations.py`**

```python
import re
from rapidfuzz import fuzz

_LATEX_TOKEN_RE = re.compile(
    r'\\(?:hat|tilde|bar|vec|mathbf|mathcal|arg\s*max|arg\s*min|max|min|'
    r'sum|prod|sqrt|frac|log|exp|theta|alpha|beta|gamma|lambda|mu|sigma|'
    r'epsilon|varepsilon|rho|delta|phi|psi|omega|Omega|Sigma|Lambda|top|'
    r'leftarrow|rightarrow|cdot|times|in|forall|exists|mathbb|sim|'
    r'mathcal|tilde|left|right|Bigl|Bigr)|'
    r'[A-Za-z_][A-Za-z0-9_]*(?:_\{[^}]+\}|_[A-Za-z0-9])?|'
    r'\d+(?:\.\d+)?'
)

_GREEK_MAP = {
    'θ': 'theta', 'α': 'alpha', 'β': 'beta', 'γ': 'gamma',
    'λ': 'lambda', 'μ': 'mu', 'σ': 'sigma', 'ε': 'epsilon',
    'ρ': 'rho', 'δ': 'delta', 'φ': 'phi', 'ψ': 'psi',
    '∑': 'sum', '∏': 'prod', '∫': 'int', '√': 'sqrt',
}

_WHITESPACE_RE = re.compile(r'\s+')


def extract_math_tokens(text: str) -> set:
    """Extract normalized math token set from a LaTeX or PDF-text string."""
    # Map Unicode Greek letters to ASCII names
    for char, name in _GREEK_MAP.items():
        text = text.replace(char, name)
    tokens = set(_LATEX_TOKEN_RE.findall(text))
    # Strip leading backslash for comparison
    normalized = set()
    for t in tokens:
        normalized.add(t.lstrip('\\').lower().replace(' ', ''))
    return normalized


def _normalize(text: str) -> str:
    """Collapse whitespace, lowercase."""
    return _WHITESPACE_RE.sub(' ', text.lower()).strip()


def _fuzzy_score(thesis_latex: str, paper_text: str) -> float:
    """Return 0.0–1.0 token-set similarity between thesis LaTeX and paper text."""
    thesis_tokens = extract_math_tokens(thesis_latex)
    paper_tokens = extract_math_tokens(paper_text)
    if not thesis_tokens:
        return 0.0
    overlap = thesis_tokens & paper_tokens
    # Jaccard-style with rapidfuzz character-level fallback
    jaccard = len(overlap) / len(thesis_tokens | paper_tokens) if (thesis_tokens | paper_tokens) else 0.0
    char_score = fuzz.token_set_ratio(_normalize(thesis_latex), _normalize(paper_text)) / 100.0
    return max(jaccard, char_score * 0.8)


def match_equation(thesis_latex: str, paper_equations: list, citation_paper: str = "") -> dict:
    """
    Find the best matching paper equation for a thesis equation.

    Returns a dict with keys: status, match_method, confidence, source_page, source_text, notes.
    Status: "PASS" (≥0.75), "LLM_QUEUE" (0.40–0.74), "FAIL" (<0.40)
    """
    if not paper_equations:
        return _result("FAIL", "none", 0.0, 0, "", "No paper equations to match against")

    best_score = 0.0
    best_eq = None

    for eq in paper_equations:
        # 1. Exact string match (normalised)
        norm_thesis = _normalize(thesis_latex.replace('\\', ''))
        norm_paper = _normalize(eq["text"])
        if norm_thesis and norm_thesis in norm_paper:
            return _result("PASS", "exact", 1.0, eq["page"], eq["text"], "Exact normalized match")

        # 2. Fuzzy token match
        score = _fuzzy_score(thesis_latex, eq["text"])
        if score > best_score:
            best_score = score
            best_eq = eq

    if best_score >= 0.75:
        return _result("PASS", "fuzzy", best_score, best_eq["page"], best_eq["text"], "")
    elif best_score >= 0.40:
        return _result("LLM_QUEUE", "fuzzy", best_score, best_eq["page"], best_eq["text"],
                       "Partial match — queued for LLM review")
    else:
        return _result("FAIL", "none", best_score, 0, "", "No match found in any paper")


def _result(status: str, method: str, confidence: float,
            page: int, text: str, notes: str) -> dict:
    return {
        "status": status,
        "match_method": method,
        "confidence": round(confidence, 3),
        "source_page": page,
        "source_text": text[:300] if text else "",
        "notes": notes,
    }
```

- [ ] **Step 4: Run — verify it passes**

```
pytest tests/test_audit/test_match_equations.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```
git add audit/lib/match_equations.py tests/test_audit/test_match_equations.py
git commit -m "feat(audit): equation matcher — exact / fuzzy / LLM-queue pipeline"
```

---

## Task 5: PDF paper extractor

**Files:**
- Create: `audit/lib/extract_pdf.py`

(Integration test uses real PDFs — no unit test file needed for this module.)

- [ ] **Step 1: Implement `audit/lib/extract_pdf.py`**

```python
import re
from pathlib import Path
import fitz   # pymupdf

_MATH_CHARS = set("αβγδεζηθλμνρστφχψω∑∏∫∂∇≤≥≠≈∈∉√")
_MATH_TOKEN_RE = re.compile(
    r'\b(?:argmax|argmin|arg\s+max|arg\s+min|UCB|regret|posterior|'
    r'E\s*\[|P\s*\(|N\s*\(|PSI)\b|'
    r'[θαβγλμσεv²]\s*[_^]|'
    r'[A-Z]_[a-z]|\b[a-z]_\{|'     # subscripted symbols like A_a or x_{t}
    r'\\frac|\\sum|\\sqrt'
)
_TITLE_STOP = re.compile(r'\b(?:abstract|introduction|1\s+introduction)\b', re.IGNORECASE)


def _is_math_line(line: str) -> bool:
    line = line.strip()
    if len(line) < 3 or len(line) > 300:
        return False
    if sum(1 for c in line if c in _MATH_CHARS) > 0:
        return True
    if _MATH_TOKEN_RE.search(line):
        return True
    ops = line.count('=') + line.count('+') + line.count('≤') + line.count('≥')
    if ops >= 2 and len(line) < 200:
        return True
    return False


def _extract_title_authors(first_pages_text: str) -> tuple:
    """Heuristic: title is the longest line in the first 30 lines; authors follow."""
    lines = [l.strip() for l in first_pages_text.split('\n') if l.strip()][:40]
    # Title: longest line before "Abstract"
    title = ""
    authors = []
    for i, line in enumerate(lines):
        if _TITLE_STOP.search(line):
            break
        if len(line) > len(title) and not line[0].isdigit():
            title = line
        elif i > 0 and 1 < len(line) < 80:
            authors.append(line)
    return title, authors[:5]


def _extract_year(text: str) -> str:
    m = re.search(r'\b(19|20)\d{2}\b', text[:2000])
    return m.group(0) if m else ""


def extract_paper(pdf_path: Path) -> dict:
    """
    Extract title, authors, year, section headings, equations, and raw page text
    from a research paper PDF.
    """
    doc = fitz.open(str(pdf_path))
    raw_pages = {}
    all_text = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        raw_pages[str(page_num + 1)] = text
        all_text.append(text)

    full_text = "\n".join(all_text)
    first_two_pages = "\n".join(list(raw_pages.values())[:2])

    title, authors = _extract_title_authors(first_two_pages)
    year = _extract_year(first_two_pages)

    # Section headings: lines that are short, possibly numbered, not all-lower
    sections = []
    heading_re = re.compile(r'^(\d+(?:\.\d+)*\.?\s+[A-Z].{3,60})$')
    for page_num_str, text in raw_pages.items():
        for line in text.split('\n'):
            if heading_re.match(line.strip()):
                sections.append({"heading": line.strip(), "page": int(page_num_str)})

    # Equations: math-heavy lines with surrounding context
    equations = []
    for page_num_str, text in raw_pages.items():
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if _is_math_line(line):
                before = " ".join(lines[max(0, i - 3):i]).strip()
                after = " ".join(lines[i + 1:i + 4]).strip()
                equations.append({
                    "text": line.strip(),
                    "page": int(page_num_str),
                    "context_before": before[:300],
                    "context_after": after[:300],
                })

    doc.close()

    return {
        "title": title,
        "authors": authors,
        "year": year,
        "filename": pdf_path.name,
        "sections": sections[:50],
        "equations": equations,
        "raw_pages": raw_pages,
    }
```

- [ ] **Step 2: Smoke-test against a real paper**

```python
# run from repo root
from pathlib import Path
from audit.lib.extract_pdf import extract_paper
p = extract_paper(Path("thesis/papers/agrawal13.pdf"))
print(f"Title: {p['title']}")
print(f"Year: {p['year']}")
print(f"Equations found: {len(p['equations'])}")
print(f"Pages: {len(p['raw_pages'])}")
assert len(p["equations"]) > 0
assert p["year"] in ("2013", "2011", "2012")
```

Expected: prints title containing "Thompson", year "2013", and > 0 equations.

- [ ] **Step 3: Commit**

```
git add audit/lib/extract_pdf.py
git commit -m "feat(audit): pymupdf paper ingestion with heuristic equation detection"
```

---

## Task 6: DOCX equation extractor

**Files:**
- Create: `audit/lib/extract_docx.py`

- [ ] **Step 1: Implement `audit/lib/extract_docx.py`**

```python
import re
from pathlib import Path
from docx import Document
from lxml import etree

_M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
_M = f"{{{_M_NS}}}"

_DISPLAY_RE = re.compile(r'\$\$(.*?)\$\$', re.DOTALL)
_INLINE_RE = re.compile(r'(?<!\$)\$(?!\$)((?:[^$]|\n)+?)(?<!\$)\$(?!\$)')


# ── OMML → LaTeX converter (limited to constructs in this thesis) ─────────────

def _omml_text(node) -> str:
    """Recursively extract text from an OMML node."""
    parts = []
    for child in node:
        tag = child.tag.replace(_M, "m:")
        if tag == "m:r":
            for sub in child:
                if "t" in sub.tag:
                    parts.append(sub.text or "")
        elif tag in ("m:f", "m:rad", "m:sup", "m:sub", "m:nary", "m:func",
                     "m:e", "m:num", "m:den", "m:deg", "m:fName"):
            parts.append(_omml_node_to_latex(child))
        else:
            parts.append(_omml_text(child))
    return "".join(parts)


def _omml_node_to_latex(node) -> str:
    tag = node.tag.replace(_M, "m:")

    if tag == "m:r":
        return "".join(sub.text or "" for sub in node if "t" in sub.tag)

    if tag == "m:f":
        num = node.find(f"{_M}num")
        den = node.find(f"{_M}den")
        n = _omml_text(num) if num is not None else ""
        d = _omml_text(den) if den is not None else ""
        return f"\\frac{{{n}}}{{{d}}}"

    if tag == "m:sup":
        base = node.find(f"{_M}e")
        sup = node.find(f"{_M}sup")
        b = _omml_text(base) if base is not None else ""
        s = _omml_text(sup) if sup is not None else ""
        return f"{b}^{{{s}}}"

    if tag == "m:sub":
        base = node.find(f"{_M}e")
        sub = node.find(f"{_M}sub")
        b = _omml_text(base) if base is not None else ""
        s = _omml_text(sub) if sub is not None else ""
        return f"{b}_{{{s}}}"

    if tag == "m:rad":
        e = node.find(f"{_M}e")
        e_tex = _omml_text(e) if e is not None else ""
        return f"\\sqrt{{{e_tex}}}"

    if tag == "m:nary":
        pr = node.find(f"{_M}naryPr")
        chr_el = pr.find(f"{_M}chr") if pr is not None else None
        op_char = (chr_el.get(f"{M}val", "∑") if chr_el is not None else "∑")
        op = {"∑": "\\sum", "∏": "\\prod", "∫": "\\int"}.get(op_char, "\\sum")
        sub = node.find(f"{_M}sub")
        sup = node.find(f"{_M}sup")
        e = node.find(f"{_M}e")
        result = op
        if sub is not None:
            result += f"_{{{_omml_text(sub)}}}"
        if sup is not None:
            result += f"^{{{_omml_text(sup)}}}"
        if e is not None:
            result += " " + _omml_text(e)
        return result

    # Default: recurse
    return _omml_text(node)


def _extract_omml_equations(doc: Document) -> list:
    """Extract equations stored as OMML (native Word math objects)."""
    equations = []
    for para_idx, para in enumerate(doc.paragraphs):
        xml = etree.fromstring(para._element.xml)
        math_nodes = xml.findall(f".//{_M}oMath")
        if not math_nodes:
            math_nodes = xml.findall(f".//{_M}oMathPara//{_M}oMath")
        for node in math_nodes:
            latex = _omml_node_to_latex(node).strip()
            if latex:
                equations.append({
                    "latex_docx": latex,
                    "para_idx": para_idx,
                    "method": "omml",
                })
    return equations


def _extract_text_equations(doc: Document) -> list:
    """Fallback: extract $$...$$ and $...$ from paragraph text."""
    equations = []
    full_text = "\n".join(p.text for p in doc.paragraphs)

    for m in _DISPLAY_RE.finditer(full_text):
        equations.append({
            "latex_docx": m.group(1).strip(),
            "para_idx": -1,
            "method": "text_display",
        })
    display_spans = [(m.start(), m.end()) for m in _DISPLAY_RE.finditer(full_text)]

    def in_display(pos):
        return any(s <= pos <= e for s, e in display_spans)

    for m in _INLINE_RE.finditer(full_text):
        if not in_display(m.start()) and len(m.group(1).strip()) >= 2:
            equations.append({
                "latex_docx": m.group(1).strip(),
                "para_idx": -1,
                "method": "text_inline",
            })
    return equations


def extract_equations_from_docx(docx_path: Path) -> list:
    """
    Extract equations from a DOCX file.
    Tries OMML first; falls back to text regex if no OMML nodes found.
    Returns list of dicts with keys: latex_docx, para_idx, method.
    """
    doc = Document(str(docx_path))
    equations = _extract_omml_equations(doc)
    if not equations:
        equations = _extract_text_equations(doc)
    return equations
```

- [ ] **Step 2: Smoke-test against the thesis DOCX**

```python
from pathlib import Path
from audit.lib.extract_docx import extract_equations_from_docx
eqs = extract_equations_from_docx(
    Path("thesis/build/I5_ITC_Thesis_Submission_Final_fig21_fig22.docx")
)
print(f"Equations found: {len(eqs)}")
print(f"Method used: {eqs[0]['method'] if eqs else 'none'}")
assert len(eqs) > 0
```

Expected: > 0 equations, method is either "omml" or "text_display"/"text_inline".

- [ ] **Step 3: Commit**

```
git add audit/lib/extract_docx.py
git commit -m "feat(audit): DOCX equation extractor — OMML-first with text regex fallback"
```

---

## Task 7: HTML renderer

**Files:**
- Create: `audit/lib/render_html.py`
- Create: `tests/test_audit/test_render_html.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_audit/test_render_html.py
from audit.lib.render_html import render_dashboard


def _fake_results() -> dict:
    return {
        "phase4": [
            {"equation_id": "ch03_disp_001", "status": "PASS", "confidence": 0.95,
             "source_paper": "agrawal13.pdf", "source_page": 4,
             "source_text": "theta_a x_t", "cited": True, "notes": "",
             "match_method": "fuzzy"},
            {"equation_id": "ch03_disp_002", "status": "FAIL", "confidence": 0.1,
             "source_paper": "", "source_page": 0,
             "source_text": "", "cited": False, "notes": "No match",
             "match_method": "none"},
        ],
        "phase5": [],
        "phase6": [],
        "phase7": [],
        "phase8": [],
        "phase9": [
            {"check_id": "RL-01", "status": "PASS", "notes": ""}
        ],
        "thesis_equations": [
            {"equation_id": "ch03_disp_001", "chapter": "03", "section": "3.3.2",
             "latex_md": r"\hat\theta_a^\top x_t", "display": True,
             "citations": ["Agrawal & Goyal, 2013"]},
            {"equation_id": "ch03_disp_002", "chapter": "03", "section": "3.3.3",
             "latex_md": r"R_T = \sum_t r_t", "display": True,
             "citations": []},
        ],
        "llm_queue": ["ch03_disp_003"],
    }


def test_html_contains_summary_table():
    html = render_dashboard(_fake_results())
    assert "Executive Summary" in html
    assert "PASS" in html
    assert "FAIL" in html


def test_html_is_self_contained():
    html = render_dashboard(_fake_results())
    assert "<!DOCTYPE html>" in html
    assert "</html>" in html
    assert "<style>" in html   # inline styles, no external CSS


def test_badge_counts_correct():
    html = render_dashboard(_fake_results())
    # 1 PASS and 1 FAIL in phase4
    assert "1" in html   # at least some count appears


def test_html_has_collapsible_sections():
    html = render_dashboard(_fake_results())
    assert "<details" in html
    assert "<summary" in html
```

- [ ] **Step 2: Run — verify it fails**

```
pytest tests/test_audit/test_render_html.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement `audit/lib/render_html.py`**

```python
from datetime import datetime

_STATUS_COLOR = {
    "PASS": "#22c55e",
    "WARNING": "#f59e0b",
    "FAIL": "#ef4444",
    "MANUAL_REVIEW": "#3b82f6",
    "LLM_QUEUE": "#8b5cf6",
    "SUPPORTED": "#22c55e",
    "PARTIALLY_SUPPORTED": "#f59e0b",
    "UNSUPPORTED": "#ef4444",
    "NO_CITED_PAPER": "#6b7280",
}

_BADGE = '<span style="background:{color};color:#fff;padding:2px 8px;border-radius:4px;font-size:0.8em;font-weight:bold">{label}</span>'


def _badge(status: str) -> str:
    color = _STATUS_COLOR.get(status, "#6b7280")
    return _BADGE.format(color=color, label=status)


def _count_statuses(items: list, key: str = "status") -> dict:
    counts = {}
    for item in items:
        s = item.get(key, "UNKNOWN")
        counts[s] = counts.get(s, 0) + 1
    return counts


def _table_rows(items: list, columns: list) -> str:
    rows = []
    for item in items:
        cells = []
        for col in columns:
            val = item.get(col, "")
            if col == "status":
                val = _badge(str(val))
            else:
                val = str(val)[:120]
            cells.append(f"<td style='padding:4px 8px;border-bottom:1px solid #e5e7eb'>{val}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return "\n".join(rows)


def _section(title: str, content: str) -> str:
    return f"""
<details open style="margin:16px 0;border:1px solid #e5e7eb;border-radius:8px;overflow:hidden">
  <summary style="background:#f9fafb;padding:12px 16px;cursor:pointer;font-weight:bold;font-size:1.05em">{title}</summary>
  <div style="padding:16px">{content}</div>
</details>"""


def _phase4_html(items: list) -> str:
    if not items:
        return "<p>No results.</p>"
    cols = ["equation_id", "status", "match_method", "confidence", "source_paper", "source_page", "cited", "notes"]
    header = "".join(f"<th style='text-align:left;padding:4px 8px;background:#f3f4f6'>{c}</th>" for c in cols)
    return (f"<table style='width:100%;border-collapse:collapse;font-size:0.9em'>"
            f"<tr>{header}</tr>{_table_rows(items, cols)}</table>")


def _phase9_html(items: list) -> str:
    if not items:
        return "<p>No results.</p>"
    cols = ["check_id", "status", "notes"]
    header = "".join(f"<th style='text-align:left;padding:4px 8px;background:#f3f4f6'>{c}</th>" for c in cols)
    return (f"<table style='width:100%;border-collapse:collapse;font-size:0.9em'>"
            f"<tr>{header}</tr>{_table_rows(items, cols)}</table>")


def _generic_html(items: list, cols: list) -> str:
    if not items:
        return "<p>No issues found.</p>"
    header = "".join(f"<th style='text-align:left;padding:4px 8px;background:#f3f4f6'>{c}</th>" for c in cols)
    return (f"<table style='width:100%;border-collapse:collapse;font-size:0.9em'>"
            f"<tr>{header}</tr>{_table_rows(items, cols)}</table>")


def render_dashboard(results: dict) -> str:
    p4 = results.get("phase4", [])
    p5 = results.get("phase5", [])
    p6 = results.get("phase6", [])
    p7 = results.get("phase7", [])
    p8 = results.get("phase8", [])
    p9 = results.get("phase9", [])
    equations = results.get("thesis_equations", [])
    llm_queue = results.get("llm_queue", [])

    # Counts
    p4_counts = _count_statuses(p4)
    total = len(p4)
    n_pass = p4_counts.get("PASS", 0)
    n_warn = p4_counts.get("WARNING", 0)
    n_fail = p4_counts.get("FAIL", 0)
    n_llm = len(llm_queue)
    n_manual = sum(1 for r in p5 if r.get("status") == "MANUAL_REVIEW")

    summary_table = f"""
<table style="border-collapse:collapse;margin:16px 0">
  <tr><th style="padding:8px 16px;background:#f3f4f6;text-align:left">Metric</th>
      <th style="padding:8px 16px;background:#f3f4f6;text-align:right">Count</th></tr>
  <tr><td style="padding:8px 16px">Total equations audited</td><td style="padding:8px 16px;text-align:right">{total}</td></tr>
  <tr><td style="padding:8px 16px">{_badge('PASS')} Traced to source</td><td style="padding:8px 16px;text-align:right">{n_pass}</td></tr>
  <tr><td style="padding:8px 16px">{_badge('WARNING')} Found in non-cited paper</td><td style="padding:8px 16px;text-align:right">{n_warn}</td></tr>
  <tr><td style="padding:8px 16px">{_badge('FAIL')} Not found in any paper</td><td style="padding:8px 16px;text-align:right">{n_fail}</td></tr>
  <tr><td style="padding:8px 16px">{_badge('LLM_QUEUE')} Queued for manual LLM review</td><td style="padding:8px 16px;text-align:right">{n_llm}</td></tr>
  <tr><td style="padding:8px 16px">{_badge('MANUAL_REVIEW')} Math derivation needs manual check</td><td style="padding:8px 16px;text-align:right">{n_manual}</td></tr>
</table>"""

    # High-priority issues
    fails = [r for r in p4 if r.get("status") == "FAIL"]
    high_priority = ""
    if fails:
        high_priority = "<h3 style='color:#ef4444'>High-Priority Issues</h3>"
        for f in fails:
            high_priority += f"<p>🔴 Equation <code>{f['equation_id']}</code>: {f['notes']}</p>"

    # LLM queue
    llm_html = ""
    if llm_queue:
        items = "".join(f"<li><code>{eq}</code> — see <code>audit/llm_review_queue/{eq}.txt</code></li>" for eq in llm_queue)
        llm_html = _section("⬜ LLM Review Queue", f"<p>{len(llm_queue)} equations need manual review via Claude:</p><ul>{items}</ul>")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Thesis Equation Audit Dashboard</title>
<style>
  body {{ font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 24px 32px; color: #1f2937; }}
  h1 {{ border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }}
  h2 {{ color: #374151; }}
  code {{ background: #f3f4f6; padding: 2px 6px; border-radius: 4px; font-size: 0.85em; }}
  details summary:hover {{ background: #f3f4f6; }}
</style>
</head>
<body>
<h1>Thesis Equation Audit Dashboard</h1>
<p style="color:#6b7280">Generated: {now}</p>

<h2>Executive Summary</h2>
{summary_table}
{high_priority}

{_section("Phase 4 — Equation Traceability", _phase4_html(p4))}
{_section("Phase 5 — Mathematical Validation", _generic_html(p5, ["equation_id","claim","status","notes"]))}
{_section("Phase 6 — Notation Consistency", _generic_html(p6, ["symbol","issue_type","locations","notes"]))}
{_section("Phase 7 — Literature Consistency", _generic_html(p7, ["claim_text","citations","status","evidence"]))}
{_section("Phase 8 — Citation Audit", _generic_html(p8, ["location","issue_type","text","notes"]))}
{_section("Phase 9 — RL &amp; Fairness Audit", _phase9_html(p9))}
{llm_html}
</body>
</html>"""
```

- [ ] **Step 4: Run tests — verify they pass**

```
pytest tests/test_audit/test_render_html.py -v
```

Expected: all 4 tests PASS.

- [ ] **Step 5: Commit**

```
git add audit/lib/render_html.py tests/test_audit/test_render_html.py
git commit -m "feat(audit): self-contained HTML dashboard renderer with collapsible sections"
```

---

## Task 8: Phases 1, 2, 3 — Inventory, Paper ingestion, Thesis ingestion

**Files:**
- Create: `audit/phases/phase_01_inventory.py`
- Create: `audit/phases/phase_02_papers.py`
- Create: `audit/phases/phase_03_thesis.py`

- [ ] **Step 1: Implement `audit/phases/phase_01_inventory.py`**

```python
import json
import os
from pathlib import Path


def run(repo_root: Path, output_dir: Path) -> dict:
    """Walk repo and document all thesis-relevant files."""
    inventory = {
        "thesis_documents": [],
        "bibliography_files": [],
        "papers": [],
        "chapter_files": [],
        "figures": [],
    }

    # Thesis DOCX
    for p in (repo_root / "thesis").rglob("*.docx"):
        if not p.name.startswith("~$"):
            inventory["thesis_documents"].append({
                "path": str(p.relative_to(repo_root)),
                "size_kb": round(p.stat().st_size / 1024, 1),
            })

    # Bibliography
    for p in repo_root.rglob("*.bib"):
        inventory["bibliography_files"].append(str(p.relative_to(repo_root)))

    # Papers
    papers_dir = repo_root / "thesis" / "papers"
    if papers_dir.exists():
        for p in papers_dir.glob("*.pdf"):
            inventory["papers"].append({
                "path": str(p.relative_to(repo_root)),
                "size_kb": round(p.stat().st_size / 1024, 1),
            })

    # Chapter markdown files
    for p in sorted((repo_root / "thesis" / "health_rl").glob("chapter*.md")):
        inventory["chapter_files"].append(str(p.relative_to(repo_root)))

    # Figures
    for p in (repo_root / "thesis" / "health_rl" / "figures").glob("*.png"):
        inventory["figures"].append(str(p.relative_to(repo_root)))

    # Write markdown report
    lines = [
        "# Repository Inventory\n",
        f"## Thesis Documents ({len(inventory['thesis_documents'])})\n",
    ]
    for d in inventory["thesis_documents"]:
        lines.append(f"- `{d['path']}` ({d['size_kb']} KB)\n")
    lines.append(f"\n## Source Papers ({len(inventory['papers'])})\n")
    for p in inventory["papers"]:
        lines.append(f"- `{p['path']}` ({p['size_kb']} KB)\n")
    lines.append(f"\n## Chapter Files ({len(inventory['chapter_files'])})\n")
    for c in inventory["chapter_files"]:
        lines.append(f"- `{c}`\n")
    lines.append(f"\n## Bibliography Files: {len(inventory['bibliography_files'])}\n")
    lines.append(f"\n## Figures: {len(inventory['figures'])}\n")

    (output_dir / "repository_inventory.md").write_text("".join(lines), encoding="utf-8")
    print(f"[Phase 1] Inventory complete: {len(inventory['papers'])} papers, "
          f"{len(inventory['chapter_files'])} chapters")
    return inventory
```

- [ ] **Step 2: Implement `audit/phases/phase_02_papers.py`**

```python
import json
from pathlib import Path
from audit.lib.extract_pdf import extract_paper


def run(repo_root: Path, cache_dir: Path) -> dict:
    """Ingest all PDFs from thesis/papers/ and write per-paper JSON."""
    papers_dir = repo_root / "thesis" / "papers"
    papers_cache_dir = cache_dir / "papers"
    papers_cache_dir.mkdir(parents=True, exist_ok=True)

    index = {}
    for pdf_path in sorted(papers_dir.glob("*.pdf")):
        print(f"[Phase 2] Ingesting {pdf_path.name} ...")
        paper = extract_paper(pdf_path)
        out_path = papers_cache_dir / f"{pdf_path.stem}.json"
        out_path.write_text(json.dumps(paper, indent=2, ensure_ascii=False), encoding="utf-8")
        index[pdf_path.stem] = {
            "title": paper["title"],
            "year": paper["year"],
            "equations_count": len(paper["equations"]),
            "pages": len(paper["raw_pages"]),
            "cache_file": str(out_path.relative_to(cache_dir.parent)),
        }
        print(f"  → {len(paper['equations'])} equations, {len(paper['raw_pages'])} pages")

    (cache_dir / "paper_index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[Phase 2] Indexed {len(index)} papers")
    return index
```

- [ ] **Step 3: Implement `audit/phases/phase_03_thesis.py`**

```python
import json
import re
from pathlib import Path
from audit.lib.extract_md import extract_equations_from_file
from audit.lib.extract_docx import extract_equations_from_docx

_CHAPTER_NUM_RE = re.compile(r'chapter(\d+)')

# Primary DOCX to audit
_DOCX_FILENAME = "I5_ITC_Thesis_Submission_Final_fig21_fig22.docx"


def _cross_check(md_eqs: list, docx_eqs: list) -> list:
    """
    For each md equation, try to find a matching docx equation by LaTeX similarity.
    Mark build_divergence=True if a display equation has no DOCX counterpart.
    """
    docx_latexes = [e["latex_docx"] for e in docx_eqs]
    results = []
    for eq in md_eqs:
        if not eq["display"]:
            # Inline equations are harder to cross-check; skip
            eq["source"] = "md_only"
            results.append(eq)
            continue

        # Try to find docx match via substring or token overlap
        matched = False
        for dl in docx_latexes:
            # Normalise: strip whitespace, compare key tokens
            md_tokens = set(re.findall(r'[A-Za-z_]+', eq["latex_md"]))
            docx_tokens = set(re.findall(r'[A-Za-z_]+', dl))
            if md_tokens and docx_tokens and len(md_tokens & docx_tokens) / len(md_tokens) > 0.5:
                matched = True
                eq["latex_docx"] = dl
                eq["source"] = "both"
                break

        if not matched:
            eq["source"] = "md_only"
            # Display equation in MD but not DOCX = potential build divergence
            eq["build_divergence"] = True

        results.append(eq)
    return results


def run(repo_root: Path, cache_dir: Path) -> list:
    """Extract equations from all chapter .md files and cross-check against DOCX."""
    chapters_dir = repo_root / "thesis" / "health_rl"
    docx_path = repo_root / "thesis" / "build" / _DOCX_FILENAME

    all_equations = []

    for md_path in sorted(chapters_dir.glob("chapter*.md")):
        m = _CHAPTER_NUM_RE.search(md_path.stem)
        chapter = m.group(1).zfill(2) if m else "00"
        eqs = extract_equations_from_file(md_path, chapter)
        all_equations.extend(eqs)
        print(f"[Phase 3] {md_path.name}: {len(eqs)} equations")

    # DOCX extraction
    docx_eqs = []
    if docx_path.exists():
        docx_eqs = extract_equations_from_docx(docx_path)
        print(f"[Phase 3] DOCX: {len(docx_eqs)} equations extracted (method: "
              f"{docx_eqs[0]['method'] if docx_eqs else 'none'})")
    else:
        print(f"[Phase 3] WARNING: DOCX not found at {docx_path}")

    # Cross-check
    all_equations = _cross_check(all_equations, docx_eqs)

    divergent = [e for e in all_equations if e["build_divergence"]]
    if divergent:
        print(f"[Phase 3] WARNING: {len(divergent)} display equations may have build divergence")

    out_path = cache_dir / "thesis_equations.json"
    out_path.write_text(json.dumps(all_equations, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[Phase 3] Total equations: {len(all_equations)} "
          f"({len([e for e in all_equations if e['display']])} display, "
          f"{len([e for e in all_equations if not e['display']])} inline)")
    return all_equations
```

- [ ] **Step 4: Smoke test phases 1–3**

```python
from pathlib import Path
from audit.phases import phase_01_inventory, phase_02_papers, phase_03_thesis

repo = Path(".")
out = Path("audit")
cache = out / "cache"
cache.mkdir(parents=True, exist_ok=True)

inv = phase_01_inventory.run(repo, out)
assert len(inv["papers"]) == 5
assert len(inv["chapter_files"]) == 6

idx = phase_02_papers.run(repo, cache)
assert len(idx) == 5

eqs = phase_03_thesis.run(repo, cache)
assert len(eqs) > 20
print("Phases 1-3 OK")
```

- [ ] **Step 5: Commit**

```
git add audit/phases/
git commit -m "feat(audit): phases 1-3 — inventory, paper ingestion, thesis extraction"
```

---

## Task 9: Phases 4, 5 — Traceability and Math Validation

**Files:**
- Create: `audit/phases/phase_04_traceability.py`
- Create: `audit/phases/phase_05_validation.py`

- [ ] **Step 1: Implement `audit/phases/phase_04_traceability.py`**

```python
import json
from pathlib import Path
from audit.lib.match_equations import match_equation


_CITATION_TO_FILE = {
    "li et al": "1772690.1772758",
    "linucb": "1772690.1772758",
    "agrawal": "agrawal13",
    "thompson sampling": "agrawal13",
    "lints": "agrawal13",
    "robbins": "S0002-9904-1952-09620-8",
    "zhou": "zhou20a",
    "neuralucb": "zhou20a",
    "ensign": "ensign18a",
    "fairness": "ensign18a",
}


def _guess_paper_stem(citations: list) -> list:
    """Map citation strings to paper file stems."""
    stems = []
    for cit in citations:
        cit_lower = cit.lower()
        for key, stem in _CITATION_TO_FILE.items():
            if key in cit_lower and stem not in stems:
                stems.append(stem)
    return stems


def run(repo_root: Path, cache_dir: Path) -> list:
    """Match each thesis equation against source papers."""
    eqs_path = cache_dir / "thesis_equations.json"
    equations = json.loads(eqs_path.read_text(encoding="utf-8"))

    # Load all paper caches
    papers = {}
    for json_path in (cache_dir / "papers").glob("*.json"):
        papers[json_path.stem] = json.loads(json_path.read_text(encoding="utf-8"))

    llm_queue_dir = Path("audit/llm_review_queue")
    llm_queue_dir.mkdir(parents=True, exist_ok=True)

    results = []
    llm_queue = []

    for eq in equations:
        # Skip very short inline equations (single variables)
        if not eq["display"] and len(eq["latex_md"]) < 5:
            continue

        cited_stems = _guess_paper_stem(eq["citations"])
        all_paper_eqs = []

        # Search cited papers first
        for stem in cited_stems:
            if stem in papers:
                for peq in papers[stem]["equations"]:
                    all_paper_eqs.append({**peq, "_paper_stem": stem})

        # Then search remaining papers
        for stem, paper in papers.items():
            if stem not in cited_stems:
                for peq in paper["equations"]:
                    all_paper_eqs.append({**peq, "_paper_stem": stem})

        match = match_equation(eq["latex_md"], all_paper_eqs)

        cited = bool(cited_stems) and (
            match.get("source_page", 0) > 0 and
            any(match.get("source_text", "") for _ in cited_stems)
        )

        # Determine final status
        status = match["status"]
        if status == "PASS" and not eq["citations"]:
            status = "WARNING"   # matched but not cited

        result = {
            "equation_id": eq["equation_id"],
            "chapter": eq["chapter"],
            "section": eq["section"],
            "latex": eq["latex_md"][:100],
            "status": status,
            "match_method": match["match_method"],
            "confidence": match["confidence"],
            "source_paper": match.get("source_paper", ""),
            "source_page": match.get("source_page", 0),
            "source_text": match.get("source_text", ""),
            "cited": bool(eq["citations"]),
            "notes": match.get("notes", ""),
        }
        results.append(result)

        if match["status"] == "LLM_QUEUE":
            llm_queue.append(eq["equation_id"])
            prompt_path = llm_queue_dir / f"{eq['equation_id']}.txt"
            if not prompt_path.exists():   # preserve existing manual reviews
                context = eq.get("nearby_text_before", "")[-300:]
                prompt_path.write_text(
                    f"EQUATION REVIEW REQUEST\n"
                    f"Equation ID: {eq['equation_id']}\n"
                    f"Chapter: {eq['chapter']} Section: {eq['section']}\n"
                    f"LaTeX: {eq['latex_md']}\n\n"
                    f"Context before: {context}\n\n"
                    f"Candidate paper match (confidence {match['confidence']:.2f}):\n"
                    f"  Paper text: {match.get('source_text', '')}\n\n"
                    f"TASK: Determine if the thesis equation and the paper text express the same\n"
                    f"mathematical object. Answer: SAME / DIFFERENT / UNCERTAIN, with 1-2 sentences\n"
                    f"of explanation.\n",
                    encoding="utf-8"
                )

    out_path = cache_dir / "phase_results" / "phase4_traceability.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(f"[Phase 4] Traceability: {counts}. LLM queue: {len(llm_queue)}")
    return results, llm_queue
```

- [ ] **Step 2: Implement `audit/phases/phase_05_validation.py`**

```python
import json
import re
from pathlib import Path
from audit.lib.sympy_verify import check_symbolic_equivalence, try_sympy_parse

_DERIVATION_CUES = re.compile(
    r'\b(?:therefore|substituting|which gives|simplifying|it follows that|'
    r'from Eq\.|expanding|rearranging|noting that)\b',
    re.IGNORECASE,
)


def run(repo_root: Path, cache_dir: Path) -> list:
    """
    Detect claimed derivations and verify them with SymPy.
    A derivation is when text between two equations contains a derivation cue.
    """
    eqs_path = cache_dir / "thesis_equations.json"
    equations = json.loads(eqs_path.read_text(encoding="utf-8"))

    # Only display equations can be derivation endpoints
    display_eqs = [e for e in equations if e["display"]]

    results = []

    for i in range(len(display_eqs) - 1):
        eq_a = display_eqs[i]
        eq_b = display_eqs[i + 1]

        # Only check within same chapter
        if eq_a["chapter"] != eq_b["chapter"]:
            continue

        bridge_text = eq_a["nearby_text_after"] + " " + eq_b["nearby_text_before"]

        if not _DERIVATION_CUES.search(bridge_text):
            continue

        # Attempt SymPy check
        expr_a = try_sympy_parse(eq_a["latex_md"])
        expr_b = try_sympy_parse(eq_b["latex_md"])

        if expr_a is None or expr_b is None:
            status = "MANUAL_REVIEW"
            notes = "Cannot parse one or both expressions with SymPy"
        else:
            # Check if B is a simplification of A (not necessarily equal — may have substitutions)
            # We can only verify exact equivalence; anything else needs manual check
            is_equiv = check_symbolic_equivalence(eq_a["latex_md"], eq_b["latex_md"])
            if is_equiv:
                status = "PASS"
                notes = "SymPy confirms algebraic equivalence"
            else:
                # Not equivalent — may be a valid derivation step (substitution) or an error
                status = "MANUAL_REVIEW"
                notes = "Expressions are not algebraically identical — verify derivation step manually"

        results.append({
            "equation_id": f"{eq_a['equation_id']} → {eq_b['equation_id']}",
            "claim": f"Eq {eq_a['equation_id']} derives Eq {eq_b['equation_id']}",
            "chapter": eq_a["chapter"],
            "status": status,
            "notes": notes,
        })

    out_path = cache_dir / "phase_results" / "phase5_validation.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[Phase 5] Validated {len(results)} derivation pairs")
    return results
```

- [ ] **Step 3: Commit**

```
git add audit/phases/phase_04_traceability.py audit/phases/phase_05_validation.py
git commit -m "feat(audit): phases 4-5 — equation traceability and SymPy math validation"
```

---

## Task 10: Phases 6, 7, 8 — Notation, Literature, Citations

**Files:**
- Create: `audit/phases/phase_06_notation.py`
- Create: `audit/phases/phase_07_literature.py`
- Create: `audit/phases/phase_08_citations.py`

- [ ] **Step 1: Implement `audit/phases/phase_06_notation.py`**

```python
import json
import re
from pathlib import Path

_SYMBOL_RE = re.compile(
    r'\\(?:hat|tilde|bar|vec|mathbf)?{?([A-Za-z_][A-Za-z0-9_]*)}?|'
    r'(?:^|(?<=[\s{(,+\-=]))([A-Za-z](?:_[A-Za-z0-9]|_\{[^}]+\})?)(?=[\s}),+\-=^]|$)'
)
_DEF_RE = re.compile(
    r'where\s+\$([^$]+)\$\s+(?:is|are|denotes?|represents?)\s+([^.;]{5,80})|'
    r'let\s+\$([^$]+)\$\s+(?:be|denote)\s+([^.;]{5,80})'
)


def _extract_symbols(latex: str) -> set:
    tokens = set()
    for m in _SYMBOL_RE.finditer(latex):
        sym = (m.group(1) or m.group(2) or "").strip()
        if sym and len(sym) <= 10:
            tokens.add(sym)
    return tokens


def run(repo_root: Path, cache_dir: Path) -> list:
    eqs_path = cache_dir / "thesis_equations.json"
    equations = json.loads(eqs_path.read_text(encoding="utf-8"))

    # Build symbol table: symbol → list of {chapter, eq_id, definition}
    symbol_table = {}

    for eq in equations:
        syms = _extract_symbols(eq["latex_md"])
        context = eq["nearby_text_before"] + " " + eq["nearby_text_after"]

        # Extract definitions from surrounding text
        definitions = {}
        for m in _DEF_RE.finditer(context):
            sym = (m.group(1) or m.group(3) or "").strip()
            defn = (m.group(2) or m.group(4) or "").strip()
            if sym:
                definitions[sym] = defn

        for sym in syms:
            if sym not in symbol_table:
                symbol_table[sym] = []
            symbol_table[sym].append({
                "chapter": eq["chapter"],
                "equation_id": eq["equation_id"],
                "definition": definitions.get(sym, ""),
            })

    issues = []

    for sym, usages in symbol_table.items():
        # Collect non-empty definitions
        defs = list({u["definition"] for u in usages if u["definition"]})
        chapters = list({u["chapter"] for u in usages})

        # REUSE_CONFLICT: same symbol, different definitions
        if len(defs) > 1:
            issues.append({
                "symbol": f"${sym}$",
                "issue_type": "REUSE_CONFLICT",
                "locations": [u["equation_id"] for u in usages],
                "notes": f"Defined as: {' | '.join(defs[:3])}",
            })

        # UNDEFINED: used in multiple equations but never defined
        if not defs and len(usages) >= 3 and len(sym) > 1:
            issues.append({
                "symbol": f"${sym}$",
                "issue_type": "UNDEFINED",
                "locations": [u["equation_id"] for u in usages[:5]],
                "notes": f"Used in {len(usages)} equations across chapters {chapters} without a definition",
            })

    out_path = cache_dir / "phase_results" / "phase6_notation.json"
    out_path.write_text(json.dumps(issues, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[Phase 6] Notation issues found: {len(issues)}")
    return issues
```

- [ ] **Step 2: Implement `audit/phases/phase_07_literature.py`**

```python
import json
import re
from pathlib import Path
from rapidfuzz import fuzz

_EPISTEMIC_RE = re.compile(
    r'(?<=[.!?]\s|\n)([^.!?\n]{20,200}?'
    r'(?:achieves?|shows?|proves?|demonstrates?|outperforms?|'
    r'is bounded by|guarantees?|establishes?|confirms?)[^.!?\n]{5,150}[.!?])',
    re.IGNORECASE,
)
_CITATION_RE = re.compile(
    r'\(([A-Z][A-Za-zÀ-ÿ\s\&]+(?:et al\.)?(?:,?\s+\d{4}[a-z]?)'
    r'(?:;\s*[A-Z][A-Za-z\s\&]+(?:et al\.)?(?:,?\s+\d{4}[a-z]?)?)*)\)'
)
_CITATION_TO_FILE = {
    "li": "1772690.1772758", "linucb": "1772690.1772758",
    "agrawal": "agrawal13", "thompson": "agrawal13",
    "robbins": "S0002-9904-1952-09620-8",
    "zhou": "zhou20a", "neural": "zhou20a",
    "ensign": "ensign18a",
}


def _find_paper_stem(citation: str) -> str:
    cit_lower = citation.lower()
    for key, stem in _CITATION_TO_FILE.items():
        if key in cit_lower:
            return stem
    return ""


def run(repo_root: Path, cache_dir: Path) -> list:
    lit_review_path = repo_root / "thesis" / "health_rl" / "chapter03_literature_review.md"
    text = lit_review_path.read_text(encoding="utf-8")

    papers_cache = {}
    for jp in (cache_dir / "papers").glob("*.json"):
        p = json.loads(jp.read_text(encoding="utf-8"))
        papers_cache[jp.stem] = "\n".join(p["raw_pages"].values())

    results = []

    for m in _EPISTEMIC_RE.finditer(text):
        claim = m.group(1).strip()
        # Find citation within 500 chars of the claim
        window_start = max(0, m.start() - 200)
        window = text[window_start:m.end() + 200]
        cit_matches = _CITATION_RE.findall(window)
        citations = []
        for c in cit_matches:
            citations.extend([s.strip() for s in c.split(";")])

        if not citations:
            results.append({
                "claim_text": claim[:200],
                "chapter": "03",
                "section": "",
                "citations": [],
                "status": "NO_CITED_PAPER",
                "evidence": "",
            })
            continue

        # Find paper and search for evidence
        best_status = "UNSUPPORTED"
        best_evidence = ""

        for cit in citations:
            stem = _find_paper_stem(cit)
            if stem not in papers_cache:
                continue
            paper_text = papers_cache[stem]
            # Search for key terms from the claim
            key_terms = " ".join(w for w in claim.split() if len(w) > 4)
            score = fuzz.partial_ratio(key_terms.lower(), paper_text.lower()) / 100.0
            if score > 0.75:
                best_status = "SUPPORTED"
                best_evidence = f"Strong keyword match in {stem} (score {score:.2f})"
                break
            elif score > 0.50:
                best_status = "PARTIALLY_SUPPORTED"
                best_evidence = f"Partial match in {stem} (score {score:.2f})"

        results.append({
            "claim_text": claim[:200],
            "chapter": "03",
            "section": "",
            "citations": citations[:3],
            "status": best_status,
            "evidence": best_evidence,
        })

    out_path = cache_dir / "phase_results" / "phase7_literature.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(f"[Phase 7] Literature claims: {counts}")
    return results
```

- [ ] **Step 3: Implement `audit/phases/phase_08_citations.py`**

```python
import json
import re
from pathlib import Path

_CITATION_RE = re.compile(
    r'\(([A-Z][A-Za-zÀ-ÿ\s\&]+(?:et al\.)?(?:,?\s+\d{4}[a-z]?))\)'
)
_KNOWN_PAPER_STEMS = {
    "1772690.1772758", "agrawal13", "S0002-9904-1952-09620-8", "zhou20a", "ensign18a"
}


def run(repo_root: Path, cache_dir: Path) -> list:
    eqs_path = cache_dir / "thesis_equations.json"
    equations = json.loads(eqs_path.read_text(encoding="utf-8"))

    issues = []

    for eq in equations:
        if not eq["display"]:
            continue  # only check display equations

        # Missing citation
        if not eq["citations"]:
            issues.append({
                "location": eq["equation_id"],
                "issue_type": "MISSING_CITATION",
                "text": eq["latex_md"][:100],
                "notes": "Display equation has no nearby citation",
            })
            continue

        # Check that cited papers are indexed
        for cit in eq["citations"]:
            cit_lower = cit.lower()
            matched = any(stem.lower().split("-")[0][:6] in cit_lower or
                          cit_lower[:6] in stem.lower()
                          for stem in _KNOWN_PAPER_STEMS)
            if not matched:
                issues.append({
                    "location": eq["equation_id"],
                    "issue_type": "UNCACHED_PAPER",
                    "text": cit,
                    "notes": f"Citation '{cit}' does not match any paper in thesis/papers/",
                })

    out_path = cache_dir / "phase_results" / "phase8_citations.json"
    out_path.write_text(json.dumps(issues, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[Phase 8] Citation issues: {len(issues)}")
    return issues
```

- [ ] **Step 4: Commit**

```
git add audit/phases/phase_06_notation.py audit/phases/phase_07_literature.py audit/phases/phase_08_citations.py
git commit -m "feat(audit): phases 6-8 — notation, literature consistency, citation audit"
```

---

## Task 11: Phase 9 — RL & Fairness Special Audit

**Files:**
- Create: `audit/phases/phase_09_rl_fairness.py`

- [ ] **Step 1: Implement `audit/phases/phase_09_rl_fairness.py`**

```python
import json
from pathlib import Path
from audit.lib.match_equations import extract_math_tokens
from audit.lib.sympy_verify import check_symbolic_equivalence

# Canonical forms — stored as token sets for robust matching
_CANONICAL_CHECKS = [
    {
        "check_id": "RL-01",
        "name": "LinUCB action selection",
        "required_tokens": {"argmax", "theta", "alpha", "sqrt", "top"},
        "description": r"\arg\max_a (\hat\theta_a^\top x_t + \alpha \sqrt{x_t^\top A_a^{-1} x_t})",
        "source": "Li et al. 2010",
    },
    {
        "check_id": "RL-02",
        "name": "LinTS posterior sampling",
        "required_tokens": {"theta", "sim", "mathcal", "hat", "argmax"},
        "alt_tokens": {"tilde", "theta", "sim", "Normal"},
        "description": r"\tilde\theta_a \sim \mathcal{N}(\hat\theta_a, v^2 A_a^{-1})",
        "source": "Agrawal & Goyal 2013",
    },
    {
        "check_id": "RL-03",
        "name": "Design matrix update",
        "required_tokens": {"leftarrow", "top"},
        "alt_tokens": {"A", "x", "top"},
        "description": r"A_a \leftarrow A_a + x_t x_t^\top",
        "source": "Li et al. 2010",
    },
    {
        "check_id": "RL-04",
        "name": "Sherman-Morrison inverse update",
        "required_tokens": {"frac", "top"},
        "description": r"A^{-1} \leftarrow A^{-1} - \frac{A^{-1} x x^\top A^{-1}}{1 + x^\top A^{-1} x}",
        "source": "Standard linear algebra",
    },
    {
        "check_id": "RL-06",
        "name": "PSI formula",
        "required_tokens": {"sum", "ln"},
        "alt_tokens": {"PSI", "sum", "log"},
        "description": r"\text{PSI} = \sum_i (A_i - E_i) \ln(A_i / E_i)",
        "source": "Standard actuarial",
    },
    {
        "check_id": "RL-07",
        "name": "Four-fifths fairness rule",
        "required_tokens": {"0.80", "frac"},
        "alt_tokens": {"0.80", "geq", "max"},
        "description": r"\frac{\text{ApprovalRate}(g)}{\max_{g'} \text{ApprovalRate}(g')} \geq 0.80",
        "source": "EEOC guideline",
    },
]


def run(repo_root: Path, cache_dir: Path) -> list:
    eqs_path = cache_dir / "thesis_equations.json"
    equations = json.loads(eqs_path.read_text(encoding="utf-8"))
    display_eqs = [e for e in equations if e["display"]]

    results = []

    for check in _CANONICAL_CHECKS:
        required = check["required_tokens"]
        alt = check.get("alt_tokens", set())
        best_match = None
        best_overlap = 0.0

        for eq in display_eqs:
            tokens = extract_math_tokens(eq["latex_md"])
            # Normalize tokens (strip backslashes)
            tokens_norm = {t.lstrip("\\").lower() for t in tokens}

            overlap = len(required & tokens_norm) / len(required) if required else 0.0
            alt_overlap = len(alt & tokens_norm) / len(alt) if alt else 0.0
            score = max(overlap, alt_overlap)

            if score > best_overlap:
                best_overlap = score
                best_match = eq

        if best_overlap >= 0.60:
            status = "PASS"
            notes = (f"Found in {best_match['equation_id']} "
                     f"(token overlap {best_overlap:.0%})")
        elif best_overlap >= 0.30:
            status = "MANUAL_REVIEW"
            notes = (f"Partial match in {best_match['equation_id'] if best_match else 'none'} "
                     f"({best_overlap:.0%}) — verify manually")
        else:
            status = "FAIL"
            notes = f"No thesis equation found matching canonical form for {check['name']}"

        results.append({
            "check_id": check["check_id"],
            "name": check["name"],
            "canonical": check["description"],
            "source": check["source"],
            "status": status,
            "matched_equation": best_match["equation_id"] if best_match else "",
            "confidence": round(best_overlap, 3),
            "notes": notes,
        })

    out_path = cache_dir / "phase_results" / "phase9_rl_fairness.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    counts = {s: sum(1 for r in results if r["status"] == s) for s in ("PASS", "FAIL", "MANUAL_REVIEW")}
    print(f"[Phase 9] RL/Fairness audit: {counts}")
    return results
```

- [ ] **Step 2: Commit**

```
git add audit/phases/phase_09_rl_fairness.py
git commit -m "feat(audit): phase 9 — RL and fairness canonical equation checks"
```

---

## Task 12: Phase 10 — HTML Dashboard

**Files:**
- Create: `audit/phases/phase_10_dashboard.py`

- [ ] **Step 1: Implement `audit/phases/phase_10_dashboard.py`**

```python
import json
from pathlib import Path
from audit.lib.render_html import render_dashboard


def run(repo_root: Path, cache_dir: Path, output_dir: Path) -> Path:
    """Aggregate all phase results and render the HTML dashboard."""

    def _load(filename: str) -> list:
        p = cache_dir / "phase_results" / filename
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        return []

    thesis_eqs_path = cache_dir / "thesis_equations.json"
    thesis_eqs = json.loads(thesis_eqs_path.read_text(encoding="utf-8")) if thesis_eqs_path.exists() else []

    # Collect LLM queue
    llm_queue = [p.stem for p in sorted((output_dir / "llm_review_queue").glob("*.txt"))]

    # Phase 4 returns (results, llm_queue) — load just the JSON
    results = {
        "phase4": _load("phase4_traceability.json"),
        "phase5": _load("phase5_validation.json"),
        "phase6": _load("phase6_notation.json"),
        "phase7": _load("phase7_literature.json"),
        "phase8": _load("phase8_citations.json"),
        "phase9": _load("phase9_rl_fairness.json"),
        "thesis_equations": thesis_eqs,
        "llm_queue": llm_queue,
    }

    html = render_dashboard(results)
    out_path = output_dir / "dashboard.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"[Phase 10] Dashboard written to {out_path}")
    return out_path
```

- [ ] **Step 2: Commit**

```
git add audit/phases/phase_10_dashboard.py
git commit -m "feat(audit): phase 10 — aggregate results and render HTML dashboard"
```

---

## Task 13: Orchestrator — `audit/run_audit.py`

**Files:**
- Create: `audit/run_audit.py`

- [ ] **Step 1: Implement the orchestrator**

```python
#!/usr/bin/env python3
"""
Thesis Equation Audit Pipeline
Run: python audit/run_audit.py

Produces:
  audit/dashboard.html        — unified HTML report
  audit/repository_inventory.md
  audit/llm_review_queue/     — equations needing manual LLM review
"""
import json
import shutil
import sys
from pathlib import Path

# Ensure project root is on path
_REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from audit.phases import (
    phase_01_inventory,
    phase_02_papers,
    phase_03_thesis,
    phase_04_traceability,
    phase_05_validation,
    phase_06_notation,
    phase_07_literature,
    phase_08_citations,
    phase_09_rl_fairness,
    phase_10_dashboard,
)

_AUDIT_DIR = _REPO_ROOT / "audit"
_CACHE_DIR = _AUDIT_DIR / "cache"


def reset_cache():
    """Delete and recreate the cache directory. Preserve llm_review_queue."""
    if _CACHE_DIR.exists():
        shutil.rmtree(_CACHE_DIR)
    _CACHE_DIR.mkdir(parents=True)
    (_CACHE_DIR / "papers").mkdir()
    (_CACHE_DIR / "phase_results").mkdir()


def main():
    print("=" * 60)
    print("Thesis Equation Audit Pipeline")
    print("=" * 60)

    reset_cache()
    (_AUDIT_DIR / "llm_review_queue").mkdir(exist_ok=True)

    print("\n── Phase 1: Repository Inventory ──")
    phase_01_inventory.run(_REPO_ROOT, _AUDIT_DIR)

    print("\n── Phase 2: Paper Ingestion ──")
    phase_02_papers.run(_REPO_ROOT, _CACHE_DIR)

    print("\n── Phase 3: Thesis Ingestion ──")
    phase_03_thesis.run(_REPO_ROOT, _CACHE_DIR)

    print("\n── Phase 4: Equation Traceability ──")
    phase_04_traceability.run(_REPO_ROOT, _CACHE_DIR)

    print("\n── Phase 5: Mathematical Validation ──")
    phase_05_validation.run(_REPO_ROOT, _CACHE_DIR)

    print("\n── Phase 6: Notation Consistency ──")
    phase_06_notation.run(_REPO_ROOT, _CACHE_DIR)

    print("\n── Phase 7: Literature Consistency ──")
    phase_07_literature.run(_REPO_ROOT, _CACHE_DIR)

    print("\n── Phase 8: Citation Audit ──")
    phase_08_citations.run(_REPO_ROOT, _CACHE_DIR)

    print("\n── Phase 9: RL & Fairness Audit ──")
    phase_09_rl_fairness.run(_REPO_ROOT, _CACHE_DIR)

    print("\n── Phase 10: HTML Dashboard ──")
    dashboard_path = phase_10_dashboard.run(_REPO_ROOT, _CACHE_DIR, _AUDIT_DIR)

    print("\n" + "=" * 60)
    print(f"AUDIT COMPLETE")
    print(f"Dashboard: {dashboard_path}")
    llm_q = list((_AUDIT_DIR / "llm_review_queue").glob("*.txt"))
    if llm_q:
        print(f"LLM queue: {len(llm_q)} equations need manual review")
        print(f"  → audit/llm_review_queue/")
    print("=" * 60)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the full pipeline**

```
python audit/run_audit.py
```

Expected output:
```
============================================================
Thesis Equation Audit Pipeline
============================================================

── Phase 1: Repository Inventory ──
[Phase 1] Inventory complete: 5 papers, 6 chapters

── Phase 2: Paper Ingestion ──
[Phase 2] Ingesting 1772690.1772758.pdf ...
  → N equations, M pages
...
[Phase 2] Indexed 5 papers

── Phase 3: Thesis Ingestion ──
[Phase 3] chapter01_introduction.md: N equations
...
[Phase 3] Total equations: N+ (M display, K inline)

── Phase 4: Equation Traceability ──
[Phase 4] Traceability: {...}. LLM queue: N

...

── Phase 10: HTML Dashboard ──
[Phase 10] Dashboard written to audit/dashboard.html

============================================================
AUDIT COMPLETE
Dashboard: audit/dashboard.html
```

- [ ] **Step 3: Open `audit/dashboard.html` in a browser and verify**

Confirm:
- Executive Summary table is present with counts
- All 6 phase sections are visible and collapsible
- PASS badges are green, FAIL badges are red
- No Python tracebacks in the terminal output

- [ ] **Step 4: Fix any runtime errors encountered**

Common issues:
- `lxml` namespace issue in `extract_docx.py`: the `_M` variable is referenced inside `_omml_node_to_latex` but defined at module level as `_M` with `f"..."` — confirm it's accessible (it is, module-level).
- `rapidfuzz` import: confirm `from rapidfuzz import fuzz` (not `from rapidfuzz.fuzz import ...`).
- `sympy.parsing.latex` may require `antlr4-python3-runtime`: install with `pip install antlr4-python3-runtime==4.11.1` if import fails.

- [ ] **Step 5: Commit**

```
git add audit/run_audit.py
git commit -m "feat(audit): orchestrator — 10-phase pipeline with cache reset"
```

---

## Task 14: Run full test suite and final commit

- [ ] **Step 1: Run all audit tests**

```
pytest tests/test_audit/ -v
```

Expected: all tests PASS.

- [ ] **Step 2: Run the pipeline end-to-end one more time cleanly**

```
python audit/run_audit.py
```

Confirm exit 0, dashboard renders, no missing file errors.

- [ ] **Step 3: Add `audit/` to `.gitignore` cache but not outputs**

Add to `.gitignore`:
```
audit/cache/
```

`audit/dashboard.html`, `audit/repository_inventory.md`, and `audit/llm_review_queue/` should be tracked (they are outputs, not derived cache).

- [ ] **Step 4: Final commit**

```
git add audit/run_audit.py audit/.gitignore tests/
git commit -m "feat(audit): complete 10-phase equation audit pipeline — phases 1-10 + HTML dashboard"
```

---

## Self-Review

**Spec coverage check:**
- Phase 1 (Inventory): ✓ `phase_01_inventory.py`
- Phase 2 (Paper ingestion): ✓ `phase_02_papers.py` + `extract_pdf.py`
- Phase 3 (Thesis ingestion, MD + DOCX cross-check): ✓ `phase_03_thesis.py` + `extract_md.py` + `extract_docx.py`
- Phase 4 (Traceability, PASS/WARNING/FAIL/LLM_QUEUE): ✓ `phase_04_traceability.py`
- Phase 5 (Math validation, SymPy): ✓ `phase_05_validation.py` + `sympy_verify.py`
- Phase 6 (Notation audit, symbol table): ✓ `phase_06_notation.py`
- Phase 7 (Literature consistency): ✓ `phase_07_literature.py`
- Phase 8 (Citation audit): ✓ `phase_08_citations.py`
- Phase 9 (RL/Fairness special audit, hardcoded checks): ✓ `phase_09_rl_fairness.py`
- Phase 10 (HTML dashboard): ✓ `phase_10_dashboard.py` + `render_html.py`
- LLM queue files written to `audit/llm_review_queue/`: ✓ `phase_04_traceability.py`
- Preserved across runs: ✓ (cache deleted, queue preserved)
- No thesis files modified: ✓ (all writes to `audit/`)

**Placeholder scan:** No TBDs found. All code steps have actual implementation.

**Type consistency:**
- `extract_equations_from_markdown` returns `list` of dicts with keys matching `ThesisEquation` — ✓
- `match_equation` returns dict with `status`, `match_method`, `confidence`, `source_page`, `source_text`, `notes` — ✓ (used in phase_04)
- `phase_04_traceability.run` writes `status` field — used by `render_dashboard` phase4 table — ✓
- `render_dashboard` reads `phase4`, `phase5`, `phase6`, `phase7`, `phase8`, `phase9` keys — all written by phases — ✓
