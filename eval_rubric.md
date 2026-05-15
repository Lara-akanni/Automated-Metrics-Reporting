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

| Dimension | App Score (1–3) | Baseline Score (1–3) | Notes |
|---|---|---|---|
| Change Detection | | | |
| Explanation Quality | | | |
| **Total** | **/6** | **/6** | |
| **Pass (5+)?** | Yes / No | Yes / No | |

---

## Test Case Index

| # | Case Name | Domain | Engineered Changes | Date Run | App Score | Baseline Score | App Pass? |
|---|---|---|---|---|---|---|---|
| 1 | `example1_product` | Product | Success rate ↓, CSAT ↓, response time ↑ | 2025-05-14 | 6/6 | 2/6 | ✅ Yes |
| 2 | `example2_marketing` | Marketing | Traffic ↑, conversion ↓, signup ↓ | 2025-05-15 | 6/6 | —/6 | ✅ Yes |
| 3 | `example3_revenue` | Revenue | Product Line C revenue ↓ ~30% | 2025-05-15 | 6/6 | —/6 | ✅ Yes |
| 4 | `example4_mixed` | Mixed | 8 accounts → Inactive, volume ↓, NPS ↓ | 2025-05-15 | 6/6 | —/6 | ✅ Yes |

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

| Metric | App | Prompt-only Baseline |
|---|---|---|
| Total test cases run | 4 | 1 (Example 1 only) |
| Average Change Detection score | 3.0 / 3 | 1.0 / 3 |
| Average Explanation Quality score | 3.0 / 3 | 1.0 / 3 |
| Average total score | 6.0 / 6 | 2.0 / 6 |
| Cases scoring 5+ (pass rate) | 4 / 4 | 0 / 1 |
