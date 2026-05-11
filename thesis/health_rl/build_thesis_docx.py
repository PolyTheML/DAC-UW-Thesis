#!/usr/bin/env python3
"""
Build a Word document (.docx) draft of the thesis formatted exactly
per the ITC template: Times New Roman, specific heading sizes, 1.5
line spacing, justified body text, and Roman-numeral chapter breaks.

Output: thesis/health_rl/ITC_Thesis_Draft.docx
"""
from __future__ import annotations

import re
import os
from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent
OUT_PATH = Path(r"C:\DAC-UW-Thesis\thesis\I5_ITC_Thesis_Template_Guideline-AMS_BACKUP_CLEAN.docx")

CHAPTERS = [
    ("chapter1_introduction.md", "CHAPTER I. INTRODUCTION"),
    ("chapter2_literature_review.md", "CHAPTER II. LITERATURE REVIEW"),
    ("chapter3_methodology.md", "CHAPTER III. METHODOLOGY"),
    ("chapter4_project_analysis.md", "CHAPTER IV. PROJECT ANALYSIS AND CONCEPTS"),
    ("chapter4_results.md", "CHAPTER V. RESULTS AND DISCUSSION"),
    ("chapter5_conclusion.md", "CHAPTER VI. CONCLUSION"),
]

FIGURES = [
    ("fig_framework.png", "Figure 3.1. System architecture of the adaptive underwriting framework."),
    ("fig_ch4_architecture.png", "Figure 4.1. System architecture of the demonstration system."),
    ("fig_ch4_bandit_loop.png", "Figure 4.2. Contextual bandit decision loop."),
    ("fig_reward_curves.png", "Figure 5.1. Cumulative reward curves for LinUCB and Static XGB baseline."),
    ("fig_action_evolution.png", "Figure 5.2. Evolution of action distribution over 5,000 rounds."),
    ("fig_fairness_region.png", "Figure 5.3. Approval rates by region with parity threshold."),
    ("fig_fairness_occupation.png", "Figure 5.4. Approval rates by occupation with parity threshold."),
    ("fig_regret_curves.png", "Figure 5.5. Cumulative regret curves across all four algorithms."),
    ("fig_hitl_experiment.png", "Figure 5.5.1. EXP-008 four-panel HITL diagnostic."),
]

TABLES = [
    ("Table 1", "Feature categories and encoding scheme for the Cambodia dataset."),
    ("Table 2", "Action-specific reward formulas and constraints."),
    ("Table 3", "Hyperparameters for bandit algorithms and baseline."),
    ("Table 4", "EXP-005 convergence validation results."),
    ("Table 5", "EXP-006 fairness audit results by region and occupation."),
    ("Table 6", "EXP-007 benchmark comparison final rankings."),
]

ABBREVIATIONS = [
    ("AMS", "Department of Applied Mathematics and Statistics"),
    ("BMI", "Body Mass Index"),
    ("COPD", "Chronic Obstructive Pulmonary Disease"),
    ("ITC", "Institute of Technology of Cambodia"),
    ("LinTS", "Linear Thompson Sampling"),
    ("LinUCB", "Linear Upper Confidence Bound"),
    ("NTK", "Neural Tangent Kernel"),
    ("PSI", "Population Stability Index"),
    ("RL", "Reinforcement Learning"),
    ("XGB", "eXtreme Gradient Boosting"),
]

# ---------------------------------------------------------------------------
# Style helpers
# ---------------------------------------------------------------------------

def set_run_font(run, font_name="Times New Roman", size_pt=12, bold=False, italic=False, color=None):
    font = run.font
    font.name = font_name
    font.size = Pt(size_pt)
    font.bold = bold
    font.italic = italic
    if color:
        font.color.rgb = color
    # Ensure font name is set properly for complex scripts
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    rFonts.set(qn('w:eastAsia'), font_name)


def set_paragraph_format(paragraph, space_after=Pt(12), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
                         first_line_indent=None, left_indent=None, right_indent=None):
    pf = paragraph.paragraph_format
    pf.space_after = space_after
    pf.space_before = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = line_spacing
    pf.alignment = alignment
    if first_line_indent is not None:
        pf.first_line_indent = first_line_indent
    if left_indent is not None:
        pf.left_indent = left_indent
    if right_indent is not None:
        pf.right_indent = right_indent


def add_page_break(doc):
    doc.add_page_break()


