"""Advanced logistics analytics tabs (Delivery Analytics, Customers & Destinations)."""

from functools import partial

import streamlit as st

from src.components import delivery_analytics as da
from src.ui import charts as ch
from src.ui.cards import callout, kpi_grid, section_title
from src.ui.chart_card import chart_card, chart_grid, display_chart
from src.ui.insights import render_insight_cards

_DAYS = '<span class="kpi-unit">days</span>'

RISK_DIMENSIONS = [
    "State/Province", "Region", "Ship Mode", "Division", "Country/Region", "City"
]

RISK_COLUMNS = [
    "Orders", "Avg Days", "Median Days", "Slow Orders",
    "Slow Rate (%)", "Risk Index", "Risk Level", "Sales"
]

RISK_COLUMN_CONFIG = {
    "Avg Days": st.column_config.NumberColumn(format="%.0f"),
    "Median Days": st.column_config.NumberColumn(format="%.0f"),
    "Slow Rate (%)": st.column_config.NumberColumn(format="%.1f%%"),
    "Risk Index": st.column_config.NumberColumn(format="%.2fx"),
    "Sales": st.column_config.NumberColumn(format="$%d"),
}


def _risk_dataframe(table, by):
    st.dataframe(
        table[[by] + RISK_COLUMNS],
        width="stretch",
        hide_index=True,
        height=min(420, 38 * len(table) + 40),
        column_config=RISK_COLUMN_CONFIG
    )


# ======================================================================
# DELIVERY ANALYTICS
# ======================================================================
def delivery_tab(df):
    orders = da.to_orders(df)
    stats = da.lead_time_stats(orders)

    section_title(
        "⏱️", "Delivery Performance & Delay Risk",
        "Order-level lead-time analysis (one record per Order ID)"
    )

    callout(
        "<b>How to read this tab.</b> Lead time is Ship Date − Order Date. "
        "The dataset has no promised delivery date, so an order counts as "
        "<b>slow</b> when it is slower than the chosen percentile of the "
        f"current selection. Lead times here are very long (median "
        f"{stats['median']:,.0f} days), so use these views to compare "
        "destinations, modes and periods against each other rather than "
        "against a service-level target."
    )

    # ---- interactive controls (shared with the Customers tab) ----
    with st.container(key="card-delivery-controls"):
        left, right = st.columns(2, gap="large")

        pct = left.slider(
            "Slow-shipment threshold (percentile of lead time)",
            50, 95, da.DEFAULT_SLOW_PCT, 5, key="slow_pct",
            help="Orders slower than this percentile are flagged as slow."
        )
        min_orders = right.slider(
            "Minimum orders per group",
            5, 100, da.DEFAULT_MIN_ORDERS, 5, key="min_orders",
            help="Hides small groups so a few orders cannot distort risk rates."
        )

    threshold, overall = da.slow_baseline(orders, pct)
    states = da.risk_table(orders, "State/Province", pct, min_orders)
    high_risk = int((states["Risk Level"] == "High").sum()) if len(states) else 0

    # ---- advanced KPIs ----
    kpi_grid([
        ("📦", "Orders Analyzed", f"{stats['orders']:,}", "indigo",
         "Unique Order IDs"),
        ("⏱️", "Median Lead Time", f"{stats['median']:,.0f}{_DAYS}", "sky",
         "Typical order"),
        ("🐢", "P90 Lead Time", f"{stats['p90']:,.0f}{_DAYS}", "rose",
         "Slowest 10% start here"),
        ("📉", "Variability", f"{stats['cv']:.0f}%", "violet",
         "Std. deviation ÷ mean"),
        ("🚩", "Slow Threshold", f"&gt; {threshold:,.0f}{_DAYS}", "amber",
         f"Above P{pct} of selection"),
        ("⚠️", "High-Risk States",
         f"{high_risk} / {len(states)}" if len(states) else "–", "teal",
         f"Risk index ≥ {da.HIGH_RISK_INDEX}x · min {min_orders} orders"),
    ])

    st.markdown('<div class="section-space"></div>', unsafe_allow_html=True)

    # ---- distribution & performance ----
    chart_grid(orders, [
        ("📊 Lead Time Distribution",
         "How order lead times are spread, with the median and slow threshold",
         partial(ch.lead_time_distribution, pct=pct)),
        ("📦 Lead Time by Ship Mode",
         "Spread of lead times for each shipping method",
         ch.lead_time_by_ship_mode),
        ("📈 Lead Time Trend",
         "Average and median lead time by order month",
         ch.lead_time_trend),
        ("🔥 Slow-Shipment Heatmap",
         "Share of slow orders by region and ship mode (cells under 10 orders hidden)",
         partial(ch.slow_rate_heatmap, pct=pct)),
    ])

    # ---- delay risk explorer ----
    with chart_card(
        "🎯 Delay Risk Explorer",
        "Where slow shipments concentrate — choose how to break the data down"
    ):
        by = st.selectbox("Break down by", RISK_DIMENSIONS, key="risk_dimension")
        table = da.risk_table(orders, by, pct, min_orders)

        display_chart(ch.delay_risk_chart(table, by, overall), key="risk-explorer-chart")

        if not table.empty:
            st.caption(
                f"Risk level compares each group's slow-order rate with the "
                f"overall rate ({overall:.0f}%): High ≥ {da.HIGH_RISK_INDEX}x, "
                f"Moderate ≥ {da.MODERATE_RISK_INDEX:.1f}x, otherwise Low. "
                f"Groups with fewer than {min_orders} orders are excluded."
            )
            _risk_dataframe(table, by)

    # ---- product line efficiency (factory-wise proxy) ----
    with chart_card(
        "🏭 Product Line Efficiency",
        "Shipping reliability by product — the closest available view to factory performance"
    ):
        callout(
            "Factory-wise efficiency cannot be calculated: no column links an "
            "order or product to a factory (<code>factory_coordinates.csv</code> "
            "only lists the 5 factory locations). Product lines are shown "
            "instead; add a product-to-factory mapping to enable it.",
            tone="warning", icon="🏭"
        )
        products = da.risk_table(orders, "Product Name", pct, min_orders)

        display_chart(
            ch.delay_risk_chart(products, "Product Name", overall),
            key="product-risk-chart"
        )

        if not products.empty:
            _risk_dataframe(products, "Product Name")

    # ---- scope note ----
    callout(
        "<b>Not analysed (no supporting data).</b> <b>Shipping cost:</b> the "
        "<code>Cost</code> column is product cost (Sales − Gross Profit), not "
        "freight. <b>Route efficiency:</b> only destinations are recorded, "
        "with no shipping origin, so route-level efficiency cannot be "
        "measured; destination-level views are shown instead.",
        tone="info", icon="🔎"
    )

    render_insight_cards(
        da.delivery_insights(orders, pct, min_orders),
        "💡 Actionable Delivery Insights",
        "Generated from the current selection and thresholds"
    )


