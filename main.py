# -*- coding: utf-8 -*-
"""
Single main file of the whole project: Food Delivery Demand Analysis
Data cleaning -> SQL scripts -> MySQL to Python -> EDA -> Statistics -> Regression (4 simple + 2 multiple linear models)
"""


import os
import matplotlib

SHOW_CHARTS = False         # False = only save the charts, do not open them (faster for a full run)
if not SHOW_CHARTS:
    matplotlib.use("Agg")       # must be set before modules are imported

import Data_Cleaning as cleaning
import Mysql_to_Python as mysql_py
import EDA as eda
import Statistics as st
import Regression as reg
from sklearn.model_selection import train_test_split
import importlib

# If the program is run again in the same Spyder / Jupyter console, Python keeps the OLD version
# of the modules in memory. reload() makes sure the latest saved version of every file is used.
for module in [cleaning, mysql_py, eda, st, reg]:
    importlib.reload(module)


#  shared helpers
shared = {}             # the MySQL connection and the Excel data are kept here, so they are made only once


def get_engine():
    # MySQL connection (the password is asked only once)
    if "engine" not in shared:
        password = input("Enter MySQL password: ")
        shared["engine"] = cleaning.connect_to_mysql(password)
    return shared["engine"]


def get_data():
    # orders, customers, restaurants, partners and the merged dataset (from the final Excel file)
    if "data" not in shared:
        orders, customers, restaurants, partners = eda.load_data()
        print("========== MERGED DATASET ==========")
        data = eda.build_merged_dataset(orders, customers, restaurants, partners)
        shared["tables"] = (orders, customers, restaurants, partners)
        shared["data"] = data
    return shared["tables"], shared["data"]


#  1. DATA CLEANING
def run_cleaning():
    # clean the 4 tables one by one
    customers = cleaning.clean_customers()
    restaurants = cleaning.clean_restaurants()
    partners = cleaning.clean_partners()
    orders = cleaning.clean_orders()

    # extra checks
    print("========== EXTRA CHECKS ==========")
    cleaning.check_order_rules(orders)
    print()
    cleaning.check_id_links(orders, customers, restaurants, partners)
    print()
    cleaning.check_date_range(orders, "Order_Date")
    print()
    cleaning.compare_total_orders(customers, orders)
    print()
    print(orders.dtypes)

    # variable types
    print("========== VARIABLE TYPES ==========")
    print("----- Customers -----")
    cleaning.show_variable_types(customers, ["Customer_ID"])
    print("----- Restaurants -----")
    cleaning.show_variable_types(restaurants, ["Restaurant_ID", "Restaurant_Name"])
    print("----- Delivery Partners -----")
    cleaning.show_variable_types(partners, ["Delivery_Partner_ID", "Partner_Name"])
    print("----- Orders -----")
    cleaning.show_variable_types(orders, ["Order_Key", "Order_ID", "Customer_ID", "Restaurant_ID", "Delivery_Partner_ID"])

    # save the cleaned tables
    print("========== SAVING ==========")
    cleaning.save_table(customers, "customers_clean.csv")
    cleaning.save_table(restaurants, "restaurants_clean.csv")
    cleaning.save_table(partners, "delivery_partners_clean.csv")
    cleaning.save_table(orders, "orders_clean.csv")

    # export the cleaned tables to MySQL
    print("========== EXPORT TO MYSQL ==========")
    mysql_engine = get_engine()
    cleaning.drop_old_tables(mysql_engine)      # removes the old tables of the earlier run, so the program can be run again
    cleaning.send_table_to_mysql(customers, "customers", mysql_engine)
    cleaning.send_table_to_mysql(restaurants, "restaurants", mysql_engine)
    cleaning.send_table_to_mysql(partners, "delivery_partners", mysql_engine)
    cleaning.send_table_to_mysql(orders, "orders", mysql_engine)

    mysql_tables = {"customers": customers, "restaurants": restaurants,
                    "delivery_partners": partners, "orders": orders}
    cleaning.check_mysql_row_counts(mysql_tables, mysql_engine)
    print("data cleaning and export finished")


