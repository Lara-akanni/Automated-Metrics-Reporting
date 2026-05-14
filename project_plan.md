# Project Plan: Automated Metrics Comparison and Reporting

---

## Section 1: Project Title

**Automated Metrics Comparison and Reporting**

---

## Section 2: Target User, Workflow, and Business Value

### Target User
The primary user is a data analyst responsible for producing periodic performance reports that go to executives and, secondarily, to functional leads such as the marketing lead, product manager, or finance partner. This analyst regularly compares two datasets from consecutive time periods (weekly, monthly, or quarterly) to identify changes in metrics and communicate findings in a report format decision-makers can act on.

### Recurring Workflow
The workflow begins when the analyst receives or prepares two Excel files containing similar metric columns from two different time periods. The analyst uploads both files to the app. The app analyzes the data, identifies all numeric and categorical changes, ranks findings by impact, and generates a professional PDF report with a narrative that explains what changed and why it matters. The analyst then shares this PDF report with executives and the relevant functional lead for decision-making or awareness.

**Workflow Boundaries:** The workflow starts with two uploaded Excel files and ends with a downloadable, shareable PDF report.

### Business Value
Currently, this comparison process is manual and time-consuming. The analyst opens both files in Excel, computes deltas using formulas, visually scans for outliers using conditional formatting, decides what findings are most important based on personal judgment, and writes explanations from scratch in a separate document. This process takes hours per reporting cycle and is error-prone.

A better system saves significant time, reduces errors, ensures consistent report quality, and produces ranked insights that surface what stakeholders need to focus on. The impact is direct:

- Faster reporting cycles
- Fewer manual errors
- Consistent, professional report format every time
- Clearer communication of changes and their business significance

This workflow recurs across reporting cycles because the data analyst produces reports that feed executive reviews as well as functional leads in marketing, product, and finance. In a given cycle they may prepare a traffic and signups comparison for the marketing lead, a success-rate and satisfaction review for the product manager, and a revenue movement summary for finance, all of which ultimately roll up to executives. The app does not require the analyst to specify which stakeholder the report is for. It detects what is in the data and analyzes accordingly, so the analyst can run the same pipeline across different requests without reconfiguring it each time.

---

## Section 3: Problem Statement and GenAI Fit

### Exact Task
The app accepts two Excel files representing datasets from two different time periods, automatically aligns columns by name, detects all numeric and categorical changes, computes statistical significance and outlier flags, ranks all findings by impact magnitude, and generates a professional PDF report with a narrative explanation for each finding organized from most to least impactful.

### What Part of the Workflow Benefits from AI
Three specific parts of this workflow benefit from language models:

**1. Reasoning and Ranking:** The model reasons about which changes are most significant and in what order they should be presented. A 5% drop in a metric that is typically stable carries more weight than a 5% drop in a metric that fluctuates regularly. The LLM applies that kind of contextual reasoning to prioritize findings.

**2. Narrative Generation:** The model writes clear, business-friendly explanations for each finding. Instead of just displaying a number, the report communicates the story. For example: "Success rate dropped from 92% to 84% this week, the largest single-week decline observed in this dataset. This is statistically significant and may warrant further investigation."

**3. Tool Use for Computation:** The model calls backend functions to compute percentage changes, run statistical significance tests, and detect outliers using methods like interquartile range. This ensures the analysis is mathematically rigorous and auditable, not just based on the model's intuition.

### Why a Simpler Non-AI Tool Would Not Be Enough
A spreadsheet template or basic Python script can compute deltas and flag outliers, but it cannot:

- Rank findings intelligently by business impact rather than just magnitude
- Write a narrative explanation that communicates what a finding means and why it matters
- Handle varying column structures across different datasets without manual configuration
- Adapt its output to the context of the data it is analyzing

The combination of structured reasoning, narrative generation, and tool-assisted computation is what makes a language model the right fit for this workflow.

---

## Section 4: Planned System Design and Baseline

### System Architecture and Workflow
The app follows a clear multi-step pipeline:

1. The analyst uploads two Excel files through the app interface.
2. The app parses and loads both files, detects all columns, and aligns them by name. Columns that do not exist in both files are flagged separately.
3. For numeric columns, the app computes raw deltas (the difference between the two values). For categorical columns, the app flags any values that changed (for example, a status field that changed from "Active" to "Inactive").
4. The LLM calls backend functions to compute percentage changes, run statistical significance tests, and detect outliers. It uses these results to rank all findings by impact magnitude.
5. The LLM generates structured JSON output for each finding, including: metric name, previous value, current value, delta, direction (up or down), impact level (high, medium, or low), and a narrative explanation.
6. The app formats the ranked findings and explanations into a professional PDF report with the most impactful findings at the top.
7. The analyst downloads or shares the PDF directly with stakeholders.

