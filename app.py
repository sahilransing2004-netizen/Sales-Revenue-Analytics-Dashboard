import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils import load_data, filter_orders, kpi_summary, mom_yoy_growth, format_inr

orders_raw, targets_raw, customers_raw = load_data()

REGIONS = sorted(orders_raw["Region"].unique())
CATEGORIES = sorted(orders_raw["Category"].unique())
MIN_DATE = orders_raw["OrderDate"].min()
MAX_DATE = orders_raw["OrderDate"].max()

COLORS = {
    "bg": "#0f1220",
    "card": "#1a1e33",
    "accent": "#6c5ce7",
    "accent2": "#00d2d3",
    "text": "#eaeaf5",
    "muted": "#9a9cc0",
    "up": "#2ecc71",
    "down": "#ff6b6b",
}

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    title="Sales & Revenue Analytics Dashboard",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

# ---------------------------------------------------------------- layout: filters
filters_bar = dbc.Card(
    dbc.CardBody(
        dbc.Row(
            [
                dbc.Col([
                    html.Label("Region", className="filter-label"),
                    dcc.Dropdown(
                        id="f-region", options=[{"label": r, "value": r} for r in REGIONS],
                        multi=True, placeholder="All regions", className="dash-dd",
                    ),
                ], md=3, sm=12),
                dbc.Col([
                    html.Label("Category", className="filter-label"),
                    dcc.Dropdown(
                        id="f-category", options=[{"label": c, "value": c} for c in CATEGORIES],
                        multi=True, placeholder="All categories", className="dash-dd",
                    ),
                ], md=3, sm=12),
                dbc.Col([
                    html.Label("Date Range", className="filter-label"),
                    dcc.DatePickerRange(
                        id="f-dates",
                        min_date_allowed=MIN_DATE, max_date_allowed=MAX_DATE,
                        start_date=MIN_DATE, end_date=MAX_DATE,
                        display_format="DD MMM YYYY",
                    ),
                ], md=6, sm=12),
            ],
            align="end", className="g-3",
        )
    ),
    className="mb-3 filters-card",
)


def kpi_card(title, value_id, icon="📊"):
    return dbc.Col(
        dbc.Card(
            dbc.CardBody([
                html.Div(icon, className="kpi-icon"),
                html.Div(title, className="kpi-title"),
                html.Div(id=value_id, className="kpi-value"),
            ]),
            className="kpi-card",
        ),
        md=2, sm=6, xs=6,
    )


kpi_row = dbc.Row(
    [
        kpi_card("Total Sales", "kpi-sales", "💰"),
        kpi_card("Total Profit", "kpi-profit", "📈"),
        kpi_card("Margin %", "kpi-margin", "🎯"),
        kpi_card("Total Orders", "kpi-orders", "🧾"),
        kpi_card("Avg Order Value", "kpi-aov", "🛒"),
        kpi_card("Achievement %", "kpi-achv", "🏁"),
    ],
    className="mb-4 g-3",
)

# ---------------------------------------------------------------- tab layouts
tab_exec_summary = html.Div([
    dbc.Row([
        dbc.Col(dcc.Graph(id="g-sales-vs-target"), md=7),
        dbc.Col(dcc.Graph(id="g-region-donut"), md=5),
    ], className="g-3 mb-3"),
    dbc.Row([
        dbc.Col(dcc.Graph(id="g-category-bar"), md=12),
    ], className="g-3"),
])

tab_product = html.Div([
    dbc.Row([
        dbc.Col(dcc.Graph(id="g-cat-sales-margin"), md=6),
        dbc.Col(dcc.Graph(id="g-top-subcat"), md=6),
    ], className="g-3 mb-3"),
    dbc.Row([
        dbc.Col(dcc.Graph(id="g-scatter-sales-margin"), md=6),
        dbc.Col(dcc.Graph(id="g-treemap"), md=6),
    ], className="g-3"),
])

tab_reps = html.Div([
    dbc.Row([
        dbc.Col(dcc.Graph(id="g-rep-leaderboard"), md=6),
        dbc.Col(dcc.Graph(id="g-top10-reps"), md=6),
    ], className="g-3 mb-3"),
    dbc.Row([
        dbc.Col(dcc.Graph(id="g-state-map"), md=7),
        dbc.Col(dcc.Graph(id="g-quarterly-region"), md=5),
    ], className="g-3"),
])

