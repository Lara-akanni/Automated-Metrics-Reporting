"""
baseline.py
-----------
Prompt-only baseline for comparison against the main app.

This module uses the same Gemini model as the main app but with:
  - No tool use / function calling
  - No structured output enforcement
  - A single direct prompt asking the model to identify and explain changes

It is run on the same synthetic test cases as the main app and scored
against the same ground_truth.json using the same rubric (evals.py).
The score difference shows the value that tool use and structured outputs
add to the analysis.

Main entry point:
  run_baseline(file_period1, file_period2) -> list[dict]
"""

import os
import re
import json
import pandas as pd
from google import genai
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# Data preparation
# ---------------------------------------------------------------------------

def prepare_data_summary(file_period1, file_period2) -> str:
    """
    Load both Excel files and produce a plain-text summary of their contents
    to include in the prompt.

    For numeric columns  → reports sum, mean, min, max, and row count.
    For categorical cols → reports per-category counts and percentages.

    Unlike the main app, no column alignment, delta computation, or tool
    calls are performed here — the LLM receives only this text summary and
    must identify changes on its own.

    Parameters
    ----------
    file_period1 : file-like object  — uploaded Period 1 Excel file
    file_period2 : file-like object  — uploaded Period 2 Excel file

    Returns
    -------
    str — a formatted text block describing both datasets for the prompt.
    """
    df1 = pd.read_excel(file_period1, engine="openpyxl")
    df2 = pd.read_excel(file_period2, engine="openpyxl")

    # Normalise column names
    df1.columns = [str(c).strip() for c in df1.columns]
    df2.columns = [str(c).strip() for c in df2.columns]

    def _summarise(df: pd.DataFrame, label: str) -> str:
        lines = [
            f"{label}",
            f"Rows: {len(df)}  |  Columns: {len(df.columns)}",
            f"Column list: {', '.join(df.columns.tolist())}",
            "",
        ]

        for col in df.columns:
            series = df[col].dropna()
            if pd.api.types.is_numeric_dtype(df[col]):
                lines.append(
                    f"  [{col}]  numeric — "
                    f"sum={series.sum():.4g}, "
                    f"mean={series.mean():.4g}, "
                    f"min={series.min():.4g}, "
                    f"max={series.max():.4g}, "
                    f"n={len(series)}"
                )
            else:
                total = len(series)
                counts = series.value_counts()
                dist = ", ".join(
                    f"{k}: {v} ({v / total * 100:.1f}%)"
                    for k, v in counts.items()
                )
                lines.append(f"  [{col}]  categorical — {dist}")

        return "\n".join(lines)

    summary1 = _summarise(df1, "=== PERIOD 1 (baseline) ===")
    summary2 = _summarise(df2, "=== PERIOD 2 (current)  ===")

    return f"{summary1}\n\n{summary2}"


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def build_prompt(data_summary: str) -> str:
    """
    Build the prompt sent to Gemini for the prompt-only baseline.

    The prompt asks the model to identify and explain all changes between
    the two datasets. No tools are provided and no JSON schema is enforced.

    Parameters
    ----------
    data_summary : str
        The plain-text data summary from prepare_data_summary().

    Returns
    -------
    str — the full prompt string.
    """
    return f"""You are a data analyst assistant. Below are summary statistics for two datasets \
from consecutive reporting periods. Period 1 is the baseline; Period 2 is the current period.

{data_summary}

Compare Period 1 and Period 2. For EVERY metric or column that changed:
- State the metric name
- State the old value (Period 1) and the new value (Period 2)
- State the direction of change (increase, decrease, or categorical shift)
- Explain what this change means in plain business language — be specific, \
not generic

List every change you detect. Do not skip any column. Do not rank or \
prioritise — surface all changes for analyst review.
"""


# ---------------------------------------------------------------------------
# Parse model response
# ---------------------------------------------------------------------------

