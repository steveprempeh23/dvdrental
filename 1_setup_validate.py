import os
import pandas as pd
from sqlalchemy import create_engine, inspect

def main():
    print("=" * 60)
    # 1. Establish connection using SQLAlchemy
    # Format: postgresql://username:password@host:port/database
    DATABASE_URL = "postgresql://postgres:your_secure_password@localhost:5432/dvd_rental"
    
    try:
        engine = create_engine(DATABASE_URL)
        # Test connection
        with engine.connect() as connection:
            print("Successfully connected to the PostgreSQL database via SQLAlchemy!")
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    print("=" * 60)
    
    # 2. Inspect database and list all available tables
    inspector = inspect(engine)
    all_tables = inspector.get_table_names()
    print(f"Total tables discovered in 'public' schema: {len(all_tables)}")
    print("Tables list:", all_tables)
    print("=" * 60)

    # 3. Critical tables to validate for the DVD Rental system
    critical_tables = ['customer', 'rental', 'payment', 'film', 'inventory', 'store', 'staff']
    
    print("RUNNING CRITICAL TABLE VALIDATION & METRICS:")
    validation_records = []

    for table in critical_tables:
        if table in all_tables:
            # 4. Report row counts using Pandas
            df = pd.read_sql_query(f"SELECT * FROM {table};", engine)
            row_count = len(df)
            
            # 5. Simple data quality check: count rows that have missing/null values in any column
            null_rows = df.isnull().any(axis=1).sum()
            
            status = "PASS"
            notes = f"Row count verified. Found {null_rows} rows with null fields."
            
            validation_records.append({
                "Table Name": table,
                "Status": status,
                "Row Count": row_count,
                "Rows with Nulls": null_rows,
                "Notes": notes
            })
            print(f" ✔ Table '{table}': Found {row_count} rows. (Null rows: {null_rows})")
        else:
            validation_records.append({
                "Table Name": table,
                "Status": "FAIL",
                "Row Count": 0,
                "Rows with Nulls": 0,
                "Notes": "CRITICAL TABLE MISSING FROM DATABASE SCHEMA!"
            })
            print(f" ✘ Table '{table}': NOT FOUND!")

    print("=" * 60)

    # 6. Produce a structured validation report dataframe
    report_df = pd.DataFrame(validation_records)
    
    # Ensure export directory exists
    os.makedirs("./exports/tables", exist_ok=True)
    
    # Export report to CSV for transparency/reproducibility
    report_path = "./exports/tables/database_validation_report.csv"
    report_df.to_csv(report_path, index=False)
    
    print("STRUCTURED VALIDATION REPORT:")
    print(report_df.to_string(index=False))
    print(f"\nReport successfully saved to: {report_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()