"""
analysis.py
-----------
Core pipeline: Excel parsing, column alignment, delta computation,
and Gemini LLM orchestration with tool use.

Main entry point:
  run_analysis(file_period1, file_period2) -> list[dict]

Pipeline steps:
  1. parse_excel()       — load each file into a DataFrame
  2. align_columns()     — match columns by name, flag mismatches
  3. compute_deltas()    — aggregate transaction data, compute per-column deltas
  4. call_llm()          — Gemini multi-turn tool loop, returns JSON findings
"""

import os
import json
import random
import pandas as pd
from google import genai
from google.genai import types
from dotenv import load_dotenv
from tools import TOOL_FUNCTIONS, TOOLS

load_dotenv(override=True)

# Minimum fraction of columns that must overlap for analysis to proceed
COLUMN_OVERLAP_THRESHOLD = 0.5


# ---------------------------------------------------------------------------
# Step 1: Parse Excel
# ---------------------------------------------------------------------------

def parse_excel(file) -> pd.DataFrame:
    """
    Load an uploaded Excel file into a pandas DataFrame.

    Parameters
    ----------
    file : file-like object or path
        The uploaded .xlsx / .xls file (from Streamlit's file_uploader).

    Returns
    -------
    pd.DataFrame with the file contents.

    Raises
    ------
    ValueError if the file cannot be parsed or is empty.
    """
    try:
        df = pd.read_excel(file, engine="openpyxl")
    except Exception as exc:
        raise ValueError(f"Could not read the Excel file: {exc}") from exc

    if df.empty:
        raise ValueError("The uploaded file contains no data.")

    # Strip leading / trailing whitespace from column names
    df.columns = [str(c).strip() for c in df.columns]
    return df


# ---------------------------------------------------------------------------
# Step 2: Align columns
# ---------------------------------------------------------------------------

def align_columns(df1: pd.DataFrame, df2: pd.DataFrame) -> dict:
    """
    Align two DataFrames by matching column names.

    Column names are normalised (stripped + lowercased) for comparison
    but the original names are preserved in the returned DataFrames.

    Parameters
    ----------
    df1 : pd.DataFrame  — Period 1 data
    df2 : pd.DataFrame  — Period 2 data

    Returns
    -------
    dict with keys:
        shared_columns   : list of column names present in both files
        only_in_period1  : list of columns only in Period 1
        only_in_period2  : list of columns only in Period 2
        overlap_ratio    : float (shared / total unique columns)
        df1_aligned      : df1 filtered to shared columns only
        df2_aligned      : df2 filtered to shared columns only

    Raises
    ------
    ValueError if overlap_ratio < COLUMN_OVERLAP_THRESHOLD
    """
    # Build lowercased → original name mapping for each file
    def _normalise_map(df):
        return {str(c).strip().lower(): str(c).strip() for c in df.columns}

    map1 = _normalise_map(df1)
    map2 = _normalise_map(df2)

    norm1 = set(map1.keys())
    norm2 = set(map2.keys())

    shared_norm = norm1 & norm2
    only_norm1  = norm1 - norm2
    only_norm2  = norm2 - norm1

    # Translate back to original names (use Period 1 names for shared columns)
    shared_columns   = [map1[n] for n in sorted(shared_norm)]
    only_in_period1  = [map1[n] for n in sorted(only_norm1)]
    only_in_period2  = [map2[n] for n in sorted(only_norm2)]

    total_unique = len(norm1 | norm2)
    overlap_ratio = len(shared_norm) / total_unique if total_unique > 0 else 0.0

    if overlap_ratio < COLUMN_OVERLAP_THRESHOLD:
        raise ValueError(
            f"Column overlap is too low ({overlap_ratio:.0%}). "
            f"At least {COLUMN_OVERLAP_THRESHOLD:.0%} of columns must match. "
            f"Period 1 columns: {list(df1.columns)}. "
            f"Period 2 columns: {list(df2.columns)}."
        )

    # Get the matching column names in df2 for shared columns
    shared_in_df2 = [map2[n] for n in sorted(shared_norm)]

    return {
        "shared_columns":  shared_columns,
        "only_in_period1": only_in_period1,
        "only_in_period2": only_in_period2,
        "overlap_ratio":   round(overlap_ratio, 4),
        "df1_aligned":     df1[shared_columns].copy(),
        "df2_aligned":     df2[shared_in_df2].rename(
                               columns=dict(zip(shared_in_df2, shared_columns))
                           ).copy(),
    }


# ---------------------------------------------------------------------------
# Step 3: Compute deltas
# ---------------------------------------------------------------------------

