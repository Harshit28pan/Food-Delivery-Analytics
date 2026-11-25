"""
Data cleaning module: Data Acquisition and Initial Understanding (data cleaning)
Project: Food Delivery Demand Analysis

This module only defines the functions (cleaning, checks, saving and export to MySQL).
The functions are called from main.py.

@author: Harshit
"""

# import the libraries and set the folder names
import os
import pandas as pd
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text

pd.set_option("display.max_columns", 50)    # show all columns when a table is printed
pd.set_option("display.width", 200)

DATA_FOLDER = "dataset"                # folder with the 4 Excel files
OUTPUT_FOLDER = "cleaned_dataset"      # cleaned files will be saved here

# MySQL settings (the password is typed when the program runs)
MYSQL_USER = "root"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DATABASE = "food_delivery"      # database that will hold the 4 cleaned tables
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# the only characters allowed in text columns, everything else is removed
ALLOWED_CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 _.+-"


# functions to load a table and look at it
def load_table(file_name):
    # read one Excel file from the data folder
    return pd.read_excel(os.path.join(DATA_FOLDER, file_name))


def audit_table(df, id_column=None):
    # print size, data types, missing values and duplicate rows of a table
    print("Rows and columns:", df.shape)
    df.info()
    print("Missing values:", df.isnull().sum().sum())
    print("Duplicate rows:", df.duplicated().sum())
    if id_column is not None:
        print("Repeated", id_column, ":", df[id_column].duplicated().sum())


def show_values(df, columns):
    # print every value of the given columns with its count
    for col in columns:
        print(df[col].value_counts())
        print()


def get_text_columns(df):
    return list(df.select_dtypes(include = 'object').columns)


# remove duplicates, fix spelling, same style for IDs
def remove_duplicates(df):
    # remove rows that are completely the same
    before = len(df)
    df = df.drop_duplicates()
    print("Duplicate rows removed:", before - len(df))
    return df


def fix_spelling(df, column, wrong_value, correct_value):
    # replace a wrong spelling with the correct one
    print("Rows changed in", column, ":", (df[column] == wrong_value).sum())
    df[column] = df[column].replace(wrong_value, correct_value)
    return df


def make_ids_uppercase(df, id_columns):
    # write the IDs in capital letters
    for col in id_columns:
        df[col] = df[col].str.upper()
    return df


# remove extra spaces and special characters from text columns
def clean_one_value(value):
    # remove spaces at the start and end, then keep only the allowed characters
    new_text = ""
    for character in value.strip():
        if character in ALLOWED_CHARACTERS:
            new_text = new_text + character
    return new_text


def clean_text(df):
    # clean every text column of the table
    changed = 0
    for col in get_text_columns(df):
        original = df[col].copy()
        df[col] = df[col].apply(clean_one_value)
        changed = changed + (original != df[col]).sum()
    print("Values changed while cleaning text:", changed)
    return df


# wrong values, missing values, decimals and unique key
def cap_at_maximum(df, column, max_value):
    # values above the allowed maximum are set to the maximum
    print("Rows above", max_value, "in", column, ":", (df[column] > max_value).sum())
    df.loc[df[column] > max_value, column] = max_value
    return df


def fill_missing_median(df, column, group_column):

    print("Missing values before:", df[column].isnull().sum())

    # Calculate median for each group
    medians = df.groupby(group_column)[column].median()

    # Fill missing values group by group
    for group in medians.index:
        df.loc[
            (df[group_column] == group) & (df[column].isnull()),
            column
        ] = medians[group]

    print("Missing values after:", df[column].isnull().sum())
    return df


def round_columns(df, decimals_by_column):
    # round columns, example: {"Avg_Rating": 2}
    for col, decimals in decimals_by_column.items():
        df[col] = df[col].round(decimals)
    return df


def add_order_key(df):
    # Order_ID is repeated for different orders, so give every row a unique number
    if "Order_Key" in df.columns:
        print("Order_Key already exists, nothing to do")
        return df
    df.insert(0, "Order_Key", list(range(1, len(df) + 1)))
    print("Order_Key is unique:", df["Order_Key"].is_unique)
    return df


