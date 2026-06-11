# Business Problem Definition

**Project:** DVD Rental Big Data Management
**Student:** Nana Owusu Achiaw Prempeh
**Roll Number:** 2000250074
**Lecturer:** Jeremiah Ishaya
**Course:** DSA5102 Big Data Management — Part A (15 marks)

---

## 1. Executive Summary

This project analyses the operational data of a mid-sized DVD rental company running two physical stores, serving over 600 customers across a catalogue of approximately 1,000 film titles in 16 genre categories. The company holds two years of rental and payment transaction history, providing a rich foundation for data-driven decision-making. Despite having substantial transactional data, senior management currently lacks structured visibility into which customers generate the most value, which film categories drive revenue, how efficiently inventory is being utilised across stores, and which customers are at risk of disengaging. This analysis addresses these gaps by applying a complete data engineering and analytics workflow — from database validation through to an interactive business intelligence dashboard — to deliver actionable, evidence-based recommendations. The four core objectives target customer value optimisation, revenue performance improvement, operational efficiency, and a forward-looking recommendation capability that positions the business to proactively retain customers and maximise returns from its existing catalogue and inventory.

---

## 2. Analytical Objectives

### Objective 1 — Understand and Segment Customer Value

**Justification:** Not all customers contribute equally to revenue. Without identifying which customers are high-value, the business applies the same treatment to everyone — wasting marketing spend on low-return customers while potentially underserving the most profitable ones. Segmenting customers by lifetime value and computing annualised CLV enables targeted retention strategies, personalised promotions, and prioritised service investment where it generates the greatest return.

---

### Objective 2 — Identify Revenue Drivers and Optimise the Pricing Strategy

**Justification:** The business stocks 16 different film categories but likely generates disproportionate revenue from a small subset. Understanding which categories, titles, and price points generate the most value — and how revenue varies across seasons and months — allows management to make informed decisions about stock investment, promotional timing, and pricing adjustments that directly improve profitability.

---

### Objective 3 — Assess Inventory Efficiency and Store Operational Performance

**Justification:** Physical inventory represents significant capital. Copies that are rarely or never rented represent dead capital that could be redeployed to higher-demand titles. If one store outperforms the other in revenue-per-inventory-item, that signals an opportunity to rebalance stock. Without this analysis, operational inefficiencies persist invisibly and drain resources across both locations.

---

### Objective 4 — Build a Proactive Customer Retention and Recommendation Capability

**Justification:** Acquiring new customers is substantially more expensive than retaining existing ones. By scoring customers on churn risk — using recency, frequency, and spend signals — the business can intervene before customers disengage permanently. Coupling this with a category-based recommendation engine creates a foundation for personalised re-engagement campaigns grounded in actual rental behaviour rather than guesswork.

---

## 3. Analytical Questions

### Theme 1 — Customer Intelligence

**Q1. Who are the highest-value customers, and how are they distributed across value segments?**

Approach: Calculate total revenue per customer using `SUM(payment.amount)` grouped by `customer_id`. Compute annualised CLV as `(lifetime_value / active_days) × 365`. Segment customers into Low Value, Mid Value, and High Value tertiles using `pd.qcut`. Visualise segment sizes, total revenue contribution per segment, and CLV distribution. Export the top 20 customers by lifetime value.

---

**Q2. Which customers are at risk of churning based on their recent payment behaviour?**

Approach: Compute days since each customer's last payment relative to the dataset's maximum payment date. Build a composite churn score using an RFM-inspired weighted formula: recency (50%), rental frequency (30%), and total spend (20%), all normalised to a 0–1 scale. Classify customers into Low Risk (0–0.33), Medium Risk (0.34–0.60), and High Risk (0.61–1.00). Produce a ranked intervention list for the marketing team.

---

### Theme 2 — Revenue Optimisation

**Q3. Which film categories generate the most revenue, and which are underperforming?**

Approach: Join `payment`, `rental`, `inventory`, `film`, `film_category`, and `category`. Aggregate total revenue, rental count, average payment, and revenue-per-rental by category across all 16 genres. Rank categories and identify candidates for increased promotional investment versus stock reduction. Plot a bubble chart comparing rental volume against revenue-per-rental efficiency.

---

**Q4. What seasonal and temporal patterns exist in revenue, and when are the peak rental periods?**

Approach: Extract year, month, and calendar month dimensions from `payment_date`. Aggregate monthly revenue and transaction counts. Plot a dual-axis time series chart of revenue and transactions. Compute average daily revenue by calendar month to identify seasonal peaks and troughs that should inform promotional planning and staffing decisions.

---

### Theme 3 — Inventory and Operations

**Q5. How efficiently is the physical inventory being utilised, and which items are slow-moving or inactive?**

Approach: Join `inventory` to `rental` using a LEFT JOIN to capture items with zero rentals. Count total rentals per `inventory_id`. Compute the inventory turnover rate as `total_rentals / total_copies` per film title. Aggregate turnover by category. Flag items with fewer than 3 rentals as slow-moving and items with zero rentals as dead stock. Export a ranked list for operational review.

---

**Q6. How do Store 1 and Store 2 compare across revenue, customer count, inventory size, and efficiency?**

Approach: Aggregate total revenue, customer count, inventory items, and rental count per store using separate subqueries to prevent row multiplication. Derive six efficiency metrics: total revenue, total rentals, total customers, total inventory, revenue-per-inventory-item, and rentals-per-inventory-item. Compare stores across all six metrics using a grouped bar chart. Identify which store is more efficient and recommend rebalancing actions accordingly.

---

### Theme 4 — Innovation and Custom Analysis

**Q7. What film categories should be recommended to customers, and how can a priority-based recommendation engine be built from existing transaction data?**

Approach: Compute a normalised priority score for each category using a weighted formula: 60% revenue score + 40% rental volume score, both normalised to a 0–1 scale using min-max normalisation. Classify categories into High, Medium, and Low Priority tiers. Supplement with a revenue-versus-customer-reach scatter chart to identify upsell opportunities. This constitutes a content-based, category-level recommendation engine built entirely from transactional data without any external tools or ML libraries.

---

**Q8. Can customer churn risk be predicted using a feature-based scoring model, and which customers should be targeted first?**

Approach: Engineer three normalised behavioural features per customer from payment and rental history: recency (days since last payment / 180), frequency (1 − rentals/50), and monetary value (1 − total_spent/200). Combine into a weighted composite churn score (recency 50%, frequency 30%, spend 20%). Visualise the score distribution and its relationship to total spend. Produce a ranked High Risk customer list ready for immediate campaign targeting.

---

## 4. High-Level Analytical Approach

The project follows a fully reproducible, sequentially numbered pipeline:

| Step | Script | Purpose |
|---|---|---|
| 1 | `1_setup_validate.py` | Confirm database structure, row counts, data quality |
| 2 | `2_data_exploration.py` | Profile all tables, detect outliers, produce 4 EDA charts |
| 3 | `3_data_relationships.py` | Build 4 merged datasets, document joins, validate outputs |
| 4 | `4_analysis.py` | Execute all four analytical themes, export 12 tables and 8 charts |
| 5 | `5_dashboard.py` | Present live interactive analysis across 5 Streamlit pages |
| — | `Executive_Report.md` | 5-6 page professional report for non-technical stakeholders |
| — | `Architecture_Diagram.md` | Full system flow documentation |
| — | `Data_Description.md` | Table definitions, join logic, derived metrics, limitations |
| — | `innovation.md` | Detailed methodology and business value of novel contributions |