#  2. SQL (the 3 scripts are run from Python)
def run_sql_scripts():
    # the 3 SQL files of the SQL folder are run one by one (same as running them in MySQL Workbench)
    print("========== SQL ==========")
    mysql_engine = get_engine()
    for file_name in ["Keys.sql", "Mysql.sql", "Agg_tab.sql"]:
        print("Running", file_name)
        cleaning.run_sql_file(mysql_engine, os.path.join("SQL", file_name))


#  3. MYSQL TO PYTHON
def run_mysql_to_python():
    mysql_engine = get_engine()

    print("========== LOAD FROM MYSQL ==========")
    tables = mysql_py.load_all_tables(mysql_engine)

    print("========== ROW COUNT CHECK ==========")
    mysql_py.check_row_counts(tables, mysql_engine)

    print("========== MISSING VALUES (BEFORE) ==========")
    mysql_py.check_missing(tables)

    print("========== FIX MISSING AND DATA TYPES ==========")
    tables = mysql_py.fix_missing(tables)
    tables = mysql_py.fix_data_types(tables)

    print("========== MISSING VALUES (AFTER) ==========")
    mysql_py.check_missing(tables)

    print("========== SAVE TO EXCEL ==========")
    mysql_py.save_to_excel(tables, "food_delivery_final.xlsx")


#  4. EDA
def run_eda():
    (orders, customers, restaurants, partners), data = get_data()
    data = data.copy()      # bivariate_part1 adds helper columns, so Statistics and Regression get an untouched copy

    print("========== PART I: UNIVARIATE (NUMERIC) ==========")
    order_cols = ["Order_Value", "Delivery_Fee", "Discount_Applied", "Final_Amount",
                  "Delivery_Time_Minutes", "Order_Rating"]
    eda.summary_stats(orders, order_cols, "Orders")
    for col in order_cols:
        eda.plot_numeric(orders, col, eda.UNI_FOLDER, "uni_orders")

    print("========== PART I: UNIVARIATE (CATEGORICAL) ==========")
    for col in ["Region", "Payment_Mode", "Order_Status", "Festival_Flag"]:
        eda.plot_categorical(orders, col, eda.UNI_FOLDER, "uni_orders")
    for col in ["Customer_Type", "Age_Group", "Gender", "Preferred_Cuisine"]:
        eda.plot_categorical(customers, col, eda.UNI_FOLDER, "uni_customers")
    eda.plot_categorical(restaurants, "Cuisine_Type", eda.UNI_FOLDER, "uni_restaurants")
    eda.plot_categorical(partners, "Vehicle_Type", eda.UNI_FOLDER, "uni_partners")

    print("========== PART I: UNIVARIATE (NUMERIC, OTHER TABLES) ==========")
    customer_cols = ["Total_Orders", "Average_Spend"]
    restaurant_cols = ["Avg_Preparation_Time_Minutes", "Avg_Rating", "Order_Capacity_Per_Day"]
    partner_cols = ["Avg_Delivery_Speed_KMPH", "Successful_Deliveries", "Delayed_Deliveries",
                    "Avg_Customer_Rating", "Delivery_Efficiency_Score"]
    eda.summary_stats(customers, customer_cols, "Customers")
    for col in customer_cols:
        eda.plot_numeric(customers, col, eda.UNI_FOLDER, "uni_customers")
    eda.summary_stats(restaurants, restaurant_cols, "Restaurants")
    for col in restaurant_cols:
        eda.plot_numeric(restaurants, col, eda.UNI_FOLDER, "uni_restaurants")
    eda.summary_stats(partners, partner_cols, "Delivery Partners")
    for col in partner_cols:
        eda.plot_numeric(partners, col, eda.UNI_FOLDER, "uni_partners")

    print("========== PART II: BIVARIATE ==========")
    eda.bivariate_part1(data, partners)
    eda.bivariate_part2(data)
    eda.bivariate_scatter(partners)

    print("========== PART III: MULTIVARIATE (only the heatmap here, rest in Power BI) ==========")
    eda.multivariate_correlation(data)


