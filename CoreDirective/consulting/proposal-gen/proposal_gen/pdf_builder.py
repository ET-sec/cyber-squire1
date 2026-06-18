"""PDF layout and rendering with ReportLab.

Builds a professional 6-page consulting proposal PDF.
"""

from datetime import datetime, timedelta

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from .config import CONSULTANT, STATS, get_relevant_pricing, PRICING_LABELS
from .templates import proposal_dark, proposal_light


# ── Page Dimensions ─────────────────────────────────────────────────────────

PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 1 * inch
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN
CONTENT_HEIGHT = PAGE_HEIGHT - 2 * MARGIN


def _load_theme(theme_name: str):
    """Load theme module by name."""
    if theme_name == "dark":
        return proposal_dark
    return proposal_light


class ProposalBuilder:
    """Builds a multi-page proposal PDF."""

    def __init__(
        self,
        output_path: str,
        theme: str = "light",
        company: str = "",
        contact: str | None = None,
        need: str = "",
        budget: str | None = None,
        content: dict | None = None,
        service_type: str = "generic",
    ):
        self.output_path = output_path
        self.theme_module = _load_theme(theme)
        self.styles = self.theme_module.get_styles()
        self.company = company
        self.contact = contact
        self.need = need
        self.budget = budget
        self.content = content or {}
        self.service_type = service_type
        self.today = datetime.now()
        self.story = []

    def build(self):
        """Build the full PDF and write to disk."""
        doc = BaseDocTemplate(
            self.output_path,
            pagesize=letter,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN,
        )

        # Cover page frame (no header/footer)
        cover_frame = Frame(
            MARGIN, MARGIN, CONTENT_WIDTH, CONTENT_HEIGHT,
            id="cover",
        )

        # Content pages frame (with room for header/footer)
        content_frame = Frame(
            MARGIN, MARGIN + 0.3 * inch,
            CONTENT_WIDTH, CONTENT_HEIGHT - 0.6 * inch,
            id="content",
        )

        theme = self.theme_module

        def cover_page_bg(canvas, doc):
            """Draw cover page background."""
            canvas.saveState()
            canvas.setFillColor(theme.BACKGROUND)
            canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
            # Accent line at top
            canvas.setStrokeColor(theme.ACCENT)
            canvas.setLineWidth(3)
            canvas.line(MARGIN, PAGE_HEIGHT - 0.6 * inch, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 0.6 * inch)
            # Thin accent line at bottom
            canvas.setLineWidth(1)
            canvas.line(MARGIN, 0.8 * inch, PAGE_WIDTH - MARGIN, 0.8 * inch)
            canvas.restoreState()

        def content_page_bg(canvas, doc):
            """Draw content page background with header and footer."""
            canvas.saveState()
            canvas.setFillColor(theme.BACKGROUND)
            canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

            # Header line
            canvas.setStrokeColor(theme.DIVIDER)
            canvas.setLineWidth(0.5)
            canvas.line(MARGIN, PAGE_HEIGHT - 0.7 * inch, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 0.7 * inch)

            # Header text
            canvas.setFont("Helvetica-Bold", 8)
            canvas.setFillColor(theme.FOOTER_TEXT)
            canvas.drawString(MARGIN, PAGE_HEIGHT - 0.6 * inch, "CoreDirective")

            canvas.setFont("Helvetica", 8)
            canvas.drawRightString(
                PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 0.6 * inch,
                f"Proposal for {self.company}"
            )

            # Footer line
            canvas.setStrokeColor(theme.DIVIDER)
            canvas.setLineWidth(0.5)
            canvas.line(MARGIN, 0.7 * inch, PAGE_WIDTH - MARGIN, 0.7 * inch)

            # Footer text
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(theme.FOOTER_TEXT)
            canvas.drawString(MARGIN, 0.5 * inch, "CONFIDENTIAL")
            canvas.drawCentredString(
                PAGE_WIDTH / 2, 0.5 * inch,
                f"CoreDirective  |  {CONSULTANT['email']}"
            )
            canvas.drawRightString(
                PAGE_WIDTH - MARGIN, 0.5 * inch,
                f"Page {doc.page}"
            )
            canvas.restoreState()

        cover_template = PageTemplate(
            id="cover",
            frames=[cover_frame],
            onPage=cover_page_bg,
        )
        content_template = PageTemplate(
            id="content",
            frames=[content_frame],
            onPage=content_page_bg,
        )

        doc.addPageTemplates([cover_template, content_template])

        # Build all pages
        self._build_cover()
        self._build_executive_summary()
        self._build_scope_of_work()
        self._build_qualifications()
        self._build_investment()
        self._build_next_steps()

        doc.build(self.story)

    # ── Page 1: Cover ───────────────────────────────────────────────────────

    def _build_cover(self):
        """Build the cover page."""
        s = self.styles

        self.story.append(Spacer(1, 1.2 * inch))

        # Company name
        self.story.append(Paragraph("CoreDirective", s["cover_company"]))
        self.story.append(Paragraph("Security &amp; Automation Consulting", s["cover_tagline"]))

        # Accent divider
        divider = Table(
            [[""]],
            colWidths=[2.5 * inch],
            rowHeights=[3],
        )
        divider.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), self.theme_module.ACCENT),
            ("LINEBELOW", (0, 0), (-1, -1), 0, self.theme_module.BACKGROUND),
        ]))
        self.story.append(divider)
        self.story.append(Spacer(1, 0.6 * inch))

        # Proposal title
        self.story.append(Paragraph(
            "Security &amp; Automation Consulting Proposal",
            s["cover_title"],
        ))

        self.story.append(Spacer(1, 0.4 * inch))

        # Client details
        self.story.append(Paragraph("Prepared for", s["cover_detail"]))
        self.story.append(Paragraph(self.company, s["cover_detail_bold"]))

        if self.contact:
            self.story.append(Spacer(1, 0.15 * inch))
            self.story.append(Paragraph("Attention", s["cover_detail"]))
            self.story.append(Paragraph(self.contact, s["cover_detail_bold"]))

        self.story.append(Spacer(1, 0.4 * inch))

        # Consultant details
        self.story.append(Paragraph("Prepared by", s["cover_detail"]))
        certs_short = "CASP+ | CCNA | AWS Security"
        self.story.append(Paragraph(
            f"{CONSULTANT['name']}, {certs_short}",
            s["cover_detail_bold"],
        ))
        self.story.append(Paragraph(CONSULTANT["company"], s["cover_detail"]))

        self.story.append(Spacer(1, 0.4 * inch))

        # Date
        self.story.append(Paragraph("Date", s["cover_detail"]))
        self.story.append(Paragraph(
            self.today.strftime("%B %d, %Y"),
            s["cover_detail_bold"],
        ))

        # Switch to content template for subsequent pages
        self.story.append(NextPageTemplate("content"))
        self.story.append(PageBreak())

    # ── Page 2: Executive Summary ───────────────────────────────────────────

    def _build_executive_summary(self):
        """Build the executive summary page."""
        s = self.styles

        self.story.append(Paragraph("Executive Summary", s["section_header"]))

        # Green accent bar under header
        self._add_section_divider()
        self.story.append(Spacer(1, 0.2 * inch))

        summary_text = self.content.get(
            "executive_summary",
            f"{self.company} requires {self.need}. CoreDirective will deliver a focused "
            f"engagement to address this need with measurable results."
        )

        # Split into paragraphs if multi-line
        for para in summary_text.split("\n\n"):
            para = para.strip()
            if para:
                self.story.append(Paragraph(para, s["body"]))
                self.story.append(Spacer(1, 0.1 * inch))

        self.story.append(Spacer(1, 0.3 * inch))

        # Engagement overview box
        self.story.append(Paragraph("Engagement Overview", s["subsection_header"]))

        overview_data = [
            ["Client", self.company],
            ["Service", self.need],
            ["Consultant", f"{CONSULTANT['name']}, {CONSULTANT['title']}"],
            ["Proposed Start", (self.today + timedelta(days=7)).strftime("%B %d, %Y")],
        ]

        if self.budget:
            overview_data.insert(2, ["Budget Range", self.budget])

        overview_table = Table(
            overview_data,
            colWidths=[1.8 * inch, CONTENT_WIDTH - 1.8 * inch],
            rowHeights=[0.35 * inch] * len(overview_data),
        )

        theme = self.theme_module
        table_styles = [
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (0, -1), theme.ACCENT_DARK),
            ("TEXTCOLOR", (1, 0), (1, -1), theme.TEXT_PRIMARY),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]

        # Alternating row backgrounds
        for i in range(len(overview_data)):
            bg = theme.TABLE_ROW_ALT if i % 2 == 0 else theme.TABLE_ROW_NORMAL
            table_styles.append(("BACKGROUND", (0, i), (-1, i), bg))

        # Subtle border
        table_styles.append(("BOX", (0, 0), (-1, -1), 0.5, theme.TABLE_BORDER))
        table_styles.append(("LINEBELOW", (0, 0), (-1, -2), 0.25, theme.TABLE_BORDER))

        overview_table.setStyle(TableStyle(table_styles))
        self.story.append(overview_table)

        self.story.append(PageBreak())

    # ── Page 3: Scope of Work ───────────────────────────────────────────────

    def _build_scope_of_work(self):
        """Build the scope of work page."""
        s = self.styles

        self.story.append(Paragraph("Scope of Work", s["section_header"]))
        self._add_section_divider()
        self.story.append(Spacer(1, 0.15 * inch))

        phases = self.content.get("phases", [])

        for i, phase in enumerate(phases):
            phase_num = i + 1
            phase_name = phase.get("name", f"Phase {phase_num}")
            description = phase.get("description", "")
            deliverables = phase.get("deliverables", [])
            timeline = phase.get("timeline", "TBD")

            # Phase header
            self.story.append(Paragraph(
                f"Phase {phase_num}: {phase_name}",
                s["phase_title"],
            ))

            # Timeline
            self.story.append(Paragraph(
                f"Estimated timeline: {timeline}",
                s["phase_timeline"],
            ))

            # Description
            if description:
                self.story.append(Paragraph(description, s["body"]))

            # Deliverables
            if deliverables:
                self.story.append(Paragraph("Deliverables:", s["body_bold"]))
                for d in deliverables:
                    bullet_char = '<font color="{}">&#8226;</font>'.format(
                        self.theme_module.ACCENT_DARK.hexval()
                    )
                    self.story.append(Paragraph(
                        f"{bullet_char}  {d}",
                        s["bullet"],
                    ))

            self.story.append(Spacer(1, 0.1 * inch))

        self.story.append(PageBreak())

    # ── Page 4: Qualifications ──────────────────────────────────────────────

    def _build_qualifications(self):
        """Build the qualifications page."""
        s = self.styles
        theme = self.theme_module

        self.story.append(Paragraph("Qualifications", s["section_header"]))
        self._add_section_divider()
        self.story.append(Spacer(1, 0.15 * inch))

        # Qualification framing paragraph
        framing = self.content.get("qualification_framing", "")
        if framing:
            self.story.append(Paragraph(framing, s["body"]))
            self.story.append(Spacer(1, 0.2 * inch))

        # Certifications
        self.story.append(Paragraph("Certifications", s["subsection_header"]))

        # Determine which certs are most relevant to this service type
        relevance_map = {
            "security_assessment": ["SecurityX (CASP+)", "SSCP", "Security+"],
            "soc2_compliance": ["SecurityX (CASP+)", "SSCP", "ISC2 CC"],
            "n8n_automation": ["CCNA", "AWS Security Specialty"],
            "cloud_security": ["AWS Security Specialty", "CCNA", "Security+"],
            "vciso_retainer": ["SecurityX (CASP+)", "SSCP", "ISC2 CC"],
            "incident_response": ["SecurityX (CASP+)", "Security+", "SSCP"],
        }
        highlighted = relevance_map.get(self.service_type, [])

        for cert in CONSULTANT["certifications"]:
            if cert in highlighted:
                bullet_char = '<font color="{}">&#9733;</font>'.format(
                    theme.ACCENT_DARK.hexval()
                )
                self.story.append(Paragraph(
                    f"{bullet_char}  {cert}  (directly relevant to this engagement)",
                    s["cert_highlight"],
                ))
            else:
                bullet_char = '<font color="{}">&#8226;</font>'.format(
                    theme.TEXT_SECONDARY.hexval()
                )
                self.story.append(Paragraph(
                    f"{bullet_char}  {cert}",
                    s["cert_item"],
                ))

        self.story.append(Spacer(1, 0.1 * inch))

        # DoD 8140 (conditionally emphasized)
        is_gov = any(
            kw in self.need.lower()
            for kw in ["dod", "defense", "government", "gov", "federal", "military", "cleared"]
        )
        if is_gov:
            self.story.append(Paragraph(
                f'<b>DoD 8140 Compliance:</b> {CONSULTANT["dod_8140"]}',
                s["cert_highlight"],
            ))
        else:
            self.story.append(Paragraph(
                f'DoD 8140 Compliance: {CONSULTANT["dod_8140"]}',
                s["cert_item"],
            ))

        self.story.append(Spacer(1, 0.25 * inch))

        # Key Stats
        self.story.append(Paragraph("By the Numbers", s["subsection_header"]))
        self.story.append(Spacer(1, 0.1 * inch))

        stat_items = [
            (STATS["security_group_rules"], "Security Group\nRules Managed"),
            (STATS["aws_resources"], "AWS Resources\nDeployed"),
            (STATS["docker_services"], "Docker Services\nOrchestrated"),
            (STATS["alert_automation"], "Alert Automation\nCoverage"),
        ]

        # Build stat boxes as a table
        stat_cells = []
        for value, label in stat_items:
            cell_content = (
                f'<font size="20" color="{theme.ACCENT_DARK.hexval()}"><b>{value}</b></font>'
                f'<br/>'
                f'<font size="9" color="{theme.TEXT_SECONDARY.hexval()}">{label}</font>'
            )
            stat_cells.append(Paragraph(cell_content, s["stat_label"]))

        stat_table = Table(
            [stat_cells],
            colWidths=[CONTENT_WIDTH / 4] * 4,
            rowHeights=[0.9 * inch],
        )

        stat_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BOX", (0, 0), (-1, -1), 0.5, theme.TABLE_BORDER),
            ("LINEBEFORE", (1, 0), (1, -1), 0.25, theme.TABLE_BORDER),
            ("LINEBEFORE", (2, 0), (2, -1), 0.25, theme.TABLE_BORDER),
            ("LINEBEFORE", (3, 0), (3, -1), 0.25, theme.TABLE_BORDER),
            ("BACKGROUND", (0, 0), (-1, -1), theme.TABLE_ROW_ALT),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))

        self.story.append(stat_table)

        self.story.append(PageBreak())

    # ── Page 5: Investment ──────────────────────────────────────────────────

    def _build_investment(self):
        """Build the investment/pricing page."""
        s = self.styles
        theme = self.theme_module

        self.story.append(Paragraph("Investment", s["section_header"]))
        self._add_section_divider()
        self.story.append(Spacer(1, 0.15 * inch))

        self.story.append(Paragraph(
            f"The following pricing applies to the engagement described in this proposal "
            f"for {self.company}. All estimates assume standard scope. "
            f"Significant scope changes will be documented and re-quoted before work begins.",
            s["body"],
        ))
        self.story.append(Spacer(1, 0.2 * inch))

        # Pricing table
        pricing_items = get_relevant_pricing(self.service_type)

        header_row = ["Service", "Investment", "Timeline"]
        table_data = [header_row]

        for label, info in pricing_items:
            price_range = info["range"]

            # If budget provided and this is the primary service, adjust display
            if self.budget and label == PRICING_LABELS.get(self.service_type, ""):
                price_range = self.budget

            table_data.append([label, price_range, info["timeline"]])

        pricing_table = Table(
            table_data,
            colWidths=[2.8 * inch, 2.2 * inch, 1.5 * inch],
            rowHeights=[0.4 * inch] * len(table_data),
        )

        table_styles = [
            # Header row
            ("BACKGROUND", (0, 0), (-1, 0), theme.TABLE_HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), theme.TABLE_HEADER_TEXT),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ALIGN", (0, 0), (-1, 0), "LEFT"),
            # Data rows
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 10),
            ("TEXTCOLOR", (0, 1), (-1, -1), theme.TEXT_PRIMARY),
            # First data row bold (primary service)
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
            # Alignment
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            # Borders
            ("BOX", (0, 0), (-1, -1), 0.75, theme.TABLE_BORDER),
            ("LINEBELOW", (0, 0), (-1, 0), 1, theme.ACCENT),
            ("LINEBELOW", (0, 1), (-1, -2), 0.25, theme.TABLE_BORDER),
        ]

        # Alternating row colors
        for i in range(1, len(table_data)):
            bg = theme.TABLE_ROW_ALT if i % 2 == 1 else theme.TABLE_ROW_NORMAL
            table_styles.append(("BACKGROUND", (0, i), (-1, i), bg))

        # Highlight primary service row
        table_styles.append(("TEXTCOLOR", (1, 1), (1, 1), theme.ACCENT_DARK))
        table_styles.append(("FONTNAME", (1, 1), (1, 1), "Helvetica-Bold"))

        pricing_table.setStyle(TableStyle(table_styles))
        self.story.append(pricing_table)

        self.story.append(Spacer(1, 0.3 * inch))

        # Payment terms
        self.story.append(Paragraph("Payment Terms", s["subsection_header"]))
        self.story.append(Paragraph(
            "50% due upon engagement start. Remaining 50% due upon delivery of final deliverables.",
            s["payment_terms"],
        ))
        self.story.append(Paragraph(
            "For retainer engagements, monthly invoicing applies. "
            "Net 15 payment terms on all invoices.",
            s["payment_terms"],
        ))

        self.story.append(Spacer(1, 0.2 * inch))

        # What's included
        self.story.append(Paragraph("Included in All Engagements", s["subsection_header"]))
        inclusions = [
            "Direct access to lead consultant via Slack, email, or Telegram",
            "Weekly progress reports with task completion metrics",
            "All source documentation and configuration files",
            "30-day post-delivery support window at no additional cost",
        ]
        for item in inclusions:
            bullet_char = '<font color="{}">&#10003;</font>'.format(
                theme.ACCENT_DARK.hexval()
            )
            self.story.append(Paragraph(f"{bullet_char}  {item}", s["bullet"]))

        self.story.append(PageBreak())

    # ── Page 6: Next Steps ──────────────────────────────────────────────────

    def _build_next_steps(self):
        """Build the next steps / signature page."""
        s = self.styles
        theme = self.theme_module

        self.story.append(Spacer(1, 0.5 * inch))

        self.story.append(Paragraph("Ready to Get Started?", s["next_steps_heading"]))

        self.story.append(Spacer(1, 0.15 * inch))

        self.story.append(Paragraph(
            "To move forward, reply to this proposal or reach out directly.",
            s["next_steps_body"],
        ))

        self.story.append(Spacer(1, 0.1 * inch))

        self.story.append(Paragraph(
            f"{CONSULTANT['email']}  |  {CONSULTANT['phone']}",
            s["next_steps_contact"],
        ))

        self.story.append(Spacer(1, 0.3 * inch))

        # Proposed start date
        start_date = (self.today + timedelta(days=7)).strftime("%B %d, %Y")
        self.story.append(Paragraph(
            f"Proposed start date: {start_date}",
            s["next_steps_body"],
        ))

        self.story.append(Spacer(1, 0.6 * inch))

        # Signature section
        self._add_section_divider()
        self.story.append(Spacer(1, 0.3 * inch))

        # Two-column signature block
        sig_data = [
            [
                Paragraph("CoreDirective", s["signature_label"]),
                Paragraph(self.company, s["signature_label"]),
            ],
            [
                Spacer(1, 0.5 * inch),
                Spacer(1, 0.5 * inch),
            ],
            [
                self._sig_line(theme),
                self._sig_line(theme),
            ],
            [
                Paragraph(CONSULTANT["name"], s["signature_name"]),
                Paragraph(self.contact or "Authorized Representative", s["signature_name"]),
            ],
            [
                Paragraph(CONSULTANT["title"], s["signature_label"]),
                Paragraph("Title: ___________________", s["signature_label"]),
            ],
            [
                Paragraph(f"Date: {self.today.strftime('%B %d, %Y')}", s["signature_label"]),
                Paragraph("Date: ___________________", s["signature_label"]),
            ],
        ]

        sig_table = Table(
            sig_data,
            colWidths=[CONTENT_WIDTH / 2 - 0.1 * inch, CONTENT_WIDTH / 2 - 0.1 * inch],
        )

        sig_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 20),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
        ]))

        self.story.append(sig_table)

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _add_section_divider(self):
        """Add a thin green accent line."""
        divider = Table(
            [[""]],
            colWidths=[CONTENT_WIDTH],
            rowHeights=[2],
        )
        divider.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), self.theme_module.ACCENT),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        self.story.append(divider)

    def _sig_line(self, theme):
        """Return a signature line as a small table."""
        line = Table(
            [[""]],
            colWidths=[2.5 * inch],
            rowHeights=[1],
        )
        line.setStyle(TableStyle([
            ("LINEBELOW", (0, 0), (-1, -1), 0.75, theme.TEXT_SECONDARY),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        return line


def build_proposal(
    output_path: str,
    theme: str,
    company: str,
    contact: str | None,
    need: str,
    budget: str | None,
    content: dict,
    service_type: str,
):
    """Public entry point to build a proposal PDF."""
    builder = ProposalBuilder(
        output_path=output_path,
        theme=theme,
        company=company,
        contact=contact,
        need=need,
        budget=budget,
        content=content,
        service_type=service_type,
    )
    builder.build()
    return output_path
