"""
report.py
---------
PDF report generation from LLM findings.

Takes the structured findings list produced by analysis.py and formats
it into a professional A4 PDF using ReportLab.

Main entry point:
  generate_pdf(findings, output_path, period1_name, period2_name) -> None

Design:
  - Header bar (dark blue) with report title and generation date
  - Period strip showing previous and current period labels
  - Summary row: total findings | significant | outliers
  - Findings table: one row per finding, impact colour-coded by row background
  - Impact key legend
  - Page numbers
  - Footer disclaimer
"""

import os
import re
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)


# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------

COLOUR_HEADER   = colors.HexColor("#1A237E")   # dark blue  — header bar
COLOUR_HIGH_BG  = colors.HexColor("#FFEBEE")   # light red  — significant row
COLOUR_MED_BG   = colors.HexColor("#FFF3E0")   # light amber — outlier row
COLOUR_LOW_BG   = colors.HexColor("#F1F8E9")   # light green — normal row
COLOUR_HIGH     = colors.HexColor("#C62828")   # red text
COLOUR_MEDIUM   = colors.HexColor("#E65100")   # amber text
COLOUR_LOW      = colors.HexColor("#2E7D32")   # green text
COLOUR_SUBTEXT  = colors.HexColor("#616161")   # grey subtext
COLOUR_WHITE    = colors.white

# Usable page width: A4 (595.27pt) minus 1.5cm margins each side
MARGIN          = 1.5 * cm
PAGE_W          = A4[0] - 2 * MARGIN    # ~510pt / ~18cm


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _derive_title(period1_name: str) -> str:
    """Derive a professional report title from the period 1 file name."""
    name = period1_name.lower()

    if name.startswith("product"):
        domain = "Product"
    elif name.startswith("marketing"):
        domain = "Marketing"
    elif name.startswith("revenue"):
        domain = "Revenue"
    elif name.startswith("mixed"):
        domain = "Mixed"
    else:
        domain = "Metrics"

    if "week" in name:
        frequency = "Weekly"
    elif any(m in name for m in ["jan","feb","mar","apr","may","jun",
                                  "jul","aug","sep","oct","nov","dec",
                                  "month","monthly"]):
        frequency = "Monthly"
    elif any(q in name for q in ["quarter","qtr","q1","q2","q3","q4"]):
        frequency = "Quarterly"
    else:
        frequency = ""

    if frequency:
        return f"{domain} Metrics {frequency} Comparison Report"
    return f"{domain} Metrics Comparison Report"


def _derive_period_label(period_name: str) -> str:
    """Derive a readable period label from the file name."""
    name = period_name.lower()

    month_map = {
        "jan": "January", "feb": "February", "mar": "March",
        "apr": "April",   "may": "May",      "jun": "June",
        "jul": "July",    "aug": "August",   "sep": "September",
        "oct": "October", "nov": "November", "dec": "December",
    }

    # Pattern: week_apr28 → Week of 28 Apr 2025
    week_match = re.search(r'week[_\-]?([a-z]{3})(\d{1,2})', name)
    if week_match:
        mon  = month_map.get(week_match.group(1), week_match.group(1).capitalize())
        day  = week_match.group(2)
        year = re.search(r'(\d{4})', period_name)
        year = year.group(1) if year else str(datetime.now().year)
        return f"Week of {day} {mon} {year}"

    # Pattern: april_2025 or apr_2025
    for abbr, full in month_map.items():
        if abbr in name or full in name:
            year = re.search(r'(\d{4})', period_name)
            year = year.group(1) if year else str(datetime.now().year)
            return f"{full} {year}"

    return period_name


def _impact_level(finding: dict) -> str:
    if finding.get("is_significant"):
        return "HIGH"
    if finding.get("is_outlier"):
        return "MEDIUM"
    return "LOW"


def _impact_colours(finding: dict):
    """Return (text_colour, background_colour) for a finding."""
    level = _impact_level(finding)
    return {
        "HIGH":   (COLOUR_HIGH,   COLOUR_HIGH_BG),
        "MEDIUM": (COLOUR_MEDIUM, COLOUR_MED_BG),
        "LOW":    (COLOUR_LOW,    COLOUR_LOW_BG),
    }[level]


def _add_page_number(canvas, doc):
    """Draw page number at bottom right of every page."""
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(COLOUR_SUBTEXT)
    canvas.drawRightString(
        A4[0] - MARGIN,
        0.8 * cm,
        f"Page {doc.page}",
    )
    canvas.restoreState()


