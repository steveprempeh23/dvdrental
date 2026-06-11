# DVD Rental Big Data Management Project

**Student:** Nana Owusu Achiaw Prempeh
**Roll Number:** 2000250074
**Lecturer:** Jeremiah Ishaya
**Course:** DSA5102 Big Data Management
**Semester:** End of First Semester — 2025/2026

---

## 1. Project Overview

This project is an industry-based analytics capstone which uses the PostgreSQL DVD Rental database to analyse customer behaviour, revenue performance, inventory efficiency, store operations, and recommendation opportunities.

The objective is to deliver a complete data analytics workflow covering Docker-based environment setup, database validation, exploratory data analysis, data integration, advanced business analysis, an interactive Streamlit dashboard, and a professional executive report.

The project was developed using Docker, PostgreSQL, Python, Pandas, SQLAlchemy, Matplotlib, Seaborn, Plotly, and Streamlit.

---

## 2. Project Structure

```
dvdrental/
│
├── .env
├── docker-compose.yml
├── dockerfile
├── requirements.txt
│
├── 1_setup_validate.py
├── 2_data_exploration.py
├── 3_data_relationships.py
├── 4_analysis.py
├── 5_dashboard.py
│
├── README.md
├── Executive_Report.md
├── Architecture_Diagram.md
├── Data_Description.md
├── Business_Problem_Definition.md
├── innovation.md
│
├── data/
│   └── backups/
│
├── exports/
├── tables/
├── merges/
└── results/
```

---

## 3. Tools and Libraries Used

### Main Tools

- Docker
- Docker Compose
- PostgreSQL
- pgAdmin
- Python 3.11
- Streamlit

### Python Libraries

- pandas
- sqlalchemy
- psycopg2-binary
- python-dotenv
- matplotlib
- seaborn
- plotly
- streamlit
- scikit-learn

---

## 4. Environment Variables