app.layout = dbc.Container(
    [
        html.Div([
            html.H2("Sales & Revenue Analytics Dashboard", className="app-title"),
            html.P("Interactive analysis of 3,000+ transactions across regions, categories & reps",
                   className="app-subtitle"),
        ], className="mb-3 mt-3"),
        filters_bar,
        kpi_row,
        dbc.Tabs(
            [
                dbc.Tab(tab_exec_summary, label="1. Executive Summary", tab_id="tab-exec"),
                dbc.Tab(tab_product, label="2. Product & Category Analysis", tab_id="tab-product"),
                dbc.Tab(tab_reps, label="3. Sales Rep & Regional Performance", tab_id="tab-reps"),
            ],
            id="tabs", active_tab="tab-exec", className="mb-3",
        ),
        html.Footer(
            "Built with Dash & Plotly · Data is synthetic, generated for demonstration purposes",
            className="app-footer",
        ),
    ],
    fluid=True,
    className="app-container",
)


def plotly_theme(fig, height=380):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        font=dict(color=COLORS["text"], family="Inter, sans-serif"),
        margin=dict(l=20, r=20, t=50, b=20),
        height=height,
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    return fig


# ---------------------------------------------------------------- callbacks: KPIs
@app.callback(
    Output("kpi-sales", "children"),
    Output("kpi-profit", "children"),
    Output("kpi-margin", "children"),
    Output("kpi-orders", "children"),
    Output("kpi-aov", "children"),
    Output("kpi-achv", "children"),
    Input("f-region", "value"),
    Input("f-category", "value"),
    Input("f-dates", "start_date"),
    Input("f-dates", "end_date"),
)
def update_kpis(regions, categories, start_date, end_date):
    df = filter_orders(orders_raw, regions, categories, (start_date, end_date))
    k = kpi_summary(df, targets_raw)
    return (
        format_inr(k["total_sales"]),
        format_inr(k["total_profit"]),
        f"{k['margin_pct']:.1f}%",
        f"{k['total_orders']:,}",
        format_inr(k["aov"]),
        f"{k['achievement_pct']:.1f}%",
    )


# ---------------------------------------------------------------- callbacks: Tab 1
@app.callback(
    Output("g-sales-vs-target", "figure"),
    Output("g-region-donut", "figure"),
    Output("g-category-bar", "figure"),
    Input("f-region", "value"),
    Input("f-category", "value"),
    Input("f-dates", "start_date"),
    Input("f-dates", "end_date"),
)
def update_exec_summary(regions, categories, start_date, end_date):
    df = filter_orders(orders_raw, regions, categories, (start_date, end_date))

    monthly_sales = df.groupby("Month")["Sales"].sum().reset_index()
    tgt = targets_raw.copy()
    if regions:
        tgt = tgt[tgt["Region"].isin(regions)]
    if categories:
        tgt = tgt[tgt["Category"].isin(categories)]
    monthly_target = tgt.groupby("Month")["TargetSales"].sum().reset_index()

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=monthly_sales["Month"], y=monthly_sales["Sales"],
                           name="Actual Sales", marker_color=COLORS["accent"]))
    fig1.add_trace(go.Scatter(x=monthly_target["Month"], y=monthly_target["TargetSales"],
                               name="Target", mode="lines+markers",
                               line=dict(color=COLORS["accent2"], width=3)))
    fig1.update_layout(title="Monthly Sales vs Target")
    plotly_theme(fig1)

    region_sales = df.groupby("Region")["Sales"].sum().reset_index()
    fig2 = px.pie(region_sales, names="Region", values="Sales", hole=0.55,
                  title="Sales by Region",
                  color_discrete_sequence=px.colors.sequential.Plasma)
    plotly_theme(fig2)

    cat_sales = df.groupby("Category")["Sales"].sum().reset_index().sort_values("Sales")
    fig3 = px.bar(cat_sales, x="Sales", y="Category", orientation="h",
                  title="Sales by Category", color="Sales",
                  color_continuous_scale="Purp")
    plotly_theme(fig3, height=340)

    return fig1, fig2, fig3


