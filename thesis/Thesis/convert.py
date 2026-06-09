#!/usr/bin/env python3
"""
convert.py — Markdown thesis chapters -> LaTeX (for the ITC XeLaTeX template).

Pipeline per chapter:
  1. Pre-process MARKDOWN (clean text is easier than mangled TeX):
       - protect math spans, escape bare currency `$`
       - convert [FIGURE: path -- caption] placeholders -> raw-LaTeX \fg{}{}{}
  2. Run Pandoc (md -> latex, --natbib) to get body TeX.
  3. Post-process TeX:
       - strip manual chapter/section numbers (let LaTeX auto-number)
       - fix narrative citations  \citep{Key:n} -> \citeyearpar{Key}
       - give Pandoc longtables a real \caption{} (numbered + listed)
       - drop Pandoc's \rule separators (from markdown ---)

Run from repo root:  python thesis/Thesis/convert.py
"""
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "thesis", "health_rl")
OUT = os.path.join(REPO, "thesis", "Thesis", "Chapters")

PANDOC = r"C:\Users\TRC\AppData\Local\Pandoc\pandoc.exe"
if not os.path.exists(PANDOC):
    PANDOC = "pandoc"

# markdown file -> (output tex name, chapter label)
CHAPTERS = [
    ("chapter01_introduction.md",     "ch1-Introduction.tex",     "introduction"),
    ("chapter02_presentation.md",     "ch2-Presentation.tex",     "presentation"),
    ("chapter03_literature_review.md","ch3-LiteratureReview.tex", "litreview"),
    ("chapter04_project_analysis.md", "ch4-ProjectAnalysis.tex",  "analysis"),
    ("chapter05_results.md",          "ch5-Results.tex",          "results"),
    ("chapter06_conclusion.md",       "ch6-Conclusion.tex",       "conclusion"),
]

# -----------------------------------------------------------------------------
# 1. Markdown pre-processing
# -----------------------------------------------------------------------------

def escape_currency(md: str) -> str:
    """Escape bare `$` (currency) without touching real math spans."""
    stash = []

    def keep(m):
        stash.append(m.group(0))
        return "\x00M%d\x00" % (len(stash) - 1)

    # protect display math  $$ ... $$
    md = re.sub(r"\$\$.*?\$\$", keep, md, flags=re.S)
    # protect inline math: opening $ not followed by space, closing $ not
    # preceded by space (Pandoc's own rule). This matches $20$, $10^{-8}$,
    # $x_t \in \mathbb{R}^d$ but NOT "$90,540 vs $72,292" (space before 2nd $).
    md = re.sub(r"\$(?=\S)(?:\\.|[^$\\])*?(?<=\S)\$", keep, md)
    # everything left is a literal dollar -> escape
    md = md.replace("$", r"\$")
    # restore math
    for i, s in enumerate(stash):
        md = md.replace("\x00M%d\x00" % i, s)
    return md


_TEX_SPECIAL = {"&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_"}

def _tex_escape_caption(text: str) -> str:
    out = []
    for ch in text:
        out.append(_TEX_SPECIAL.get(ch, ch))
    return "".join(out)


def convert_figures(md: str) -> str:
    """[FIGURE: ... png ... -- caption] -> raw-latex \\fg{w}{caption}{images/base}."""
    def repl(m):
        body = m.group(1)
        png = re.search(r"([A-Za-z0-9_./-]+\.png)", body)
        if not png:
            return m.group(0)
        base = png.group(1).split("/")[-1]
        if "Source:" in body:                       # [FIGURE 4.1: CAP -- Source: `path`.]
            cap = body.split("Source:")[0]
            cap = re.sub(r"^FIGURE[^:]*:\s*", "", cap)
        elif "—" in body or "--" in body:           # [FIGURE: path -- CAP]
            cap = re.split(r"—|--", body, maxsplit=1)[1]
        else:
            cap = body
        cap = cap.strip().strip("—-` .")
        if "Source:" in body:                       # reconstruct "Figure N.N." for format B
            nm = re.match(r"\s*FIGURE\s+([0-9.]+)\s*:", body)
            if nm and not re.match(r"Figure\s+[0-9.]+", cap):
                cap = "Figure %s. %s" % (nm.group(1), cap)
        cap = _tex_escape_caption(cap)   # manual "Figure N.N." numbers are PRESERVED
        return ("\n\n```{=latex}\n\\fg{0.85\\textwidth}{%s}{images/%s}\n```\n\n"
                % (cap, base))
    return re.sub(r"\[FIGURE([^\]]*)\]", repl, md)


