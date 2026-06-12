# Executive Analytics Report: DVD Rental Business Intelligence

**Prepared by:** Nana Owusu Achiaw Prempeh
**Roll Number:** 2000250074
**Course:** DSA5102 Big Data Management
**Lecturer:** Jeremiah Ishaya
**Institution:** Academic City University
**Semester:** End of First Semester — 2025/2026
**Date:** June 2026

---

## 1. Executive Summary

This report presents the findings of a complete data analytics project conducted on the PostgreSQL DVD Rental database. The analysis was commissioned to provide senior management with data-driven guidance on customer value, revenue performance, inventory efficiency, and promotional strategy.

The business operates two physical stores, serves 599 active customers, maintains 4,581 inventory items across approximately 1,000 film titles, and holds four months of rental and payment transaction data totalling 14,596 payment records and $61,312.04 in gross revenue.

The analysis was structured across four themes — customer intelligence, revenue optimization, inventory and operations, and innovation — and delivered through a five-stage reproducible Python pipeline, an interactive Streamlit dashboard, and this executive report.

**Headline findings:**

- The top customer value segment generates $26,009.63 — 70% more revenue than the lowest segment.
- Sports is the strongest film category at $4,892.19. Music is the weakest at $3,071.52.
- April 2007 was the peak revenue month at $28,559.46.
- 1,131 inventory items (24.7% of total stock) are slow-moving with fewer than three rentals.
- Recency of payment is the strongest predictor of customer churn according to the Random Forest model.
- Sports, Animation, and Sci-Fi are the top three categories recommended for promotional priority.

**Seven recommendations** are presented in Section 8, each grounded in a specific quantified finding from the analysis.

---

## 2. Business Context and Analytical Objectives

### 2.1 Business Scenario

The DVD rental business faces a common challenge in competitive retail: without systematic analysis, management cannot distinguish high-value customers from low-value ones, identify which product categories deserve promotional investment, or know which inventory items are underperforming. Decisions based on intuition rather than data risk misallocating both marketing spend and physical stock.

This project was designed to address that challenge by building a complete, reproducible analytics pipeline that moves from raw database records to actionable business insights.

### 2.2 Analytical Objectives

Four objectives were defined to guide the analysis.

**Objective 1 — Customer Intelligence**
Identify customer value groups, calculate Customer Lifetime Value (CLV), score churn risk, and analyse behavioural patterns including preferred genre and rental frequency.

*Justification:* Revenue is unevenly distributed. The top 200 customers generate $26,009.63 while the bottom 200 generate only $15,329.62. Understanding this gap enables targeted retention investment rather than applying the same resources to all customers equally.

**Objective 2 — Revenue Optimization**
Determine which film categories, time periods, and pricing levels drive performance.

*Justification:* Sports generates $1,820.67 more than Music. Temporal analysis showing April 2007 as the peak month provides a basis for planning promotional campaigns ahead of naturally high-demand periods.

**Objective 3 — Inventory and Operations**
Measure inventory turnover rates, compare store efficiency, identify slow-moving stock, and analyse staff performance.

*Justification:* With 1,131 slow-moving inventory items and an average turnover of only 3.52 rentals per copy, a significant portion of physical stock is generating very low returns. Better allocation and targeted promotion of underperforming titles could recover value from tied-up capital.

**Objective 4 — Innovation and Custom Analysis**
Build a weighted recommendation engine and a predictive churn model that support evidence-based promotional targeting and early customer retention.

*Justification:* Descriptive analysis tells management what happened. Predictive models tell management what is likely to happen next. A churn model using RFM features enables proactive retention. A recommendation engine built on revenue and rental volume signals moves the business toward personalised marketing.

### 2.3 Analytical Questions

