"""Light theme styles for proposal PDF generation."""

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle


# ── Color Palette ───────────────────────────────────────────────────────────

BACKGROUND = HexColor("#FFFFFF")
TEXT_PRIMARY = HexColor("#1A1A1A")
TEXT_SECONDARY = HexColor("#4A4A4A")
HEADER_COLOR = HexColor("#0A0A0A")
ACCENT = HexColor("#00FF41")
ACCENT_DARK = HexColor("#00CC33")  # For text on white (better readability)
DIVIDER = HexColor("#00FF41")
TABLE_HEADER_BG = HexColor("#0A0A0A")
TABLE_HEADER_TEXT = HexColor("#FFFFFF")
TABLE_ROW_ALT = HexColor("#F5F5F5")
TABLE_ROW_NORMAL = HexColor("#FFFFFF")
TABLE_BORDER = HexColor("#E0E0E0")
FOOTER_TEXT = HexColor("#888888")
COVER_SUBTITLE = HexColor("#333333")


# ── Paragraph Styles ───────────────────────────────────────────────────────

def get_styles() -> dict[str, ParagraphStyle]:
    """Return all paragraph styles for the light theme."""
    return {
        "cover_company": ParagraphStyle(
            "cover_company",
            fontName="Helvetica-Bold",
            fontSize=32,
            leading=38,
            textColor=HEADER_COLOR,
            alignment=TA_LEFT,
            spaceAfter=4,
        ),
        "cover_tagline": ParagraphStyle(
            "cover_tagline",
            fontName="Helvetica",
            fontSize=14,
            leading=18,
            textColor=ACCENT_DARK,
            alignment=TA_LEFT,
            spaceAfter=40,
        ),
        "cover_title": ParagraphStyle(
            "cover_title",
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            textColor=HEADER_COLOR,
            alignment=TA_LEFT,
            spaceAfter=30,
        ),
        "cover_detail": ParagraphStyle(
            "cover_detail",
            fontName="Helvetica",
            fontSize=12,
            leading=18,
            textColor=TEXT_SECONDARY,
            alignment=TA_LEFT,
            spaceAfter=6,
        ),
        "cover_detail_bold": ParagraphStyle(
            "cover_detail_bold",
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=18,
            textColor=TEXT_PRIMARY,
            alignment=TA_LEFT,
            spaceAfter=6,
        ),
        "section_header": ParagraphStyle(
            "section_header",
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=26,
            textColor=HEADER_COLOR,
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=16,
        ),
        "subsection_header": ParagraphStyle(
            "subsection_header",
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=20,
            textColor=HEADER_COLOR,
            alignment=TA_LEFT,
            spaceBefore=16,
            spaceAfter=8,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Helvetica",
            fontSize=10.5,
            leading=16,
            textColor=TEXT_PRIMARY,
            alignment=TA_LEFT,
            spaceAfter=10,
        ),
        "body_bold": ParagraphStyle(
            "body_bold",
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=16,
            textColor=TEXT_PRIMARY,
            alignment=TA_LEFT,
            spaceAfter=10,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName="Helvetica",
            fontSize=10.5,
            leading=16,
            textColor=TEXT_PRIMARY,
            alignment=TA_LEFT,
            leftIndent=20,
            spaceAfter=4,
            bulletIndent=8,
        ),
        "phase_title": ParagraphStyle(
            "phase_title",
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=18,
            textColor=ACCENT_DARK,
            alignment=TA_LEFT,
            spaceBefore=14,
            spaceAfter=6,
        ),
        "phase_timeline": ParagraphStyle(
            "phase_timeline",
            fontName="Helvetica-Oblique",
            fontSize=9.5,
            leading=14,
            textColor=TEXT_SECONDARY,
            alignment=TA_LEFT,
            spaceAfter=6,
        ),
        "cert_item": ParagraphStyle(
            "cert_item",
            fontName="Helvetica",
            fontSize=10.5,
            leading=16,
            textColor=TEXT_PRIMARY,
            alignment=TA_LEFT,
            leftIndent=10,
            spaceAfter=4,
        ),
        "cert_highlight": ParagraphStyle(
            "cert_highlight",
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=16,
            textColor=ACCENT_DARK,
            alignment=TA_LEFT,
            leftIndent=10,
            spaceAfter=4,
        ),
        "stat_label": ParagraphStyle(
            "stat_label",
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=TEXT_SECONDARY,
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "stat_value": ParagraphStyle(
            "stat_value",
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            textColor=ACCENT_DARK,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=FOOTER_TEXT,
            alignment=TA_CENTER,
        ),
        "header_left": ParagraphStyle(
            "header_left",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=FOOTER_TEXT,
            alignment=TA_LEFT,
        ),
        "header_right": ParagraphStyle(
            "header_right",
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=FOOTER_TEXT,
            alignment=TA_RIGHT,
        ),
        "next_steps_heading": ParagraphStyle(
            "next_steps_heading",
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=24,
            textColor=HEADER_COLOR,
            alignment=TA_CENTER,
            spaceBefore=20,
            spaceAfter=20,
        ),
        "next_steps_body": ParagraphStyle(
            "next_steps_body",
            fontName="Helvetica",
            fontSize=11,
            leading=17,
            textColor=TEXT_PRIMARY,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "next_steps_contact": ParagraphStyle(
            "next_steps_contact",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=17,
            textColor=ACCENT_DARK,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "signature_label": ParagraphStyle(
            "signature_label",
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=TEXT_SECONDARY,
            alignment=TA_LEFT,
            spaceAfter=4,
        ),
        "signature_name": ParagraphStyle(
            "signature_name",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=16,
            textColor=TEXT_PRIMARY,
            alignment=TA_LEFT,
            spaceAfter=2,
        ),
        "payment_terms": ParagraphStyle(
            "payment_terms",
            fontName="Helvetica-Oblique",
            fontSize=10,
            leading=15,
            textColor=TEXT_SECONDARY,
            alignment=TA_LEFT,
            spaceBefore=12,
            spaceAfter=6,
        ),
    }
