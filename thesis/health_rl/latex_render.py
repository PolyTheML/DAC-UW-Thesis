"""Lightweight LaTeX -> Unicode renderer for ITC thesis DOCX builder.

Designed to cover the LaTeX surface area actually used in the thesis chapters
(see chapter*.md). Token-based: identifies \\macro names as whole units so
\\top is never mis-parsed as \\to + p.
"""
from __future__ import annotations

import re


# --- Symbol maps (looked up by macro name without leading backslash) ----

GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ",
    "epsilon": "ε", "varepsilon": "ε", "zeta": "ζ", "eta": "η",
    "theta": "θ", "vartheta": "ϑ", "iota": "ι", "kappa": "κ",
    "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ", "pi": "π",
    "varpi": "ϖ", "rho": "ρ", "varrho": "ϱ", "sigma": "σ", "varsigma": "ς",
    "tau": "τ", "upsilon": "υ", "phi": "φ", "varphi": "ϕ", "chi": "χ",
    "psi": "ψ", "omega": "ω",
    "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ",
    "Xi": "Ξ", "Pi": "Π", "Sigma": "Σ", "Upsilon": "Υ",
    "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω",
}

OPS = {
    "le": "≤", "leq": "≤", "ge": "≥", "geq": "≥",
    "ne": "≠", "neq": "≠", "approx": "≈", "sim": "∼", "simeq": "≃",
    "in": "∈", "notin": "∉", "subset": "⊂", "supset": "⊃",
    "subseteq": "⊆", "supseteq": "⊇",
    "cup": "∪", "cap": "∩", "emptyset": "∅",
    "cdot": "·", "times": "×", "div": "÷", "pm": "±", "mp": "∓",
    "to": "→", "rightarrow": "→", "leftarrow": "←", "leftrightarrow": "↔",
    "Rightarrow": "⇒", "Leftarrow": "⇐", "Leftrightarrow": "⇔",
    "longrightarrow": "⟶", "longleftarrow": "⟵",
    "forall": "∀", "exists": "∃",
    "infty": "∞", "partial": "∂", "nabla": "∇",
    "prod": "∏", "int": "∫", "oint": "∮",
    "top": "⊤", "bot": "⊥",
    "circ": "∘", "ast": "∗", "star": "⋆",
    "ldots": "…", "dots": "…", "cdots": "⋯", "vdots": "⋮", "ddots": "⋱",
    "prime": "′",
    "perp": "⊥", "parallel": "∥",
    "wedge": "∧", "vee": "∨", "neg": "¬", "lnot": "¬",
    "implies": "⇒", "iff": "⇔",
    "mid": "|", "setminus": "∖",
    "oplus": "⊕", "otimes": "⊗",
    "leftarrow": "←",
}

BLACKBOARD = {
    "R": "ℝ", "N": "ℕ", "Z": "ℤ", "Q": "ℚ", "C": "ℂ", "E": "𝔼", "P": "ℙ", "H": "ℍ",
}

CALLIGRAPHIC = {
    "A": "𝒜", "B": "ℬ", "C": "𝒞", "D": "𝒟", "E": "ℰ", "F": "ℱ",
    "G": "𝒢", "H": "ℋ", "I": "ℐ", "J": "𝒥", "K": "𝒦", "L": "ℒ",
    "M": "ℳ", "N": "𝒩", "O": "𝒪", "P": "𝒫", "Q": "𝒬", "R": "ℛ",
    "S": "𝒮", "T": "𝒯", "U": "𝒰", "V": "𝒱", "W": "𝒲", "X": "𝒳",
    "Y": "𝒴", "Z": "𝒵",
}

# Spacing macros — produce a single space (\, \;) or nothing (\!)
SPACE_MACROS = {"quad": " ", "qquad": "  ",
                ",": " ", ";": " ", ":": " ", " ": " ", "!": ""}

# Bracket sizing macros — emit the following delimiter character verbatim
SIZE_MACROS = {"left", "right", "bigl", "bigr", "big", "Bigl", "Bigr", "Big",
               "biggl", "biggr", "bigg", "Biggl", "Biggr", "Bigg"}

