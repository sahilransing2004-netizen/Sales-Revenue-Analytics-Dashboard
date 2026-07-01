"""Data loading and KPI calculation helpers for the dashboard."""
import pandas as pd
import numpy as np
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_data():
    orders = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"), parse_dates=["OrderDate"])
    targets = pd.read_csv(os.path.join(DATA_DIR, "targets.csv"), parse_dates=["Month"])
    customers = pd.read_csv(os.path.join(DATA_DIR, "customers.csv"), parse_dates=["JoinDate"])

    orders["Month"] = orders["OrderDate"].values.astype("datetime64[M]")
    orders["Year"] = orders["OrderDate"].dt.year
    orders["Quarter"] = orders["OrderDate"].dt.to_period("Q").astype(str)
    orders["MarginPct"] = (orders["Profit"] / orders["Sales"] * 100).round(2)
    return orders, targets, customers


def filter_orders(orders, regions=None, categories=None, date_range=None):
    df = orders.copy()
    if regions:
        df = df[df["Region"].isin(regions)]
    if categories:
        df = df[df["Category"].isin(categories)]
    if date_range and date_range[0] and date_range[1]:
        df = df[(df["OrderDate"] >= date_range[0]) & (df["OrderDate"] <= date_range[1])]
    return df


def kpi_summary(orders, targets):
    total_sales = orders["Sales"].sum()
    total_profit = orders["Profit"].sum()
    margin_pct = (total_profit / total_sales * 100) if total_sales else 0
    total_orders = orders["OrderID"].nunique()
    aov = total_sales / total_orders if total_orders else 0

    # Achievement % = actual sales vs target sales for the same filtered scope
    relevant_targets = targets[
        targets["Region"].isin(orders["Region"].unique()) &
        targets["Category"].isin(orders["Category"].unique())
    ] if len(orders) else targets
    target_sum = relevant_targets["TargetSales"].sum()
    achievement_pct = (total_sales / target_sum * 100) if target_sum else 0

    return {
        "total_sales": total_sales,
        "total_profit": total_profit,
        "margin_pct": margin_pct,
        "total_orders": total_orders,
        "aov": aov,
        "achievement_pct": achievement_pct,
    }


def mom_yoy_growth(orders):
    monthly = orders.groupby("Month")["Sales"].sum().reset_index().sort_values("Month")
    monthly["MoM_Growth"] = monthly["Sales"].pct_change() * 100
    monthly["YoY_Growth"] = monthly["Sales"].pct_change(periods=12) * 100
    return monthly


def format_inr(value):
    """Format a number in compact Indian-currency style, e.g. 12.4L, 3.2Cr."""
    if value is None or np.isnan(value):
        return "₹0"
    abs_val = abs(value)
    if abs_val >= 1e7:
        return f"₹{value / 1e7:.2f} Cr"
    elif abs_val >= 1e5:
        return f"₹{value / 1e5:.2f} L"
    elif abs_val >= 1e3:
        return f"₹{value / 1e3:.1f} K"
    return f"₹{value:.0f}"
