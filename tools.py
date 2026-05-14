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
        old_value       : original baseline value
        new_value       : original comparison value
        absolute_delta  : new_value - old_value
        percentage_change : rounded to 2 decimal places; None if old_value is 0
        direction       : "increase", "decrease", or "no change"
    """
    # TODO: implement percentage change logic
    # Guard against division by zero when old_value == 0
    pass


# ---------------------------------------------------------------------------
# Tool 2: Outlier detection (IQR method)
# ---------------------------------------------------------------------------

def detect_outliers(values: list[Union[float, int]]) -> dict:
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
    # TODO: implement IQR outlier detection
    pass


# ---------------------------------------------------------------------------
# Tool 3: Statistical significance test (Welch's t-test)
# ---------------------------------------------------------------------------

def run_significance_test(
    values_period1: list[Union[float, int]],
    values_period2: list[Union[float, int]],
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
        t_statistic     : the test statistic
        p_value         : two-tailed p-value
        is_significant  : bool — True if p_value < alpha
        alpha           : the threshold used
        interpretation  : plain-English string summarising the result
    """
    # TODO: implement Welch's t-test using scipy.stats.ttest_ind(equal_var=False)
    pass


# ---------------------------------------------------------------------------
# Tool registry (passed to Gemini for function calling)
# ---------------------------------------------------------------------------

# TODO: define the tools list in the format expected by google-generativeai
# Each entry should be a genai.protos.Tool / FunctionDeclaration describing
# the function name, description, and parameter schema.

TOOLS = [
    # compute_percentage_change declaration
    # detect_outliers declaration
    # run_significance_test declaration
]