#  5. STATISTICS
def run_statistics():
    _, data = get_data()

    # ---------------- SAMPLING ----------------
    print("\n===== SAMPLING =====")
    simple = st.simple_random_sample(data, "Order_Value", 500)
    stratified = st.stratified_sample(data, "Order_Value", "Region")
    systematic = st.systematic_sample(data, "Order_Value", 200)

    print("Population mean   :", round(data["Order_Value"].mean(), 2))
    print("Simple sample     : size", len(simple), "mean", round(simple.mean(), 2))
    print("Stratified sample : size", len(stratified), "mean", round(stratified.mean(), 2))
    print("Systematic sample : size", len(systematic), "mean", round(systematic.mean(), 2))

    # ---------------- CENTRAL LIMIT THEOREM ----------------
    print("\n===== CENTRAL LIMIT THEOREM =====")
    st.central_limit_theorem(data, "Discount_Applied")
    st.central_limit_theorem(data, "Order_Value")

    # ---------------- NORMALITY ----------------
    print("\n===== NORMALITY CHECK =====")
    st.check_normality(data, "Order_Value")
    st.check_normality(data, "Delivery_Time_Minutes")
    st.check_normality(data, "Discount_Applied")

    # ---------------- HYPOTHESIS TESTS ----------------
    # Significance level = 0.05 (if p-value < 0.05, reject H0)
    festive = data[data["Festival_Flag"] == 1]
    normal = data[data["Festival_Flag"] == 0]
    metro = data[data["Region"] == "Metropolitan"]
    semi_urban = data[data["Region"] == "Semi-Urban"]

    print("\n===== ONE SAMPLE Z-TEST =====")
    # H0: average delivery time = 35 minutes (company target)
    # H1: average delivery time is not equal to 35 minutes
    st.one_sample_z_test(
        data["Delivery_Time_Minutes"].sample(500, random_state=42), 35, "delivery time (minutes)",
        h0="average delivery time = 35 minutes",
        h1="average delivery time is not equal to 35 minutes")

    print("\n===== TWO SAMPLE Z-TEST =====")
    # H0: Metropolitan and Semi-Urban orders have the same average delivery time
    # H1: Metropolitan and Semi-Urban orders have different average delivery time
    st.two_sample_z_test(
        metro["Delivery_Time_Minutes"].sample(500, random_state=42),
        semi_urban["Delivery_Time_Minutes"].sample(500, random_state=42),
        "Metropolitan", "Semi-Urban", "delivery time (minutes)",
        h0="average delivery time of Metropolitan = average delivery time of Semi-Urban",
        h1="average delivery time of Metropolitan is not equal to Semi-Urban")

    print("\n===== ONE SAMPLE T-TEST =====")
    # H0: average delivery time = 35 minutes (small sample of 30 orders)
    # H1: average delivery time is not equal to 35 minutes
    st.one_sample_t_test(
        data["Delivery_Time_Minutes"].sample(30, random_state=42), 35, "delivery time (minutes)",
        h0="average delivery time = 35 minutes",
        h1="average delivery time is not equal to 35 minutes")

    print("\n===== TWO SAMPLE T-TEST =====")
    # H0: festive and normal orders have the same average final amount
    # H1: festive and normal orders have different average final amount
    st.two_sample_t_test(
        festive["Final_Amount"].sample(40, random_state=42),
        normal["Final_Amount"].sample(40, random_state=42),
        "Festive", "Normal", "final amount (Rs)",
        h0="average final amount of festive orders = average final amount of normal orders",
        h1="average final amount of festive orders is not equal to normal orders")

    print("\n===== PAIRED T-TEST =====")
    # Same 12 months measured in two years, so every month of 2024 is paired with the same month of 2025
    # H0: average monthly delivered revenue of 2024 = average monthly delivered revenue of 2025
    # H1: average monthly delivered revenue of 2024 is not equal to 2025
    delivered = data[data["Order_Status"] == "Delivered"]
    monthly_revenue = delivered.groupby(["Order_Year", "Order_Month"])["Final_Amount"].sum().unstack(0)
    st.paired_t_test(
        monthly_revenue[2024], monthly_revenue[2025], "2024", "2025", "monthly delivered revenue (Rs)",
        h0="monthly delivered revenue of 2024 = monthly delivered revenue of 2025",
        h1="monthly delivered revenue of 2024 is not equal to 2025")


