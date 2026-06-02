"""Phase 9: RL and Fairness Special Audit.

Validates thesis against canonical equations for:
- LinUCB action selection (Li et al. 2010)
- LinTS posterior sampling (Agrawal & Goyal 2013)
- Design matrix update
- Sherman-Morrison inverse
- Cumulative regret definition
- PSI formula (actuarial)
- Four-fifths fairness rule (EEOC)

Token-based matching against extracted thesis equations.
"""

import json
from pathlib import Path
from audit.lib.match_equations import extract_math_tokens


# Canonical checks for the thesis's core domain equations
_CANONICAL_CHECKS = [
    {
        "check_id": "RL-01",
        "name": "LinUCB action selection",
        "required_tokens": {"argmax", "theta", "alpha", "sqrt"},
        "alt_tokens": {"argmax", "hat", "alpha", "sqrt", "top"},
        "description": r"\arg\max_a (\hat\theta_a^\top x_t + \alpha \sqrt{x_t^\top A_a^{-1} x_t})",
        "source": "Li et al. 2010",
    },
    {
        "check_id": "RL-02",
        "name": "LinTS posterior sampling",
        "required_tokens": {"theta", "sim", "mathcal"},
        "alt_tokens": {"tilde", "theta", "Normal", "hat"},
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
        "alt_tokens": {"frac", "leftarrow"},
        "description": r"A^{-1} \leftarrow A^{-1} - \frac{A^{-1} x x^\top A^{-1}}{1 + x^\top A^{-1} x}",
        "source": "Standard linear algebra",
    },
    {
        "check_id": "RL-05",
        "name": "Cumulative regret definition",
        "required_tokens": {"sum", "r"},
        "alt_tokens": {"R", "sum", "regret"},
        "description": r"R_T = \sum_t (r^*_t - r_t)",
        "source": "Lattimore & Szepesvari 2020",
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
    """
    Run RL/Fairness canonical equation checks.

    Args:
        repo_root: Repository root directory
        cache_dir: Cache directory containing thesis_equations.json

    Returns:
        List of result dicts with keys: check_id, name, canonical, source,
        status (PASS/FAIL/MANUAL_REVIEW), matched_equation, confidence, notes
    """
    eqs_path = cache_dir / "thesis_equations.json"
    equations = json.loads(eqs_path.read_text(encoding="utf-8"))
    display_eqs = [e for e in equations if e.get("display")]

    results = []

    for check in _CANONICAL_CHECKS:
        required = check["required_tokens"]
        alt = check.get("alt_tokens", set())
        best_match = None
        best_overlap = 0.0

        for eq in display_eqs:
            tokens = extract_math_tokens(eq.get("latex_md", ""))
            # Normalize tokens (strip backslashes, lowercase)
            tokens_norm = {t.lstrip("\\").lower().replace(" ", "") for t in tokens}

            overlap = len(required & tokens_norm) / len(required) if required else 0.0
            alt_overlap = len(alt & tokens_norm) / len(alt) if alt else 0.0
            score = max(overlap, alt_overlap)

            if score > best_overlap:
                best_overlap = score
                best_match = eq

        if best_overlap >= 0.60:
            status = "PASS"
            eq_id = best_match["equation_id"] if best_match else ""
            notes = f"Found in {eq_id} (token overlap {best_overlap:.0%})"
        elif best_overlap >= 0.30:
            status = "MANUAL_REVIEW"
            eq_id = best_match["equation_id"] if best_match else "none"
            notes = f"Partial match in {eq_id} ({best_overlap:.0%}) — verify manually"
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
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    counts = {s: sum(1 for r in results if r["status"] == s)
              for s in ("PASS", "FAIL", "MANUAL_REVIEW")}
    print(f"[Phase 9] RL/Fairness audit: {counts}")
    return results
