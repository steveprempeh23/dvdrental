# Architecture Diagram

**Project:** DVD Rental Big Data Management
**Student:** Nana Owusu Achiaw Prempeh
**Roll Number:** 2000250074
**Lecturer:** Jeremiah Ishaya
**Course:** DSA5102 Big Data Management

---

## 1. System Architecture Overview

The project follows a sequential, reproducible data analytics pipeline. The DVD Rental database is restored into PostgreSQL running inside Docker. Python scripts connect to the database, validate its structure, explore and profile the data, build merged analysis-ready datasets, perform advanced business analysis, and present findings through a Streamlit dashboard and professional written reports.

---

## 2. Full Architecture Flow

```
┌─────────────────────────────────┐
│      DVD Rental Backup File     │
│        dvdrental.tar            │
└────────────────┬────────────────┘
                 │
                 │  Restored via pgAdmin
                 ▼
┌─────────────────────────────────────────────┐
│          Docker Compose Environment         │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │  Service 1: PostgreSQL              │    │
│  │  Container: bdm-postgres-db         │    │
│  │  Port: 5432                         │    │
│  │  Database: dvd_rental               │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │  Service 2: pgAdmin                 │    │
│  │  Container: bdm-pgadmin-web         │    │
│  │  Port: 8080                         │    │
│  │  Browser: http://localhost:8080     │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │  Service 3: MinIO Object Storage    │    │
│  │  Container: bdm-minio-storage       │    │
│  │  API Port: 9000                     │    │
│  │  Console Port: 9001                 │    │
│  └─────────────────────────────────────┘    │
└───────────────────┬─────────────────────────┘
                    │
                    │  SQLAlchemy + psycopg2
                    ▼
┌─────────────────────────────────┐
│     PostgreSQL: dvd_rental      │
│                                 │
│  Tables:                        │
│  customer    payment   rental   │
│  film        inventory store    │
│  category    film_category      │
│  staff       actor    language  │
│  address     city     country   │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│     1_setup_validate.py         │
│                                 │
│  - Connect to database          │
│  - List all tables              │
│  - Validate critical tables     │
│  - Count rows per table         │
│  - Check data quality issues    │
│  - Export validation report     │
│                                 │
│  Outputs:                       │
│  exports/validation_report.txt  │
│  tables/table_row_counts.csv    │
│  tables/data_quality_summary    │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│     2_data_exploration.py       │
│                                 │
│  - Schema and type inspection   │
│  - Missing values check         │
│  - Descriptive statistics       │
│  - IQR outlier detection        │
│  - 4 exploratory charts         │
│                                 │
│  Outputs:                       │
│  tables/schema_summary.csv      │
│  tables/missing_values.csv      │
│  tables/descriptive_stats.csv   │
│  results/*.png (4 charts)       │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│    3_data_relationships.py      │
│                                 │
│  - Build 4 merged datasets      │
│  - Document join keys/types     │
│  - Validate merged outputs      │
│  - Export relationships report  │
│                                 │
│  Outputs:                       │
│  merges/customer_revenue.csv    │
│  merges/film_category_rev.csv   │
│  merges/store_performance.csv   │
│  merges/inventory_turnover.csv  │
│  exports/relationships_rpt.txt  │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│        4_analysis.py            │
│                                 │
│  D1 - Customer Analytics:       │
│    CLV, segmentation,           │
│    churn risk, behaviour        │
│                                 │
│  D2 - Revenue Optimisation:     │
│    Category performance,        │
│    temporal trends, pricing     │
│                                 │
│  D3 - Inventory & Operations:   │
│    Turnover rate, slow movers,  │
│    store comparison             │
│                                 │
│  D4 - Innovation:               │
│    Recommendation engine,       │
│    churn prediction model       │
│                                 │
│  Outputs:                       │
│  tables/*.csv (12 files)        │
│  results/*.png (8 charts)       │
│  exports/business_insights.txt  │
└────────────────┬────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌───────────────┐  ┌────────────────────┐
│  Output       │  │  5_dashboard.py    │
│  Folders      │  │                    │
│               │  │  Streamlit App     │
│  tables/      │  │  5 pages           │
│  merges/      │  │  10+ Plotly charts │
│  results/     │  │  7 KPI cards       │
│  exports/     │  │  http://localhost  │
│               │  │        :8501       │
└───────────────┘  └────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────┐
        │     Documentation & Reports     │
        │                                 │
        │  README.md                      │
        │  Executive_Report.md            │
        │  Architecture_Diagram.md        │
        │  Data_Description.md            │
        │  Business_Problem_Definition.md │
        │  innovation.md                  │
        └─────────────────────────────────┘
```

---

## 3. Component Descriptions

### Docker Compose

Defines and runs three services — PostgreSQL, pgAdmin, and MinIO — in a consistent, isolated environment. Any developer can reproduce the full environment with a single `docker compose up -d` command after cloning the repository and creating the `.env` file.

### PostgreSQL

The primary data source. Stores the restored DVD Rental database and is accessed by all Python scripts through SQLAlchemy and psycopg2.

### pgAdmin

Browser-based GUI for managing PostgreSQL. Used to restore the database backup and inspect tables directly without writing SQL.

### MinIO

Object storage service included in the Docker Compose setup. Available for storing large output files or future integration with data lake workflows.

### Python Scripts (1–5)

Handle all data work in sequence: database validation, exploratory analysis, dataset construction, advanced analysis, and dashboard delivery. Each script saves its outputs to clearly named folders.

### Output Folders

| Folder | Contents |
|---|---|
| `tables/` | CSV summaries — validation results, schema info, analysis tables |
| `merges/` | Merged datasets built by joining multiple database tables |
| `results/` | PNG chart files produced by matplotlib, seaborn, and plotly |
| `exports/` | Written text reports and business insight summaries |

### Streamlit Dashboard

Reads from the generated CSVs and connects directly to PostgreSQL via SQLAlchemy. Presents five pages of interactive analysis with KPI cards, Plotly charts, and data tables. Requires no separate data preparation step to launch.

---

## 4. Data Flow Summary

1. The `.tar` backup is restored into PostgreSQL via pgAdmin inside Docker.
2. Python connects to PostgreSQL via SQLAlchemy using credentials from `.env`.
3. `1_setup_validate.py` confirms the database structure and exports a validation report.
4. `2_data_exploration.py` profiles all tables and produces four exploratory charts.
5. `3_data_relationships.py` builds four merged datasets from multi-table joins and saves them as CSVs.
6. `4_analysis.py` reads from the database and merged CSVs, performs all four analytical themes, and saves 12 CSV tables and 8 chart files.
7. `5_dashboard.py` connects to the database directly and presents live interactive analysis across five pages.
8. Written documentation communicates findings, methodology, and recommendations to stakeholders.

---

## 5. Reproducibility

| Factor | How It Is Handled |
|---|---|
| Credentials | Stored in `.env`, never hardcoded |
| Services | Defined in `docker-compose.yml` |
| Python environment | Declared in `requirements.txt` and `dockerfile` |
| Script order | Numbered 1–5 with documented dependencies |
| Outputs | Written to named folders with consistent naming conventions |
| Assumptions | Documented in `Data_Description.md` and script docstrings |