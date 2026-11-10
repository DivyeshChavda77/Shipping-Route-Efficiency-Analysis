import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

from src.components import delivery_analytics as da
from src.ui.theme import (
    CATEGORICAL, FONT_STACK, SCALES, SEMANTIC, is_dark, palette
)

RISK_COLORS = {
    "High": SEMANTIC["danger"],
    "Moderate": SEMANTIC["warning"],
    "Low": SEMANTIC["success"],
}

CHART_HEIGHT = 380


def chart_layout(fig, x_title="", y_title="", legend=False):
    """Apply the shared premium chart style (theme-aware)."""
    p = palette()
    tick = dict(size=12, color=p["muted"])
    axis_title = dict(size=12, color=p["muted"])

    fig.update_layout(
        template="plotly_dark" if is_dark() else "plotly_white",

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(family=FONT_STACK, size=13, color=p["text_2"]),

        title="",
        height=CHART_HEIGHT,
        showlegend=legend,
        hovermode="closest",
        bargap=0.35,

        margin=dict(l=8, r=12, t=40 if legend else 12, b=8),

        hoverlabel=dict(
            bgcolor=p["surface"],
            bordercolor=p["border_strong"],
            font=dict(color=p["text"], size=13, family=FONT_STACK)
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="left", x=0,
            title_text="",
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12, color=p["text_2"])
        ),

        xaxis=dict(
            title=dict(text=x_title, font=axis_title),
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor=p["border_strong"],
            ticks="outside",
            tickcolor=p["border_strong"],
            tickfont=tick,
            automargin=True
        ),

        yaxis=dict(
            title=dict(text=y_title, font=axis_title),
            showgrid=True,
            gridcolor=p["grid"],
            gridwidth=1,
            zeroline=False,
            showline=False,
            tickfont=tick,
            automargin=True
        )
    )

    # Rounded bars + tidy value labels (rounded corners need Plotly >= 6)
    try:
        fig.update_layout(barcornerradius=6)
    except ValueError:
        pass

    fig.update_traces(
        selector=dict(type="bar"),
        marker_line_width=0,
        textposition="outside",
        textfont=dict(size=12, color=p["text_2"]),
        cliponaxis=False
    )

    return fig

# Sales By Region
def sales_by_region(df):
    sales = (
        df.groupby("Region",as_index=False)["Sales"]
        .sum()
        .sort_values("Sales",ascending=False)
    )
    fig = px.bar(
        sales,
        x="Region",
        y="Sales",
        color="Sales",
        text_auto=".2s",
        color_continuous_scale=SCALES["indigo"]
    )
    fig.update_layout(
        coloraxis_showscale=False
    )

    return chart_layout(
        fig,
        x_title="Region",
        y_title="Sales ($)"
        )

# Profit by Region
def profit_by_region(df):

    profit = (
        df.groupby("Region", as_index=False)["Gross Profit"]
        .sum()
        .sort_values("Gross Profit", ascending=False)
    )

    fig = px.bar(
        profit,
        x="Region",
        y="Gross Profit",
        color="Gross Profit",
        text_auto=".2s",
        color_continuous_scale=SCALES["emerald"]
    )
    fig.update_layout(
        coloraxis_showscale=False
    )

    return chart_layout(
        fig,
        x_title="Region",
        y_title="Gross Profit ($)"
    )

# Sales vs Profit
def sales_vs_profit(df):
    summary = (
        df.groupby("Region", as_index=False)
        .agg({
            "Sales": "sum",
            "Gross Profit": "sum",
            "Units": "sum"
        })
    )

    fig = px.scatter(
        summary,
        x="Sales",
        y="Gross Profit",
        color="Region",
        size="Units",
        size_max=42,
        hover_name="Region",
        color_discrete_sequence=CATEGORICAL,
        labels={
            "Sales": "Sales",
            "Gross Profit": "Gross Profit",
            "Units": "Units"
        },
        hover_data={
            "Sales": ":,.0f",
            "Gross Profit": ":,.0f",
            "Units": ":,.0f"
        }
    )
    fig.update_traces(
        marker=dict(opacity=.85, line=dict(width=1.5, color=palette()["surface"]))
    )
    fig.update_layout(
        title_text="",
        coloraxis_showscale=False
    )      

    return chart_layout(
        fig,
        x_title="Sales ($)",
        y_title="Gross Profit ($)",
        legend=True
    )

