# -*- coding: utf-8 -*-


"""
MySQL to Python module: bring the MySQL tables back into Python.
Functions only, they are called from main.py.
"""
import os
import pandas as pd

# python name -> MySQL table name
TABLE_NAMES = {
    "orders": "orders",
    "customers": "customers",
    "restaurants": "restaurants",
    "delivery_partners": "delivery_partners",
    "backup": "orders_backup",
    "daily_kpi": "daily_kpi_summary",
    "agg_region": "agg_region_summary",
    "agg_monthly": "agg_monthly_summary",
    "agg_customer_type": "agg_customer_type_summary",
    "agg_partner": "agg_partner_summary",
}


def load_from_mysql(table_name, engine):
    # read one full MySQL table into a dataframe
    df = pd.read_sql("SELECT * FROM " + table_name, engine)
    print("Loaded:", table_name, df.shape)
    return df


def load_all_tables(engine):
    tables = {}

    for name, table in TABLE_NAMES.items():
        df = load_from_mysql(table, engine)
        tables[name] = df

    return tables

def check_row_counts(tables, engine):
    # compare Python rows with MySQL rows
    for name, df in tables.items():
        sql_rows = pd.read_sql("SELECT COUNT(*) AS n FROM " + TABLE_NAMES[name], engine)["n"][0]
        print(TABLE_NAMES[name], "| Python:", len(df), "| MySQL:", sql_rows,
              "| Match:", len(df) == sql_rows)
        
def check_missing(tables):
    # print the missing values of every table
    for name, df in tables.items():
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if len(missing) == 0:
            print(name, ": 0 missing")
        else:
            print(name, ": missing values")
            print(missing)


def fix_missing(tables):
    # partners with no orders have no average, so they are filled with 0
    p = tables["agg_partner"]
    for col in ["Avg_Delivery_Time", "Avg_Rating"]:
        p[col] = p[col].fillna(0)
    return tables


def fix_data_types(tables):
    # dates as dates
    tables["daily_kpi"]["KPI_Date"] = pd.to_datetime(tables["daily_kpi"]["KPI_Date"])
    tables["backup"]["Order_Date"] = pd.to_datetime(tables["backup"]["Order_Date"])
    tables["orders"]["Order_Date"] = pd.to_datetime(tables["orders"]["Order_Date"])
    
    # counts as whole numbers
    r = tables["agg_region"]
    for col in ["Delivered_Orders", "Cancelled_Orders", "Returned_Orders"]:
        r[col] = r[col].astype(int)

    # money and averages as numbers with 2 decimals
    money_cols = ["Delivered_Revenue", "Avg_Order_Value", "Avg_Delivery_Time", "Avg_Rating"]
    for df in tables.values():
        for col in money_cols:
            if col in df.columns:
                df[col] = df[col].astype(float).round(2)
    return tables

def save_to_excel(tables, file_name):

    if not os.path.exists("final_dataset"):
        os.mkdir("final_dataset")

    path = "final_dataset/" + file_name

    writer = pd.ExcelWriter(path, engine="openpyxl")

    for name, df in tables.items():
        df.to_excel(writer, sheet_name=name, index=False)

    writer.close()

    print("Excel saved:", path)