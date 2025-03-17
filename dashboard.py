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
        .main, .block-container { background: rgba(255, 255, 255, 0.85); border-radius: 10px; padding: 20px; }
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

# ---- Mapping of State Names to Abbreviations ----
state_abbreviations = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO",
    "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
}

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
    
    # ---- KPI Display ----
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Sales", value=f"${total_sales:,.2f}")
        st.metric(label="Total Profit", value=f"${total_profit:,.2f}")
    with col2:
        st.metric(label="Margin Rate", value=f"{(margin_rate * 100):,.2f}%")
    
    # ---- Sales Performance by Location (Choropleth Map) ----
    st.subheader("Sales Performance by Location")
    location_data = df_filtered.groupby("State").agg({"Sales": "sum"}).reset_index()
    location_data["State Abbreviation"] = location_data["State"].map(state_abbreviations)
    location_data = location_data.dropna()
    
    location_fig = px.choropleth(location_data, locations="State Abbreviation", locationmode="USA-states", color="Sales",
                                 scope="usa", title="Sales by State", color_continuous_scale="Blues")
    st.plotly_chart(location_fig, use_container_width=True)

st.success("Dashboard updated with best practices! 🚀")
