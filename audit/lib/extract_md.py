import re
from pathlib import Path

_DISPLAY_RE = re.compile(r'\$\$(.*?)\$\$', re.DOTALL)
_INLINE_RE = re.compile(r'(?<!\$)\$(?!\$)((?:[^$]|\n)+?)(?<!\$)\$(?!\$)')
_CITATION_RE = re.compile(
    r'\(([A-Z][A-Za-zÀ-ÿ\s\&,\.]+,\s*\d{4}[a-z]?(?:;\s*[A-Z][A-Za-zÀ-ÿ\s\&,\.]+,\s*\d{4}[a-z]?)*)\)'
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


def _extract_citations(window: str) -> list[str]:
    seen, result = set(), []
    for m in _CITATION_RE.finditer(window):
        for part in m.group(1).split(";"):
            s = part.strip()
            if s and s not in seen:
                seen.add(s)
                result.append(s)
    return result


def _context_window(text: str, start: int, end: int, chars: int = 400) -> tuple[str, str]:
    before = text[max(0, start - chars):start].strip()
    after = text[end:end + chars].strip()
    return before, after


def extract_equations_from_markdown(md_text: str, chapter: str) -> list[dict]:
    """
    Extract all display ($$...$$) and inline ($...$) equations from a markdown string.
    Returns a list of ThesisEquation-compatible dicts.
    """
    results = []
    counter: dict[str, int] = {"display": 0, "inline": 0}

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

    # Inline equations — skip those inside a display block
    display_spans = [(m.start(), m.end()) for m in _DISPLAY_RE.finditer(md_text)]

    def in_display(pos: int) -> bool:
        return any(s <= pos <= e for s, e in display_spans)

    for m in _INLINE_RE.finditer(md_text):
        if in_display(m.start()):
            continue
        latex = m.group(1).strip()
        if len(latex) < 2:
            continue
        # Skip currency amounts and non-math dollar signs
        if latex[0].isdigit() and not any(c in latex for c in r'\_{^'):
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


def extract_equations_from_file(md_path: Path, chapter: str) -> list[dict]:
    return extract_equations_from_markdown(md_path.read_text(encoding="utf-8"), chapter)
