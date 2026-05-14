"""
create_sample_data.py
---------------------
Generates realistic transaction-level Excel file pairs for Examples 1–4.

Each example produces two files (period1 / period2) saved into
sample_data/<example_folder>/. Files are raw transaction / session /
account-level data — not pre-aggregated — so the app and tools can
compute metrics (success rate, total revenue, conversion rate, etc.)
from the underlying records, just as a real analyst would.

Row counts:
  Example 1 — Product  : ~350 rows per file (payment transaction log)
  Example 2 — Marketing: ~550 rows per file (session log)
  Example 3 — Revenue  : ~480 rows per file (payment transaction table)
  Example 4 — Mixed    : ~80  rows per file (account records)

Run:
    python3 create_sample_data.py
"""

import os
import numpy as np
import pandas as pd
from datetime import date, timedelta

rng = np.random.default_rng(42)   # fixed seed → reproducible files

OUTPUT_BASE = "sample_data"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def save(df: pd.DataFrame, folder: str, filename: str):
    path = os.path.join(OUTPUT_BASE, folder)
    os.makedirs(path, exist_ok=True)
    full_path = os.path.join(path, filename)
    df.to_excel(full_path, index=False)
    print(f"  Saved {len(df):>4} rows → {full_path}")


def random_dates_in_range(start: date, end: date, n: int) -> list:
    delta = (end - start).days
    offsets = rng.integers(0, delta + 1, size=n)
    return [str(start + timedelta(days=int(d))) for d in offsets]


def random_times(n: int) -> list:
    h = rng.integers(0, 24, size=n)
    m = rng.integers(0, 60, size=n)
    return [f"{hh:02d}:{mm:02d}:{rng.integers(0,60):02d}" for hh, mm in zip(h, m)]


def seq_ids(prefix: str, n: int, start: int = 1) -> list:
    return [f"{prefix}{str(i).zfill(6)}" for i in range(start, start + n)]


# ===========================================================================
# Example 1 — Product Metrics  (Payment transaction log, week-over-week)
# ===========================================================================
# Each row = one payment transaction attempt.
# Key fields  : status (Success / Failed), csat_score, response_time_ms
# Derived KPIs: success_rate = Success / total,  avg CSAT,  active_users (distinct user_ids)
# Engineered  : Period 2 has more failures (rate drops ~92% → ~85%) and lower CSAT
# Extra cols  : transaction_id, reference_number, user_id, team, region,
#               product_version, payment_method, amount_usd, error_code,
#               device_type, channel, currency
# ===========================================================================