def parse_response(response_text: str) -> list[dict]:
    """
    Parse the model's freeform text response into a list of finding dicts.

    Because the baseline does not enforce a JSON schema, this function
    does a best-effort parse of the model's output into a structure
    compatible with the eval rubric.

    Strategy:
      1. Split the response into bullet points, numbered items, or paragraphs.
      2. Treat each chunk as a separate finding.
      3. Extract metric name from the first line/sentence of each chunk.
      4. Scan for "from X to Y" patterns to capture previous/current values.
      5. Detect direction keywords (increase / decrease / changed).

    Parameters
    ----------
    response_text : str
        The raw text response from the Gemini model.

    Returns
    -------
    list of dicts, each with keys:
        metric_name     : str   (extracted from response, best-effort)
        explanation     : str   (the model's full explanation for this finding)
        previous_value  : str   (extracted if present, else "unknown")
        current_value   : str   (extracted if present, else "unknown")
        direction       : str   (increase / decrease / no change / changed)

    Note: is_outlier and is_significant are absent — no statistical tools
    were called in the baseline.
    """
    if not response_text or not response_text.strip():
        return []

    # Split on bullet/numbered-list markers or on blank lines between paragraphs
    chunks = re.split(r'\n(?=\s*[-*•]|\s*\d+[.)]\s|\n)', response_text.strip())
    chunks = [c.strip() for c in chunks if c.strip()]

    findings = []

    for chunk in chunks:
        # Strip leading list markers (-, *, •, 1., 2), etc.)
        clean = re.sub(r'^\s*[-*•]\s*', '', chunk)
        clean = re.sub(r'^\s*\d+[.)]\s*', '', clean).strip()

        if len(clean) < 10:          # skip very short fragments
            continue

        # --- metric name: first sentence or first line, capped at 100 chars ---
        first_line = re.split(r'[\n:]', clean)[0].strip()
        # Remove trailing punctuation
        metric_name = re.sub(r'[.,:;]+$', '', first_line)[:100]

        # --- previous / current values: "from X to Y" or "X → Y" patterns ---
        prev_val = "unknown"
        curr_val = "unknown"

        from_to = re.search(
            r'from\s+([\d,. %]+\S*)\s+to\s+([\d,. %]+\S*)',
            clean, re.IGNORECASE
        )
        if from_to:
            prev_val = from_to.group(1).strip()
            curr_val = from_to.group(2).strip()
        else:
            arrow = re.search(r'([\d,.%]+)\s*[→➔]\s*([\d,.%]+)', clean)
            if arrow:
                prev_val = arrow.group(1).strip()
                curr_val = arrow.group(2).strip()

        # --- direction ---
        low = clean.lower()
        if re.search(r'\b(increas|grew|risen?|higher|uptick|upward|up\b)', low):
            direction = "increase"
        elif re.search(r'\b(decreas|fell|fallen|drop|lower|declin|downward|down\b)', low):
            direction = "decrease"
        elif re.search(r'\b(no change|unchanged|stable|flat\b)', low):
            direction = "no change"
        else:
            direction = "changed"

        findings.append({
            "metric_name":    metric_name,
            "explanation":    clean,
            "previous_value": prev_val,
            "current_value":  curr_val,
            "direction":      direction,
        })

    return findings


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_baseline(file_period1, file_period2) -> list[dict]:
    """
    Run the prompt-only baseline on two Excel files.

    Sends both datasets to Gemini in a single prompt with no tool use
    and no structured output enforcement. Parses the freeform response
    into a list of finding dicts for scoring by evals.py.

    Parameters
    ----------
    file_period1 : file-like object  — uploaded Period 1 Excel file
    file_period2 : file-like object  — uploaded Period 2 Excel file

    Returns
    -------
    list of finding dicts (see parse_response for schema).
    Returns an empty list if the model produces no usable output.
    """
    data_summary = prepare_data_summary(file_period1, file_period2)
    prompt       = build_prompt(data_summary)

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        # No tools, no structured output — intentionally bare prompt
    )

    response_text = response.text or ""
    return parse_response(response_text)
