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
    Detect claimed derivations between consecutive display equations
    and verify them with SymPy where possible.
    """
    eqs_path = cache_dir / "thesis_equations.json"
    equations = json.loads(eqs_path.read_text(encoding="utf-8"))

    # Only display equations can be derivation endpoints
    display_eqs = [e for e in equations if e.get("display")]

    results = []

    for i in range(len(display_eqs) - 1):
        eq_a = display_eqs[i]
        eq_b = display_eqs[i + 1]

        # Only check within same chapter
        if eq_a["chapter"] != eq_b["chapter"]:
            continue

        bridge_text = (eq_a.get("nearby_text_after", "") + " " +
                       eq_b.get("nearby_text_before", ""))

        if not _DERIVATION_CUES.search(bridge_text):
            continue

        # Attempt SymPy check
        expr_a = try_sympy_parse(eq_a.get("latex_md", ""))
        expr_b = try_sympy_parse(eq_b.get("latex_md", ""))

        if expr_a is None or expr_b is None:
            status = "MANUAL_REVIEW"
            notes = "Cannot parse one or both expressions with SymPy"
        else:
            is_equiv = check_symbolic_equivalence(eq_a.get("latex_md", ""),
                                                   eq_b.get("latex_md", ""))
            if is_equiv:
                status = "PASS"
                notes = "SymPy confirms algebraic equivalence"
            else:
                status = "MANUAL_REVIEW"
                notes = "Expressions not identical — verify derivation step manually"

        results.append({
            "equation_id": f"{eq_a['equation_id']} -> {eq_b['equation_id']}",
            "claim": f"Eq {eq_a['equation_id']} derives Eq {eq_b['equation_id']}",
            "chapter": eq_a["chapter"],
            "status": status,
            "notes": notes,
        })

    out_path = cache_dir / "phase_results" / "phase5_validation.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[Phase 5] Validated {len(results)} derivation pairs")
    return results