def add_heading_paragraph(doc, text, level="chapter"):
    """Add a heading with ITC template formatting.
    level: 'chapter' | 'section' | 'subsection' | 'subsubsection'
    """
    para = doc.add_paragraph()
    if level == "chapter":
        # Size 16, Bold, ALL CAPS, center aligned, page break before
        run = para.add_run(text.upper())
        set_run_font(run, size_pt=16, bold=True)
        set_paragraph_format(para, space_after=Pt(24), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.CENTER)
    elif level == "section":
        # Size 14, Bold
        run = para.add_run(text)
        set_run_font(run, size_pt=14, bold=True)
        set_paragraph_format(para, space_after=Pt(12), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT)
    elif level == "subsection":
        # Size 12, Bold, indent once (1.27 cm)
        run = para.add_run(text)
        set_run_font(run, size_pt=12, bold=True)
        set_paragraph_format(para, space_after=Pt(12), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                             left_indent=Cm(1.27))
    elif level == "subsubsection":
        run = para.add_run(text)
        set_run_font(run, size_pt=12, bold=True, italic=True)
        set_paragraph_format(para, space_after=Pt(12), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                             left_indent=Cm(2.0))
    return para


def add_body_paragraph(doc, text, is_bullet=False, bullet_level=0, is_numbered=False):
    """Add a body paragraph with ITC template formatting."""
    para = doc.add_paragraph()
    if is_bullet:
        para.style = "List Bullet"
        # Indent based on level
        para.paragraph_format.left_indent = Cm(1.27 + bullet_level * 0.64)
    elif is_numbered:
        para.style = "List Number"
        para.paragraph_format.left_indent = Cm(1.27)
    else:
        set_paragraph_format(para, space_after=Pt(12), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
                             first_line_indent=Cm(1.27))

    # Parse inline formatting: **bold**, *italic*, $math$
    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|\$.*?\$)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            run = para.add_run(part[2:-2])
            set_run_font(run, size_pt=12, bold=True)
        elif part.startswith('*') and part.endswith('*') and not part.startswith('**'):
            run = para.add_run(part[1:-1])
            set_run_font(run, size_pt=12, italic=True)
        elif part.startswith('$') and part.endswith('$'):
            run = para.add_run(part)
            set_run_font(run, size_pt=12, italic=True)
        else:
            run = para.add_run(part)
            set_run_font(run, size_pt=12)
    return para


def add_placeholder_paragraph(doc, text, kind="FIGURE"):
    para = doc.add_paragraph()
    run = para.add_run(f"[{kind}: {text}]")
    set_run_font(run, size_pt=12, italic=True, color=RGBColor(0x80, 0x80, 0x80))
    set_paragraph_format(para, space_after=Pt(12), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.CENTER)
    return para


def add_citation_paragraph(doc, text):
    para = doc.add_paragraph()
    run = para.add_run(f"[CITATION: {text}]")
    set_run_font(run, size_pt=12, italic=True, color=RGBColor(0x80, 0x80, 0x80))
    set_paragraph_format(para, space_after=Pt(12), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                         first_line_indent=Cm(1.27))
    return para


def extract_figure_label(caption: str) -> tuple[str | None, str]:
    """Extract leading figure label like 'Figure 3.1.' or 'Fig. 4.5.1:' from caption.
    Returns (normalized_label, cleaned_caption)."""
    m = re.match(r'^(Figure\s+\d+(\.\d+)*\.?\s|Fig\.\s+\d+(\.\d+)*:\s*)(.*)$', caption)
    if m:
        label = m.group(1).strip()
        label = label.replace("Fig.", "Figure").replace(":", ".")
        if not label.endswith("."):
            label += "."
        return label, m.group(4)
    return None, caption


def add_embedded_figure(doc, image_path: str, caption_text: str, figure_label: str | None = None):
    """Embed an image with a centered caption."""
    full_path = Path(image_path)
    if not full_path.exists():
        full_path = ROOT / image_path
    if not full_path.exists():
        full_path = ROOT / "figures" / image_path
    if full_path.exists():
        para = doc.add_paragraph()
        run = para.add_run()
        run.add_picture(str(full_path), width=Inches(6))
        set_paragraph_format(para, space_after=Pt(6), line_spacing=1.5,
                             alignment=WD_ALIGN_PARAGRAPH.CENTER)
    else:
        add_placeholder_paragraph(doc, f"{caption_text} (image not found: {image_path})", kind="FIGURE")

    # Normalize caption with figure label
    extracted_label, cleaned_caption = extract_figure_label(caption_text)
    if figure_label is None:
        figure_label = extracted_label
    if figure_label:
        full_caption = f"{figure_label} {cleaned_caption}"
    else:
        full_caption = caption_text

    para = doc.add_paragraph()
    run = para.add_run(full_caption)
    set_run_font(run, size_pt=11, italic=True)
    set_paragraph_format(para, space_after=Pt(12), line_spacing=1.5,
                         alignment=WD_ALIGN_PARAGRAPH.CENTER)


