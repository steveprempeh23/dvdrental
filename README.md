"""
5_dashboard.py  –  DSA5102 Big Data Management Capstone
DVD Rental Analytics Dashboard
Author: Steve Prempeh

Answers all 8 analytical questions across 4 exam themes:
  Customer Intelligence  |  Revenue Optimisation
  Inventory & Operations |  Innovation / Recommendation

Run:
    streamlit run 5_dashboard.py
"""

import os
import warnings
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="DVD Rental Analytics",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL STYLE
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.kpi-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 12px;
    padding: 20px 24px;
    border-left: 4px solid #e94560;
    color: #ffffff;
    text-align: center;
    margin-bottom: 8px;
}
.kpi-label { font-size: 11px; color: #a0aec0; text-transform: uppercase; letter-spacing: 1.2px; font-weight: 600; }
.kpi-value { font-size: 30px; font-weight: 700; color: #ffffff; margin-top: 4px; }
.kpi-delta { font-size: 12px; color: #68d391; margin-top: 2px; }

.section-header {
    font-size: 13px;
    font-weight: 600;
    color: #e94560;
    text-transform: uppercase;
    letter-spacing: 1px;
    border-bottom: 1px solid #2d3748;
    padding-bottom: 6px;
    margin-bottom: 16px;
}

.insight-box {
    background: #f7fafc;
    border-left: 4px solid #4299e1;
    border-radius: 6px;
    padding: 12px 16px;
    font-size: 13px;
    color: #2d3748;
    margin-top: 8px;
}

div[data-testid="stSidebar"] { background-color: #1a1a2e; }
div[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  DATABASE CONNECTION
# ─────────────────────────────────────────────
@st.cache_resource
def get_engine():
    load_dotenv()
    user     = os.getenv("POSTGRES_USER",     "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "your_secure_password")
    db       = os.getenv("POSTGRES_DB",       "dvd_rental")
    host     = os.getenv("POSTGRES_HOST",     "localhost")
    port     = os.getenv("POSTGRES_PORT",     "5432")
    return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")


@st.cache_data(ttl=300)
def run_query(sql: str) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)


# ─────────────────────────────────────────────
#  HELPER: KPI card
# ─────────────────────────────────────────────
def kpi(label, value, delta=""):
    delta_html = f'<div class="kpi-delta">{delta}</div>' if delta else ""
    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'{delta_html}</div>',
        unsafe_allow_html=True,
    )


def section(title):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def insight(text_body):
    st.markdown(f'<div class="insight-box">💡 {text_body}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎬 DVD Rental")
    st.markdown("**DSA5102 Analytics Dashboard**")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        [
            "📊 Executive Overview",
            "👥 Customer Intelligence",
            "💰 Revenue Optimisation",
            "📦 Inventory & Operations",
            "🤖 Innovation & Recommendations",
        ],
    )
    st.markdown("---")
    st.caption("Data: PostgreSQL dvdrental  \nAuthor: Steve Prempeh")


# ══════════════════════════════════════════════
#  PAGE 1 – EXECUTIVE OVERVIEW
# ══════════════════════════════════════════════
if page == "📊 Executive Overview":
    st.title("📊 Executive Overview")
    st.markdown("High-level performance snapshot across the DVD rental business.")
    st.markdown("---")

    # ── KPI data ──
    kpi_sql = """
    SELECT
        COUNT(DISTINCT c.customer_id)            AS total_customers,
        COUNT(DISTINCT f.film_id)                AS total_films,
        COUNT(DISTINCT r.rental_id)              AS total_rentals,
        ROUND(SUM(p.amount)::numeric, 2)         AS total_revenue,
        ROUND(AVG(p.amount)::numeric, 4)         AS avg_payment,
        COUNT(DISTINCT s.store_id)               AS total_stores,
        COUNT(DISTINCT i.inventory_id)           AS total_inventory
    FROM payment p
    JOIN rental   r ON p.rental_id    = r.rental_id
    JOIN customer c ON p.customer_id  = c.customer_id
    JOIN inventory i ON r.inventory_id = i.inventory_id
    JOIN film      f ON i.film_id      = f.film_id
    JOIN store     s ON i.store_id     = s.store_id
    """
    try:
        kdf = run_query(kpi_sql).iloc[0]

        c1, c2, c3, c4 = st.columns(4)
        with c1: kpi("Total Revenue", f"${kdf['total_revenue']:,.2f}")
        with c2: kpi("Total Rentals", f"{int(kdf['total_rentals']):,}")
        with c3: kpi("Total Customers", f"{int(kdf['total_customers']):,}")
        with c4: kpi("Avg Payment", f"${float(kdf['avg_payment']):.2f}")

        c5, c6, c7, _ = st.columns(4)
        with c5: kpi("Films in Catalogue", f"{int(kdf['total_films']):,}")
        with c6: kpi("Inventory Items", f"{int(kdf['total_inventory']):,}")
        with c7: kpi("Active Stores", f"{int(kdf['total_stores'])}")

    except Exception as e:
        st.error(f"Database connection failed: {e}")
        st.stop()

    st.markdown("---")
    col_l, col_r = st.columns(2)

    # Monthly revenue trend
    with col_l:
        section("Monthly Revenue Trend")
        monthly_sql = """
        SELECT
            DATE_TRUNC('month', payment_date) AS month,
            ROUND(SUM(amount)::numeric, 2)    AS revenue
        FROM payment
        GROUP BY 1 ORDER BY 1
        """
        mdf = run_query(monthly_sql)
        mdf["month"] = pd.to_datetime(mdf["month"])
        fig = px.area(mdf, x="month", y="revenue",
                      color_discrete_sequence=["#e94560"],
                      labels={"month": "", "revenue": "Revenue ($)"})
        fig.update_layout(margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)",
                          paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        insight("Revenue peaked in mid-period and shows a clear seasonal pattern. "
                "This informs when to run promotional campaigns.")

    # Revenue by store
    with col_r:
        section("Revenue by Store")
        store_rev_sql = """
        SELECT
            s.store_id,
            ROUND(SUM(p.amount)::numeric, 2) AS revenue,
            COUNT(DISTINCT p.customer_id)    AS customers
        FROM payment p
        JOIN rental    r ON p.rental_id   = r.rental_id
        JOIN inventory i ON r.inventory_id = i.inventory_id
        JOIN store     s ON i.store_id     = s.store_id
        GROUP BY s.store_id ORDER BY s.store_id
        """
        sdf = run_query(store_rev_sql)
        sdf["store_label"] = "Store " + sdf["store_id"].astype(str)
        fig2 = px.bar(sdf, x="store_label", y="revenue",
                      text="revenue", color="store_label",
                      color_discrete_sequence=["#e94560", "#4299e1"],
                      labels={"store_label": "Store", "revenue": "Revenue ($)"})
        fig2.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig2.update_layout(margin=dict(t=10, b=10), showlegend=False,
                           plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)
        insight("Both stores perform at near-identical revenue levels, suggesting balanced "
                "inventory and customer distribution.")


# ══════════════════════════════════════════════
#  PAGE 2 – CUSTOMER INTELLIGENCE
#  Q1: Who are the highest-value customers?
#  Q2: Which customers are at risk of churning?
# ══════════════════════════════════════════════
elif page == "👥 Customer Intelligence":
    st.title("👥 Customer Intelligence")
    st.markdown(
        "**Q1:** Who are the highest-value customers and how are they segmented?  \n"
        "**Q2:** Which customers are at risk of churning based on recency?"
    )
    st.markdown("---")

    # ── Customer Lifetime Value + Segmentation ──
    clv_sql = """
    SELECT
        c.customer_id,
        c.first_name || ' ' || c.last_name    AS customer_name,
        c.store_id,
        c.active,
        COUNT(DISTINCT p.payment_id)           AS total_payments,
        ROUND(SUM(p.amount)::numeric, 2)       AS lifetime_value,
        ROUND(AVG(p.amount)::numeric, 4)       AS avg_payment,
        MAX(p.payment_date)::date              AS last_payment_date
    FROM customer c
    JOIN payment  p ON c.customer_id = p.customer_id
    GROUP BY c.customer_id, c.first_name, c.last_name, c.store_id, c.active
    ORDER BY lifetime_value DESC
    """
    cdf = run_query(clv_sql)

    # Tertile segmentation
    cdf["segment"] = pd.qcut(
        cdf["lifetime_value"],
        q=3,
        labels=["Low Value", "Mid Value", "High Value"]
    )

    # Churn risk: days since last payment vs dataset max date
    max_date = pd.to_datetime(cdf["last_payment_date"]).max()
    cdf["days_inactive"] = (max_date - pd.to_datetime(cdf["last_payment_date"])).dt.days
    cdf["churn_risk"] = pd.cut(
        cdf["days_inactive"],
        bins=[-1, 30, 90, 99999],
        labels=["Low Risk", "Medium Risk", "High Risk"]
    )

    # ── Row 1: KPIs ──
    seg_rev = cdf.groupby("segment")["lifetime_value"].sum()
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("High-Value Customers", f"{(cdf['segment'] == 'High Value').sum()}")
    with c2: kpi("High-Value Revenue", f"${seg_rev.get('High Value', 0):,.2f}")
    with c3: kpi("High Churn Risk", f"{(cdf['churn_risk'] == 'High Risk').sum()}")
    with c4: kpi("Avg Customer LTV", f"${cdf['lifetime_value'].mean():.2f}")

    st.markdown("---")
    col_l, col_r = st.columns(2)

    # Segment revenue contribution
    with col_l:
        section("Q1 — Customer Value Segmentation")
        seg_summary = cdf.groupby("segment").agg(
            count=("customer_id", "count"),
            total_revenue=("lifetime_value", "sum"),
            avg_ltv=("lifetime_value", "mean")
        ).reset_index()

        fig = px.bar(seg_summary, x="segment", y="total_revenue",
                     text="count",
                     color="segment",
                     color_discrete_sequence=["#4299e1", "#ed8936", "#e94560"],
                     labels={"segment": "Segment", "total_revenue": "Total Revenue ($)"})
        fig.update_traces(texttemplate="%{text} customers", textposition="outside")
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)",
                          paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)
        insight(f"High-Value customers ({seg_summary[seg_summary['segment']=='High Value']['count'].values[0]}) "
                f"generate ${seg_rev.get('High Value',0):,.0f} — "
                f"disproportionately high contribution relative to their count.")

    # Churn risk distribution
    with col_r:
        section("Q2 — Churn Risk by Recency")
        churn_summary = cdf.groupby("churn_risk").agg(
            count=("customer_id", "count"),
            avg_ltv=("lifetime_value", "mean")
        ).reset_index()

        fig2 = px.pie(churn_summary, names="churn_risk", values="count",
                      color="churn_risk",
                      color_discrete_map={
                          "Low Risk": "#68d391",
                          "Medium Risk": "#ed8936",
                          "High Risk": "#e94560"
                      },
                      hole=0.45)
        fig2.update_layout(margin=dict(t=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)
        insight("Customers inactive for more than 90 days are classified as High Risk. "
                "They should be targeted with re-engagement offers immediately.")

    st.markdown("---")
    section("Behavioural Patterns — Rental Frequency Distribution")

    rental_freq_sql = """
    SELECT
        c.customer_id,
        COUNT(r.rental_id) AS rental_count
    FROM customer c
    JOIN rental r ON c.customer_id = r.customer_id
    GROUP BY c.customer_id
    """
    rdf = run_query(rental_freq_sql)
    fig3 = px.histogram(rdf, x="rental_count", nbins=30,
                        color_discrete_sequence=["#4299e1"],
                        labels={"rental_count": "Rentals per Customer", "count": "Customers"})
    fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                       margin=dict(t=10))
    st.plotly_chart(fig3, use_container_width=True)
    insight("Most customers cluster in the 20-40 rental range. A small high-frequency "
            "tail (60+ rentals) represents VIP behaviour worth protecting with loyalty incentives.")

    st.markdown("---")
    section("Top 20 Customers by Lifetime Value")
    st.dataframe(
        cdf[["customer_name", "store_id", "lifetime_value", "total_payments",
             "avg_payment", "segment", "churn_risk", "days_inactive"]]
        .head(20)
        .rename(columns={
            "customer_name": "Customer",
            "store_id": "Store",
            "lifetime_value": "Lifetime Value ($)",
            "total_payments": "Payments",
            "avg_payment": "Avg Payment ($)",
            "segment": "Segment",
            "churn_risk": "Churn Risk",
            "days_inactive": "Days Inactive"
        }),
        use_container_width=True,
        hide_index=True,
    )


# ══════════════════════════════════════════════
#  PAGE 3 – REVENUE OPTIMISATION
#  Q3: Which film categories drive the most revenue?
#  Q4: What are the temporal revenue trends (seasonal/monthly)?
# ══════════════════════════════════════════════
elif page == "💰 Revenue Optimisation":
    st.title("💰 Revenue Optimisation")
    st.markdown(
        "**Q3:** Which film categories drive the most revenue and rentals?  \n"
        "**Q4:** What seasonal and temporal trends affect revenue performance?"
    )
    st.markdown("---")

    # ── Category performance ──
    cat_sql = """
    SELECT
        cat.name                                       AS category,
        COUNT(DISTINCT r.rental_id)                    AS total_rentals,
        ROUND(SUM(p.amount)::numeric, 2)               AS total_revenue,
        ROUND(AVG(p.amount)::numeric, 4)               AS avg_payment,
        ROUND(AVG(f.rental_rate)::numeric, 4)          AS avg_rental_rate,
        ROUND(SUM(p.amount) / NULLIF(COUNT(r.rental_id),0), 4) AS revenue_per_rental
    FROM payment p
    JOIN rental      r  ON p.rental_id    = r.rental_id
    JOIN inventory   i  ON r.inventory_id = i.inventory_id
    JOIN film        f  ON i.film_id      = f.film_id
    JOIN film_category fc ON f.film_id   = fc.film_id
    JOIN category   cat ON fc.category_id = cat.category_id
    GROUP BY cat.name
    ORDER BY total_revenue DESC
    """
    catdf = run_query(cat_sql)

    # KPIs
    top_cat = catdf.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Top Category", top_cat["category"])
    with c2: kpi("Top Category Revenue", f"${top_cat['total_revenue']:,.2f}")
    with c3: kpi("Most Rented Category", catdf.sort_values("total_rentals", ascending=False).iloc[0]["category"])
    with c4: kpi("Best Revenue/Rental", catdf.sort_values("revenue_per_rental", ascending=False).iloc[0]["category"])

    st.markdown("---")
    col_l, col_r = st.columns(2)

    with col_l:
        section("Q3 — Revenue by Film Category")
        fig = px.bar(catdf.sort_values("total_revenue"), x="total_revenue", y="category",
                     orientation="h", text="total_revenue",
                     color="total_revenue",
                     color_continuous_scale=["#1a1a2e", "#e94560"],
                     labels={"total_revenue": "Revenue ($)", "category": ""})
        fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig.update_layout(coloraxis_showscale=False, showlegend=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          margin=dict(t=10, l=10))
        st.plotly_chart(fig, use_container_width=True)
        insight(f"**{top_cat['category']}** leads in total revenue. "
                "Low-revenue categories like Music and Travel may warrant a stock review or promotional push.")

    with col_r:
        section("Q3 — Rental Volume vs Revenue per Rental")
        fig2 = px.scatter(catdf, x="total_rentals", y="revenue_per_rental",
                          size="total_revenue", text="category",
                          color="category",
                          labels={
                              "total_rentals": "Total Rentals",
                              "revenue_per_rental": "Revenue per Rental ($)"
                          })
        fig2.update_traces(textposition="top center")
        fig2.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)",
                           paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=10))
        st.plotly_chart(fig2, use_container_width=True)
        insight("Categories sitting high and right (high volume AND high revenue per rental) "
                "are the most efficient drivers of business value.")

    st.markdown("---")
    section("Q4 — Temporal Revenue Trends")

    temporal_sql = """
    SELECT
        EXTRACT(YEAR  FROM payment_date)::int  AS year,
        EXTRACT(MONTH FROM payment_date)::int  AS month,
        TO_CHAR(payment_date, 'Mon YYYY')      AS month_label,
        DATE_TRUNC('month', payment_date)      AS month_date,
        ROUND(SUM(amount)::numeric, 2)         AS revenue,
        COUNT(payment_id)                      AS transactions,
        EXTRACT(DOW FROM payment_date)::int    AS day_of_week
    FROM payment
    GROUP BY 1,2,3,4
    ORDER BY month_date
    """
    tdf = run_query(temporal_sql)
    tdf["month_date"] = pd.to_datetime(tdf["month_date"])

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        section("Monthly Revenue with Transaction Volume")
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=tdf["month_date"], y=tdf["revenue"],
                              name="Revenue", marker_color="#e94560", opacity=0.8))
        fig3.add_trace(go.Scatter(x=tdf["month_date"], y=tdf["transactions"],
                                  name="Transactions", yaxis="y2",
                                  line=dict(color="#4299e1", width=2)))
        fig3.update_layout(
            yaxis=dict(title="Revenue ($)"),
            yaxis2=dict(title="Transactions", overlaying="y", side="right"),
            legend=dict(orientation="h", y=1.1),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=30)
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_t2:
        section("Revenue by Month-of-Year (Seasonality)")
        seasonal_sql = """
        SELECT
            EXTRACT(MONTH FROM payment_date)::int AS month_num,
            TO_CHAR(payment_date, 'Mon')          AS month_name,
            ROUND(AVG(daily_rev), 2)              AS avg_revenue
        FROM (
            SELECT
                DATE_TRUNC('day', payment_date) AS day,
                payment_date,
                SUM(amount) AS daily_rev
            FROM payment
            GROUP BY 1, 2
        ) sub
        GROUP BY 1, 2
        ORDER BY 1
        """
        seadf = run_query(seasonal_sql)
        fig4 = px.bar(seadf, x="month_name", y="avg_revenue",
                      color="avg_revenue",
                      color_continuous_scale=["#1a1a2e", "#4299e1", "#e94560"],
                      labels={"month_name": "Month", "avg_revenue": "Avg Daily Revenue ($)"})
        fig4.update_layout(coloraxis_showscale=False,
                           plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           margin=dict(t=10))
        st.plotly_chart(fig4, use_container_width=True)
        insight("Months with above-average daily revenue indicate peak rental seasons. "
                "Ensure inventory and staffing are aligned during these periods.")

    st.markdown("---")
    section("Category Performance Table")
    st.dataframe(
        catdf.rename(columns={
            "category": "Category",
            "total_rentals": "Rentals",
            "total_revenue": "Revenue ($)",
            "avg_payment": "Avg Payment ($)",
            "avg_rental_rate": "Avg Rental Rate ($)",
            "revenue_per_rental": "Revenue/Rental ($)"
        }),
        use_container_width=True, hide_index=True
    )


