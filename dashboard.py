# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1wqNM_IhyE5iFN0A5tbtGzKVKRwHiJsCk
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Set page config for wide layout
st.set_page_config(page_title="SuperStore KPI Dashboard", layout="wide")

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

if selected_region != "All":
    df_filtered = df_original[df_original["Region"] == selected_region]
else:
    df_filtered = df_original

all_states = sorted(df_filtered["State"].dropna().unique())
selected_state = st.sidebar.selectbox("Select State", options=["All"] + all_states)

if selected_state != "All":
    df_filtered = df_filtered[df_filtered["State"] == selected_state]

all_categories = sorted(df_filtered["Category"].dropna().unique())
selected_category = st.sidebar.selectbox("Select Category", options=["All"] + all_categories)

if selected_category != "All":
    df_filtered = df_filtered[df_filtered["Category"] == selected_category]

all_products = sorted(df_filtered["Product Name"].dropna().unique())
selected_product = st.sidebar.selectbox("Select Product", options=["All"] + all_products)

if selected_product != "All":
    df_filtered = df_filtered[df_filtered["Product Name"] == selected_product]

min_date = df_filtered["Order Date"].min()
max_date = df_filtered["Order Date"].max()

from_date = st.sidebar.date_input("From Date", value=min_date, min_value=min_date, max_value=max_date)
to_date = st.sidebar.date_input("To Date", value=max_date, min_value=min_date, max_value=max_date)

if from_date > to_date:
    st.sidebar.error("From Date must be earlier than To Date.")

df_filtered = df_filtered[(df_filtered["Order Date"] >= pd.to_datetime(from_date)) & (df_filtered["Order Date"] <= pd.to_datetime(to_date))]

# ---- KPI Calculation ----
if df_filtered.empty:
    total_sales = 0
    total_quantity = 0
    total_profit = 0
    margin_rate = 0
else:
    total_sales = df_filtered["Sales"].sum()
    total_quantity = df_filtered["Quantity"].sum()
    total_profit = df_filtered["Profit"].sum()
    margin_rate = (total_profit / total_sales) if total_sales != 0 else 0

st.title("Enhanced SuperStore KPI Dashboard")

# ---- KPI Display ----
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
with kpi_col1:
    st.metric(label="Total Sales", value=f"${total_sales:,.2f}")
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

    kpi_options = ["Sales", "Quantity", "Profit", "Margin Rate"]
    selected_kpi = st.radio("Select KPI to visualize:", options=kpi_options, horizontal=True)

    col1, col2 = st.columns(2)
    with col1:
        fig_line = px.line(df_grouped, x="Order Date", y=selected_kpi, title=f"{selected_kpi} Over Time")
        st.plotly_chart(fig_line, use_container_width=True)

    top_products = df_filtered.groupby("Product Name").agg({"Sales": "sum", "Quantity": "sum", "Profit": "sum"}).reset_index()
    top_products["Margin Rate"] = top_products["Profit"] / top_products["Sales"].replace(0, 1)
    top_products = top_products.sort_values(by=selected_kpi, ascending=False).head(10)

    with col2:
        fig_bar = px.bar(top_products, x=selected_kpi, y="Product Name", orientation="h", title=f"Top 10 Products by {selected_kpi}", color=selected_kpi)
        st.plotly_chart(fig_bar, use_container_width=True)

st.success("Dashboard updated with best practices! 🚀")