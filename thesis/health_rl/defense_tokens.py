from pptx.dml.color import RGBColor
from pptx.util import Emu, Pt

# ── Palette ───────────────────────────────────────────────────────────
NAVY     = RGBColor(0x1F, 0x3A, 0x6E)
BLUE     = RGBColor(0x2E, 0x74, 0xB5)
LIGHT_BG = RGBColor(0xEF, 0xF3, 0xF8)
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
GRAY     = RGBColor(0x50, 0x50, 0x50)
DARK_TXT = RGBColor(0x26, 0x26, 0x26)
DIVIDER  = RGBColor(0xCB, 0xDC, 0xEF)
AMBER_BG = RGBColor(0xFE, 0xF3, 0xCD)
AMBER_ACC= RGBColor(0xF4, 0xA1, 0x1D)
AMBER_TXT= RGBColor(0x7D, 0x4E, 0x00)
RED_BG   = RGBColor(0xF8, 0xE7, 0xE7)
RED_ACC  = RGBColor(0xC0, 0x20, 0x20)
GREEN_BG = RGBColor(0xE7, 0xF4, 0xE8)
GREEN_ACC= RGBColor(0x21, 0x82, 0x38)
ORANGE   = RGBColor(0xF4, 0xA1, 0x1D)

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
