# Data Description

**Project:** DVD Rental Big Data Management
**Student:** Nana Owusu Achiaw Prempeh
**Roll Number:** 2000250074
**Lecturer:** Jeremiah Ishaya
**Course:** DSA5102 Big Data Management

---

## 1. Dataset Overview

The project uses the PostgreSQL DVD Rental sample database, which models the operations of a DVD rental business. It contains data about customers, films, rentals, payments, inventory, staff, stores, and film categories.

The database covers approximately 600 customers, 1,000 film titles across 16 genre categories, 4,500+ physical inventory copies, and two years of rental and payment transaction history across two stores.

---

## 2. Table Descriptions

### customer

One record per registered customer.

| Column | Type | Description |
|---|---|---|
| `customer_id` | integer | Primary key |
| `store_id` | smallint | Store this customer is linked to (FK → store) |
| `first_name` | varchar | Customer first name |
| `last_name` | varchar | Customer last name |
| `email` | varchar | Customer email address |
| `active` | integer | 1 = active, 0 = inactive |
| `create_date` | date | Date the customer record was created |

Used for: customer segmentation, CLV, churn risk, behavioural analysis.

---

### payment

One record per payment transaction.

| Column | Type | Description |
|---|---|---|
| `payment_id` | integer | Primary key |
| `customer_id` | integer | Customer who paid (FK → customer) |
| `staff_id` | smallint | Staff who handled the transaction (FK → staff) |
| `rental_id` | integer | Rental this payment relates to (FK → rental) |
| `amount` | numeric | Payment amount in dollars |
| `payment_date` | timestamp | Date and time the payment was made |

Used for: all revenue analysis, CLV calculation, churn scoring.

---

### rental

One record per rental transaction.

| Column | Type | Description |
|---|---|---|
| `rental_id` | integer | Primary key |
| `rental_date` | timestamp | Date and time the rental started |
| `inventory_id` | integer | Physical copy rented (FK → inventory) |
| `customer_id` | integer | Customer who rented (FK → customer) |
| `return_date` | timestamp | Date returned (NULL if not yet returned) |
| `staff_id` | smallint | Staff who handled the rental (FK → staff) |

Used for: rental frequency, rental duration, inventory turnover.

---

### film

One record per film title.

| Column | Type | Description |
|---|---|---|
| `film_id` | integer | Primary key |
| `title` | varchar | Film title |
| `description` | text | Short synopsis |
| `release_year` | year | Year of release |
| `language_id` | tinyint | Film language (FK → language) |
| `rental_duration` | tinyint | Days customer may keep the film |
| `rental_rate` | numeric | Price per rental in dollars |
| `length` | smallint | Film duration in minutes |
| `replacement_cost` | numeric | Cost to replace a lost or damaged copy |
| `rating` | mpaa_rating | Age rating: G, PG, PG-13, R, NC-17 |

Used for: film-level pricing analysis, inventory analysis, recommendation engine.

---

### category

One record per genre category.

| Column | Type | Description |
|---|---|---|
| `category_id` | integer | Primary key |
| `name` | varchar | Category name (e.g. Action, Comedy, Drama) |

Used for: grouping films, revenue by category, recommendation scoring.

---

### film_category

Bridge table linking films to categories. Each film belongs to exactly one category.

| Column | Type | Description |
|---|---|---|
| `film_id` | integer | FK → film |
| `category_id` | integer | FK → category |

Used for: joining `film` to `category` in all category-level analyses.

---

### inventory

One record per physical copy of a film held at a store.

| Column | Type | Description |
|---|---|---|
| `inventory_id` | integer | Primary key |
| `film_id` | integer | Film this copy belongs to (FK → film) |
| `store_id` | tinyint | Store where this copy is held (FK → store) |

Used for: inventory turnover analysis, dead stock identification, store efficiency ratios.

---

### store

One record per store location.

| Column | Type | Description |
|---|---|---|
| `store_id` | tinyint | Primary key |
| `manager_staff_id` | tinyint | Store manager (FK → staff) |
| `address_id` | smallint | Physical address (FK → address) |

Used for: store-level performance comparisons.

---

### staff

One record per staff member.

| Column | Type | Description |
|---|---|---|
| `staff_id` | tinyint | Primary key |
| `first_name` | varchar | First name |
| `last_name` | varchar | Last name |
| `store_id` | tinyint | Store where staff member works (FK → store) |
| `active` | boolean | Whether currently employed |
| `username` | varchar | Login username |

Used for: transaction context and store operations.

---

## 3. Entity Relationship Summary

```
customer ──< payment >── rental ──< inventory >── film ──< film_category >── category
                                        │
                                      store
```