# ======================================================================
# CUSTOMERS & DESTINATIONS
# ======================================================================
def customer_tab(df):
    orders = da.to_orders(df)

    # thresholds are set on the Delivery Analytics tab
    pct = st.session_state.get("slow_pct", da.DEFAULT_SLOW_PCT)
    min_orders = st.session_state.get("min_orders", da.DEFAULT_MIN_ORDERS)

    threshold, _ = da.slow_baseline(orders, pct)
    customers = da.customer_stats(orders)
    total_sales = orders["Sales"].sum()
    slow_sales = orders.loc[orders["Shipping Days"] > threshold, "Sales"].sum()

    section_title(
        "👥", "Customers & Destinations",
        "Who orders, where orders go and how concentrated the business is"
    )

    kpi_grid([
        ("👥", "Customers", f"{customers['customers']:,}", "indigo",
         "Unique customer IDs"),
        ("🔁", "Repeat Customers", f"{customers['repeat_rate']:.0f}%", "emerald",
         "Ordered more than once"),
        ("🧾", "Orders / Customer", f"{customers['orders_per_customer']:.1f}",
         "sky", "Average"),
        ("💵", "Avg Order Value", f"${customers['avg_order_value']:,.2f}",
         "violet", "Sales ÷ orders"),
        ("🧭", "Top-5 State Share",
         f"{da.sales_concentration(orders, 'State/Province', 5):.0f}%", "amber",
         "Of total sales"),
        ("💸", "Sales in Slow Orders",
         f"{slow_sales / total_sales * 100 if total_sales else 0:.0f}%", "rose",
         f"Orders above {threshold:,.0f} days"),
    ])

    st.markdown('<div class="section-space"></div>', unsafe_allow_html=True)

    chart_grid(orders, [
        ("🔁 Customer Order Frequency",
         "How many customers placed 1, 2, 3 or more orders",
         ch.order_frequency_chart),
        ("🌍 Sales by Country",
         "Share of sales by destination country",
         ch.sales_by_country),
        ("🧭 Destination Concentration",
         "Top 15 states/provinces by sales, with cumulative share of total sales",
         ch.destination_pareto),
        ("🎯 Lead Time vs Sales by Destination",
         "Large bubbles on the right: high-volume destinations with slow delivery",
         partial(ch.destination_quadrant, min_orders=min_orders)),
    ])

    with chart_card(
        "🏆 Top Destinations",
        "Rank states/provinces or cities by the metric of your choice"
    ):
        left, right = st.columns(2, gap="large")
        level = left.selectbox(
            "Destination level", ["State/Province", "City"],
            key="destination_level"
        )
        metric = right.selectbox(
            "Rank by",
            ["Sales", "Gross Profit", "Orders", "Avg Shipping Days"],
            key="destination_metric"
        )
        display_chart(
            ch.top_destinations_chart(orders, level, metric, min_orders),
            key="top-destinations-chart"
        )

        if metric == "Avg Shipping Days":
            st.caption(
                f"Slowest destinations with at least {min_orders} orders "
                "(set on the Delivery Analytics tab)."
            )

    with chart_card(
        "🥇 Top Customers",
        "Largest accounts by sales, with their delivery experience"
    ):
        top = da.top_customers(orders, pct)

        st.dataframe(
            top,
            width="stretch",
            hide_index=True,
            height=min(420, 38 * len(top) + 40),
            column_config={
                "Customer ID": st.column_config.NumberColumn(format="%d"),
                "Sales": st.column_config.NumberColumn(format="$%.0f"),
                "Gross Profit": st.column_config.NumberColumn(format="$%.0f"),
                "Avg Days": st.column_config.NumberColumn(format="%.0f"),
            }
        )

    render_insight_cards(
        da.customer_insights(orders, pct),
        "💡 Customer & Destination Insights",
        "Generated from the current selection"
    )