# ══════════════════════════════════════════════
#  PAGE 4 – INVENTORY & OPERATIONS
#  Q5: How efficiently is inventory being used?
#  Q6: How do the two stores compare operationally?
# ══════════════════════════════════════════════
elif page == "📦 Inventory & Operations":
    st.title("📦 Inventory & Operations")
    st.markdown(
        "**Q5:** How efficiently is inventory being used? Which items are slow-moving?  \n"
        "**Q6:** How do the two stores compare across revenue, customers, and efficiency?"
    )
    st.markdown("---")

    # ── Inventory turnover ──
    inv_sql = """
    SELECT
        i.inventory_id,
        i.store_id,
        f.film_id,
        f.title,
        f.rental_rate,
        cat.name                                        AS category,
        COUNT(r.rental_id)                              AS rental_count,
        ROUND(COALESCE(SUM(p.amount), 0)::numeric, 2)  AS total_revenue,
        MAX(r.rental_date)::date                        AS last_rental_date
    FROM inventory i
    JOIN film        f  ON i.film_id      = f.film_id
    JOIN film_category fc ON f.film_id   = fc.film_id
    JOIN category   cat ON fc.category_id = cat.category_id
    LEFT JOIN rental r  ON i.inventory_id = r.inventory_id
    LEFT JOIN payment p ON r.rental_id   = p.rental_id
    GROUP BY i.inventory_id, i.store_id, f.film_id, f.title, f.rental_rate, cat.name
    """
    invdf = run_query(inv_sql)

    # ── Store performance ──
    store_sql = """
    SELECT
        s.store_id,
        COUNT(DISTINCT c.customer_id)                AS total_customers,
        COUNT(DISTINCT i.inventory_id)               AS total_inventory,
        COUNT(DISTINCT r.rental_id)                  AS total_rentals,
        ROUND(SUM(p.amount)::numeric, 2)             AS total_revenue
    FROM store s
    LEFT JOIN customer  c ON s.store_id  = c.store_id
    LEFT JOIN inventory i ON s.store_id  = i.store_id
    LEFT JOIN rental    r ON i.inventory_id = r.inventory_id
    LEFT JOIN payment   p ON r.rental_id = p.rental_id
    GROUP BY s.store_id ORDER BY s.store_id
    """
    stdf = run_query(store_sql)
    stdf["revenue_per_inventory"] = (stdf["total_revenue"] / stdf["total_inventory"]).round(2)
    stdf["rentals_per_inventory"] = (stdf["total_rentals"] / stdf["total_inventory"]).round(2)
    stdf["store_label"] = "Store " + stdf["store_id"].astype(str)

    # KPIs
    slow_count = (invdf["rental_count"] == 0).sum()
    avg_turnover = invdf["rental_count"].mean()
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Total Inventory Items", f"{len(invdf):,}")
    with c2: kpi("Zero-Rental Items", f"{slow_count}")
    with c3: kpi("Avg Rentals per Copy", f"{avg_turnover:.1f}")
    with c4: kpi("Slow-Moving (<3 Rentals)", f"{(invdf['rental_count'] < 3).sum()}")

    st.markdown("---")
    col_l, col_r = st.columns(2)

    with col_l:
        section("Q6 — Store Comparison: Revenue & Efficiency")
        metrics = ["total_revenue", "total_rentals", "total_customers", "total_inventory",
                   "revenue_per_inventory", "rentals_per_inventory"]
        labels  = ["Revenue ($)", "Rentals", "Customers", "Inventory Items",
                   "Rev/Inventory ($)", "Rentals/Inventory"]
        store1 = stdf[stdf["store_id"] == 1][metrics].values.flatten()
        store2 = stdf[stdf["store_id"] == 2][metrics].values.flatten()

        fig = go.Figure(data=[
            go.Bar(name="Store 1", x=labels, y=store1, marker_color="#e94560"),
            go.Bar(name="Store 2", x=labels, y=store2, marker_color="#4299e1"),
        ])
        fig.update_layout(barmode="group",
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          legend=dict(orientation="h", y=1.1), margin=dict(t=30))
        st.plotly_chart(fig, use_container_width=True)
        insight("Compare revenue-per-inventory to identify which store squeezes more value "
                "from each copy. Reallocate stock from the lower-efficiency store.")

    with col_r:
        section("Q5 — Inventory Turnover Distribution")
        fig2 = px.histogram(invdf, x="rental_count", nbins=25,
                            color_discrete_sequence=["#ed8936"],
                            labels={"rental_count": "Rentals per Copy", "count": "# Copies"})
        fig2.add_vline(x=avg_turnover, line_dash="dash", line_color="#e94560",
                       annotation_text=f"Avg {avg_turnover:.1f}")
        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           margin=dict(t=10))
        st.plotly_chart(fig2, use_container_width=True)
        insight(f"{slow_count} inventory items have never been rented. These represent "
                "dead stock that should be removed or promoted aggressively.")

    st.markdown("---")
    section("Q5 — Inventory Turnover by Category")
    cat_inv = invdf.groupby("category").agg(
        avg_rentals=("rental_count", "mean"),
        total_copies=("inventory_id", "count"),
        zero_rental=("rental_count", lambda x: (x == 0).sum())
    ).reset_index().sort_values("avg_rentals", ascending=False)

    fig3 = px.bar(cat_inv, x="category", y="avg_rentals",
                  color="zero_rental", text="total_copies",
                  color_continuous_scale=["#68d391", "#e94560"],
                  labels={
                      "category": "Category",
                      "avg_rentals": "Avg Rentals per Copy",
                      "zero_rental": "Zero-Rental Copies",
                      "total_copies": "Total Copies"
                  })
    fig3.update_traces(texttemplate="%{text} copies", textposition="outside")
    fig3.update_layout(coloraxis_colorbar=dict(title="Dead Stock"),
                       plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                       margin=dict(t=10))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    section("Bottom 20 Slowest-Moving Inventory Items")
    slow_df = (invdf[invdf["rental_count"] < 3]
               .sort_values("rental_count")[["title", "category", "store_id",
                                             "rental_rate", "rental_count",
                                             "total_revenue", "last_rental_date"]]
               .head(20))
    st.dataframe(
        slow_df.rename(columns={
            "title": "Film Title", "category": "Category", "store_id": "Store",
            "rental_rate": "Rate ($)", "rental_count": "Total Rentals",
            "total_revenue": "Revenue ($)", "last_rental_date": "Last Rented"
        }),
        use_container_width=True, hide_index=True
    )


