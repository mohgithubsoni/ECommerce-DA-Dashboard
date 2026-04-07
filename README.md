# E-Commerce Sales Data Analytics Dashboard

A scalable analytics pipeline that generates, cleans, processes, and visualizes e-commerce transactional data.

## Project Structure

```
ecommerce_dashboard/
│
├── data_generator.py   # Generates synthetic transactional dataset (5000+ rows)
├── pipeline.py         # EcommercePipeline class — clean, transform, aggregate
├── dashboard.py        # Matplotlib/Seaborn visualizations & dashboard builder
├── main.py             # Entry point — runs the full pipeline end-to-end
│
├── data/
│   └── raw_transactions.csv     # Generated raw data
│
└── output/
    ├── dashboard.png            # Final analytics dashboard (PNG)
    └── reports/
        ├── monthly_revenue.csv
        ├── category_performance.csv
        ├── top_products.csv
        ├── regional_breakdown.csv
        └── quarterly_trend.csv
```

## Tech Stack

- **Python 3.8+**
- **Pandas** — data cleaning, transformation, SQL-style aggregations
- **NumPy** — synthetic data generation, vectorised operations
- **Matplotlib & Seaborn** — charting and dashboard layout

## How to Run

```bash
# Install dependencies
pip install pandas numpy matplotlib seaborn

# Run the full pipeline
python main.py
```

## Pipeline Overview

### 1. Data Generation (`data_generator.py`)
- Generates 5,000 synthetic orders across 7 product categories, 5 regions, over 2 years
- Includes: order ID, date, category, product, region, unit price, quantity, discount, return flag

### 2. Data Processing (`pipeline.py`)
The `EcommercePipeline` class implements a 2-step pipeline:

**Step 1 — Clean & Validate**
- Date parsing with error handling
- Null/duplicate removal
- Outlier clipping (quantity > 100)
- String standardisation (strip, title-case)
- Feature engineering: year, month, quarter, week, day_of_week

**Step 2 — SQL-style Aggregations**
| Method | Description |
|--------|-------------|
| `monthly_revenue()` | Revenue, orders, AOV, MoM growth, cumulative |
| `category_performance()` | Revenue share, return rate, avg discount by category |
| `top_products(n)` | Top N products by net revenue |
| `regional_breakdown()` | Revenue and orders by region |
| `quarterly_trend()` | Quarter-over-quarter performance |

### 3. Dashboard (`dashboard.py`)
6-panel dark-theme dashboard:
- **Monthly Revenue Trend** — line chart with MoM growth annotations
- **Cumulative Revenue** — running total over time
- **Revenue by Category** — horizontal bar with revenue share %
- **Order Share by Category** — donut/pie chart
- **Top 10 Products** — horizontal bar chart
- **Return Rate by Category** — bar chart with avg reference line
- **KPI Summary Bar** — 6 headline metrics at the top

## Key Metrics Tracked
- Total Net Revenue
- Total Orders & Average Order Value
- Units Sold
- Month-over-Month Revenue Growth
- Category Revenue Share
- Product-level Performance
- Return Rates by Category
- Regional Breakdown

## Resume Bullets This Covers
- ✅ Built a scalable **data processing pipeline** to clean, transform, and structure raw transactional datasets
- ✅ Utilized **SQL-style aggregations in Python/Pandas** for filtering, grouping, and trend analysis on 5,000+ row datasets
- ✅ Developed **data visualizations and reports** highlighting key metrics: revenue trends, product performance, return rates
