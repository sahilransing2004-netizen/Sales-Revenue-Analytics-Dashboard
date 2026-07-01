# Sales & Revenue Analytics Dashboard

An interactive, multi-page sales analytics dashboard built with **Python, Dash & Plotly**, analyzing 3,000+ synthetic sales transactions (2022–2024) across regions, product categories, and sales representatives. Designed to support executive-level decision-making through KPI tracking, trend analysis, and drill-down visualizations.

Live demo: _add your Render URL here after deploying_

## Dataset

Three datasets, generated synthetically for this project (`data/generate_data.py`):

| Dataset | Rows | Description |
|---|---|---|
| Orders | 3,000 | Sales transactions with product, region, category, and sales rep detail |
| Targets | 720 | Monthly sales targets by region and category |
| Customers | ~2,100 | Customer profiles and segments |

## Dashboard Pages

**1. Executive Summary**
- KPI cards: Total Sales, Total Profit, Margin %, Total Orders, Average Order Value, Achievement %
- Monthly Sales vs Target
- Sales by Region (donut)
- Sales by Category (bar)

**2. Product & Category Analysis**
- Category-wise Sales & Profit Margin (combo chart)
- Top Sub-Categories by Sales
- Sales vs Profit Margin scatter (bubble sized by order count)
- Treemap breakdown (Category → Sub-Category)

**3. Sales Rep & Regional Performance**
- Sales Rep Leaderboard
- Top 10 Sales Reps by order count
- State-wise Sales
- Quarterly Regional Sales trend

All charts respond to a shared filter bar (Region, Category, Date Range) at the top of the page — the equivalent of synced slicers across pages in a BI tool.

## Key Features

- Cross-filtering: Region / Category / Date Range filters apply to every KPI and chart simultaneously
- Time intelligence: monthly trend vs target, quarterly regional trend
- Interactive Plotly charts: hover tooltips, zoom, legend toggling
- Responsive layout (Bootstrap grid via `dash-bootstrap-components`)
- Dark, dashboard-style UI theme

## Tech Stack

| Tool | Purpose |
|---|---|
| Python (Pandas, NumPy) | Data generation & aggregation |
| Dash | App framework & callbacks |
| Plotly Express / Graph Objects | Visualizations |
| dash-bootstrap-components | Layout & responsive UI |
| Gunicorn | Production WSGI server |
| Docker / Render | Deployment |

## Project Structure

```
sales-revenue-analytics-dashboard/
├── app.py                  # Main Dash app: layout, callbacks
├── utils.py                # Data loading & KPI calculation helpers
├── data/
│   ├── generate_data.py    # Synthetic dataset generator
│   ├── orders.csv
│   ├── targets.csv
│   ├── customers.csv
│   └── Sales_Dashboard_Dataset.xlsx
├── assets/
│   └── style.css           # Dashboard theme
├── requirements.txt
├── Dockerfile
├── Procfile
└── README.md
```

## Running Locally

```bash
git clone https://github.com/sahilransing2004-netizen/sales-revenue-analytics-dashboard.git
cd sales-revenue-analytics-dashboard
pip install -r requirements.txt
python data/generate_data.py   # generates the CSV/xlsx dataset (already included in repo)
python app.py
```

Visit `http://localhost:8050`.

## Deployment (Render)

1. Push this repo to GitHub.
2. On Render: New → Web Service → connect this repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:server --bind 0.0.0.0:$PORT`
5. Render auto-detects the `Procfile` as well.

## Notes

This project reproduces the structure and analytical scope of a Power BI dashboard concept (KPI tracking, regional/category/rep breakdowns, target vs actual, drill-down analysis) rebuilt independently as a full-stack Python web app, and using synthetic data generated for this project.
