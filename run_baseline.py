"""
run_baseline.py
---------------
Terminal runner for the prompt-only baseline.

Runs baseline.py on a pair of Excel files and prints findings in a
readable format so they can be compared side-by-side with the main app.

Usage:
    python3 run_baseline.py <file1.xlsx> <file2.xlsx>

Examples:
    python3 run_baseline.py sample_data/example1_product_metrics/Product_week_apr28.xlsx \
                            sample_data/example1_product_metrics/Product_week_may05.xlsx

    python3 run_baseline.py sample_data/example2_marketing_metrics/Marketing_week_apr28.xlsx \
                            sample_data/example2_marketing_metrics/Marketing_week_may05.xlsx

    python3 run_baseline.py sample_data/example3_revenue_mom/Revenue_april_2025.xlsx \
                            sample_data/example3_revenue_mom/Revenue_may_2025.xlsx

    python3 run_baseline.py sample_data/example4_mixed/Mixed_april_2025.xlsx \
                            sample_data/example4_mixed/Mixed_may_2025.xlsx
"""

import sys
import os
from baseline import run_baseline

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SEP  = "─" * 68
SEP2 = "═" * 68


def print_findings(findings: list[dict]) -> None:
    if not findings:
        print("\n  No findings returned.")
        return

    for i, f in enumerate(findings, 1):
        metric    = f.get("metric_name",    "Unknown metric")
        prev      = f.get("previous_value", "—")
        curr      = f.get("current_value",  "—")
        direction = f.get("direction",      "—")
        explain   = f.get("explanation",    "")

        print(f"\n  Finding {i}: {metric}")
        print(f"  {SEP}")
        print(f"  Previous : {prev}")
        print(f"  Current  : {curr}")
        print(f"  Direction: {direction}")
        if explain:
            # Word-wrap explanation at 64 chars
            words = explain.split()
            line, lines = "", []
            for w in words:
                if len(line) + len(w) + 1 > 64:
                    lines.append(line)
                    line = w
                else:
                    line = f"{line} {w}".strip()
            if line:
                lines.append(line)
            print(f"  Insight  : {lines[0]}")
            for l in lines[1:]:
                print(f"             {l}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 3:
        print("\nUsage: python3 run_baseline.py <period1.xlsx> <period2.xlsx>")
        print("\nExample:")
        print("  python3 run_baseline.py "
              "sample_data/example1_product_metrics/Product_week_apr28.xlsx "
              "sample_data/example1_product_metrics/Product_week_may05.xlsx")
        sys.exit(1)

    file1_path = sys.argv[1]
    file2_path = sys.argv[2]

    for path in (file1_path, file2_path):
        if not os.path.exists(path):
            print(f"\nFile not found: {path}")
            sys.exit(1)

    p1_name = os.path.splitext(os.path.basename(file1_path))[0]
    p2_name = os.path.splitext(os.path.basename(file2_path))[0]

    print(f"\n{SEP2}")
    print("  BASELINE ANALYSIS  (prompt-only, no tools)")
    print(SEP2)
    print(f"  Previous : {p1_name}")
    print(f"  Current  : {p2_name}")
    print(SEP2)
    print("  Running baseline — this may take a moment...")

    with open(file1_path, "rb") as f1, open(file2_path, "rb") as f2:
        findings = run_baseline(f1, f2)

    print(f"\n  {len(findings)} finding(s) returned")
    print(SEP2)

    print_findings(findings)

    print(f"\n{SEP2}")
    print("  DONE — compare these findings with the main app output.")
    print("  Record both in test_findings.md under the Manual Spot Check section.")
    print(SEP2)


if __name__ == "__main__":
    main()
