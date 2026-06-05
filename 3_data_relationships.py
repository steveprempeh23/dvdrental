import os
import pandas as pd
from sqlalchemy import create_engine

def main():
    print("=" * 60)
    print("RUNNING QUESTION 4.3.2: DATA RELATIONSHIP MAPPING")
    print("=" * 60)
    
    # 1. Database Connection
    DATABASE_URL = "postgresql://postgres:your_secure_password@localhost:5432/dvd_rental"
    engine = create_engine(DATABASE_URL)
    
    # Ensure export directories exist
    os.makedirs("./exports/merges", exist_ok=True)
    
    # Load foundational datasets
    rental_df = pd.read_sql_query("SELECT * FROM rental;", engine)
    payment_df = pd.read_sql_query("SELECT * FROM payment;", engine)
    customer_df = pd.read_sql_query("SELECT * FROM customer;", engine)
    inventory_df = pd.read_sql_query("SELECT * FROM inventory;", engine)
    film_df = pd.read_sql_query("SELECT * FROM film;", engine)
    
    print("[Processing Relationship Merges...]")

    # --- CORE MERGE 1: Core Transaction Ledger (Rental + Payment) ---
    # Justification: INNER JOIN ensures we isolate completed payment transactions 
    # matched perfectly to operational rentals for precise revenue metrics.
    tx_merge = pd.merge(
        payment_df, 
        rental_df, 
        on="rental_id", 
        suffixes=("_payment", "_rental"), 
        how="inner"
    )
    
# --- CORE MERGE 2: Master Analytical Matrix (Tx + Customer + Film Catalog) ---
    # Merge Customer info using the suffixed customer ID from the payment table
    cust_merge = pd.merge(
        tx_merge, 
        customer_df, 
        left_on="customer_id_payment", 
        right_on="customer_id", 
        how="inner"
    )
    
    # Merge Inventory and Film info to understand what asset generated the cash
    inv_film_merge = pd.merge(inventory_df, film_df, on="film_id", how="inner")
    master_analytical_df = pd.merge(cust_merge, inv_film_merge, on="inventory_id", how="inner")

    
    # 2. Validation Checks (Ensuring join structural integrity)
    print("\n[Join Structural Validation]")
    print(f"Payment Table Base Rows: {len(payment_df)}")
    print(f"Master Analytical Table Merged Rows: {len(master_analytical_df)}")
    
    if len(master_analytical_df) <= len(payment_df):
        print(" ✔ Structural Validation: Passed. No artificial row-multiplication detected.")
    else:
        print(" ⚠ Warning: Row count exceeds baseline. Verify primary-foreign key relationships.")

    # 3. Save Core Output
    master_path = "./exports/merges/master_analytical_matrix.csv"
    master_analytical_df.to_csv(master_path, index=False)
    
    # 4. Documenting Assumptions and Limitations (Required for Part C Grading)
    print("\n[Documenting Constraints & Limitations]")
    print(" 1. Assumption: All rental records require an explicit 'rental_id' link inside payment ledger.")
    print(" 2. Limitation: Drop-offs during inner joins could surface if historical database purges occurred.")
    print(" 3. Limitation: Timezone deltas between local execution and server docker images can shift date metrics.")
    print("=" * 60)
    print(f"SUCCESS: Merged master dataset exported cleanly to: {master_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()