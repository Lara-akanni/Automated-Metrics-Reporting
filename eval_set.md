# Evaluation Set — Automated Metrics Comparison and Reporting

This evaluation set contains representative test cases for the metrics comparison pipeline.
The user uploads two transaction-level Excel files from consecutive time periods; the system
should detect all meaningful changes, run statistical checks using its tools, and return
clear, business-relevant findings a stakeholder can act on.

Each case describes the input file pair, what was deliberately engineered into the data,
and what a good output should do.

---

## Eval 1 — Normal Case: Product Metrics (Weekly)

**Type:** Normal

**Input:**
Two weekly transaction-level payment logs (`product_metrics_wk_p1.xlsx` / `_p2.xlsx`).
~350 rows in Period 1, ~370 rows in Period 2.
Key columns: `transaction_id`, `date`, `amount`, `status` (Success / Failed), `satisfaction_score`.

**What was engineered:**
- Payment success rate dropped from ~92% to ~85% (engineered by flipping ~25 extra transactions to Failed)
- Average customer satisfaction score dropped from 4.3 to 3.7

**What a good output should do:**
- Detect the drop in payment success rate and quantify it (e.g., "success rate fell from 92.1% to 85.1%, a 7-point drop")
- Detect the drop in average satisfaction score and state both the old and new values
- Call `run_significance_test` on the satisfaction scores across both periods and report whether the drop is statistically significant
- Call `detect_outliers` on the amount or satisfaction series to flag any anomalous transactions
- Provide a business-relevant explanation — e.g., "a rise in failed payments may indicate a payment gateway issue or friction in the checkout flow"
- Return both findings as structured JSON with `is_significant` and `is_outlier` populated

---

## Eval 2 — Normal Case: Marketing Metrics (Weekly)

**Type:** Normal

**Input:**
Two weekly web session logs (`marketing_metrics_wk_p1.xlsx` / `_p2.xlsx`).
~520 rows in Period 1, ~680 rows in Period 2.
Key columns: `session_id`, `date`, `channel`, `page_views`, `session_duration`, `signed_up`, `converted`.

**What was engineered:**
- Total sessions increased ~31% (traffic spike)
- Conversion rate dropped from ~8% to ~4.5% (more visitors, fewer converting)
- Sign-up rate dropped from ~15% to ~10%

**What a good output should do:**
- Detect that session volume increased and frame it as a traffic spike
- Detect that conversion rate dropped despite the traffic increase — and explicitly connect these two facts in the explanation (the pattern is meaningful: volume up but quality down)
- Detect the sign-up rate drop as a separate finding
- Call `compute_percentage_change` to quantify each metric shift
- Not treat the session count increase as unambiguously positive — the explanation should note the conversion drop as a concern
- Return findings as structured JSON with appropriate `direction` values (increase for sessions, decrease for conversion/signup)

---

## Eval 3 — Normal Case: Revenue by Product Line (Month-on-Month)

**Type:** Normal

**Input:**
Two monthly payment transaction tables (`revenue_mom_p1.xlsx` / `_p2.xlsx`).
~480 rows in Period 1, ~398 rows in Period 2.
Key columns: `transaction_id`, `date`, `product_line` (A / B / C), `amount`, `status`.

**What was engineered:**
- Product Line C revenue dropped ~30% (engineered by removing rows and reducing amounts)
- Overall total revenue dropped as a result
- Product Lines A and B remain approximately stable

**What a good output should do:**
- Detect the overall revenue decline and quantify it
- Detect that the revenue drop is concentrated in Product Line C (not evenly distributed)
- Not flag Product Lines A or B as significant changes if they are stable
- Call `run_significance_test` on the amount values for each product line across periods, and flag Product Line C as significant
- Provide a business-relevant explanation — e.g., "the overall revenue decline is driven entirely by Product Line C, which warrants investigation into pricing, demand, or operational issues specific to that line"
- Return a finding for Product Line C specifically, not just a generic "revenue decreased" finding

---

## Eval 4 — Normal Case: Mixed Numeric and Categorical (Account-Level)

**Type:** Normal

**Input:**
Two account-level snapshots (`mixed_numeric_categorical_p1.xlsx` / `_p2.xlsx`).
80 rows in each period (one row per account, same accounts across both files).
Key columns: `account_name`, `status` (Active / Inactive), `monthly_volume`, `rate_pct`, `score`, `nps_score`.

**What was engineered:**
- 18 of 80 accounts flipped from Active → Inactive (22.5% of accounts churned)
- `monthly_volume` decreased for accounts that became Inactive
- `rate_pct` increased slightly across the board
- `nps_score` declined for the Inactive group

**What a good output should do:**
- Detect the categorical shift in `status` — specifically that Active accounts decreased from 80 to ~62 and flag the 18 accounts that became Inactive
- Detect changes in `monthly_volume`, `rate_pct`, and `nps_score` as numeric findings
- Call `compute_percentage_change` for each numeric metric
- Provide a business-relevant explanation for the status shift — e.g., "22% of accounts moved to Inactive, which may indicate churn risk or account closures that warrant follow-up"
- Not treat all accounts as identical — the finding should reflect that the numeric changes are linked to the status change (the accounts that went Inactive drove the volume decline)

