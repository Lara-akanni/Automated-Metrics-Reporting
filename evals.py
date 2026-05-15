"""
evals.py
--------
Evaluation script for scoring app output against ground truth.

Rubric (each dimension scored 1–3, max 6 points):
  1. Change Detection    — did the app catch all major changes?
  2. Explanation Quality — are narratives clear and business-relevant? (manual)

A score of 5+ indicates strong performance.

Usage:
  python evals.py                          # run all test cases in eval_cases/
  python evals.py --case product_metrics_wk  # run a single named test case

Test case directory structure:
  eval_cases/
    example1_product/
      period1.xlsx
      period2.xlsx
      ground_truth.json
    example2_marketing/
      period1.xlsx
      period2.xlsx
      ground_truth.json
    example3_revenue/
      ...
    example4_mixed/
      ...

ground_truth.json format:
  {
    "case_name": "product_metrics_wk",
    "domain": "Product",
    "expected_changes": [
      {
        "metric": "success_rate",
        "direction": "decrease",
        "description": "Payment success rate dropped from ~92% to ~85%"
      },
      ...
    ]
  }
"""

import os
import re
import json
import argparse
import pandas as pd
from analysis import run_analysis
from baseline import run_baseline


# ---------------------------------------------------------------------------
# Scoring constants
# ---------------------------------------------------------------------------

MAX_SCORE_PER_DIMENSION = 3
NUM_DIMENSIONS          = 2
MAX_TOTAL_SCORE         = MAX_SCORE_PER_DIMENSION * NUM_DIMENSIONS  # 6
STRONG_PERFORMANCE      = 5

# Thresholds for Change Detection scoring
THRESHOLD_FULL  = 1.00   # 100% caught → 3
THRESHOLD_MOST  = 0.75   # ≥75%  caught → 2
                          # <75%          → 1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalise(text: str) -> str:
    """Lowercase and strip punctuation for loose keyword matching."""
    return re.sub(r"[^a-z0-9 ]", " ", text.lower())


def _finding_mentions_metric(finding: dict, metric_keyword: str) -> bool:
    """
    Return True if a finding dict references the given metric keyword.

    Checks both metric_name and explanation (if present) so the scorer
    is not fooled by different column-name conventions (e.g. 'success_rate'
    vs 'Payment Success Rate').
    """
    keyword = _normalise(metric_keyword)
    haystack = " ".join([
        _normalise(str(finding.get("metric_name", ""))),
        _normalise(str(finding.get("explanation",  ""))),
    ])
    # Check every word in the keyword against the haystack
    return all(word in haystack for word in keyword.split())


# ---------------------------------------------------------------------------
# Rubric scoring functions
# ---------------------------------------------------------------------------

def score_change_detection(
    findings: list[dict],
    expected_changes: list[dict],
) -> tuple[int, list[str], list[str]]:
    """
    Score dimension 1: Change Detection.

    For each expected change, check whether any finding in the output
    mentions that metric (loose keyword match on metric name + explanation).

    Scoring:
      3 — caught all expected changes   (recall = 100%)
      2 — caught most                   (recall ≥ 75%)
      1 — missed key changes            (recall < 75%)

    Parameters
    ----------
    findings         : list of finding dicts from run_analysis() or run_baseline()
    expected_changes : list of dicts from ground_truth.json, each with a "metric" key

    Returns
    -------
    (score, caught_list, missed_list)
      score       : int 1–3
      caught_list : metric keywords that were found in the output
      missed_list : metric keywords that were not found
    """
    if not expected_changes:
        return 3, [], []   # nothing to check → full marks

    caught = []
    missed = []

    for change in expected_changes:
        keyword = change.get("metric", "")
        found = any(_finding_mentions_metric(f, keyword) for f in findings)
        if found:
            caught.append(keyword)
        else:
            missed.append(keyword)

    if len(expected_changes) == 0:
        recall = 1.0
    else:
        recall = len(caught) / len(expected_changes)

    if recall >= THRESHOLD_FULL:
        score = 3
    elif recall >= THRESHOLD_MOST:
        score = 2
    else:
        score = 1

    return score, caught, missed