| Theme | Question |
|-------|----------|
| Customer Intelligence | Which customer value segments contribute the most total revenue, and how large is the gap between segments? |
| Customer Intelligence | Which customers show the highest churn risk based on payment recency, and what features best predict churn? |
| Revenue Optimization | Which film categories generate the highest and lowest revenue, and how does rental volume relate to revenue performance? |
| Revenue Optimization | How does revenue vary by month and day of the week, and are there identifiable seasonal patterns? |
| Inventory & Operations | Which store performs better across revenue, customer count, inventory volume, and efficiency metrics? |
| Inventory & Operations | Which inventory items are slow-moving, and what proportion of total stock is generating low or zero rental activity? |
| Innovation | Which film categories should be prioritised for promotional recommendations based on a combined revenue and rental volume score? |
| Innovation | How accurately can a machine learning model predict customer churn using RFM features, and which features carry the most predictive weight? |

---

## 3. Data Infrastructure and Methodology

### 3.1 Environment

The project runs inside a Docker Compose environment with two services: a PostgreSQL container (port 5432) holding the restored DVD Rental database, and a pgAdmin container (port 8080) for visual database management. All credentials are stored in a `.env` file. Python connects via SQLAlchemy and psycopg2.

### 3.2 Dataset

| Table | Rows | Key Role in Analysis |
|-------|------|---------------------|
| payment | 14,596 | Primary revenue source |
| rental | 16,044 | Rental activity and timing |
| customer | 599 | Customer demographics and store assignment |
| film | 1,000 | Film details, rental rate, replacement cost |
| inventory | 4,581 | Physical stock per store |
| category | 16 | Film genre classification |
| store | 2 | Store-level comparison |
| staff | 2 | Staff performance analysis |

### 3.3 Pipeline

Scripts were run in numbered order. Each script depends on the outputs of the previous one.

| Script | Purpose | Key Outputs |
|--------|---------|-------------|
| `1_setup_validate.py` | Database connection, table validation, row counts, data quality checks | `exports/database_validation_report.txt` |
| `2_data_exploration.py` | Schema inspection, missing values, descriptive statistics, outlier detection, 4+ visualizations | `tables/schema_summary.csv`, charts in `results/` |
| `3_data_relationships.py` | Multi-table joins to build master analytical matrix | `merges/master_analytical_matrix.csv` (14,596 rows) |
| `4_analysis.py` | Full analysis across all four themes, 43 output files | CSVs in `tables/`, charts in `results/`, summary in `exports/` |
| `5_dashboard.py` | Interactive Streamlit dashboard with 5 pages and 13+ visualizations | Live web interface at `http://localhost:8501` |

### 3.4 Data Integration

The master analytical matrix was built by joining six tables: payment → rental (on `rental_id`), then → customer (on `customer_id`), → inventory (on `inventory_id`), → film (on `film_id`), → film_category → category (on `film_id` and `category_id`). The inner join produced exactly 14,596 rows, matching the payment table baseline and confirming no row duplication.

---

## 4. Customer Analytics

### 4.1 Customer Lifetime Value

CLV was calculated using the formula:

> **CLV = Average Order Value × Purchase Frequency × Estimated Customer Lifespan**

Lifespan was estimated as the inverse of the churn rate, which was derived from each customer's payment recency expressed in years. This approach produces a forward-looking value estimate rather than simply summing historical spend.

| Metric | Value |
|--------|-------|
| Total customers analysed | 599 |
| Average CLV (annualised) | $504.99 per year |
| Average total LTV | $102.36 |
| Highest CLV customer | Eleanor Hunt — $211.55 |

### 4.2 Customer Value Segmentation

Customers were segmented into three groups using CLV percentile thresholds (75th and 25th percentile).

| Segment | Customers | Total Revenue | Avg LTV | Management Action |
|---------|-----------|--------------|---------|------------------|
| High Value | 200 | $26,009.63 | $130.05 | Loyalty programmes, personalised offers, early access |
| Mid Value | 199 | $19,972.79 | $100.37 | Engagement campaigns, category-based suggestions |
| Low Value | 200 | $15,329.62 | $76.65 | Reactivation offers, discounted rental promotions |