def create_example1():
    print("\n[Example 1] Product Metrics — payment transaction log")

    n1, n2 = 350, 370

    teams          = ["Mobile", "Web", "API", "Desktop", "Payments", "Auth", "Search", "Notifications"]
    regions        = ["NA", "EMEA", "APAC"]
    product_vers   = ["v3.2", "v3.1", "v2.9", "v3.0"]
    pay_methods    = ["Credit Card", "Debit Card", "Bank Transfer", "PayPal", "Apple Pay", "Google Pay"]
    devices        = ["Mobile", "Desktop", "Tablet"]
    channels       = ["App", "Web", "API"]
    currencies     = ["USD", "USD", "USD", "GBP", "EUR", "USD", "USD", "CAD"]
    error_codes    = ["ERR_TIMEOUT", "ERR_INSUFFICIENT_FUNDS", "ERR_INVALID_CARD",
                      "ERR_NETWORK", "ERR_DECLINED", "ERR_AUTH_FAILED"]

    def make_product_file(n, week_start, week_end, success_rate, avg_csat, id_start):
        statuses    = rng.choice(["Success", "Failed"],  size=n,
                                  p=[success_rate, 1 - success_rate])
        csat_mask   = rng.random(n) < 0.28          # ~28% of txns get a CSAT response
        csat_raw    = rng.normal(avg_csat, 0.4, n).clip(1, 5).round(1)
        csat_col    = [round(float(c), 1) if m else None for c, m in zip(csat_raw, csat_mask)]
        amounts     = rng.uniform(25, 850, n).round(2)
        error_col   = [rng.choice(error_codes) if s == "Failed" else None for s in statuses]

        return pd.DataFrame({
            "transaction_id":    seq_ids("TXN-P1-", n, id_start),
            "reference_number":  seq_ids("REF-", n, id_start * 3),
            "date":              random_dates_in_range(week_start, week_end, n),
            "time":              random_times(n),
            "user_id":           seq_ids("USR-", n, rng.integers(1000, 9000)),
            "team":              rng.choice(teams, size=n),
            "region":            rng.choice(regions, size=n),
            "country":           rng.choice(["US", "UK", "DE", "FR", "AU", "CA", "SG", "IN"], size=n),
            "product_version":   rng.choice(product_vers, size=n),
            "payment_method":    rng.choice(pay_methods, size=n),
            "currency":          rng.choice(currencies, size=n),
            "amount_usd":        amounts,
            "status":            statuses,
            "error_code":        error_col,
            "response_time_ms":  rng.integers(80, 620, size=n),
            "csat_score":        csat_col,
            "device_type":       rng.choice(devices, size=n),
            "channel":           rng.choice(channels, size=n),
            "is_retry":          rng.choice(["Yes", "No"], size=n, p=[0.12, 0.88]),
            "merchant_category": rng.choice(["SaaS", "E-commerce", "Healthcare",
                                              "Finance", "Education", "Retail"], size=n),
        })

    p1 = make_product_file(n1,
                            date(2025, 4, 28), date(2025, 5, 4),
                            success_rate=0.921, avg_csat=4.3, id_start=1)
    p2 = make_product_file(n2,
                            date(2025, 5, 5),  date(2025, 5, 11),
                            success_rate=0.851, avg_csat=3.7, id_start=n1 + 1)

    save(p1, "example1_product_metrics", "period1_week_apr28.xlsx")
    save(p2, "example1_product_metrics", "period2_week_may05.xlsx")


# ===========================================================================
# Example 2 — Marketing Metrics  (Session log, week-over-week)
# ===========================================================================
# Each row = one website / app session.
# Key fields  : channel, signed_up, converted (bool)
# Derived KPIs: total_visits = row count,  signups = sum(signed_up),
#               conversion_rate = sum(converted) / total
# Engineered  : Period 2 has more traffic (visits ↑) but signups and
#               conversion_rate drop notably
# Extra cols  : session_id, user_id, date, time, device, landing_page,
#               referral_source, campaign_id, region, pages_viewed,
#               time_on_site_secs, bounced, ad_click, utm_medium
# ===========================================================================

