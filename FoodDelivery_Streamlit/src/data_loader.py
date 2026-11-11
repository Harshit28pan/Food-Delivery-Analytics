"""
data_loader.py
Step 1 of the project: read the CSV files, join the tables and apply the sidebar filters.
"""
import os
import pandas as pd

import config


def load_tables():
    """Read the 4 cleaned CSV files (made in the Data_Cleaning step) and return them in a dictionary."""
    tables = {}
    for name, file_name in config.FILES.items():
        path = os.path.join(config.DATA_DIR, file_name)
        tables[name] = pd.read_csv(path)

    # the date column is read as text, so convert it to a real date
    tables["orders"]["Order_Date"] = pd.to_datetime(tables["orders"]["Order_Date"])
    return tables


def build_merged(tables):
    """
    Join the tables (same idea as EDA.py).
    Orders is the main table. Customers, restaurants and partners are joined to it
    using their ID columns (many orders belong to one customer / restaurant / partner).
    """
    orders = tables["orders"]
    customers = tables["customers"][["Customer_ID", "Customer_Type", "Age_Group"]]
    restaurants = tables["restaurants"][["Restaurant_ID", "Cuisine_Type"]]
    partners = tables["partners"][["Delivery_Partner_ID", "Vehicle_Type"]]

    data = orders.merge(customers, on="Customer_ID", how="left")
    data = data.merge(restaurants, on="Restaurant_ID", how="left")
    data = data.merge(partners, on="Delivery_Partner_ID", how="left")

    # extra columns for month and year analysis
    data["Order_Year"] = data["Order_Date"].dt.year
    data["Order_Month"] = data["Order_Date"].dt.month
    return data


def apply_filters(data, years, regions, vehicles):
    """Keep only the rows that match the years, regions and vehicles chosen in the sidebar."""
    data = data[data["Order_Year"].isin(years)]
    data = data[data["Region"].isin(regions)]
    data = data[data["Vehicle_Type"].isin(vehicles)]
    return data


def filter_partners(partners, regions, vehicles):
    """Same region and vehicle filter, but for the delivery partner table."""
    partners = partners[partners["Region"].isin(regions)]
    partners = partners[partners["Vehicle_Type"].isin(vehicles)]
    return partners