# ---------------------------------------------------------------------------
# Markdown parser
# ---------------------------------------------------------------------------

def parse_markdown(doc, md_text: str):
    lines = md_text.splitlines()
    i = 0
    in_code_block = False
    code_lines = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Code blocks
        if stripped.startswith("```"):
            if in_code_block:
                # End code block
                code_text = "\n".join(code_lines)
                para = doc.add_paragraph()
                run = para.add_run(code_text)
                set_run_font(run, size_pt=10)
                set_paragraph_format(para, space_after=Pt(12), line_spacing=1.15, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                                     first_line_indent=Cm(1.27))
                # Shade the paragraph background lightly
                shading_elm = OxmlElement('w:shd')
                shading_elm.set(qn('w:fill'), "F2F2F2")
                para._element.get_or_add_pPr().append(shading_elm)
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Horizontal rule
        if stripped == "---" or stripped == "***":
            i += 1
            continue

        # Skip empty lines (but they may end a paragraph)
        if not stripped:
            i += 1
            continue

        # Headings
        if stripped.startswith("# "):
            text = stripped[2:].strip()
            add_heading_paragraph(doc, text, level="chapter")
            i += 1
            continue
        if stripped.startswith("## "):
            text = stripped[3:].strip()
            add_heading_paragraph(doc, text, level="section")
            i += 1
            continue
        if stripped.startswith("### "):
            text = stripped[4:].strip()
            add_heading_paragraph(doc, text, level="subsection")
            i += 1
            continue
        if stripped.startswith("#### "):
            text = stripped[5:].strip()
            add_heading_paragraph(doc, text, level="subsubsection")
            i += 1
            continue

        # Bullet lists
        bullet_match = re.match(r'^(\s*)[-*]\s+(.*)$', line)
        if bullet_match:
            indent_level = len(bullet_match.group(1)) // 4
            text = bullet_match.group(2).strip()
            add_body_paragraph(doc, text, is_bullet=True, bullet_level=indent_level)
            i += 1
            continue

        # Numbered lists
        numbered_match = re.match(r'^(\s*)\d+\.\s+(.*)$', line)
        if numbered_match:
            text = numbered_match.group(2).strip()
            add_body_paragraph(doc, text, is_numbered=True)
            i += 1
            continue

        # Embedded figures — new syntax: [FIGURE 4.1: caption. Source: `path`.]
        fig_embed_match = re.search(r'\[FIGURE\s+([\d\.]+):\s*(.*?)\s+Source:\s*`?([^`]+)`?\.\]', stripped)
        if fig_embed_match:
            figure_label = f"Figure {fig_embed_match.group(1)}."
            caption = fig_embed_match.group(2).strip()
            img_path = fig_embed_match.group(3).strip()
            add_embedded_figure(doc, img_path, caption, figure_label=figure_label)
            i += 1
            continue

        # Embedded figures — old syntax: [FIGURE: path — caption]
        fig_match = re.search(r'\[FIGURE:\s*(.*?)\]', stripped)
        if fig_match:
            content = fig_match.group(1).strip()
            if ' — ' in content:
                path_part, caption_part = content.split(' — ', 1)
                add_embedded_figure(doc, path_part.strip(), caption_part.strip())
            else:
                add_placeholder_paragraph(doc, content, kind="FIGURE")
            i += 1
            continue

        tbl_match = re.search(r'\[TABLE:\s*(.*?)\]', stripped)
        if tbl_match:
            add_placeholder_paragraph(doc, tbl_match.group(1).strip(), kind="TABLE")
            i += 1
            continue

        cit_match = re.search(r'\[CITATION:\s*(.*?)\]', stripped)
        if cit_match and stripped.startswith("[CITATION:"):
            add_citation_paragraph(doc, cit_match.group(1).strip())
            i += 1
            continue

        # Markdown table — simplistic parser
        if '|' in stripped and not stripped.startswith('['):
            # Check if next line is a separator like |---|---|
            table_lines = []
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i].strip())
                i += 1
            # Filter out separator lines
            data_lines = [l for l in table_lines if not re.match(r'^[\s|\-:]+$', l.replace('|', '').strip())]
            if data_lines:
                add_markdown_table(doc, data_lines)
            continue

        # Regular paragraph
        # Check if next lines are continuations (not blank, not heading, not list, not table)
        para_lines = [stripped]
        j = i + 1
        while j < len(lines):
            next_line = lines[j]
            next_stripped = next_line.strip()
            if not next_stripped:
                break
            if next_stripped.startswith('#') or next_stripped.startswith('-') or next_stripped.startswith('*') or re.match(r'^\d+\.', next_stripped):
                break
            if next_stripped.startswith('```') or next_stripped.startswith('---') or next_stripped.startswith('***'):
                break
            if '|' in next_stripped and not next_stripped.startswith('['):
                break
            # Append continuation
            para_lines.append(next_stripped)
            j += 1
        full_text = " ".join(para_lines)
        add_body_paragraph(doc, full_text)
        i = j
        continue