The project uses a `.env` file to store database credentials. Create a file named `.env` in the root of the project folder with the following content:

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=dvd_rental
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=adminpassword
```

> The `.env` file is excluded from version control to protect credentials. Never commit it to GitHub.

---

## 5. Docker Setup

The project uses Docker Compose to run PostgreSQL and pgAdmin together in containers.

To start the services:

```
docker compose up -d
```

To check that the containers are running:

```
docker ps
```

Expected containers:

```
bdm-postgres-db
bdm-pgadmin-web
```

pgAdmin can be opened in the browser at:

```
http://localhost:8080
```

Login using:

```
Email:    admin@example.com
Password: adminpassword
```

---

## 6. PostgreSQL and pgAdmin Connection

In pgAdmin, register the PostgreSQL server using the following details:

```
Name:                 DVD Rental DB
Host name/address:    postgres
Port:                 5432
Maintenance database: dvd_rental
Username:             postgres
Password:             your_secure_password
```

> The host is `postgres` (not `localhost`) inside pgAdmin because both services are in the same Docker Compose network and communicate using the service name.

When running Python scripts from your local machine, the host is `localhost`.

---

## 7. Database Restoration

Place the DVD Rental backup file at:

```
data/backups/dvdrental.tar
```

In pgAdmin, restore from the path (as seen inside the Docker container):

```
/backups/dvdrental.tar
```

After restoration, the following critical tables should be present:

```
actor         address       category      city          country
customer      film          film_actor    film_category inventory
language      payment       rental        staff         store
```

---

## 8. Installing Python Requirements

```
python -m pip install -r requirements.txt
```

If `psycopg2` fails, install the binary version directly:

```
python -m pip install psycopg2-binary
```

---

## 9. How to Run the Project

Run all scripts in numbered order. Each script depends on the outputs of the previous one.

### Step 1 — Database Validation

```
python 1_setup_validate.py
```

Connects to PostgreSQL, lists all tables, validates critical DVD Rental tables, counts rows, checks data quality, and exports a validation report.

Main outputs:
```
exports/database_validation_report.txt
tables/table_row_counts.csv
tables/data_quality_summary.csv
```

---

### Step 2 — Exploratory Data Analysis

```
python 2_data_exploration.py
```

Inspects schemas and data types, checks for missing values, produces descriptive statistics, detects outliers using IQR, and generates four business visualisations.

Main outputs:
```
tables/schema_summary.csv
tables/missing_values_summary.csv
tables/descriptive_statistics.csv
tables/outlier_summary.csv
results/monthly_revenue.png
results/top_film_categories_by_revenue.png
results/top_customers_by_revenue.png
results/rentals_by_store.png
```

---

### Step 3 — Data Relationship Mapping

```
python 3_data_relationships.py
```

Builds merged analysis-ready datasets by joining multiple database tables. Documents join keys, join types, and validates merged outputs.

Main outputs:
```
merges/customer_revenue_dataset.csv
merges/film_category_revenue_dataset.csv
merges/store_performance_dataset.csv
merges/inventory_turnover_dataset.csv
exports/data_relationships_report.txt
```

---

### Step 4 — Advanced Business Analysis

```
python 4_analysis.py
```

Performs customer lifetime value calculation, segmentation, churn risk scoring, behavioural pattern analysis, revenue analysis by category, temporal trend analysis, inventory turnover analysis, store performance comparison, and category-based recommendation scoring.

Main outputs:
```
tables/customer_clv.csv
tables/customer_segments.csv
tables/churn_risk_customers.csv
tables/customer_behavioural_patterns.csv
tables/revenue_by_category.csv
tables/seasonal_revenue_pattern.csv
tables/pricing_insight.csv
tables/inventory_turnover.csv
tables/inventory_turnover_by_category.csv
tables/slow_moving_inventory.csv
tables/store_performance.csv
tables/recommendation_candidates.csv
exports/business_insights_summary.txt
results/d1_customer_lifetime_value.png
results/d1_churn_risk.png
results/d1_behavioural_patterns.png
results/d2_revenue_by_category.png
results/d2_temporal_revenue_trends.png
results/d3_inventory_turnover.png
results/d3_store_comparison.png
results/d4_recommendation_engine.png
```

---

### Step 5 — Streamlit Dashboard

```
streamlit run 5_dashboard.py
```

Opens in the browser at:

```
http://localhost:8501
```

The dashboard includes:

- Executive overview with 7 KPI cards
- Customer Intelligence page (CLV, segmentation, churn risk, behavioural patterns)
- Revenue Optimisation page (category performance, temporal trends, seasonality)
- Inventory and Operations page (turnover, slow-movers, store comparison)
- Innovation and Recommendations page (priority engine, churn prediction model)
- Multi-page sidebar navigation
- 10+ interactive Plotly charts

---

## 10. Analytical Areas Covered

### Customer Analytics

- Customer Lifetime Value (CLV) and annualised CLV
- Value segmentation: Low Value, Mid Value, High Value
- Churn risk scoring using RFM-inspired composite score
- Behavioural patterns: rental frequency, duration, favourite categories

### Revenue Optimisation

- Revenue by film category (all 16 categories)
- Rental volume and revenue-per-rental efficiency
- Monthly revenue trends and transaction volumes
- Seasonality analysis by calendar month
- Pricing insight: rental rate vs rental demand correlation

### Inventory and Operations

- Inventory turnover rate per copy and per category
- Dead stock and slow-moving inventory identification
- Store comparison across 6 performance metrics
- Revenue-per-inventory-item and rentals-per-inventory-item efficiency ratios

### Innovation and Custom Analysis

- Category recommendation priority engine (normalised 60/40 weighted score)
- Feature-based churn prediction model (RFM composite, recency 50%, frequency 30%, spend 20%)
- Revenue vs customer reach quadrant analysis
- Ranked intervention lists for marketing campaigns

---

## 11. Key Findings Summary

Customer value is unevenly distributed. The High Value segment generated $26,009.63 compared to $15,329.62 from the Low Value segment. Sports was the strongest film category by revenue at $4,892.19 from 1,179 rentals. Music was the lowest revenue category at $3,071.52.

Store 1 generated $9,985,024.66 in total revenue with 326 customers and a revenue-per-inventory ratio of $4,398.69. Store 2 generated $8,376,494.49 with 273 customers and a revenue-per-inventory ratio of $3,624.62, indicating Store 1 is operationally more efficient per inventory item.

The inventory analysis identified 1 zero-rental item and 1,131 slow-moving copies with fewer than 3 rentals, representing a significant proportion of the total 4,581 inventory items.

---

## 12. Main Recommendations

1. Protect High Value customers through a dedicated loyalty programme with personalised offers.
2. Re-engage High and Medium Risk churn customers with time-limited discount campaigns.
3. Prioritise Sports, Animation, and Sci-Fi categories in promotional and stocking decisions.
4. Review and reduce the 1,131 slow-moving inventory items to free up capital and shelf space.
5. Reallocate inventory from Store 2 to Store 1 for high-demand titles to maximise efficiency.
6. Run promotional campaigns in peak rental months identified from the seasonal analysis.
7. Extend the recommendation engine to customer-level collaborative filtering as a future step.

---

## 13. Ethical Considerations and Limitations

The dataset contains personally identifiable customer information including names and email addresses. In any real-world deployment, analysis should use aggregated metrics rather than exposing individual identities. All customer-facing communications must comply with applicable data privacy regulations and provide clear opt-out options.

The analysis is based on historical transaction data only and does not account for competitor behaviour, customer satisfaction, marketing campaigns, or the impact of streaming services on DVD rental demand. Churn risk was estimated from payment recency rather than direct cancellation data. The recommendation engine operates at category level and does not personalise at the individual customer level.

---

## 14. Notes on Reproducibility

The project is fully reproducible because:

- All credentials are stored in `.env` and not hardcoded anywhere in the code
- Services are managed consistently through Docker Compose
- All Python dependencies are declared in `requirements.txt`
- The `dockerfile` defines the Python environment consistently
- Scripts are numbered and must be run in the order shown
- All outputs are written to clearly named and structured folders
- Documentation covers every assumption, join decision, and analytical limitation

---

## 15. Author

**Name:** Nana Owusu Achiaw Prempeh
**Roll Number:** 2000250074
**Course:** DSA5102 Big Data Management
**Lecturer:** Jeremiah Ishaya
**Institution:** Academic City University — Faculty of Computational Sciences and Informatics