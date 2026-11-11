"""
kpis.py
Step 2: calculate the numbers (KPIs) and summary tables shown on the dashboard.
Revenue always means Final_Amount of Delivered orders (same as the EDA report).
"""
import pandas as pd

import config


def headline_kpis(df, partners_f):
    """Single numbers for the KPI cards. df = filtered orders, partners_f = filtered partners."""
    delivered = df[df["Order_Status"] == "Delivered"]
    total_orders = len(df)
    lost_orders = len(df) - len(delivered)          # cancelled + returned
    n_partners = len(partners_f)

    kpi = {}
    kpi["total_orders"] = total_orders
    kpi["delivered_orders"] = len(delivered)
    kpi["revenue"] = delivered["Final_Amount"].sum()
    kpi["lost_rate"] = lost_orders / total_orders * 100
    kpi["avg_delivery_time"] = df["Delivery_Time_Minutes"].mean()
    kpi["avg_rating"] = df["Order_Rating"].mean()
    kpi["active_partners"] = n_partners
    kpi["orders_per_partner"] = total_orders / n_partners
    kpi["avg_speed"] = partners_f["Avg_Delivery_Speed_KMPH"].mean()
    kpi["avg_efficiency"] = partners_f["Delivery_Efficiency_Score"].mean()
    return kpi


def region_load(df, partners_f):
    """For each region: orders, partners and orders per partner (the workload)."""
    orders_by_region = df.groupby("Region").agg(
        Orders=("Order_ID", "count"),
        Avg_Delivery_Time=("Delivery_Time_Minutes", "mean"),
        Avg_Rating=("Order_Rating", "mean"),
    )
    partners_by_region = partners_f.groupby("Region").agg(
        Partners=("Delivery_Partner_ID", "count"),
        Avg_Speed=("Avg_Delivery_Speed_KMPH", "mean"),
        Avg_Efficiency=("Delivery_Efficiency_Score", "mean"),
    )
    table = orders_by_region.join(partners_by_region, how="inner")
    table["Orders_per_Partner"] = table["Orders"] / table["Partners"]
    return table.reset_index()


def speed_by_region_vehicle(partners_f):
    """Average delivery speed for every region and vehicle type."""
    table = partners_f.groupby(["Region", "Vehicle_Type"])["Avg_Delivery_Speed_KMPH"].mean()
    return table.reset_index()


def partner_table(df, partners_f):
    """One row per partner: profile from the partner table + orders handled from the orders table."""
    from_orders = df.groupby("Delivery_Partner_ID").agg(
        Orders=("Order_ID", "count"),
        Avg_Order_Rating=("Order_Rating", "mean"),
    )
    table = partners_f.merge(from_orders, left_on="Delivery_Partner_ID",
                             right_index=True, how="left")
    table["Orders"] = table["Orders"].fillna(0).astype(int)   # partners with no orders get 0
    return table


def monthly_orders(df):
    """Number of orders in each month (all selected years together)."""
    table = df.groupby("Order_Month").size().reset_index(name="Orders")
    table["Month_Name"] = table["Order_Month"].apply(lambda m: config.MONTH_NAMES[m - 1])
    table["Festive"] = table["Order_Month"].isin(config.FESTIVE_MONTHS)
    return table


def status_mix_by_region(df):
    """Percentage of Delivered / Cancelled / Returned orders in each region."""
    return pd.crosstab(df["Region"], df["Order_Status"], normalize="index") * 100


def restaurant_table(df, restaurants_f):
    """One row per restaurant with its number of orders."""
    from_orders = df.groupby("Restaurant_ID").size().rename("Orders")
    table = restaurants_f.merge(from_orders, left_on="Restaurant_ID",
                                right_index=True, how="left")
    table["Orders"] = table["Orders"].fillna(0).astype(int)
    return table


def prep_time_by_cuisine_region(restaurants_f):
    """Average kitchen preparation time for every region and cuisine."""
    table = restaurants_f.groupby(["City", "Cuisine_Type"])["Avg_Preparation_Time_Minutes"].mean()
    return table.reset_index().rename(columns={"City": "Region"})


def format_money(value):
    """Write a rupee amount in short form, for example 52.06M or 640.5K."""
    if value >= 1_000_000:
        return f"₹{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"₹{value / 1_000:.1f}K"
    return f"₹{value:.0f}"
