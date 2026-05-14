"""
app.py
------
Streamlit entry point for the Automated Metrics Comparison and Reporting app.

Flow:
  1. Analyst uploads two Excel files (Period 1 and Period 2)
  2. App parses, aligns, and computes deltas via analysis.py
  3. Gemini LLM ranks findings and generates narrative via analysis.py
  4. Results are previewed in the UI
  5. Analyst downloads the PDF report generated via report.py
"""

import streamlit as st
from analysis import run_analysis
from report import generate_pdf
import tempfile
import os

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Automated Metrics Comparison",
    page_icon="📊",
    layout="centered",
)

st.title("📊 Automated Metrics Comparison & Reporting")
st.markdown(
    "Upload two Excel files from consecutive time periods. "
    "The app will compare them, rank the findings by impact, and generate a PDF report."
)

st.divider()

# ---------------------------------------------------------------------------
# File upload
# ---------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Period 1 (Baseline)")
    file_period1 = st.file_uploader(
        "Upload Period 1 Excel file",
        type=["xlsx", "xls"],
        key="period1",
    )

with col2:
    st.subheader("Period 2 (Comparison)")
    file_period2 = st.file_uploader(
        "Upload Period 2 Excel file",
        type=["xlsx", "xls"],
        key="period2",
    )

st.divider()

# ---------------------------------------------------------------------------
# Run analysis
# ---------------------------------------------------------------------------
if st.button("▶ Run Analysis", disabled=not (file_period1 and file_period2), type="primary"):

    with st.spinner("Analysing files and generating insights..."):
        # TODO: call run_analysis() once analysis.py is implemented
        # findings = run_analysis(file_period1, file_period2)
        findings = []  # placeholder

    if not findings:
        st.info("No significant changes detected between the two files.")
    else:
        st.success(f"Analysis complete — {len(findings)} finding(s) ranked by impact.")

        # -------------------------------------------------------------------
        # Display findings preview
        # -------------------------------------------------------------------
        st.subheader("Top Findings")

        for i, finding in enumerate(findings, start=1):
            # TODO: render each finding card once findings schema is confirmed
            # Expected keys: metric_name, previous_value, current_value,
            #                delta, direction, impact_level, explanation
            impact_colour = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢",
            }.get(finding.get("impact_level", "low"), "⚪")

            with st.expander(
                f"{impact_colour} {i}. {finding.get('metric_name', 'Metric')} "
                f"({finding.get('impact_level', '').capitalize()} Impact)"
            ):
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Period 1", finding.get("previous_value", "—"))
                col_b.metric(
                    "Period 2",
                    finding.get("current_value", "—"),
                    delta=str(finding.get("delta", "")),
                )
                col_c.metric("Direction", finding.get("direction", "—").capitalize())
                st.markdown(f"**Insight:** {finding.get('explanation', '')}")

        # -------------------------------------------------------------------
        # PDF download
        # -------------------------------------------------------------------
        st.divider()
        st.subheader("Download Report")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp_path = tmp.name

        # TODO: call generate_pdf() once report.py is implemented
        # generate_pdf(findings, tmp_path)

        # Placeholder download button (will serve real PDF once generate_pdf works)
        with open(tmp_path, "rb") as f:
            st.download_button(
                label="📥 Download PDF Report",
                data=f,
                file_name="metrics_report.pdf",
                mime="application/pdf",
            )

        os.unlink(tmp_path)

elif not (file_period1 and file_period2):
    st.caption("Upload both files above to enable analysis.")
