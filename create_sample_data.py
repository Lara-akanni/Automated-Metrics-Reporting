"""
create_sample_data.py
---------------------
Generates all sample Excel file pairs for Examples 1–4 from the project plan.

Each example produces two files (period1.xlsx and period2.xlsx) saved into
sample_data/<example_folder>/. Files include extra realistic columns (IDs,
dates, regions, managers etc.) alongside the key metric columns, mirroring
how real-world data exports typically look.

Run:
    python3 create_sample_data.py
"""

import os
import pandas as pd

OUTPUT_BASE = "sample_data"

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def save(df: pd.DataFrame, folder: str, filename: str):
    path = os.path.join(OUTPUT_BASE, folder)
    os.makedirs(path, exist_ok=True)
    full_path = os.path.join(path, filename)
    df.to_excel(full_path, index=False)
    print(f"  Saved: {full_path}")


# ===========================================================================
# Example 1 — Product Metrics (Week-over-Week)
# ===========================================================================
# Key metrics : active_users (notable drop), csat_score (notable drop),
#               success_rate (calm / stable)
# Extra cols  : team, region, product_version, response_time_ms,
#               bug_reports, tickets_opened, tickets_resolved,
#               avg_session_mins
# Rows        : 10 product teams
# ===========================================================================

def create_example1():
    print("\n[Example 1] Product Metrics...")

    teams = [
        "Mobile", "Web", "API", "Desktop",
        "Analytics", "Payments", "Auth", "Search",
        "Notifications", "Admin",
    ]
    regions        = ["EMEA", "NA", "APAC", "NA", "EMEA", "NA", "APAC", "EMEA", "NA", "APAC"]
    product_vers   = ["v3.2", "v3.2", "v2.8", "v3.1", "v3.2", "v2.9", "v3.2", "v3.0", "v3.2", "v2.8"]

    # --- Period 1: Week of 2025-04-28 ---
    p1 = pd.DataFrame({
        "week_start":          ["2025-04-28"] * 10,
        "team":                teams,
        "region":              regions,
        "product_version":     product_vers,
        "success_rate_pct":    [92.1, 91.8, 93.0, 90.5, 91.2, 92.6, 93.1, 90.8, 91.5, 92.0],
        "active_users":        [2450, 3800, 1200, 870,  1560, 2100, 980,  1340, 760,  430 ],
        "csat_score":          [4.3,  4.4,  4.2,  4.1,  4.5,  4.3,  4.4,  4.2,  4.0,  4.3 ],
        "response_time_ms":    [210,  185,  140,  320,  195,  160,  175,  205,  230,  310 ],
        "bug_reports":         [12,   8,    5,    18,   7,    4,    6,    10,   14,   9   ],
        "tickets_opened":      [88,   120,  45,   62,   95,   74,   38,   83,   51,   29  ],
        "tickets_resolved":    [80,   115,  43,   55,   90,   72,   36,   79,   48,   26  ],
        "avg_session_mins":    [8.4,  12.1, 5.2,  6.8,  9.7,  7.3,  6.1,  8.9,  4.5,  3.2 ],
    })

    # --- Period 2: Week of 2025-05-05 ---
    # active_users and csat_score drop notably; success_rate stays calm
    p2 = pd.DataFrame({
        "week_start":          ["2025-05-05"] * 10,
        "team":                teams,
        "region":              regions,
        "product_version":     product_vers,
        "success_rate_pct":    [91.8, 91.5, 92.7, 90.1, 91.0, 92.3, 92.9, 90.5, 91.2, 91.7],
        "active_users":        [1980, 3100, 940,  650,  1210, 1650, 740,  1050, 580,  310 ],
        "csat_score":          [3.8,  3.7,  3.6,  3.5,  3.9,  3.7,  3.8,  3.6,  3.4,  3.7 ],
        "response_time_ms":    [225,  192,  148,  335,  201,  168,  182,  218,  244,  325 ],
        "bug_reports":         [18,   14,   9,    24,   11,   7,    10,   15,   19,   13  ],
        "tickets_opened":      [102,  138,  58,   74,   110,  88,   47,   96,   63,   38  ],
        "tickets_resolved":    [88,   121,  49,   61,   98,   79,   42,   85,   55,   31  ],
        "avg_session_mins":    [7.9,  11.3, 4.8,  6.1,  9.0,  6.9,  5.7,  8.2,  4.1,  2.9 ],
    })

    save(p1, "example1_product_metrics", "period1_week_apr28.xlsx")
    save(p2, "example1_product_metrics", "period2_week_may05.xlsx")