#  6. REGRESSION (2 SIMPLE LINEAR REGRESSION MODELS)
def run_regression():
    (orders, customers, restaurants, partners), data = get_data()

    # Simple linear regression = 1 independent variable (X) and 1 dependent variable (y)
    # Steps for each model: target -> feature selection -> train -> evaluate -> predict -> chart

    # ================= MODEL 1: TARGET = DAILY REVENUE (used for the 2026 forecast) =================
    print("\n===== MODEL 1: DAILY REVENUE =====")
    daily = reg.create_daily_data(data)
    print(daily.head())

    # train = 2023 and 2024, test = 2025 (we predict a year the model has not seen)
    train1 = daily[daily["Order_Year"] < 2025]
    test1 = daily[daily["Order_Year"] == 2025]
    print("\nTrain:", train1.shape, " Test:", test1.shape)

    # feature selection: only variables known in advance, the highest correlation |r| becomes X
    print("\nFeature selection (train data)")
    x1 = reg.select_feature(train1, "Daily_Revenue", reg.DAILY_FEATURES)

    # H0 (null hypothesis)        : X has no effect on Daily_Revenue (slope = 0)
    # H1 (alternative hypothesis) : X has an effect on Daily_Revenue (slope is not 0)
    print("\nModel 1 - coefficients")
    model1 = reg.train_model(train1, x1, "Daily_Revenue")

    print("\nModel 1 - train")
    reg.evaluate_model(model1, train1, x1, "Daily_Revenue")
    print("\nModel 1 - test (unseen 2025 data)")
    reg.evaluate_model(model1, test1, x1, "Daily_Revenue")

    # predict the revenue for a normal day (0) and a festive day (1)
    print("\nModel 1 - predicted revenue for new values of", x1)
    reg.predict_values(model1, x1, "Daily_Revenue", [0, 1])

    reg.plot_regression_line(test1, model1, x1, "Daily_Revenue",
                             "Model 1: " + x1 + " vs Daily Revenue (2025)", "Model1_Regression_Line.png")
    reg.plot_residuals(test1, model1, x1, "Daily_Revenue",
                       "Model 1: Residual Plot", "Model1_Residuals.png")

    # ---------------- 2026 FORECAST ----------------
    # X is known for every day of 2026, so no assumption is needed.
    # The final model learns from all 3 years, then predicts every day of 2026.
    print("\nModel 1 - final model on all 3 years (used for the forecast)")
    final_model = reg.train_model(daily, x1, "Daily_Revenue")

    print("\nModel 1 - 2026 forecast")
    forecast = reg.forecast_2026(final_model, x1, daily)
    festive_months = sorted(daily[daily["Festival_Flag"] == 1]["Month"].unique())
    actual_2025 = daily[daily["Order_Year"] == 2025].groupby("Month")["Daily_Revenue"].sum()
    reg.plot_forecast(forecast, actual_2025, festive_months)

    # ================= MODEL 2: TARGET = AVG CUSTOMER RATING (delivery partners) =================
    print("\n===== MODEL 2: PARTNER RATING =====")
    partner_data = reg.create_partner_data(partners)

    # partner data has no dates, so 80% of the partners are used for training and 20% for testing
    train2, test2 = train_test_split(partner_data, test_size=0.2, random_state=42)
    print("Train:", train2.shape, " Test:", test2.shape)

    print("\nFeature selection (train data)")
    x2 = reg.select_feature(train2, "Avg_Customer_Rating", reg.PARTNER_FEATURES)

    # H0 (null hypothesis)        : X has no effect on Avg_Customer_Rating (slope = 0)
    # H1 (alternative hypothesis) : X has an effect on Avg_Customer_Rating (slope is not 0)
    print("\nModel 2 - coefficients")
    model2 = reg.train_model(train2, x2, "Avg_Customer_Rating")

    print("\nModel 2 - train")
    reg.evaluate_model(model2, train2, x2, "Avg_Customer_Rating")
    print("\nModel 2 - test (unseen 20% partners)")
    reg.evaluate_model(model2, test2, x2, "Avg_Customer_Rating")

    print("\nModel 2 - predicted rating for new values of", x2)
    reg.predict_values(model2, x2, "Avg_Customer_Rating", [15, 22, 30])

    reg.plot_regression_line(test2, model2, x2, "Avg_Customer_Rating",
                             "Model 2: " + x2 + " vs Avg Customer Rating (20% test partners)", "Model2_Regression_Line.png")
    reg.plot_residuals(test2, model2, x2, "Avg_Customer_Rating",
                       "Model 2: Residual Plot", "Model2_Residuals.png")


