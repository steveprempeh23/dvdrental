import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

def main():
    print("=" * 60)
    print("RUNNING QUESTION 4.3.1: EXPLORATORY DATA ANALYSIS")
    print("=" * 60)
    
    # 1. Database Connection
    DATABASE_URL = "postgresql://postgres:your_secure_password@localhost:5432/dvd_rental"
    engine = create_engine(DATABASE_URL)
    
    # Ensure export directories exist
    os.makedirs("./exports/results", exist_ok=True)
    sns.set_theme(style="whitegrid") # Clean minimalist theme for academic grading
    
    # 2. Extract key datasets for exploration
    film_df = pd.read_sql_query("SELECT * FROM film;", engine)
    customer_df = pd.read_sql_query("SELECT * FROM customer;", engine)
    payment_df = pd.read_sql_query("SELECT * FROM payment;", engine)
    rental_df = pd.read_sql_query("SELECT * FROM rental;", engine)
    
    # --- TASK A: INSPECT SCHEMA, DATA TYPES, AND MISSING VALUES ---
    for name, df in [("Film", film_df), ("Customer", customer_df), ("Payment", payment_df)]:
        print(f"\n[Schema Inspection for {name} Table]")
        print(df.dtypes)
        null_counts = df.isnull().sum()
        print(f"Missing Values:\n{null_counts[null_counts > 0] if null_counts.sum() > 0 else 'None discovered.'}")
        print("-" * 40)
        
    # --- TASK B: DESCRIPTIVE STATISTICS & OUTLIERS ---
    print("\n[Descriptive Statistics for Payment Amounts & Film Features]")
    print(payment_df['amount'].describe())
    print(film_df[['rental_rate', 'length', 'replacement_cost']].describe())
    
    # Identify outliers using IQR for payment amounts
    Q1 = payment_df['amount'].quantile(0.25)
    Q3 = payment_df['amount'].quantile(0.75)
    IQR = Q3 - Q1
    outliers = payment_df[payment_df['amount'] > (Q3 + 1.5 * IQR)]
    print(f"\nIdentified {len(outliers)} statistical outlier payments above threshold ${Q3 + 1.5 * IQR:.2f}")

    # --- TASK C: VISUALIZATIONS (Exporting 4 required figures) ---
    print("\nGenerating and exporting 4 required visualizations...")

    # Visualization 1: Distribution of Film Lengths (Histogram)
    plt.figure(figsize=(8, 4))
    sns.histplot(film_df['length'], bins=20, kde=True, color='#2ca02c') # Green tint
    plt.title('Distribution of Film Lengths (Catalog Profile)')
    plt.xlabel('Duration (Minutes)')
    plt.ylabel('Film Count')
    plt.tight_layout()
    plt.savefig('./exports/results/v1_film_length_distribution.png')
    plt.close()

    # Visualization 2: Rental Rate vs Replacement Cost (Scatter plot for asset profiling)
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=film_df, x='replacement_cost', y='rental_rate', alpha=0.4, color='#1f77b4')
    plt.title('Rental Rate vs. Asset Replacement Cost')
    plt.xlabel('Replacement Cost ($)')
    plt.ylabel('Rental Rate ($)')
    plt.tight_layout()
    plt.savefig('./exports/results/v2_rental_rate_vs_replacement.png')
    plt.close()

    # Visualization 3: Payment Amount Outlier & Density Profile (Boxplot)
    plt.figure(figsize=(6, 4))
    sns.boxplot(x=payment_df['amount'], color='#d62728')
    plt.title('Detection Matrix: Payment Amount Outliers')
    plt.xlabel('Transaction Amount ($)')
    plt.tight_layout()
    plt.savefig('./exports/results/v3_payment_amount_boxplot.png')
    plt.close()

    # Visualization 4: Global Distribution of Rental Durations (Calculated Field)
    rental_df['rental_duration_days'] = (pd.to_datetime(rental_df['return_date']) - pd.to_datetime(rental_df['rental_date'])).dt.days
    plt.figure(figsize=(8, 4))
    sns.countplot(x=rental_df['rental_duration_days'].dropna().astype(int), color='#7f7f7f')
    plt.title('Operational Profile: Actual Customer Rental Durations')
    plt.xlabel('Days Kept Before Return')
    plt.ylabel('Transaction Count')
    plt.tight_layout()
    plt.savefig('./exports/results/v4_actual_rental_days.png')
    plt.close()

    print("=" * 60)
    print("SUCCESS: 4 visualizations saved cleanly to ./exports/results/")
    print("Exploratory processing complete. Ready for Data Integration.")
    print("=" * 60)

if __name__ == "__main__":
    main()