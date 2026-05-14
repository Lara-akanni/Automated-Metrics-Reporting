"""
tools.py
--------
Backend tool functions called by the Gemini LLM during analysis.

These functions handle all deterministic maths so the LLM never computes
statistics itself. This keeps results auditable and reproducible.

Functions exposed as tools:
  - compute_percentage_change(old_value, new_value)
  - detect_outliers(values)
  - run_significance_test(values_period1, values_period2)
"""

import numpy as np
from scipy import stats
from typing import Union
from google import genai
from google.genai import types


# ---------------------------------------------------------------------------
# Tool 1: Percentage change
# ---------------------------------------------------------------------------

def compute_percentage_change(
    old_value: Union[float, int],
    new_value: Union[float, int],
) -> dict:
    """
    Compute the percentage change between two numeric values.

    Parameters
    ----------
    old_value : float | int
        The value from the baseline period (Period 1).
    new_value : float | int
        The value from the comparison period (Period 2).

    Returns
    -------
    dict with keys:
        old_value         : original baseline value
        new_value         : original comparison value
        absolute_delta    : new_value - old_value
        percentage_change : rounded to 2 decimal places; None if old_value is 0
        direction         : "increase", "decrease", or "no change"
    """
    absolute_delta = new_value - old_value

    if old_value == 0:
        percentage_change = None
    else:
        percentage_change = round((absolute_delta / old_value) * 100, 2)

    if absolute_delta > 0:
        direction = "increase"
    elif absolute_delta < 0:
        direction = "decrease"
    else:
        direction = "no change"

    return {
        "old_value":         old_value,
        "new_value":         new_value,
        "absolute_delta":    absolute_delta,
        "percentage_change": percentage_change,
        "direction":         direction,
    }


# ---------------------------------------------------------------------------
# Tool 2: Outlier detection (IQR method)
# ---------------------------------------------------------------------------

def detect_outliers(values: list) -> dict:
    """
    Detect outliers in a list of numeric values using the
    interquartile range (IQR) method.

    A value is flagged as an outlier if it falls below
    Q1 - 1.5 * IQR  or above  Q3 + 1.5 * IQR.

    Parameters
    ----------
    values : list of float | int
        The numeric series to analyse (e.g. all values for one metric).

    Returns
    -------
    dict with keys:
        q1              : first quartile
        q3              : third quartile
        iqr             : interquartile range
        lower_bound     : Q1 - 1.5 * IQR
        upper_bound     : Q3 + 1.5 * IQR
        outliers        : list of values flagged as outliers
        outlier_indices : list of indices corresponding to flagged values
        has_outliers    : bool
    """
    if len(values) < 4:
        # Not enough data points for a meaningful IQR calculation
        return {
            "q1":              None,
            "q3":              None,
            "iqr":             None,
            "lower_bound":     None,
            "upper_bound":     None,
            "outliers":        [],
            "outlier_indices": [],
            "has_outliers":    False,
        }

    arr = np.array(values, dtype=float)
    q1  = float(np.percentile(arr, 25))
    q3  = float(np.percentile(arr, 75))
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outlier_indices = [
        i for i, v in enumerate(arr)
        if v < lower_bound or v > upper_bound
    ]
    outliers = [float(arr[i]) for i in outlier_indices]

    return {
        "q1":              round(q1, 4),
        "q3":              round(q3, 4),
        "iqr":             round(iqr, 4),
        "lower_bound":     round(lower_bound, 4),
        "upper_bound":     round(upper_bound, 4),
        "outliers":        outliers,
        "outlier_indices": outlier_indices,
        "has_outliers":    len(outliers) > 0,
    }


# ---------------------------------------------------------------------------
# Tool 3: Statistical significance test (Welch's t-test)
# ---------------------------------------------------------------------------

