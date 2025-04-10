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
        .stMultiSelect div[data-baseweb="select"] > div { height: auto !important; }
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
def multiselect_with_all(label, options, default_options):
    selected_options = st.sidebar.multiselect(label, ["All"] + options, default=["All"] if set(default_options) == set(options) else default_options)
    if "All" in selected_options and len(selected_options) > 1:
        selected_options.remove("All")
    elif len(selected_options) == 0:
        st.sidebar.warning(f"At least one {label.lower()} must be selected.")
        selected_options = ["All"]
    return options if "All" in selected_options else selected_options

st.sidebar.title("Filters")
selected_regions = multiselect_with_all("Select Region(s)", sorted(df_original["Region"].dropna().unique()), df_original["Region"].unique())
df_filtered = df_original[df_original["Region"].isin(selected_regions)]

selected_states = multiselect_with_all("Select State(s)", sorted(df_filtered["State"].dropna().unique()), df_filtered["State"].unique())
df_filtered = df_filtered[df_filtered["State"].isin(selected_states)]

selected_categories = multiselect_with_all("Select Category(s)", sorted(df_filtered["Category"].dropna().unique()), df_filtered["Category"].unique())
df_filtered = df_filtered[df_filtered["Category"].isin(selected_categories)]

selected_subcategories = multiselect_with_all("Select Sub-Category(s)", sorted(df_filtered["Sub-Category"].dropna().unique()), df_filtered["Sub-Category"].unique())
df_filtered = df_filtered[df_filtered["Sub-Category"].isin(selected_subcategories)]

selected_products = multiselect_with_all("Select Product(s)", sorted(df_filtered["Product Name"].dropna().unique()), df_filtered["Product Name"].unique())
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
    total_quantity = df_filtered["Quantity"].sum() if not df_filtered.empty else 0

    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Sales", value=f"${total_sales:,.2f}")
        st.metric(label="Total Profit", value=f"${total_profit:,.2f}")
    with col2:
        st.metric(label="Margin Rate", value=f"{(margin_rate * 100):,.2f}%")
        st.metric(label="Total Quantity Sold", value=f"{total_quantity:,}")


    
    # ---- Treemap Visualization ----
    # ---- Treemap Tooltip Update ----
    st.subheader("Sales Breakdown by Category & Sub-Category")
    treemap_fig = px.treemap(df_filtered, path=["Category", "Sub-Category"], values="Sales", title="Category Sales Breakdown",
                         custom_data=["Category", "Sub-Category", "Sales"])
    treemap_fig.update_traces(hovertemplate="<b>Category:</b> %{customdata[0]}<br>"
                                        "<b>Sub-Category:</b> %{customdata[1]}<br>"
                                        "<b>Sales:</b> $%{customdata[2]:,.2f}")
    st.plotly_chart(treemap_fig, use_container_width=True)

    
    # ---- Top Products ----
    top_products = df_filtered.groupby("Product Name").agg({"Sales": "sum"}).reset_index()
    top_products = top_products.sort_values(by="Sales", ascending=False).head(5)
    top_products["Short Name"] = top_products["Product Name"].str[:15] + "..."
    
    # ---- Bar Chart Tooltip Update ----
    st.subheader("Top 5 Products by Sales")
    top_products = df_filtered.groupby("Product Name").agg({"Sales": "sum", "Quantity": "sum", "Profit": "sum"}).reset_index()
    top_products = top_products.sort_values(by="Sales", ascending=False).head(5)
    top_products["Short Name"] = top_products["Product Name"].str[:15] + "..."

    fig_bar = px.bar(top_products, x="Sales", y="Short Name", orientation="h", color="Sales", title="Top Products",
                 color_continuous_scale="Blues", custom_data=["Product Name", "Sales", "Quantity", "Profit"])
    fig_bar.update_traces(hovertemplate="<b>Product:</b> %{customdata[0]}<br>"
                                    "<b>Sales:</b> $%{customdata[1]:,.2f}<br>"
                                    "<b>Quantity Sold:</b> %{customdata[2]}<br>"
                                    "<b>Profit:</b> $%{customdata[3]:,.2f}")
    st.plotly_chart(fig_bar, use_container_width=True)

    
    # ---- Sales Performance by Location ----
    # ---- Sales Performance by Location ----
    st.subheader("Sales Performance by Location")
    location_sales = df_filtered.groupby("State").agg({"Sales": "sum", "Profit": "sum"}).reset_index()

    location_fig = px.bar(location_sales, x="Sales", y="State", orientation="h", title="Sales by State",
                      color="Sales", color_continuous_scale="Blues", custom_data=["State", "Sales", "Profit"])
    location_fig.update_traces(hovertemplate="<b>State:</b> %{customdata[0]}<br>"
                                         "<b>Sales:</b> $%{customdata[1]:,.2f}<br>"
                                         "<b>Profit:</b> $%{customdata[2]:,.2f}")
    location_fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(location_fig, use_container_width=True)


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
    df_grouped["Order Date"] = pd.to_datetime(df_grouped["Order Date"])  # Ensure datetime format
    df_grouped["Formatted Date"] = df_grouped["Order Date"].dt.strftime("%B %d, %Y")  # Format for hover tooltip

    fig_line = px.line(df_grouped, x="Order Date", y=selected_kpi, title=f"{selected_kpi} Over Time",
                   labels={"Order Date": "Date", selected_kpi: selected_kpi}, template="plotly_white",
                   custom_data=["Formatted Date", selected_kpi])

# Reduce number of x-axis labels by setting tick mode
    fig_line.update_layout(xaxis=dict(
        tickmode="auto",  # Automatically space ticks
        tickangle=-45,  # Rotate labels for better readability
        nticks=6  # Control number of labels shown (Adjust if needed)
    ))

    fig_line.update_traces(hovertemplate="<b>Date:</b> %{customdata[0]}<br>"
                                     f"<b>{selected_kpi}:</b> $%{{customdata[1]:,.2f}}")

    st.plotly_chart(fig_line, use_container_width=True)



