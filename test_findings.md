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

**Date:** 2025-05-15
**File pair:** `sample_data/example2_marketing_metrics/`
**Engineered changes:** Session volume ↑ (traffic spike, 50 → 65 rows) | Signup rate ↓ (12% → 6%) | Conversion rate ↓ (8% → 4%)

### App Findings

9 findings returned. Notable findings:

| # | Metric Name | Previous | Current | Change | Notes |
|---|---|---|---|---|---|
| ✓ | Signup volume | 5 | 3 | -40% | Plausible given engineered rate drop |
| ✓ | Conversion volume | 5 | 0 | -100% | Caught but value needs verification — expected ~2, not 0 |
| ? | Session volume ↑ | — | — | — | Unclear if traffic spike was explicitly surfaced |

### PDF Report
All layout issues from initial test resolved after `report.py` rewrite:
- ✅ No edge clipping
- ✅ Page numbers showing
- ✅ All content visible
- ⚠️ Explanations not framed in marketing terms — stated direction only, no domain language (e.g. "traffic", "signups", "conversion rate"). Domain-aware prompt fix pushed after this run — retest needed.

### Scoring

| Dimension | Score (1–3) | Notes |
|---|---|---|
| Change Detection | 2 | Caught signup and conversion drops but session volume spike unclear; some findings may be noise |
| Explanation Quality | 2 | Correct direction but generic — not framed in marketing context; no domain language |
| **Total** | **4/6** | |
| **Pass (5+)?** | **No** | |

### Observations

**What worked:**
- PDF layout fully fixed — clean, numbered, no overflow ✅
- Signup and conversion rate drops detected ✅

**Issues to address:**
1. **Domain language missing** — explanations should reference traffic, signups, conversion in marketing terms. Domain-aware prompt fix already pushed; retest needed.
2. **Conversion volume showing 0** — verify against sample data whether 0 conversions in Period 2 is accurate or a data issue.
3. **Session volume spike** — confirm whether the traffic increase (50→65 rows) was explicitly surfaced as a finding.

---

## Run 3 — Example 3: Revenue Month-over-Month

**Date:** 2025-05-15
**File pair:** `sample_data/example3_revenue_mom/`
**Engineered changes:** Product Line C revenue ↓ ~30% (fewer transactions + lower amounts) | Lines A and B stable

### App Findings

5 findings returned. Detected changes:
- ✅ Completed status distribution — detected
- ✅ Refunded status distribution — detected
- ✅ Product lines distribution — detected (Line C drop visible)
- ⚠️ Revenue amounts — detected but currency symbol missing from insights (e.g. should say "$" or "USD")
- ⚠️ Outlier flagged in Revenue April — but explanation did not describe what the outlier value was

### Issues Identified (to fix before retest)

1. **Currency missing from insights** — when revenue/amount metrics are detected, the explanation should reference the currency (e.g. "$" or "USD") not just the raw number
2. **Outlier description too vague** — stated "outliers were detected in Revenue April" without specifying what the outlier value was. Should describe the unusual value (e.g. "an unusually high revenue of $X was detected")
3. **"percentage points" in insights** — categorical changes described as "decreased by X percentage points" instead of using the % symbol. All changes should use % symbol consistently

### PDF
Layout clean and complete ✅. Same wording issues as insights (percentage points, no currency).

### Scoring (pre-fix — pending retest)

| Dimension | Score (1–3) | Notes |
|---|---|---|
| Change Detection | 3 | All engineered changes surfaced — Product Line C drop, status distributions, revenue |
| Explanation Quality | 2 | Correct findings but currency missing, outlier details vague, "percentage points" wording |
| **Total** | **5/6** | |
| **Pass (5+)?** | **Yes (borderline)** | |

### Retest — After Fixes (2025-05-15)

**Changes made:** Currency symbols in insights, outlier value descriptions, "percentage points" → "%" fixed in `analysis.py`. Dollar sign LaTeX rendering fixed in `app.py`.