| Relationship | Join Key | Type |
|---|---|---|
| customer → payment | `customer_id` | One-to-many |
| payment → rental | `rental_id` | One-to-one |
| rental → inventory | `inventory_id` | Many-to-one |
| inventory → film | `film_id` | Many-to-one |
| film → film_category | `film_id` | One-to-one |
| film_category → category | `category_id` | Many-to-one |
| inventory → store | `store_id` | Many-to-one |
| customer → store | `store_id` | Many-to-one |

---

## 4. Merged Datasets Built in This Project

### customer_revenue_dataset.csv

Joins `customer` and `payment`.

Purpose: Customer lifetime value, segmentation, churn risk.

Key derived fields:
- `total_payments` — COUNT of payments per customer
- `lifetime_value` — SUM of payment amounts
- `avg_payment` — AVG payment amount
- `last_payment_date` — MAX payment date
- `annualised_clv` — (lifetime_value / active_days) × 365

---

### film_category_revenue_dataset.csv

Joins `film`, `film_category`, `category`, `inventory`, `rental`, `payment`.

Purpose: Revenue by category, pricing insight, recommendation scoring.

Key derived fields:
- `total_rentals` — COUNT of rentals per film
- `total_revenue` — SUM of payments
- `revenue_per_rental` — total_revenue / total_rentals

---

### store_performance_dataset.csv

Joins `store`, `customer`, `inventory`, `rental`, `payment`.

Purpose: Store-level performance comparison and efficiency ratios.

Key derived fields:
- `total_customers` — customers per store
- `total_inventory` — inventory items per store
- `total_rentals` — rentals per store
- `total_revenue` — revenue per store
- `revenue_per_inventory` — total_revenue / total_inventory
- `rentals_per_inventory` — total_rentals / total_inventory

> Note: Aggregations were computed in separate subqueries before joining to prevent row multiplication from one-to-many relationships.

---

### inventory_turnover_dataset.csv

Joins `inventory`, `film`, `film_category`, `category`, `rental`, `payment`.

Purpose: Per-copy rental activity, dead stock detection, turnover rate by category.

Key derived fields:
- `rental_count` — rentals for this specific physical copy
- `total_revenue` — revenue from this copy
- `last_rental_date` — most recent rental date
- `turnover_rate` — rental_count / copies of this title

---

## 5. Key Analytical Metrics

| Metric | Formula | Purpose |
|---|---|---|
| Customer Lifetime Value (CLV) | `SUM(payment.amount)` per customer | Total historical revenue per customer |
| Annualised CLV | `CLV / active_days × 365` | Comparable annual rate across customers |
| Churn Score | `0.50 × recency + 0.30 × frequency + 0.20 × spend` | RFM-based churn risk (0 = safe, 1 = high risk) |
| Inventory Turnover Rate | `total_rentals / total_copies` per film | Efficiency of physical stock usage |
| Revenue per Inventory Item | `total_revenue / total_inventory` per store | Store operational efficiency |
| Recommendation Priority Score | `0.60 × rev_score + 0.40 × rent_score` | Normalised category promotion priority (0–1) |

---

## 6. Data Quality Notes

Checks performed in `1_setup_validate.py` and `2_data_exploration.py`:

- All 15 critical tables confirmed present
- Row counts verified for all tables
- Missing (NULL) value counts checked per column
- Duplicate record checks performed
- Schema and data type inspection completed
- IQR outlier detection applied to numeric columns in `payment`, `film`, `rental`, `inventory`

The dataset was confirmed clean for all core transactional tables. No critical missing values were found in `payment`, `rental`, or `customer`. The `rental.return_date` column contains NULLs for items not yet returned, which is expected behaviour and was handled in all queries using `WHERE return_date IS NOT NULL` where rental duration was calculated.

---

## 7. Limitations

- The data is historical and does not reflect current business conditions or competitor activity.
- `rental.return_date` is NULL for unreturned items; rental duration analysis excludes these records.
- Churn risk uses payment recency as a proxy for disengagement — a seasonal renter may appear at risk without being genuinely churned.
- The recommendation engine operates at category level only, not at individual customer level.
- Staff performance analysis is limited by the small number of staff records in the dataset.

---

## 8. Ethical Considerations

The `customer` table contains personally identifiable information (names and email addresses). In this project:

- All charts and reports use `customer_id` or aggregated metrics rather than displaying individual names.
- The `.env` file storing database credentials is excluded from version control.
- No customer data is exposed in any public-facing output.

In any real deployment, access to this data must be restricted to authorised personnel and all customer communications based on this analysis must comply with applicable data privacy regulations.