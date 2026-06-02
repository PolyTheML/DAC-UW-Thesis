import re
from pathlib import Path
import fitz   # pymupdf

_MATH_CHARS = set("αβγδεζηθλμνρστφχψω∑∏∫∂∇≤≥≠≈∈∉√")
_MATH_TOKEN_RE = re.compile(
    r'\b(?:argmax|argmin|arg\s+max|arg\s+min|UCB|regret|posterior|'
    r'E\s*\[|P\s*\(|N\s*\(|PSI)\b|'
    r'[θαβγλμσεv²]\s*[_^]|'
    r'[A-Z]_[a-z]|\b[a-z]_\{|'
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


def _extract_title_authors(first_pages_text: str) -> tuple[str, list[str]]:
    """Heuristic: title is the longest line in the first 40 lines; authors follow."""
    lines = [l.strip() for l in first_pages_text.split('\n') if l.strip()][:40]
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
    raw_pages: dict[str, str] = {}
    all_text = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        raw_pages[str(page_num + 1)] = text
        all_text.append(text)

    doc.close()

    full_text = "\n".join(all_text)
    first_two_pages = "\n".join(list(raw_pages.values())[:2])

    title, authors = _extract_title_authors(first_two_pages)
    year = _extract_year(first_two_pages)

    # Section headings: short numbered lines with uppercase start
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

    return {
        "title": title,
        "authors": authors,
        "year": year,
        "filename": pdf_path.name,
        "sections": sections[:50],
        "equations": equations,
        "raw_pages": raw_pages,
    }
