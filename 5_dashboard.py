import streamlit as st
import pandas as pd
import os

# Page config matching a minimalist, contemporary aesthetic
st.set_page_config(page_title="BDM DVD Rental Analytics", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for crisp shadows and subtle financial highlights
st.markdown("""
    <style>
    .kpi-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #2ea44f;
        text-align: center;
    }
    .kpi-title { font-size: 14px; color: #666666; text-transform: uppercase; font-weight: bold; }
    .kpi-value { font-size: 28px; color: #111111; font-weight: bold; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# Data verification check
results_dir = "./exports/results"
matrix_path = "./exports/merges/master_analytical_matrix.csv"

@st.cache_data
def load_data():
    master = pd.read_csv(matrix_path) if os.path.exists(matrix_path) else None
    segments = pd.read_csv(f"{results_dir}/customer_segments.csv") if os.path.exists(f"{results_dir}/customer_segments.csv") else None
    ratings = pd.read_csv(f"{results_dir}/revenue_by_rating.csv") if os.path.exists(f"{results_dir}/revenue_by_rating.csv") else None
    store = pd.read_csv(f"{results_dir}/store_operational_performance.csv") if os.path.exists(f"{results_dir}/store_operational_performance.csv") else None
    return master, segments, ratings, store

master_df, segments_df, ratings_df, store_df = load_data()

# Navigation Sidebar
st.sidebar.title("Navigation Matrix")
page = st.sidebar.radio("Go to:", ["Executive Overview", "Customer Intelligence", "Revenue & Inventory Optimization"])

if page == "Executive Overview":
    st.title("📊 Executive Performance Dashboard")
    st.subheader("DSA5102 Big Data Management Capstone - Infrastructure & Data Overview")
    
    # 3 Distinct Top-Level KPI Cards
    if master_df is not None:
        total_rev = master_df['amount'].sum()
        total_tx = len(master_df)
        avg_tx = master_df['amount'].mean()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="kpi-box"><div class="kpi-title">Gross Revenue Pipeline</div><div class="kpi-value">${total_rev:,.2f}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="kpi-box"><div class="kpi-title">Total Processed Rentals</div><div class="kpi-value">{total_tx:,}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="kpi-box"><div class="kpi-title">Average Transaction Velocity</div><div class="kpi-value">${avg_tx:.2f}</div></div>', unsafe_allow_html=True)
            
    st.write("### Data Warehouse Integrity Log")
    if store_df is not None:
        st.dataframe(store_df, use_container_width=True)

elif page == "Customer Intelligence":
    st.title("👥 Customer Cohorts & Lifetime Value (LTV)")
    
    if segments_df is not None:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.write("#### Value Segmentation Distribution")
            seg_counts = segments_df['segment'].value_counts()
            st.bar_chart(seg_counts)
        with col2:
            st.write("#### High-Value VIP Roster (Sample)")
            st.dataframe(segments_df[segments_df['segment'] == 'High-Value VIP'].head(10), use_container_width=True)

elif page == "Revenue & Inventory Optimization":
    st.title("💰 Revenue Drivers & Operational Velocity")
    
    if ratings_df is not None:
        st.write("#### Metric Chart 1: Revenue Volume by MPAA Rating")
        st.bar_chart(ratings_df.set_index('rating')['total_revenue'])
        
        st.write("#### Metric Chart 2: Rental Volume Density")
        st.line_chart(ratings_df.set_index('rating')['rental_count'])