# ===========================================================================
# Example 2 — Marketing Metrics (Week-over-Week)
# ===========================================================================
# Key metrics : total_visits (spike up), signups (down), conversion_rate (drop)
# Extra cols  : channel, campaign_id, region, unique_visitors, bounce_rate,
#               avg_time_on_page_secs, pages_per_session, ad_spend_usd,
#               impressions, click_through_rate_pct
# Rows        : 8 marketing channels
# ===========================================================================

def create_example2():
    print("\n[Example 2] Marketing Metrics...")

    channels = [
        "Organic Search", "Paid Search", "Social Media",
        "Email", "Referral", "Direct", "Display Ads", "Affiliate",
    ]
    campaign_ids = ["ORG-01", "PAD-07", "SOC-12", "EML-04", "REF-09", "DIR-01", "DSP-03", "AFF-06"]
    regions      = ["Global", "NA", "EMEA", "NA", "APAC", "Global", "NA", "EMEA"]

    # --- Period 1: Week of 2025-04-28 ---
    p1 = pd.DataFrame({
        "week_start":               ["2025-04-28"] * 8,
        "channel":                  channels,
        "campaign_id":              campaign_ids,
        "region":                   regions,
        "total_visits":             [18500, 9200,  7400, 5100, 3800, 4200, 2900, 1600],
        "unique_visitors":          [15200, 7800,  6100, 4300, 3100, 3700, 2400, 1350],
        "signups":                  [420,   310,   185,  260,  140,  95,   88,   62  ],
        "bounce_rate_pct":          [38.2,  42.5,  51.3, 28.4, 35.6, 32.1, 58.7, 44.2],
        "conversion_rate_pct":      [2.8,   3.4,   2.5,  5.1,  3.7,  2.3,  3.0,  3.9 ],
        "avg_time_on_page_secs":    [142,   98,    74,   210,  165,  188,  62,   110 ],
        "pages_per_session":        [4.2,   3.1,   2.8,  5.6,  3.9,  4.8,  2.1,  3.4 ],
        "ad_spend_usd":             [0,     12500, 8200, 3100, 0,    0,    5400, 2800],
        "impressions":              [0,     98000, 74000,52000,0,    0,    120000,38000],
        "click_through_rate_pct":   [0,     9.4,   10.0, 9.8,  0,    0,    2.4,  4.2 ],
    })

    # --- Period 2: Week of 2025-05-05 ---
    # visits spike up; signups and conversion_rate drop
    p2 = pd.DataFrame({
        "week_start":               ["2025-05-05"] * 8,
        "channel":                  channels,
        "campaign_id":              campaign_ids,
        "region":                   regions,
        "total_visits":             [22100, 11800, 9600, 5400, 4200, 4800, 3700, 1950],
        "unique_visitors":          [18400, 9900,  7900, 4600, 3500, 4200, 3100, 1650],
        "signups":                  [310,   228,   134,  195,  98,   72,   60,   44  ],
        "bounce_rate_pct":          [42.1,  47.8,  56.4, 31.2, 38.9, 35.4, 62.1, 48.7],
        "conversion_rate_pct":      [1.8,   1.9,   1.4,  3.6,  2.3,  1.5,  1.6,  2.3 ],
        "avg_time_on_page_secs":    [128,   87,    68,   198,  151,  174,  54,   99  ],
        "pages_per_session":        [3.8,   2.7,   2.4,  5.1,  3.5,  4.3,  1.8,  3.0 ],
        "ad_spend_usd":             [0,     14200, 9500, 3100, 0,    0,    6800, 3200],
        "impressions":              [0,     115000,88000,52000,0,    0,    145000,46000],
        "click_through_rate_pct":   [0,     10.3,  10.9, 10.4, 0,    0,    2.5,  4.2 ],
    })

    save(p1, "example2_marketing_metrics", "period1_week_apr28.xlsx")
    save(p2, "example2_marketing_metrics", "period2_week_may05.xlsx")


