"""
app.py
------
Streamlit entry point for the Automated Metrics Comparison and Reporting app.

Flow:
  1. Analyst uploads two Excel files (Period 1 and Period 2)
  2. App parses, aligns, and computes deltas via analysis.py
  3. Gemini LLM detects changes and generates narrative via analysis.py
  4. Results are previewed in the UI
  5. Analyst downloads the PDF report generated via report.py
"""

import os
import tempfile
import streamlit as st
from analysis import run_analysis

# report.py is implemented separately — import guarded so the app still
# runs while report.py is being built
try:
    from report import generate_pdf
    PDF_AVAILABLE = True
except Exception:
    PDF_AVAILABLE = False


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
    "The app will detect all changes, run statistical checks, "
    "and surface findings with business-relevant explanations."
)

st.divider()

# ---------------------------------------------------------------------------
# File upload
# ---------------------------------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    st.subheader("Period 1 — Baseline")
    file_period1 = st.file_uploader(
        "Upload Period 1 Excel file",
        type=["xlsx", "xls"],
        key="period1",
    )

with col2:
    st.subheader("Period 2 — Current")
    file_period2 = st.file_uploader(
        "Upload Period 2 Excel file",
        type=["xlsx", "xls"],
        key="period2",
    )

st.divider()

# ---------------------------------------------------------------------------
# Run analysis
# ---------------------------------------------------------------------------

both_uploaded = file_period1 is not None and file_period2 is not None

if not both_uploaded:
    st.caption("Upload both files above to enable analysis.")

if st.button("▶ Run Analysis", disabled=not both_uploaded, type="primary"):

    with st.spinner("Analysing files and generating insights — this may take a moment..."):
        try:
            findings = run_analysis(file_period1, file_period2)
        except ValueError as e:
            st.error(f"⚠️ Could not run analysis: {e}")
            st.stop()
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            st.stop()

    # -----------------------------------------------------------------------
    # No findings
    # -----------------------------------------------------------------------
    if not findings:
        st.info("✅ No significant changes detected between the two files.")
        st.stop()

    # -----------------------------------------------------------------------
    # Results header
    # -----------------------------------------------------------------------
    st.success(f"Analysis complete — **{len(findings)}** change(s) detected.")
    st.caption(
        "All detected changes are shown below. "
        "Review and prioritise based on what matters most to your stakeholders."
    )

    # -----------------------------------------------------------------------
    # Findings cards
    # -----------------------------------------------------------------------
    st.subheader("Detected Changes")

    for i, finding in enumerate(findings, start=1):

        is_outlier     = finding.get("is_outlier",     False)
        is_significant = finding.get("is_significant", False)

        badges = ""
        if is_outlier:
            badges += " 🔺 Outlier"
        if is_significant:
            badges += " ⚠️ Significant"

        metric_label = finding.get("metric_name", f"Finding {i}")

        with st.expander(f"{i}. {metric_label}{badges}", expanded=(i == 1)):

            prev = finding.get("previous_value", "—")
            curr = finding.get("current_value",  "—")
            delta     = finding.get("delta",     "")
            direction = finding.get("direction", "—")

            # Format delta for st.metric — needs to be a string or number
            delta_display = str(delta) if delta not in (None, "", "—") else None

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Period 1", prev)
            col_b.metric("Period 2", curr, delta=delta_display)
            col_c.metric("Direction", direction.capitalize() if direction else "—")

            st.markdown(f"**Insight:** {finding.get('explanation', '_No explanation provided._')}")

            # Small stat badges
            badge_cols = st.columns(2)
            badge_cols[0].markdown(
                "🔺 **Outlier detected**" if is_outlier else "✔ No outlier"
            )
            badge_cols[1].markdown(
                "⚠️ **Statistically significant**" if is_significant
                else "✔ Not statistically significant"
            )

    # -----------------------------------------------------------------------
    # PDF download
    # -----------------------------------------------------------------------
    st.divider()
    st.subheader("Download Report")

    if PDF_AVAILABLE:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp_path = tmp.name

        try:
            p1_name = getattr(file_period1, "name", "Period 1")
            p2_name = getattr(file_period2, "name", "Period 2")
            generate_pdf(findings, tmp_path, period1_name=p1_name, period2_name=p2_name)

            with open(tmp_path, "rb") as f:
                st.download_button(
                    label="📥 Download PDF Report",
                    data=f,
                    file_name="metrics_report.pdf",
                    mime="application/pdf",
                )
        except Exception as e:
            st.warning(f"PDF generation failed: {e}")
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    else:
        st.info("📄 PDF report generation is coming soon.")