### Two Course Concepts Integrated

#### Concept 1: Anatomy of an LLM Call (Structured Outputs)
The LLM is prompted to return all findings in strict JSON format rather than freeform prose. Each finding object includes: metric name, previous value, current value, delta, direction, impact level, and explanation. This structured output allows the app to programmatically sort findings by impact, build the PDF report consistently, and produce the same format regardless of the domain the data comes from. Without structured outputs, the app would not be able to reliably rank findings or assemble the PDF from LLM-generated content.

#### Concept 2: Tool Use and Function Calling
Rather than asking the LLM to compute statistical tests or detect outliers itself (which would be unreliable), the app gives the LLM access to backend functions it can call: `compute_percentage_change`, `detect_outliers` (using interquartile range), and `run_significance_test`. The LLM calls these functions during its analysis step and uses the results to inform its ranking and narrative. This keeps the math deterministic and auditable while the LLM focuses on reasoning and explanation.

### Simpler Baseline for Comparison
The simpler alternative being compared against is manual Excel-based analysis. The analyst opens both files, manually computes deltas using formulas, applies conditional formatting to spot outliers visually, decides on finding priority based on personal judgment, and writes the narrative explanation in a separate document. This is the current real-world workflow the app is designed to replace. Comparing the app's output against this manual baseline will show whether the app correctly identifies and prioritizes the same findings a skilled analyst would catch.

### What the App Looks Like
The analyst opens a simple web app built with Streamlit or equivalent. They are presented with two file upload areas labeled "Period 1" and "Period 2." After uploading both Excel files, they click a button to run the analysis. The app shows a loading state while it processes the files, runs the comparison, and calls the LLM. When ready, the app displays a preview of the top findings ranked by impact with a brief explanation for each. The analyst can then download the full PDF report, which is formatted and ready to share with stakeholders. No configuration is required. The app detects column types automatically and handles varying structures across different datasets.

---

## Section 5: Evaluation Plan

### What Success Looks Like
The app successfully identifies all major changes between the two datasets, ranks them correctly by impact or magnitude, flags real outliers, and generates explanations that are clear enough for a stakeholder to understand without needing to see the raw data. The report should read like something a skilled analyst would write, not like an automated summary.

### What Will Be Measured
Each test run will be scored on a rubric with three dimensions, each scored 1 to 3:

| Rubric Dimension | What It Measures | Scoring (1 to 3) |
|---|---|---|
| **Change Detection** | Did the app correctly identify all major numeric and categorical changes? | 1 = missed key changes, 2 = caught most, 3 = caught all |
| **Ranking Correctness** | Are the most impactful findings ranked at the top? | 1 = ranking is wrong, 2 = mostly correct, 3 = fully correct |
| **Explanation Quality** | Are the narrative explanations clear and business-relevant? | 1 = unclear or generic, 2 = acceptable, 3 = clear and specific |

Each test run is scored out of 9 points. A score of 7 or higher indicates strong performance.

### Test Set
The evaluation will use 8 to 12 synthetic mock Excel file pairs created specifically for testing. Each file pair is engineered with known changes built in (for example, success rate deliberately dropped by 12%, a status column deliberately changed from Active to Inactive for a subset of records, a revenue figure deliberately spiked). Because the changes are known ahead of time, scoring against ground truth is objective.

The test file pairs will span multiple real-world domains:
- Product metrics (success rate, customer satisfaction scores)
- Marketing metrics (website traffic, signups, conversion rates)
- Revenue and business performance metrics
- Mixed datasets with both numeric and categorical columns

In addition to the synthetic evaluation set, 2 to 3 manual spot checks will be run where the analyst analyzes the same file pair independently and compares their findings to the app's output. This provides qualitative insight into where the app excels or struggles in ways the rubric alone might not capture.

### Baseline Comparison
For each synthetic test case, the app's output will be compared against the known ground truth (the engineered changes). For the manual spot checks, the app's output will be compared to the analyst's own independent findings. The goal is to demonstrate that the app catches the same changes a skilled analyst would catch, ranks them correctly, and communicates them clearly.

---

## Section 6: Example Inputs and Failure Cases

### Example Inputs

**Example 1: Product Metrics (Week-over-Week)**
Two Excel files containing product performance data. Columns include success rate, error rate, customer satisfaction score, and number of active users. The current week shows a notable drop in success rate and a corresponding dip in satisfaction scores. The app should flag these as the top two findings and explain their relationship.

