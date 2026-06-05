import os
import pandas as pd
import numpy as np

def main():
    print("=" * 60)
    print("RUNNING QUESTION 4.4: ADVANCED ANALYSIS & INSIGHTS")
    print("=" * 60)
    
    # 1. Load the unified data matrix we generated in Part C
    matrix_path = "./exports/merges/master_analytical_matrix.csv"
    if not os.path.exists(matrix_path):
        print(f"Error: Missing {matrix_path}. Please execute script 3 first.")
        return
        
    df = pd.read_csv(matrix_path)
    os.makedirs("./exports/results", exist_ok=True)
    
    # --- 1. CUSTOMER ANALYTICS (12 Marks) ---
    print("[Analyzing Customer Intelligence...]")
    # Calculate Customer Lifetime Value (LTV)
    customer_ltv = df.groupby(['customer_id_payment', 'first_name', 'last_name'])['amount'].sum().reset_index()
    customer_ltv.rename(columns={'amount': 'lifetime_value'}, inplace=True)
    
    # Segments based on LTV percentiles
    q75 = customer_ltv['lifetime_value'].quantile(0.75)
    q25 = customer_ltv['lifetime_value'].quantile(0.25)
    
    def assign_segment(ltv):
        if ltv >= q75: return 'High-Value VIP'
        elif ltv >= q25: return 'Mid-Tier Core'
        else: return 'Low-Yield Casual'
        
    customer_ltv['segment'] = customer_ltv['lifetime_value'].apply(assign_segment)
    customer_ltv.to_csv("./exports/results/customer_segments.csv", index=False)
    
    # --- 2. REVENUE OPTIMIZATION (12 Marks) ---
    print("[Analyzing Revenue Drivers...]")
    # Revenue contribution by film category (genre)
    # Note: Depending on your exact schema dump, look up category names if joined, 
    # otherwise group by available descriptors like rental_rate or rating profiles
    category_perf = df.groupby('rating')['amount'].agg(['sum', 'count', 'mean']).reset_index()
    category_perf.rename(columns={'sum': 'total_revenue', 'count': 'rental_count'}, inplace=True)
    category_perf.to_csv("./exports/results/revenue_by_rating.csv", index=False)
    
# --- 3. INVENTORY & OPERATIONS (12 Marks) ---
    print("[Analyzing Inventory Efficiency...]")
    
    # Dynamically find the correct store column name due to merge suffixes
    store_col = 'store_id'
    if 'store_id' not in df.columns:
        # Fallback to whatever suffixed store column Pandas generated (e.g., store_id_x)
        store_col = [col for col in df.columns if 'store_id' in col][0]
    
    print(f" -> Grouping operations by identified column: '{store_col}'")
    store_perf = df.groupby(store_col)['amount'].agg(['sum', 'count']).reset_index()
    store_perf.rename(columns={store_col: 'store_id', 'sum': 'gross_sales', 'count': 'total_rentals'}, inplace=True)
    store_perf.to_csv("./exports/results/store_operational_performance.csv", index=False)
    
    # --- 4. INNOVATION: RECOMMENDATION BLUEPRINT (9 Marks) ---
    print("[Generating Innovation Recommendation Matrix...]")
    # Build a cross-tabulation matrix of user rental habits for a Collaborative Recommendation engine
    recommendation_matrix = pd.crosstab(df['customer_id_payment'], df['rating'])
    recommendation_matrix.to_csv("./exports/results/innovation_recommendation_matrix.csv")

    print("=" * 60)
    print("SUCCESS: Advanced analytics data tables compiled and exported successfully!")
    print("Locations: Check inside your ./exports/results/ directory.")
    print("=" * 60)

if __name__ == "__main__":
    main()