# Macros that consume a single {arg}
ARG_MACROS_TEXT = {"text", "mathrm", "operatorname"}    # arg used as plain text
ARG_MACROS_HAT = {"hat"}
ARG_MACROS_TILDE = {"tilde", "widetilde"}
ARG_MACROS_BAR = {"bar", "overline"}
ARG_MACROS_VEC = {"vec"}
ARG_MACROS_BB = {"mathbb"}
ARG_MACROS_CAL = {"mathcal"}
ARG_MACROS_SQRT = {"sqrt"}
# Two-argument macros
ARG_MACROS_FRAC = {"frac", "tfrac", "dfrac"}

FUNCTION_MACROS = {"log": "log", "ln": "ln", "exp": "exp",
                   "sin": "sin", "cos": "cos", "tan": "tan",
                   "max": "max", "min": "min",
                   "sum": "Σ", "prod": "∏", "int": "∫",
                   "arg": "arg",
                   "lim": "lim", "sup": "sup", "inf": "inf",
                   "det": "det", "dim": "dim",
                   "Pr": "Pr",
                   "Uniform": "Uniform", "Bernoulli": "Bernoulli", "Normal": "Normal"}


# --- Sub/superscript Unicode helpers --------------------------------------

SUB_MAP = {
    "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄",
    "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉",
    "+": "₊", "-": "₋", "=": "₌", "(": "₍", ")": "₎",
    "a": "ₐ", "e": "ₑ", "h": "ₕ", "i": "ᵢ", "j": "ⱼ", "k": "ₖ",
    "l": "ₗ", "m": "ₘ", "n": "ₙ", "o": "ₒ", "p": "ₚ", "r": "ᵣ",
    "s": "ₛ", "t": "ₜ", "u": "ᵤ", "v": "ᵥ", "x": "ₓ",
}

SUP_MAP = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
    "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
    "+": "⁺", "-": "⁻", "=": "⁼", "(": "⁽", ")": "⁾",
    "a": "ᵃ", "b": "ᵇ", "c": "ᶜ", "d": "ᵈ", "e": "ᵉ", "f": "ᶠ",
    "g": "ᵍ", "h": "ʰ", "i": "ⁱ", "j": "ʲ", "k": "ᵏ", "l": "ˡ",
    "m": "ᵐ", "n": "ⁿ", "o": "ᵒ", "p": "ᵖ", "r": "ʳ", "s": "ˢ",
    "t": "ᵗ", "u": "ᵘ", "v": "ᵛ", "w": "ʷ", "x": "ˣ", "y": "ʸ", "z": "ᶻ",
    "T": "ᵀ", "⊤": "ᵀ",
}


def _to_sub(s: str) -> str:
    if all(ch in SUB_MAP for ch in s) and s:
        return "".join(SUB_MAP[ch] for ch in s)
    return f"_({s})"


def _to_sup(s: str) -> str:
    if all(ch in SUP_MAP for ch in s) and s:
        return "".join(SUP_MAP[ch] for ch in s)
    return f"^({s})"


# --- Tokenizer / parser ---------------------------------------------------

def _find_matching_brace(s: str, start: int) -> int:
    depth = 0
    for i in range(start, len(s)):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    return -1


def _take_arg(s: str, i: int) -> tuple[str, int]:
    """Take one LaTeX argument starting at position i:
    - {braced} -> contents, position past closing brace
    - \\macro{...}{...}... -> the macro plus any consecutive {braced} groups
    - single char otherwise
    """
    if i >= len(s):
        return "", i
    if s[i] == "{":
        j = _find_matching_brace(s, i)
        if j < 0:
            return s[i + 1:], len(s)
        return s[i + 1:j], j + 1
    if s[i] == "\\":
        m = re.match(r"\\([a-zA-Z]+|.)", s[i:])
        if m:
            end = i + m.end()
            # Greedily attach any consecutive {braced} groups so a subscript
            # of \text{base} captures the whole \text{base}, not just \text.
            while end < len(s) and s[end] == "{":
                close = _find_matching_brace(s, end)
                if close < 0:
                    break
                end = close + 1
            return s[i:end], end
    return s[i], i + 1


