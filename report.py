"""
report.py
---------
PDF report generation from LLM findings.

Takes the structured findings list produced by analysis.py and formats
it into a professional, one-page A4 PDF using ReportLab.

Main entry point:
  generate_pdf(findings, output_path, period1_name, period2_name) -> None

Design:
  - Header bar (dark blue) with report title and generation date
  - Period strip showing previous and current period labels
  - Summary row: total findings | significant | outliers
  - Findings table: one compact row per finding with colour-coded impact strip
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

COLOUR_HEADER  = colors.HexColor("#1A237E")   # dark blue — header bar
COLOUR_HIGH    = colors.HexColor("#C62828")   # red       — significant
COLOUR_MEDIUM  = colors.HexColor("#E65100")   # amber     — outlier only
COLOUR_LOW     = colors.HexColor("#2E7D32")   # green     — normal variation
COLOUR_STRIP   = colors.HexColor("#F5F5F5")   # light grey — alternate rows
COLOUR_WHITE   = colors.white
COLOUR_SUBTEXT = colors.HexColor("#616161")   # grey for subtext


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _derive_title(period1_name: str) -> str:
    """
    Derive a professional report title from the period 1 file name.
    e.g. 'Product_week_apr28' → 'Product Metrics Weekly Comparison Report'
    """
    name = period1_name.lower()

    # Domain
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

    # Frequency
    if "week" in name:
        frequency = "Weekly"
    elif any(m in name for m in ["jan","feb","mar","apr","may","jun",
                                  "jul","aug","sep","oct","nov","dec",
                                  "month","monthly"]):
        frequency = "Monthly"
    elif "quarter" in name or "qtr" in name or "q1" in name or "q2" in name:
        frequency = "Quarterly"
    else:
        frequency = ""

    if frequency:
        return f"{domain} Metrics {frequency} Comparison Report"
    return f"{domain} Metrics Comparison Report"


def _derive_period_label(period_name: str) -> str:
    """
    Derive a readable period label from the file name.
    e.g. 'Product_week_apr28' → 'Week of 28 Apr 2025'
         'Revenue_april_2025' → 'April 2025'
    Falls back to the original name if no pattern is matched.
    """
    name = period_name.lower()

    month_map = {
        "jan": "January", "feb": "February", "mar": "March",
        "apr": "April",   "may": "May",      "jun": "June",
        "jul": "July",    "aug": "August",   "sep": "September",
        "oct": "October", "nov": "November", "dec": "December",
    }

    # Pattern: week_apr28  → Week of 28 Apr
    week_match = re.search(r'week[_\-]?([a-z]{3})(\d{1,2})', name)
    if week_match:
        mon = month_map.get(week_match.group(1), week_match.group(1).capitalize())
        day = week_match.group(2)
        # Try to extract year
        year_match = re.search(r'(\d{4})', period_name)
        year = year_match.group(1) if year_match else str(datetime.now().year)
        return f"Week of {day} {mon} {year}"

    # Pattern: april_2025 or apr_2025
    for abbr, full in month_map.items():
        if abbr in name or full in name:
            year_match = re.search(r'(\d{4})', period_name)
            year = year_match.group(1) if year_match else str(datetime.now().year)
            return f"{full} {year}"

    return period_name  # fallback


def _impact_label(finding: dict) -> str:
    if finding.get("is_significant"):
        return "HIGH"
    if finding.get("is_outlier"):
        return "MEDIUM"
    return "LOW"


def _impact_colour(finding: dict):
    level = _impact_label(finding)
    return {
        "HIGH":   COLOUR_HIGH,
        "MEDIUM": COLOUR_MEDIUM,
        "LOW":    COLOUR_LOW,
    }[level]


def _build_styles() -> dict:
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "ReportTitle",
            fontSize=14,
            fontName="Helvetica-Bold",
            textColor=COLOUR_WHITE,
            alignment=TA_LEFT,
            spaceAfter=0,
            leading=18,
        ),
        "date": ParagraphStyle(
            "ReportDate",
            fontSize=9,
            fontName="Helvetica",
            textColor=COLOUR_WHITE,
            alignment=TA_RIGHT,
            spaceAfter=0,
        ),
        "period_label": ParagraphStyle(
            "PeriodLabel",
            fontSize=9,
            fontName="Helvetica-Bold",
            textColor=COLOUR_SUBTEXT,
            spaceAfter=2,
        ),
        "period_value": ParagraphStyle(
            "PeriodValue",
            fontSize=10,
            fontName="Helvetica",
            textColor=colors.black,
            spaceAfter=0,
        ),
        "summary": ParagraphStyle(
            "Summary",
            fontSize=9,
            fontName="Helvetica-Bold",
            textColor=COLOUR_SUBTEXT,
            alignment=TA_CENTER,
        ),
        "section_head": ParagraphStyle(
            "SectionHead",
            fontSize=9,
            fontName="Helvetica-Bold",
            textColor=COLOUR_SUBTEXT,
            spaceAfter=4,
            spaceBefore=6,
        ),
        "cell_metric": ParagraphStyle(
            "CellMetric",
            fontSize=9,
            fontName="Helvetica-Bold",
            textColor=colors.black,
            leading=12,
        ),
        "cell_body": ParagraphStyle(
            "CellBody",
            fontSize=8,
            fontName="Helvetica",
            textColor=colors.black,
            leading=11,
            wordWrap="CJK",
        ),
        "cell_insight": ParagraphStyle(
            "CellInsight",
            fontSize=7.5,
            fontName="Helvetica-Oblique",
            textColor=colors.HexColor("#424242"),
            leading=10,
            wordWrap="CJK",
        ),
        "impact_label": ParagraphStyle(
            "ImpactLabel",
            fontSize=8,
            fontName="Helvetica-Bold",
            textColor=COLOUR_WHITE,
            alignment=TA_CENTER,
            leading=10,
        ),
        "footer": ParagraphStyle(
            "Footer",
            fontSize=7,
            fontName="Helvetica-Oblique",
            textColor=COLOUR_SUBTEXT,
            alignment=TA_CENTER,
            leading=9,
        ),
    }
    return styles


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def _build_header(styles: dict, title: str) -> list:
    """Dark blue header bar with title on left and date on right."""
    gen_date = datetime.now().strftime("%-d %B %Y")

    header_table = Table(
        [[Paragraph(title, styles["title"]),
          Paragraph(f"Generated: {gen_date}", styles["date"])]],
        colWidths=["70%", "30%"],
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), COLOUR_HEADER),
        ("TOPPADDING",  (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",  (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return [header_table]


def _build_period_strip(styles: dict, p1_label: str, p2_label: str) -> list:
    """Two-column strip showing previous and current period labels."""
    strip = Table(
        [[
            Paragraph("Previous Period", styles["period_label"]),
            Paragraph("Current Period", styles["period_label"]),
        ],[
            Paragraph(p1_label, styles["period_value"]),
            Paragraph(p2_label, styles["period_value"]),
        ]],
        colWidths=["50%", "50%"],
    )
    strip.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
    ]))
    return [Spacer(1, 0.3 * cm), strip]


def _build_summary(styles: dict, findings: list) -> list:
    """Single summary row: total | significant | outliers."""
    total       = len(findings)
    significant = sum(1 for f in findings if f.get("is_significant"))
    outliers    = sum(1 for f in findings if f.get("is_outlier"))

    summary_text = (
        f"<b>{total}</b> change(s) detected"
        f"&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"<b>{significant}</b> statistically significant"
        f"&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"<b>{outliers}</b> outlier(s) flagged"
    )

    summary_table = Table(
        [[Paragraph(summary_text, styles["summary"])]],
        colWidths=["100%"],
    )
    summary_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#E8EAF6")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
    ]))
    return [Spacer(1, 0.25 * cm), summary_table]


def _build_findings_table(styles: dict, findings: list) -> list:
    """Compact findings table — one row per finding with impact colour strip."""
    PAGE_WIDTH   = A4[0] - 4 * cm   # usable width (2cm margins each side)
    COL_WIDTHS   = [
        0.5  * cm,   # impact colour strip
        3.2  * cm,   # metric name
        2.2  * cm,   # previous value
        2.2  * cm,   # current value
        1.8  * cm,   # change
        1.6  * cm,   # impact label
        PAGE_WIDTH - 0.5 - 3.2 - 2.2 - 2.2 - 1.8 - 1.6,  # insight
    ]

    # Header row
    header = [
        Paragraph("", styles["cell_body"]),
        Paragraph("Metric", styles["section_head"]),
        Paragraph("Previous", styles["section_head"]),
        Paragraph("Current", styles["section_head"]),
        Paragraph("Change", styles["section_head"]),
        Paragraph("Impact", styles["section_head"]),
        Paragraph("Insight", styles["section_head"]),
    ]

    rows = [header]
    row_colours = []

    for i, finding in enumerate(findings):
        imp_colour = _impact_colour(finding)
        imp_label  = _impact_label(finding)

        metric   = finding.get("metric_name",    "—")
        prev_val = str(finding.get("previous_value", "—"))
        curr_val = str(finding.get("current_value",  "—"))
        delta    = str(finding.get("delta",          "—"))
        insight  = finding.get("explanation", "")

        # Truncate insight to keep rows compact
        if len(insight) > 160:
            insight = insight[:157] + "..."

        impact_para = Paragraph(
            f'<font color="white"><b>{imp_label}</b></font>',
            styles["impact_label"],
        )

        row = [
            Paragraph("", styles["cell_body"]),           # colour strip column
            Paragraph(metric,   styles["cell_metric"]),
            Paragraph(prev_val, styles["cell_body"]),
            Paragraph(curr_val, styles["cell_body"]),
            Paragraph(delta,    styles["cell_body"]),
            impact_para,
            Paragraph(insight,  styles["cell_insight"]),
        ]
        rows.append(row)

        # Track colour for this data row (index = i + 1 because row 0 is header)
        row_colours.append((i + 1, imp_colour))

    table = Table(rows, colWidths=COL_WIDTHS, repeatRows=1)

    style_cmds = [
        # Header
        ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#E8EAF6")),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 8),
        ("TEXTCOLOR",     (0, 0), (-1, 0), COLOUR_SUBTEXT),
        # All rows
        ("FONTSIZE",      (0, 1), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("GRID",          (1, 0), (-1, -1), 0.3, colors.HexColor("#E0E0E0")),
        ("NOSPLIT",       (0, 0), (-1, -1)),
    ]

    # Colour strip column and impact label per data row
    for row_idx, imp_colour in row_colours:
        style_cmds.append(("BACKGROUND", (0, row_idx), (0, row_idx), imp_colour))
        style_cmds.append(("BACKGROUND", (5, row_idx), (5, row_idx), imp_colour))
        # Alternating light background for even rows
        if row_idx % 2 == 0:
            style_cmds.append(
                ("BACKGROUND", (1, row_idx), (4, row_idx), COLOUR_STRIP)
            )
            style_cmds.append(
                ("BACKGROUND", (6, row_idx), (6, row_idx), COLOUR_STRIP)
            )

    table.setStyle(TableStyle(style_cmds))

    return [
        Spacer(1, 0.25 * cm),
        Paragraph("FINDINGS", styles["section_head"]),
        table,
    ]


def _build_footer(styles: dict) -> list:
    text = (
        "This report was generated automatically by the Automated Metrics Comparison app. "
        "Findings are based on statistical analysis of the uploaded data. "
        "Review all findings and apply business context before sharing with stakeholders or making decisions."
    )
    return [
        Spacer(1, 0.3 * cm),
        HRFlowable(width="100%", thickness=0.5, color=COLOUR_SUBTEXT),
        Spacer(1, 0.15 * cm),
        Paragraph(text, styles["footer"]),
    ]


def _build_impact_key(styles: dict) -> list:
    """Small impact key legend below the findings table."""
    key_text = (
        '<font color="#C62828"><b>■ HIGH</b></font> — statistically significant change'
        '&nbsp;&nbsp;&nbsp;'
        '<font color="#E65100"><b>■ MEDIUM</b></font> — outlier detected'
        '&nbsp;&nbsp;&nbsp;'
        '<font color="#2E7D32"><b>■ LOW</b></font> — within normal variation'
    )
    key_style = ParagraphStyle(
        "ImpactKey",
        fontSize=7,
        fontName="Helvetica",
        textColor=COLOUR_SUBTEXT,
        leading=9,
    )
    return [Spacer(1, 0.15 * cm), Paragraph(key_text, key_style)]


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
    Generate a one-page A4 PDF report from findings.

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
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles    = _build_styles()
    title     = _derive_title(period1_name)
    p1_label  = _derive_period_label(period1_name)
    p2_label  = _derive_period_label(period2_name)

    story = []
    story += _build_header(styles, title)
    story += _build_period_strip(styles, p1_label, p2_label)
    story += _build_summary(styles, findings)
    story += _build_findings_table(styles, findings)
    story += _build_impact_key(styles)
    story += _build_footer(styles)

    doc.build(story)