def create_example2():
    print("\n[Example 2] Marketing Metrics — session log")

    n1, n2 = 520, 680    # n2 > n1  →  traffic spike in Period 2

    channels      = ["Organic Search", "Paid Search", "Social Media",
                     "Email", "Referral", "Direct", "Display Ads", "Affiliate"]
    ch_weights_p1 = [0.30, 0.20, 0.16, 0.12, 0.09, 0.07, 0.04, 0.02]
    ch_weights_p2 = [0.28, 0.24, 0.18, 0.10, 0.08, 0.06, 0.04, 0.02]   # more paid/social
    devices       = ["Mobile", "Desktop", "Tablet"]
    landing_pages = ["/home", "/product", "/pricing", "/blog", "/features",
                     "/signup", "/demo", "/case-studies"]
    referrers     = ["google.com", "facebook.com", "linkedin.com", "twitter.com",
                     "bing.com", "newsletter", "partner-site.com", "(direct)"]
    campaigns     = ["CAMP-SPR25", "CAMP-RET01", "CAMP-BRD02", "CAMP-NL03",
                     "CAMP-SOC04", "CAMP-ORG", "CAMP-AFF05", "CAMP-DSP06"]
    regions       = ["NA", "EMEA", "APAC", "LATAM"]
    utm_mediums   = ["organic", "cpc", "social", "email", "referral", "none", "display", "affiliate"]

    def make_marketing_file(n, week_start, week_end, signup_rate, conversion_rate, ch_weights, id_start):
        channel_idx = rng.choice(len(channels), size=n, p=ch_weights)
        signed_up   = (rng.random(n) < signup_rate).astype(int)
        converted   = np.where(signed_up, (rng.random(n) < 0.35).astype(int),
                               (rng.random(n) < conversion_rate * 0.3).astype(int))
        pages       = rng.integers(1, 18, size=n)
        bounced     = (pages == 1).astype(int)
        time_on     = np.where(bounced, rng.integers(5, 30, size=n),
                               rng.integers(45, 720, size=n))

        return pd.DataFrame({
            "session_id":           seq_ids("SES-", n, id_start),
            "user_id":              seq_ids("USR-MKT-", n, rng.integers(5000, 50000)),
            "date":                 random_dates_in_range(week_start, week_end, n),
            "time":                 random_times(n),
            "channel":              [channels[i] for i in channel_idx],
            "campaign_id":          [campaigns[i] for i in channel_idx],
            "utm_medium":           [utm_mediums[i] for i in channel_idx],
            "region":               rng.choice(regions, size=n),
            "country":              rng.choice(["US", "UK", "DE", "FR", "CA",
                                                "AU", "BR", "SG", "IN", "NL"], size=n),
            "device":               rng.choice(devices, size=n, p=[0.54, 0.38, 0.08]),
            "landing_page":         rng.choice(landing_pages, size=n),
            "referral_source":      rng.choice(referrers, size=n),
            "pages_viewed":         pages,
            "time_on_site_secs":    time_on,
            "bounced":              bounced,
            "signed_up":            signed_up,
            "converted":            converted,
            "ad_click":             (rng.random(n) < 0.18).astype(int),
            "returning_visitor":    rng.choice([0, 1], size=n, p=[0.62, 0.38]),
            "browser":              rng.choice(["Chrome", "Safari", "Firefox",
                                                "Edge", "Other"], size=n,
                                               p=[0.55, 0.25, 0.09, 0.08, 0.03]),
            "screen_resolution":    rng.choice(["1920x1080", "1366x768", "375x667",
                                                "414x896", "1280x800", "2560x1440"], size=n),
        })

    p1 = make_marketing_file(n1,
                              date(2025, 4, 28), date(2025, 5, 4),
                              signup_rate=0.082, conversion_rate=0.028,
                              ch_weights=ch_weights_p1, id_start=1)
    p2 = make_marketing_file(n2,
                              date(2025, 5, 5),  date(2025, 5, 11),
                              signup_rate=0.054, conversion_rate=0.019,
                              ch_weights=ch_weights_p2, id_start=n1 + 1)

    save(p1, "example2_marketing_metrics", "period1_week_apr28.xlsx")
    save(p2, "example2_marketing_metrics", "period2_week_may05.xlsx")


# ===========================================================================
# Example 3 — Revenue  (Payment transaction table, month-over-month)
# ===========================================================================
# Each row = one payment transaction.
# Key fields  : product_line (A / B / C), amount_usd, status
# Derived KPIs: total revenue per product = sum(amount_usd where status=Completed)
# Engineered  : Product Line C has significantly fewer & lower-value transactions
#               in Period 2, causing a ~30% revenue drop for that line.
#               Lines A and B remain stable.
# Extra cols  : transaction_id, invoice_number, customer_id, customer_name,
#               country, region, account_manager, salesperson, product_name,
#               plan_type, payment_method, currency, status, refund_reason
# ===========================================================================

