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
