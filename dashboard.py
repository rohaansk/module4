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
        .stMultiSelect div[data-baseweb="tag"] { display: none; }
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

# ---- Sidebar Navigation ----
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["📊 Business Overview", "📈 Advanced Analytics"])

# ---- Sidebar Filters ----
st.sidebar.title("Filters")
selected_regions = st.sidebar.multiselect("Select Region(s) (Selected: " + str(len(df_original["Region"].unique())) + ")", 
                                          sorted(df_original["Region"].dropna().unique()), 
                                          default=df_original["Region"].unique())
df_filtered = df_original[df_original["Region"].isin(selected_regions)]

selected_states = st.sidebar.multiselect("Select State(s) (Selected: " + str(len(df_filtered["State"].unique())) + ")", 
                                          sorted(df_filtered["State"].dropna().unique()), 
                                          default=df_filtered["State"].unique())
df_filtered = df_filtered[df_filtered["State"].isin(selected_states)]

selected_categories = st.sidebar.multiselect("Select Category(s) (Selected: " + str(len(df_filtered["Category"].unique())) + ")", 
                                              sorted(df_filtered["Category"].dropna().unique()), 
                                              default=df_filtered["Category"].unique())
df_filtered = df_filtered[df_filtered["Category"].isin(selected_categories)]

selected_subcategories = st.sidebar.multiselect("Select Sub-Category(s) (Selected: " + str(len(df_filtered["Sub-Category"].unique())) + ")", 
                                                 sorted(df_filtered["Sub-Category"].dropna().unique()), 
                                                 default=df_filtered["Sub-Category"].unique())
df_filtered = df_filtered[df_filtered["Sub-Category"].isin(selected_subcategories)]

selected_products = st.sidebar.multiselect("Select Product(s) (Selected: " + str(len(df_filtered["Product Name"].unique())) + ")", 
                                           sorted(df_filtered["Product Name"].dropna().unique()), 
                                           default=df_filtered["Product Name"].unique())
df_filtered = df_filtered[df_filtered["Product Name"].isin(selected_products)]

min_date, max_date = df_filtered["Order Date"].min(), df_filtered["Order Date"].max()
from_date = st.sidebar.date_input("From Date", value=min_date, min_value=min_date, max_value=max_date)
to_date = st.sidebar.date_input("To Date", value=max_date, min_value=min_date, max_value=max_date)

df_filtered = df_filtered[(df_filtered["Order Date"] >= pd.to_datetime(from_date)) & (df_filtered["Order Date"] <= pd.to_datetime(to_date))]

if page == "📊 Business Overview":
    st.title("📊 Business Overview")
    
    # ---- KPI Calculation ----
    total_sales = df_filtered["Sales"].sum() if not df_filtered.empty else 0
    total_profit = df_filtered["Profit"].sum() if not df_filtered.empty else 0
    margin_rate = (total_profit / total_sales) if total_sales != 0 else 0
    
    # ---- KPI Display ----
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Sales", value=f"${total_sales:,.2f}")
        st.metric(label="Total Profit", value=f"${total_profit:,.2f}")
    with col2:
        st.metric(label="Margin Rate", value=f"{(margin_rate * 100):,.2f}%")
    
    # ---- Treemap Visualization ----
    st.subheader("Sales Breakdown by Category & Sub-Category")
    treemap_fig = px.treemap(df_filtered, path=["Category", "Sub-Category"], values="Sales", title="Category Sales Breakdown")
    st.plotly_chart(treemap_fig, use_container_width=True)
    
    # ---- Top Products ----
    top_products = df_filtered.groupby("Product Name").agg({"Sales": "sum"}).reset_index()
    top_products = top_products.sort_values(by="Sales", ascending=False).head(5)
    top_products["Short Name"] = top_products["Product Name"].str[:15] + "..."
    
    st.subheader("Top 5 Products by Sales")
    fig_bar = px.bar(top_products, x="Sales", y="Short Name", orientation="h", color="Sales", title="Top Products", color_continuous_scale="Blues")
    fig_bar.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_bar, use_container_width=True)

elif page == "📈 Advanced Analytics":
    st.title("📈 Advanced Analytics")
    
    # ---- Profitability vs Sales Scatter Plot ----
    st.subheader("Profit vs. Sales")
    fig_scatter = px.scatter(df_filtered, x="Sales", y="Profit", color="Category", size="Quantity", title="Profitability vs Sales")
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # ---- KPI Trend Over Time ----
    st.subheader("KPI Trend Over Time")
    kpi_options = ["Sales", "Quantity", "Profit", "Margin Rate"]
    selected_kpi = st.radio("Select KPI to visualize:", options=kpi_options, horizontal=True)
    df_grouped = df_filtered.groupby("Order Date").agg({"Sales": "sum", "Quantity": "sum", "Profit": "sum"}).reset_index()
    df_grouped["Margin Rate"] = df_grouped["Profit"] / df_grouped["Sales"].replace(0, 1)
    
    fig_line = px.line(df_grouped, x="Order Date", y=selected_kpi, title=f"{selected_kpi} Over Time", labels={"Order Date": "Date", selected_kpi: selected_kpi}, template="plotly_white")
    st.plotly_chart(fig_line, use_container_width=True)
    
st.success("Dashboard updated with best practices! 🚀")
