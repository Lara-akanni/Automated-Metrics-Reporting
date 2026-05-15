"""
create_sample_data.py
---------------------
Generates realistic transaction-level Excel file pairs for Examples 1–4.

Each example produces two files (period1 / period2) saved into
sample_data/<example_folder>/. Files are raw transaction / session /
account-level data — not pre-aggregated — so the app and tools can
compute metrics (success rate, total revenue, conversion rate, etc.)
from the underlying records, just as a real analyst would.

Row counts (kept small for API token efficiency during testing):
  Example 1 — Product  : 50 rows per file (payment transaction log)
  Example 2 — Marketing: 50 / 65 rows per file (session log — n2 > n1 for traffic spike)
  Example 3 — Revenue  : 50 rows per file (payment transaction table)
  Example 4 — Mixed    : 40 rows per file (account records)

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


def seq_ids(prefix: str, n: int, start: int = 1) -> list:
    return [f"{prefix}{str(i).zfill(5)}" for i in range(start, start + n)]


# ===========================================================================
# Example 1 — Product Metrics  (Payment transaction log, week-over-week)
# ===========================================================================
# Each row = one payment transaction attempt.
# Key columns : transaction_id, date, amount_usd, status, csat_score, response_time_ms
# Engineered  : success rate drops ~92% → ~85%; avg csat drops 4.3 → 3.7
# ===========================================================================

def create_example1():
    print("\n[Example 1] Product Metrics — payment transaction log")

    n1, n2 = 50, 50

    def make_product_file(n, week_start, week_end, success_rate, avg_csat, id_start):
        statuses  = rng.choice(["Success", "Failed"], size=n,
                                p=[success_rate, 1 - success_rate])
        csat_mask = rng.random(n) < 0.30
        csat_raw  = rng.normal(avg_csat, 0.4, n).clip(1, 5).round(1)
        csat_col  = [round(float(c), 1) if m else None for c, m in zip(csat_raw, csat_mask)]

        return pd.DataFrame({
            "transaction_id":   seq_ids("TXN-", n, id_start),
            "date":             random_dates_in_range(week_start, week_end, n),
            "amount_usd":       rng.uniform(25, 850, n).round(2),
            "status":           statuses,
            "csat_score":       csat_col,
            "response_time_ms": rng.integers(80, 620, size=n),
        })

    p1 = make_product_file(n1, date(2025, 4, 28), date(2025, 5, 4),
                           success_rate=0.921, avg_csat=4.3, id_start=1)
    p2 = make_product_file(n2, date(2025, 5, 5),  date(2025, 5, 11),
                           success_rate=0.851, avg_csat=3.7, id_start=n1 + 1)

    save(p1, "example1_product_metrics", "Product_week_apr28.xlsx")
    save(p2, "example1_product_metrics", "Product_week_may05.xlsx")


# ===========================================================================
# Example 2 — Marketing Metrics  (Session log, week-over-week)
# ===========================================================================
# Each row = one website / app session.
# Key columns : session_id, date, channel, pages_viewed, time_on_site_secs,
#               bounced, signed_up, converted
# Engineered  : n2 > n1 (traffic spike); signup and conversion rates drop
# ===========================================================================

def create_example2():
    print("\n[Example 2] Marketing Metrics — session log")

    n1, n2 = 50, 65    # n2 > n1 → traffic spike in Period 2

    channels = ["Organic Search", "Paid Search", "Social Media",
                "Email", "Referral", "Direct"]

    def make_marketing_file(n, week_start, week_end, signup_rate, conv_rate, id_start):
        pages    = rng.integers(1, 15, size=n)
        bounced  = (pages == 1).astype(int)
        time_on  = np.where(bounced,
                            rng.integers(5, 30, size=n),
                            rng.integers(45, 600, size=n))
        signed   = (rng.random(n) < signup_rate).astype(int)
        conv     = (rng.random(n) < conv_rate).astype(int)

        return pd.DataFrame({
            "session_id":        seq_ids("SES-", n, id_start),
            "date":              random_dates_in_range(week_start, week_end, n),
            "channel":           rng.choice(channels, size=n),
            "pages_viewed":      pages,
            "time_on_site_secs": time_on,
            "bounced":           bounced,
            "signed_up":         signed,
            "converted":         conv,
        })

    p1 = make_marketing_file(n1, date(2025, 4, 28), date(2025, 5, 4),
                             signup_rate=0.12, conv_rate=0.08, id_start=1)
    p2 = make_marketing_file(n2, date(2025, 5, 5),  date(2025, 5, 11),
                             signup_rate=0.06, conv_rate=0.04, id_start=n1 + 1)

    save(p1, "example2_marketing_metrics", "Marketing_week_apr28.xlsx")
    save(p2, "example2_marketing_metrics", "Marketing_week_may05.xlsx")


# ===========================================================================
# Example 3 — Revenue  (Payment transaction table, month-over-month)
# ===========================================================================
# Each row = one payment transaction.
# Key columns : transaction_id, date, product_line, amount_usd, status
# Engineered  : Product Line C has fewer and lower-value transactions in
#               Period 2, causing a ~30% revenue drop for that line.
#               Lines A and B remain stable.
# ===========================================================================

def create_example3():
    print("\n[Example 3] Revenue — payment transaction table")

    # Keep total rows ~50 per period but maintain the A/B/C split
    config = {
        "p1": {
            "Product Line A": (15, 800, 2200, 0.04),
            "Product Line B": (20, 350, 1000, 0.05),
            "Product Line C": (15,  80,  480, 0.06),
        },
        "p2": {
            "Product Line A": (15, 810, 2200, 0.04),
            "Product Line B": (19, 350,  980, 0.05),
            "Product Line C": (10,  75,  350, 0.10),   # fewer txns + lower amounts
        },
    }

    def make_revenue_file(period_config, month_start, month_end, id_start):
        rows = []
        txn_counter = id_start
        for pl, (n, lo, hi, refund_rate) in period_config.items():
            statuses = rng.choice(
                ["Completed", "Refunded", "Failed"],
                size=n,
                p=[1 - refund_rate - 0.02, refund_rate, 0.02],
            )
            amounts = rng.uniform(lo, hi, size=n).round(2)
            for i in range(n):
                rows.append({
                    "transaction_id": f"TXN-{str(txn_counter).zfill(5)}",
                    "date":           rng.choice(
                                          random_dates_in_range(month_start, month_end, 1)
                                      ),
                    "product_line":   pl,
                    "amount_usd":     amounts[i],
                    "status":         statuses[i],
                })
                txn_counter += 1

        df = pd.DataFrame(rows)
        return df.sample(frac=1, random_state=42).reset_index(drop=True)

    p1 = make_revenue_file(config["p1"], date(2025, 4, 1), date(2025, 4, 30), id_start=1)
    p2 = make_revenue_file(config["p2"], date(2025, 5, 1), date(2025, 5, 31), id_start=100)

    save(p1, "example3_revenue_mom", "Revenue_april_2025.xlsx")
    save(p2, "example3_revenue_mom", "Revenue_may_2025.xlsx")


# ===========================================================================
# Example 4 — Mixed Dataset  (Account records, month-over-month)
# ===========================================================================
# Each row = one account record.
# Key columns : record_id, account_name, status, volume, rate_pct, account_health_score, nps_score
# Engineered  : 8 of 40 accounts flip Active → Inactive in Period 2;
#               volume drops for those accounts; nps_score declines overall
# nps_score values are 0–10 raw survey ratings (Promoters 9–10, Passives 7–8, Detractors 0–6)
# ===========================================================================

def create_example4():
    print("\n[Example 4] Mixed Dataset — account records")

    n = 40

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
    ][:n]

    # 8 accounts flip to Inactive in Period 2
    inactive_idx = rng.choice(n, size=8, replace=False)
    status_p1 = ["Active"] * n
    status_p2 = ["Active"] * n
    for i in inactive_idx:
        status_p2[i] = "Inactive"

    volume_p1  = rng.integers(500, 9500, size=n)
    rate_p1    = rng.uniform(58, 88, size=n).round(1)
    health_p1  = rng.integers(55, 96, size=n)
    # NPS: 0–10 raw survey ratings per account (Promoters 9–10, Passives 7–8, Detractors 0–6)
    # Period 1: mostly Promoters and Passives
    nps_p1     = rng.choice([7, 8, 9, 9, 10, 10], size=n)

    vol_delta   = rng.integers(-400, 500, size=n)
    vol_delta[inactive_idx] = rng.integers(-2000, -800, size=len(inactive_idx))
    rate_delta  = rng.uniform(-4, 3, size=n).round(1)
    health_delta = rng.integers(-5, 4, size=n)
    # Period 2: NPS declines — inactive accounts pull down to Detractor range
    nps_p2      = nps_p1.copy()
    nps_p2      = rng.choice([7, 8, 9, 9, 10], size=n)          # base: slight drop
    nps_p2[inactive_idx] = rng.choice([0, 1, 2, 3, 4, 5, 6],    # inactive → Detractors
                                       size=len(inactive_idx))

    volume_p2      = (volume_p1 + vol_delta).clip(0)
    rate_p2        = (rate_p1 + rate_delta).clip(0, 100).round(1)
    health_p2      = (health_p1 + health_delta).clip(0, 100)

    def build_mixed(statuses, volumes, rates, health_scores, nps_vals):
        return pd.DataFrame({
            "record_id":            [f"ACC-{str(i).zfill(3)}" for i in range(1, n + 1)],
            "account_name":         account_names,
            "status":               statuses,
            "volume":               volumes,
            "rate_pct":             rates,
            "account_health_score": health_scores,
            "nps_score":            nps_vals,
        })

    p1 = build_mixed(status_p1, volume_p1, rate_p1, health_p1, nps_p1)
    p2 = build_mixed(status_p2, volume_p2, rate_p2, health_p2, nps_p2)

    save(p1, "example4_mixed", "Mixed_april_2025.xlsx")
    save(p2, "example4_mixed", "Mixed_may_2025.xlsx")


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
    print("  Example 1 — Product   : 50 rows/file  (payment transaction log)")
    print("  Example 2 — Marketing : 50 / 65 rows  (session log)")
    print("  Example 3 — Revenue   : ~50 rows/file (payment transaction table)")
    print("  Example 4 — Mixed     : 40 rows/file  (account records)")
