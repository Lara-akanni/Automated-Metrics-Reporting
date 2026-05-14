"""
report.py
---------
PDF report generation from ranked LLM findings.

Takes the structured findings list produced by analysis.py and formats
it into a professional, downloadable PDF using ReportLab.

Main entry point:
  generate_pdf(findings, output_path) -> None
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from datetime import datetime


# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------

COLOUR_HIGH   = colors.HexColor("#D32F2F")   # red
COLOUR_MEDIUM = colors.HexColor("#F57C00")   # amber
COLOUR_LOW    = colors.HexColor("#388E3C")   # green
COLOUR_HEADER = colors.HexColor("#1A237E")   # dark blue


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _impact_colour(impact_level: str):
    """Return the ReportLab colour for a given impact level string."""
    return {
        "high":   COLOUR_HIGH,
        "medium": COLOUR_MEDIUM,
        "low":    COLOUR_LOW,
    }.get(impact_level.lower(), colors.grey)


def _build_styles():
    """Return a dict of named ParagraphStyles used in the report."""
    base = getSampleStyleSheet()

    # TODO: define custom styles for title, section header, finding header,
    # body text, and metric label using ParagraphStyle
    styles = {
        "title":          base["Title"],
        "section_header": base["Heading2"],
        "body":           base["BodyText"],
        # Add custom styles here
    }
    return styles


# ---------------------------------------------------------------------------
# Report sections
# ---------------------------------------------------------------------------

def _build_cover(styles: dict, period1_name: str, period2_name: str) -> list:
    """
    Build the cover / header section of the report.

    Returns a list of ReportLab Flowable objects.

    TODO: include report title, period labels, and generation timestamp.
    """
    # TODO: implement cover section
    return []


def _build_summary_table(findings: list[dict], styles: dict) -> list:
    """
    Build a summary table listing all findings with their impact level,
    metric name, and direction at a glance.

    Returns a list of ReportLab Flowable objects.

    TODO: create a Table with columns: Rank | Metric | Direction | Impact
    """
    # TODO: implement summary table
    return []


def _build_finding_section(finding: dict, rank: int, styles: dict) -> list:
    """
    Build the detailed section for a single finding.

    Includes: metric name, impact badge, Period 1 vs Period 2 values,
    delta, and the LLM-generated narrative explanation.

    Parameters
    ----------
    finding : dict   — one entry from the findings list
    rank    : int    — 1-based position in the ranked list
    styles  : dict   — paragraph styles

    Returns a list of ReportLab Flowable objects.

    TODO: implement individual finding block with colour-coded impact header.
    """
    # TODO: implement finding section
    return []


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
    Generate a formatted PDF report from ranked findings.

    Parameters
    ----------
    findings     : list[dict]
        Ranked findings from analysis.call_llm(). Each dict has keys:
        metric_name, previous_value, current_value, delta, direction,
        impact_level, explanation.
    output_path  : str
        File path where the PDF will be saved.
    period1_name : str
        Label for the baseline period (default "Period 1").
    period2_name : str
        Label for the comparison period (default "Period 2").

    Returns
    -------
    None. Writes the PDF to output_path.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = _build_styles()
    story = []

    # TODO: assemble the full story list by calling each section builder:
    # story += _build_cover(styles, period1_name, period2_name)
    # story += _build_summary_table(findings, styles)
    # for rank, finding in enumerate(findings, start=1):
    #     story += _build_finding_section(finding, rank, styles)

    doc.build(story)
