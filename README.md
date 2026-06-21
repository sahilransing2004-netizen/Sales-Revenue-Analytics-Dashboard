#  Sales & Revenue Analytics Dashboard

A multi-page Power BI dashboard built on 3,000+ sales transactions (2022–2024) covering regions, product categories, sales representatives, and monthly targets. Designed to support executive-level decision-making through interactive visualizations, KPI tracking, and drill-through analysis.

##  Dataset

The project uses three sheets:

- **Orders (3,000 rows)** – Sales transactions, products, regions, and sales reps
- **Targets (720 rows)** – Monthly sales targets by region and category
- **Customers (~2,100 rows)** – Customer profiles and segments

##  Dashboard Pages

### 1. Executive Summary
- KPI Cards (Sales, Profit, Margin, Orders, Achievement %)
- Monthly Sales vs Target
- Sales by Region
- Sales by Category

### 2. Product & Category Analysis
- Category-wise Sales & Profit Margin
- Top Sub-Categories by Sales
- Sales vs Profit Margin Scatter Plot
- Treemap Breakdown

### 3. Sales Rep & Regional Performance
- Sales Rep Leaderboard
- Top 10 Sales Reps
- State-wise Sales Map
- Quarterly Regional Sales

##  DAX Measures

- Total Sales
- Total Profit
- Profit Margin %
- Total Orders
- Average Order Value
- Achievement %
- MoM Growth %
- YoY Growth %

##  Key Features

- Time Intelligence (MoM & YoY Growth)
- Drill-Through Navigation
- Conditional Formatting
- Synced Slicers Across Pages
- Interactive Filtering

| Tool | Purpose |
|--------|---------|
| Power BI Desktop | Dashboard Development |
| DAX | Measures & Calculations |
| Power Query (M) | Data Cleaning & Transformation |
| Python (Pandas) | Dataset Preparation |
| Excel | Source Data Storage |

##  Files

```text
SalesRevenueDashboard.pbix
Sales_Dashboard_Dataset.xlsx
README.md
```
