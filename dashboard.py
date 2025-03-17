import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from sklearn.linear_model import LinearRegression
import numpy as np

# Set page config for wide layout and multi-page navigation
st.set_page_config(page_title="SuperStore KPI Dashboard", layout="wide")

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

if page == "📊 Business Overview":
    # ---- Sidebar Filters ----
    st.sidebar.title("Filters")
    selected_regions = st.sidebar.multiselect("Select Region(s)", sorted(df_original["Region"].unique()), default=df_original["Region"].unique())
    df_filtered = df_original[df_original["Region"].isin(selected_regions)]
    
    selected_states = st.sidebar.multiselect("Select State(s)", sorted(df_filtered["State"].unique()), default=df_filtered["State"].unique())
    df_filtered = df_filtered[df_filtered["State"].isin(selected_states)]
    
    selected_categories = st.sidebar.multiselect("Select Category(s)", sorted(df_filtered["Category"].unique()), default=df_filtered["Category"].unique())
    df_filtered = df_filtered[df_filtered["Category"].isin(selected_categories)]
    
    top_n = st.sidebar.radio("Show Top:", [5, 10], index=0)
    
    # ---- KPI Calculation ----
    total_sales = df_filtered["Sales"].sum() if not df_filtered.empty else 0
    total_profit = df_filtered["Profit"].sum() if not df_filtered.empty else 0
    margin_rate = (total_profit / total_sales) if total_sales != 0 else 0
    
    st.title("📊 Business Overview")
    
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
    top_products = top_products.sort_values(by="Sales", ascending=False).head(top_n)
    top_products["Short Name"] = top_products["Product Name"].str[:15] + "..."
    
    st.subheader(f"Top {top_n} Products by Sales")
    fig_bar = px.bar(top_products, x="Sales", y="Short Name", orientation="h", color="Sales", title="Top Products", color_continuous_scale="Blues")
    fig_bar.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Sales: $%{x:,.2f}")
    fig_bar.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_bar, use_container_width=True)
    
elif page == "📈 Advanced Analytics":
    st.title("📈 Advanced Analytics")
    
    # ---- Profitability vs Sales Scatter Plot ----
    st.subheader("Profit vs. Sales")
    fig_scatter = px.scatter(df_original, x="Sales", y="Profit", color="Category", size="Quantity", title="Profitability vs Sales")
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # ---- Sales Forecasting ----
    st.subheader("Future Sales Forecast")
    df_time = df_original.groupby("Order Date").agg({"Sales": "sum"}).reset_index()
    df_time["Days"] = (df_time["Order Date"] - df_time["Order Date"].min()).dt.days
    
    X = df_time["Days"].values.reshape(-1, 1)
    y = df_time["Sales"].values
    model = LinearRegression()
    model.fit(X, y)
    future_days = np.array(range(X.max() + 1, X.max() + 31)).reshape(-1, 1)
    future_sales = model.predict(future_days)
    
    future_df = pd.DataFrame({"Order Date": pd.date_range(df_time["Order Date"].max() + pd.Timedelta(days=1), periods=30), "Sales": future_sales})
    
    fig_forecast = px.line(df_time, x="Order Date", y="Sales", title="Sales Forecast")
    fig_forecast.add_scatter(x=future_df["Order Date"], y=future_df["Sales"], mode='lines', name="Predicted Sales")
    st.plotly_chart(fig_forecast, use_container_width=True)
    
    st.caption("Forecasted sales are based on a simple linear regression model.")
    
st.success("Dashboard updated with advanced analytics and multi-page support! 🚀")