# Shiping by Shipmode
def shipping_by_shipmode(df):
    shipping = (
        df.groupby("Ship Mode", as_index=False)["Shipping Days"]
        .mean()
        .sort_values("Shipping Days")
    )

    fig = px.bar(
        shipping,
        x="Ship Mode",
        y="Shipping Days",
        color="Shipping Days",
        text_auto=".0f",
        color_continuous_scale=SCALES["amber"]
    )
    fig.update_layout(
     coloraxis_showscale=False
    )

    return chart_layout(
        fig,
        x_title="Ship Mode",
        y_title="Average Shipping Days"
    )

# -----------------Route Analysis Tab --------------
# Fastest and slowest city

def fastest_cities(df):

    fastest = (
        df.groupby("City", as_index=False)
        .agg({
            "Shipping Days": "mean"
        })
        .sort_values("Shipping Days")
        .head(10)
    )

    fig = px.bar(
        fastest,
        x="Shipping Days",
        y="City",
        orientation="h",
        text_auto=".0f",
        color="Shipping Days",
        color_continuous_scale=SCALES["teal"],
        title="Top 10 Fastest Shipping Cities"
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Value: %{x:,.2f}<extra></extra>"
    )

    fig.update_layout(
        title=None,
        coloraxis_showscale=False,
        yaxis=dict(categoryorder="total ascending")
    )

    return chart_layout(
        fig,
        x_title="Average Shipping Days",    
        y_title="City")

def slowest_cities(df):

    slowest = (
        df.groupby("City", as_index=False)
        .agg({
            "Shipping Days": "mean"
        })
        .sort_values("Shipping Days", ascending=False)
        .head(10)
    )

    fig = px.bar(
        slowest,
        x="Shipping Days",
        y="City",
        orientation="h",
        text_auto=".0f",
        color="Shipping Days",
        color_continuous_scale=SCALES["rose"],
        title="Top 10 Slowest Shipping Cities"
    )

    fig.update_layout(
        title=None,
        coloraxis_showscale=False
    )

    return chart_layout(
        fig,
        x_title="Average Shipping Days",
        y_title="City"
        )

# Shipping by State
def shipping_by_state(df):
    state = (
        df.groupby("State/Province", as_index=False)
        .agg({"Shipping Days":"mean"})
        .sort_values("Shipping Days", ascending=False)
        .head(10)
    )

    fig = px.bar(
        state,
        x="Shipping Days",
        y="State/Province",
        orientation="h",
        color="Shipping Days",
        color_continuous_scale=SCALES["amber"],
        text_auto=".0f"
    )
    fig.update_layout(
        title=None,
        coloraxis_showscale=False,
        yaxis=dict(categoryorder="total ascending")
    )

    return chart_layout(
        fig,
        x_title="Average Shipping Days",
        y_title="State/Province"
    )

# Shipping by Region
def shipping_by_region(df):
    region = (
        df.groupby("Region", as_index=False)
        .agg({"Shipping Days":"mean"})
    )

    fig = px.bar(
        region,
        x="Region",
        y="Shipping Days",
        color="Shipping Days",
        color_continuous_scale=SCALES["sky"],
        text_auto=".0f"
    )

    fig.update_layout(
        title=None,
        coloraxis_showscale=False
    )

    return chart_layout(
        fig,
        x_title="Region",
        y_title="Average Shipping Days"
    )

# --------------Salse Tab Charts----------------

# Monthly Sales Trend
def monthly_sales(df):

    data = df.copy()

    data["Order Date"] = pd.to_datetime(
        data["Order Date"],
        errors="coerce"
    )

    monthly = (
        data.dropna(subset=["Order Date"])
        .assign(
            Month=data["Order Date"].dt.to_period("M")
        )
        .groupby("Month", as_index=False)
        .agg({
            "Sales": "sum"
        })
        .sort_values("Month")
    )

    monthly["Month"] = monthly["Month"].astype(str)

    fig = px.line(
        monthly,
        x="Month",
        y="Sales",
        markers=True
    )

    primary = palette()["primary"]

    fig.update_traces(
        line=dict(width=3, color=primary),
        marker=dict(
            size=7,
            color=primary,
            line=dict(width=2, color=palette()["surface"])
        ),
        fill="tozeroy",
        fillcolor="rgba(99,102,241,0.15)"
    )

    fig.update_layout(
        title=None,
        coloraxis_showscale=False
    )

    return chart_layout(
        fig,
        x_title="Order Month",
        y_title="Sales"
    )

