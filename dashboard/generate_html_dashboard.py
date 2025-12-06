import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from pathlib import Path

# ---------------------------------------------------------------------
# Paths & data loading
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]  # project root
DATA_DIR = BASE_DIR / "meltano_kaggle_csv" / "data"

@st.cache_data(show_spinner=True)
def load_data():
    # Load only the columns we need to keep it faster
    orders = pd.read_csv(
        DATA_DIR / "olist_orders_dataset.csv",
        usecols=["order_id", "customer_id", "order_purchase_timestamp"],
        parse_dates=["order_purchase_timestamp"],
    )

    customers = pd.read_csv(
        DATA_DIR / "olist_customers_dataset.csv",
        usecols=["customer_id", "customer_state", "customer_city"],
    )

    sellers = pd.read_csv(
        DATA_DIR / "olist_sellers_dataset.csv",
        usecols=["seller_id", "seller_state", "seller_city"],
    )

    items = pd.read_csv(
        DATA_DIR / "olist_order_items_dataset.csv",
        usecols=["order_id", "order_item_id", "product_id", "seller_id", "price", "freight_value"],
    )

    payments = pd.read_csv(
        DATA_DIR / "olist_order_payments_dataset.csv",
        usecols=["order_id", "payment_value"],
    )

    products = pd.read_csv(
        DATA_DIR / "olist_products_dataset.csv",
        usecols=["product_id", "product_category_name"],
    )

    reviews = pd.read_csv(
        DATA_DIR / "olist_order_reviews_dataset.csv",
        usecols=["order_id", "review_score"],
    )

    trans = pd.read_csv(
        DATA_DIR / "product_category_name_translation.csv",
        usecols=["product_category_name", "product_category_name_english"],
    )

    # Aggregate payments & reviews to 1 row per order
    pay_sum = payments.groupby("order_id", as_index=False)["payment_value"].sum()
    rev_mean = reviews.groupby("order_id", as_index=False)["review_score"].mean()

    # Build a main fact table (one row per order-item)
    df = (
        orders
        .merge(customers, on="customer_id", how="left")
        .merge(items, on="order_id", how="left")
        .merge(products, on="product_id", how="left")
        .merge(trans, on="product_category_name", how="left")
        .merge(sellers, on="seller_id", how="left")
        .merge(pay_sum, on="order_id", how="left")
        .merge(rev_mean, on="order_id", how="left")
    )

    # Extra time columns
    df["order_year"] = df["order_purchase_timestamp"].dt.year
    df["order_month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)

    # Clean category name
    df["product_category_name_english"] = df[
        "product_category_name_english"
    ].fillna("Unknown")

    return df


df = load_data()

# ---------------------------------------------------------------------
# Sidebar filters (like Tableau filter panel)
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Brazilian E-Commerce – Interactive Dashboard",
    layout="wide",
)

st.sidebar.title("Filters")

years = sorted(df["order_year"].dropna().unique().tolist())
year_min, year_max = int(min(years)), int(max(years))
year_range = st.sidebar.slider(
    "Order Year range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
)

state_options = sorted(df["customer_state"].dropna().unique().tolist())
selected_states = st.sidebar.multiselect(
    "Customer State",
    options=state_options,
    default=state_options,  # all selected by default
)

category_options = (
    df["product_category_name_english"]
    .value_counts()
    .head(50)
    .index.tolist()
)
selected_categories = st.sidebar.multiselect(
    "Top Product Categories (English)",
    options=category_options,
    default=category_options,
)

min_payment = float(df["payment_value"].min())
max_payment = float(df["payment_value"].max())
payment_range = st.sidebar.slider(
    "Order payment value (BRL)",
    min_value=round(min_payment, 1),
    max_value=round(max_payment, 1),
    value=(round(min_payment, 1), round(min_payment + (max_payment - min_payment) * 0.7, 1)),
)

# Apply filters
filtered = df.copy()
filtered = filtered[
    (filtered["order_year"].between(year_range[0], year_range[1]))
    & (filtered["customer_state"].isin(selected_states))
    & (filtered["product_category_name_english"].isin(selected_categories))
    & (filtered["payment_value"].between(payment_range[0], payment_range[1]))
]

# Guard if no data
if filtered.empty:
    st.warning("No data for the current filter selection. Please adjust filters.")
    st.stop()

# ---------------------------------------------------------------------
# KPI section
# ---------------------------------------------------------------------
st.title("Brazilian E-Commerce – Interactive Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_orders = filtered["order_id"].nunique()
    st.metric("Total Orders", f"{total_orders:,}")

with col2:
    total_revenue = filtered["payment_value"].sum()
    st.metric("Total Revenue (BRL)", f"{total_revenue:,.0f}")

with col3:
    avg_ticket = filtered.groupby("order_id")["payment_value"].sum().mean()
    st.metric("Average Order Value", f"{avg_ticket:,.2f}")

with col4:
    avg_review = filtered["review_score"].mean()
    st.metric("Avg Review Score", f"{avg_review:.2f} / 5")

st.markdown("---")

# ---------------------------------------------------------------------
# First row: Customer & Seller distribution (treemaps)
# ---------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    cust_state = (
        filtered.groupby("customer_state")["customer_id"]
        .nunique()
        .reset_index(name="unique_customers")
    )
    fig_cust = px.treemap(
        cust_state,
        path=["customer_state"],
        values="unique_customers",
        title="Customer Distribution per State",
        color="unique_customers",
        color_continuous_scale="Blues",
    )
    st.plotly_chart(fig_cust, use_container_width=True)

with c2:
    seller_state = (
        filtered.groupby("seller_state")["seller_id"]
        .nunique()
        .reset_index(name="unique_sellers")
    )
    fig_seller = px.treemap(
        seller_state,
        path=["seller_state"],
        values="unique_sellers",
        title="Seller Distribution per State",
        color="unique_sellers",
        color_continuous_scale="Purples",
    )
    st.plotly_chart(fig_seller, use_container_width=True)

# ---------------------------------------------------------------------
# Second row: Top categories + Monthly sales
# ---------------------------------------------------------------------
c3, c4 = st.columns(2)

with c3:
    top_cat = (
        filtered.groupby("product_category_name_english")["order_id"]
        .nunique()
        .reset_index(name="order_count")
        .sort_values("order_count", ascending=False)
        .head(50)
    )

    fig_cat = px.bar(
        top_cat,
        x="order_count",
        y="product_category_name_english",
        orientation="h",
        title="Top 50 Product Categories Sold",
        labels={"order_count": "Order Count", "product_category_name_english": ""},
    )
    fig_cat.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_cat, use_container_width=True)

with c4:
    monthly = (
        filtered.groupby("order_month")["order_id"]
        .nunique()
        .reset_index(name="order_count")
        .sort_values("order_month")
    )

    fig_month = px.line(
        monthly,
        x="order_month",
        y="order_count",
        title="Orders per Month",
        markers=True,
        labels={"order_month": "Month", "order_count": "Order Count"},
    )
    st.plotly_chart(fig_month, use_container_width=True)

# ---------------------------------------------------------------------
# Third row: Top sellers table (like right panel in Tableau)
# ---------------------------------------------------------------------
st.markdown("### Top Sellers (by number of orders)")

top_sellers = (
    filtered.groupby(["seller_id", "seller_state", "seller_city"])["order_id"]
    .nunique()
    .reset_index(name="orders")
    .sort_values("orders", ascending=False)
    .head(100)
)

st.dataframe(
    top_sellers,
    use_container_width=True,
    height=350,
)
