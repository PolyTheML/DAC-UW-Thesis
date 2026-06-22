from pptx.dml.color import RGBColor
from pptx.util import Emu, Pt

# ── Palette ───────────────────────────────────────────────────────────
# Burgundy-chrome restyle 2026-06-22: token VALUES remapped to the
# user-approved cobalt "Yuth-reference" palette (build_burgundy_presentation.py
# 61-82). Token NAMES kept so 66 content-slide usages auto-repaint.
NAVY     = RGBColor(0x1B, 0x56, 0x97)   # titles, underline, card accent, stat blocks, table headers
BLUE     = RGBColor(0x1F, 0x6F, 0xC4)   # secondary accents
LIGHT_BG = RGBColor(0xF3, 0xF6, 0xFB)   # card / panel fill
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
GRAY     = RGBColor(0x50, 0x50, 0x50)
DARK_TXT = RGBColor(0x26, 0x26, 0x26)
DIVIDER  = RGBColor(0xDD, 0xDD, 0xDD)   # thin separators / hairlines
AMBER_BG = RGBColor(0xFE, 0xF3, 0xCD)
AMBER_ACC= RGBColor(0xE6, 0xA6, 0x2E)
AMBER_TXT= RGBColor(0x7D, 0x4E, 0x00)
RED_BG   = RGBColor(0xF8, 0xE7, 0xE7)
RED_ACC  = RGBColor(0xD9, 0x3B, 0x3B)
GREEN_BG = RGBColor(0xE7, 0xF4, 0xE8)
GREEN_ACC= RGBColor(0x2E, 0x8B, 0x57)
ORANGE   = RGBColor(0xE6, 0xA6, 0x2E)

# Finer cobalt blues for chrome (footer / divider) — used by defense_draw
BLUE_DEEP    = RGBColor(0x14, 0x3D, 0x6B)   # footer org panels
BLUE_DIVIDER = RGBColor(0x1F, 0x6F, 0xC4)   # divider-slide background
BLUE_TINT    = RGBColor(0xAF, 0xC4, 0xE4)   # footer center panel

# Fonts (burgundy: Segoe UI headings / Calibri body; v3 previously unset)
HEAD_FONT = "Segoe UI"
BODY_FONT = "Calibri"

# ── Geometry ──────────────────────────────────────────────────────────
SW          = 12191695   # slide width  EMU
SH          = 6858000    # slide height EMU
FOOTER_TOP  = 6437376    # y-coord where footer starts
CONTENT_BOT = FOOTER_TOP - 80000   # safe content bottom
MARGIN_L    = 457200     # left margin
MARGIN_R    = SW - 457200           # right edge
CONTENT_W   = MARGIN_R - MARGIN_L  # 11277295
TITLE_T     = 310896
TITLE_H     = 566928
UNDERLINE_T = 969696
UNDERLINE_H = 36576

# ── Sophea canonical profile ──────────────────────────────────────────
SOPHEA = {
    "name":       "Sophea",
    "age":        42,
    "gender":     "Female",
    "region":     "Kampong Cham",
    "occupation": "Rice Farmer",
    "bmi":        24.1,
    "smoker":     "No",
    "activity":   "High (field farming)",
    "clinical":   "Hypertension (managed)",
    "wealth":     "Low",
    "education":  "Primary",
    # standardised key dims
    "age_std":    0.3,
    "bmi_std":    -0.1,
    # arm scores (after training)
    "arm_rated":   0.31,
    "arm_standard":0.52,
    "arm_decline": 0.10,
    "arm_refer":   0.28,
    "verdict_2023": "DECLINE",
    "verdict_2026": "STANDARD",
}
