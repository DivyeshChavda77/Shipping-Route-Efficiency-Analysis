"""Advanced logistics analytics (pure pandas, no Streamlit).

Rules this module follows:
  * Only existing dataset columns are used.
  * Lead time = "Shipping Days" (Ship Date - Order Date).
  * Analysis is done per order (one row per Order ID). Every line of an order
    shares the same ship date, ship mode, customer and destination.
  * The dataset has no promised delivery date, so a "slow" order is a
    *relative* label: lead time above the chosen percentile of the current
    selection.
  * Not analysed because the data does not support it: factory-wise
    efficiency (no order/product -> factory link), shipping cost ("Cost" is
    product cost: Sales - Gross Profit = Cost) and true route efficiency
    (destination only, no origin).
"""

import numpy as np
import pandas as pd

DEFAULT_SLOW_PCT = 75
DEFAULT_MIN_ORDERS = 30
HIGH_RISK_INDEX = 1.25      # slow rate >= 1.25x the overall slow rate
MODERATE_RISK_INDEX = 1.00  # slow rate >= overall slow rate


# ----------------------------------------------------------------------
# Preparation
# ----------------------------------------------------------------------
def to_orders(df):
    """Collapse order lines into one row per Order ID."""
    orders = (
        df.groupby("Order ID", as_index=False)
        .agg(
            **{
                "Order Date": ("Order Date", "first"),
                "Customer ID": ("Customer ID", "first"),
                "Ship Mode": ("Ship Mode", "first"),
                "Country/Region": ("Country/Region", "first"),
                "Region": ("Region", "first"),
                "State/Province": ("State/Province", "first"),
                "City": ("City", "first"),
                "Division": ("Division", "first"),
                "Product Name": ("Product Name", "first"),
                "Shipping Days": ("Shipping Days", "first"),
                "Sales": ("Sales", "sum"),
                "Gross Profit": ("Gross Profit", "sum"),
                "Units": ("Units", "sum"),
            }
        )
    )

    orders["Order Date"] = pd.to_datetime(orders["Order Date"], errors="coerce")

    return orders


def slow_baseline(orders, pct):
    """(threshold in days, overall slow-order rate in %) for a percentile."""
    days = orders["Shipping Days"]
    threshold = days.quantile(pct / 100)

    return threshold, (days > threshold).mean() * 100


# ----------------------------------------------------------------------
# Shipping performance
# ----------------------------------------------------------------------
def lead_time_stats(orders):
    days = orders["Shipping Days"]
    mean = days.mean()

    return {
        "orders": len(days),
        "mean": mean,
        "median": days.median(),
        "p90": days.quantile(0.90),
        "cv": (days.std(ddof=0) / mean * 100) if mean else 0.0,
    }


def monthly_lead_time(orders):
    data = orders.dropna(subset=["Order Date"])

    return (
        data.assign(Month=data["Order Date"].dt.to_period("M").astype(str))
        .groupby("Month", as_index=False)
        .agg(
            Orders=("Order ID", "size"),
            **{
                "Average": ("Shipping Days", "mean"),
                "Median": ("Shipping Days", "median"),
            },
        )
        .sort_values("Month")
    )


# ----------------------------------------------------------------------
# Delay analysis & risk
# ----------------------------------------------------------------------
def risk_table(orders, by, pct, min_orders):
    """Slow-order rate and risk level for every group of `by`."""
    threshold, overall = slow_baseline(orders, pct)

    table = (
        orders.assign(_slow=orders["Shipping Days"] > threshold)
        .groupby(by, as_index=False)
        .agg(
            Orders=("Order ID", "size"),
            **{
                "Avg Days": ("Shipping Days", "mean"),
                "Median Days": ("Shipping Days", "median"),
                "Slow Orders": ("_slow", "sum"),
                "Sales": ("Sales", "sum"),
            },
        )
    )

    table = table[table["Orders"] >= min_orders].copy()

    table["Slow Rate (%)"] = table["Slow Orders"] / table["Orders"] * 100
    table["Risk Index"] = table["Slow Rate (%)"] / overall if overall else 0.0
    table["Risk Level"] = np.select(
        [
            table["Risk Index"] >= HIGH_RISK_INDEX,
            table["Risk Index"] >= MODERATE_RISK_INDEX,
        ],
        ["High", "Moderate"],
        default="Low",
    )

    return table.sort_values("Slow Rate (%)", ascending=False).reset_index(drop=True)