# find outliers with the IQR method and cap them (winsorization)
def find_outliers_iqr(df, columns):
    # outlier = value below Q1 - 1.5*IQR or above Q3 + 1.5*IQR
    rows = []
    for col in columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        count = ((df[col] < lower) | (df[col] > upper)).sum()
        rows.append({"Column": col, "Min": df[col].min(), "Max": df[col].max(),
                     "Q1": q1, "Q3": q3, "Lower fence": round(lower, 2), "Upper fence": round(upper, 2),
                     "Outliers": count, "Outlier %": round(count / len(df) * 100, 2)})
    return pd.DataFrame(rows)


def winsorize_iqr(df, column):
    # values above the upper fence become the upper fence, values below the lower fence become the lower fence
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower = int(q1 - 1.5 * iqr)         # int() removes the decimals (these are whole-number columns)
    upper = int(q3 + 1.5 * iqr)

    new_column = column + "_wins"       # the original column is kept as it is
    df[new_column] = df[column]
    df.loc[df[column] > upper, new_column] = upper
    df.loc[df[column] < lower, new_column] = lower

    print(column, "| lower limit:", lower, "| upper limit:", upper)
    print("Max before:", df[column].max(), "| Max after:", df[new_column].max())
    print("Rows changed:", (df[column] != df[new_column]).sum())
    return df


# group the columns into numerical, categorical, boolean and date/time
def show_variable_types(df, id_columns):
    numerical = []
    categorical = []
    boolean = []
    date_time = []
    for col in df.columns:
        if col not in id_columns:
            data_type = str(df[col].dtype)
            if data_type == "bool":
                boolean.append(col)
            elif data_type.startswith("datetime"):
                date_time.append(col)
            elif data_type.startswith("int") or data_type.startswith("float"):
                numerical.append(col)
            else:
                categorical.append(col)
    print("Identifier :", id_columns)
    print("Numerical  :", numerical)
    print("Categorical:", categorical)
    print("Boolean    :", boolean)
    print("Date/Time  :", date_time)


# extra checks to make sure the cleaned data is correct
def check_order_rules(orders):
    # business rules every order must follow (all numbers should be 0)
    for col in ["Order_Value", "Delivery_Fee", "Discount_Applied", "Final_Amount"]:
        print("Negative values in", col, ":", (orders[col] < 0).sum())
    print("Rating outside 1 to 5:", ((orders["Order_Rating"] < 1) | (orders["Order_Rating"] > 5)).sum())
    print("Discount more than Order_Value:", (orders["Discount_Applied"] > orders["Order_Value"]).sum())
    calculated = orders["Order_Value"] - orders["Discount_Applied"] + orders["Delivery_Fee"]
    print("Rows where Final_Amount is wrong:", (calculated != orders["Final_Amount"]).sum())


def check_id_links(orders, customers, restaurants, partners):
    # every ID in Orders must be present in the other tables (all numbers should be 0)
    customer_found = orders["Customer_ID"].isin(customers["Customer_ID"])
    restaurant_found = orders["Restaurant_ID"].isin(restaurants["Restaurant_ID"])
    partner_found = orders["Delivery_Partner_ID"].isin(partners["Delivery_Partner_ID"])
    print("Customer_ID not found:", (customer_found == False).sum())
    print("Restaurant_ID not found:", (restaurant_found == False).sum())
    print("Delivery_Partner_ID not found:", (partner_found == False).sum())


def check_date_range(df, date_column):
    # first date, last date and whether any month is missing in between
    first_date = df[date_column].min()
    last_date = df[date_column].max()
    months_found = df[date_column].dt.strftime("%Y-%m").nunique()
    months_expected = (last_date.year - first_date.year) * 12 + (last_date.month - first_date.month) + 1
    print("First date:", first_date.date(), "| Last date:", last_date.date())
    print("Months found:", months_found, "| Months expected:", months_expected)


def compare_total_orders(customers, orders):
    # Total_Orders in Customers should match the real number of orders in the Orders table
    real_orders = orders.groupby("Customer_ID").size()               # orders of every customer
    real_for_each_customer = customers["Customer_ID"].map(real_orders).fillna(0)
    mismatch = (customers["Total_Orders"] != real_for_each_customer).sum()
    print("Customers whose Total_Orders does not match the Orders table:", mismatch)


# save a cleaned table as a CSV file
def save_table(df, file_name):
    df.to_csv(os.path.join(OUTPUT_FOLDER, file_name), index=False, date_format="%Y-%m-%d")
    print("Saved:", file_name, df.shape)


# export the cleaned tables from Python to MySQL