def _build_styles() -> dict:
    styles = {
        "title": ParagraphStyle(
            "ReportTitle",
            fontSize=13,
            fontName="Helvetica-Bold",
            textColor=COLOUR_WHITE,
            alignment=TA_LEFT,
            leading=17,
        ),
        "date_header": ParagraphStyle(
            "DateHeader",
            fontSize=8,
            fontName="Helvetica",
            textColor=COLOUR_WHITE,
            alignment=TA_RIGHT,
        ),
        "period_label": ParagraphStyle(
            "PeriodLabel",
            fontSize=8,
            fontName="Helvetica-Bold",
            textColor=COLOUR_SUBTEXT,
            spaceAfter=1,
        ),
        "period_value": ParagraphStyle(
            "PeriodValue",
            fontSize=9,
            fontName="Helvetica",
            textColor=colors.black,
        ),
        "summary": ParagraphStyle(
            "Summary",
            fontSize=8,
            fontName="Helvetica-Bold",
            textColor=COLOUR_SUBTEXT,
            alignment=TA_CENTER,
        ),
        "section_head": ParagraphStyle(
            "SectionHead",
            fontSize=8,
            fontName="Helvetica-Bold",
            textColor=COLOUR_SUBTEXT,
            spaceAfter=3,
            spaceBefore=4,
        ),
        "col_header": ParagraphStyle(
            "ColHeader",
            fontSize=7.5,
            fontName="Helvetica-Bold",
            textColor=COLOUR_SUBTEXT,
        ),
        "cell_metric": ParagraphStyle(
            "CellMetric",
            fontSize=8,
            fontName="Helvetica-Bold",
            textColor=colors.black,
            leading=11,
        ),
        "cell_body": ParagraphStyle(
            "CellBody",
            fontSize=7.5,
            fontName="Helvetica",
            textColor=colors.black,
            leading=10,
            wordWrap="CJK",
        ),
        "cell_insight": ParagraphStyle(
            "CellInsight",
            fontSize=7.5,
            fontName="Helvetica-Oblique",
            textColor=colors.HexColor("#333333"),
            leading=10,
            wordWrap="CJK",
        ),
        "impact_badge": ParagraphStyle(
            "ImpactBadge",
            fontSize=7.5,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
            leading=10,
        ),
        "footer": ParagraphStyle(
            "Footer",
            fontSize=6.5,
            fontName="Helvetica-Oblique",
            textColor=COLOUR_SUBTEXT,
            alignment=TA_CENTER,
            leading=9,
        ),
        "key": ParagraphStyle(
            "ImpactKey",
            fontSize=7,
            fontName="Helvetica",
            textColor=COLOUR_SUBTEXT,
            leading=9,
        ),
    }
    return styles


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def _build_header(styles: dict, title: str) -> list:
    gen_date = datetime.now().strftime("%-d %B %Y")
    tbl = Table(
        [[Paragraph(title, styles["title"]),
          Paragraph(f"Generated: {gen_date}", styles["date_header"])]],
        colWidths=[PAGE_W * 0.72, PAGE_W * 0.28],
    )
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), COLOUR_HEADER),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return [tbl]


def _build_period_strip(styles: dict, p1_label: str, p2_label: str) -> list:
    tbl = Table(
        [
            [Paragraph("Previous Period", styles["period_label"]),
             Paragraph("Current Period",  styles["period_label"])],
            [Paragraph(p1_label, styles["period_value"]),
             Paragraph(p2_label, styles["period_value"])],
        ],
        colWidths=[PAGE_W * 0.5, PAGE_W * 0.5],
    )
    tbl.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
    ]))
    return [Spacer(1, 0.25 * cm), tbl]


def _build_summary(styles: dict, findings: list) -> list:
    total       = len(findings)
    significant = sum(1 for f in findings if f.get("is_significant"))
    outliers    = sum(1 for f in findings if f.get("is_outlier"))

    text = (
        f"<b>{total}</b> change(s) detected"
        f"&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"<b>{significant}</b> statistically significant"
        f"&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"<b>{outliers}</b> outlier(s) flagged"
    )
    tbl = Table(
        [[Paragraph(text, styles["summary"])]],
        colWidths=[PAGE_W],
    )
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#E8EAF6")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
    ]))
    return [Spacer(1, 0.2 * cm), tbl]