# Sales by shipMode
def sales_by_ship_mode(df):
    ship = (
        df.groupby("Ship Mode", as_index=False)
        .agg({"Sales": "sum"})
    )
    fig = px.bar(
        ship,
        x="Ship Mode",
        y="Sales",
        color="Sales",
        text_auto=".2s",
        color_continuous_scale=SCALES["sky"]
    )
    fig.update_layout(
        title=None,
        coloraxis_showscale=False
    )

    return chart_layout(
        fig,
        x_title="Ship Mode",
        y_title="Sales ($)"
    )

# Sales by Division
def sales_by_division(df):
    division = (
        df.groupby("Division", as_index=False)
        .agg({"Sales": "sum"})
    )
    fig = px.pie(
        division,
        names="Division",
        values="Sales",
        hole=.55,
        color_discrete_sequence=CATEGORICAL
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(size=13, color="#FFFFFF"),
        marker=dict(line=dict(color=palette()["surface"], width=3))
    )
    fig.update_layout(
        title=None,
        coloraxis_showscale=False
    )

    return chart_layout(
        fig,
        x_title="Division",
        y_title="Sales ($)",
        legend=True
    )

# Sales Distribution
def sales_distribution(df):
    fig = px.histogram(
        df,
        x="Sales",
        nbins=30,
        marginal="box",
        color_discrete_sequence=[SCALES["sky"][1]]
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(
        title=None,
        coloraxis_showscale=False
    )
    return chart_layout(
        fig,
        x_title="Sales ($)",
        y_title="Number of Orders"
    )

# -------------Product Analysis Tab Charts-------------

# Profit By Products
def profit_by_product(df):
    product = (
        df.groupby("Product Name", as_index=False)
        .agg({"Gross Profit":"sum"})
        .sort_values("Gross Profit", ascending=False)
        .head(10)
    )
    fig = px.bar(
        product,
        x="Gross Profit",
        y="Product Name",
        orientation="h",
        color="Gross Profit",
        color_continuous_scale=SCALES["emerald"],
        text_auto=".2s"
    )
    fig.update_layout(
        title=None,
        coloraxis_showscale=False,
        yaxis=dict(categoryorder="total ascending")
    )

    return chart_layout(
        fig,
        x_title="Gross Profit ($)",
        y_title="Product Name"
    )

# Top Products
def top_products(df):
    product = (
        df.groupby("Product Name", as_index=False)
        .agg({"Sales": "sum"})
        .sort_values("Sales", ascending=False)
        .head(10)
    )
    fig = px.bar(
        product,
        x="Sales",
        y="Product Name",
        orientation="h",
        text_auto=".2s",
        color="Sales",
        color_continuous_scale=SCALES["violet"]
    )

    fig.update_layout(
        title=None,
        coloraxis_showscale=False,
        yaxis=dict(categoryorder="total ascending")
    )

    return chart_layout(
        fig,
        x_title="Sales ($)",
        y_title="Product Name"
    )

# Sales vs Profit Buble Chart
def bubble_sales_profit(df):
    fig = px.scatter(
        df,
        x="Sales",
        y="Gross Profit",
        size="Units",
        color="Division",
        hover_name="Product Name",
        color_discrete_sequence=CATEGORICAL
    )
    fig.update_traces(marker=dict(opacity=.7, line=dict(width=0)))
    fig.update_layout(
        title=None,
        coloraxis_showscale=False
    )

    return chart_layout(
        fig,
        x_title="Sales ($)",
        y_title="Gross Profit ($)",
        legend=True
    )


# ======================================================================
# ADVANCED LOGISTICS ANALYTICS
# All charts below take ORDER-LEVEL data (see delivery_analytics.to_orders)
# ======================================================================
def _empty_figure(message):
    """Friendly placeholder when a chart has no data to show."""
    fig = go.Figure()
    fig.add_annotation(
        text=message, showarrow=False, xref="paper", yref="paper",
        x=0.5, y=0.5, font=dict(size=14, color=palette()["muted"])
    )
    chart_layout(fig)
    fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False))

    return fig