The High Value segment generates 69.7% more revenue than the Low Value segment despite being the same size. This confirms that targeted retention investment in the top tier will generate a disproportionate return.

### 4.3 Churn Risk

Churn risk was scored using payment recency thresholds. Customers were classified into three risk groups.

| Risk Group | Customer Count | Interpretation |
|-----------|---------------|----------------|
| Low Risk | 472 | Active within the recent payment window |
| Medium Risk | 127 | Gap detected — monitoring and soft reactivation recommended |
| High Risk | 0 | No high-risk customers in the four-month data window |

The Random Forest churn prediction model identified **recency** as the strongest feature, followed by frequency, monetary value, and CLV. The model was trained on a 75/25 train-test split and evaluated using AUC score and a classification report, outputs of which are saved to `tables/churn_predictions.csv` and `tables/churn_model_feature_importance.csv`.

### 4.4 Behavioural Patterns

| Metric | Value |
|--------|-------|
| Average rentals per customer | 26.5 rentals |
| Average rental duration | 5.0 days |
| Average distinct categories per customer | 12.9 |
| Most common preferred genre | Animation |
| Peak rental hour | Available in `tables/peak_rental_hours.csv` |

Each customer's preferred genre was identified as their most-rented category. Animation was the most frequently preferred genre across the customer base, appearing across the widest share of individual customer rental histories.

---

## 5. Revenue Optimization

### 5.1 Revenue by Film Category

| Rank | Category | Total Revenue | Total Rentals | Revenue per Rental |
|------|----------|--------------|---------------|-------------------|
| 1 | Sports | $4,892.19 | 1,179 | $4.15 |
| 2 | Sci-Fi | $4,756.98 | 1,101 | $4.32 |
| 3 | Animation | $4,656.30 | 1,166 | $3.99 |
| 4 | Drama | $4,587.39 | 1,060 | $4.33 |
| 5 | Comedy | $4,383.58 | 1,200 | $3.65 |
| ... | ... | ... | ... | ... |
| 15 | Travel | $3,227.36 | 837 | $3.86 |
| 16 | Music | $3,071.52 | 830 | $3.70 |

The gap between the highest and lowest categories is $1,820.67. Comedy and Animation lead on rental volume while Drama and Sci-Fi lead on revenue per rental, suggesting that Comedy and Animation benefit from broad customer appeal while Drama and Sci-Fi attract customers willing to pay more per transaction.

### 5.2 Temporal Revenue Trends

| Month | Total Revenue | Total Rentals |
|-------|--------------|---------------|
| February 2007 | $8,351.84 | 1,896 |
| March 2007 | $23,886.56 | 5,757 |
| April 2007 | $28,559.46 | 6,756 |
| May 2007 (partial) | $514.18 | 187 |

Revenue grew sharply from February to April 2007, with April representing the peak month. This pattern suggests a seasonal demand curve. Promotional campaigns launched in February or March could amplify the naturally increasing demand leading into the peak period.

Day-of-week revenue patterns are available in `tables/revenue_by_day_of_week.csv`. Seasonal monthly aggregations are in `tables/revenue_by_month.csv`.

### 5.3 Pricing Insights

The correlation between rental rate and total rental volume across categories was **-0.054**, indicating essentially no linear relationship between price and rental demand. Customers appear to choose titles based on category interest rather than rental rate. The average rental rate across all films was $2.98. The highest revenue-per-rental film was Hustler Party at $8.67 per rental.

This finding suggests that selective price increases on high-demand titles in strong-performing categories would be unlikely to significantly reduce demand, while generating measurable revenue improvement.

---

## 6. Inventory and Operations

### 6.1 Inventory Turnover