# ══════════════════════════════════════════════
#  PAGE 5 – INNOVATION & RECOMMENDATIONS
#  Q7: What should customers rent next? (Recommendation engine)
#  Q8: Can we predict customer churn? (Predictive model)
# ══════════════════════════════════════════════
elif page == "🤖 Innovation & Recommendations":
    st.title("🤖 Innovation & Recommendations")
    st.markdown(
        "**Q7:** What genres should be recommended to each customer segment?  \n"
        "**Q8:** Can we predict churn risk using rental behaviour features?"
    )
    st.markdown("---")

    # ── Recommendation Engine: Category affinity by segment ──
    affinity_sql = """
    SELECT
        cat.name                                       AS category,
        ROUND(SUM(p.amount)::numeric, 2)               AS total_revenue,
        COUNT(DISTINCT r.rental_id)                    AS total_rentals,
        ROUND(AVG(p.amount)::numeric, 4)               AS avg_payment,
        COUNT(DISTINCT p.customer_id)                  AS unique_customers
    FROM payment p
    JOIN rental      r  ON p.rental_id    = r.rental_id
    JOIN inventory   i  ON r.inventory_id = i.inventory_id
    JOIN film        f  ON i.film_id      = f.film_id
    JOIN film_category fc ON f.film_id   = fc.film_id
    JOIN category   cat ON fc.category_id = cat.category_id
    GROUP BY cat.name
    ORDER BY total_revenue DESC
    """
    adf = run_query(affinity_sql)

    # Priority score: normalise revenue + rental volume
    adf["rev_score"]    = (adf["total_revenue"]  - adf["total_revenue"].min())  / (adf["total_revenue"].max()  - adf["total_revenue"].min())
    adf["rent_score"]   = (adf["total_rentals"]  - adf["total_rentals"].min())  / (adf["total_rentals"].max()  - adf["total_rentals"].min())
    adf["priority_score"] = (0.6 * adf["rev_score"] + 0.4 * adf["rent_score"]).round(4)
    adf["priority"] = pd.cut(adf["priority_score"], bins=3,
                             labels=["Low Priority", "Medium Priority", "High Priority"])

    col_l, col_r = st.columns(2)

    with col_l:
        section("Q7 — Category Recommendation Priority Score")
        fig = px.bar(adf.sort_values("priority_score"), x="priority_score", y="category",
                     orientation="h",
                     color="priority_score",
                     color_continuous_scale=["#1a1a2e", "#4299e1", "#e94560"],
                     text="priority",
                     labels={"priority_score": "Priority Score (0–1)", "category": ""})
        fig.update_traces(textposition="outside")
        fig.update_layout(coloraxis_showscale=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          margin=dict(t=10, l=10))
        st.plotly_chart(fig, use_container_width=True)
        insight("High-Priority categories (score > 0.67) should be prominently featured "
                "in any customer-facing recommendation engine or promotional email.")

    with col_r:
        section("Q7 — Revenue vs Reach (Unique Customers)")
        fig2 = px.scatter(adf, x="unique_customers", y="total_revenue",
                          size="total_rentals", color="priority",
                          text="category",
                          color_discrete_map={
                              "High Priority": "#e94560",
                              "Medium Priority": "#ed8936",
                              "Low Priority": "#4299e1"
                          },
                          labels={
                              "unique_customers": "Unique Customers Who Rented",
                              "total_revenue": "Total Revenue ($)"
                          })
        fig2.update_traces(textposition="top center")
        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           margin=dict(t=10))
        st.plotly_chart(fig2, use_container_width=True)
        insight("Categories with high customer reach but lower revenue may benefit from "
                "a pricing review. Categories with high revenue but fewer customers "
                "represent upsell opportunities.")

    st.markdown("---")
    section("Q8 — Churn Risk Prediction: Feature-Based Scoring Model")

    churn_sql = """
    SELECT
        c.customer_id,
        c.active,
        COUNT(DISTINCT r.rental_id)                              AS rental_count,
        ROUND(SUM(p.amount)::numeric, 2)                         AS total_spent,
        ROUND(AVG(p.amount)::numeric, 4)                         AS avg_payment,
        MAX(p.payment_date)::date                                AS last_payment,
        (MAX(p.payment_date) - MIN(p.payment_date))::int / 30.0  AS tenure_months,
        COUNT(DISTINCT p.payment_id) * 1.0
            / NULLIF((MAX(p.payment_date) - MIN(p.payment_date))::int, 0) AS payment_frequency
    FROM customer c
    JOIN payment p ON c.customer_id = p.customer_id
    JOIN rental  r ON p.rental_id   = r.rental_id
    GROUP BY c.customer_id, c.active
    """
    pred_df = run_query(churn_sql)

    max_date = pd.to_datetime(pred_df["last_payment"]).max()
    pred_df["days_since_last"] = (max_date - pd.to_datetime(pred_df["last_payment"])).dt.days

    # Churn score: weighted combination of recency + low frequency + low spend
    pred_df["recency_norm"]   = pred_df["days_since_last"].clip(0, 180) / 180
    pred_df["freq_norm"]      = 1 - (pred_df["rental_count"].clip(0, 50) / 50)
    pred_df["spend_norm"]     = 1 - (pred_df["total_spent"].clip(0, 200) / 200)
    pred_df["churn_score"]    = (
        0.50 * pred_df["recency_norm"] +
        0.30 * pred_df["freq_norm"]    +
        0.20 * pred_df["spend_norm"]
    ).round(4)
    pred_df["risk_label"] = pd.cut(
        pred_df["churn_score"],
        bins=[0, 0.33, 0.66, 1.01],
        labels=["Low Risk", "Medium Risk", "High Risk"]
    )

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        section("Churn Score Distribution")
        fig3 = px.histogram(pred_df, x="churn_score", nbins=30,
                            color_discrete_sequence=["#e94560"],
                            labels={"churn_score": "Churn Score (0 = safe, 1 = high risk)"})
        fig3.add_vline(x=0.66, line_dash="dash", line_color="#ed8936",
                       annotation_text="High Risk threshold")
        fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           margin=dict(t=10))
        st.plotly_chart(fig3, use_container_width=True)

    with col_p2:
        section("Churn Score vs Total Spend")
        fig4 = px.scatter(pred_df, x="total_spent", y="churn_score",
                          color="risk_label",
                          color_discrete_map={
                              "Low Risk": "#68d391",
                              "Medium Risk": "#ed8936",
                              "High Risk": "#e94560"
                          },
                          opacity=0.6,
                          labels={"total_spent": "Total Spend ($)", "churn_score": "Churn Score"})
        fig4.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           margin=dict(t=10))
        st.plotly_chart(fig4, use_container_width=True)

    insight("The churn score is a weighted composite of recency (50%), rental frequency (30%), "
            "and total spend (20%). Customers scoring above 0.66 are flagged High Risk and "
            "should be prioritised for re-engagement campaigns. This model is interpretable, "
            "requires no training data, and can be updated in real-time as new payments arrive.")

    st.markdown("---")
    section("High-Risk Customers to Target (Top 20 by Churn Score)")
    high_risk = (pred_df[pred_df["risk_label"] == "High Risk"]
                 .sort_values("churn_score", ascending=False)
                 [["customer_id", "days_since_last", "rental_count",
                   "total_spent", "churn_score", "tenure_months"]]
                 .head(20))
    st.dataframe(
        high_risk.rename(columns={
            "customer_id": "Customer ID",
            "days_since_last": "Days Inactive",
            "rental_count": "Total Rentals",
            "total_spent": "Total Spent ($)",
            "churn_score": "Churn Score",
            "tenure_months": "Tenure (months)"
        }),
        use_container_width=True, hide_index=True
    )

    st.markdown("---")
    section("Summary of Business Recommendations")
    recommendations = {
        "🎯 Protect High-Value Customers": "Launch a loyalty programme targeting the top 33% by lifetime value. Offer early access to new titles and personalised discounts.",
        "⚠️ Re-engage At-Risk Customers": "Send personalised re-engagement emails to the 50+ high-risk customers (churn score > 0.66) with a time-limited discount offer.",
        "🎬 Promote High-Priority Categories": "Feature Sports, Sci-Fi, and Animation prominently in store and in any digital communications. These categories combine strong revenue with broad customer appeal.",
        "📦 Retire Dead Stock": f"Review and remove or promote the {(run_query('SELECT COUNT(*) AS c FROM inventory i LEFT JOIN rental r ON i.inventory_id = r.inventory_id WHERE r.rental_id IS NULL').iloc[0]['c'])} inventory items that have never been rented.",
        "🏪 Rebalance Inventory Across Stores": "Reallocate copies from the lower revenue-per-inventory store to the more efficient one, particularly for top-performing categories.",
        "📈 Seasonal Promotions": "Run promotional campaigns in months that historically show above-average daily revenue. Align staffing and inventory restocking to match peak periods.",
    }
    for title, desc in recommendations.items():
        with st.expander(title):
            st.write(desc)