def add_markdown_table(doc, data_lines):
    """Convert markdown table rows to a Word table."""
    rows_data = []
    for line in data_lines:
        cells = [c.strip() for c in line.split('|')]
        cells = [c for c in cells if c]  # Remove empty edge cells
        rows_data.append(cells)
    if not rows_data:
        return
    num_cols = max(len(r) for r in rows_data)
    table = doc.add_table(rows=len(rows_data), cols=num_cols)
    table.style = 'Table Grid'
    for row_idx, row_data in enumerate(rows_data):
        row = table.rows[row_idx]
        for col_idx in range(num_cols):
            cell = row.cells[col_idx]
            if col_idx < len(row_data):
                cell.text = row_data[col_idx]
            # Format cell text
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    set_run_font(run, size_pt=11)
                set_paragraph_format(paragraph, space_after=Pt(6), line_spacing=1.15,
                                     alignment=WD_ALIGN_PARAGRAPH.LEFT)
    doc.add_paragraph()  # spacing after table


# ---------------------------------------------------------------------------
# Front matter builders
# ---------------------------------------------------------------------------

def add_title_page(doc):
    # Top spacing
    for _ in range(4):
        doc.add_paragraph()

    # Khmer title
    para = doc.add_paragraph()
    run = para.add_run("គម្រោងសញ្ញាបត្រវិស្វករ")
    set_run_font(run, size_pt=16, bold=True)
    set_paragraph_format(para, space_after=Pt(6), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.CENTER)

    # Date line Khmer
    para = doc.add_paragraph()
    run = para.add_run("ថ្ងៃទី     ខែ        ឆ្នាំ ២០២៦")
    set_run_font(run, size_pt=12)
    set_paragraph_format(para, space_after=Pt(24), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.CENTER)

    # Topic Khmer
    para = doc.add_paragraph()
    run = para.add_run("ប្រធានបទ:")
    set_run_font(run, size_pt=14, bold=True)
    set_paragraph_format(para, space_after=Pt(6), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                         left_indent=Cm(2))

    para = doc.add_paragraph()
    run = para.add_run("Adaptive Health Insurance Underwriting via Contextual Bandits:\nA Reinforcement Learning Approach for Cambodia")
    set_run_font(run, size_pt=14, bold=True)
    set_paragraph_format(para, space_after=Pt(24), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                         left_indent=Cm(2))

    # Company / Department
    para = doc.add_paragraph()
    run = para.add_run("សហគ្រាស: DAC (Decent Actuarial Consultants)")
    set_run_font(run, size_pt=12)
    set_paragraph_format(para, space_after=Pt(6), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                         left_indent=Cm(2))

    para = doc.add_paragraph()
    run = para.add_run("ប្រធានដេប៉ាតឺម៉ង់:\tបណ្ឌិត លិន មង្គលសិរី")
    set_run_font(run, size_pt=12)
    set_paragraph_format(para, space_after=Pt(6), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                         left_indent=Cm(2))

    para = doc.add_paragraph()
    run = para.add_run("សាស្រ្តាចារ្យដឹកនាំគម្រោង:\tលោក ហាស់ សូធាា")
    set_run_font(run, size_pt=12)
    set_paragraph_format(para, space_after=Pt(6), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                         left_indent=Cm(2))

    para = doc.add_paragraph()
    run = para.add_run("អ្នកទទួលខុសត្រូវក្នុងសហគ្រាស:\tលោក Chris & Peter (DAC)")
    set_run_font(run, size_pt=12)
    set_paragraph_format(para, space_after=Pt(6), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                         left_indent=Cm(2))

    para = doc.add_paragraph()
    run = para.add_run("រាជធានីភ្នំពេញ")
    set_run_font(run, size_pt=12, bold=True)
    set_paragraph_format(para, space_after=Pt(36), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.CENTER)

    add_page_break(doc)

    # French / English title page
    for _ in range(2):
        doc.add_paragraph()

    para = doc.add_paragraph()
    run = para.add_run("DEPARTMENT DE MATHEMATIQUES APPLIQUEES ET STATISTIQUES")
    set_run_font(run, size_pt=14, bold=True)
    set_paragraph_format(para, space_after=Pt(6), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.CENTER)

    para = doc.add_paragraph()
    run = para.add_run("MEMOIRE DE FIN D’ETUDES")
    set_run_font(run, size_pt=16, bold=True)
    set_paragraph_format(para, space_after=Pt(6), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.CENTER)

    para = doc.add_paragraph()
    run = para.add_run("DE Mlle. LUN CHANPOLY")
    set_run_font(run, size_pt=12)
    set_paragraph_format(para, space_after=Pt(24), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.CENTER)

    para = doc.add_paragraph()
    run = para.add_run('Date de soutenance : le          \t2026')
    set_run_font(run, size_pt=12)
    set_paragraph_format(para, space_after=Pt(24), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.CENTER)

    para = doc.add_paragraph()
    run = para.add_run("Titre : ")
    set_run_font(run, size_pt=14, bold=True)
    set_paragraph_format(para, space_after=Pt(6), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                         left_indent=Cm(2))

    para = doc.add_paragraph()
    run = para.add_run("Adaptive Health Insurance Underwriting via Contextual Bandits:\nA Reinforcement Learning Approach for Cambodia")
    set_run_font(run, size_pt=14, bold=True)
    set_paragraph_format(para, space_after=Pt(24), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                         left_indent=Cm(2))

    para = doc.add_paragraph()
    run = para.add_run("Etablissement du stage:\tDAC (Decent Actuarial Consultants)")
    set_run_font(run, size_pt=12)
    set_paragraph_format(para, space_after=Pt(6), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                         left_indent=Cm(2))

    para = doc.add_paragraph()
    run = para.add_run("Chef du département:\tDr. LIN Mongkolsery")
    set_run_font(run, size_pt=12)
    set_paragraph_format(para, space_after=Pt(6), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                         left_indent=Cm(2))

    para = doc.add_paragraph()
    run = para.add_run("Tuteur de stage:\tM. Has Sothea")
    set_run_font(run, size_pt=12)
    set_paragraph_format(para, space_after=Pt(6), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                         left_indent=Cm(2))

    para = doc.add_paragraph()
    run = para.add_run("Responsable de l’établissement:\tM. Chris & Peter (DAC)")
    set_run_font(run, size_pt=12)
    set_paragraph_format(para, space_after=Pt(6), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                         left_indent=Cm(2))

    para = doc.add_paragraph()
    run = para.add_run("PHNOM PENH")
    set_run_font(run, size_pt=12, bold=True)
    set_paragraph_format(para, space_after=Pt(36), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.CENTER)

    add_page_break(doc)