def compute_deltas(df1: pd.DataFrame, df2: pd.DataFrame) -> list[dict]:
    """
    Aggregate transaction-level data and compute per-column deltas.

    For numeric columns the function captures both the sum (useful for
    revenue / volume metrics) and the mean (useful for rate / score metrics),
    plus the raw value lists needed for outlier and significance testing.

    For categorical columns the function computes value-count distributions
    and percentage breakdowns for each unique category.

    Parameters
    ----------
    df1 : pd.DataFrame  — Period 1 (aligned, shared columns only)
    df2 : pd.DataFrame  — Period 2 (aligned, shared columns only)

    Returns
    -------
    list of dicts, one per column.
    Numeric dicts include:
        column_name, column_type, period1_sum, period2_sum,
        period1_mean, period2_mean, period1_values, period2_values,
        period1_row_count, period2_row_count
    Categorical dicts include:
        column_name, column_type, period1_value_counts,
        period2_value_counts, period1_percentages, period2_percentages,
        period1_total, period2_total, all_categories
    """
    deltas = []

    for col in df1.columns:
        if col not in df2.columns:
            continue  # should not happen after alignment, but guard anyway

        series1 = df1[col].dropna()
        series2 = df2[col].dropna()

        if pd.api.types.is_numeric_dtype(df1[col]):
            # ----- Numeric column -----
            # Cap at 100 values so Gemini's function call arguments stay small.
            # The summary stats (sum/mean) use the full series; the sample is
            # only used for outlier detection and significance testing.
            MAX_SAMPLE = 100
            all_vals1 = [round(float(v), 6) for v in series1.tolist()]
            all_vals2 = [round(float(v), 6) for v in series2.tolist()]
            random.seed(42)
            vals1 = random.sample(all_vals1, min(MAX_SAMPLE, len(all_vals1)))
            vals2 = random.sample(all_vals2, min(MAX_SAMPLE, len(all_vals2)))

            deltas.append({
                "column_name":      col,
                "column_type":      "numeric",
                "period1_sum":      round(float(series1.sum()),  4),
                "period2_sum":      round(float(series2.sum()),  4),
                "period1_mean":     round(float(series1.mean()), 4),
                "period2_mean":     round(float(series2.mean()), 4),
                "period1_values":   vals1,
                "period2_values":   vals2,
                "period1_row_count": len(vals1),
                "period2_row_count": len(vals2),
            })

        else:
            # ----- Categorical column -----
            counts1 = series1.astype(str).value_counts().to_dict()
            counts2 = series2.astype(str).value_counts().to_dict()

            total1 = len(series1)
            total2 = len(series2)

            pct1 = {
                k: round(v / total1 * 100, 2) if total1 > 0 else 0.0
                for k, v in counts1.items()
            }
            pct2 = {
                k: round(v / total2 * 100, 2) if total2 > 0 else 0.0
                for k, v in counts2.items()
            }

            all_categories = sorted(
                set(list(counts1.keys()) + list(counts2.keys())),
                key=lambda x: str(x),
            )

            deltas.append({
                "column_name":            col,
                "column_type":            "categorical",
                "period1_value_counts":   counts1,
                "period2_value_counts":   counts2,
                "period1_percentages":    pct1,
                "period2_percentages":    pct2,
                "period1_total":          total1,
                "period2_total":          total2,
                "all_categories":         all_categories,
            })

    return deltas


# ---------------------------------------------------------------------------
# Step 4: LLM call with tool use
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are a data analyst reviewing changes between two business reporting periods.

Period 1 is the BASELINE (earlier period).
Period 2 is the CURRENT period (the one being evaluated).

You have three tools available — use them to compute statistics before drawing conclusions:
  • compute_percentage_change  — quantify how much a numeric metric changed
  • detect_outliers            — check whether values in a series are statistical outliers
  • run_significance_test      — test whether a numeric change is statistically significant

INSTRUCTIONS
1. For EVERY numeric column:
   a. Call compute_percentage_change with the appropriate aggregate values
      (use period1_sum / period2_sum for volume/revenue/amount metrics;
       use period1_mean / period2_mean for rate/score metrics).
   b. Call detect_outliers on the combined period1_values list to flag anomalies.
   c. Call run_significance_test with period1_values and period2_values to assess
      whether the difference is statistically meaningful.

2. For EVERY categorical column:
   - Compare the percentage distributions across categories between periods.
   - Note any category that gained or lost more than 5 percentage points.
   - Set is_outlier and is_significant based on the magnitude of the shift.

3. Return ALL detected changes — do NOT rank, prioritise, or omit any finding.
   Every column with a measurable change must appear in the output.

4. Your FINAL response must be ONLY a valid JSON array — no markdown fences, no
   commentary, no text before or after the array.