# ===========================================================================
# Example 3 — Revenue Metrics (Month-over-Month)
# ===========================================================================
# Key metrics : total_monthly_revenue (Product Line C significant drop),
#               units_sold, avg_order_value
# Extra cols  : product_line, region, account_manager, quarter,
#               new_customers, churned_customers, gross_margin_pct,
#               returns, support_tickets, nps_score
# Rows        : 5 product lines
# ===========================================================================

def create_example3():
    print("\n[Example 3] Revenue Metrics...")

    lines    = ["Product Line A", "Product Line B", "Product Line C", "Product Line D", "Product Line E"]
    regions  = ["NA", "EMEA", "APAC", "NA", "EMEA"]
    managers = ["Sarah Mitchell", "James Okafor", "Priya Nair", "Carlos Rivera", "Emma Thompson"]
    quarters = ["Q2 2025"] * 5

    # --- Period 1: April 2025 ---
    p1 = pd.DataFrame({
        "month":                    ["April 2025"] * 5,
        "product_line":             lines,
        "region":                   regions,
        "account_manager":          managers,
        "quarter":                  quarters,
        "total_monthly_revenue":    [125000, 98000, 87000, 210000, 65000],
        "units_sold":               [1240,   870,   920,   2100,   580  ],
        "avg_order_value":          [100.8,  112.6, 94.6,  100.0,  112.1],
        "new_customers":            [42,     31,    38,    74,     22   ],
        "churned_customers":        [8,      5,     7,     12,     4    ],
        "gross_margin_pct":         [62.4,   58.1,  60.3,  64.8,   57.2 ],
        "returns":                  [28,     19,    24,    45,     11   ],
        "support_tickets":          [64,     48,    55,    98,     32   ],
        "nps_score":                [48,     42,    45,    52,     39   ],
    })

    # --- Period 2: May 2025 ---
    # Product Line C drops significantly; others stable
    p2 = pd.DataFrame({
        "month":                    ["May 2025"] * 5,
        "product_line":             lines,
        "region":                   regions,
        "account_manager":          managers,
        "quarter":                  quarters,
        "total_monthly_revenue":    [123000, 95000, 61000, 208000, 64000],
        "units_sold":               [1210,   845,   645,   2080,   570  ],
        "avg_order_value":          [101.7,  112.4, 94.6,  100.0,  112.3],
        "new_customers":            [39,     28,    18,    71,     21   ],
        "churned_customers":        [9,      6,     24,    13,     5    ],
        "gross_margin_pct":         [62.1,   57.8,  55.4,  64.5,   57.0 ],
        "returns":                  [31,     22,    48,    47,     12   ],
        "support_tickets":          [68,     51,    112,   101,    34   ],
        "nps_score":                [47,     41,    28,    51,     38   ],
    })

    save(p1, "example3_revenue_mom", "period1_april_2025.xlsx")
    save(p2, "example3_revenue_mom", "period2_may_2025.xlsx")


# ===========================================================================
# Example 4 — Mixed Dataset (Numeric + Categorical Changes)
# ===========================================================================
# Key metrics : volume (numeric, moderate changes),
#               rate_pct (numeric, moderate changes),
#               score (numeric, minor changes),
#               status (categorical — some flip Active → Inactive)
# Extra cols  : record_id, account_name, region, account_manager,
#               tier, contract_value_usd, last_contact_date,
#               industry, employee_count
# Rows        : 12 account records
# ===========================================================================