# ---------------------------------------------------------------- callbacks: Tab 2
@app.callback(
    Output("g-cat-sales-margin", "figure"),
    Output("g-top-subcat", "figure"),
    Output("g-scatter-sales-margin", "figure"),
    Output("g-treemap", "figure"),
    Input("f-region", "value"),
    Input("f-category", "value"),
    Input("f-dates", "start_date"),
    Input("f-dates", "end_date"),
)
def update_product_analysis(regions, categories, start_date, end_date):
    df = filter_orders(orders_raw, regions, categories, (start_date, end_date))

    cat_summary = df.groupby("Category").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
    cat_summary["MarginPct"] = (cat_summary["Profit"] / cat_summary["Sales"] * 100).round(1)
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=cat_summary["Category"], y=cat_summary["Sales"], name="Sales",
                           marker_color=COLORS["accent"]))
    fig1.add_trace(go.Scatter(x=cat_summary["Category"], y=cat_summary["MarginPct"], name="Margin %",
                               yaxis="y2", mode="lines+markers", line=dict(color=COLORS["accent2"], width=3)))
    fig1.update_layout(
        title="Category-wise Sales & Profit Margin",
        yaxis2=dict(overlaying="y", side="right", title="Margin %"),
    )
    plotly_theme(fig1)

    subcat = df.groupby("SubCategory")["Sales"].sum().reset_index().sort_values("Sales", ascending=False).head(10)
    fig2 = px.bar(subcat, x="Sales", y="SubCategory", orientation="h",
                  title="Top Sub-Categories by Sales", color="Sales",
                  color_continuous_scale="Teal")
    fig2.update_layout(yaxis=dict(categoryorder="total ascending"))
    plotly_theme(fig2)

    sub_scatter = df.groupby("SubCategory").agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("OrderID", "nunique")
    ).reset_index()
    sub_scatter["MarginPct"] = (sub_scatter["Profit"] / sub_scatter["Sales"] * 100).round(1)
    fig3 = px.scatter(sub_scatter, x="Sales", y="MarginPct", size="Orders", color="SubCategory",
                       title="Sales vs Profit Margin (by Sub-Category)",
                       size_max=40)
    plotly_theme(fig3)

    fig4 = px.treemap(df, path=["Category", "SubCategory"], values="Sales",
                       title="Sales Breakdown (Treemap)",
                       color="Sales", color_continuous_scale="Purp")
    plotly_theme(fig4)

    return fig1, fig2, fig3, fig4


# ---------------------------------------------------------------- callbacks: Tab 3
@app.callback(
    Output("g-rep-leaderboard", "figure"),
    Output("g-top10-reps", "figure"),
    Output("g-state-map", "figure"),
    Output("g-quarterly-region", "figure"),
    Input("f-region", "value"),
    Input("f-category", "value"),
    Input("f-dates", "start_date"),
    Input("f-dates", "end_date"),
)
def update_rep_regional(regions, categories, start_date, end_date):
    df = filter_orders(orders_raw, regions, categories, (start_date, end_date))

    rep_summary = df.groupby("SalesRep").agg(
        Sales=("Sales", "sum"), Orders=("OrderID", "nunique")
    ).reset_index().sort_values("Sales", ascending=False)

    fig1 = px.bar(rep_summary, x="Sales", y="SalesRep", orientation="h",
                  title="Sales Rep Leaderboard", color="Sales",
                  color_continuous_scale="Magenta")
    fig1.update_layout(yaxis=dict(categoryorder="total ascending"))
    plotly_theme(fig1)

    top10 = rep_summary.head(10)
    fig2 = px.bar(top10, x="SalesRep", y="Orders", title="Top 10 Sales Reps by Order Count",
                  color="Orders", color_continuous_scale="Sunset")
    plotly_theme(fig2)

    state_summary = df.groupby("State")["Sales"].sum().reset_index()
    fig3 = px.bar(state_summary.sort_values("Sales"), x="Sales", y="State", orientation="h",
                  title="State-wise Sales", color="Sales", color_continuous_scale="Viridis")
    plotly_theme(fig3, height=420)

    df["Quarter"] = df["OrderDate"].dt.to_period("Q").astype(str)
    q_region = df.groupby(["Quarter", "Region"])["Sales"].sum().reset_index()
    fig4 = px.line(q_region, x="Quarter", y="Sales", color="Region", markers=True,
                    title="Quarterly Regional Sales")
    plotly_theme(fig4)

    return fig1, fig2, fig3, fig4


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)