def score_explanation_quality(findings: list[dict], interactive: bool = False):
    """
    Score dimension 2: Explanation Quality.

    This dimension requires human review — the function either prompts
    an interactive reviewer (interactive=True) or returns None as a
    placeholder for manual completion later.

    Scoring:
      3 — clear and specific; a stakeholder could act on it without the raw data
      2 — acceptable; communicates the change but explanation is generic or vague
      1 — unclear, generic, or missing context

    Parameters
    ----------
    findings    : list of finding dicts with "explanation" keys
    interactive : if True, prints each explanation and prompts for a score

    Returns
    -------
    int (1–3) if interactive=True and reviewer enters a score,
    None otherwise (flagged for manual review).
    """
    if not interactive:
        return None   # placeholder — fill in manually after reviewing output

    print("\n" + "=" * 60)
    print("EXPLANATION QUALITY REVIEW")
    print("=" * 60)
    print("Read each explanation below and score the overall quality.")
    print("Ask: could a stakeholder act on this without seeing the raw data?\n")

    for i, finding in enumerate(findings, 1):
        metric = finding.get("metric_name", "unknown metric")
        explanation = finding.get("explanation", "(no explanation provided)")
        print(f"  Finding {i}: {metric}")
        print(f"  {explanation}")
        print()

    print("Rubric:")
    print("  3 = Clear and specific — stakeholder can act without raw data")
    print("  2 = Acceptable — communicates change but explanation is generic")
    print("  1 = Unclear or generic — missing context or misleading")

    while True:
        raw = input("\nYour score (1, 2, or 3): ").strip()
        if raw in ("1", "2", "3"):
            return int(raw)
        print("  Please enter 1, 2, or 3.")


# ---------------------------------------------------------------------------
# Single test case runner
# ---------------------------------------------------------------------------

def run_test_case(case_path: str, interactive: bool = False) -> dict:
    """
    Run both the main app and the baseline against a single test case.

    Parameters
    ----------
    case_path   : str  — path to the test case directory
    interactive : bool — if True, prompt reviewer for Explanation Quality scores

    Returns
    -------
    dict with full scoring results for both app and baseline (see below).
    """
    case_name = os.path.basename(case_path.rstrip("/"))

    # --- Load files ---
    p1_path = os.path.join(case_path, "period1.xlsx")
    p2_path = os.path.join(case_path, "period2.xlsx")
    gt_path = os.path.join(case_path, "ground_truth.json")

    for path in (p1_path, p2_path, gt_path):
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Missing file in test case '{case_name}': {path}"
            )

    with open(gt_path, "r") as f:
        ground_truth = json.load(f)

    expected_changes = ground_truth.get("expected_changes", [])

    # --- Run pipelines ---
    print(f"\n[{case_name}] Running main app...")
    with open(p1_path, "rb") as f1, open(p2_path, "rb") as f2:
        app_findings = run_analysis(f1, f2)

    print(f"[{case_name}] Running baseline...")
    with open(p1_path, "rb") as f1, open(p2_path, "rb") as f2:
        baseline_findings = run_baseline(f1, f2)

    # --- Score Change Detection ---
    app_cd_score, app_caught, app_missed = score_change_detection(
        app_findings, expected_changes
    )
    base_cd_score, base_caught, base_missed = score_change_detection(
        baseline_findings, expected_changes
    )

    # --- Score Explanation Quality (manual / interactive) ---
    print(f"\n[{case_name}] APP output — {len(app_findings)} findings")
    app_eq_score = score_explanation_quality(app_findings, interactive=interactive)

    print(f"\n[{case_name}] BASELINE output — {len(baseline_findings)} findings")
    base_eq_score = score_explanation_quality(baseline_findings, interactive=interactive)

    # --- Compute totals (None if explanation quality not yet scored) ---
    def _total(cd, eq):
        if eq is None:
            return None
        return cd + eq

    def _passed(total):
        if total is None:
            return None
        return total >= STRONG_PERFORMANCE

    app_total      = _total(app_cd_score, app_eq_score)
    baseline_total = _total(base_cd_score, base_eq_score)

    return {
        "case_name":   case_name,
        "domain":      ground_truth.get("domain", ""),
        # ---- App ----
        "app_change_detection_score":  app_cd_score,
        "app_explanation_score":       app_eq_score,
        "app_total_score":             app_total,
        "app_passed":                  _passed(app_total),
        "app_changes_caught":          app_caught,
        "app_changes_missed":          app_missed,
        "app_findings":                app_findings,
        # ---- Baseline ----
        "baseline_change_detection_score": base_cd_score,
        "baseline_explanation_score":      base_eq_score,
        "baseline_total_score":            baseline_total,
        "baseline_passed":                 _passed(baseline_total),
        "baseline_changes_caught":         base_caught,
        "baseline_changes_missed":         base_missed,
        "baseline_findings":               baseline_findings,
        # ---- Ground truth reference ----
        "expected_changes": expected_changes,
    }


