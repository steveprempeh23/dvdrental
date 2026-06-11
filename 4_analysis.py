"""
4_analysis.py  —  DSA5102 Big Data Management Capstone
Advanced Business Analysis Script
Author: Steve Prempeh

Covers all four exam themes:
  Part D1 - Customer Analytics      (12 marks)
  Part D2 - Revenue Optimisation    (12 marks)
  Part D3 - Inventory & Operations  (12 marks)
  Part D4 - Innovation / Custom     ( 9 marks)

Run AFTER:
  1_setup_validate.py
  2_data_exploration.py
  3_data_relationships.py

Outputs written to:
  tables/   — CSV analysis results
  results/  — PNG chart files
  exports/  — Text summary reports
"""

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
#  SETUP
# ─────────────────────────────────────────────
load_dotenv()

DB_USER = os.getenv("POSTGRES_USER",     "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "your_secure_password")
DB_NAME = os.getenv("POSTGRES_DB",       "dvd_rental")
DB_HOST = os.getenv("POSTGRES_HOST",     "localhost")
DB_PORT = os.getenv("POSTGRES_PORT",     "5432")

ENGINE = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

for folder in ["tables", "results", "exports", "merges"]:
    os.makedirs(folder, exist_ok=True)

PALETTE = ["#e94560", "#4299e1", "#ed8936", "#68d391", "#9f7aea",
           "#f6ad55", "#fc8181", "#63b3ed", "#76e4f7", "#b794f4"]

sns.set_theme(style="whitegrid", palette=PALETTE)
plt.rcParams.update({"figure.dpi": 120, "font.size": 10})

insights = []


def query(sql: str) -> pd.DataFrame:
    with ENGINE.connect() as conn:
        return pd.read_sql(text(sql), conn)


def save_fig(name: str):
    path = os.path.join("results", f"{name}.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"  Chart saved: {path}")


def log(msg: str):
    print(msg)
    insights.append(msg)


print("=" * 60)
print("4_analysis.py  —  Advanced Business Analysis")
print("=" * 60)


# ═══════════════════════════════════════════════════════════
#  PART D1 — CUSTOMER ANALYTICS (12 marks)
#  - Customer Lifetime Value (CLV)
#  - Segmentation
#  - Churn Risk
#  - Behavioural Patterns
# ═══════════════════════════════════════════════════════════
print("\n── PART D1: Customer Analytics ──")

# ── D1.1  Customer Lifetime Value ──────────────────────────
clv_sql = """
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name          AS customer_name,
    c.store_id,
    c.active,
    COUNT(DISTINCT p.payment_id)                AS total_payments,
    ROUND(SUM(p.amount)::numeric, 2)            AS lifetime_value,
    ROUND(AVG(p.amount)::numeric, 4)            AS avg_payment,
    MIN(p.payment_date)::date                   AS first_payment_date,
    MAX(p.payment_date)::date                   AS last_payment_date,
    EXTRACT(EPOCH FROM (MAX(p.payment_date) - MIN(p.payment_date)))
        / 86400.0                               AS active_days,
    COUNT(DISTINCT r.rental_id)                 AS total_rentals
FROM customer c
JOIN payment  p ON c.customer_id = p.customer_id
JOIN rental   r ON p.rental_id   = r.rental_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.store_id, c.active
ORDER BY lifetime_value DESC
"""
clv_df = query(clv_sql)

# Annualised CLV = (total_value / active_days) * 365
clv_df["active_days"] = clv_df["active_days"].fillna(1).clip(lower=1)
clv_df["annualised_clv"] = (
    clv_df["lifetime_value"] / clv_df["active_days"] * 365
).round(2)

# Tertile segmentation
clv_df["segment"] = pd.qcut(
    clv_df["lifetime_value"],
    q=3,
    labels=["Low Value", "Mid Value", "High Value"]
)

clv_df.to_csv("tables/customer_clv.csv", index=False)
log(f"CLV — {len(clv_df)} customers analysed.")
log(f"CLV — Top customer: {clv_df.iloc[0]['customer_name']} "
    f"(${clv_df.iloc[0]['lifetime_value']:.2f})")
log(f"CLV — Average LTV: ${clv_df['lifetime_value'].mean():.2f}")
log(f"CLV — Average annualised CLV: ${clv_df['annualised_clv'].mean():.2f}/year")

# Chart 1: CLV distribution by segment
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

seg_rev = clv_df.groupby("segment")["lifetime_value"].sum().reset_index()
axes[0].bar(seg_rev["segment"], seg_rev["lifetime_value"],
            color=PALETTE[:3], edgecolor="white", linewidth=0.8)
axes[0].set_title("Total Revenue by Customer Segment", fontweight="bold")
axes[0].set_xlabel("Segment")
axes[0].set_ylabel("Total Revenue ($)")
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
for bar, val in zip(axes[0].patches, seg_rev["lifetime_value"]):
    axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 50,
                 f"${val:,.0f}", ha="center", va="bottom", fontsize=9)

axes[1].hist(clv_df["lifetime_value"], bins=30, color=PALETTE[1],
             edgecolor="white", linewidth=0.5)
axes[1].axvline(clv_df["lifetime_value"].mean(), color=PALETTE[0],
                linestyle="--", linewidth=1.5, label=f"Mean ${clv_df['lifetime_value'].mean():.2f}")
axes[1].set_title("Customer Lifetime Value Distribution", fontweight="bold")
axes[1].set_xlabel("Lifetime Value ($)")
axes[1].set_ylabel("Number of Customers")
axes[1].legend()

plt.suptitle("Customer Lifetime Value Analysis", fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
save_fig("d1_customer_lifetime_value")

# ── D1.2  Customer Segmentation table ──────────────────────
seg_summary = clv_df.groupby("segment").agg(
    customer_count=("customer_id", "count"),
    total_revenue=("lifetime_value", "sum"),
    avg_ltv=("lifetime_value", "mean"),
    avg_annualised_clv=("annualised_clv", "mean"),
    avg_payments=("total_payments", "mean"),
    avg_rentals=("total_rentals", "mean")
).round(2).reset_index()
seg_summary.to_csv("tables/customer_segments.csv", index=False)

for _, row in seg_summary.iterrows():
    log(f"Segment '{row['segment']}': {int(row['customer_count'])} customers, "
        f"avg LTV ${row['avg_ltv']:.2f}, total revenue ${row['total_revenue']:,.2f}")

# ── D1.3  Churn Risk Scoring ────────────────────────────────
max_date = pd.to_datetime(clv_df["last_payment_date"]).max()
clv_df["days_inactive"] = (
    max_date - pd.to_datetime(clv_df["last_payment_date"])
).dt.days

# Normalised RFM-inspired churn score
clv_df["recency_norm"] = clv_df["days_inactive"].clip(0, 180) / 180
clv_df["freq_norm"]    = 1 - (clv_df["total_rentals"].clip(0, 50) / 50)
clv_df["spend_norm"]   = 1 - (clv_df["lifetime_value"].clip(0, 200) / 200)
clv_df["churn_score"]  = (
    0.50 * clv_df["recency_norm"] +
    0.30 * clv_df["freq_norm"]    +
    0.20 * clv_df["spend_norm"]
).round(4)

clv_df["churn_risk"] = pd.cut(
    clv_df["churn_score"],
    bins=[0, 0.33, 0.60, 1.01],
    labels=["Low Risk", "Medium Risk", "High Risk"],
    include_lowest=True
)

churn_df = clv_df[["customer_id", "customer_name", "store_id", "segment",
                    "lifetime_value", "total_rentals", "days_inactive",
                    "churn_score", "churn_risk"]].copy()
churn_df.to_csv("tables/churn_risk_customers.csv", index=False)

risk_counts = clv_df["churn_risk"].value_counts()
for risk, count in risk_counts.items():
    log(f"Churn Risk — {risk}: {count} customers")

high_risk_count = (clv_df["churn_risk"] == "High Risk").sum()
log(f"Churn — {high_risk_count} customers are High Risk and need immediate re-engagement.")

# Chart 2: Churn risk
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

risk_labels = risk_counts.index.tolist()
risk_values = risk_counts.values.tolist()
risk_colors = {"Low Risk": "#68d391", "Medium Risk": "#ed8936", "High Risk": "#e94560"}
bar_colors = [risk_colors.get(r, "#aaa") for r in risk_labels]

axes[0].bar(risk_labels, risk_values, color=bar_colors, edgecolor="white")
axes[0].set_title("Customer Count by Churn Risk", fontweight="bold")
axes[0].set_xlabel("Risk Category")
axes[0].set_ylabel("Number of Customers")
for bar, val in zip(axes[0].patches, risk_values):
    axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                 str(val), ha="center", va="bottom", fontsize=10)

axes[1].scatter(clv_df["lifetime_value"], clv_df["churn_score"],
                c=[risk_colors.get(str(r), "#aaa") for r in clv_df["churn_risk"]],
                alpha=0.5, s=20)
axes[1].axhline(0.60, color="#e94560", linestyle="--", linewidth=1.2,
                label="High Risk threshold (0.60)")
axes[1].set_title("Churn Score vs Lifetime Value", fontweight="bold")
axes[1].set_xlabel("Lifetime Value ($)")
axes[1].set_ylabel("Churn Score")
axes[1].legend()

plt.suptitle("Customer Churn Risk Analysis", fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
save_fig("d1_churn_risk")

# ── D1.4  Behavioural Patterns ──────────────────────────────
behaviour_sql = """
SELECT
    c.customer_id,
    COUNT(r.rental_id)                                           AS rental_count,
    ROUND(AVG(
        EXTRACT(EPOCH FROM (r.return_date - r.rental_date)) / 86400.0
    )::numeric, 2)                                               AS avg_rental_duration_days,
    COUNT(DISTINCT fc.category_id)                               AS distinct_categories_rented,
    MODE() WITHIN GROUP (ORDER BY cat.name)                      AS favourite_category,
    EXTRACT(DOW FROM MIN(r.rental_date))::int                    AS most_common_rental_dow
FROM customer c
JOIN rental        r   ON c.customer_id  = r.customer_id
JOIN inventory     i   ON r.inventory_id = i.inventory_id
JOIN film          f   ON i.film_id      = f.film_id
JOIN film_category fc  ON f.film_id      = fc.film_id
JOIN category      cat ON fc.category_id = cat.category_id
WHERE r.return_date IS NOT NULL
GROUP BY c.customer_id
ORDER BY rental_count DESC
"""
behaviour_df = query(behaviour_sql)
behaviour_df.to_csv("tables/customer_behavioural_patterns.csv", index=False)

log(f"Behaviour — Avg rentals per customer: {behaviour_df['rental_count'].mean():.1f}")
log(f"Behaviour — Avg rental duration: {behaviour_df['avg_rental_duration_days'].mean():.1f} days")
log(f"Behaviour — Avg distinct categories per customer: {behaviour_df['distinct_categories_rented'].mean():.1f}")
top_fav = behaviour_df["favourite_category"].value_counts().idxmax()
log(f"Behaviour — Most common favourite category: {top_fav}")

# Chart 3: Rental frequency histogram
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].hist(behaviour_df["rental_count"], bins=25,
             color=PALETTE[1], edgecolor="white", linewidth=0.5)
axes[0].axvline(behaviour_df["rental_count"].mean(), color=PALETTE[0],
                linestyle="--", linewidth=1.5,
                label=f"Mean {behaviour_df['rental_count'].mean():.1f}")
axes[0].set_title("Rental Frequency per Customer", fontweight="bold")
axes[0].set_xlabel("Number of Rentals")
axes[0].set_ylabel("Number of Customers")
axes[0].legend()

fav_cat = behaviour_df["favourite_category"].value_counts().head(10)
axes[1].barh(fav_cat.index[::-1], fav_cat.values[::-1], color=PALETTE[2])
axes[1].set_title("Top 10 Favourite Categories (Most Customers)", fontweight="bold")
axes[1].set_xlabel("Number of Customers")

plt.suptitle("Customer Behavioural Patterns", fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
save_fig("d1_behavioural_patterns")


# ═══════════════════════════════════════════════════════════
#  PART D2 — REVENUE OPTIMISATION (12 marks)
#  - Category performance
#  - Temporal trends
#  - Pricing insights
# ═══════════════════════════════════════════════════════════
print("\n── PART D2: Revenue Optimisation ──")

# ── D2.1  Revenue by Category ──────────────────────────────
cat_sql = """
SELECT
    cat.name                                               AS category,
    COUNT(DISTINCT r.rental_id)                            AS total_rentals,
    ROUND(SUM(p.amount)::numeric, 2)                       AS total_revenue,
    ROUND(AVG(p.amount)::numeric, 4)                       AS avg_payment,
    ROUND(AVG(f.rental_rate)::numeric, 4)                  AS avg_rental_rate,
    ROUND(SUM(p.amount)::numeric / NULLIF(COUNT(r.rental_id), 0), 4)
                                                           AS revenue_per_rental,
    COUNT(DISTINCT f.film_id)                              AS film_count,
    COUNT(DISTINCT p.customer_id)                          AS unique_customers
FROM payment p
JOIN rental        r   ON p.rental_id    = r.rental_id
JOIN inventory     i   ON r.inventory_id = i.inventory_id
JOIN film          f   ON i.film_id      = f.film_id
JOIN film_category fc  ON f.film_id      = fc.film_id
JOIN category      cat ON fc.category_id = cat.category_id
GROUP BY cat.name
ORDER BY total_revenue DESC
"""
cat_df = query(cat_sql)
cat_df.to_csv("tables/revenue_by_category.csv", index=False)

log(f"Revenue — Top category: {cat_df.iloc[0]['category']} "
    f"(${cat_df.iloc[0]['total_revenue']:,.2f})")
log(f"Revenue — Bottom category: {cat_df.iloc[-1]['category']} "
    f"(${cat_df.iloc[-1]['total_revenue']:,.2f})")
log(f"Revenue — Best revenue/rental: "
    f"{cat_df.sort_values('revenue_per_rental', ascending=False).iloc[0]['category']}")

# Chart 4: Category revenue
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

cat_sorted = cat_df.sort_values("total_revenue")
colors = plt.cm.RdYlGn(
    np.linspace(0.2, 0.9, len(cat_sorted))
)
axes[0].barh(cat_sorted["category"], cat_sorted["total_revenue"],
             color=colors, edgecolor="white", linewidth=0.5)
axes[0].set_title("Total Revenue by Film Category", fontweight="bold")
axes[0].set_xlabel("Total Revenue ($)")
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

scatter_colors = [PALETTE[i % len(PALETTE)] for i in range(len(cat_df))]
axes[1].scatter(cat_df["total_rentals"], cat_df["revenue_per_rental"],
                s=cat_df["total_revenue"] / 100,
                c=scatter_colors, alpha=0.8)
for _, row in cat_df.iterrows():
    axes[1].annotate(row["category"],
                     (row["total_rentals"], row["revenue_per_rental"]),
                     fontsize=7, ha="left", va="bottom",
                     xytext=(3, 3), textcoords="offset points")
axes[1].set_title("Rentals vs Revenue per Rental\n(bubble = total revenue)", fontweight="bold")
axes[1].set_xlabel("Total Rentals")
axes[1].set_ylabel("Revenue per Rental ($)")

plt.suptitle("Revenue Analysis by Film Category", fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
save_fig("d2_revenue_by_category")

# ── D2.2  Temporal Revenue Trends ──────────────────────────
temporal_sql = """
SELECT
    DATE_TRUNC('month', payment_date)       AS month_date,
    TO_CHAR(payment_date, 'Mon YYYY')       AS month_label,
    EXTRACT(MONTH FROM payment_date)::int   AS month_num,
    EXTRACT(YEAR  FROM payment_date)::int   AS year_num,
    ROUND(SUM(amount)::numeric, 2)          AS revenue,
    COUNT(payment_id)                       AS transactions,
    COUNT(DISTINCT customer_id)             AS active_customers,
    ROUND(AVG(amount)::numeric, 4)          AS avg_payment
FROM payment
GROUP BY 1, 2, 3, 4
ORDER BY 1
"""
temporal_df = query(temporal_sql)
temporal_df["month_date"] = pd.to_datetime(temporal_df["month_date"])
temporal_df.to_csv("tables/monthly_revenue_trends.csv", index=False)

peak_month = temporal_df.loc[temporal_df["revenue"].idxmax()]
log(f"Temporal — Peak revenue month: {peak_month['month_label']} "
    f"(${peak_month['revenue']:,.2f})")
log(f"Temporal — Total months of data: {len(temporal_df)}")

# Seasonality: average daily revenue by calendar month
seasonal_sql = """
SELECT
    EXTRACT(MONTH FROM day)::int  AS month_num,
    TO_CHAR(day, 'Mon')           AS month_name,
    ROUND(AVG(daily_rev), 2)      AS avg_daily_revenue
FROM (
    SELECT
        DATE_TRUNC('day', payment_date) AS day,
        SUM(amount)                     AS daily_rev
    FROM payment
    GROUP BY 1
) sub
GROUP BY 1, 2
ORDER BY 1
"""
seasonal_df = query(seasonal_sql)
seasonal_df.to_csv("tables/seasonal_revenue_pattern.csv", index=False)

# Chart 5: Temporal trends
fig, axes = plt.subplots(2, 1, figsize=(12, 8))

axes[0].fill_between(temporal_df["month_date"], temporal_df["revenue"],
                     alpha=0.3, color=PALETTE[0])
axes[0].plot(temporal_df["month_date"], temporal_df["revenue"],
             color=PALETTE[0], linewidth=2)
ax2 = axes[0].twinx()
ax2.plot(temporal_df["month_date"], temporal_df["transactions"],
         color=PALETTE[1], linewidth=1.5, linestyle="--", alpha=0.8)
ax2.set_ylabel("Transactions", color=PALETTE[1])
axes[0].set_title("Monthly Revenue and Transaction Volume", fontweight="bold")
axes[0].set_ylabel("Revenue ($)")
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

axes[1].bar(seasonal_df["month_name"], seasonal_df["avg_daily_revenue"],
            color=PALETTE[2], edgecolor="white")
axes[1].set_title("Average Daily Revenue by Month (Seasonality)", fontweight="bold")
axes[1].set_xlabel("Month")
axes[1].set_ylabel("Avg Daily Revenue ($)")
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

plt.suptitle("Revenue Temporal Analysis", fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
save_fig("d2_temporal_revenue_trends")

# ── D2.3  Pricing Insight ──────────────────────────────────
pricing_sql = """
SELECT
    f.title,
    cat.name                                   AS category,
    f.rental_rate,
    f.replacement_cost,
    COUNT(r.rental_id)                         AS total_rentals,
    ROUND(SUM(p.amount)::numeric, 2)           AS total_revenue,
    ROUND(SUM(p.amount)::numeric
          / NULLIF(COUNT(r.rental_id), 0), 4)  AS revenue_per_rental
FROM film          f
JOIN film_category fc  ON f.film_id      = fc.film_id
JOIN category      cat ON fc.category_id = cat.category_id
JOIN inventory     i   ON f.film_id      = i.film_id
LEFT JOIN rental   r   ON i.inventory_id = r.inventory_id
LEFT JOIN payment  p   ON r.rental_id    = p.rental_id
GROUP BY f.film_id, f.title, cat.name, f.rental_rate, f.replacement_cost
HAVING COUNT(r.rental_id) > 0
ORDER BY revenue_per_rental DESC
"""
pricing_df = query(pricing_sql)
pricing_df.to_csv("tables/pricing_insight.csv", index=False)

corr = pricing_df["rental_rate"].corr(pricing_df["total_rentals"])
log(f"Pricing — Correlation between rental rate and total rentals: {corr:.4f}")
log(f"Pricing — Avg rental rate: ${pricing_df['rental_rate'].mean():.2f}")
log(f"Pricing — Top revenue/rental film: {pricing_df.iloc[0]['title']} "
    f"(${pricing_df.iloc[0]['revenue_per_rental']:.2f}/rental)")


# ═══════════════════════════════════════════════════════════
#  PART D3 — INVENTORY & OPERATIONS (12 marks)
#  - Inventory turnover rate
#  - Slow-moving inventory
#  - Store comparison
# ═══════════════════════════════════════════════════════════
print("\n── PART D3: Inventory & Operations ──")

# ── D3.1  Inventory Turnover ───────────────────────────────
inv_sql = """
SELECT
    i.inventory_id,
    i.store_id,
    f.film_id,
    f.title,
    f.rental_rate,
    f.replacement_cost,
    cat.name                                           AS category,
    COUNT(r.rental_id)                                 AS rental_count,
    ROUND(COALESCE(SUM(p.amount), 0)::numeric, 2)     AS total_revenue,
    MAX(r.rental_date)::date                           AS last_rental_date
FROM inventory     i
JOIN film          f   ON i.film_id      = f.film_id
JOIN film_category fc  ON f.film_id      = fc.film_id
JOIN category      cat ON fc.category_id = cat.category_id
LEFT JOIN rental   r   ON i.inventory_id = r.inventory_id
LEFT JOIN payment  p   ON r.rental_id    = p.rental_id
GROUP BY i.inventory_id, i.store_id, f.film_id, f.title,
         f.rental_rate, f.replacement_cost, cat.name
"""
inv_df = query(inv_sql)

# Inventory turnover rate = total rentals / total copies per film
turnover_df = inv_df.groupby(["film_id", "title", "category"]).agg(
    total_copies=("inventory_id", "count"),
    total_rentals=("rental_count", "sum"),
    total_revenue=("total_revenue", "sum"),
    avg_rental_rate=("rental_rate", "mean")
).reset_index()
turnover_df["turnover_rate"] = (
    turnover_df["total_rentals"] / turnover_df["total_copies"]
).round(2)
turnover_df = turnover_df.sort_values("turnover_rate", ascending=False)
turnover_df.to_csv("tables/inventory_turnover.csv", index=False)

avg_turnover = turnover_df["turnover_rate"].mean()
log(f"Inventory — Total inventory items: {len(inv_df)}")
log(f"Inventory — Average turnover rate: {avg_turnover:.2f} rentals per copy")
log(f"Inventory — Zero-rental items: {(inv_df['rental_count'] == 0).sum()}")
log(f"Inventory — Slow-moving (<3 rentals): {(inv_df['rental_count'] < 3).sum()}")

# Turnover by category
cat_turnover = inv_df.groupby("category").agg(
    avg_turnover=("rental_count", "mean"),
    total_copies=("inventory_id", "count"),
    dead_stock=("rental_count", lambda x: (x == 0).sum())
).round(2).reset_index().sort_values("avg_turnover", ascending=False)
cat_turnover.to_csv("tables/inventory_turnover_by_category.csv", index=False)

# Slow-moving inventory
slow_df = inv_df[inv_df["rental_count"] < 3].sort_values("rental_count")
slow_df.to_csv("tables/slow_moving_inventory.csv", index=False)
log(f"Inventory — Slow-moving items exported: {len(slow_df)}")

# Chart 6: Inventory turnover
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].barh(cat_turnover["category"], cat_turnover["avg_turnover"],
             color=PALETTE[3], edgecolor="white")
axes[0].axvline(avg_turnover, color=PALETTE[0], linestyle="--",
                linewidth=1.5, label=f"Overall avg {avg_turnover:.1f}")
axes[0].set_title("Avg Inventory Turnover Rate by Category\n(rentals per copy)", fontweight="bold")
axes[0].set_xlabel("Avg Rentals per Copy")
axes[0].legend()

axes[1].hist(inv_df["rental_count"], bins=30,
             color=PALETTE[1], edgecolor="white", linewidth=0.5)
axes[1].axvline(avg_turnover, color=PALETTE[0], linestyle="--",
                linewidth=1.5, label=f"Avg {avg_turnover:.1f}")
axes[1].set_title("Inventory Turnover Distribution\n(all copies)", fontweight="bold")
axes[1].set_xlabel("Rentals per Copy")
axes[1].set_ylabel("Number of Copies")
axes[1].legend()

plt.suptitle("Inventory Turnover Analysis", fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
save_fig("d3_inventory_turnover")

# ── D3.2  Store Performance Comparison ────────────────────
store_sql = """
SELECT
    s.store_id,
    COUNT(DISTINCT c.customer_id)          AS total_customers,
    COUNT(DISTINCT i.inventory_id)         AS total_inventory,
    COUNT(DISTINCT r.rental_id)            AS total_rentals,
    ROUND(SUM(p.amount)::numeric, 2)       AS total_revenue
FROM store      s
LEFT JOIN customer  c ON s.store_id      = c.store_id
LEFT JOIN inventory i ON s.store_id      = i.store_id
LEFT JOIN rental    r ON i.inventory_id  = r.inventory_id
LEFT JOIN payment   p ON r.rental_id     = p.rental_id
GROUP BY s.store_id
ORDER BY s.store_id
"""
store_df = query(store_sql)
store_df["revenue_per_inventory"] = (
    store_df["total_revenue"] / store_df["total_inventory"]
).round(2)
store_df["rentals_per_inventory"] = (
    store_df["total_rentals"] / store_df["total_inventory"]
).round(2)
store_df["revenue_per_customer"] = (
    store_df["total_revenue"] / store_df["total_customers"]
).round(2)
store_df.to_csv("tables/store_performance.csv", index=False)

for _, row in store_df.iterrows():
    log(f"Store {int(row['store_id'])} — Revenue: ${row['total_revenue']:,.2f} | "
        f"Customers: {int(row['total_customers'])} | "
        f"Rev/Inventory: ${row['revenue_per_inventory']:.2f} | "
        f"Rev/Customer: ${row['revenue_per_customer']:.2f}")

# Chart 7: Store comparison
metrics = ["total_revenue", "total_rentals", "total_customers",
           "total_inventory", "revenue_per_inventory", "rentals_per_inventory"]
labels = ["Revenue ($)", "Rentals", "Customers",
          "Inventory", "Rev/Item ($)", "Rentals/Item"]

fig, axes = plt.subplots(2, 3, figsize=(14, 8))
axes = axes.flatten()

for idx, (metric, label) in enumerate(zip(metrics, labels)):
    vals = store_df[metric].tolist()
    bar_labels = [f"Store {int(s)}" for s in store_df["store_id"]]
    axes[idx].bar(bar_labels, vals, color=[PALETTE[0], PALETTE[1]],
                  edgecolor="white")
    axes[idx].set_title(label, fontweight="bold")
    for bar, val in zip(axes[idx].patches, vals):
        axes[idx].text(bar.get_x() + bar.get_width() / 2,
                       bar.get_height() * 0.97,
                       f"{val:,.1f}", ha="center", va="top",
                       fontsize=9, color="white", fontweight="bold")

plt.suptitle("Store Performance Comparison", fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
save_fig("d3_store_comparison")


# ═══════════════════════════════════════════════════════════
#  PART D4 — INNOVATION / CUSTOM ANALYSIS (9 marks)
#  - Category recommendation engine (priority scoring)
#  - Churn prediction model summary
# ═══════════════════════════════════════════════════════════
print("\n── PART D4: Innovation & Custom Analysis ──")

# ── D4.1  Recommendation Engine ───────────────────────────
rec_df = cat_df.copy()

# Normalise revenue and rental volume to 0–1
rec_df["rev_score"]  = (
    (rec_df["total_revenue"] - rec_df["total_revenue"].min()) /
    (rec_df["total_revenue"].max() - rec_df["total_revenue"].min())
)
rec_df["rent_score"] = (
    (rec_df["total_rentals"] - rec_df["total_rentals"].min()) /
    (rec_df["total_rentals"].max() - rec_df["total_rentals"].min())
)
rec_df["priority_score"] = (
    0.60 * rec_df["rev_score"] + 0.40 * rec_df["rent_score"]
).round(4)
rec_df["recommendation_priority"] = pd.cut(
    rec_df["priority_score"],
    bins=3,
    labels=["Low Priority", "Medium Priority", "High Priority"]
)
rec_df = rec_df.sort_values("priority_score", ascending=False)
rec_df.to_csv("tables/recommendation_candidates.csv", index=False)

high_priority = rec_df[rec_df["recommendation_priority"] == "High Priority"]["category"].tolist()
log(f"Recommendation — High Priority categories: {', '.join(high_priority)}")
log("Recommendation — Score = 60% normalised revenue + 40% normalised rental volume")

# Chart 8: Recommendation priority
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

priority_colors = {
    "High Priority": PALETTE[0],
    "Medium Priority": PALETTE[2],
    "Low Priority": PALETTE[1]
}
bar_colors = [priority_colors.get(str(p), "#aaa")
              for p in rec_df["recommendation_priority"]]

axes[0].barh(rec_df["category"], rec_df["priority_score"],
             color=bar_colors, edgecolor="white")
axes[0].set_title("Category Recommendation Priority Score", fontweight="bold")
axes[0].set_xlabel("Priority Score (0–1)")
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=v, label=k)
                   for k, v in priority_colors.items()]
axes[0].legend(handles=legend_elements, loc="lower right")

scatter_colors_rec = [priority_colors.get(str(p), "#aaa")
                      for p in rec_df["recommendation_priority"]]
axes[1].scatter(rec_df["unique_customers"], rec_df["total_revenue"],
                s=rec_df["total_rentals"] / 5,
                c=scatter_colors_rec, alpha=0.8)
for _, row in rec_df.iterrows():
    axes[1].annotate(row["category"],
                     (row["unique_customers"], row["total_revenue"]),
                     fontsize=7, xytext=(3, 3), textcoords="offset points")
axes[1].set_title("Revenue vs Customer Reach\n(bubble = rental volume)", fontweight="bold")
axes[1].set_xlabel("Unique Customers Who Rented")
axes[1].set_ylabel("Total Revenue ($)")
axes[1].legend(handles=legend_elements)

plt.suptitle("Category-Based Recommendation Engine", fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
save_fig("d4_recommendation_engine")

# ── D4.2  Churn Prediction Model Summary ──────────────────
churn_summary = clv_df.groupby("churn_risk").agg(
    count=("customer_id", "count"),
    avg_lifetime_value=("lifetime_value", "mean"),
    avg_churn_score=("churn_score", "mean"),
    avg_days_inactive=("days_inactive", "mean"),
    avg_rentals=("total_rentals", "mean")
).round(2).reset_index()
churn_summary.to_csv("tables/churn_model_summary.csv", index=False)
log("Churn Model — Feature weights: Recency 50%, Frequency 30%, Spend 20%")


# ═══════════════════════════════════════════════════════════
#  EXPORT BUSINESS INSIGHTS SUMMARY
# ═══════════════════════════════════════════════════════════
print("\n── Writing Business Insights Summary ──")

summary_path = os.path.join("exports", "business_insights_summary.txt")
with open(summary_path, "w") as f:
    f.write("=" * 60 + "\n")
    f.write("BUSINESS INSIGHTS SUMMARY\n")
    f.write("DVD Rental Analytics — DSA5102 Capstone\n")
    f.write("Author: Steve Prempeh\n")
    f.write("=" * 60 + "\n\n")

    f.write("CUSTOMER ANALYTICS\n")
    f.write("-" * 40 + "\n")
    for i in insights:
        if any(k in i for k in ["CLV", "Segment", "Churn", "Behaviour"]):
            f.write(f"  • {i}\n")
    f.write("\nREVENUE OPTIMISATION\n")
    f.write("-" * 40 + "\n")
    for i in insights:
        if any(k in i for k in ["Revenue", "Temporal", "Pricing", "category"]):
            f.write(f"  • {i}\n")
    f.write("\nINVENTORY & OPERATIONS\n")
    f.write("-" * 40 + "\n")
    for i in insights:
        if any(k in i for k in ["Inventory", "Store", "turnover", "slow"]):
            f.write(f"  • {i}\n")
    f.write("\nINNOVATION\n")
    f.write("-" * 40 + "\n")
    for i in insights:
        if any(k in i for k in ["Recommendation", "Churn Model"]):
            f.write(f"  • {i}\n")

    f.write("\n" + "=" * 60 + "\n")
    f.write("KEY RECOMMENDATIONS\n")
    f.write("=" * 60 + "\n")
    recommendations = [
        "Protect High-Value customers with a loyalty programme (early access, personalised discounts).",
        "Re-engage High Risk churn customers immediately with a time-limited discount campaign.",
        f"Prioritise stock investment and promotion in High Priority categories: {', '.join(high_priority)}.",
        f"Review or retire the {(inv_df['rental_count'] == 0).sum()} inventory items with zero rentals.",
        "Rebalance inventory between stores based on revenue-per-inventory-item efficiency ratios.",
        "Run promotional campaigns during peak seasonal months identified in the temporal analysis.",
        "Extend the recommendation engine to customer-level collaborative filtering as a next step.",
    ]
    for i, rec in enumerate(recommendations, 1):
        f.write(f"  {i}. {rec}\n")

print(f"  Summary saved: {summary_path}")

# ── Final output manifest ──────────────────────────────────
print("\n" + "=" * 60)
print("OUTPUTS GENERATED")
print("=" * 60)
all_outputs = (
    [f"tables/{f}" for f in os.listdir("tables") if f.endswith(".csv")] +
    [f"results/{f}" for f in os.listdir("results") if f.endswith(".png")] +
    [f"exports/{f}" for f in os.listdir("exports")]
)
for o in sorted(all_outputs):
    print(f"  ✓ {o}")

print("\n4_analysis.py complete.")