def _vline(fig, x, label, color, position="top"):
    fig.add_vline(
        x=x, line_dash="dash", line_width=2, line_color=color,
        annotation_text=label, annotation_position=position,
        annotation_font=dict(size=11, color=color)
    )


# ---------------- Delivery performance ----------------
def lead_time_distribution(orders, pct=da.DEFAULT_SLOW_PCT):
    threshold, _ = da.slow_baseline(orders, pct)

    fig = px.histogram(
        orders,
        x="Shipping Days",
        nbins=40,
        color_discrete_sequence=[SCALES["sky"][1]]
    )
    fig.update_traces(marker_line_width=0, opacity=0.9)

    _vline(fig, orders["Shipping Days"].median(), "Median",
           SEMANTIC["success"], "top left")
    _vline(fig, threshold, f"Slow &gt; {threshold:.0f} days (P{pct})",
           SEMANTIC["danger"], "top right")

    chart_layout(fig, x_title="Lead time (days)", y_title="Orders")
    fig.update_layout(bargap=0.04)

    return fig


def lead_time_by_ship_mode(orders):
    fig = px.box(
        orders,
        x="Ship Mode",
        y="Shipping Days",
        color="Ship Mode",
        points=False,
        color_discrete_sequence=CATEGORICAL
    )

    return chart_layout(
        fig, x_title="Ship Mode", y_title="Lead time (days)"
    )


def lead_time_trend(orders):
    monthly = da.monthly_lead_time(orders)

    if len(monthly) < 2:
        return _empty_figure("Not enough order months to show a trend")

    long = monthly.melt(
        id_vars="Month",
        value_vars=["Average", "Median"],
        var_name="Metric",
        value_name="Days"
    )

    fig = px.line(
        long,
        x="Month",
        y="Days",
        color="Metric",
        markers=True,
        color_discrete_sequence=[palette()["primary"], SEMANTIC["warning"]]
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=7))

    return chart_layout(
        fig, x_title="Order month", y_title="Lead time (days)", legend=True
    )


def slow_rate_heatmap(orders, pct=da.DEFAULT_SLOW_PCT):
    matrix = da.region_mode_slow_rate(orders, pct)

    if matrix.isna().all().all():
        return _empty_figure("Not enough orders per region and ship mode")

    fig = px.imshow(
        matrix,
        aspect="auto",
        color_continuous_scale=SCALES["rose"]
    )
    fig.update_traces(
        xgap=3, ygap=3,
        texttemplate="%{z:.0f}%",
        hovertemplate="%{y} · %{x}<br>Slow orders: %{z:.1f}%<extra></extra>"
    )
    fig.update_layout(coloraxis_showscale=False)

    chart_layout(fig, x_title="Ship Mode", y_title="Region")
    fig.update_layout(yaxis=dict(showgrid=False))

    return fig


# ---------------- Delay risk ----------------
def delay_risk_chart(table, by, overall, top=15):
    """Slow-order rate per group, coloured by risk level."""
    if table.empty:
        return _empty_figure(
            "No group has enough orders - lower the minimum orders slider"
        )

    data = table.head(top)

    fig = px.bar(
        data,
        x="Slow Rate (%)",
        y=by,
        orientation="h",
        color="Risk Level",
        color_discrete_map=RISK_COLORS,
        category_orders={"Risk Level": ["High", "Moderate", "Low"]},
        text_auto=".0f",
        hover_data={"Orders": True, "Avg Days": ":.0f", "Risk Index": ":.2f"}
    )

    _vline(fig, overall, f"Overall {overall:.0f}%", palette()["muted"], "top")

    chart_layout(fig, x_title="Slow-order rate (%)", y_title=by, legend=True)
    fig.update_layout(
        barmode="relative",
        yaxis=dict(categoryorder="total ascending"),
        height=max(CHART_HEIGHT, 26 * len(data) + 120)
    )

    return fig


# ---------------- Customers & destinations ----------------
def order_frequency_chart(orders):
    frequency = da.order_frequency(orders)

    fig = px.bar(
        frequency,
        x="Frequency",
        y="Customers",
        text_auto=",.0f",
        hover_data={"Sales": ":$,.0f"},
        color_discrete_sequence=[SCALES["indigo"][1]]
    )

    return chart_layout(
        fig, x_title="Orders placed per customer", y_title="Customers"
    )


