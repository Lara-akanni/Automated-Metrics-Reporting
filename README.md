# Automated Metrics Comparison and Reporting

> A GenAI-powered app that compares two Excel datasets across time periods and produces a ranked, narrative-driven PDF report — replacing a hours-long manual analyst workflow.

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
- An [Anthropic API key](https://console.anthropic.com/) — the app uses Claude for analysis and narrative generation

---

### 1. Clone the Repository

```bash
git clone https://github.com/Lara-akanni/genai_project.git
cd genai_project
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
| `anthropic` | Claude API client (LLM + tool use) |
| `reportlab` | PDF report generation |
| `scipy` | Statistical significance testing |

---

### 4. Set Your API Key

Create a `.env` file in the project root (this file is git-ignored and should never be committed):

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

Or export it directly in your terminal session:

```bash
# Mac/Linux
export ANTHROPIC_API_KEY=your_api_key_here

# Windows
set ANTHROPIC_API_KEY=your_api_key_here
```

---

### 5. Run the App

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

### 6. Try It with the Sample Files

Two sample Excel files are included in the `sample_data/` folder so you can run the app immediately without preparing your own data:

```
sample_data/
  sample_period1.xlsx   ← baseline period (e.g. last week)
  sample_period2.xlsx   ← comparison period (e.g. this week)
```

**Steps:**
1. In the app, click **Browse files** under **Period 1** and upload `sample_period1.xlsx`
2. Click **Browse files** under **Period 2** and upload `sample_period2.xlsx`
3. Click **Run Analysis**
4. Review the ranked findings displayed on screen
5. Click **Download PDF Report** to save the output

The sample files contain product metrics with deliberate engineered changes (a success rate drop and a satisfaction score dip) so you can verify the app is detecting and ranking findings correctly.

---

### Project Structure

```
genai_project/
├── app.py                  # Streamlit app entry point
├── requirements.txt        # Python dependencies
├── .env.example            # Template for API key setup (copy to .env)
├── tools.py                # Backend functions called by the LLM
│   ├── compute_percentage_change()
│   ├── detect_outliers()
│   └── run_significance_test()
├── analysis.py             # Column alignment, delta computation, LLM orchestration
├── report.py               # PDF generation from structured JSON findings
└── sample_data/
    ├── sample_period1.xlsx
    └── sample_period2.xlsx
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
  LLM returns structured JSON findings, ranked by impact
  (each finding: metric, prev value, curr value, delta,
   direction, impact level, narrative explanation)
            │
            ▼
  App formats findings into PDF report
  (most impactful findings at the top)
            │
            ▼
  [Analyst downloads and shares PDF]
```

### Key Design Choices

**1. Structured Outputs (JSON)**
The LLM is prompted to return all findings as strict JSON rather than freeform prose. Each finding object includes: `metric_name`, `previous_value`, `current_value`, `delta`, `direction`, `impact_level`, and `explanation`. This makes it possible to programmatically sort findings by impact and assemble a consistent PDF regardless of the dataset domain.

**2. Tool Use / Function Calling**
Rather than asking the LLM to compute statistics itself (which would be unreliable), the LLM is given access to three backend functions it calls during analysis. This keeps the maths deterministic and auditable while letting the LLM focus on reasoning and narrative.

**3. No-configuration Design**
The analyst does not need to specify column types, stakeholder audience, or domain. The app infers all of this from the data. This means the same pipeline works for a marketing report and a revenue report without reconfiguration.

**4. Built-in Guardrails**
- Refuses to run if column overlap between the two files is below 50%
- Returns a clear "no significant changes found" message instead of fabricating findings
- Normalises categorical values to lowercase before comparison to avoid false positives from formatting differences (e.g. `"active"` vs `"Active"` vs `"ACTIVE"`)

---

## Evaluation and Results

### Baseline Being Compared Against
The baseline is the **manual Excel workflow** described above. For each test case, the analyst independently analyzes the same file pair and records their findings. The app's output is then compared against that ground truth.

### Evaluation Rubric
Each test run is scored on three dimensions, each rated 1–3, for a maximum of **9 points**. A score of **7 or higher** indicates strong performance.

| Dimension | What It Measures | 1 | 2 | 3 |
|---|---|---|---|---|
| **Change Detection** | Did the app correctly identify all major numeric and categorical changes? | Missed key changes | Caught most | Caught all |
| **Ranking Correctness** | Are the most impactful findings ranked at the top? | Ranking is wrong | Mostly correct | Fully correct |
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
│  Average total score:   [ X.X ] / 9                              │
│  Cases scoring 7+:      [ X ] / [ X ]                            │
│                                                                   │
│  Per-dimension averages                                           │
│  ──────────────────────                                           │
│  Change Detection:      [ X.X ] / 3                              │
│  Ranking Correctness:   [ X.X ] / 3                              │
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