#  7. REGRESSION: MULTIPLE LINEAR REGRESSION (MODEL 1 AND 2) + 2 MORE SIMPLE MODELS (MODEL 3 AND 4)
def run_regression_multiple():
    (orders, customers, restaurants, partners), data = get_data()

    # Multiple linear regression = 2 or more independent variables (X) and 1 dependent variable (y)
    # The models of step 6 are not changed. Here we try more X variables to see if R2 increases.
    # We compare the models on the TEST data, because R2 on train data always goes up when X is added.

    # ================= MODEL 1 (MULTIPLE): TARGET = DAILY REVENUE =================
    print("\n===== MODEL 1 (MULTIPLE): DAILY REVENUE =====")
    daily = reg.create_daily_data(data)
    daily = reg.add_order_value_column(daily, data)      # Avg_Order_Value of every day
    print(daily.head())

    # same split as step 6: train = 2023 and 2024, test = 2025
    train1 = daily[daily["Order_Year"] < 2025]
    test1 = daily[daily["Order_Year"] == 2025]
    print("\nTrain:", train1.shape, " Test:", test1.shape)

    print("\nModel 1 - R2 of all the models")
    table1 = reg.compare_models(train1, test1, reg.MODEL1_OPTIONS, "Daily_Revenue")
    reg.plot_r2_comparison(table1, "Model 1: R2 of different X variables (2025 test data)", "Model1_R2_Comparison.png")

    # the best model (1C) in detail
    reg.run_model(train1, test1, reg.MODEL1_OPTIONS["1C Festival_Flag + Avg_Order_Value"],
                  "Daily_Revenue", "Model 1C", "unseen 2025 data")

    # ================= MODEL 2 (MULTIPLE): TARGET = AVG CUSTOMER RATING =================
    print("\n===== MODEL 2 (MULTIPLE): PARTNER RATING =====")
    partner_data = reg.create_partner_data(partners)
    partner_data = reg.add_delay_rate(partner_data)      # Delay_Rate = delayed / (delayed + successful)
    print(partner_data.head())

    # same split as step 6: 80% of the partners for training and 20% for testing
    train2, test2 = train_test_split(partner_data, test_size=0.2, random_state=42)
    print("\nTrain:", train2.shape, " Test:", test2.shape)

    print("\nModel 2 - R2 of all the models")
    table2 = reg.compare_models(train2, test2, reg.MODEL2_OPTIONS, "Avg_Customer_Rating")
    reg.plot_r2_comparison(table2, "Model 2: R2 of different X variables (20% test partners)", "Model2_R2_Comparison.png")

    # the best model (2C) in detail
    reg.run_model(train2, test2, reg.MODEL2_OPTIONS["2C Speed + Delay_Rate"],
                  "Avg_Customer_Rating", "Model 2C", "unseen 20% partners")

    # ================= MODEL 3 (SIMPLE): TARGET = AVG ORDER VALUE OF THE DAY =================
    print("\n===== MODEL 3: AVG ORDER VALUE =====")
    # same data and same split as Model 1 (daily data with Avg_Order_Value)
    print("\nFeature selection (train data)")
    x3 = reg.select_feature(train1, "Avg_Order_Value", reg.MODEL3_FEATURES)

    print("\nAverage order value of normal and festive days")
    reg.show_group_average(daily, "Festival_Flag", "Avg_Order_Value")

    model3 = reg.run_model(train1, test1, x3, "Avg_Order_Value", "Model 3", "unseen 2025 data")

    print("\nModel 3 - predicted order value for new values of", x3)
    reg.predict_values(model3, x3, "Avg_Order_Value", [0, 1])

    reg.plot_regression_line(test1, model3, x3, "Avg_Order_Value",
                             "Model 3: " + x3 + " vs Avg Order Value (2025)", "Model3_Regression_Line.png")
    reg.plot_residuals(test1, model3, x3, "Avg_Order_Value",
                       "Model 3: Residual Plot", "Model3_Residuals.png")

    # ================= MODEL 4 (SIMPLE): TARGET = DELAYED DELIVERIES OF A PARTNER =================
    print("\n===== MODEL 4: DELAYED DELIVERIES =====")
    # same partner data and same split as Model 2
    print("\nFeature selection (train data)")
    x4 = reg.select_feature(train2, "Delayed_Deliveries", reg.MODEL4_FEATURES)

    model4 = reg.run_model(train2, test2, x4, "Delayed_Deliveries", "Model 4", "unseen 20% partners")

    print("\nModel 4 - predicted delayed deliveries for new values of", x4)
    reg.predict_values(model4, x4, "Delayed_Deliveries", [10, 25, 40])

    reg.plot_regression_line(test2, model4, x4, "Delayed_Deliveries",
                             "Model 4: " + x4 + " vs Delayed Deliveries (20% test partners)", "Model4_Regression_Line.png")
    reg.plot_residuals(test2, model4, x4, "Delayed_Deliveries",
                       "Model 4: Residual Plot", "Model4_Residuals.png")


