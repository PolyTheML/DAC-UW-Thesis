"""
Fuzzy equation matching for thesis validation against papers.

Uses Jaccard token overlap + character similarity to match LaTeX equations.
Returns status (PASS/LLM_QUEUE/FAIL) + confidence [0, 1].
"""

import re
from rapidfuzz import fuzz


# Regex to extract mathematical tokens: LaTeX commands, identifiers, numbers
_LATEX_TOKEN_RE = re.compile(
    r'\\(?:hat|tilde|bar|vec|mathbf|mathcal|argmax|argmin|arg|'
    r'sum|prod|sqrt|frac|log|exp|theta|alpha|beta|gamma|lambda|mu|sigma|'
    r'epsilon|varepsilon|rho|delta|phi|psi|omega|Omega|Sigma|Lambda|top|'
    r'leftarrow|rightarrow|cdot|times|in|forall|exists|mathbb|sim|'
    r'left|right|Bigl|Bigr|Bigm)|'
    r'[A-Za-z_][A-Za-z0-9_]*(?:_\{[^}]+\}|_[A-Za-z0-9])?|'
    r'\d+(?:\.\d+)?'
)

# Map Unicode math symbols to their LaTeX token equivalents
_GREEK_MAP = {
    'θ': 'theta', 'α': 'alpha', 'β': 'beta', 'γ': 'gamma',
    'λ': 'lambda', 'μ': 'mu', 'σ': 'sigma', 'ε': 'epsilon',
    'ρ': 'rho', 'δ': 'delta', 'φ': 'phi', 'ψ': 'psi',
    'ω': 'omega', 'Ω': 'Omega', 'Σ': 'Sigma', 'Λ': 'Lambda',
    '∑': 'sum', '∏': 'prod', '∫': 'int', '√': 'sqrt',
    '∀': 'forall', '∃': 'exists',
    'θ̂': 'thetahat',  # combining hat
}

_WHITESPACE_RE = re.compile(r'\s+')


def extract_math_tokens(text: str) -> set:
    """
    Extract and normalize math tokens from LaTeX or PDF-extracted text.

    Returns a set of normalized token strings.
    Handles Greek letters, LaTeX commands, variables, and numbers.
    """
    # Replace Unicode math symbols with their token equivalents
    normalized = text
    for char, name in _GREEK_MAP.items():
        normalized = normalized.replace(char, name)

    # Extract all tokens (commands, identifiers, numbers)
    tokens = _LATEX_TOKEN_RE.findall(normalized)

    # Normalize: remove LaTeX backslashes, lowercase, collapse spaces
    result = set()
    for token in tokens:
        clean = token.lstrip('\\').lower().replace(' ', '')
        if clean:
            result.add(clean)

    return result


def _normalize(text: str) -> str:
    """Normalize text for string comparison: lowercase, collapse whitespace."""
    return _WHITESPACE_RE.sub(' ', text.lower()).strip()


def _fuzzy_score(thesis_latex: str, paper_text: str) -> float:
    """
    Score similarity between thesis LaTeX and paper text.

    Returns 0.0–1.0. Uses:
    1. Jaccard similarity of token sets
    2. Character-level fuzzy matching (token_set_ratio)

    Takes the max of both approaches.
    """
    thesis_tokens = extract_math_tokens(thesis_latex)
    paper_tokens = extract_math_tokens(paper_text)

    if not thesis_tokens:
        return 0.0

    # Jaccard: intersection / union
    overlap = thesis_tokens & paper_tokens
    union = thesis_tokens | paper_tokens
    jaccard = len(overlap) / len(union) if union else 0.0

    # Character-level fuzzy match (normalized texts)
    norm_thesis = _normalize(thesis_latex)
    norm_paper = _normalize(paper_text)
    char_score = fuzz.token_set_ratio(norm_thesis, norm_paper) / 100.0

    # Return max of both scores (Jaccard or char-based)
    return max(jaccard, char_score * 0.8)


def match_equation(thesis_latex: str, paper_equations: list, citation_paper: str = "") -> dict:
    """
    Find the best matching equation in the paper for a thesis equation.

    Args:
        thesis_latex: The equation to match (LaTeX string)
        paper_equations: List of dicts with keys: text, page, context_before, context_after
        citation_paper: Optional paper name for notes (unused in core matching)

    Returns:
        Dict with keys:
            - status: "PASS" (conf >= 0.75), "LLM_QUEUE" (0.40 <= conf < 0.75), "FAIL" (conf < 0.40)
            - match_method: "exact", "fuzzy", or "none"
            - confidence: float in [0, 1]
            - source_page: int
            - source_text: str (first 300 chars)
            - notes: str
    """
    if not paper_equations:
        return _result("FAIL", "none", 0.0, 0, "", "No paper equations to match against")

    best_score = 0.0
    best_eq = None

    for eq in paper_equations:
        # Check 1: Exact match on normalized text
        norm_thesis = _normalize(thesis_latex.replace('\\', ''))
        norm_paper = _normalize(eq["text"])

        if norm_thesis and norm_thesis in norm_paper:
            return _result("PASS", "exact", 1.0, eq["page"], eq["text"],
                          "Exact normalized match")

        # Check 2: Fuzzy token-based match
        score = _fuzzy_score(thesis_latex, eq["text"])
        if score > best_score:
            best_score = score
            best_eq = eq

    # Decision tree based on score
    if best_score >= 0.75:
        return _result("PASS", "fuzzy", best_score, best_eq["page"], best_eq["text"],
                      "")
    elif best_score >= 0.40:
        return _result("LLM_QUEUE", "fuzzy", best_score, best_eq["page"], best_eq["text"],
                      "Partial match — queued for LLM review")
    else:
        return _result("FAIL", "none", best_score, 0, "",
                      "No match found in any paper")


def _result(status: str, method: str, confidence: float,
            page: int, text: str, notes: str) -> dict:
    """Helper to construct result dict with consistent structure."""
    return {
        "status": status,
        "match_method": method,
        "confidence": round(confidence, 3),
        "source_page": page,
        "source_text": text[:300] if text else "",
        "notes": notes,
    }
