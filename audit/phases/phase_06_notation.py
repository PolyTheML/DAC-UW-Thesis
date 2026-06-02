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

    # Build symbol table: symbol -> list of {chapter, eq_id, definition}
    symbol_table: dict[str, list] = {}

    for eq in equations:
        syms = _extract_symbols(eq.get("latex_md", ""))
        context = (eq.get("nearby_text_before", "") + " " +
                   eq.get("nearby_text_after", ""))

        # Extract definitions from surrounding text
        definitions: dict[str, str] = {}
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
        defs = list({u["definition"] for u in usages if u["definition"]})
        chapters = list({u["chapter"] for u in usages})

        # REUSE_CONFLICT: same symbol, conflicting definitions
        if len(defs) > 1:
            issues.append({
                "symbol": f"${sym}$",
                "issue_type": "REUSE_CONFLICT",
                "locations": [u["equation_id"] for u in usages],
                "notes": f"Defined as: {' | '.join(defs[:3])}",
            })

        # UNDEFINED: used in 3+ equations but never defined
        if not defs and len(usages) >= 3 and len(sym) > 1:
            issues.append({
                "symbol": f"${sym}$",
                "issue_type": "UNDEFINED",
                "locations": [u["equation_id"] for u in usages[:5]],
                "notes": f"Used in {len(usages)} equations across chapters {chapters} with no definition found",
            })

    out_path = cache_dir / "phase_results" / "phase6_notation.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(issues, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[Phase 6] Notation issues found: {len(issues)}")
    return issues