def region_mode_slow_rate(orders, pct, min_cell=10):
    """Region x Ship Mode matrix of slow-order rates (%); small cells blank."""
    threshold, _ = slow_baseline(orders, pct)

    cells = (
        orders.assign(_slow=orders["Shipping Days"] > threshold)
        .groupby(["Region", "Ship Mode"])
        .agg(n=("Order ID", "size"), rate=("_slow", "mean"))
    )
    cells.loc[cells["n"] < min_cell, "rate"] = np.nan

    return (cells["rate"] * 100).unstack("Ship Mode")


# ----------------------------------------------------------------------
# Customers & destinations
# ----------------------------------------------------------------------
def customer_stats(orders):
    per_customer = orders.groupby("Customer ID").size()
    customers = len(per_customer)

    return {
        "customers": customers,
        "repeat_rate": (per_customer > 1).mean() * 100 if customers else 0.0,
        "orders_per_customer": per_customer.mean() if customers else 0.0,
        "avg_order_value": orders["Sales"].sum() / len(orders),
    }


def order_frequency(orders):
    """Customers (and their sales) grouped by number of orders placed."""
    per_customer = orders.groupby("Customer ID").agg(
        Orders=("Order ID", "size"), Sales=("Sales", "sum")
    )
    labels = ["1 order", "2 orders", "3 orders", "4+ orders"]
    per_customer["Frequency"] = pd.cut(
        per_customer["Orders"], [0, 1, 2, 3, np.inf], labels=labels
    )

    return (
        per_customer.groupby("Frequency", observed=False)
        .agg(Customers=("Orders", "size"), Sales=("Sales", "sum"))
        .reset_index()
    )


