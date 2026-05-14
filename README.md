# Automated Metrics Comparison and Reporting

> A GenAI-powered app that compares two Excel datasets across time periods, detects all changes, and generates a narrative-driven PDF report for analyst review — replacing a hours-long manual workflow.

---

## Table of Contents
- [Setup and Usage](#setup-and-usage)
- [Context, User, and Problem](#context-user-and-problem)
- [Solution and Design](#solution-and-design)
- [Evaluation and Results](#evaluation-and-results)
- [Artifact Snapshot](#artifact-snapshot)

---

## Setup and Usage

### Prerequisites
- Python 3.9 or higher
- A [Google Gemini API key](https://aistudio.google.com/app/apikey) — the app uses Gemini for analysis and narrative generation

---

### 1. Clone the Repository

```bash
git clone https://github.com/Lara-akanni/Automated-Metrics-Reporting.git
cd Automated-Metrics-Reporting
```

---

### 2. Create and Activate a Virtual Environment

```bash
# Create the environment
python -m venv venv

# Activate it — Mac/Linux
source venv/bin/activate

# Activate it — Windows
venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The key packages used by this project are:

| Package | Purpose |
|---|---|
| `streamlit` | Web app interface |
| `pandas` | Excel file parsing and delta computation |
| `openpyxl` | Reading `.xlsx` files |
| `google-genai` | Gemini API client (LLM + tool use) |
| `reportlab` | PDF report generation |
| `scipy` | Statistical significance testing |

---

### 4. Set Your API Key

This app requires a **Google Gemini API key**. Get one for free at [Google AI Studio](https://aistudio.google.com/app/apikey).

**Step 1 — Copy the example file:**
```bash
cp .env.example .env
```

**Step 2 — Open `.env` and replace the placeholder with your real key:**
```
GEMINI_API_KEY=your_actual_key_here
```

> ⚠️ `.env` is listed in `.gitignore` and will never be committed to the repository. Never share or publish this file — it contains your private API key. The `.env.example` file shows the required format but does not contain a real key.

---

### 5. Run the App

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

### 6. Try It with the Sample Files

Sample Excel file pairs are included in the `sample_data/` folder so you can run the app immediately without preparing your own data:

```
sample_data/
  example1_product_metrics/
    period1_week_apr28.xlsx   ← baseline period
    period2_week_may05.xlsx   ← comparison period
  example2_marketing_metrics/
  example3_revenue_mom/
  example4_mixed/
```

**Steps (using Example 1 — Product Metrics):**
1. In the app, click **Browse files** under **Period 1** and upload `period1_week_apr28.xlsx`
2. Click **Browse files** under **Period 2** and upload `period2_week_may05.xlsx`
3. Click **▶ Run Analysis**
4. Review the findings displayed on screen — each finding shows Period 1 vs Period 2 values, the change direction, statistical significance, and a plain-English explanation

Example 1 contains product payment data with a deliberate success rate drop and satisfaction score dip — upload both files to verify the app detects them correctly.

---

### Project Structure

```
Automated-Metrics-Reporting/
├── app.py                  # Streamlit app entry point
├── analysis.py             # Parse → align → delta → LLM tool loop
├── baseline.py             # Prompt-only baseline (no tools) for comparison
├── tools.py                # Backend math functions called by the LLM
├── report.py               # PDF generation from structured findings
├── evals.py                # Automated scoring against ground truth
├── requirements.txt        # Python dependencies
├── .env.example            # API key template — copy to .env and fill in
├── eval_set.md             # Human-readable evaluation test cases
├── eval_rubric.md          # Scoring rubric (2 dimensions, max 6 points)
├── project_plan.md         # Full project plan and design decisions
├── create_sample_data.py   # Script to regenerate synthetic Excel test files
├── eval_cases/             # Ground truth JSON files for automated eval
└── sample_data/            # Synthetic Excel file pairs for testing
    ├── example1_product_metrics/
    ├── example2_marketing_metrics/
    ├── example3_revenue_mom/
    └── example4_mixed/
```

---

## Context, User, and Problem

### Who the User Is
The primary user is a **data analyst** responsible for producing periodic performance reports (weekly, monthly, or quarterly) for executives and functional leads — including marketing, product, and finance stakeholders.

### The Workflow Being Improved
Each reporting cycle, the analyst receives two Excel files representing the same set of metrics from two consecutive time periods. The current manual workflow looks like this:

1. Open both Excel files side by side
2. Write delta formulas to compute the difference for each metric
3. Apply conditional formatting to visually scan for outliers
4. Decide which findings are most important based on personal judgment
5. Write narrative explanations from scratch in a separate document
6. Assemble everything into a shareable report

This process is repeated across multiple report types in a single cycle — traffic and signups for marketing, success rates for product, revenue breakdowns for finance — each requiring the same manual effort.

### Why It Matters
The manual process has three core problems:

| Problem | Impact |
|---|---|
| **Time-consuming** | Hours per reporting cycle, multiplied across report types |
| **Error-prone** | Manual delta formulas and subjective outlier spotting introduce mistakes |
| **Inconsistent** | Report quality and depth depend on the analyst's bandwidth and judgment that day |

A better system saves time, reduces errors, standardises report quality, and surfaces the most important findings automatically — so the analyst can focus on review and decision-making rather than data wrangling.

---

## Solution and Design

### What Was Built
A web app (built with **Streamlit**) where the analyst uploads two Excel files and receives a downloadable PDF report. No manual configuration is required — the app detects column types and dataset structure automatically.

### How It Works

```
[Upload Period 1 Excel] + [Upload Period 2 Excel]
            │
            ▼
  Parse files → Align columns by name
  Flag columns that exist in only one file
            │
            ▼
  Numeric columns  →  Compute raw deltas
  Categorical columns  →  Flag value changes
            │
            ▼
  LLM calls backend tools:
    • compute_percentage_change()
    • detect_outliers()          ← interquartile range method
    • run_significance_test()
            │
            ▼
  LLM returns structured JSON findings
  (each finding: metric, prev value, curr value, delta,
   direction, outlier flag, significance flag, narrative explanation)
            │
            ▼
  App formats all findings into PDF report
            │
            ▼
  [Analyst reviews findings and decides what matters most]
  [Analyst downloads and shares PDF with stakeholders]
```

### Key Design Choices

**1. Structured Outputs (JSON)**
The LLM is prompted to return all findings as strict JSON rather than freeform prose. Each finding object includes: `metric_name`, `previous_value`, `current_value`, `delta`, `direction`, `is_outlier`, `is_significant`, and `explanation`. This ensures a consistent, machine-readable format that assembles reliably into a PDF regardless of the dataset domain.

**2. Tool Use / Function Calling**
Rather than asking the LLM to compute statistics itself (which would be unreliable), the LLM is given access to three backend functions it calls during analysis. This keeps the maths deterministic and auditable while letting the LLM focus on explanation.

**3. Analyst-led prioritisation**
The app does not attempt to rank or prioritise findings by business importance — that judgment requires domain context the LLM does not have. Instead, all detected changes are surfaced and clearly explained, leaving prioritisation to the analyst who knows their stakeholders.

**4. No-configuration Design**
The analyst does not need to specify column types, stakeholder audience, or domain. The app infers all of this from the data. This means the same pipeline works for a marketing report and a revenue report without reconfiguration.

**5. Built-in Guardrails**
- Refuses to run if column overlap between the two files is below 50%
- Returns a clear "no significant changes found" message instead of fabricating findings
- Normalises categorical values to lowercase before comparison to avoid false positives from formatting differences (e.g. `"active"` vs `"Active"` vs `"ACTIVE"`)

---

## Evaluation and Results

### Baseline Being Compared Against
The baseline is the **manual Excel workflow** described above. For each test case, the analyst independently analyzes the same file pair and records their findings. The app's output is then compared against that ground truth.

### Evaluation Rubric
Each test run is scored on two dimensions, each rated 1–3, for a maximum of **6 points**. A score of **5 or higher** indicates strong performance.

| Dimension | What It Measures | 1 | 2 | 3 |
|---|---|---|---|---|
| **Change Detection** | Did the app correctly identify all major numeric and categorical changes? | Missed key changes | Caught most | Caught all |
| **Explanation Quality** | Are the narrative explanations clear and business-relevant? | Unclear or generic | Acceptable | Clear and specific |

### Test Cases
The evaluation uses **8–12 synthetic Excel file pairs** with engineered, known changes — making scoring against ground truth fully objective. Test cases span:
- Product metrics (success rate, error rate, customer satisfaction)
- Marketing metrics (traffic, signups, bounce rate, conversion rate)
- Revenue and business performance metrics
- Mixed datasets with both numeric and categorical columns

In addition, **2–3 manual spot checks** are run where the analyst analyzes the same file pair independently and compares findings to the app's output.

---

### Results

> **[TO BE COMPLETED AFTER TESTING]**

```
┌─────────────────────────────────────────────────────────────────┐
│  RESULTS TEMPLATE — update this section after running test cases │
│                                                                   │
│  Overall score summary                                            │
│  ─────────────────────                                            │
│  Test cases run:        [ X ] of 8–12                            │
│  Average total score:   [ X.X ] / 6                              │
│  Cases scoring 5+:      [ X ] / [ X ]                            │
│                                                                   │
│  Per-dimension averages                                           │
│  ──────────────────────                                           │
│  Change Detection:      [ X.X ] / 3                              │
│  Explanation Quality:   [ X.X ] / 3                              │
│                                                                   │
│  Key findings                                                     │
│  ────────────                                                     │
│  • What the app did well:    [ describe ]                         │
│  • Where it struggled:       [ describe ]                         │
│  • Manual spot check notes:  [ describe ]                         │
│                                                                   │
│  Comparison to baseline                                           │
│  ──────────────────────                                           │
│  [ Describe how the app's findings compared to the analyst's     │
│    independent findings for the same file pairs ]                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Artifact Snapshot

> **[TO BE COMPLETED — add screenshots, sample files, and/or a recorded clip]**

### App Interface

```
┌──────────────────────────────────────────────────────┐
│  SCREENSHOT PLACEHOLDER                               │
│                                                       │
│  Add a screenshot of the Streamlit upload screen      │
│  showing the two file upload areas and Run button.    │
│                                                       │
│  Suggested filename: screenshot_upload_screen.png     │
└──────────────────────────────────────────────────────┘
```

### Sample Output — Top Findings Preview

```
┌──────────────────────────────────────────────────────┐
│  SCREENSHOT PLACEHOLDER                               │
│                                                       │
│  Add a screenshot of the in-app findings preview      │
│  showing ranked findings with impact labels and       │
│  short explanations.                                  │
│                                                       │
│  Suggested filename: screenshot_findings_preview.png  │
└──────────────────────────────────────────────────────┘
```

### Sample PDF Report

```
┌──────────────────────────────────────────────────────┐
│  FILE PLACEHOLDER                                     │
│                                                       │
│  Add a sample generated PDF report from one of your   │
│  synthetic test cases (use mock data only).           │
│                                                       │
│  Suggested filename: sample_report_product_metrics.pdf│
└──────────────────────────────────────────────────────┘
```

### Sample Input Files

```
┌──────────────────────────────────────────────────────┐
│  FILE PLACEHOLDER                                     │
│                                                       │
│  Add one of your synthetic Excel file pairs so        │
│  reviewers can reproduce the demo run.                │
│                                                       │
│  Suggested filenames:                                 │
│    sample_period1.xlsx                                │
│    sample_period2.xlsx                                │
└──────────────────────────────────────────────────────┘
```

### Demo Clip *(optional but recommended)*

```
┌──────────────────────────────────────────────────────┐
│  CLIP PLACEHOLDER                                     │
│                                                       │
│  Record a short screen capture (30–90 seconds)        │
│  showing: upload → run analysis → view findings       │
│  → download PDF.                                      │
│                                                       │
│  Suggested filename: demo_clip.gif  or  demo_clip.mp4 │
└──────────────────────────────────────────────────────┘
```

---

## Author
Rofiah Omolara Akanni