def add_acknowledgement(doc):
    add_heading_paragraph(doc, "ACKNOWLEDGEMENT", level="chapter")
    text = (
        "I would like to express my sincere gratitude to my academic advisor, Dr. Has Sothea, "
        "for his continuous guidance, encouragement, and invaluable support throughout this thesis. "
        "His expertise in actuarial science and machine learning has been essential to the completion of this work. "
        "I also extend my thanks to my industry supervisors, Chris and Peter, at DAC (Decent Actuarial Consultants), "
        "for their practical guidance and technical support during my research period.\n\n"
        "My heartfelt appreciation goes to the members of the thesis committee and reviewers for taking the time "
        "to evaluate my work and provide constructive feedback. Their comments have helped me improve the quality "
        "and rigor of this research.\n\n"
        "I would also like to express my gratitude to the Department of Applied Mathematics and Statistics (AMS) "
        "at the Institute of Technology of Cambodia, particularly to Dr. LIN Mongkolsery, and the lecturers in AMS "
        "who have taught and guided me throughout the program. I am also thankful to the department secretary, "
        "Ms. CHHEANG Sreypich, for her administrative and academic support. I would like to extend my deepest "
        "gratitude to the rector of ITC, Dr. PO Kimtho, for leading an institution that fosters academic excellence and research.\n\n"
        "Last but not least, I would like to thank my beloved family and friends for their unwavering support, "
        "encouragement, and understanding. Their presence has been a constant source of motivation throughout my academic journey."
    )
    for para_text in text.split("\n\n"):
        add_body_paragraph(doc, para_text.strip())
    add_page_break(doc)