def sales_by_country(orders):
    country = orders.groupby("Country/Region", as_index=False)["Sales"].sum()

    fig = px.pie(
        country,
        names="Country/Region",
        values="Sales",
        hole=0.55,
        color_discrete_sequence=CATEGORICAL
    )
    fig.update_traces(
        textposition="auto",
        textinfo="percent",
        insidetextorientation="horizontal",
        textfont=dict(size=13),
        marker=dict(line=dict(color=palette()["surface"], width=3))
    )

    return chart_layout(fig, legend=True)


def destination_pareto(orders, top=15):
    sales = (
        orders.groupby("State/Province")["Sales"]
        .sum()
        .sort_values(ascending=False)
    )
    shown = sales.head(top)
    cumulative = shown.cumsum() / sales.sum() * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=shown.index, y=shown.values, name="Sales",
            marker_color=SCALES["indigo"][1],
            hovertemplate="%{x}<br>Sales: $%{y:,.0f}<extra></extra>"
        ),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(
            x=cumulative.index, y=cumulative.values,
            name="Cumulative share", mode="lines+markers",
            line=dict(width=3, color=SEMANTIC["warning"]),
            marker=dict(size=7),
            hovertemplate="%{x}<br>Cumulative: %{y:.1f}%<extra></extra>"
        ),
        secondary_y=True
    )

    chart_layout(fig, x_title="State/Province", y_title="Sales ($)", legend=True)

    muted = palette()["muted"]
    fig.update_xaxes(tickangle=-35)
    fig.update_yaxes(
        secondary_y=True, range=[0, 105], ticksuffix="%", showgrid=False,
        tickfont=dict(size=12, color=muted),
        title=dict(text="Cumulative share of sales",
                   font=dict(size=12, color=muted))
    )

    return fig


def destination_quadrant(orders, min_orders=da.DEFAULT_MIN_ORDERS):
    states = da.destination_summary(orders, "State/Province", min_orders)

    if len(states) < 3:
        return _empty_figure(
            "Fewer than 3 destinations have enough orders - lower the minimum"
        )

    states["Region"] = states["State/Province"].map(
        orders.groupby("State/Province")["Region"].first()
    )

    fig = px.scatter(
        states,
        x="Avg Shipping Days",
        y="Sales",
        size="Orders",
        size_max=38,
        color="Region",
        hover_name="State/Province",
        color_discrete_sequence=CATEGORICAL,
        hover_data={"Orders": True, "Avg Shipping Days": ":.0f", "Sales": ":,.0f"}
    )
    fig.update_traces(
        marker=dict(opacity=0.8, line=dict(width=1.5, color=palette()["surface"]))
    )

    muted = palette()["muted"]
    fig.add_vline(
        x=states["Avg Shipping Days"].median(), line_dash="dot",
        line_color=muted, annotation_text="Median lead time",
        annotation_font=dict(size=11, color=muted)
    )
    fig.add_hline(
        y=states["Sales"].median(), line_dash="dot", line_color=muted,
        annotation_text="Median sales",
        annotation_font=dict(size=11, color=muted)
    )

    return chart_layout(
        fig, x_title="Average lead time (days)", y_title="Sales ($)", legend=True
    )


_METRIC_SCALE = {
    "Sales": "indigo",
    "Gross Profit": "emerald",
    "Orders": "sky",
    "Avg Shipping Days": "rose",
}


def top_destinations_chart(orders, level, metric, min_orders, top=10):
    # Averages are only meaningful for destinations with enough orders
    floor = min_orders if metric == "Avg Shipping Days" else 1
    table = da.destination_summary(orders, level, floor)

    if table.empty:
        return _empty_figure("No destination has enough orders")

    data = table.sort_values(metric, ascending=False).head(top)

    fig = px.bar(
        data,
        x=metric,
        y=level,
        orientation="h",
        color=metric,
        color_continuous_scale=SCALES[_METRIC_SCALE[metric]],
        text_auto=".0f" if metric == "Avg Shipping Days" else ".2s"
    )
    fig.update_layout(
        coloraxis_showscale=False,
        yaxis=dict(categoryorder="total ascending")
    )

    return chart_layout(fig, x_title=metric, y_title=level)
