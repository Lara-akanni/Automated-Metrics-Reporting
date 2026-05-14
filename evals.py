"""
evals.py
--------
Evaluation script for scoring app output against ground truth.

Rubric (each dimension scored 1–3, max 9 points):
  1. Change Detection    — did the app catch all major changes?
  2. Ranking Correctness — are the most impactful findings at the top?
  3. Explanation Quality — are narratives clear and business-relevant?

A score of 7+ indicates strong performance.

Usage:
  python evals.py                          # run all test cases in eval_cases/
  python evals.py --case product_metrics   # run a single named test case
"""

import os
import json
import argparse
import pandas as pd
from analysis import run_analysis


# ---------------------------------------------------------------------------
# Scoring constants
# ---------------------------------------------------------------------------

MAX_SCORE_PER_DIMENSION = 3
NUM_DIMENSIONS          = 3
MAX_TOTAL_SCORE         = MAX_SCORE_PER_DIMENSION * NUM_DIMENSIONS  # 9
STRONG_PERFORMANCE      = 7


# ---------------------------------------------------------------------------
# Rubric scoring functions
# ---------------------------------------------------------------------------

def score_change_detection(app_findings: list[dict], ground_truth: list[dict]) -> int:
    """
    Score dimension 1: Change Detection.

    Compare the metric names in app_findings against the expected changes
    listed in ground_truth.

    Scoring:
      3 — app caught all expected changes
      2 — app caught most (≥ 75%) of expected changes
      1 — app missed key changes (< 75% caught)

    Parameters
    ----------
    app_findings  : list of finding dicts from run_analysis()
    ground_truth  : list of dicts from the test case JSON, each with
                    at least a "metric_name" key

    Returns
    -------
    int score (1, 2, or 3)
    """
    # TODO: implement change detection scoring
    # Extract metric names from both lists (normalise to lowercase)
    # Compute recall = matched / total expected
    pass


def score_ranking_correctness(app_findings: list[dict], ground_truth: list[dict]) -> int:
    """
    Score dimension 2: Ranking Correctness.

    Check whether the app's top-ranked findings match the expected
    high-impact findings from ground_truth.

    Scoring:
      3 — ranking is fully correct (top findings match expected order)
      2 — mostly correct (top finding is right; minor ordering issues)
      1 — ranking is wrong (low-impact findings ranked above high-impact ones)

    Parameters
    ----------
    app_findings  : list of finding dicts (already sorted by app, most to least impactful)
    ground_truth  : list of dicts sorted by expected impact (most impactful first),
                    each with "metric_name" and "expected_impact_level"

    Returns
    -------
    int score (1, 2, or 3)
    """
    # TODO: implement ranking correctness scoring
    pass


def score_explanation_quality(app_findings: list[dict]) -> int:
    """
    Score dimension 3: Explanation Quality.

    Manually reviewed dimension — this function provides a prompt and
    structured template for the human reviewer to score each explanation.

    Scoring:
      3 — explanations are clear, specific, and business-relevant
      2 — explanations are acceptable but generic or vague
      1 — explanations are unclear, missing, or misleading

    Parameters
    ----------
    app_findings : list of finding dicts with "explanation" keys

    Returns
    -------
    int score entered by the human reviewer (1, 2, or 3)
    """
    # TODO: print each explanation and prompt the reviewer for a score
    # For automated runs, default to None and flag for manual review
    pass


# ---------------------------------------------------------------------------
# Single test case runner
# ---------------------------------------------------------------------------

def run_test_case(case_path: str) -> dict:
    """
    Run the app against a single test case and return its scores.

    A test case directory contains:
      period1.xlsx         — baseline period input file
      period2.xlsx         — comparison period input file
      ground_truth.json    — expected findings (see eval_cases/README)

    Parameters
    ----------
    case_path : str
        Path to the test case directory.

    Returns
    -------
    dict with keys:
        case_name               : str
        change_detection_score  : int
        ranking_score           : int
        explanation_score       : int | None (None = needs manual review)
        total_score             : int | None
        passed                  : bool | None (True if total >= STRONG_PERFORMANCE)
        app_findings            : list[dict]
        ground_truth            : list[dict]
    """
    case_name = os.path.basename(case_path)

    # TODO: load period1.xlsx, period2.xlsx, and ground_truth.json from case_path
    # Call run_analysis(file1, file2)
    # Score each dimension
    # Return results dict
    pass


# ---------------------------------------------------------------------------
# Full eval suite runner
# ---------------------------------------------------------------------------

def run_eval_suite(cases_dir: str = "eval_cases") -> pd.DataFrame:
    """
    Run all test cases found in cases_dir and return a summary DataFrame.

    Parameters
    ----------
    cases_dir : str
        Directory containing one subdirectory per test case.

    Returns
    -------
    pd.DataFrame with one row per test case and columns:
        case_name, change_detection, ranking, explanation, total, passed
    """
    # TODO: discover all subdirectories in cases_dir
    # Run run_test_case() for each
    # Aggregate into a DataFrame
    # Print summary stats (mean scores, pass rate)
    pass


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run evaluation suite for the Automated Metrics app."
    )
    parser.add_argument(
        "--case",
        type=str,
        default=None,
        help="Name of a single test case directory inside eval_cases/ to run.",
    )
    parser.add_argument(
        "--cases-dir",
        type=str,
        default="eval_cases",
        help="Path to the directory containing all test cases (default: eval_cases/).",
    )
    args = parser.parse_args()

    if args.case:
        case_path = os.path.join(args.cases_dir, args.case)
        result = run_test_case(case_path)
        print(json.dumps(result, indent=2))
    else:
        summary = run_eval_suite(args.cases_dir)
        if summary is not None:
            print(summary.to_string())