# ---------------------------------------------------------------------------
# Full eval suite runner
# ---------------------------------------------------------------------------

def run_eval_suite(cases_dir: str = "eval_cases", interactive: bool = False) -> pd.DataFrame:
    """
    Run all test cases found in cases_dir and return a summary DataFrame.

    Each subdirectory inside cases_dir that contains period1.xlsx,
    period2.xlsx, and ground_truth.json is treated as a test case.

    Parameters
    ----------
    cases_dir   : str  — directory containing one subdirectory per test case
    interactive : bool — if True, prompt reviewer for Explanation Quality scores

    Returns
    -------
    pd.DataFrame with one row per test case.
    Also prints a formatted side-by-side summary to stdout.
    """
    if not os.path.isdir(cases_dir):
        print(f"No eval_cases directory found at '{cases_dir}'. Nothing to run.")
        return pd.DataFrame()

    # Discover valid test case directories
    case_dirs = sorted([
        os.path.join(cases_dir, d)
        for d in os.listdir(cases_dir)
        if os.path.isdir(os.path.join(cases_dir, d))
        and os.path.exists(os.path.join(cases_dir, d, "ground_truth.json"))
    ])

    if not case_dirs:
        print(f"No valid test cases found in '{cases_dir}'.")
        return pd.DataFrame()

    rows = []
    errors = []

    for case_path in case_dirs:
        try:
            result = run_test_case(case_path, interactive=interactive)
            rows.append({
                "case_name":                  result["case_name"],
                "domain":                     result["domain"],
                "app_change_detection":       result["app_change_detection_score"],
                "app_explanation":            result["app_explanation_score"],
                "app_total":                  result["app_total_score"],
                "app_passed":                 result["app_passed"],
                "baseline_change_detection":  result["baseline_change_detection_score"],
                "baseline_explanation":       result["baseline_explanation_score"],
                "baseline_total":             result["baseline_total_score"],
                "baseline_passed":            result["baseline_passed"],
            })
        except Exception as exc:
            errors.append((os.path.basename(case_path), str(exc)))
            print(f"  ERROR in '{os.path.basename(case_path)}': {exc}")

    if not rows:
        print("No test cases completed successfully.")
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # --- Print summary ---
    _print_summary(df, errors)

    return df


# ---------------------------------------------------------------------------
# Summary printer
# ---------------------------------------------------------------------------