def create_example3():
    print("\n[Example 3] Revenue — payment transaction table")

    product_lines  = ["Product Line A", "Product Line B", "Product Line C"]
    product_names  = {
        "Product Line A": ["Alpha Enterprise", "Alpha Pro+", "Alpha Teams"],
        "Product Line B": ["Beta Business",   "Beta Standard", "Beta Starter"],
        "Product Line C": ["Core Lite",       "Core Basic",    "Core Free+"],
    }
    plan_types     = ["Annual", "Monthly", "Quarterly", "One-time"]
    pay_methods    = ["Credit Card", "Bank Transfer", "ACH", "Wire Transfer", "PayPal"]
    currencies     = ["USD", "USD", "EUR", "GBP", "USD", "CAD", "USD", "AUD"]
    regions        = ["NA", "EMEA", "APAC", "LATAM"]
    countries      = ["US", "UK", "DE", "FR", "CA", "AU", "SG", "NL", "BR", "IN"]
    managers       = ["Sarah Mitchell", "James Okafor", "Priya Nair",
                      "Carlos Rivera", "Emma Thompson"]
    salespersons   = ["Alex Huang", "Mia Fernandez", "Liam Osei",
                      "Chloe Dupont", "Noah Patel", "Sofia Andersen"]
    refund_reasons = ["Customer Request", "Duplicate Charge", "Service Issue",
                      "Billing Error", "Cancellation"]

    # Transaction counts and amount ranges per product per period
    # Period 1 (April): A=90, B=150, C=240  → totals approx A=£126k B=£97k C=£86k
    # Period 2 (May):   A=88, B=145, C=165  → totals approx A=£123k B=£94k C=£60k

    config = {
        # (n_transactions, amount_low, amount_high, refund_rate)
        "p1": {
            "Product Line A": (90,  800, 2200, 0.04),
            "Product Line B": (150, 350, 1000, 0.05),
            "Product Line C": (240,  80,  480, 0.06),
        },
        "p2": {
            "Product Line A": (88,  810, 2200, 0.04),
            "Product Line B": (145, 350,  980, 0.05),
            "Product Line C": (165,  75,  470, 0.09),   # fewer txns, higher refund
        },
    }

    def make_revenue_file(period_config, month_start, month_end, id_start):
        rows = []
        txn_counter = id_start
        for pl, (n, lo, hi, refund_rate) in period_config.items():
            pnames = product_names[pl]
            statuses = rng.choice(
                ["Completed", "Refunded", "Failed"],
                size=n,
                p=[1 - refund_rate - 0.02, refund_rate, 0.02],
            )
            amounts = rng.uniform(lo, hi, size=n).round(2)

            for i in range(n):
                rows.append({
                    "transaction_id":   f"TXN-REV-{str(txn_counter).zfill(6)}",
                    "invoice_number":   f"INV-{str(txn_counter * 7 + 1001).zfill(7)}",
                    "date":             rng.choice(
                                            random_dates_in_range(month_start, month_end, 1)
                                        ),
                    "time":             random_times(1)[0],
                    "customer_id":      f"CUST-{str(rng.integers(1000, 9999)).zfill(4)}",
                    "customer_name":    rng.choice([
                                            "Apex Corp", "BlueStar Ltd", "Crestwood Inc",
                                            "Delta Group", "Echo Systems", "Frontier Co",
                                            "Greenfield Partners", "Horizon LLC",
                                            "Iris Holdings", "JetStream GmbH",
                                            "Keystone AG", "Luminary Srl",
                                            "Marble Tech", "Nova Solutions",
                                            "Orbit Digital", "Pinnacle Ventures",
                                        ]),
                    "region":           rng.choice(regions),
                    "country":          rng.choice(countries),
                    "account_manager":  rng.choice(managers),
                    "salesperson":      rng.choice(salespersons),
                    "product_line":     pl,
                    "product_name":     rng.choice(pnames),
                    "plan_type":        rng.choice(plan_types, p=[0.55, 0.30, 0.10, 0.05]),
                    "payment_method":   rng.choice(pay_methods),
                    "currency":         rng.choice(currencies),
                    "amount_usd":       amounts[i],
                    "status":           statuses[i],
                    "refund_reason":    (rng.choice(refund_reasons)
                                         if statuses[i] == "Refunded" else None),
                    "is_new_customer":  rng.choice(["Yes", "No"], p=[0.22, 0.78]),
                    "contract_type":    rng.choice(["Direct", "Reseller", "Partner"],
                                                    p=[0.70, 0.20, 0.10]),
                    "discount_pct":     round(float(rng.choice(
                                            [0, 0, 0, 5, 10, 15, 20],
                                            p=[0.40, 0.20, 0.15, 0.10, 0.08, 0.04, 0.03]
                                        )), 1),
                })
                txn_counter += 1

        df = pd.DataFrame(rows)
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)   # shuffle rows
        return df

    p1 = make_revenue_file(config["p1"],
                            date(2025, 4, 1), date(2025, 4, 30), id_start=1)
    p2 = make_revenue_file(config["p2"],
                            date(2025, 5, 1), date(2025, 5, 31), id_start=600)

    save(p1, "example3_revenue_mom", "period1_april_2025.xlsx")
    save(p2, "example3_revenue_mom", "period2_may_2025.xlsx")


