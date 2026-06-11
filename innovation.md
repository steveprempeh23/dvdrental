# Part F: Innovation and Excellence

## DSA5102 Big Data Management — Capstone Project
**Student:** Steve Prempeh

---

## Overview

This section documents two novel analytical contributions delivered in this project that go beyond the standard descriptive analysis of the DVD rental dataset. Both contributions demonstrate practical business value, methodological rigour, and a clear path toward more sophisticated future implementations.

---

## Innovation 1: RFM-Based Customer Churn Scoring Model

### What Was Built

A fully interpretable, feature-engineered churn prediction model was built from scratch using only the existing payment and rental transaction history. The model computes a composite churn risk score for every customer without requiring any external machine learning libraries, training datasets, or labelled churn outcomes.

The model engineers three behavioural features per customer:

**Recency** — days elapsed since the customer's last payment, normalised over a 180-day window:
```
recency_norm = days_since_last_payment / 180   (clipped at 180)
```

**Frequency** — inverse of rental count, normalised over a 50-rental ceiling:
```
freq_norm = 1 - (total_rentals / 50)   (clipped at 50)
```

**Monetary** — inverse of total spend, normalised over a $200 ceiling:
```
spend_norm = 1 - (total_spent / 200)   (clipped at 200)
```

These are combined into a weighted composite churn score:
```
churn_score = (0.50 × recency_norm) + (0.30 × freq_norm) + (0.20 × spend_norm)
```

Customers are then classified into three risk tiers using `pd.cut` with `include_lowest=True`:
- **Low Risk:** score 0.00–0.33
- **Medium Risk:** score 0.34–0.60
- **High Risk:** score 0.61–1.00

### Why This Is Novel

Standard descriptive analysis of this dataset stops at counting rentals per customer or summing revenue. This model goes further by combining three independent signals into a single actionable score that ranks every customer on a continuous risk scale.

The weight assignments (50% recency, 30% frequency, 20% monetary) are grounded in the established RFM (Recency, Frequency, Monetary) framework from customer analytics literature, which consistently identifies recency as the strongest predictor of future engagement. The weights were adapted to reflect the DVD rental context, where inactivity is a stronger signal than spend level given the low price-per-transaction nature of the business.

### Business Value

The model produces a ranked intervention list that a marketing team can act on the same day it is run. High Risk customers can be targeted with a personalised re-engagement offer before they disengage permanently. The cost of implementing and running this model is effectively zero — it requires no infrastructure beyond the existing database connection and the standard Python libraries already used throughout this project.

Unlike a black-box machine learning classifier, this model is fully transparent. Every score can be explained to a non-technical manager in terms of three simple questions: when did this customer last rent, how often do they rent, and how much have they spent? This interpretability is essential for a business that needs to justify campaign targeting decisions to stakeholders.

### Limitations

The model relies on payment recency as a proxy for churn intent. It cannot distinguish between a genuinely churned customer and a seasonal renter who is simply in a quiet period. Direct cancellation data or a customer survey would improve accuracy. The feature weights were set using domain knowledge rather than empirical optimisation; with a labelled historical churn dataset, the weights could be tuned using logistic regression or gradient boosting to improve predictive accuracy.

### Next Step

The natural extension of this model is a supervised machine learning classifier trained on historical examples of customers who churned versus those who did not. A logistic regression baseline using scikit-learn would be the recommended starting point, using the same three features plus customer tenure and store ID as inputs. With even 12 months of labelled churn history, this would meaningfully outperform the rule-based scoring approach.

---

## Innovation 2: Normalised Category Recommendation Priority Engine

### What Was Built

A category-level recommendation priority engine was built to rank all 16 film categories on a continuous priority score, enabling data-driven decisions about which categories to promote, stock, and feature in customer communications.

The engine computes a composite priority score for each category using two signals:

**Revenue score** — normalised total revenue for the category:
```
rev_score = (category_revenue - min_revenue) / (max_revenue - min_revenue)
```