---

## Eval 5 — Edge Case: Mismatched File Templates

**Type:** Edge case

**Input:**
Two Excel files that come from different reporting templates — they share fewer than 50% of column names (e.g., one file has `transaction_id, amount, status` and the other has `order_id, revenue, outcome, region`).

**What was engineered:**
Nothing — this case tests how the app handles incompatible inputs.

**What a good output should do:**
- Raise a clear, user-facing error before attempting any analysis
- State specifically that the column overlap is below the required threshold (50%)
- List which columns are present in each file so the user knows what is missing
- Not crash silently or return empty findings without explanation
- Not attempt to force-match semantically similar but differently named columns (e.g., `amount` ≠ `revenue` unless the user has confirmed they are equivalent)

---

## Eval 6 — Edge Case: Very Small Sample (Significance Testing Edge)

**Type:** Edge case

**Input:**
Two Excel files with only 5–8 rows each. All columns are shared.
A numeric change is present (e.g., mean amount dropped from 200 to 150).

**What was engineered:**
A real numeric change, but on an intentionally tiny dataset.

**What a good output should do:**
- Still detect and report the numeric change (mean / sum shift)
- Call `run_significance_test` — but correctly report that the result is **not statistically significant** due to the small sample, even if the raw difference looks large
- Set `is_significant: false` in the finding and explain why in plain language (e.g., "the sample is too small to draw reliable conclusions — at least 2 values are required per period for this test")
- Not overstate confidence in a change that cannot be statistically validated
- The `detect_outliers` tool should gracefully return no result (it requires ≥4 values) and the output should not crash or omit the finding entirely

---

## Eval 7 — Likely Failure Case: Subtle Change Buried in Noise

**Type:** Likely failure / requires human review

**Input:**
Two transaction-level files with a large number of rows (~500 each) and many numeric columns.
Only one column has a real engineered change — a 5% drop in a rate metric — and the rest of the data is stable with normal random variation.

**What was engineered:**
A single 5% drop in one rate metric. All other columns are unchanged (within random noise).

**What a good output should do:**
- Surface the 5% rate drop as a finding and flag it with `is_significant`
- Not flag stable columns as meaningful changes just because of random noise
- Use `run_significance_test` to distinguish the real change from noise — columns with no engineered change should come back as `is_significant: false`
- Not overwhelm the analyst with false positives

**Why this is a likely failure point:**
With many numeric columns and random variation, the model may call `compute_percentage_change` on every column and surface multiple small shifts as findings — even when those shifts are just noise. The significance test is the key tool here: only the one engineered change should cross the significance threshold. If the model skips the significance test or misinterprets the result, it will produce a noisy, hard-to-use output that buries the real finding.

---

## Eval 8 — Likely Failure Case: No Real Changes

**Type:** Likely failure / requires human review

**Input:**
Two transaction-level files generated from the same distribution — no changes were engineered. Any differences between periods are purely due to random sampling variation.

**What was engineered:**
Nothing.

**What a good output should do:**
- Return few or no findings, with `is_significant: false` on any minor numeric differences
- Not fabricate changes or overstate random variation as meaningful
- Ideally include a summary note that no significant changes were detected between the two periods
- Demonstrate that the pipeline does not produce findings just to have something to report

**Why this is a likely failure point:**
LLMs have a tendency to find patterns even when none exist. Without tool use, a prompt-only model would likely narrate small random differences as meaningful trends. This case directly tests whether the significance test acts as a gatekeeper — and whether the model respects the tool output when it says `is_significant: false`. It also serves as a direct comparison point for the baseline: the baseline is expected to fail this case (by surfacing false positives), while the main app should pass it.

---

## Eval 9 — Likely Failure Case: Inconsistent Categorical Formatting

**Type:** Likely failure / requires human review

**Input:**
Two Excel files where a categorical column contains the same values but with inconsistent casing across periods — for example, Period 1 has `"Active"` and `"Inactive"`, while Period 2 has `"active"` and `"INACTIVE"`.
No real status changes were engineered — the same accounts have the same status in both periods.

**What was engineered:**
Nothing — only formatting inconsistency.

**What a good output should do:**
- Normalise categorical values to lowercase before comparison so that `"Active"`, `"active"`, and `"ACTIVE"` are treated as the same value
- Not flag the formatting difference as a real categorical change
- Return no status-related findings (or note that values appear equivalent after normalisation)
- Demonstrate that the app does not produce false positives from formatting noise

**Why this is a likely failure point:**
A case-sensitive comparison would treat `"Active"` and `"active"` as different categories and report a shift in the status distribution — even though nothing actually changed. This would produce misleading findings and erode analyst trust in the output. The app's `compute_deltas()` function normalises categorical values to lowercase before comparing, but if that step is skipped or incomplete, this case will produce false positives. The baseline is especially likely to fail here since it has no normalisation step and the model receives raw summary statistics where the formatting difference may appear as a real distribution shift.