def _print_summary(df: pd.DataFrame, errors: list = None) -> None:
    """Print a formatted side-by-side summary table to stdout."""

    sep = "-" * 72

    print("\n" + "=" * 72)
    print("  EVALUATION RESULTS SUMMARY")
    print("=" * 72)

    # Per-case table
    header = (
        f"{'Case':<30} "
        f"{'App CD':>6} {'App EQ':>6} {'App /6':>6} {'Pass?':>5}  "
        f"{'Base CD':>7} {'Base EQ':>7} {'Base /6':>7} {'Pass?':>5}"
    )
    print(header)
    print(sep)

    for _, row in df.iterrows():
        app_eq   = str(row["app_explanation"])   if row["app_explanation"]   is not None else "—"
        base_eq  = str(row["baseline_explanation"]) if row["baseline_explanation"] is not None else "—"
        app_tot  = str(row["app_total"])          if row["app_total"]          is not None else "—"
        base_tot = str(row["baseline_total"])     if row["baseline_total"]     is not None else "—"
        app_pass  = ("Yes" if row["app_passed"]      else "No") if row["app_passed"]      is not None else "—"
        base_pass = ("Yes" if row["baseline_passed"] else "No") if row["baseline_passed"] is not None else "—"

        print(
            f"{row['case_name']:<30} "
            f"{row['app_change_detection']:>6} {app_eq:>6} {app_tot:>6} {app_pass:>5}  "
            f"{row['baseline_change_detection']:>7} {base_eq:>7} {base_tot:>7} {base_pass:>5}"
        )

    print(sep)

    # Averages (only for numeric columns with data)
    numeric_cols = [
        "app_change_detection", "baseline_change_detection",
        "app_explanation",      "baseline_explanation",
        "app_total",            "baseline_total",
    ]
    avgs = {c: df[c].dropna().mean() for c in numeric_cols}

    app_eq_avg   = f"{avgs['app_explanation']:.1f}"   if avgs['app_explanation'] == avgs['app_explanation']   else "—"
    app_tot_avg  = f"{avgs['app_total']:.1f}"          if avgs['app_total'] == avgs['app_total']               else "—"
    base_eq_avg  = f"{avgs['baseline_explanation']:.1f}" if avgs['baseline_explanation'] == avgs['baseline_explanation'] else "—"
    base_tot_avg = f"{avgs['baseline_total']:.1f}"     if avgs['baseline_total'] == avgs['baseline_total']     else "—"

    print(
        f"{'AVERAGE':<30} "
        f"{avgs['app_change_detection']:>6.1f} {app_eq_avg:>6} {app_tot_avg:>6}  "
        f"  {avgs['baseline_change_detection']:>7.1f} {base_eq_avg:>7} {base_tot_avg:>7}"
    )

    print("\nCD = Change Detection (auto-scored)   EQ = Explanation Quality (manual)")
    print("— means Explanation Quality has not yet been scored manually.")
    print(f"Pass threshold = {STRONG_PERFORMANCE}+ out of {MAX_TOTAL_SCORE}")

    if errors:
        print(f"\n{len(errors)} case(s) failed with errors:")
        for name, msg in errors:
            print(f"  {name}: {msg}")

    print("=" * 72)


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
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Prompt for Explanation Quality scores during the run.",
    )
    args = parser.parse_args()

    if args.case:
        case_path = os.path.join(args.cases_dir, args.case)
        result = run_test_case(case_path, interactive=args.interactive)
        # Print a readable single-case summary
        print("\n" + "=" * 50)
        print(f"  RESULTS: {result['case_name']}")
        print("=" * 50)
        print(f"  Expected changes : {[c['metric'] for c in result['expected_changes']]}")
        print(f"  App caught       : {result['app_changes_caught']}")
        print(f"  App missed       : {result['app_changes_missed']}")
        print(f"  App CD score     : {result['app_change_detection_score']} / 3")
        print(f"  App EQ score     : {result['app_explanation_score'] or '(manual review needed)'}")
        print(f"  Baseline caught  : {result['baseline_changes_caught']}")
        print(f"  Baseline missed  : {result['baseline_changes_missed']}")
        print(f"  Baseline CD score: {result['baseline_change_detection_score']} / 3")
        print(f"  Baseline EQ score: {result['baseline_explanation_score'] or '(manual review needed)'}")
    else:
        summary_df = run_eval_suite(args.cases_dir, interactive=args.interactive)