**Rental score** — normalised total rental volume for the category:
```
rent_score = (category_rentals - min_rentals) / (max_rentals - min_rentals)
```

These are combined into a weighted priority score:
```
priority_score = (0.60 × rev_score) + (0.40 × rent_score)
```

Categories are then classified into three tiers:
- **High Priority** (score 0.67–1.00): Promote aggressively; increase stock
- **Medium Priority** (score 0.34–0.66): Maintain current investment
- **Low Priority** (score 0.00–0.33): Review stock levels; consider targeted promotions

A secondary analysis plots each category on a revenue-versus-customer-reach scatter chart, with bubble size proportional to rental volume. This two-dimensional view identifies four strategic quadrants:
- **High revenue, high reach:** Core performers — protect and expand
- **High revenue, low reach:** Niche premium — upsell opportunity
- **Low revenue, high reach:** High traffic, low yield — pricing review needed
- **Low revenue, low reach:** Candidates for stock reduction

### Why This Is Novel

A standard analysis of this dataset would simply sort categories by total revenue and report the top five. This engine goes further by combining two signals — revenue and volume — into a single normalised score that avoids overweighting either dimension independently.

The min-max normalisation ensures that the score is robust to the scale difference between revenue (in dollars) and rental count (in units). Without normalisation, revenue would dominate the composite score entirely and the rental volume signal would be lost.

The weight assignment (60% revenue, 40% volume) reflects a deliberate analytical choice: revenue is the primary business objective, but volume matters because it indicates breadth of customer appeal. A category that generates high revenue from a small number of customers is more fragile than one that generates similar revenue from a larger, more diverse customer base. The 60/40 split balances these two considerations.

The scatter chart quadrant analysis adds a dimension that the bar chart alone cannot provide. It surfaces categories that are popular but under-monetised (high reach, low revenue per rental) — a signal that a modest pricing increase could significantly improve contribution without reducing demand.

### Business Value

The priority score can be recalculated at any point in time using fresh transaction data with a single script execution. This makes it a living operational tool rather than a one-time report. Management can review category priorities monthly and adjust stock purchasing and promotional spend accordingly.

The quadrant analysis has direct implications for pricing strategy. Categories identified as high-reach but low-revenue indicate an opportunity to test a modest rental rate increase — for example, raising the rate by $0.25 per rental — to capture more revenue from existing demand without needing to attract new customers.

The model is also extensible. The same normalisation and weighting approach can be applied at the film level rather than the category level to produce a film-level priority score, enabling individual title stocking decisions rather than just category-level ones.

### Limitations

The recommendation engine operates at the category level and does not account for individual customer preferences. Two customers who have both rented primarily from the Drama category may have very different film preferences within it. A full content-based or collaborative filtering recommendation system would personalise recommendations at the customer level rather than the business level.

The 60/40 weight split was set analytically rather than tested against a measurable outcome. In a production environment, the weights could be optimised by measuring the click-through or conversion rate of promotions built on different weight configurations, using an A/B testing framework.

### Next Step

The natural extension is a customer-level collaborative filtering model: "customers who rented the same films as you also rented these." This requires building a customer-film rental matrix and computing cosine similarity between customer rental vectors. A sparse matrix implementation using `scipy.sparse` would handle the scale of this dataset efficiently. This approach would transform the current category-level engine into a genuine personalised recommendation system.

---

## Summary of Novel Contributions

| Innovation | Method | Business Output | Marks Rationale |
|---|---|---|---|
| Churn Scoring Model | RFM-weighted composite score with min-max normalisation | Ranked intervention list of at-risk customers | Novel methodology, interpretable, directly actionable |
| Recommendation Engine | Dual-signal normalised priority score with quadrant analysis | Category priority tiers + pricing insight quadrant | Combines two signals, extensible, grounded in business strategy |

Both innovations were built entirely from the existing transaction data, require no external APIs or machine learning infrastructure, produce outputs that a non-technical manager can understand and act on immediately, and have a clearly articulated path toward more sophisticated future implementations.