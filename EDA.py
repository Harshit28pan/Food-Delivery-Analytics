"""
EDA module: Exploratory Data Analysis (functions only, called from main.py)
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

EXCEL_FILE = os.path.join("final_dataset", "food_delivery_final.xlsx")

# one folder for every type of analysis
UNI_FOLDER = os.path.join("eda_charts", "univariate")
BI_FOLDER = os.path.join("eda_charts", "bivariate")
MULTI_FOLDER = os.path.join("eda_charts", "multivariate")
for folder in [UNI_FOLDER, BI_FOLDER, MULTI_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# project colour theme
NAVY, TEAL, ORANGE, DARK = "#1F3A5F", "#2A9D8F", "#E76F51", "#333333"
sns.set_theme(style="whitegrid")


def load_data():
    # read the 4 main tables from the final Excel file
    sheets = pd.read_excel(EXCEL_FILE, sheet_name=["orders", "customers", "restaurants", "delivery_partners"])
    for name, df in sheets.items():
        print("Loaded:", name, df.shape)
    return sheets["orders"], sheets["customers"], sheets["restaurants"], sheets["delivery_partners"]


def save_chart(folder, file_name):
    # save the current chart in the given folder and show it
    plt.tight_layout()
    path = os.path.join(folder, file_name)
    plt.savefig(path, dpi=150)
    plt.show()
    print("Saved:", path)


def summary_stats(df, columns, name):
    # count, mean, std, min, max and skewness of the numeric columns
    print("-----", name, "-----")
    print(df[columns].describe().round(2))
    print("Skewness:")
    print(df[columns].skew().round(2))


def plot_numeric(df, column, folder, file_prefix):
    # histogram (shape) and boxplot (outliers) of one numeric column
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    sns.histplot(df[column], bins=30, color=TEAL, ax=ax[0])
    ax[0].set_title("Distribution of " + column, color=NAVY, fontsize=13)
    sns.boxplot(x=df[column], color=ORANGE, ax=ax[1])
    ax[1].set_title("Boxplot of " + column, color=NAVY, fontsize=13)
    save_chart(folder, file_prefix + "_" + column + ".png")


def plot_categorical(df, column, folder, file_prefix):
    # bar chart of one categorical column with count and % on every bar
    counts = df[column].value_counts()
    percent = (counts / counts.sum() * 100).round(1)
    print(pd.DataFrame({"Count": counts, "Percent": percent}))

    plt.figure(figsize=(8, 4.5))
    sns.barplot(x=counts.index.astype(str), y=counts.values, color=TEAL)
    for i in range(len(counts)):
        plt.text(i, counts.values[i], f"{counts.values[i]:,}\n({percent.values[i]}%)",
                 ha="center", va="bottom", fontsize=10, color=DARK)
    plt.title("Count of " + column, color=NAVY, fontsize=14)
    plt.xlabel(column, fontsize=11)
    plt.ylabel("Count", fontsize=11)
    plt.ylim(0, counts.max() * 1.18)
    save_chart(folder, file_prefix + "_" + column + ".png")

def build_merged_dataset(orders, customers, restaurants, partners):
    # Relationships (one-to-many): one customer, one restaurant and one delivery
    # partner can have many orders. So orders is the main table and the other
    # three tables are joined to it using their ID columns.
    # Not joined: agg_ tables, daily_kpi and orders_backup. They are only summaries
    # or copies of orders, so joining them would count the same orders twice.

    # keep only the useful columns and give clear names to clashing columns
    customers_small = customers[["Customer_ID", "Gender", "Age_Group", "Customer_Type",
                                 "Preferred_Cuisine", "Average_Spend"]]
    restaurants_small = restaurants[["Restaurant_ID", "Cuisine_Type", "Avg_Preparation_Time_Minutes",
                                     "Order_Capacity_Per_Day"]]
    partners_small = partners[["Delivery_Partner_ID", "Vehicle_Type", "Avg_Delivery_Speed_KMPH",
                               "Delayed_Deliveries", "Delivery_Efficiency_Score"]]

    # validate checks that every ID is unique in the smaller table (many orders to one row)
    data = orders.merge(customers_small, on="Customer_ID", how="left", validate="many_to_one")
    data = data.merge(restaurants_small, on="Restaurant_ID", how="left", validate="many_to_one")
    data = data.merge(partners_small, on="Delivery_Partner_ID", how="left", validate="many_to_one")

    # month and year columns for the monthly analysis
    data["Order_Year"] = data["Order_Date"].dt.year
    data["Order_Month"] = data["Order_Date"].dt.month

    print("Merged dataset:", data.shape)
    print("Rows same as orders:", len(data) == len(orders))
    print("Missing values after merge:", data.isnull().sum().sum())
    return data

def plot_bar(table, x, y, title, y_label, folder, file_name, decimals=0):
    # simple bar chart: x column on the bottom, y column as bar height, value written on each bar
    plt.figure(figsize=(8, 4.5))
    sns.barplot(data=table, x=x, y=y, color=TEAL)
    for i in range(len(table)):
        plt.text(i, table[y].iloc[i], f"{table[y].iloc[i]:,.{decimals}f}",
                 ha="center", va="bottom", fontsize=10, color=DARK)
    plt.title(title, color=NAVY, fontsize=14)
    plt.xlabel(x, fontsize=11)
    plt.ylabel(y_label, fontsize=11)
    plt.ylim(0, table[y].max() * 1.15)
    save_chart(folder, file_name)


def bivariate_part1(data, partners):
    # 4 bivariate charts for the business questions
    delivered = data[data["Order_Status"] == "Delivered"]

    # 1. Region vs delivered revenue
    region_revenue = delivered.groupby("Region")["Final_Amount"].sum().reset_index()
    print(region_revenue)
    plot_bar(region_revenue, "Region", "Final_Amount", "Delivered Revenue by Region",
             "Delivered Revenue (Rs)", BI_FOLDER, "bi_1_region_revenue.png")

    # 2. Customer type vs delivered revenue
    type_revenue = delivered.groupby("Customer_Type")["Final_Amount"].sum().reset_index()
    type_revenue = type_revenue.sort_values("Final_Amount", ascending=False)
    type_revenue["Share_%"] = (type_revenue["Final_Amount"] / type_revenue["Final_Amount"].sum() * 100).round(1)
    print(type_revenue)
    plot_bar(type_revenue, "Customer_Type", "Final_Amount", "Delivered Revenue by Customer Type",
             "Delivered Revenue (Rs)", BI_FOLDER, "bi_2_customer_type_revenue.png")

    # 3. Region vs cancelled % and returned %
    # give 100 to a cancelled order and 0 to others, so the average becomes the percentage
    
    data["Is_Cancelled"] = (data["Order_Status"] == "Cancelled") * 100
    data["Is_Returned"] = (data["Order_Status"] == "Returned") * 100
    rate = data.groupby("Region")[["Is_Cancelled", "Is_Returned"]].mean().round(2)
    print(rate)
    rate.plot(kind="bar", color=[ORANGE, NAVY], figsize=(8, 4.5))
    plt.title("Cancelled and Returned Orders by Region (%)", color=NAVY, fontsize=14)
    plt.xlabel("Region", fontsize=11)
    plt.ylabel("% of orders", fontsize=11)
    plt.xticks(rotation=0)
    save_chart(BI_FOLDER, "bi_3_region_cancel_return.png")
    

    # 4. Vehicle type vs average delivery speed (from the delivery partners table)
    speed = partners.groupby("Vehicle_Type")["Avg_Delivery_Speed_KMPH"].mean().round(2).reset_index()
    speed = speed.sort_values("Avg_Delivery_Speed_KMPH", ascending=False)
    print(speed)
    plot_bar(speed, "Vehicle_Type", "Avg_Delivery_Speed_KMPH", "Average Delivery Speed by Vehicle Type",
             "Speed (KMPH)", BI_FOLDER, "bi_4_vehicle_speed.png", decimals=2)
    
def bivariate_part2(data):
    # 4 more bivariate charts: festive vs normal, month, year and correlation

    # 5. Festival flag vs average order value
    festive = data.groupby("Festival_Flag")["Order_Value"].mean().round(2).reset_index()
    festive["Festival_Flag"] = festive["Festival_Flag"].map({0: "Normal", 1: "Festive"})
    print(festive)
    plot_bar(festive, "Festival_Flag", "Order_Value", "Average Order Value: Festive vs Normal Orders",
             "Average Order Value (Rs)", BI_FOLDER, "bi_5_festive_order_value.png", decimals=2)

    # 6. Month vs total orders (all 3 years together)
    month_orders = data.groupby("Order_Month").size().reset_index(name="Total_Orders")
    print(month_orders)
    plot_bar(month_orders, "Order_Month", "Total_Orders", "Total Orders by Month (2023-2025)",
             "Total Orders", BI_FOLDER, "bi_6_month_orders.png")

    # 7. Year vs total orders
    year_orders = data.groupby("Order_Year").size().reset_index(name="Total_Orders")
    print(year_orders)
    plot_bar(year_orders, "Order_Year", "Total_Orders", "Total Orders by Year",
             "Total Orders", BI_FOLDER, "bi_7_year_orders.png")

    # 8. Correlation between the numeric columns (+1 = move together, 0 = no relation)
    numeric_cols = ["Order_Value", "Delivery_Fee", "Discount_Applied", "Delivery_Time_Minutes",
                    "Order_Rating", "Avg_Delivery_Speed_KMPH", "Delivery_Efficiency_Score",
                    "Avg_Preparation_Time_Minutes", "Order_Capacity_Per_Day"]
    corr = data[numeric_cols].corr().round(2)
    plt.figure(figsize=(9,7))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, annot_kws={"size": 10})
    plt.title("Correlation between Numeric Columns", color=NAVY, fontsize=13)
    plt.xticks(rotation=45, ha="right", fontsize=11)
    save_chart(BI_FOLDER, "bi_8_correlation_heatmap.png")