def connect_to_mysql(password):

    safe_password = quote_plus(password)

    server_url = f"mysql+pymysql://{MYSQL_USER}:{safe_password}@{MYSQL_HOST}:{MYSQL_PORT}"

    server_engine = create_engine(server_url)

    with server_engine.connect() as connection:
        connection.execute(text("CREATE DATABASE IF NOT EXISTS " + MYSQL_DATABASE))

    engine = create_engine(server_url + "/" + MYSQL_DATABASE)

    print("Connected to database:", MYSQL_DATABASE)

    return engine



def drop_old_tables(engine):
    # Remove everything left from an earlier run (tables, procedures, events), so the program
    # can be run again and again on the same MySQL without errors.
    # Foreign key checks are switched off while dropping, so the order of dropping does not matter.
    # Keys, triggers and procedures are created again by the SQL scripts (step 2).
    with engine.begin() as connection:
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

        tables = connection.execute(text("SHOW TABLES")).fetchall()
        for row in tables:
            connection.execute(text("DROP TABLE IF EXISTS `" + row[0] + "`"))

        procedures = connection.execute(
            text("SELECT ROUTINE_NAME FROM information_schema.ROUTINES "
                 "WHERE ROUTINE_SCHEMA = :db AND ROUTINE_TYPE = 'PROCEDURE'"),
            {"db": MYSQL_DATABASE}).fetchall()
        for row in procedures:
            connection.execute(text("DROP PROCEDURE IF EXISTS `" + row[0] + "`"))

        events = connection.execute(
            text("SELECT EVENT_NAME FROM information_schema.EVENTS WHERE EVENT_SCHEMA = :db"),
            {"db": MYSQL_DATABASE}).fetchall()
        for row in events:
            connection.execute(text("DROP EVENT IF EXISTS `" + row[0] + "`"))

        connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    print("Old tables, procedures and events removed")


def split_sql(script):
    # Cut a SQL script into single statements.
    # It understands the DELIMITER lines (used for procedures and triggers), because
    # a procedure has ; inside its body and must be sent to MySQL as one statement.
    statements = []
    delimiter = ";"
    current = ""

    for line in script.splitlines():
        stripped = line.strip()

        if stripped.upper().startswith("DELIMITER"):
            delimiter = stripped[9:].strip()
            if delimiter == "":
                delimiter = ";"
            continue

        if stripped.startswith("--") and current.strip() == "":
            continue                        # comment line between two statements

        current = current + line + "\n"

        if stripped.endswith(delimiter):
            statement = current.strip()
            statement = statement[:-len(delimiter)].strip()
            if statement != "":
                statements.append(statement)
            current = ""

    if current.strip() != "":
        statements.append(current.strip())
    return statements


def run_sql_file(engine, file_path):
    # Run one .sql file from Python (same as running it in MySQL Workbench).
    # One connection is used for the whole file, so START TRANSACTION ... ROLLBACK works.
    with open(file_path, encoding="utf-8") as file:
        statements = split_sql(file.read())

    connection = engine.raw_connection()
    cursor = connection.cursor()
    failed = 0

    for statement in statements:
        try:
            cursor.execute(statement)
            cursor.fetchall()               # read the result of SELECT / CALL and ignore it
            while cursor.nextset():         # a procedure can return more than one result
                pass
        except Exception as error:
            failed = failed + 1
            print("   Skipped:", statement.splitlines()[0][:70])
            print("   Reason :", error)

    connection.commit()
    cursor.close()
    connection.close()
    print(file_path, "finished:", len(statements) - failed, "of", len(statements), "statements ran")


def send_table_to_mysql(df, table_name, engine):

    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(table_name, "sent to MySQL:", len(df), "rows")



def check_mysql_row_counts(tables, engine):

    for table_name, df in tables.items():

        result = pd.read_sql(
            "SELECT COUNT(*) AS total_rows FROM " + table_name, engine
        )

        mysql_rows = result["total_rows"][0]
        python_rows = len(df)

        print(table_name, "| Python:", python_rows,
              "| MySQL:", mysql_rows,
              "| Match:", python_rows == mysql_rows)