**Example 2: Marketing Metrics (Week-over-Week)**
Two Excel files containing website analytics. Columns include total visits, unique visitors, signups, bounce rate, and conversion rate. One week shows a spike in visits but a drop in conversions. The app should catch both changes, note the contrast, and rank the conversion drop higher because it has more direct business impact.

**Example 3: Revenue Metrics (Month-over-Month)**
Two Excel files containing revenue data broken down by product line. Most lines are stable but one shows a significant month-over-month decline. The app should identify this as the primary finding, flag it as a statistical outlier, and generate a clear explanation.

**Example 4: Mixed Dataset with Numeric and Categorical Changes**
Two Excel files where some columns are numeric (volume, rate, score) and some are categorical (status, region, tier). Several numeric metrics changed moderately and one status column changed from Active to Inactive for a subset of records. The app should surface both types of changes and explain them in the context of the broader dataset.

### Anticipated Failure Cases

**Failure Case 1: No Column Overlap**
The two uploaded Excel files have completely different column names with no overlap. The app cannot align any columns and has nothing meaningful to compare. The app should detect this condition, refuse to proceed, and return a clear message explaining that the files do not share comparable columns.

**Failure Case 2: No Changes Detected**
Both Excel files are identical or nearly identical. All numeric columns have zero or negligible deltas and no categorical values changed. The app should detect this and report that no significant changes were found, rather than fabricating findings that do not exist.

**Failure Case 3: Inconsistent Categorical Formatting**
A categorical column contains values that are semantically the same but formatted differently (for example, "active" vs "Active" vs "ACTIVE"). The app may not flag these as changes even though a case-sensitive comparison would treat them as different. This is a known edge case that will require case normalization handling.

---

## Section 7: Risks and Governance

### Where the System Could Fail
- If the two Excel files have very few columns in common, the comparison will be shallow and potentially misleading
- If numeric columns contain data entry errors or extreme values unrelated to actual performance changes, the app may flag false positives as significant findings
- If the LLM generates explanations that sound confident but miss domain-specific context (for example, a seasonal pattern that explains a drop), the narrative could mislead stakeholders
- If column alignment fails silently because two columns have similar but not identical names, the app may miss key comparisons without informing the user

### Where the System Should Not Be Trusted
The app should not be used as the sole basis for high-stakes business decisions without human review. The LLM's explanations are generated based on data patterns and do not incorporate business context, historical trends, or external factors. Stakeholders should always review the report critically rather than treating it as a definitive analysis.

Because these reports often reach executives, the analyst should review the ranked findings and narrative before sharing. The LLM can surface patterns but does not know about ongoing initiatives, seasonality, or external events that the analyst or executive audience would factor into a real decision.

The app should not be used with sensitive or confidential real-world data in its current prototype form, as no data security controls have been implemented yet.

### Controls and Refusal Rules
- The app will refuse to compare two files if column overlap is below 50%, returning a message asking the user to verify their uploads
- The app will return a clear message if no significant changes are detected, rather than generating a report with fabricated or trivial findings
- Categorical value comparisons will be case-normalized before comparison to reduce false positives from formatting differences

### Data, Privacy, and Cost Considerations
All testing and evaluation will use synthetic mock data only. No real business data, personally identifiable information, or confidential metrics will be used. No API keys or sensitive data will be committed to the repository.

API cost is a consideration if the app scales to large datasets or high-frequency use, since each comparison involves multiple LLM calls. For the scope of this project, free tier usage is expected to be sufficient. Model and provider selection will be finalized during implementation based on cost, latency, and output quality trade-offs.

---

## Section 8: Plan for the Week 6 Check-In

### What Will Be Running
By the Week 6 check-in, the following parts of the app will be functional:

- File upload and parsing for two Excel files
- Column detection and alignment by name, handling different column orders and missing columns
- Raw delta computation for numeric columns and categorical change flagging
- Basic LLM tool use for outlier detection and statistical flagging
- Structured JSON output from the LLM with ranked findings
- A basic PDF report generated from the structured output

The app interface will be functional enough to upload two files, run the analysis, and download a report. It will not yet be fully polished, but it will demonstrate the core pipeline end to end.

### What Evaluation Will Be in Place
By Week 6, the evaluation rubric will be fully defined (three dimensions, scored 1 to 3, out of 9 points total). At least 3 to 4 synthetic test cases will have been run through the app and scored against ground truth. Initial results will be available showing where the app performs well and where it struggles.

### Baseline Comparison
At least 1 to 2 manual spot checks will have been completed where the analyst analyzed the same file pair independently and compared their findings to the app's output. This will serve as the first real-world comparison against the manual baseline and will inform refinements before the final submission.