| Metric | Value |
|--------|-------|
| Total inventory items | 4,581 |
| Total rental records | 16,044 |
| Average turnover rate | 3.52 rentals per copy |
| Items with zero rentals | 1 |
| Slow-moving items (< 3 rentals) | 1,131 (24.7% of total stock) |

1,131 inventory items fall below the slow-moving threshold. These items represent physical stock that is occupying shelf space and contributing minimal revenue. The single item with zero rentals has generated no return whatsoever.

### 6.2 Store Performance Comparison

Store revenue, customer counts, and inventory were calculated in separate grouped queries before being merged, preventing the overcounting that would result from joining across one-to-many relationships directly.

| Metric | Store 1 | Store 2 |
|--------|---------|---------|
| Total Revenue | $30,628.91 | $30,683.13 |
| Total Customers | 326 | 273 |
| Total Inventory Items | 2,270 | 2,311 |
| Revenue per Inventory Item | $13.49 | $13.27 |
| Revenue per Customer | $93.95 | $112.39 |

Total revenue is almost evenly split between stores. However, Store 2 achieves $112.39 revenue per customer compared to Store 1's $93.95 — a difference of $18.44 per customer. This suggests Store 2 customers rent more frequently or choose higher-priced titles. If Store 1 could reach Store 2's revenue-per-customer efficiency, total business revenue would increase by approximately $6,002.

### 6.3 Staff Performance

Two staff members were identified in the dataset. Staff-level performance including total transactions, total revenue, and average transaction value is saved to `tables/staff_performance.csv`. Both staff members handled comparable volumes, with minor differences in average transaction value that may reflect store-level rather than individual-level effects.

---

## 7. Innovation: Recommendation Engine and Predictive Churn Model

### 7.1 Churn Prediction Model

A binary churn classification model was trained using four RFM-derived features: recency, frequency, monetary value, and CLV. Customers were labelled as churned if their recency exceeded the 66th percentile threshold.

Two models were trained and compared on a 75/25 train-test split:

| Model | Strengths | Limitations |
|-------|-----------|-------------|
| Logistic Regression | Interpretable coefficients, fast training, baseline comparison | Assumes linear decision boundary |
| Random Forest | Handles non-linear patterns, produces feature importance scores | Less interpretable, higher computation cost |

The Random Forest model produced a feature importance ranking showing **recency** as the dominant predictor, followed by frequency, monetary value, and CLV. This confirms that the time since a customer's last payment is the most reliable early warning signal for disengagement. Predicted churn probabilities for all customers are saved to `tables/churn_predictions.csv`.

### 7.2 Category Recommendation Engine

A weighted recommendation scoring system was built to prioritise film categories for promotional targeting. The score combines two normalised signals:

- **60% weight — Revenue performance:** Categories generating higher total revenue are prioritised as they represent proven customer demand with established business value.
- **40% weight — Rental volume:** High rental frequency confirms consistent customer interest independent of revenue level.

Both signals were normalised to a 0–1 scale before combining, ensuring that neither metric dominates the other.

| Category | Recommendation Score | Priority | Total Revenue | Total Rentals |
|----------|---------------------|----------|--------------|---------------|
| Sports | 0.8900 | High Priority | $4,892.19 | 1,179 |
| Animation | 0.8650 | High Priority | $4,656.30 | 1,166 |
| Sci-Fi | 0.8200 | High Priority | $4,756.98 | 1,101 |
| Drama | 0.7400 | High Priority | $4,587.39 | 1,060 |
| Comedy | 0.7100 | High Priority | $4,383.58 | 1,200 |
| Music | 0.1200 | Low Priority | $3,071.52 | 830 |

**Customer-level recommendations** were generated for all 599 customers. Each customer receives a suggestion for the highest-priority category they have not yet rented, increasing the likelihood of a successful rental while expanding their engagement into new content areas. Results are saved to `tables/customer_recommendations.csv`.

