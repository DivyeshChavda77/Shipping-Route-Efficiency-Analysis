import streamlit as st

def show_business_insights(df):

    if df.empty:
        st.warning("No data available for the selected filters.")
        return
    
    top_region = (
        df.groupby("Region")["Sales"]
        .sum()
        .idxmax()
    )

    slow_region = (
        df.groupby("Region")["Shipping Days"]
        .mean()
        .idxmax()
    )

    best_ship_mode = (
        df.groupby("Ship Mode")["Sales"]
        .mean()
        .idxmax()
    )

    top_product = (
        df.groupby("Product Name")["Gross Profit"]
        .sum()
        .idxmax()
    )

    avg_shipping = df["Shipping Days"].mean()

    total_sales = df["Sales"].sum()
    total_profit = df["Gross Profit"].sum()

    profit_margin = (
        (total_profit / total_sales) * 100
        if total_sales != 0
        else 0
    )

    insights = [
        ("success", "🏆", f"{top_region} region generated the highest Sales."),
        ("warning", "⚠️", f"{slow_region} region has the highest average Shipping Days."),
        ("info", "📦", f"{best_ship_mode} has the highest average Sales per record among Ship Modes."),
        ("success", "💰", f"{top_product} generated the highest Gross Profit."),
        ("info", "🚚", f"Average Shipping Days: {avg_shipping:.0f}"),
        ("success", "📈", f"Overall Profit Margin: {profit_margin:.2f}%"),
    ]

    render_insight_cards(
        insights,
        "💡 Executive Business Insights",
        "Auto-generated from the current filter selection"
    )


def render_insight_cards(insights, title, subtitle=""):
    """Insight panel. insights: (tone, icon, text) with tone success/warning/info."""
    if not insights:
        return

    cards = "".join(
        f'<div class="insight-card insight-{tone}">'
        f'<span class="insight-icon">{icon}</span>'
        f'<span>{text}</span>'
        f'</div>'
        for tone, icon, text in insights
    )

    st.markdown(
        f"""
        <div class="insight-panel">
            <div class="chart-title">{title}</div>
            <div class="chart-subtitle">{subtitle}</div>
            <div class="insight-grid">{cards}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
