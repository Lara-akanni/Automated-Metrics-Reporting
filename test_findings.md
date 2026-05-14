# Test Findings Log

This file records manual observations from each test run of the Automated Metrics app.
Each entry covers one file pair, what the app returned, and a manual score against the eval rubric.

**Rubric reminder:**
- Change Detection (CD): 3 = caught all | 2 = caught most (≥75%) | 1 = missed key changes (<75%)
- Explanation Quality (EQ): 3 = clear and specific, stakeholder can act on it | 2 = acceptable but generic | 1 = unclear or missing context
- Pass = total score of 5 or higher out of 6

---

## Run 1 — Example 1: Product Metrics (Week-over-Week)

**Date:** 2025-05-14
**File pair:** `sample_data/example1_product_metrics/`
**Engineered changes:** Payment success rate ↓ (~92% → ~85%) | Avg CSAT score ↓ (4.3 → 3.7)

### App Findings

18 findings returned in total. Useful findings included:

| # | Metric Name | Period 1 | Period 2 | Direction | Outlier? | Significant? |
|---|---|---|---|---|---|---|
| ✓ | amount_usd | — | — | Detected | ⚠️ | ⚠️ |
| ✓ | csat_score | — | — | Detected | ⚠️ | ⚠️ |
| ✓ | response_time_ms | — | — | Detected | ⚠️ | ⚠️ |
| ✓ | status — Failed | — | — | Detected | ⚠️ | ⚠️ |
| ✓ | status — Success | — | — | Detected | ⚠️ | ⚠️ |
| ✗ | date (per-date) | — | — | Not useful — 13 extra date-by-date findings added noise | | |

**Sample explanation from app:**
> "The percentage of events on 2025-05-03 decreased by 12.0 percentage points from Period 1 to Period 2. This is a significant shift in event distribution."

### Scoring

| Dimension | Score (1–3) | Notes |
|---|---|---|
| Change Detection | 3 | Caught all engineered changes (status, CSAT, amount) but also returned 13 noisy per-date findings |
| Explanation Quality | 1 | Not usable for a stakeholder — references "Period 1/Period 2" instead of actual week names; uses absolute differences instead of percentages; LLM makes significance judgments instead of leaving that to the analyst |
| **Total** | **4/6** | |
| **Pass (5+)?** | **No** | |

### Observations

**What worked:**
- Correctly detected success/failure rate shift, CSAT drop, amount_usd changes, and response time
- Correctly identified direction (increase/decrease) for all real findings

**Issues identified (all fixed before retest):**
1. **Date column treated as categorical** — produced 13 per-date breakdown findings. Fixed by skipping date/ID/name columns in `compute_deltas()`.
2. **Absolute differences instead of percentages** — Fixed by updating the system prompt to require % symbol on all numeric changes.
3. **Period 1 / Period 2 labels** — Fixed by passing file names to the LLM and instructing it to use them in explanations.
4. **LLM making significance judgments** — Fixed by removing opinion language from the prompt.
5. **All findings showed ⚠️ and 🔺 badges** — Fixed by instructing the model to only set flags based on tool results.
6. **% symbol missing** — Fixed alongside issue 2.

---

### Retest — After Fixes (2025-05-14)

**Changes made:** All 6 issues above addressed in `analysis.py` (prompt rewrite, metadata column skip) and `app.py` (file name passing).

| Dimension | Score (1–3) | Notes |
|---|---|---|
| Change Detection | 3 | 5 findings returned — all relevant (status, CSAT, amount, response time). No date noise. |
| Explanation Quality | 3 | Specific and usable — changes expressed as percentages with % symbol, actual week names referenced, badges more selective |
| **Total** | **6/6** | |
| **Pass (5+)?** | **Yes** | |

**Improvements confirmed:**
- Date column noise eliminated — down from 18 findings to 5 clean findings ✅
- Changes now shown as percentages with % symbol ✅
- ⚠️ Significant and 🔺 Outlier badges more selective — not everything flagged ✅
- Explanations reference actual period names (week names) not "Period 1/Period 2" ✅
- LLM no longer makes its own significance judgments ✅

---

## Run 2 — Example 2: Marketing Metrics (Week-over-Week)

**Date:**
**File pair:** `sample_data/example2_marketing_metrics/`
**Engineered changes:** Session volume ↑ (traffic spike, 50 → 65 rows) | Signup rate ↓ (12% → 6%) | Conversion rate ↓ (8% → 4%)

**Date:** 2025-05-14

### App Findings
*(To be completed — findings noted, full log pending)*

### PDF Report Issues Identified
1. **Content cut at edges** — table overflows page width; margins too narrow
2. **Incomplete content** — findings cut off; page too small for all rows
3. **No page numbers** — PDF should be numbered
4. **Insight not domain-aware** — explanations are generic rather than framed in marketing context (e.g. should reference traffic, signups, conversion in marketing terms)

*All issues above to be fixed in `report.py` and `report.md` before scoring.*

### Observations
PDF layout needs fixing before this run can be properly scored. App findings and scoring to be completed after PDF fixes are applied.

---

## Run 3 — Example 3: Revenue Month-over-Month

**Date:**
**File pair:** `sample_data/example3_revenue_mom/`
**Engineered changes:** Product Line C revenue ↓ ~30% (fewer transactions + lower amounts) | Lines A and B stable

### App Findings
*(Paste or summarise what the app returned here)*

| # | Metric Name | Period 1 | Period 2 | Direction | Outlier? | Significant? |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |

**Explanations (copy from app):**
>

### Scoring

| Dimension | Score (1–3) | Notes |
|---|---|---|
| Change Detection | | |
| Explanation Quality | | |
| **Total** | **/6** | |
| **Pass (5+)?** | | |

### Observations

---

## Run 4 — Example 4: Mixed Numeric and Categorical

**Date:**
**File pair:** `sample_data/example4_mixed/`
**Engineered changes:** 8 of 40 accounts flipped Active → Inactive | Volume ↓ for inactive accounts | NPS score ↓

### App Findings
*(Paste or summarise what the app returned here)*

| # | Metric Name | Period 1 | Period 2 | Direction | Outlier? | Significant? |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |

**Explanations (copy from app):**
>

### Scoring

| Dimension | Score (1–3) | Notes |
|---|---|---|
| Change Detection | | |
| Explanation Quality | | |
| **Total** | **/6** | |
| **Pass (5+)?** | | |

### Observations

---

## Aggregate Summary
*(Fill in after all 4 runs are complete)*

| Test Case | CD Score | EQ Score | Total | Pass? |
|---|---|---|---|---|
| Example 1 — Product | | | /6 | |
| Example 2 — Marketing | | | /6 | |
| Example 3 — Revenue | | | /6 | |
| Example 4 — Mixed | | | /6 | |
| **Average** | | | /6 | |

**Overall observations:**
*(What patterns did you notice across all four runs? Where did the app consistently do well or struggle?)*

---

## Manual Spot Check Notes
*(Optional — record any additional observations from running the app on your own data or re-running the same files independently as an analyst)*

| # | File Pair | Your Independent Findings | App Findings | Match? | Notes |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
