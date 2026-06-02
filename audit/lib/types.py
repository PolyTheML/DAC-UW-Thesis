from typing import TypedDict


class PaperEquation(TypedDict):
    text: str
    page: int
    context_before: str
    context_after: str


class Paper(TypedDict):
    title: str
    authors: list[str]
    year: str
    filename: str
    sections: list[dict[str, str]]
    equations: list[PaperEquation]
    raw_pages: dict[str, str]


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
    citations: list[str]


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
    locations: list[str]
    notes: str


class LiteratureClaim(TypedDict):
    claim_text: str
    chapter: str
    section: str
    citations: list[str]
    status: str              # "SUPPORTED" | "PARTIALLY_SUPPORTED" | "UNSUPPORTED" | "NO_CITED_PAPER"
    evidence: str


class CitationIssue(TypedDict):
    location: str            # equation_id or "ch03:para:5"
    issue_type: str          # "MISSING_CITATION" | "UNCACHED_PAPER"
    text: str
    notes: str