# cleaning pipeline of the Customers table
def clean_customers():
    print("========== CUSTOMERS ==========")
    customers = load_table("Customers.xlsx")
    audit_table(customers, id_column="Customer_ID")
    show_values(customers, ["Gender", "Age_Group", "City", "Customer_Type", "Preferred_Cuisine"])
    print(customers[["Total_Orders", "Average_Spend"]].describe())

    customers = remove_duplicates(customers)
    customers = clean_text(customers)
    customers = make_ids_uppercase(customers, ["Customer_ID"])
    customers = fix_spelling(customers, "City", "Metropolitian", "Metropolitan")

    print(find_outliers_iqr(customers, ["Total_Orders", "Average_Spend"]))
    customers = winsorize_iqr(customers, "Total_Orders")
    return customers


# cleaning pipeline of the Restaurants table
def clean_restaurants():
    print("========== RESTAURANTS ==========")
    restaurants = load_table("Restaurants.xlsx")
    audit_table(restaurants, id_column="Restaurant_ID")
    show_values(restaurants, ["City", "Cuisine_Type"])
    print(restaurants[["Avg_Preparation_Time_Minutes", "Avg_Rating", "Order_Capacity_Per_Day"]].describe())

    restaurants = remove_duplicates(restaurants)
    restaurants = clean_text(restaurants)
    restaurants = make_ids_uppercase(restaurants, ["Restaurant_ID"])
    restaurants = fix_spelling(restaurants, "City", "Metropolitian", "Metropolitan")
    restaurants = fill_missing_median(restaurants, "Avg_Rating", "City")
    restaurants = round_columns(restaurants, {"Avg_Rating": 2})

    print(find_outliers_iqr(restaurants, ["Avg_Preparation_Time_Minutes", "Avg_Rating", "Order_Capacity_Per_Day"]))
    return restaurants


# cleaning pipeline of the Delivery Partners table
def clean_partners():
    print("========== DELIVERY PARTNERS ==========")
    partners = load_table("Delivery_Partners.xlsx")
    audit_table(partners, id_column="Delivery_Partner_ID")
    show_values(partners, ["Vehicle_Type", "Region"])
    print(partners[["Avg_Delivery_Speed_KMPH", "Successful_Deliveries", "Delayed_Deliveries",
                    "Avg_Customer_Rating", "Delivery_Efficiency_Score"]].describe())

    partners = remove_duplicates(partners)
    partners = clean_text(partners)
    partners = make_ids_uppercase(partners, ["Delivery_Partner_ID"])
    partners = fix_spelling(partners, "Region", "Metropolitian", "Metropolitan")
    partners = cap_at_maximum(partners, "Avg_Customer_Rating", 5)
    partners = fill_missing_median(partners, "Avg_Customer_Rating", "Region")
    partners = fill_missing_median(partners, "Delivery_Efficiency_Score", "Region")
    partners = round_columns(partners, {"Avg_Customer_Rating": 2, "Avg_Delivery_Speed_KMPH": 2,
                                        "Delivery_Efficiency_Score": 3})

    print(find_outliers_iqr(partners, ["Avg_Delivery_Speed_KMPH", "Successful_Deliveries", "Delayed_Deliveries",
                                       "Avg_Customer_Rating", "Delivery_Efficiency_Score"]))
    partners = winsorize_iqr(partners, "Delayed_Deliveries")
    return partners


# cleaning pipeline of the Orders table
def clean_orders():
    print("========== ORDERS ==========")
    orders = load_table("Orders.xlsx")
    audit_table(orders, id_column="Order_ID")
    print("Duplicate rows if Order_ID is ignored:", orders.drop(columns="Order_ID").duplicated().sum())
    show_values(orders, ["Region", "Payment_Mode", "Order_Status"])
    print(orders[["Order_Value", "Delivery_Fee", "Discount_Applied", "Final_Amount",
                  "Delivery_Time_Minutes", "Order_Rating"]].describe())

    orders = remove_duplicates(orders)
    orders = clean_text(orders)
    orders = make_ids_uppercase(orders, ["Order_ID", "Customer_ID", "Restaurant_ID", "Delivery_Partner_ID"])
    orders = fix_spelling(orders, "Region", "Metropolitian", "Metropolitan")
    orders["Order_Date"] = pd.to_datetime(orders["Order_Date"])
    orders = add_order_key(orders)

    print(find_outliers_iqr(orders, ["Order_Value", "Delivery_Fee", "Discount_Applied", "Final_Amount",
                                     "Delivery_Time_Minutes", "Order_Rating"]))
    return orders