def preprocess_md(md: str) -> str:
    md = escape_currency(md)
    md = convert_figures(md)
    return md

# -----------------------------------------------------------------------------
# 2. Pandoc
# -----------------------------------------------------------------------------

def run_pandoc(md_text: str) -> str:
    p = subprocess.run(
        [PANDOC, "-f", "markdown", "-t", "latex", "--natbib",
         "--top-level-division=chapter", "--wrap=preserve"],
        input=md_text.encode("utf-8"),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if p.returncode != 0:
        sys.stderr.write(p.stderr.decode("utf-8", "replace"))
        raise SystemExit("pandoc failed")
    # normalize line endings (pandoc emits CRLF on Windows -> avoid CR doubling)
    return p.stdout.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")

# -----------------------------------------------------------------------------
# 3. TeX post-processing
# -----------------------------------------------------------------------------

def strip_heading_numbers(tex: str) -> str:
    # \chapter{CHAPTER IV. Title}  -> \chapter{Title}
    tex = re.sub(r"(\\chapter\{)\s*CHAPTER\s+[IVXLC]+\.?\s*", r"\1", tex)
    # \section{4.1 Title} / \subsection{4.5.2 Title} -> strip the leading number
    tex = re.sub(r"(\\(?:sub)*section\{)\s*\d+(?:\.\d+)*\.?\s+", r"\1", tex)
    return tex


def fix_narrative_cites(tex: str) -> str:
    # [@Key:n] became \citep{Key:n}; narrative form wants just the year.
    return re.sub(r"\\citep\{([A-Za-z0-9]+):n\}", r"\\citeyearpar{\1}", tex)


def caption_tables(tex: str) -> str:
    """Convert the author's bold 'Table X.Y --- caption' paragraph (which sits
    immediately above each table) into \\captionof{table}{...}. Placed BEFORE the
    longtable -> no surgery inside it, so it cannot break the table. Keeps the
    manual 'Table X.Y' number in the text (matches in-text references) and enters
    the table into the List of Tables. labelformat=empty (preamble) suppresses a
    second auto-number. Greedy [^\\n]* spans the Pandoc-escaped {[} ... {]}."""
    def repl(m):
        full, label = m.group(1), m.group(2)
        return "\\captionof{table}{%s}\\label{tab:%s}" % (full, label)
    return re.sub(r"^\\textbf\{(Table\s+([0-9.]+[a-z]?)[^\n]*)\}[ \t]*$",
                  repl, tex, flags=re.M)


def drop_rules(tex: str) -> str:
    return re.sub(r"\\begin\{center\}\\rule\{0\.5\\linewidth\}\{0\.5pt\}\\end\{center\}\s*\n?",
                  "", tex)


def postprocess_tex(tex: str) -> str:
    tex = strip_heading_numbers(tex)
    tex = fix_narrative_cites(tex)
    tex = caption_tables(tex)   # bold "Table X.Y" paragraphs -> \captionof (safe, LoT-enabled)
    tex = drop_rules(tex)
    return tex

# -----------------------------------------------------------------------------

def main():
    os.makedirs(OUT, exist_ok=True)
    for md_name, tex_name, _label in CHAPTERS:
        md_path = os.path.join(SRC, md_name)
        with open(md_path, encoding="utf-8") as f:
            md = f.read()
        tex = postprocess_tex(run_pandoc(preprocess_md(md)))
        out_path = os.path.join(OUT, tex_name)
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(tex)
        n_fig = tex.count(r"\fg{")
        n_tab = tex.count(r"\begin{longtable}")
        n_cite = len(re.findall(r"\\cite", tex))
        print("%-26s -> %-26s  figs=%d tables=%d cites=%d  (%d lines)"
              % (md_name, tex_name, n_fig, n_tab, n_cite, tex.count("\n")))

if __name__ == "__main__":
    main()
