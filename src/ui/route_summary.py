import streamlit as st

from src.ui.chart_card import chart_card


def _tile(icon, label, value):
    return (
        '<div class="summary-item">'
        f'<span class="summary-icon">{icon}</span>'
        f'<span class="summary-label">{label}</span>'
        f'<span class="summary-value" title="{value}">{value}</span>'
        '</div>'
    )


def route_summary(df):
    
    total_factory = 5
    total_region = df["Region"].nunique()
    total_state = df["State/Province"].nunique()
    total_city = df["City"].nunique()
    total_orders = df["Order ID"].nunique()
    avg_shipping = df["Shipping Days"].mean()
    best_city = (
        df.groupby("City")["Shipping Days"]
        .mean()
        .idxmin()
    )
    slowest_city = (
        df.groupby("City")["Shipping Days"]
        .mean()
        .idxmax()
    )

    tiles = "".join([
        _tile("🏭", "Factories", total_factory),
        _tile("🌎", "Regions", total_region),
        _tile("🗺️", "States", total_state),
        _tile("🏙️", "Cities", total_city),
        _tile("📦", "Orders", f"{total_orders:,}"),
        _tile("🚚", "Avg Shipping", f"{avg_shipping:.0f} Days"),
        _tile("⚡", "Best City", best_city),
        _tile("🐢", "Slowest City", slowest_city),
    ])

    st.markdown(
        f"""
        <div class="route-summary">
            <div class="route-summary-title">📊 Route Summary</div>
            <div class="summary-grid">{tiles}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    route_performance = (
        df.groupby("City", as_index=False)
        .agg(
            Orders=("Order ID", "nunique"),
            Sales=("Sales", "sum"),
            Profit=("Gross Profit", "sum"),
            Avg_Shipping_Days=("Shipping Days", "mean")
        )
        .sort_values(
            "Avg_Shipping_Days",
            ascending=False
        )
    )

    route_performance["Profit Margin"] = (
        route_performance["Profit"]
        .div(route_performance["Sales"])
        .mul(100)
        .fillna(0)
    )

    route_performance["Sales"] = (
    route_performance["Sales"].round(0)
    )

    route_performance["Profit"] = (
        route_performance["Profit"].round(0)
    )

    route_performance["Avg_Shipping_Days"] = (
        route_performance["Avg_Shipping_Days"].round(1)
    )

    route_performance["Profit Margin"] = (
        route_performance["Profit Margin"].round(1)
    )

    with chart_card(
        "📋 Route Performance",
        "Orders, sales, profit and shipping time by destination city"
    ):
        st.dataframe(
            route_performance,
            width="stretch",
            hide_index=True,
            height=420,
            column_config={
                "Sales": st.column_config.NumberColumn(format="$%d"),
                "Profit": st.column_config.NumberColumn(format="$%d"),
                "Avg_Shipping_Days": st.column_config.NumberColumn(
                    "Avg Shipping Days", format="%.1f"
                ),
                "Profit Margin": st.column_config.NumberColumn(
                    "Profit Margin (%)", format="%.1f%%"
                ),
            }
        )