# ===========================================================================
# Example 4 — Mixed Dataset  (Account records, month-over-month)
# ===========================================================================
# Each row = one account / customer record.
# Key fields  : status (Active / Inactive — categorical),
#               volume, rate_pct, score (numeric)
# Engineered  : ~18 accounts flip Active → Inactive in Period 2;
#               volume, rate_pct, score all show moderate numeric changes.
# Extra cols  : record_id, account_name, region, country, account_manager,
#               industry, employee_count, tier, contract_value_usd,
#               last_contact_date, renewal_date, support_tier, nps_score
# ===========================================================================

def create_example4():
    print("\n[Example 4] Mixed Dataset — account records")

    n = 80

    account_names = [
        "Apex Technologies", "BlueStar Logistics", "Crestwood Finance",
        "Delta Healthcare", "Echo Retail", "Frontier Media",
        "Greenfield Energy", "Horizon Consulting", "Iris Manufacturing",
        "JetStream Airlines", "Keystone Pharma", "Luminary EdTech",
        "Marble Dynamics", "Nova Legal", "Orbit Digital", "Pinnacle Ventures",
        "Quorum Analytics", "Redwood Biotech", "Summit Architecture", "Tidal Payments",
        "Umbrella Security", "Vertex Robotics", "Wavelength Audio", "Xenon Aerospace",
        "Yellowstone Mining", "Zephyr Mobility", "Anchor Fintech", "Beacon Publishing",
        "Cascade Networks", "Driftwood Creative", "Eclipse Automotive", "Forge Industries",
        "Glacier Properties", "Halo Sportswear", "Indigo Hospitality", "Jade Commerce",
        "Kite Insurance", "Lattice Software", "Mosaic Events", "Nectar Foods",
        "Onyx Engineering", "Prism Textiles", "Quest Shipping", "Ridge Agriculture",
        "Sterling Media", "Tempest Clean Energy", "Union Telecom", "Vantage Wealth",
        "Wildfire Gaming", "Xcel Healthcare", "Yarrow Cosmetics", "Zenith Aerospace",
        "Alpine Consulting", "Bright Futures NGO", "Cobalt Semiconductors",
        "Dawn Hospitality", "Ember Logistics", "Flux Analytics", "Grove Pharma",
        "Haven Insurance", "Impact Ventures", "Junction Rail", "Knoll Architecture",
        "Lark Media", "Mantis Cybersecurity", "Nimbus Cloud", "Obsidian Mining",
        "Pulse Wearables", "Quartz Construction", "Raven Defense", "Solace Health",
        "Thorn Agritech", "Uplift Finance", "Valor Logistics", "Wren Publishing",
        "Axis Motors", "Bloom Biotech", "Cipher Networks", "Dusk Realty",
        "Eagle Fintech",
    ][:n]

    industries  = rng.choice(["Technology", "Healthcare", "Finance", "Retail",
                               "Logistics", "Energy", "Media", "Manufacturing",
                               "Consulting", "Education", "Legal", "Pharma"], size=n)
    regions     = rng.choice(["NA", "EMEA", "APAC", "LATAM"], size=n,
                              p=[0.40, 0.30, 0.20, 0.10])
    countries   = rng.choice(["US", "UK", "DE", "FR", "CA", "AU", "SG",
                               "NL", "BR", "IN", "JP", "ZA"], size=n)
    managers    = rng.choice(["Dana Lee", "Tom Walsh", "Priya Nair",
                               "Carlos Rivera", "Emma Thompson"], size=n)
    tiers       = rng.choice(["Enterprise", "Mid-Market", "SMB"],
                              size=n, p=[0.25, 0.45, 0.30])
    emp_counts  = rng.integers(50, 25000, size=n)
    contracts   = rng.integers(8000, 450000, size=n)
    support_tiers = rng.choice(["Platinum", "Gold", "Silver", "Standard"], size=n,
                                p=[0.15, 0.30, 0.35, 0.20])

    # 18 accounts will flip to Inactive in Period 2
    inactive_idx = rng.choice(n, size=18, replace=False)
    status_p1    = ["Active"] * n
    status_p2    = ["Active"] * n
    for i in inactive_idx:
        status_p2[i] = "Inactive"

    # Numeric cols: moderate changes between periods
    volume_p1   = rng.integers(500, 9500, size=n)
    rate_p1     = rng.uniform(58, 88, size=n).round(1)
    score_p1    = rng.integers(55, 96, size=n)
    nps_p1      = rng.integers(20, 72, size=n)

    # Period 2: apply moderate deltas; inactive accounts drop more
    volume_delta = rng.integers(-800, 900, size=n)
    volume_delta[inactive_idx] = rng.integers(-2000, -800, size=len(inactive_idx))
    rate_delta   = rng.uniform(-5, 4, size=n).round(1)
    score_delta  = rng.integers(-6, 5, size=n)
    nps_delta    = rng.integers(-12, 8, size=n)
    nps_delta[inactive_idx] = rng.integers(-25, -10, size=len(inactive_idx))

    volume_p2 = (volume_p1 + volume_delta).clip(0)
    rate_p2   = (rate_p1   + rate_delta).clip(0, 100).round(1)
    score_p2  = (score_p1  + score_delta).clip(0, 100)
    nps_p2    = (nps_p1    + nps_delta).clip(-100, 100)

    last_contact_p1 = [
        str(date(2025, 4, 1) + timedelta(days=int(rng.integers(0, 29))))
        for _ in range(n)
    ]
    last_contact_p2 = [
        str(date(2025, 5, 1) + timedelta(days=int(rng.integers(0, 30))))
        for _ in range(n)
    ]
    renewal_dates = [
        str(date(2025, 6, 1) + timedelta(days=int(rng.integers(0, 180))))
        for _ in range(n)
    ]

    record_ids = [f"ACC-{str(i).zfill(4)}" for i in range(1, n + 1)]

    def build_mixed(statuses, volumes, rates, scores, nps_vals, last_contacts, report_date):
        return pd.DataFrame({
            "report_date":          [report_date] * n,
            "record_id":            record_ids,
            "account_name":         account_names,
            "industry":             industries,
            "region":               regions,
            "country":              countries,
            "account_manager":      managers,
            "tier":                 tiers,
            "support_tier":         support_tiers,
            "employee_count":       emp_counts,
            "contract_value_usd":   contracts,
            "renewal_date":         renewal_dates,
            "status":               statuses,
            "volume":               volumes,
            "rate_pct":             rates,
            "score":                scores,
            "nps_score":            nps_vals,
            "last_contact_date":    last_contacts,
            "open_support_tickets": rng.integers(0, 18, size=n),
            "product_modules_used": rng.integers(1, 9,  size=n),
            "logins_last_30_days":  rng.integers(0, 120, size=n),
        })

    p1 = build_mixed(status_p1, volume_p1, rate_p1, score_p1,
                     nps_p1, last_contact_p1, "2025-04-30")
    p2 = build_mixed(status_p2, volume_p2, rate_p2, score_p2,
                     nps_p2, last_contact_p2, "2025-05-31")

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
    print("\nDone. All files saved to sample_data/")
    print("\nRow summary:")
    print("  Example 1 — Product   : ~350 rows/file  (payment transaction log)")
    print("  Example 2 — Marketing : ~550 rows/file  (session log)")
    print("  Example 3 — Revenue   : ~480 rows/file  (payment transaction table)")
    print("  Example 4 — Mixed     :  80  rows/file  (account records)")
