# Test Findings Log

This file records manual observations from each test run of the Automated Metrics app.
Each entry covers one file pair, what the app returned, and a manual score against the eval rubric.

**Rubric reminder:**
- Change Detection (CD): 3 = caught all | 2 = caught most (≥75%) | 1 = missed key changes (<75%)
- Explanation Quality (EQ): 3 = clear and specific, stakeholder can act on it | 2 = acceptable but generic | 1 = unclear or missing context
- Pass = total score of 5 or higher out of 6

---

## Run 1 — Example 1: Product Metrics (Week-over-Week)

**Date:**
**File pair:** `sample_data/example1_product_metrics/`
**Engineered changes:** Payment success rate ↓ (~92% → ~85%) | Avg CSAT score ↓ (4.3 → 3.7)

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
*(What did the app do well? What did it miss or get wrong? Any surprising findings?)*

---

## Run 2 — Example 2: Marketing Metrics (Week-over-Week)

**Date:**
**File pair:** `sample_data/example2_marketing_metrics/`
**Engineered changes:** Session volume ↑ (traffic spike, 50 → 65 rows) | Signup rate ↓ (12% → 6%) | Conversion rate ↓ (8% → 4%)

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
