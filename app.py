import streamlit as st
from pathlib import Path

import pandas as pd

from src.components.route_analysis import RouteAnalysis

from src.ui import theme
from src.ui.cards import hero_banner, kpi_grid, section_title
from src.ui.filters import sidebar_filters
from src.ui.navigation import (
    create_tabs, sidebar_brand, theme_toggle, sidebar_summary
)
from src.ui.charts import (
    sales_by_region, profit_by_region, sales_vs_profit, shipping_by_shipmode,
    fastest_cities, slowest_cities, shipping_by_state, shipping_by_region,
    monthly_sales, sales_by_ship_mode,  sales_by_division, sales_distribution,
    profit_by_product, top_products, bubble_sales_profit
    )
from src.ui.chart_card import chart_grid
from src.ui.route_summary import route_summary
from src.ui.analytics_tabs import delivery_tab, customer_tab
from src.ui.insights import show_business_insights
from src.ui.data_explorer import data_explorer

BASE_DIR = Path(__file__).resolve().parent


def load_css():
    """Inject Inter font + active theme tokens + assets/style.css."""
    css_path = BASE_DIR / "assets" / "style.css"

    with open(css_path, encoding="utf-8") as f:
        stylesheet = f.read()

    st.markdown(
        f"<style>{theme.build_css(stylesheet)}</style>",
        unsafe_allow_html=True
    )

# =========== Page Configuration ===========
st.set_page_config(
    page_title="Factory-to-Customer Shipping Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="auto"
)

load_css()

# =========== Load Data Set =============
DATA_PATH = BASE_DIR / "artifacts" / "processed_data.csv"

REQUIRED_COLUMNS = [
    "Order ID", "Order Date", "Ship Mode", "Customer ID", "Country/Region",
    "City", "State/Province", "Division", "Region", "Product Name",
    "Sales", "Units", "Gross Profit", "Shipping Days"
]


def load_dataset():
    """Load the processed dataset, or show a clear message and stop."""
    try:
        data = RouteAnalysis(str(DATA_PATH)).df
    except FileNotFoundError:
        st.error(
            f"Dataset not found: `{DATA_PATH}`. Run `python test.py` from the "
            "project folder to generate it from `data/Nassau-Candy-Distributor.csv`."
        )
        st.stop()
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        st.error(
            f"`{DATA_PATH.name}` is empty or not a valid CSV. "
            "Run `python test.py` to regenerate it."
        )
        st.stop()

    missing = [c for c in REQUIRED_COLUMNS if c not in data.columns]

    if missing:
        st.error(
            "The dataset is missing required columns: "
            + ", ".join(f"`{c}`" for c in missing)
            + ". Run `python test.py` to regenerate it."
        )
        st.stop()

    if data.empty:
        st.error("The dataset contains no records.")
        st.stop()

    return data


df = load_dataset()

# =========== Sidebar ===========
sidebar_brand()

theme_toggle()

filtered_df = sidebar_filters(df)

if filtered_df.empty:
    st.sidebar.warning(
        "No records match the selected filters. "
        "Please adjust the filters and try again."
    )
    st.stop()

sidebar_summary(len(filtered_df), len(df))

# =========== Hero Banner ===========
hero_pills = [f"📋 {len(filtered_df):,} records"]

if filtered_df["Order Date"].notna().any():
    hero_pills.append(
        "📅 "
        f"{filtered_df['Order Date'].min():%b %Y} – "
        f"{filtered_df['Order Date'].max():%b %Y}"
    )

hero_banner(
    "📦 Factory-to-Customer Shipping Route Efficiency Dashboard",
    "Analyze shipping performance, route efficiency, sales, "
    "and profitability using interactive business analytics.",
    pills=hero_pills,
    eyebrow="Logistics &amp; Supply Chain Analytics"
)

# =========== Calculate KPIs ===========
total_sales = filtered_df["Sales"].sum()

total_profit = filtered_df["Gross Profit"].sum()

total_orders = filtered_df["Order ID"].nunique()

total_units = filtered_df["Units"].sum()

avg_shipping = filtered_df["Shipping Days"].mean()

profit_margin = (
    total_profit / total_sales
) * 100