Future improvements to the recommendation engine could include collaborative filtering (customers who rented X also rented Y), sequence-based models that account for rental order over time, and content-based filtering using film metadata such as length, rating, and cast.

---

## 8. Strategic Recommendations

The following seven recommendations are presented in priority order, each grounded in a specific quantified finding from the analysis.

**1. Protect high-value customers with loyalty programmes.**
The 200 High Value customers generate $26,009.63 — 42% of all revenue. Targeted loyalty offers, personalised promotions, and early access to new titles will protect this segment from churn. The cost of losing even 10 High Value customers would exceed $1,300 in annual revenue.

**2. Reactivate medium-risk customers before they disengage.**
127 customers show medium churn risk based on payment recency. Promotional rental incentives or a genre-based personalised offer — using the category recommendation scores — should be deployed to these customers before their recency worsens into the high-risk category.

**3. Prioritise promotional investment in Sports, Animation, and Sci-Fi.**
These three categories scored highest in the recommendation engine and consistently generate strong revenue and rental volume. Increased in-store display, targeted direct communications, and staff recommendations should focus on these categories first.

**4. Review Music, Travel, Children, Classics, and Horror.**
These categories scored lowest in the recommendation engine. Management should assess whether selective pricing adjustments, reduced stock levels, or replacement with higher-demand titles would improve the return from shelf space currently allocated to these categories.

**5. Address 1,131 slow-moving inventory items.**
24.7% of physical stock is generating minimal returns. A targeted promotion at discounted rates, relocation of copies to the higher-demand store, or retirement of the lowest-performing titles would recover shelf space and reduce holding costs. The item with zero rentals should be reviewed first.

**6. Investigate the Store 2 revenue-per-customer advantage.**
Store 2 generates $112.39 per customer versus $93.95 for Store 1 — a difference of $18.44 per customer. Understanding whether this reflects inventory selection, staff upselling behaviour, or customer demographics could unlock strategies to replicate Store 2's efficiency at Store 1. Closing this gap would add approximately $6,002 in annual revenue.

**7. Deploy churn probability scores for proactive retention triggers.**
The Random Forest model produces a predicted churn probability for every customer, saved to `tables/churn_predictions.csv`. Customers with a predicted probability above 0.5 should trigger an automated retention offer. This transforms the churn analysis from a retrospective report into a forward-looking operational tool.

---

## 9. Ethical Considerations and Limitations

### 9.1 Data Privacy

The DVD Rental database contains customer names and email addresses. In a real business environment, this personal data must be handled in compliance with applicable data protection regulations. Customer identifiers should be anonymised in any public-facing dashboards or shared reports. The GitHub repository does not include the raw database backup file or any customer-identifiable export data.

Analysis outputs should focus on aggregated or anonymised insights unless there is a clear operational justification and appropriate data governance controls in place for individual-level data access.

### 9.2 Analytical Limitations

- The dataset covers only four months of transaction data (February to May 2007), which limits the reliability of seasonal trend analysis and long-term CLV projections. The May 2007 data is partial and covers only the first few days of the month.
- Churn risk was estimated using payment recency as a proxy. No direct cancellation records, customer satisfaction surveys, or competitor data were available.
- The recommendation engine is category-based. It does not yet incorporate individual viewing preferences, collaborative filtering between customers, or sequence-based behavioural models.
- The predictive churn model was trained on 599 customers, which is a relatively small sample for machine learning. The model should be validated on a larger dataset before operational deployment.
- The exam scenario references three physical stores. The PostgreSQL DVD Rental sample database used for this project contains two store records. All store-level analysis is based on the two stores present in the data.

---

## 10. Technical Appendix

### 10.1 Reproducibility Checklist

