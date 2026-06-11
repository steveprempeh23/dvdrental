# Part A: Business Problem Definition

## DSA5102 Big Data Management — Capstone Project
**Student:** Steve Prempeh
**Dataset:** PostgreSQL DVD Rental Database

---

## 1. Executive Summary

This project analyses the operational data of a mid-sized DVD rental company running three physical stores, serving over 600 customers across a catalogue of approximately 1,000 film titles. The company holds two years of rental and payment transaction history, providing a rich foundation for data-driven decision-making. Despite having substantial transactional data, senior management currently lacks structured visibility into which customers generate the most value, which film categories drive revenue, how efficiently inventory is being utilised across stores, and which customers are at risk of disengaging. This analysis addresses these gaps by applying a complete data engineering and analytics workflow — from database validation through to an interactive business intelligence dashboard — to deliver actionable, evidence-based recommendations. The four core objectives target customer value optimisation, revenue performance improvement, operational efficiency, and a forward-looking recommendation capability that positions the business to proactively retain customers and maximise returns from its existing catalogue and inventory.

---

## 2. Analytical Objectives

### Objective 1: Understand and Segment Customer Value
**Justification:** Not all customers contribute equally to revenue. Without knowing which customers are high-value, the business applies the same treatment to everyone, wasting marketing spend on low-return customers while potentially underserving the most profitable ones. Segmenting customers by lifetime value enables targeted retention strategies, personalised promotions, and prioritised service for the customers who matter most to the bottom line.

### Objective 2: Identify Revenue Drivers and Optimise Pricing Strategy
**Justification:** The business stocks 16 different film categories but likely generates disproportionate revenue from a small subset of them. Understanding which categories, film titles, and rental price points generate the most value — and how this varies across seasons and months — allows management to make informed decisions about stock investment, promotional timing, and pricing adjustments that directly improve profitability.

### Objective 3: Assess Inventory Efficiency and Store Operational Performance
**Justification:** Physical inventory represents a significant capital investment. Copies that are never rented, or rented infrequently, represent dead capital that could be redeployed. Similarly, if one store significantly outperforms the other in revenue-per-inventory-item, that signals an opportunity to rebalance stock. Without this analysis, operational inefficiencies persist invisibly and drain resources.

### Objective 4: Build a Proactive Customer Retention and Recommendation Capability
**Justification:** Acquiring new customers is substantially more expensive than retaining existing ones. By scoring existing customers on their churn risk — based on recency, frequency, and spend — the business can intervene before customers disengage. Coupling this with a category-based recommendation engine creates a foundation for personalised re-engagement campaigns that are grounded in actual rental behaviour rather than guesswork.

---

## 3. Analytical Questions

### Theme 1: Customer Intelligence

**Q1. Who are the highest-value customers, and how are they distributed across value segments?**
Approach: Calculate total revenue per customer using `SUM(payment.amount)` grouped by `customer_id`. Segment into Low, Mid, and High Value tertiles using `pd.qcut`. Visualise segment sizes and their respective revenue contributions. Identify the top 20 customers by lifetime value.

**Q2. Which customers are at risk of churning based on their recent payment behaviour?**
Approach: Compute days since each customer's last payment relative to the most recent transaction date in the dataset. Classify customers into Low Risk (0–30 days), Medium Risk (31–90 days), and High Risk (90+ days). Build a composite churn score weighted by recency (50%), rental frequency (30%), and total spend (20%) to produce a ranked target list for re-engagement.

---

### Theme 2: Revenue Optimisation

**Q3. Which film categories generate the most revenue, and which are underperforming?**
Approach: Join `payment`, `rental`, `inventory`, `film`, `film_category`, and `category` tables. Aggregate total revenue, rental count, average payment, and revenue-per-rental by category. Rank all 16 categories and identify candidates for promotional investment versus stock review.

**Q4. What seasonal and temporal patterns exist in revenue, and when are peak rental periods?**
Approach: Extract year, month, and day-of-week dimensions from `payment_date`. Aggregate monthly revenue and transaction counts. Plot revenue trends over time and calculate average daily revenue by month-of-year to identify seasonal peaks and troughs that should inform promotional and staffing decisions.

---

### Theme 3: Inventory and Operations

**Q5. How efficiently is the physical inventory being utilised, and which items are slow-moving or inactive?**
Approach: Join `inventory` to `rental` using a LEFT JOIN to capture items with zero rentals. Count total rentals per `inventory_id`. Compute average rentals per copy by film category. Flag items with fewer than 3 rentals as slow-moving and items with zero rentals as dead stock. Calculate an inventory turnover rate (rentals per copy) as the primary efficiency metric.

**Q6. How do Store 1 and Store 2 compare across revenue, customer count, inventory size, and operational efficiency?**
Approach: Aggregate total revenue, customer count, inventory items, and rental count per store. Derive efficiency ratios: revenue-per-inventory-item and rentals-per-inventory-item. Compare stores across all six metrics using grouped bar charts. Identify which store is more efficient and recommend stock rebalancing accordingly.

---

### Theme 4: Innovation / Custom Analysis

**Q7. What film categories should be recommended to customers, and how can a priority-based recommendation engine be built from existing data?**
Approach: Compute a normalised recommendation priority score for each category using a weighted formula: 60% revenue score + 40% rental volume score, both normalised to a 0–1 scale. Classify categories into High, Medium, and Low Priority tiers. Use a revenue-vs-customer-reach scatter chart to identify upsell opportunities. This constitutes a content-based, category-level recommendation engine built entirely from transactional data without requiring any external tools or ML libraries.

**Q8. Can customer churn risk be predicted using a feature-based scoring model, and which customers should be targeted first?**
Approach: Engineer three behavioural features per customer: recency (days since last payment, normalised to 0–1 over a 180-day window), frequency (rental count, normalised over a 50-rental ceiling), and monetary value (total spend, normalised over a $200 ceiling). Combine into a weighted composite churn score. This RFM-inspired model is fully interpretable, requires no training data, and produces a ranked intervention list that a marketing team can act on immediately.

---

## 4. High-Level Analytical Approach

The project follows a sequential, reproducible pipeline:

1. **Environment Setup** — Docker Compose launches PostgreSQL and pgAdmin. The DVD Rental database is restored from a `.tar` backup file.
2. **Validation** (`1_setup_validate.py`) — Confirms all 15 critical tables are present, counts rows, checks for data quality issues, and exports a structured validation report.
3. **Exploration** (`2_data_exploration.py`) — Inspects schemas, identifies missing values and outliers using IQR, produces descriptive statistics, and generates four exploratory visualisations.
4. **Data Integration** (`3_data_relationships.py`) — Builds four merged analysis-ready datasets by joining multiple tables. Justifies join keys and types. Validates output row counts.
5. **Advanced Analysis** (`4_analysis.py`) — Executes customer segmentation, CLV calculation, churn risk scoring, revenue analysis, inventory turnover, store comparison, and recommendation scoring. Exports all results to `tables/`, `results/`, and `exports/`.
6. **Dashboard** (`5_dashboard.py`) — Streamlit application with five pages, KPI cards, and ten interactive Plotly charts answering all eight analytical questions.
7. **Reporting** — Executive Report communicates findings and recommendations for non-technical stakeholders. Architecture Diagram and Data Description provide full technical transparency.