# Display Cards
section_title("🎯", "Executive KPIs", "Headline metrics for the current selection")

kpi_grid([
    ("💰", "Sales", f"${total_sales:,.0f}", "indigo", "Total revenue"),
    ("📈", "Profit", f"${total_profit:,.0f}", "emerald", "Gross profit"),
    ("📋", "Orders", f"{total_orders:,}", "sky", "Unique order IDs"),
    ("📦", "Units", f"{total_units:,}", "violet", "Units sold"),
    ("🚚", "Shipping", f"{avg_shipping:.0f} Days", "amber", "Avg. order-to-ship time"),
    ("📊", "Margin", f"{profit_margin:.1f}%", "teal", "Profit ÷ Sales"),
])

st.markdown(
    '<div class="section-space"></div>',
    unsafe_allow_html=True
)
# =========== Create tabs ===========
(overview_tab, route_tab, sales_tab, product_tab,
 delivery_tab_ui, customer_tab_ui, data_tab) = create_tabs()

# ------------- Overview Tab -------------
with overview_tab:
    section_title(
        "📊", "Executive Overview",
        "Sales, profit and shipping performance at a glance"
    )

    chart_grid(filtered_df, [
        ("📊 Sales by Region",
         "Total Sales generated across regions",
         sales_by_region),
        ("📈 Gross Profit",
         "Regional profit comparison",
         profit_by_region),
        ("📉 Sales vs Profit",
         "Relationship between Sales and Gross Profit",
         sales_vs_profit),
        ("🚚 Shipping Days",
         "Average shipping time by ship mode",
         shipping_by_shipmode),
    ])

# ------------- Route Tab -------------
with route_tab:
    section_title(
        "🚚", "Route Analysis",
        "Destination cities, states and regions ranked by shipping time"
    )

    route_summary(filtered_df)

    chart_grid(filtered_df, [
        ("🏆 Fastest Shipping Cities",
         "Cities with the lowest average shipping time",
         fastest_cities),
        ("⚠ Slowest Shipping Cities",
         "Cities with the highest average shipping time",
         slowest_cities),
        ("🌎 Shipping Performance by State",
         "Top 10 states with highest average shipping days",
         shipping_by_state),
        ("🚚 Shipping Performance by Region",
         "Average shipping days across regions",
         shipping_by_region),
    ])

# ------------- Sales Tab -------------
with sales_tab:
    section_title(
        "💰", "Sales Analysis",
        "Revenue trends and distribution"
    )

    chart_grid(filtered_df, [
        ("📈 Monthly Sales Trend",
         "Sales trend over time",
         monthly_sales),
        ("🚚 Sales by Ship Mode",
         "Sales distribution by shipping method",
         sales_by_ship_mode),
        ("📦 Sales by Division",
         "Contribution of each product division",
         sales_by_division),
        ("💵 Sales Distribution",
         "Distribution of sales values",
         sales_distribution),
    ])

# ------------- Product Tab -------------
with product_tab:
    section_title(
        "📦", "Product Analysis",
        "Top products by profit and sales"
    )

    chart_grid(filtered_df, [
        ("💰 Profit by Product",
         "Top profit generating products",
         profit_by_product),
        ("🏆 Top Products",
         "Products generating the highest sales",
         top_products),
    ])

    chart_grid(filtered_df, [
        ("💵 Sales vs Profit",
         "Relationship between sales, profit and units sold",
         bubble_sales_profit),
    ], cols=1)

# ------------- Delivery Analytics Tab -------------
with delivery_tab_ui:
    delivery_tab(filtered_df)

# ------------- Customers & Destinations Tab -------------
with customer_tab_ui:
    customer_tab(filtered_df)

# ------------- Data Tab -------------
with data_tab:
    data_explorer(filtered_df)

# =========== Business Insights ===========
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

show_business_insights(filtered_df)

# =========== Footer ===========
st.markdown(
    """
<div class="app-footer">
📦 <b>Factory-to-Customer Shipping Route Efficiency Analysis</b>
<br>
Developed by <b>Divyesh Chavda</b> · Artificial Intelligence &amp; Data Science
<br>
© 2026 All Rights Reserved
</div>
""",
    unsafe_allow_html=True
)
