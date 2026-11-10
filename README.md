# 📦 Factory-to-Customer Shipping Route Efficiency Analysis

A Logistics & Supply Chain analytics project for the **Nassau Candy Distributor** dataset. It combines a data pipeline (ingestion, transformation, route analysis) with a premium, responsive **Streamlit dashboard** that covers shipping performance, delivery-delay risk, sales, products, customers and destinations.

> **Author:** Divyesh Chavda · B.E. Artificial Intelligence & Data Science

---

## 🎯 Project Overview

- Analyze shipping efficiency and compare ship modes, regions, states and cities
- Identify fast and slow destinations and where delivery delays concentrate
- Analyze sales, profitability, products, customers and destination concentration
- Present everything in an interactive dashboard with dark and light themes

---

## ✨ Features

### Dashboard (7 tabs)

| Tab | What it shows |
|---|---|
| 📊 **Overview** | Sales by region, gross profit, sales vs profit, shipping days by ship mode |
| 🚚 **Route Analysis** | Route summary tiles, route performance table, fastest/slowest cities, shipping by state and region |
| 💰 **Sales Analysis** | Monthly sales trend, sales by ship mode and division, sales distribution |
| 📦 **Product Analysis** | Profit by product, top products, sales-vs-profit bubble chart |
| ⏱️ **Delivery Analytics** | Lead-time distribution, ship-mode box plots, monthly lead-time trend, slow-shipment heatmap, **Delay Risk Explorer** (by state, region, ship mode, division, country or city), product-line efficiency, actionable insights |
| 👥 **Customers & Destinations** | Order-frequency and repeat-customer analysis, sales by country, destination concentration (Pareto), lead time vs sales per destination, **Top Destinations** explorer, top customers, insights |
| 📄 **Data Explorer** | Dataset health metrics, text search, table view and CSV download |

### Interactive controls

- **Sidebar filters:** Region, Ship Mode, State and Division (cascading), plus an Order Date range; a counter shows how many records are in view
- **Dark / light theme** toggle in the sidebar
- **Delivery Analytics sliders:** slow-shipment percentile threshold and minimum orders per group
- Explorer selectors for delay-risk dimension, destination level and ranking metric

### Design

Inter typography, KPI cards, rounded card layout, subtle animations, theme-aware Plotly charts, and a responsive layout for desktop, tablet and mobile.

---

## 📐 Analytics Method and Data Scope

- **Lead time** = `Ship Date − Order Date` (the `Shipping Days` column).
- Advanced analytics work **per order** (one row per `Order ID`); order lines share the same shipping attributes.
- The dataset has **no promised delivery date**, so an order is **slow** when it is slower than the chosen percentile of the current selection. This is a relative measure.
- **Risk level** compares each group's slow-order rate with the overall rate: High ≥ 1.25×, Moderate ≥ 1.0×, otherwise Low. Groups below the minimum order count are excluded.
- **Not analysed, because the data does not support it:**
  - *Factory-wise efficiency* – no column links an order or product to a factory (`factory_coordinates.csv` only lists locations). Product-line efficiency is shown instead.
  - *Shipping cost* – the `Cost` column is product cost (`Sales − Gross Profit`), not freight.
  - *Route efficiency from an origin* – only destinations are recorded.

> **Dataset note:** shipping durations in this dataset are unusually long compared with real-world logistics (average 1,344 days). Use `Shipping Days` to compare groups against each other, not to judge service levels.

---

## 📊 Dataset

| Item | Value |
|---|---:|
| Records | 10,194 (18 original columns, 20 after processing) |
| Unique orders | 8,549 |
| Unique customers | 5,044 |
| Destinations | 59 states/provinces, 542 cities, 2 countries |
| Products | 15 across 3 divisions |
| Regions / ship modes | 4 / 4 |
| Order dates | 2024-01-02 to 2025-12-31 |

**Engineered features** (see `src/components/data_transformation.py`):

```text
Shipping Days     = Ship Date - Order Date
Profit Margin (%) = (Gross Profit / Sales) x 100
```

### Key KPIs

| KPI | Value |
|---|---:|
| Total Sales | $141,783.63 |
| Gross Profit | $93,442.80 |
| Unique Orders | 8,549 |
| Units Sold | 38,654 |
| Avg. Shipping Days | 1,344.24 |
| Profit Margin (Profit ÷ Sales, shown on the dashboard) | 65.91% |
| Avg. per-record Profit Margin (EDA) | 66.51% |

### Key findings from the data

- Sales and Gross Profit are strongly correlated (≈ 0.98).
- The **Pacific** region has the highest average Sales and Gross Profit per record.
- **Second Class** has the highest average Sales among ship modes.
- The **Atlantic** region has the highest average Shipping Days.
- **New York City** has the highest Route Score among analyzed high-volume routes.
- Shipping-time differences between ship modes and regions are relatively small.

