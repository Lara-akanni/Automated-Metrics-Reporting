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
import json
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])


# ---------------------------------------------------------------------------
# Data preparation
# ---------------------------------------------------------------------------

def prepare_data_summary(file_period1, file_period2) -> str:
    """
    Load both Excel files and produce a plain-text summary of their
    contents to include in the prompt.

    Unlike the main app, no column alignment, delta computation, or
    tool calls are performed here — the raw data is passed directly
    to the model.

    Parameters
    ----------
    file_period1 : file-like object  — uploaded Period 1 Excel file
    file_period2 : file-like object  — uploaded Period 2 Excel file

    Returns
    -------
    str — a formatted text block describing both datasets for the prompt.
    """
    # TODO: load both files with pd.read_excel()
    # Convert each DataFrame to a readable string (e.g. df.to_string())
    # Return a combined summary string formatted as:
    #   "Period 1 data:\n<df1 string>\n\nPeriod 2 data:\n<df2 string>"
    pass


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
    return f"""You are a data analyst assistant. Below are two datasets from consecutive time periods.

{data_summary}

Compare Period 1 and Period 2. For each metric or column that changed:
- State what changed (the metric name, old value, new value)
- State the direction of change (increase, decrease, or categorical change)
- Explain what this change means in plain business language

List every change you detect. Do not skip any columns.
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

    Parameters
    ----------
    response_text : str
        The raw text response from the Gemini model.

    Returns
    -------
    list of dicts, each with keys:
        metric_name     : str   (extracted from response, best-effort)
        explanation     : str   (the model's explanation for this finding)
        previous_value  : str   (extracted if present, else "unknown")
        current_value   : str   (extracted if present, else "unknown")
        direction       : str   (extracted if present, else "unknown")

    Note: is_outlier and is_significant are not present in baseline output
    because no statistical tools were called.
    """
    # TODO: implement best-effort parsing of the freeform response
    # Strategy: split response into paragraphs or bullet points,
    # treat each as a separate finding, extract metric name from the
    # first sentence where possible
    # Return a list of dicts with the keys above
    pass


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
    # TODO: implement baseline pipeline
    # 1. Call prepare_data_summary(file_period1, file_period2)
    # 2. Call build_prompt(data_summary)
    # 3. Initialise genai.GenerativeModel (no tools passed)
    # 4. Call model.generate_content(prompt)
    # 5. Call parse_response(response.text)
    # 6. Return findings list
    pass