| Dimension | Score (1–3) | Notes |
|---|---|---|
| Change Detection | 3 | 4 findings returned — all engineered changes covered ✅ |
| Explanation Quality | 3 | Currency shown correctly, outlier values described specifically, % symbol used throughout |
| **Total** | **6/6** | |
| **Pass (5+)?** | **Yes** | |

**Improvements confirmed:**
- Currency symbols displaying correctly in app and PDF ✅
- Outlier explanation now specifies the unusual value ✅
- "Percentage points" replaced with "%" throughout ✅
- 4 findings (down from 5) — clean, no noise ✅

---

## Run 4 — Example 4: Mixed Numeric and Categorical

**Date:** 2025-05-15
**File pair:** `sample_data/example4_mixed/`
**Engineered changes:** 8 of 40 accounts flipped Active → Inactive | Volume ↓ for inactive accounts | NPS score ↓

### Initial Run Issues (pre-fix)

1. **Account status shown as percentages** — Active/Inactive reported as share (%) instead of actual counts (e.g. "32 Active, 8 Inactive"). Counts are more meaningful for stakeholders tracking account numbers.
2. **"Score" in insight instead of full name** — explanation used generic "score" instead of the exact column name (e.g. "nps_score"). Fixed by instructing LLM to always use exact column names.
3. **NPS values incorrect** — showing 46.525 → 41.425 (raw numeric mean/sum), not proper NPS calculation. NPS responses (0–10 scale) should be bucketed into Promoters (9–10), Passives (7–8), Detractors (0–6), and NPS score = (Promoters% − Detractors%) × 100.

### Fixes Applied
- `compute_deltas()`: NPS detection added — if column name contains "nps" and values are 0–10, automatically bucket into Promoters/Passives/Detractors and compute NPS score
- System prompt: status-type categoricals report counts not just percentages
- System prompt: always use exact column name in metric_name and explanations
- System prompt: for score/rating/nps columns use mean not sum

### Scoring (pending retest)

| Dimension | Score (1–3) | Notes |
|---|---|---|
| Change Detection | — | Pending retest |
| Explanation Quality | — | Pending retest |
| **Total** | **—/6** | |
| **Pass (5+)?** | **Pending** | |

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

---

## Baseline Comparison — prompt-only, no tools

**Run on:** Example 1 — Product Metrics (Week-over-Week)
**File pair:** `Product_week_apr28.xlsx` vs `Product_week_may05.xlsx`
**Date:** 2025-05-15
**How run:** `python3 run_baseline.py` in terminal

### Baseline vs App — Side by Side

| Dimension | Baseline (prompt-only) | App (tool use + JSON) |
|---|---|---|
| Findings returned | 90 | 5 |
| Previous / Current values | "unknown" for all | Actual values with % changes |
| Output format | Markdown fragments as findings | Clean structured rows |
| Change Detection score | 1 | 3 |
| Explanation Quality score | 1 | 3 |
| **Total** | **2/6** | **6/6** |
| **Pass (5+)?** | **No** | **Yes** |

### What the baseline output showed
- The model returned 90 "findings" — each bullet point of its markdown prose response was parsed as a separate finding
- `Previous` and `Current` fields were "unknown" across all findings — no structured values extracted
- Markdown syntax bled through: `**Old Value (Period 1):**`, `*1. Metric*` appeared as finding titles
- No percentage changes, no outlier flags, no significance flags
- Findings were unactionable — a stakeholder could not use this output

### Conclusion
Same model, same data — without tool use and structured JSON output, the output is unusable. Tool use keeps math in code (reliable) and language with the LLM (readable). Structured JSON makes every response parseable and drives both the UI and PDF directly.

*Note: Baseline run on Example 1 only. The failure pattern (fragmented output, no structured values) is expected to be consistent across all examples — one run is sufficient to demonstrate the contrast.*
