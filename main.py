# -*- coding: utf-8 -*-
"""
Single main file of the whole project: Food Delivery Demand Analysis
Data cleaning -> SQL (MySQL Workbench) -> MySQL to Python -> EDA -> Statistics -> Regression and forecast
"""


import matplotlib

SHOW_CHARTS = False         # False = only save the charts, do not open them (faster for a full run)
if not SHOW_CHARTS:
    matplotlib.use("Agg")       # must be set before the day modules are imported

import Data_Cleaning as cleaning
import Mysql_to_Python as mysql_py
import EDA as eda
import Statistics as st
import Regression as reg


# ---------------------------------------------------------------- shared helpers
engine = None           # MySQL connection (the password is asked only once)
shared = {}             # the Excel data is loaded only once and reused by EDA, Statistics and Regression


def get_engine():
    global engine
    if engine is None:
        password = input("Enter MySQL password: ")
        engine = cleaning.connect_to_mysql(password)
    return engine


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
    cleaning.send_table_to_mysql(customers, "customers", mysql_engine)
    cleaning.send_table_to_mysql(restaurants, "restaurants", mysql_engine)
    cleaning.send_table_to_mysql(partners, "delivery_partners", mysql_engine)
    cleaning.send_table_to_mysql(orders, "orders", mysql_engine)

    mysql_tables = {"customers": customers, "restaurants": restaurants,
                    "delivery_partners": partners, "orders": orders}
    cleaning.check_mysql_row_counts(mysql_tables, mysql_engine)
    print("data cleaning and export finished")


#  2. SQL (run in MySQL Workbench)
def pause_for_sql():
    print("========== SQL ==========")
    print("This step is done in MySQL Workbench, not in Python.")
    print("Run the 3 scripts of the SQL folder (Keys.sql, Mysql.sql, Agg_tab.sql)")
    print("so that the keys, the backup and the agg_ tables exist before step 3 (MySQL to Python).")
    input("Press Enter when the SQL scripts are finished...")


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


#  6. REGRESSION AND FORECAST
def run_regression():
    _, data = get_data()

    # ---------------- DAILY DATA ----------------
    print("\n===== DAILY DATA =====")
    daily = reg.create_daily_data(data)
    print(daily.head())

    # ---------------- TRAIN TEST SPLIT ----------------
    # train = 2023 and 2024, test = 2025 (we predict a year the model has not seen)
    train = daily[daily["Order_Year"] < 2025]
    test = daily[daily["Order_Year"] == 2025]
    print("\nTrain:", train.shape, " Test:", test.shape)

    # ---------------- MODEL 1: CORRELATION BASED FEATURES ----------------
    # H0 (null hypothesis)        : Festival_Flag and Month have no effect on Daily_Revenue (their coefficients are 0)
    # H1 (alternative hypothesis) : at least one of them has an effect on Daily_Revenue (a coefficient is not 0)
    print("\n===== MODEL 1 =====")
    features1 = reg.select_features(train)
    model1 = reg.train_model(train, features1)

    print("\nModel 1 - train")
    reg.evaluate_model(model1, train, features1)
    print("\nModel 1 - test")
    actual1, predicted1 = reg.evaluate_model(model1, test, features1)

    reg.plot_actual_predicted(actual1, predicted1, "Model1_Actual_vs_Predicted.png")
    reg.plot_residuals(actual1, predicted1, "Model1_Residuals.png")

    # ---------------- MODEL 2: MONTH BASED ----------------
    # H0 (null hypothesis)        : the month of the year has no effect on Daily_Revenue (all 11 month coefficients are 0)
    # H1 (alternative hypothesis) : at least one month has an effect on Daily_Revenue (a month coefficient is not 0)
    print("\n===== MODEL 2 =====")
    # add the 0/1 month columns (Month_2 ... Month_12) to the daily data
    month_columns = reg.create_month_columns(daily)
    month_features = month_columns.columns.tolist()

    daily = daily.join(month_columns)
    train = daily[daily["Order_Year"] < 2025]
    test = daily[daily["Order_Year"] == 2025]

    model2 = reg.train_model(train, month_features)

    print("\nModel 2 - train")
    reg.evaluate_model(model2, train, month_features)
    print("\nModel 2 - test")
    actual2, predicted2 = reg.evaluate_model(model2, test, month_features)

    reg.plot_actual_predicted(actual2, predicted2, "Model2_Actual_vs_Predicted.png")
    reg.plot_residuals(actual2, predicted2, "Model2_Residuals.png")

    # ---------------- FORECAST 2026 ----------------
    # H0 (null hypothesis)        : daily revenue does not change from month to month, so the 2026 forecast is the same every month
    # H1 (alternative hypothesis) : daily revenue changes with the month, so the 2026 forecast is different in different months
    print("\n===== FORECAST 2026 =====")
    forecast_model, monthly_forecast = reg.forecast_next_year(daily, month_features)
    reg.plot_forecast(monthly_forecast)

    print("\n===== MONTH IMPACT =====")
    reg.show_month_impact(forecast_model, month_features)


#  MAIN

def main():
    steps = {1: ("Data cleaning + export to MySQL", run_cleaning),
             2: ("SQL scripts (done in MySQL Workbench)", pause_for_sql),
             3: ("MySQL to Python + final Excel file", run_mysql_to_python),
             4: ("EDA (univariate and bivariate charts)", run_eda),
             5: ("Statistics: sampling, CLT, normality, hypothesis tests", run_statistics),
             6: ("Regression and 2026 forecast", run_regression)}

    print("Food Delivery Demand Analysis: what do you want to run?")
    for number, (title, _) in steps.items():
        print("  ", number, "=", title)
    choice = input("Type the step numbers with a space (example: 4 5 6), or press Enter to run all: ").strip()

    if choice == "":
        selected = list(steps.keys())
    else:
        selected = sorted({int(x) for x in choice.split() if x.isdigit() and int(x) in steps})

    for number in selected:
        print("\n" + "#" * 70)
        print("#", number, "-", steps[number][0])
        print("#" * 70)
        steps[number][1]()

    print("\nAll selected steps finished.")


if __name__ == "__main__":
    main()
