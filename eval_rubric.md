# Evaluation Rubric

Each test run is scored across **two dimensions**, each rated **1–3**, for a maximum of **6 points**.
A score of **5 or higher** indicates strong performance.

---

## Dimensions

### 1. Change Detection
**Question:** Did the app correctly identify all major numeric and categorical changes?

| Score | Meaning |
|---|---|
| 3 | Caught all expected changes |
| 2 | Caught most expected changes (≥ 75%) |
| 1 | Missed key changes (< 75% caught) |

**How to score:**
- List all changes engineered into the test case (from `ground_truth.json`)
- Check each one against the app's output
- Count how many were surfaced as findings
- Apply the threshold above

---

### 2. Explanation Quality
**Question:** Are the narrative explanations clear and business-relevant?

| Score | Meaning |
|---|---|
| 3 | Clear and specific — a stakeholder could act on it without seeing raw data |
| 2 | Acceptable — communicates the change but explanation is generic or vague |
| 1 | Unclear or generic — could apply to any finding; misleading or missing context |

**How to score:**
- Read each explanation in the app's output
- Ask: *"Could an executive understand this finding and its significance without opening the Excel file?"*
- This dimension requires **manual human review** — it cannot be fully automated

---

## Scoring Sheet (per test case)

| Dimension | Score (1–3) | Notes |
|---|---|---|
| Change Detection | | |
| Explanation Quality | | |
| **Total** | **/6** | |
| **Pass (5+)?** | Yes / No | |

---

## Test Case Index

| # | Case Name | Domain | Engineered Changes | Date Run | Total Score | Pass? |
|---|---|---|---|---|---|---|
| 1 | `product_metrics_wk` | Product | Success rate ↓, satisfaction ↓ | | | |
| 2 | `marketing_metrics_wk` | Marketing | Traffic ↑, conversion ↓ | | | |
| 3 | `revenue_mom` | Revenue | One product line significant ↓ | | | |
| 4 | `mixed_numeric_categorical` | Mixed | Numeric changes + status → Inactive | | | |
| 5 | *(add more as created)* | | | | | |

---

## Manual Spot Checks

In addition to synthetic test cases, 2–3 manual spot checks are run where the analyst independently
analyses the same file pair and compares their findings to the app's output.

| # | File Pair Used | Analyst Findings Summary | App Findings Summary | Match? | Notes |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

---

## Aggregate Results Summary

> **[TO BE COMPLETED AFTER TESTING]**

| Metric | Value |
|---|---|
| Total test cases run | |
| Average Change Detection score | / 3 |
| Average Explanation Quality score | / 3 |
| Average total score | / 6 |
| Cases scoring 5+ (pass rate) | / |