def add_khmer_abstract(doc):
    add_heading_paragraph(doc, "អត្ថបទសង្ខេប", level="chapter")
    para = doc.add_paragraph()
    run = para.add_run("[អត្ថបទសង្ខេបជាភាសាខ្មែរ សូមបញ្ចូលនៅទីនេះ]")
    set_run_font(run, size_pt=12, italic=True, color=RGBColor(0x80, 0x80, 0x80))
    set_paragraph_format(para, space_after=Pt(12), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
                         first_line_indent=Cm(1.27))
    add_page_break(doc)


def add_english_abstract(doc):
    add_heading_paragraph(doc, "ABSTRACT", level="chapter")
    abstract_text = (
        "Health insurance underwriting in emerging markets such as Cambodia faces structural challenges including low insurance penetration, "
        "fragmented healthcare infrastructure, and limited longitudinal health records. Traditional static rule-based underwriting systems "
        "are suboptimal because they ignore feature interactions, cannot adapt to portfolio drift, and may inadvertently discriminate against "
        "demographic segments. This thesis investigates whether contextual bandits — a class of online learning algorithms for sequential "
        "decision-making under uncertainty — can replace static rules in emerging-market health insurance underwriting.\n\n"
        "The research designs and implements a contextual bandit framework with three algorithms (LinUCB, LinTS, and Epsilon-Greedy) "
        "and compares them against a static XGBoost rule baseline on a synthetic dataset of 2,000 Cambodian health insurance applicants anchored on the Cambodia Demographic and Health Survey (CDHS) 2021–22 (National Institute of Statistics / ICF, 2023). "
        "A profit-based actuarial reward simulator evaluates four underwriting actions (standard, rated, decline, refer), while Population "
        "Stability Index (PSI) guardrails monitor regional and occupational fairness.\n\n"
        "Three controlled experiments validate the framework. EXP-005 demonstrates that LinUCB achieves 67% higher cumulative reward than "
        "the static baseline and reduces average regret by 50% in the final 500 rounds. EXP-006 confirms that all regional and occupational "
        "segments meet the 50% approval-rate parity constraint, with PSI values in the GREEN zone for both dimensions. EXP-007 establishes "
        "a clear performance ranking: LinTS lowest regret ($5,641), followed by LinUCB ($12,954), Epsilon-Greedy ($24,273), and Static XGB "
        "($35,067).\n\n"
        "The results provide a rigorous proof of concept that contextual bandits can improve both profitability and fairness in Cambodian "
        "health insurance underwriting while remaining computationally lightweight enough for deployment on low-resource mobile infrastructure. "
        "The thesis contributes a reproducible experimental harness, a Cambodia-calibrated synthetic dataset, and a fairness monitoring protocol "
        "that may inform future research and industry practice in emerging-market algorithmic insurance."
    )
    for para_text in abstract_text.split("\n\n"):
        add_body_paragraph(doc, para_text.strip())
    add_page_break(doc)


def add_toc(doc):
    add_heading_paragraph(doc, "TABLE OF CONTENTS", level="chapter")
    para = doc.add_paragraph()
    run = para.add_run("[Table of Contents — update field in Microsoft Word after opening]")
    set_run_font(run, size_pt=12, italic=True, color=RGBColor(0x80, 0x80, 0x80))
    set_paragraph_format(para, space_after=Pt(12), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT)

    # Insert Word TOC field
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'TOC \\o "1-3" \\h \\z \\u'
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')
    run._element.append(fldChar)
    run._element.append(instrText)
    run._element.append(fldChar2)
    run._element.append(fldChar3)

    add_page_break(doc)


def add_list_of_figures(doc):
    add_heading_paragraph(doc, "LIST OF FIGURES", level="chapter")
    for fname, caption in FIGURES:
        para = doc.add_paragraph()
        run = para.add_run(caption)
        set_run_font(run, size_pt=12)
        set_paragraph_format(para, space_after=Pt(6), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                             first_line_indent=Cm(1.27))
    add_page_break(doc)