def _render_token_stream(s: str) -> str:
    """Walk through s, recognising \\macros as whole units."""
    out: list[str] = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]

        if ch == "\\":
            m = re.match(r"\\([a-zA-Z]+|[^a-zA-Z])", s[i:])
            if not m:
                out.append(ch); i += 1; continue
            name = m.group(1)
            i += m.end()

            # Handle \\arg\\max / \\arg\\min specially
            if name == "arg" and s[i:i + 4] == r"\max":
                i += 4
                # Optional _{sub}
                if i < n and s[i] == "_":
                    sub, i = _take_arg(s, i + 1)
                    out.append("argmax" + _to_sub(_render_token_stream(sub).replace(" ", "")))
                else:
                    out.append("argmax")
                continue
            if name == "arg" and s[i:i + 4] == r"\min":
                i += 4
                if i < n and s[i] == "_":
                    sub, i = _take_arg(s, i + 1)
                    out.append("argmin" + _to_sub(_render_token_stream(sub).replace(" ", "")))
                else:
                    out.append("argmin")
                continue

            # Spacing
            if name in SPACE_MACROS:
                out.append(SPACE_MACROS[name]); continue

            # Sizing — eat next delimiter char
            if name in SIZE_MACROS:
                if i < n and s[i] in "()[]{}|.<>":
                    delim = s[i]
                    out.append("" if delim == "." else delim)
                    i += 1
                continue

            # Greek
            if name in GREEK:
                out.append(GREEK[name]); continue

            # Operators / function symbols
            if name in OPS:
                out.append(OPS[name]); continue

            # Function-like (named, may have _{sub} or ^{sup} attached)
            if name in FUNCTION_MACROS:
                token = FUNCTION_MACROS[name]
                # Handle attached _ and ^ specially for big operators
                if i < n and s[i] == "_":
                    sub, i = _take_arg(s, i + 1)
                    sub_rendered = _render_token_stream(sub)
                    token += _to_sub(sub_rendered.replace(" ", "")) if sub_rendered else ""
                if i < n and s[i] == "^":
                    sup, i = _take_arg(s, i + 1)
                    sup_rendered = _render_token_stream(sup)
                    token += _to_sup(sup_rendered.replace(" ", "")) if sup_rendered else ""
                out.append(token); continue

            # Arg-consuming macros
            if name in ARG_MACROS_TEXT:
                arg, i = _take_arg(s, i)
                out.append(_render_token_stream(arg))
                continue
            if name in ARG_MACROS_HAT:
                arg, i = _take_arg(s, i)
                rendered = _render_token_stream(arg)
                out.append(rendered + "̂" if rendered else "")
                continue
            if name in ARG_MACROS_TILDE:
                arg, i = _take_arg(s, i)
                rendered = _render_token_stream(arg)
                # Use widetilde where possible
                if rendered == "O":
                    out.append("Õ")
                elif rendered == "d":
                    out.append("d̃")
                else:
                    out.append(rendered + "̃" if rendered else "")
                continue
            if name in ARG_MACROS_BAR:
                arg, i = _take_arg(s, i)
                rendered = _render_token_stream(arg)
                out.append(rendered + "̄" if rendered else "")
                continue
            if name in ARG_MACROS_VEC:
                arg, i = _take_arg(s, i)
                rendered = _render_token_stream(arg)
                out.append(rendered + "⃗" if rendered else "")
                continue
            if name in ARG_MACROS_BB:
                arg, i = _take_arg(s, i)
                out.append(BLACKBOARD.get(arg, arg))
                continue
            if name in ARG_MACROS_CAL:
                arg, i = _take_arg(s, i)
                out.append(CALLIGRAPHIC.get(arg, arg))
                continue
            if name in ARG_MACROS_SQRT:
                arg, i = _take_arg(s, i)
                out.append("√(" + _render_token_stream(arg) + ")")
                continue
            if name in ARG_MACROS_FRAC:
                num, i = _take_arg(s, i)
                den, i = _take_arg(s, i)
                out.append("(" + _render_token_stream(num) + ")/(" + _render_token_stream(den) + ")")
                continue
            if name == "begin":
                env, i = _take_arg(s, i)
                if env == "cases":
                    # Find \end{cases}
                    end_marker = r"\end{cases}"
                    j = s.find(end_marker, i)
                    if j < 0:
                        # Unbalanced, emit raw and continue
                        out.append(env); continue
                    body = s[i:j]
                    i = j + len(end_marker)
                    rows = re.split(r"\\\\", body)
                    parts = []
                    for row in rows:
                        row = row.strip()
                        if not row: continue
                        cells = re.split(r"(?<!\\)&", row, maxsplit=1)
                        if len(cells) == 2:
                            val = _render_token_stream(cells[0].strip()).rstrip(", ").rstrip()
                            cond = _render_token_stream(cells[1].strip()).rstrip(".").rstrip()
                            # If condition reads naturally without "if", omit it.
                            connector = "" if cond.lower().startswith(("with probability", "otherwise", "if ")) else "if "
                            parts.append(f"{val}, {connector}{cond}")
                        else:
                            parts.append(_render_token_stream(row))
                    out.append("{ " + "; ".join(parts) + " }")
                    continue
                # Unknown environment — emit nothing and skip until matching \end
                continue
            if name == "end":
                _, i = _take_arg(s, i)
                continue

            # Unknown macro — drop the backslash, emit name as-is
            out.append(name); continue

        if ch == "_":
            sub, i = _take_arg(s, i + 1)
            rendered = _render_token_stream(sub)
            out.append(_to_sub(rendered.replace(" ", "")))
            continue
        if ch == "^":
            sup, i = _take_arg(s, i + 1)
            rendered = _render_token_stream(sup)
            out.append(_to_sup(rendered.replace(" ", "")))
            continue
        if ch == "{":
            j = _find_matching_brace(s, i)
            if j < 0:
                out.append(ch); i += 1; continue
            inner = s[i + 1:j]
            out.append(_render_token_stream(inner))
            i = j + 1
            continue
        if ch == "}":
            i += 1; continue
        # Plain character — keep
        out.append(ch); i += 1

    return "".join(out)


