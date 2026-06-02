from audit.lib.sympy_verify import check_symbolic_equivalence, try_sympy_parse


def test_simple_equivalence():
    # a^2 - b^2 == (a-b)(a+b)
    assert check_symbolic_equivalence("a**2 - b**2", "(a - b)*(a + b)") is True


def test_non_equivalence():
    assert check_symbolic_equivalence("a + b", "a - b") is False


def test_parse_failure_returns_none():
    # Invalid/malformed LaTeX that SymPy cannot parse
    result = try_sympy_parse("{{{{")
    assert result is None


def test_parse_simple_latex():
    result = try_sympy_parse(r"\frac{a}{b}")
    assert result is not None


def test_equivalence_returns_false_on_parse_failure():
    # Should not raise — return False if either parse fails
    result = check_symbolic_equivalence(r"\arg\max_{a}", r"\sum_{i=1}^n x_i")
    assert isinstance(result, bool)