#  MAIN

def show_title(text):
    print("\n" + "#" * 70)
    print("#", text)
    print("#" * 70)


def main():
    print("Food Delivery Demand Analysis: what do you want to run?")
    print("   1 = Data cleaning + export to MySQL")
    print("   2 = SQL scripts (keys, procedures, triggers, agg_ tables)")
    print("   3 = MySQL to Python + final Excel file")
    print("   4 = EDA (univariate and bivariate charts)")
    print("   5 = Statistics: sampling, CLT, normality, hypothesis tests")
    print("   6 = Regression: 2 simple linear regression models")
    print("   7 = Regression: multiple linear regression + 2 more models")
    choice = input("Type the step numbers with a space (example: 4 5 6), or press Enter to run all: ")

    if choice.strip() == "":
        choice = "1 2 3 4 5 6 7"
    steps = choice.split()          # for example "4 5 6" becomes ["4", "5", "6"]

    if "1" in steps:
        show_title("1 - Data cleaning + export to MySQL")
        run_cleaning()
    if "2" in steps:
        show_title("2 - SQL scripts (keys, procedures, triggers, agg_ tables)")
        run_sql_scripts()
    if "3" in steps:
        show_title("3 - MySQL to Python + final Excel file")
        run_mysql_to_python()
    if "4" in steps:
        show_title("4 - EDA (univariate and bivariate charts)")
        run_eda()
    if "5" in steps:
        show_title("5 - Statistics: sampling, CLT, normality, hypothesis tests")
        run_statistics()
    if "6" in steps:
        show_title("6 - Regression: 2 simple linear regression models")
        run_regression()
    if "7" in steps:
        show_title("7 - Regression: multiple linear regression + 2 more models")
        run_regression_multiple()

    print("\nAll selected steps finished.")


if __name__ == "__main__":
    main()