def create_example4():
    print("\n[Example 4] Mixed Dataset...")

    record_ids    = [f"ACC-{str(i).zfill(3)}" for i in range(1, 13)]
    account_names = [
        "Apex Technologies", "BlueStar Logistics", "Crestwood Finance",
        "Delta Healthcare", "Echo Retail", "Frontier Media",
        "Greenfield Energy", "Horizon Consulting", "Iris Manufacturing",
        "JetStream Airlines", "Keystone Pharma", "Luminary EdTech",
    ]
    regions   = ["NA", "EMEA", "NA", "APAC", "NA", "EMEA", "NA", "APAC", "EMEA", "NA", "APAC", "NA"]
    managers  = [
        "Dana Lee", "Tom Walsh", "Dana Lee", "Priya Nair",
        "Tom Walsh", "Carlos Rivera", "Dana Lee", "Emma Thompson",
        "Tom Walsh", "Carlos Rivera", "Priya Nair", "Dana Lee",
    ]
    tiers     = ["Enterprise", "Mid-Market", "Enterprise", "SMB", "Mid-Market", "Enterprise",
                 "SMB", "Mid-Market", "Enterprise", "Mid-Market", "Enterprise", "SMB"]
    industry  = ["Tech", "Logistics", "Finance", "Healthcare", "Retail", "Media",
                 "Energy", "Consulting", "Manufacturing", "Airlines", "Pharma", "Education"]
    emp_count = [5200, 1800, 3400, 8900, 620, 2100, 450, 1200, 4100, 12000, 6700, 310]

    # --- Period 1 ---
    p1 = pd.DataFrame({
        "report_date":          ["2025-04-30"] * 12,
        "record_id":            record_ids,
        "account_name":         account_names,
        "region":               regions,
        "account_manager":      managers,
        "industry":             industry,
        "employee_count":       emp_count,
        "tier":                 tiers,
        "status":               ["Active"] * 12,
        "volume":               [5200, 3100, 4800, 7200, 1500, 2900, 980,  3600, 4200, 8100, 6300, 750 ],
        "rate_pct":             [78.4, 72.1, 80.5, 68.3, 74.2, 76.8, 65.4, 71.9, 79.2, 66.7, 77.5, 63.1],
        "score":                [82,   75,   88,   71,   79,   84,   68,   76,   85,   70,   81,   65  ],
        "contract_value_usd":   [124000,48000,98000,210000,22000,75000,15000,52000,115000,380000,175000,12000],
        "last_contact_date":    ["2025-04-25","2025-04-22","2025-04-28","2025-04-20","2025-04-26",
                                  "2025-04-24","2025-04-29","2025-04-23","2025-04-27","2025-04-21",
                                  "2025-04-25","2025-04-28"],
    })

    # --- Period 2 ---
    # status: 4 accounts flip to Inactive (BlueStar, Echo, Greenfield, Luminary)
    # volume, rate_pct, score: moderate numeric changes across the board
    p2 = pd.DataFrame({
        "report_date":          ["2025-05-31"] * 12,
        "record_id":            record_ids,
        "account_name":         account_names,
        "region":               regions,
        "account_manager":      managers,
        "industry":             industry,
        "employee_count":       emp_count,
        "tier":                 tiers,
        "status":               ["Active", "Inactive", "Active", "Active", "Inactive",
                                  "Active", "Inactive", "Active", "Active", "Active",
                                  "Active", "Inactive"],
        "volume":               [5480, 2800, 5100, 7450, 1200, 3100, 820,  3800, 4350, 8400, 6600, 600 ],
        "rate_pct":             [75.2, 68.4, 77.8, 65.1, 70.8, 74.3, 61.2, 69.5, 76.8, 64.2, 74.9, 59.8],
        "score":                [80,   71,   85,   69,   75,   82,   64,   74,   83,   68,   79,   61  ],
        "contract_value_usd":   [124000,48000,98000,210000,22000,75000,15000,52000,115000,380000,175000,12000],
        "last_contact_date":    ["2025-05-28","2025-05-15","2025-05-29","2025-05-20","2025-05-10",
                                  "2025-05-27","2025-05-08","2025-05-25","2025-05-30","2025-05-22",
                                  "2025-05-26","2025-05-05"],
    })

    save(p1, "example4_mixed", "period1_april_2025.xlsx")
    save(p2, "example4_mixed", "period2_may_2025.xlsx")


# ===========================================================================
# Run all
# ===========================================================================

if __name__ == "__main__":
    print("Generating sample Excel files...")
    create_example1()
    create_example2()
    create_example3()
    create_example4()
    print("\nDone! All files saved to sample_data/")
