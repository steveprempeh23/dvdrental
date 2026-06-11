# Innovation and Excellence

**Project:** DVD Rental Big Data Management
**Student:** Nana Owusu Achiaw Prempeh
**Roll Number:** 2000250074
**Lecturer:** Jeremiah Ishaya
**Course:** DSA5102 Big Data Management — Part F (5 bonus marks)

---

## Overview

This document presents two novel analytical contributions that go beyond standard descriptive analysis. Both are built entirely from the existing transaction data, require no external ML infrastructure, produce outputs that a non-technical manager can understand and act on immediately, and have a clearly articulated path toward more sophisticated future implementations.

---

## Innovation 1 — RFM-Based Customer Churn Scoring Model

### What Was Built

A fully interpretable, feature-engineered churn prediction model that computes a composite risk score for every customer without requiring labelled training data, machine learning libraries, or historical churn outcomes.

### Method

Three behavioural features are engineered from payment and rental history, each normalised to a 0–1 scale:

**Recency** (how long since the customer last rented):
```
recency_norm = min(days_since_last_payment, 180) / 180
```

**Frequency** (inverse of rental activity):
```
freq_norm = 1 − min(total_rentals, 50) / 50
```

**Monetary Value** (inverse of total spend):
```
spend_norm = 1 − min(total_spent, 200) / 200
```

Combined into a weighted composite churn score:
```
churn_score = (0.50 × recency_norm) + (0.30 × freq_norm) + (0.20 × spend_norm)
```

Risk classification using `pd.cut` with `include_lowest=True`:

| Score Range | Risk Label |
|---|---|
| 0.00 – 0.33 | Low Risk |
| 0.34 – 0.60 | Medium Risk |
| 0.61 – 1.00 | High Risk |

### Why It Is Novel

Standard analysis of this dataset stops at ranking customers by revenue. This model goes further by combining three independent behavioural signals into a single continuous score that ranks every customer on a spectrum from fully engaged to at risk of permanent disengagement.

The weight assignments follow the established RFM (Recency, Frequency, Monetary) framework from customer analytics literature, which consistently identifies recency as the strongest predictor of future engagement. The weights were calibrated to the DVD rental context, where inactivity (recency) is a stronger churn signal than spend level given the low price-per-transaction nature of the business.

### Business Value

The model produces a ranked intervention list that a marketing team can act on the same day. High Risk customers can be targeted with personalised re-engagement offers before they disengage permanently. The cost of running this model is zero — it uses only the existing database connection and standard Python libraries already present in the project.

Unlike a black-box ML classifier, every score can be explained in plain language: when did this customer last rent, how often do they rent, and how much have they spent? This interpretability is essential for a business that needs to justify campaign targeting decisions to non-technical managers.

### Results

From the analysis run on the DVD Rental dataset:
- 472 customers classified as Low Risk
- 127 customers classified as Medium Risk
- High Risk customers identified for immediate re-engagement targeting

### Limitations

The model uses payment recency as a proxy for churn intent. It cannot distinguish between a genuinely churned customer and a seasonal renter in a quiet period. Direct cancellation data would improve accuracy. The feature weights were set using domain knowledge rather than empirical optimisation.

### Next Step

A logistic regression classifier trained on historical labelled churn data using scikit-learn would be the natural extension. The same three features plus customer tenure and store ID would serve as inputs. With 12 months of labelled churn history, this would meaningfully outperform the rule-based approach and enable probability calibration.

---

## Innovation 2 — Normalised Category Recommendation Priority Engine

### What Was Built

A category-level recommendation priority engine that ranks all 16 film categories on a continuous priority score, enabling data-driven decisions about which categories to promote, stock, and feature in customer communications.

### Method

Two signals are computed for each category and normalised to a 0–1 scale using min-max normalisation:

**Revenue score:**
```
rev_score = (category_revenue − min_revenue) / (max_revenue − min_revenue)
```

**Rental volume score:**
```
rent_score = (category_rentals − min_rentals) / (max_rentals − min_rentals)
```

Combined into a weighted priority score:
```
priority_score = (0.60 × rev_score) + (0.40 × rent_score)
```

Priority classification using `pd.cut`:

| Score Range | Priority Tier |
|---|---|
| 0.67 – 1.00 | High Priority |
| 0.34 – 0.66 | Medium Priority |
| 0.00 – 0.33 | Low Priority |

A secondary revenue-versus-customer-reach scatter chart identifies four strategic quadrants:

| Quadrant | Interpretation |
|---|---|
| High revenue, high reach | Core performers — protect and expand stock |
| High revenue, low reach | Niche premium — upsell opportunity |
| Low revenue, high reach | High traffic, low yield — pricing review needed |
| Low revenue, low reach | Candidates for stock reduction |

### Why It Is Novel

A standard analysis would sort categories by total revenue and report the top five. This engine goes further by combining two signals into a single normalised score that avoids overweighting either dimension independently. Without normalisation, the revenue signal (measured in dollars) would dominate the rental volume signal (measured in counts) entirely.

The 60/40 weight split reflects a deliberate analytical choice: revenue is the primary business objective, but volume matters because it indicates breadth of customer appeal. A category generating high revenue from a small customer base is more fragile than one generating similar revenue from a larger, more diverse group. The 60/40 split balances these two considerations explicitly.

The quadrant analysis surfaces a dimension the bar chart cannot provide: categories that are popular but under-monetised (high reach, low revenue per rental) — signalling that a modest pricing increase could significantly improve contribution without reducing demand.

### Results

From the analysis run on the DVD Rental dataset:

**High Priority categories:** Sports, Animation, Sci-Fi

These three categories combine strong total revenue with high rental volume and should be prioritised in stock purchasing, store display, and promotional communications.

**Recommendation Priority Score** computed for all 16 categories and exported to `tables/recommendation_candidates.csv`.

### Business Value

The priority score can be recalculated at any time using fresh transaction data with a single script execution, making it a living operational tool rather than a one-time report. Management can review category priorities monthly and adjust stock and promotional spend accordingly.

The quadrant analysis has direct pricing implications. Categories identified as high-reach but low-revenue per rental indicate an opportunity to test a modest rental rate increase — for example, raising the rate by $0.25 per rental — to capture more revenue from existing demand without needing to attract new customers.

### Limitations

The engine operates at category level and does not personalise to individual customers. Two customers who both favour Drama may have very different title preferences within that category. The 60/40 weight split was set analytically rather than optimised against a measurable outcome.

### Next Step

The natural extension is a customer-level collaborative filtering model: customers who rented the same films as you also rented these. This requires building a sparse customer-film rental matrix and computing cosine similarity between customer rental vectors using `scipy.sparse`. This would transform the current category-level engine into a genuine personalised recommendation system.

---

## Summary

| Innovation | Method | Key Output | Business Value |
|---|---|---|---|
| Churn Scoring Model | RFM composite score, min-max normalisation, weighted features | Ranked list of at-risk customers with churn scores | Enables targeted re-engagement before customers disengage permanently |
| Recommendation Engine | Dual-signal normalised priority score, quadrant analysis | Category priority tiers + upsell quadrant chart | Directs stock and promotional investment toward highest-value categories |

Both innovations are fully interpretable, require no external infrastructure, produce immediately actionable outputs, and have a clear and specific path toward more sophisticated future implementations using standard Python data science tools.