---

## 🛠️ Tech Stack

Python · Pandas · NumPy · Plotly · Streamlit (EDA notebook also uses Matplotlib and Seaborn)

**Tested with:** Python 3.12 on Linux; Streamlit 1.50.0 and 1.67.0; Plotly 6.0.0 and 7.1.0; pandas 2.3.3 and 3.0.6. `requirements.txt` sets these as minimum versions.

---

## 🚀 Installation

```bash
# 1. Extract the ZIP and enter the project folder
unzip Factory_to_Customer_Shipping_Route_Efficiency_Analysis.zip
cd Factory_to_Customer_Shipping_Route_Efficiency_Analysis

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## ▶️ Run the Application

```bash
streamlit run app.py
```

Then open the URL shown in the terminal (normally http://localhost:8501).

### Optional

```bash
# Rebuild artifacts/ from data/ (run from the project root) and print KPIs
python test.py

# Open the EDA notebook (Jupyter is not part of requirements.txt)
pip install jupyter
jupyter notebook notebook/EDA.ipynb
```

---

## 🏗️ Project Structure

```text
Factory_to_Customer_Shipping_Route_Efficiency_Analysis/
├── .streamlit/
│   └── config.toml   # Streamlit base theme (dark), primary colour, toolbar
├── artifacts/
│   ├── factory_coordinates.csv   # Factory locations (reference only)
│   ├── processed_data.csv   # Cleaned dataset used by the dashboard
│   └── raw_data.csv   # Raw copy produced by data ingestion
├── assets/
│   └── style.css   # Premium theme: layout, cards, tabs, responsive rules
├── data/
│   └── Nassau-Candy-Distributor.csv   # Original source dataset
├── notebook/
│   └── EDA.ipynb   # Exploratory data analysis
├── Report/   # Project report (PDF and DOCX)
│   ├── Factory_to_Custermer_Route_Shipping_Efficiency_Analysis Report.pdf
│   └── Factory_to_Custermer_Route_Shipping_Efficiency_Analysis.docx
├── src/
│   ├── components/
│   │   ├── __init__.py
│   │   ├── data_ingestion.py   # Reads the source CSV into artifacts/
│   │   ├── data_transformation.py   # Cleaning and feature engineering
│   │   ├── delivery_analytics.py   # Advanced delivery, delay-risk and customer analytics
│   │   └── route_analysis.py   # RouteAnalysis: KPIs, summaries, route score
│   ├── ui/
│   │   ├── analytics_tabs.py   # Delivery Analytics and Customers & Destinations tabs
│   │   ├── cards.py   # Hero banner, section headings, KPI cards, callouts
│   │   ├── chart_card.py   # Chart cards and chart grid helpers
│   │   ├── charts.py   # All Plotly charts (theme-aware)
│   │   ├── data_explorer.py   # Data Explorer tab
│   │   ├── filters.py   # Sidebar filters
│   │   ├── insights.py   # Business insight cards
│   │   ├── navigation.py   # Tabs, sidebar brand, dark-mode toggle
│   │   ├── route_summary.py   # Route summary tiles and route table
│   │   └── theme.py   # Dark/light colour tokens and chart palettes
│   ├── __init__.py
│   ├── exception.py   # Custom exception with traceback details
│   └── logger.py   # File logging (creates logs/ at run time)
├── .gitignore
├── app.py   # Streamlit entry point (layout, KPIs, tabs)
├── README.md
├── requirements.txt   # Python dependencies
├── setup.py   # Package metadata
└── test.py   # Runs the data pipeline end to end and prints KPIs
```

`logs/` is created automatically at run time and is not part of the distribution.

---

## ⚙️ Configuration Notes

- `.streamlit/config.toml` sets Streamlit's base theme to dark. The dashboard's light mode relies on this, so keep the file. If a different theme is chosen in Streamlit's own menu, data tables may not match the dashboard theme.
- The Inter font is loaded from Google Fonts; offline, the dashboard falls back to system fonts.
- If the dataset is missing, empty or lacks required columns, the app shows a message explaining how to regenerate it with `python test.py`.

## ⚙️ Data Workflow

```text
data/Nassau-Candy-Distributor.csv
        ↓  data_ingestion.py
artifacts/raw_data.csv
        ↓  data_transformation.py
artifacts/processed_data.csv
        ↓  route_analysis.py / delivery_analytics.py
Streamlit dashboard (app.py)
```

---

## 👤 Author

**Divyesh Chavda**
B.E. Artificial Intelligence & Data Science
