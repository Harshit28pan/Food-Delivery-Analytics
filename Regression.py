"""
Regression module: simple and multiple linear regression
Simple linear regression = 1 independent variable (X) and 1 dependent variable (y)
    y = intercept + slope * X
Multiple linear regression = 2 or more independent variables (X) and 1 dependent variable (y)
    y = intercept + b1 * X1 + b2 * X2 + ...
Model 1: Daily_Revenue (y) from a variable that is known in advance, used for the 2026 forecast
Model 2: Avg_Customer_Rating (y) of the delivery partners from one partner KPI
Model 1C and 2C: the multiple regression versions of Model 1 and Model 2 (main.py step 7)
Model 3: Avg_Order_Value (y) of the day from the calendar variables (simple regression)
Model 4: Delayed_Deliveries (y) of a delivery partner from one partner variable (simple regression)
Only functions here. They are called from main.py
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import EDA as eda

CHART_FOLDER = "regression_charts"
os.makedirs(CHART_FOLDER, exist_ok=True)


# ---------------- DATA FOR MODEL 1: ONE ROW = ONE DAY ----------------
# Daily_Revenue = total final amount of the delivered orders of the day   (y)
# The other columns are things we already know about a day before it happens (calendar)

def create_daily_data(data):
    delivered = data[data["Order_Status"] == "Delivered"]

    daily = delivered.groupby("Order_Date").agg(
        Daily_Revenue=("Final_Amount", "sum"),
        Festival_Flag=("Festival_Flag", "max")
    ).reset_index()

    daily["Order_Year"] = daily["Order_Date"].dt.year
    daily["Month"] = daily["Order_Date"].dt.month
    daily["Is_Weekend"] = (daily["Order_Date"].dt.dayofweek >= 5).astype(int)

    print("Daily data shape:", daily.shape)
    return daily


# ---------------- DATA FOR MODEL 2: ONE ROW = ONE DELIVERY PARTNER ----------------
# Avg_Customer_Rating = average rating the customers gave to the partner   (y)

def create_partner_data(partners):
    columns = ["Avg_Customer_Rating", "Avg_Delivery_Speed_KMPH", "Successful_Deliveries", "Delayed_Deliveries"]
    partner_data = partners[columns].copy()
    print("Partner data shape:", partner_data.shape)
    return partner_data


# ---------------- FEATURE SELECTION (FOR SIMPLE REGRESSION) ----------------
# Simple regression needs only 1 X. We choose it in 2 steps:
# Step 1: the candidate list has only variables that are known when we predict
#         and that are not a part of y (so no variable that is just a formula of y).
#         Daily_Orders is left out of Model 1 because it is not known for 2026 and it
#         decides the revenue directly. Delivery_Efficiency_Score is left out of Model 2
#         because the score is built from the rating itself.
# Step 2: find the correlation (r) of every candidate with y and take the one with the
#         highest |r| (the strongest relationship).
# This is done on the train data only, so the test data stays unseen.

DAILY_FEATURES = ["Festival_Flag", "Month", "Is_Weekend"]
PARTNER_FEATURES = ["Avg_Delivery_Speed_KMPH", "Successful_Deliveries", "Delayed_Deliveries"]


def select_feature(train_data, y_col, candidates):
    correlation = train_data[candidates].corrwith(train_data[y_col])      # r of every candidate with y
    print(correlation.round(3))

    best = correlation.abs().idxmax()                                     # highest |r|
    print("Selected X for", y_col, ":", best)
    return best


# ---------------- TRAIN ----------------

def train_model(train_data, x_cols, y_col):
    # x_cols = one column name (simple regression) or a list of names (multiple regression)
    if isinstance(x_cols, str):
        x_cols = [x_cols]

    model = LinearRegression()
    model.fit(train_data[x_cols], train_data[y_col])        # x_cols is a list, so X is a table

    print("Intercept:", round(model.intercept_, 4))
    equation = str(round(model.intercept_, 4))
    for col, coef in zip(x_cols, model.coef_):
        print("Coefficient of", col, ":", round(coef, 4))    # change in y for +1 in this X (other X fixed)
        equation = equation + " + " + str(round(coef, 4)) + " * " + col
    print("Equation :", y_col, "=", equation)
    return model


# ---------------- EVALUATE ----------------

def evaluate_model(model, data, x_cols, y_col):
    if isinstance(x_cols, str):
        x_cols = [x_cols]
    actual = data[y_col]
    predicted = model.predict(data[x_cols])

    mae = mean_absolute_error(actual, predicted)      # average error (same unit as y)
    mse = mean_squared_error(actual, predicted)       # average of squared errors
    rmse = np.sqrt(mse)                               # MSE brought back to the unit of y
    r2 = r2_score(actual, predicted)                  # share of variation explained

    print("MAE :", round(mae, 3))
    print("MSE :", round(mse, 3))
    print("RMSE:", round(rmse, 3))
    print("R2  :", round(r2, 3))


# ---------------- PREDICTION FOR NEW VALUES ----------------
# give some X values and the model tells the expected y

def predict_values(model, x_col, y_col, values):
    for value in values:
        predicted = model.predict(pd.DataFrame({x_col: [value]}))[0]
        print(x_col, "=", value, "->", "predicted", y_col, "=", round(predicted, 2))


# ---------------- CHARTS ----------------

def plot_regression_line(data, model, x_col, y_col, title, file_name):
    plt.figure(figsize=(8, 5))
    plt.scatter(data[x_col], data[y_col], color=eda.TEAL, alpha=0.5, label="Actual (test data)")

    # the straight line = predicted values
    x_line = pd.DataFrame({x_col: [data[x_col].min(), data[x_col].max()]})
    plt.plot(x_line[x_col], model.predict(x_line), color=eda.ORANGE, linewidth=2.5, label="Regression line")

    if data[x_col].nunique() == 2:          # a 0/1 variable: show only 0 and 1 on the axis
        plt.xticks([0, 1])

    plt.title(title, color=eda.NAVY)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.legend()
    eda.save_chart(CHART_FOLDER, file_name)


def plot_residuals(data, model, x_col, y_col, title, file_name):
    # residual = actual - predicted. Good model: points spread randomly around 0
    predicted = model.predict(data[[x_col]])

    plt.figure(figsize=(8, 5))
    plt.scatter(predicted, data[y_col] - predicted, color=eda.TEAL, alpha=0.5)
    plt.axhline(0, linestyle="--", color="red")
    plt.title(title, color=eda.NAVY)
    plt.xlabel("Predicted " + y_col)
    plt.ylabel("Residual")
    eda.save_chart(CHART_FOLDER, file_name)


# ---------------- 2026 FORECAST (MODEL 1) ----------------
# The X of Model 1 is known in advance (festive months and weekdays come from the calendar),
# so the 2026 forecast needs no assumption: we find X for every day of 2026,
# predict the daily revenue and add the days up month by month.

def forecast_2026(model, x_col, daily_data):
    festive_months = sorted(daily_data[daily_data["Festival_Flag"] == 1]["Month"].unique())

    days = pd.DataFrame({"Order_Date": pd.date_range("2026-01-01", "2026-12-31")})
    days["Month"] = days["Order_Date"].dt.month
    days["Festival_Flag"] = days["Month"].isin(festive_months).astype(int)
    days["Is_Weekend"] = (days["Order_Date"].dt.dayofweek >= 5).astype(int)

    days["Predicted_Revenue"] = model.predict(days[[x_col]])
    monthly_forecast = days.groupby("Month")["Predicted_Revenue"].sum()

    print("Festive months used:", [int(m) for m in festive_months])
    print(monthly_forecast.round(0))
    print("Total 2026 forecast:", round(monthly_forecast.sum(), 0))
    return monthly_forecast


def plot_forecast(monthly_forecast, actual_2025, festive_months):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    colors = [eda.ORANGE if m in festive_months else eda.TEAL for m in monthly_forecast.index]

    plt.figure(figsize=(10, 5))
    plt.bar(months, monthly_forecast.values / 1_000_000, color=colors, label="2026 forecast")
    plt.plot(months, actual_2025.values / 1_000_000, color=eda.NAVY, marker="o", label="2025 actual")
    plt.title("2026 Monthly Revenue Forecast (festive months in orange)", color=eda.NAVY)
    plt.ylabel("Revenue (million Rs)")
    plt.legend()
    eda.save_chart(CHART_FOLDER, "Forecast_2026.png")


# =====================================================================================
# NEW PART: MULTIPLE LINEAR REGRESSION (MODEL 1)
# Multiple linear regression = 2 or more independent variables (X) and 1 dependent variable (y)
#     y = intercept + b1 * X1 + b2 * X2 + ...
# train_model and evaluate_model (above) also accept a LIST of X columns, so the same functions are used.
# =====================================================================================

# ---------------- EXTRA COLUMN FOR MODEL 1 ----------------
# Avg_Order_Value = average order value of the day
# It is known only after the day is over, so it is not used for the 2026 forecast.
# We use it to see how much more of the daily revenue can be explained.

def add_order_value_column(daily_data, data):
    order_info = data.groupby("Order_Date").agg(
        Avg_Order_Value=("Order_Value", "mean")
    ).reset_index()

    daily_data = daily_data.merge(order_info, on="Order_Date", how="left")
    print("Daily data shape after adding the order value column:", daily_data.shape)
    return daily_data


# ---------------- MODELS TO COMPARE ----------------
# Each model = a name and its list of X variables. y is Daily_Revenue for all of them.

MODEL1_OPTIONS = {
    "1A Festival_Flag": ["Festival_Flag"],
    "1B Festival_Flag + Is_Weekend": ["Festival_Flag", "Is_Weekend"],     # Is_Weekend does not increase R2
    "1C Festival_Flag + Avg_Order_Value": ["Festival_Flag", "Avg_Order_Value"]
}


# ---------------- COMPARE ALL MODELS IN ONE TABLE ----------------

def compare_models(train_data, test_data, model_options, y_col):
    rows = []
    for name, x_cols in model_options.items():
        model = LinearRegression()
        model.fit(train_data[x_cols], train_data[y_col])

        train_r2 = r2_score(train_data[y_col], model.predict(train_data[x_cols]))
        test_predicted = model.predict(test_data[x_cols])
        test_r2 = r2_score(test_data[y_col], test_predicted)
        test_mae = mean_absolute_error(test_data[y_col], test_predicted)

        rows.append([name, round(train_r2, 3), round(test_r2, 3), round(test_mae, 3)])

    table = pd.DataFrame(rows, columns=["Model", "Train_R2", "Test_R2", "Test_MAE"])
    print(table.to_string(index=False))
    return table


def plot_r2_comparison(table, title, file_name):
    plt.figure(figsize=(9, 5))
    bars = plt.bar(table["Model"], table["Test_R2"], color=eda.TEAL)
    for bar, value in zip(bars, table["Test_R2"]):
        plt.text(bar.get_x() + bar.get_width() / 2, value + 0.01, str(value), ha="center")

    plt.title(title, color=eda.NAVY)
    plt.ylabel("R2 on test data")
    plt.ylim(0, 1)
    plt.xticks(rotation=15, ha="right")
    eda.save_chart(CHART_FOLDER, file_name)


# =====================================================================================
# NEW PART: MULTIPLE LINEAR REGRESSION (MODEL 2)
# The functions compare_models and plot_r2_comparison from the Model 1 part above are used here also.
# =====================================================================================

# ---------------- EXTRA COLUMN FOR MODEL 2 ----------------
# Delay_Rate = Delayed_Deliveries / (Delayed_Deliveries + Successful_Deliveries)
# A partner with 2 late deliveries out of 10 is worse than a partner with 2 late deliveries
# out of 100. The delay count alone cannot show this, the rate can.

def add_delay_rate(partner_data):
    partner_data = partner_data.copy()
    total = partner_data["Delayed_Deliveries"] + partner_data["Successful_Deliveries"]
    partner_data["Delay_Rate"] = (partner_data["Delayed_Deliveries"] / total).fillna(0)   # 0 deliveries -> rate 0
    print("Partner data shape after adding Delay_Rate:", partner_data.shape)
    return partner_data


# ---------------- MODELS TO COMPARE ----------------
# y is Avg_Customer_Rating for all of them.

MODEL2_OPTIONS = {
    "2A Avg_Delivery_Speed_KMPH": ["Avg_Delivery_Speed_KMPH"],
    "2B Speed + Delayed + Successful": ["Avg_Delivery_Speed_KMPH", "Delayed_Deliveries", "Successful_Deliveries"],
    "2C Speed + Delay_Rate": ["Avg_Delivery_Speed_KMPH", "Delay_Rate"]
}


# =====================================================================================
# NEW PART: MODEL 3 AND MODEL 4 (2 MORE SIMPLE LINEAR REGRESSION MODELS)
# They use the same functions as the first 2 models (select_feature, train_model,
# evaluate_model, predict_values, plot_regression_line, plot_residuals), so no new
# training code is needed. Only the candidate lists and two small helpers are new.
#
# Model 3: Avg_Order_Value (y) of the day, from the calendar variables.
#          Data = the daily data of Model 1 after add_order_value_column().
#          Train = 2023-24, test = 2025, same as Model 1.
# Model 4: Delayed_Deliveries (y) of a delivery partner, from the partner variables.
#          Data = the partner data of Model 2. Same 80% / 20% split as Model 2.
# =====================================================================================

MODEL3_FEATURES = ["Festival_Flag", "Month", "Is_Weekend"]
MODEL4_FEATURES = ["Successful_Deliveries", "Avg_Delivery_Speed_KMPH", "Avg_Customer_Rating"]


# average of y for every value of a group column (for example festive day and normal day)
def show_group_average(data, group_col, y_col):
    print(data.groupby(group_col)[y_col].mean().round(2))


# train a model and evaluate it on the train data and on the unseen test data (used by all the models of step 7)
def run_model(train_data, test_data, x_cols, y_col, name, test_label):
    print("\n" + name + " - coefficients")
    model = train_model(train_data, x_cols, y_col)

    print("\n" + name + " - train")
    evaluate_model(model, train_data, x_cols, y_col)

    print("\n" + name + " - test (" + test_label + ")")
    evaluate_model(model, test_data, x_cols, y_col)
    return model