def top_customers(orders, pct, n=15):
    threshold, _ = slow_baseline(orders, pct)

    return (
        orders.assign(_slow=orders["Shipping Days"] > threshold)
        .groupby("Customer ID", as_index=False)
        .agg(
            Orders=("Order ID", "size"),
            Sales=("Sales", "sum"),
            **{
                "Gross Profit": ("Gross Profit", "sum"),
                "Avg Days": ("Shipping Days", "mean"),
                "Slow Orders": ("_slow", "sum"),
            },
        )
        .sort_values("Sales", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )


def destination_summary(orders, by, min_orders=1):
    table = (
        orders.groupby(by, as_index=False)
        .agg(
            Orders=("Order ID", "size"),
            Sales=("Sales", "sum"),
            **{
                "Gross Profit": ("Gross Profit", "sum"),
                "Avg Shipping Days": ("Shipping Days", "mean"),
            },
        )
    )

    return table[table["Orders"] >= min_orders].reset_index(drop=True)


def sales_concentration(orders, by="State/Province", top=5):
    """Share (%) of total sales coming from the top-N destinations."""
    sales = orders.groupby(by)["Sales"].sum().sort_values(ascending=False)
    total = sales.sum()

    return sales.head(top).sum() / total * 100 if total else 0.0


# ----------------------------------------------------------------------
# Actionable insights -> list of (tone, icon, text)
# ----------------------------------------------------------------------
def delivery_insights(orders, pct, min_orders):
    insights = []
    threshold, overall = slow_baseline(orders, pct)
    stats = lead_time_stats(orders)

    # Highest / lowest risk destination state
    states = risk_table(orders, "State/Province", pct, min_orders)
    if len(states) >= 2:
        worst, best = states.iloc[0], states.iloc[-1]
        insights.append((
            "warning", "🚩",
            f"{worst['State/Province']} has the highest slow-shipment rate "
            f"({worst['Slow Rate (%)']:.0f}% vs {overall:.0f}% overall, "
            f"{int(worst['Orders']):,} orders). Prioritise a carrier and "
            f"routing review for this destination."
        ))
        insights.append((
            "success", "✅",
            f"{best['State/Province']} is the most reliable destination "
            f"({best['Slow Rate (%)']:.0f}% slow orders across "
            f"{int(best['Orders']):,} orders) - a useful benchmark for "
            f"weaker destinations."
        ))

    # Do ship modes actually differ?
    modes = risk_table(orders, "Ship Mode", pct, 10)
    if len(modes) >= 2 and stats["median"]:
        medians = modes.set_index("Ship Mode")["Median Days"]
        fast, slow = medians.idxmin(), medians.idxmax()
        spread = medians.max() - medians.min()
        relative = spread / stats["median"] * 100

        if relative < 10:
            insights.append((
                "warning", "⚖️",
                f"Ship modes perform almost identically: median lead times "
                f"differ by only {spread:.0f} days ({relative:.0f}%) between "
                f"{fast} and {slow}. Ship mode names do not translate into "
                f"measurable speed - review service levels with carriers."
            ))
        else:
            insights.append((
                "info", "🚚",
                f"{fast} is the fastest ship mode (median {medians[fast]:.0f} "
                f"days) and {slow} the slowest ({medians[slow]:.0f} days), a "
                f"{relative:.0f}% gap."
            ))

    # Worst region / ship-mode combination
    matrix = region_mode_slow_rate(orders, pct)
    if matrix.notna().any().any():
        stacked = matrix.stack()
        region, mode = stacked.idxmax()
        insights.append((
            "warning", "🔥",
            f"{region} region shipped via {mode} has the highest "
            f"slow-shipment rate of any combination ({stacked.max():.0f}% "
            f"vs {overall:.0f}% overall)."
        ))

    # Recent trend
    monthly = orders.dropna(subset=["Order Date"])
    months = monthly["Order Date"].dt.to_period("M")
    if months.nunique() >= 6:
        cutoff = sorted(months.unique())[-3]
        recent = monthly.loc[months >= cutoff, "Shipping Days"].mean()
        prior = monthly.loc[months < cutoff, "Shipping Days"].mean()
        change = (recent - prior) / prior * 100

        if abs(change) < 3:
            insights.append((
                "info", "📈",
                f"Lead times are stable: orders from the latest 3 months "
                f"average {recent:.0f} days vs {prior:.0f} days earlier."
            ))
        else:
            higher = change > 0
            insights.append((
                "warning" if higher else "success",
                "📈" if higher else "📉",
                f"Orders from the latest 3 months average {recent:.0f} days, "
                f"{abs(change):.0f}% {'higher' if higher else 'lower'} than "
                f"earlier months ({prior:.0f} days)."
            ))

    # Spread of lead times
    if stats["median"]:
        insights.append((
            "info", "📊",
            f"The slowest 10% of orders take {stats['p90']:.0f}+ days, "
            f"{stats['p90'] / stats['median']:.1f}x the median "
            f"({stats['median']:.0f} days) - delivery times are "
            f"{'highly' if stats['cv'] > 25 else 'moderately'} variable "
            f"(variability {stats['cv']:.0f}%)."
        ))

    return insights


def customer_insights(orders, pct):
    insights = []
    threshold, _ = slow_baseline(orders, pct)
    customers = customer_stats(orders)

    insights.append((
        "info", "👥",
        f"{customers['repeat_rate']:.0f}% of {customers['customers']:,} "
        f"customers ordered more than once (average "
        f"{customers['orders_per_customer']:.1f} orders per customer)."
    ))

    destinations = orders["State/Province"].nunique()
    if destinations > 5:
        share = sales_concentration(orders, "State/Province", 5)
        insights.append((
            "info", "🧭",
            f"The top 5 of {destinations} states/provinces generate "
            f"{share:.0f}% of sales - protect delivery quality there first."
        ))

    total_sales = orders["Sales"].sum()
    if total_sales:
        exposed = orders.loc[orders["Shipping Days"] > threshold, "Sales"].sum()
        insights.append((
            "warning", "💸",
            f"${exposed:,.0f} ({exposed / total_sales * 100:.0f}%) of sales "
            f"value sits in slow shipments (above {threshold:.0f} days)."
        ))

    top = top_customers(orders, pct, 1)
    if not top.empty and total_sales:
        row = top.iloc[0]
        insights.append((
            "success", "🥇",
            f"Customer {int(row['Customer ID'])} is the largest account: "
            f"${row['Sales']:,.0f} ({row['Sales'] / total_sales * 100:.1f}% "
            f"of sales) across {int(row['Orders'])} orders."
        ))

    countries = destination_summary(orders, "Country/Region")
    if len(countries) >= 2:
        countries = countries.sort_values("Orders", ascending=False)
        main, other = countries.iloc[0], countries.iloc[1]
        insights.append((
            "info", "🌍",
            f"{other['Country/Region']} accounts for "
            f"{other['Orders'] / orders.shape[0] * 100:.1f}% of orders, with an "
            f"average lead time of {other['Avg Shipping Days']:.0f} days vs "
            f"{main['Avg Shipping Days']:.0f} days for {main['Country/Region']}."
        ))

    return insights
