"""
Generates a synthetic Orders / Targets / Customers dataset for the
Sales & Revenue Analytics Dashboard project.

This is original synthetic data (not copied from anywhere) shaped to
match the structure described in the source project: ~3,000 orders,
~720 target rows, ~2,100 customers, spanning 2022-2024.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

REGIONS = ["North", "South", "East", "West", "Central"]
STATES_BY_REGION = {
    "North": ["Delhi", "Punjab", "Haryana", "Uttar Pradesh"],
    "South": ["Karnataka", "Tamil Nadu", "Kerala", "Andhra Pradesh"],
    "East": ["West Bengal", "Odisha", "Bihar", "Jharkhand"],
    "West": ["Maharashtra", "Gujarat", "Rajasthan", "Goa"],
    "Central": ["Madhya Pradesh", "Chhattisgarh"],
}
CATEGORIES = {
    "Electronics": ["Smartphones", "Laptops", "Accessories", "Tablets"],
    "Furniture": ["Chairs", "Tables", "Storage", "Sofas"],
    "Office Supplies": ["Paper", "Binders", "Pens & Stationery", "Printers"],
    "Clothing": ["Menswear", "Womenswear", "Footwear", "Kidswear"],
}
SEGMENTS = ["Consumer", "Corporate", "Small Business"]
SALES_REPS = [
    "Aarav Shah", "Priya Mehta", "Rohan Iyer", "Sneha Kulkarni", "Vikram Nair",
    "Ananya Rao", "Karan Malhotra", "Isha Deshpande", "Arjun Bhatt", "Neha Kapoor",
    "Siddharth Joshi", "Divya Menon",
]

START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2024, 12, 31)


def random_dates(n):
    delta_days = (END_DATE - START_DATE).days
    offsets = np.random.randint(0, delta_days, size=n)
    return [START_DATE + timedelta(days=int(o)) for o in offsets]


def generate_customers(n=2100):
    ids = [f"CUST-{i:05d}" for i in range(1, n + 1)]
    first_names = ["Aditya", "Meera", "Rahul", "Kavya", "Aman", "Riya", "Yash",
                   "Simran", "Dev", "Pooja", "Aryan", "Tanvi", "Ravi", "Ishita"]
    last_names = ["Sharma", "Verma", "Reddy", "Patel", "Gupta", "Singh", "Nair",
                  "Iyer", "Chopra", "Bose", "Kulkarni", "Pillai"]
    names = [f"{np.random.choice(first_names)} {np.random.choice(last_names)}" for _ in range(n)]
    regions = np.random.choice(REGIONS, size=n)
    segments = np.random.choice(SEGMENTS, size=n, p=[0.55, 0.30, 0.15])
    join_dates = random_dates(n)
    return pd.DataFrame({
        "CustomerID": ids,
        "CustomerName": names,
        "Segment": segments,
        "Region": regions,
        "JoinDate": join_dates,
    })


def generate_orders(customers_df, n=3000):
    order_ids = [f"ORD-{i:05d}" for i in range(1, n + 1)]
    dates = random_dates(n)
    regions = np.random.choice(REGIONS, size=n)
    states = [np.random.choice(STATES_BY_REGION[r]) for r in regions]
    categories = np.random.choice(list(CATEGORIES.keys()), size=n, p=[0.35, 0.2, 0.25, 0.2])
    sub_categories = [np.random.choice(CATEGORIES[c]) for c in categories]
    sales_reps = np.random.choice(SALES_REPS, size=n)
    customer_ids = np.random.choice(customers_df["CustomerID"], size=n)
    quantities = np.random.randint(1, 12, size=n)

    # unit price varies by category to keep things realistic
    base_price = {
        "Electronics": (8000, 45000),
        "Furniture": (2500, 20000),
        "Office Supplies": (100, 3000),
        "Clothing": (500, 4500),
    }
    unit_prices = np.array([
        np.random.uniform(*base_price[c]) for c in categories
    ]).round(2)

    sales = (quantities * unit_prices).round(2)
    # margin varies by category, with noise
    base_margin = {
        "Electronics": 0.14, "Furniture": 0.22,
        "Office Supplies": 0.28, "Clothing": 0.35,
    }
    margins = np.array([
        np.clip(np.random.normal(base_margin[c], 0.06), -0.05, 0.55) for c in categories
    ])
    profit = (sales * margins).round(2)

    df = pd.DataFrame({
        "OrderID": order_ids,
        "OrderDate": dates,
        "Region": regions,
        "State": states,
        "Category": categories,
        "SubCategory": sub_categories,
        "SalesRep": sales_reps,
        "CustomerID": customer_ids,
        "Quantity": quantities,
        "UnitPrice": unit_prices,
        "Sales": sales,
        "Profit": profit,
    })
    return df.sort_values("OrderDate").reset_index(drop=True)


def generate_targets(orders_df, n=720):
    # Monthly targets by Region x Category, derived from actual sales +/- noise,
    # so "Achievement %" looks realistic rather than random.
    orders_df = orders_df.copy()
    orders_df["Month"] = orders_df["OrderDate"].values.astype("datetime64[M]")
    monthly_actual = (
        orders_df.groupby(["Month", "Region", "Category"])["Sales"]
        .sum()
        .reset_index()
    )
    monthly_actual["TargetSales"] = (
        monthly_actual["Sales"] * np.random.uniform(0.85, 1.15, size=len(monthly_actual))
    ).round(2)
    targets = monthly_actual[["Month", "Region", "Category", "TargetSales"]]

    # pad/trim to ~720 rows to match original row count
    if len(targets) > n:
        targets = targets.sample(n, random_state=42)
    elif len(targets) < n:
        extra = targets.sample(n - len(targets), replace=True, random_state=1).copy()
        extra["TargetSales"] = (extra["TargetSales"] * np.random.uniform(0.9, 1.1, size=len(extra))).round(2)
        targets = pd.concat([targets, extra], ignore_index=True)

    return targets.reset_index(drop=True)


if __name__ == "__main__":
    customers = generate_customers()
    orders = generate_orders(customers)
    targets = generate_targets(orders)

    customers.to_csv("customers.csv", index=False)
    orders.to_csv("orders.csv", index=False)
    targets.to_csv("targets.csv", index=False)

    with pd.ExcelWriter("Sales_Dashboard_Dataset.xlsx", engine="openpyxl") as writer:
        orders.to_excel(writer, sheet_name="Orders", index=False)
        targets.to_excel(writer, sheet_name="Targets", index=False)
        customers.to_excel(writer, sheet_name="Customers", index=False)

    print(f"Orders: {len(orders)} rows")
    print(f"Targets: {len(targets)} rows")
    print(f"Customers: {len(customers)} rows")