def render_inline(latex: str) -> str:
    """Convert a LaTeX math snippet to Unicode-rich plain text."""
    return _render_token_stream(latex)


def render_inline_dollar(text: str) -> str:
    """Convert markdown text containing $...$ inline math to rendered text.
    Strips $ delimiters, renders the math. Escaped \\$ is preserved as $."""
    text = text.replace("\\$", "\x01")
    text = re.sub(r"\$([^$\n]+?)\$", lambda m: render_inline(m.group(1)), text)
    text = text.replace("\x01", "$")
    return text


def extract_display_math(line: str) -> str | None:
    """If `line` is exactly $$...$$, return rendered Unicode. Else None."""
    s = line.strip()
    m = re.fullmatch(r"\$\$(.+)\$\$", s)
    if not m:
        return None
    return render_inline(m.group(1))


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    tests = [
        r"\alpha = 1.0",
        r"x_t \in \mathbb{R}^d",
        r"\hat{\theta}_a",
        r"\arg\max_{a \in \mathcal{A}} \hat\theta_a^T x_t",
        r"\sum_{i=1}^{B} (A_i - E_i) \times \ln(A_i / E_i)",
        r"\tilde\theta_a \sim \mathcal{N}(\hat\theta_a, v^2 A_a^{-1})",
        r"P_\text{base} = 200 \times m",
        r"\hat{r}_\text{std} = r_\text{std} - c \cdot 5.0",
        r"\tilde{O}(d \sqrt{T})",
        r"A_a^{-1} \leftarrow A_a^{-1} - \frac{A_a^{-1} x_t x_t^\top A_a^{-1}}{1 + x_t^\top A_a^{-1} x_t}",
        r"\theta_a^\top x_t",
        r"a_t = \begin{cases} \text{Uniform}(\mathcal{A}) & \text{with probability } \varepsilon, \\ \arg\max_a \hat\theta_a^\top x_t & \text{otherwise}. \end{cases}",
        r"p_\text{accept} = \max\Bigl(0.05,\; 0.95 - 3.5 \times \frac{p_\text{monthly}}{\text{income}}\Bigr)",
    ]
    for t in tests:
        print(f"  {t}")
        print(f"  -> {render_inline(t)}")
        print()
