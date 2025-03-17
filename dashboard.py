import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Set page config for wide layout
st.set_page_config(page_title="SuperStore KPI Dashboard", layout="wide")

st.markdown("""
    <style>
        body { font-family: Arial, sans-serif; }
        h1, h2, h3, h4, h5, h6 { font-family: 'Roboto', sans-serif; color: #333; }
        .stRadio > label { font-size: 16px; font-weight: bold; }
        .stMetric > div { font-size: 18px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ---- Load Data ----
@st.cache_data
def load_data():
    df = pd.read_excel("Sample - Superstore.xlsx", engine="openpyxl")
    if not pd.api.types.is_datetime64_any_dtype(df["Order Date"]):
        df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df

df_original = load_data()

# ---- Sidebar Filters ----
st.sidebar.title("Filters")

all_regions = sorted(df_original["Region"].dropna().unique())
selected_region = st.sidebar.selectbox("Select Region", options=["All"] + all_regions)

df_filtered = df_original if selected_region == "All" else df_original[df_original["Region"] == selected_region]

all_states = sorted(df_filtered["State"].dropna().unique())
selected_state = st.sidebar.selectbox("Select State", options=["All"] + all_states)

df_filtered = df_filtered if selected_state == "All" else df_filtered[df_filtered["State"] == selected_state]

all_categories = sorted(df_filtered["Category"].dropna().unique())
selected_category = st.sidebar.selectbox("Select Category", options=["All"] + all_categories)

df_filtered = df_filtered if selected_category == "All" else df_filtered[df_filtered["Category"] == selected_category]

all_products = sorted(df_filtered["Product Name"].dropna().unique())
selected_product = st.sidebar.selectbox("Select Product", options=["All"] + all_products)

df_filtered = df_filtered if selected_product == "All" else df_filtered[df_filtered["Product Name"] == selected_product]

min_date, max_date = df_filtered["Order Date"].min(), df_filtered["Order Date"].max()
from_date = st.sidebar.date_input("From Date", value=min_date, min_value=min_date, max_value=max_date)
to_date = st.sidebar.date_input("To Date", value=max_date, min_value=min_date, max_value=max_date)

if from_date > to_date:
    st.sidebar.error("From Date must be earlier than To Date.")

df_filtered = df_filtered[(df_filtered["Order Date"] >= pd.to_datetime(from_date)) & (df_filtered["Order Date"] <= pd.to_datetime(to_date))]

# ---- KPI Calculation ----
previous_sales = df_original["Sales"].sum() - total_sales if not df_original.empty else 0
total_sales = df_filtered["Sales"].sum() if not df_filtered.empty else 0
total_quantity = df_filtered["Quantity"].sum() if not df_filtered.empty else 0
total_profit = df_filtered["Profit"].sum() if not df_filtered.empty else 0
margin_rate = (total_profit / total_sales) if total_sales != 0 else 0

st.title("Enhanced SuperStore KPI Dashboard")

# ---- KPI Display with Percentage Change ----
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
with kpi_col1:
    st.metric(label="Total Sales", value=f"${total_sales:,.2f}", delta=f"${total_sales - previous_sales:,.2f}")
with kpi_col2:
    st.metric(label="Total Quantity Sold", value=f"{total_quantity:,.0f}")
with kpi_col3:
    st.metric(label="Total Profit", value=f"${total_profit:,.2f}")
with kpi_col4:
    st.metric(label="Margin Rate", value=f"{(margin_rate * 100):,.2f}%")

# ---- KPI Trend Over Time ----
if not df_filtered.empty:
    df_grouped = df_filtered.groupby("Order Date").agg({"Sales": "sum", "Quantity": "sum", "Profit": "sum"}).reset_index()
    df_grouped["Margin Rate"] = df_grouped["Profit"] / df_grouped["Sales"].replace(0, 1)
    
    top_product = df_filtered.groupby("Product Name")["Quantity"].sum().idxmax()
    st.subheader(f"Best Selling Product: {top_product}")
    
    kpi_options = ["Sales", "Quantity", "Profit", "Margin Rate"]
    selected_kpi = st.radio("Select KPI to visualize:", options=kpi_options, horizontal=True)
    
    col1, empty_col, col2 = st.columns([0.8, 0.2, 1])  # Adds space between charts
    with col1:
        fig_line = px.line(df_grouped, x="Order Date", y=selected_kpi, title=f"{selected_kpi} Over Time",
                           labels={"Order Date": "Date", selected_kpi: selected_kpi}, template="plotly_white",
                           hover_data={"Order Date": "|%B %d, %Y", selected_kpi: ":.2f"})
        fig_line.update_layout(height=300)
        st.plotly_chart(fig_line, use_container_width=True)
    
    top_products = df_filtered.groupby("Product Name").agg({"Sales": "sum", "Quantity": "sum", "Profit": "sum"}).reset_index()
    top_products["Margin Rate"] = top_products["Profit"] / top_products["Sales"].replace(0, 1)
    top_products = top_products.sort_values(by=selected_kpi, ascending=False).head(10)
    
    with col2:
        fig_bar = px.bar(top_products, x=selected_kpi, y=top_products.index, orientation="h", 
                         title=f"Top 10 Products by {selected_kpi}", color=selected_kpi,
                         color_continuous_scale="Blues", template="plotly_white",
                         hover_name="Product Name")
        fig_bar.update_layout(height=300, yaxis={"categoryorder": "total ascending", "showticklabels": False})
        st.plotly_chart(fig_bar, use_container_width=True)

st.success("Dashboard updated with best practices! 🚀")