def _build_findings_table(styles: dict, findings: list) -> list:
    # Column widths — must sum to exactly PAGE_W
    C_METRIC  = 3.5 * cm
    C_PREV    = 2.2 * cm
    C_CURR    = 2.2 * cm
    C_CHANGE  = 1.8 * cm
    C_IMPACT  = 1.6 * cm
    C_INSIGHT = PAGE_W - C_METRIC - C_PREV - C_CURR - C_CHANGE - C_IMPACT
    COL_WIDTHS = [C_METRIC, C_PREV, C_CURR, C_CHANGE, C_IMPACT, C_INSIGHT]

    # Header row
    header = [
        Paragraph("Metric",   styles["col_header"]),
        Paragraph("Previous", styles["col_header"]),
        Paragraph("Current",  styles["col_header"]),
        Paragraph("Change",   styles["col_header"]),
        Paragraph("Impact",   styles["col_header"]),
        Paragraph("Insight",  styles["col_header"]),
    ]

    rows       = [header]
    style_cmds = [
        # Header styling
        ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#E8EAF6")),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#BDBDBD")),
        ("FONTSIZE",      (0, 0), (-1, -1), 7.5),
    ]

    for i, finding in enumerate(findings):
        row_idx = i + 1
        txt_col, bg_col = _impact_colours(finding)
        level           = _impact_level(finding)

        metric  = finding.get("metric_name",    "—")
        prev    = str(finding.get("previous_value", "—"))
        curr    = str(finding.get("current_value",  "—"))
        delta   = str(finding.get("delta",          "—"))
        insight = finding.get("explanation", "")

        # Truncate insight to keep rows manageable
        if len(insight) > 200:
            insight = insight[:197] + "..."

        impact_para = Paragraph(
            f'<font color="#{txt_col.hexval()[1:]}"><b>{level}</b></font>',
            styles["impact_badge"],
        )

        rows.append([
            Paragraph(metric,  styles["cell_metric"]),
            Paragraph(prev,    styles["cell_body"]),
            Paragraph(curr,    styles["cell_body"]),
            Paragraph(delta,   styles["cell_body"]),
            impact_para,
            Paragraph(insight, styles["cell_insight"]),
        ])

        # Row background colour
        style_cmds.append(("BACKGROUND", (0, row_idx), (-1, row_idx), bg_col))
        # Bold impact text colour
        style_cmds.append(("TEXTCOLOR",  (4, row_idx), (4, row_idx), txt_col))

    tbl = Table(rows, colWidths=COL_WIDTHS)
    tbl.setStyle(TableStyle(style_cmds))

    return [
        Spacer(1, 0.2 * cm),
        Paragraph("FINDINGS", styles["section_head"]),
        tbl,
    ]


def _build_impact_key(styles: dict) -> list:
    text = (
        '<font color="#C62828"><b>■ HIGH</b></font> — statistically significant change'
        '&nbsp;&nbsp;&nbsp;'
        '<font color="#E65100"><b>■ MEDIUM</b></font> — outlier detected'
        '&nbsp;&nbsp;&nbsp;'
        '<font color="#2E7D32"><b>■ LOW</b></font> — within normal variation'
    )
    return [Spacer(1, 0.15 * cm), Paragraph(text, styles["key"])]


def _build_footer(styles: dict) -> list:
    text = (
        "This report was generated automatically by the Automated Metrics Comparison app. "
        "Findings are based on statistical analysis of the uploaded data. "
        "Review all findings and apply business context before sharing with stakeholders or making decisions."
    )
    return [
        Spacer(1, 0.3 * cm),
        HRFlowable(width="100%", thickness=0.4, color=COLOUR_SUBTEXT),
        Spacer(1, 0.1 * cm),
        Paragraph(text, styles["footer"]),
    ]


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_pdf(
    findings: list[dict],
    output_path: str,
    period1_name: str = "Period 1",
    period2_name: str = "Period 2",
) -> None:
    """
    Generate an A4 PDF report from findings.

    Parameters
    ----------
    findings     : list[dict] — from analysis.run_analysis()
    output_path  : str        — where to save the PDF
    period1_name : str        — file name (without extension) of Period 1
    period2_name : str        — file name (without extension) of Period 2
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=1.2 * cm,
        bottomMargin=1.5 * cm,   # extra bottom space for page number
    )

    styles   = _build_styles()
    title    = _derive_title(period1_name)
    p1_label = _derive_period_label(period1_name)
    p2_label = _derive_period_label(period2_name)

    story = []
    story += _build_header(styles, title)
    story += _build_period_strip(styles, p1_label, p2_label)
    story += _build_summary(styles, findings)
    story += _build_findings_table(styles, findings)
    story += _build_impact_key(styles)
    story += _build_footer(styles)

    doc.build(
        story,
        onFirstPage=_add_page_number,
        onLaterPages=_add_page_number,
    )