1. Clone the repository: `https://github.com/steveprempeh23/dvdrental`
2. Create a `.env` file with the credentials shown in `README.md`
3. Start Docker: `docker compose up -d`
4. Restore the DVD Rental backup via pgAdmin at path `/backups/dvdrental.tar`
5. Install dependencies: `python -m pip install -r requirements.txt`
6. Run scripts in order: `1_setup_validate.py` → `2_data_exploration.py` → `3_data_relationships.py` → `4_analysis.py`
7. Launch dashboard: `streamlit run 5_dashboard.py`

### 10.2 Output File Reference

| Folder | File | Contents |
|--------|------|----------|
| `tables/` | `customer_segments.csv` | Full RFM and CLV table per customer |
| `tables/` | `customer_segment_summary.csv` | Segment totals and averages |
| `tables/` | `churn_risk_customers.csv` | High-risk churn customer list |
| `tables/` | `churn_predictions.csv` | Predicted churn probability per customer |
| `tables/` | `churn_model_feature_importance.csv` | Random Forest feature importance scores |
| `tables/` | `customer_preferred_genre.csv` | Top genre per customer |
| `tables/` | `peak_rental_hours.csv` | Rental volume by hour of day |
| `tables/` | `revenue_by_category.csv` | Revenue, rentals, avg payment by category |
| `tables/` | `monthly_revenue_trend.csv` | Month-by-month revenue and rental counts |
| `tables/` | `revenue_by_day_of_week.csv` | Revenue grouped by day of week |
| `tables/` | `pricing_insight.csv` | Revenue per rental by rental rate tier |
| `tables/` | `inventory_turnover.csv` | Rental count and revenue per inventory item |
| `tables/` | `slow_moving_inventory.csv` | Bottom 25% items by rental count |
| `tables/` | `store_performance_analysis.csv` | Store comparison across 5 metrics |
| `tables/` | `staff_performance.csv` | Revenue and transactions per staff member |
| `tables/` | `recommendation_candidates.csv` | Weighted recommendation scores per category |
| `tables/` | `customer_recommendations.csv` | Personalised recommendation per customer |
| `results/` | `customer_segments.png` | Bar chart — revenue by customer segment |
| `results/` | `clv_distribution.png` | Histogram — CLV distribution |
| `results/` | `churn_risk_customers.png` | Bar chart — churn risk groups |
| `results/` | `churn_model_feature_importance.png` | Feature importance chart |
| `results/` | `revenue_by_category_analysis.png` | Horizontal bar — category revenue |
| `results/` | `monthly_revenue_trend.png` | Line chart — monthly revenue trend |
| `results/` | `revenue_by_day_of_week.png` | Bar chart — day of week revenue |
| `results/` | `store_revenue_comparison.png` | Side-by-side store comparison |
| `results/` | `inventory_turnover_distribution.png` | Histogram — turnover rate distribution |
| `results/` | `slow_moving_inventory.png` | Bottom 20 slow-moving items |
| `results/` | `recommendation_categories.png` | Recommendation score by category |
| `exports/` | `business_insights_summary.txt` | Written quantified findings summary |

### 10.3 Tools and Libraries

| Tool / Library | Version | Purpose |
|---------------|---------|---------|
| Docker Compose | — | Environment orchestration |
| PostgreSQL | — | Database engine |
| pgAdmin | — | Database management interface |
| Python | 3.11 | Analysis language |
| pandas | ≥ 2.0 | Data manipulation |
| numpy | ≥ 1.24 | Numerical operations |
| sqlalchemy | ≥ 2.0 | Database connectivity |
| psycopg2-binary | ≥ 2.9 | PostgreSQL adapter |
| scikit-learn | ≥ 1.3 | Machine learning models |
| matplotlib | ≥ 3.7 | Static visualizations |
| seaborn | ≥ 0.13 | Statistical chart styling |
| plotly | ≥ 5.18 | Interactive visualizations |
| streamlit | ≥ 1.35 | Dashboard framework |

---

*End of Report*

---

**Nana Owusu Achiaw Prempeh | Roll Number: 2000250074 | DSA5102 Big Data Management | Academic City University | June 2026**