def add_list_of_tables(doc):
    add_heading_paragraph(doc, "LIST OF TABLES", level="chapter")
    for label, caption in TABLES:
        para = doc.add_paragraph()
        run = para.add_run(f"{label}.  {caption}")
        set_run_font(run, size_pt=12)
        set_paragraph_format(para, space_after=Pt(6), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                             first_line_indent=Cm(1.27))
    add_page_break(doc)


def add_list_of_abbreviations(doc):
    add_heading_paragraph(doc, "LIST OF ABBREVIATIONS", level="chapter")
    table = doc.add_table(rows=len(ABBREVIATIONS), cols=2)
    table.style = 'Table Grid'
    for row_idx, (abbr, meaning) in enumerate(ABBREVIATIONS):
        row = table.rows[row_idx]
        row.cells[0].text = abbr
        row.cells[1].text = meaning
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    set_run_font(run, size_pt=12)
                set_paragraph_format(paragraph, space_after=Pt(6), line_spacing=1.15,
                                     alignment=WD_ALIGN_PARAGRAPH.LEFT)
    add_page_break(doc)


# ---------------------------------------------------------------------------
# Document setup
# ---------------------------------------------------------------------------

def setup_document_styles(doc):
    """Configure default styles to match ITC template."""
    style = doc.styles['Normal']
    font = style.font
    font.name = "Times New Roman"
    font.size = Pt(12)
    pf = style.paragraph_format
    pf.space_after = Pt(12)
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = 1.5
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Set default font for East Asian scripts
    rFonts = style.element.rPr.rFonts
    if rFonts is None:
        rPr = style.element.get_or_add_rPr()
        rFonts = OxmlElement('w:rFonts')
        rPr.insert(0, rFonts)
    rFonts.set(qn('w:eastAsia'), 'Times New Roman')

    # Page margins (standard A4)
    sections = doc.sections[0]
    sections.page_height = Cm(29.7)
    sections.page_width = Cm(21.0)
    sections.top_margin = Cm(2.54)
    sections.bottom_margin = Cm(2.54)
    sections.left_margin = Cm(3.17)
    sections.right_margin = Cm(2.54)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    doc = Document()
    setup_document_styles(doc)

    # ---- Front matter ------------------------------------------------------
    add_title_page(doc)
    add_acknowledgement(doc)
    add_khmer_abstract(doc)
    add_english_abstract(doc)
    add_toc(doc)
    add_list_of_figures(doc)
    add_list_of_tables(doc)
    add_list_of_abbreviations(doc)

    # ---- Body chapters -----------------------------------------------------
    for filename, expected_chapter_title in CHAPTERS:
        filepath = ROOT / filename
        if not filepath.exists():
            print(f"Warning: {filepath} not found, skipping.")
            continue
        md_text = filepath.read_text(encoding="utf-8")

        # Inject a page break before the chapter
        add_page_break(doc)
        parse_markdown(doc, md_text)

    # ---- References --------------------------------------------------------
    add_page_break(doc)
    add_heading_paragraph(doc, "REFERENCES", level="chapter")
    ref_text = (
        "References should be written in APA 7th edition style. "
        "The following placeholders indicate the key sources cited in this thesis:\n\n"
        "[CITATION: Robbins 1952] Robbins, H. (1952). Some aspects of the sequential design of experiments. "
        "Bulletin of the American Mathematical Society, 58(5), 527–535.\n\n"
        "[CITATION: Li et al. 2010] Li, L., Chu, W., Langford, J., & Schapire, R. E. (2010). "
        "A contextual-bandit approach to personalized news article recommendation. "
        "Proceedings of the 19th International Conference on World Wide Web, 661–670.\n\n"
        "[CITATION: Agrawal & Goyal 2013] Agrawal, S., & Goyal, N. (2013). "
        "Thompson sampling for contextual bandits with linear payoffs. "
        "Proceedings of the 30th International Conference on Machine Learning, 127–135.\n\n"
        "[CITATION: Lattimore & Szepesvari 2020] Lattimore, T., & Szepesvári, C. (2020). "
        "Bandit algorithms. Cambridge University Press.\n\n"
        "[CITATION: Russo et al. 2018] Russo, D., Van Roy, B., Kazerouni, A., Osband, I., & Wen, Z. (2018). "
        "A tutorial on Thompson sampling. Foundations and Trends in Machine Learning, 11(1), 1–96.\n\n"
        "[CITATION: Sutton & Barto 2018] Sutton, R. S., & Barto, A. G. (2018). "
        "Reinforcement learning: An introduction (2nd ed.). MIT Press.\n\n"
        "[CITATION: Zhou et al. 2020] Zhou, D., Gu, Q., & Szepesvári, C. (2020). "
        "Neural contextual bandits with UCB-based exploration. "
        "Proceedings of the 37th International Conference on Machine Learning.\n\n"
        "[CITATION: Zhang et al. 2021] Zhang, W., Zhou, D., Li, L., & Gu, Q. (2021). "
        "Neural Thompson sampling. Proceedings of the 9th International Conference on Learning Representations.\n\n"
        "[CITATION: Chen et al. 2022] Chen, X., Wang, Y., & Wang, X. (2022). "
        "EE-Net: Exploitation and exploration neural network for dynamic pricing. arXiv preprint.\n\n"
        "[CITATION: Barocas et al. 2019] Barocas, S., Hardt, M., & Narayanan, A. (2019). "
        "Fairness and machine learning. fairmlbook.org.\n\n"
        "[CITATION: Ensign et al. 2018] Ensign, D., Friedler, S. A., Neville, S., Scheidegger, C., & Venkatasubramanian, S. (2018). "
        "Runaway feedback loops in predictive policing. Proceedings of the 1st Conference on Fairness, Accountability and Transparency.\n\n"
        "[CITATION: Lewis 1994] Lewis, E. M. (1994). An introduction to credit scoring. Athena Press, London.\n\n"
        "[CITATION: Thomas et al. 2002] Thomas, L. C., Edelman, D. B., & Crook, J. N. (2002). Credit scoring and its applications. "
        "SIAM monographs on mathematical modeling and computation. Philadelphia: SIAM. ISBN 978-0-89871-483-8.\n\n"
        "[CITATION: Siddiqi 2006] Siddiqi, N. (2006). Credit risk scorecards: Developing and implementing intelligent credit scoring. "
        "Hoboken, NJ: John Wiley & Sons. ISBN 978-0-471-75451-0. (Reprinted 2012, DOI:10.1002/9781119201731).\n\n"
        "[CITATION: Yurdakul & Naranjo 2020] Yurdakul, B., & Naranjo, J. (2020). Statistical properties of the population stability index. "
        "Journal of Risk Model Validation, 14(4), 89–100. DOI:10.21314/JRMV.2020.227.\n\n"
        "[CITATION: Lin 1991] Lin, J. (1991). Divergence measures based on the Shannon entropy. "
        "IEEE Transactions on Information Theory, 37(1), 145–151. DOI:10.1109/18.61115."
    )
    for para_text in ref_text.split("\n\n"):
        add_body_paragraph(doc, para_text.strip())

    # ---- Appendices --------------------------------------------------------
    add_page_break(doc)
    add_heading_paragraph(doc, "APPENDICES", level="chapter")
    add_heading_paragraph(doc, "Appendix A: Dataset Generation Code", level="section")
    para = doc.add_paragraph()
    run = para.add_run("[Source code listing from case-study/generate_cambodia_dataset.py]")
    set_run_font(run, size_pt=12, italic=True, color=RGBColor(0x80, 0x80, 0x80))
    set_paragraph_format(para, space_after=Pt(12), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                         first_line_indent=Cm(1.27))

    add_heading_paragraph(doc, "Appendix B: Bandit Algorithm Implementation", level="section")
    para = doc.add_paragraph()
    run = para.add_run("[Source code listing from stress_testing/rl/underwriting_bandit.py]")
    set_run_font(run, size_pt=12, italic=True, color=RGBColor(0x80, 0x80, 0x80))
    set_paragraph_format(para, space_after=Pt(12), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                         first_line_indent=Cm(1.27))

    add_heading_paragraph(doc, "Appendix C: Experiment Scripts", level="section")
    para = doc.add_paragraph()
    run = para.add_run("[Source code listings from stress_testing/rl/experiments/exp_005_*.py, exp_006_*.py, exp_007_*.py]")
    set_run_font(run, size_pt=12, italic=True, color=RGBColor(0x80, 0x80, 0x80))
    set_paragraph_format(para, space_after=Pt(12), line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                         first_line_indent=Cm(1.27))

    # ---- Save --------------------------------------------------------------
    doc.save(OUT_PATH)
    print(f"Saved thesis draft to: {OUT_PATH}")


if __name__ == "__main__":
    main()