OUTPUT SCHEMA  (one object per finding)
[
  {
    "metric_name":     "human-readable column/metric name",
    "previous_value":  <number or string>,
    "current_value":   <number or string>,
    "delta":           <number or descriptive string>,
    "direction":       "increase" | "decrease" | "no change" | "changed",
    "is_outlier":      true | false,
    "is_significant":  true | false,
    "explanation":     "Specific, business-relevant sentence a stakeholder can act on"
  },
  ...
]
"""


def call_llm(deltas: list[dict]) -> list[dict]:
    """
    Send delta data to Gemini with tool use enabled.

    The model calls compute_percentage_change, detect_outliers, and
    run_significance_test as needed, then returns a list of findings
    as structured JSON.

    Parameters
    ----------
    deltas : list[dict]
        Output from compute_deltas().

    Returns
    -------
    list of finding dicts (see _SYSTEM_PROMPT for the schema).

    Raises
    ------
    ValueError if the LLM response cannot be parsed as valid JSON.
    """
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    delta_json = json.dumps(deltas, indent=2)

    user_message = (
        "Below is the aggregated delta data comparing Period 1 (baseline) "
        "to Period 2 (current).\n\n"
        f"```json\n{delta_json}\n```\n\n"
        "Please use the available tools to compute statistics for every metric, "
        "then return the JSON findings array as instructed."
    )

    contents = [
        types.Content(
            role="user",
            parts=[types.Part(text=user_message)],
        )
    ]

    config = types.GenerateContentConfig(
        system_instruction=_SYSTEM_PROMPT,
        tools=TOOLS,
    )

    # Multi-turn tool call loop
    max_iterations = 30  # generous safety cap
    response = None

    for _ in range(max_iterations):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=config,
        )

        # Guard against empty or blocked responses
        if not response.candidates:
            raise ValueError("Gemini returned no candidates. The request may have been blocked.")

        candidate = response.candidates[0]

        if candidate.content is None:
            finish_reason = getattr(candidate, "finish_reason", "unknown")
            raise ValueError(
                f"Gemini returned empty content (finish_reason: {finish_reason}). "
                "This may be a safety filter or an API issue."
            )

        candidate_parts = candidate.content.parts or []

        # Append model turn to conversation history
        contents.append(
            types.Content(role="model", parts=candidate_parts)
        )

        # Collect any function calls in this turn
        fn_call_parts = [p for p in candidate_parts if p.function_call is not None]

        if not fn_call_parts:
            # No tool calls → this is the final response
            break

        # Execute each tool and gather function responses
        fn_response_parts = []
        for part in fn_call_parts:
            fn_name = part.function_call.name
            fn_args = dict(part.function_call.args)

            if fn_name in TOOL_FUNCTIONS:
                result = TOOL_FUNCTIONS[fn_name](**fn_args)
            else:
                result = {"error": f"Unknown function: {fn_name}"}

            fn_response_parts.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=fn_name,
                        response=result,
                    )
                )
            )

        # Return tool results to the model
        contents.append(
            types.Content(role="user", parts=fn_response_parts)
        )

    if response is None:
        raise ValueError("No response received from the LLM.")

    # Extract the final text from the last model turn
    final_text = "".join(
        p.text for p in response.candidates[0].content.parts
        if hasattr(p, "text") and p.text
    ).strip()

    # Strip markdown code fences if the model wrapped the JSON
    if final_text.startswith("```"):
        lines = final_text.splitlines()
        # Remove opening fence (```json or ```)
        lines = lines[1:] if lines[0].startswith("```") else lines
        # Remove closing fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        final_text = "\n".join(lines).strip()

    try:
        findings = json.loads(final_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM response could not be parsed as JSON: {exc}\n"
            f"Raw response (first 800 chars):\n{final_text[:800]}"
        ) from exc

    if not isinstance(findings, list):
        raise ValueError(
            f"Expected a JSON array of findings, got {type(findings).__name__}."
        )

    return findings


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_analysis(file_period1, file_period2) -> list[dict]:
    """
    Full pipeline: parse → align → delta → LLM → findings.

    Parameters
    ----------
    file_period1 : file-like object  — uploaded Period 1 Excel file
    file_period2 : file-like object  — uploaded Period 2 Excel file

    Returns
    -------
    list of finding dicts (see call_llm for the schema).
    Returns an empty list if no changes are detected.
    """
    df1 = parse_excel(file_period1)
    df2 = parse_excel(file_period2)

    alignment = align_columns(df1, df2)
    deltas     = compute_deltas(alignment["df1_aligned"], alignment["df2_aligned"])

    if not deltas:
        return []

    findings = call_llm(deltas)
    return findings