def run_significance_test(
    values_period1: list,
    values_period2: list,
    alpha: float = 0.05,
) -> dict:
    """
    Run a two-sample Welch's t-test to determine whether the difference
    between two sets of values is statistically significant.

    Welch's t-test is used (rather than Student's) because it does not
    assume equal variances between the two groups.

    Parameters
    ----------
    values_period1 : list of float | int
        Numeric values from the baseline period.
    values_period2 : list of float | int
        Numeric values from the comparison period.
    alpha : float
        Significance level threshold (default 0.05).

    Returns
    -------
    dict with keys:
        t_statistic    : the test statistic
        p_value        : two-tailed p-value
        is_significant : bool — True if p_value < alpha
        alpha          : the threshold used
        interpretation : plain-English string summarising the result
    """
    if len(values_period1) < 2 or len(values_period2) < 2:
        return {
            "t_statistic":    None,
            "p_value":        None,
            "is_significant": False,
            "alpha":          alpha,
            "interpretation": (
                "Not enough data points to run a significance test. "
                "At least 2 values are required in each period."
            ),
        }

    t_stat, p_value = stats.ttest_ind(
        values_period1,
        values_period2,
        equal_var=False,   # Welch's t-test
    )

    t_stat  = round(float(t_stat), 4)
    p_value = round(float(p_value), 4)
    is_significant = p_value < alpha

    if is_significant:
        interpretation = (
            f"The difference is statistically significant "
            f"(p={p_value}, which is below the threshold of {alpha}). "
            f"This change is unlikely to be due to random variation."
        )
    else:
        interpretation = (
            f"The difference is not statistically significant "
            f"(p={p_value}, which is above the threshold of {alpha}). "
            f"This change may be due to random variation."
        )

    return {
        "t_statistic":    t_stat,
        "p_value":        p_value,
        "is_significant": is_significant,
        "alpha":          alpha,
        "interpretation": interpretation,
    }


# ---------------------------------------------------------------------------
# Tool dispatcher
# ---------------------------------------------------------------------------

# Maps tool names (as Gemini will call them) to the actual Python functions.
# Used in analysis.py to execute the correct function when the LLM requests it.

TOOL_FUNCTIONS = {
    "compute_percentage_change": compute_percentage_change,
    "detect_outliers":           detect_outliers,
    "run_significance_test":     run_significance_test,
}


# ---------------------------------------------------------------------------
# Tool registry (passed to Gemini for function calling)
# ---------------------------------------------------------------------------

# Defines the schema Gemini uses to understand what each tool does
# and what arguments to pass when calling it.

TOOLS = [
    types.Tool(
        function_declarations=[

            # --- compute_percentage_change ---
            types.FunctionDeclaration(
                name="compute_percentage_change",
                description=(
                    "Compute the percentage change between two numeric values. "
                    "Returns the absolute delta, percentage change, and direction "
                    "(increase / decrease / no change). Returns None for percentage_change "
                    "if old_value is 0."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "old_value": types.Schema(
                            type=types.Type.NUMBER,
                            description="The numeric value from Period 1 (baseline).",
                        ),
                        "new_value": types.Schema(
                            type=types.Type.NUMBER,
                            description="The numeric value from Period 2 (comparison).",
                        ),
                    },
                    required=["old_value", "new_value"],
                ),
            ),

            # --- detect_outliers ---
            types.FunctionDeclaration(
                name="detect_outliers",
                description=(
                    "Detect outliers in a list of numeric values using the "
                    "interquartile range (IQR) method. A value is an outlier if it "
                    "falls below Q1 - 1.5*IQR or above Q3 + 1.5*IQR. "
                    "Requires at least 4 values for a meaningful result."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "values": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(type=types.Type.NUMBER),
                            description="List of numeric values to analyse for outliers.",
                        ),
                    },
                    required=["values"],
                ),
            ),

            # --- run_significance_test ---
            types.FunctionDeclaration(
                name="run_significance_test",
                description=(
                    "Run a two-sample Welch's t-test to determine whether the difference "
                    "between values from Period 1 and Period 2 is statistically significant. "
                    "Returns a p-value and a plain-English interpretation. "
                    "Requires at least 2 values in each period."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "values_period1": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(type=types.Type.NUMBER),
                            description="Numeric values from Period 1 (baseline).",
                        ),
                        "values_period2": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(type=types.Type.NUMBER),
                            description="Numeric values from Period 2 (comparison).",
                        ),
                        "alpha": types.Schema(
                            type=types.Type.NUMBER,
                            description="Significance threshold (default 0.05).",
                        ),
                    },
                    required=["values_period1", "values_period2"],
                ),
            ),

        ]
    )
]
