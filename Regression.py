"""
Regression module: Linear Regression to predict Daily Revenue
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

TARGET = "Daily_Revenue"


# ---------------- DAILY DATA ----------------
# One row = one day. We add up the revenue of all delivered orders of that day.

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


# ---------------- MONTH DUMMY COLUMNS ----------------
# Month 1 to 12 are names, not a straight line, so we make one 0/1 column per month.
# January is left out (drop_first) and becomes the base month.

def create_month_columns(data):
    return pd.get_dummies(data["Month"], prefix="Month", drop_first=True, dtype=int)


# ---------------- MODEL 1: FEATURES CHOSEN BY CORRELATION ----------------

def select_features(train_data):
    correlation = train_data.corr(numeric_only=True)[TARGET].abs()

    # keep columns whose correlation with revenue is above 0.1 (not the target itself)
    selected = correlation[correlation > 0.1].index.tolist()
    selected.remove(TARGET)

    print("Selected features:", selected)
    return selected


# ---------------- TRAIN AND EVALUATE ----------------

def train_model(train_data, features):
    model = LinearRegression()
    model.fit(train_data[features], train_data[TARGET])

    print("Intercept:", round(model.intercept_, 2))
    for feature, coefficient in zip(features, model.coef_):
        print(feature, "coefficient:", round(coefficient, 2))
    return model


def evaluate_model(model, data, features):
    actual = data[TARGET]
    predicted = model.predict(data[features])

    mae = mean_absolute_error(actual, predicted)      # average error in rupees
    mse = mean_squared_error(actual, predicted)       # average of squared errors
    rmse = np.sqrt(mse)                               # MSE brought back to rupees
    r2 = r2_score(actual, predicted)                  # share of variation explained

    print("MAE :", round(mae, 2))
    print("MSE :", round(mse, 2))
    print("RMSE:", round(rmse, 2))
    print("R2  :", round(r2, 3))

    return actual, predicted


# ---------------- CHARTS ----------------

def plot_actual_predicted(actual, predicted, file_name):
    plt.figure(figsize=(10, 5))
    plt.plot(actual.values, label="Actual")
    plt.plot(predicted, label="Predicted")
    plt.title("Actual vs Predicted Daily Revenue (2025)")
    plt.xlabel("Day")
    plt.ylabel("Revenue")
    plt.legend()
    eda.save_chart(CHART_FOLDER, file_name)


def plot_residuals(actual, predicted, file_name):
    # residual = actual - predicted. Good model: points spread randomly around 0
    plt.figure(figsize=(8, 5))
    plt.scatter(predicted, actual - predicted, color=eda.TEAL)
    plt.axhline(0, linestyle="--", color="red")
    plt.title("Residual Plot")
    plt.xlabel("Predicted revenue")
    plt.ylabel("Residual")
    eda.save_chart(CHART_FOLDER, file_name)


# ---------------- FORECAST 2026 ----------------
# Train on all 3 years, then predict every day of 2026 and add up month by month.

def forecast_next_year(daily_data, month_features):
    model = LinearRegression()
    model.fit(daily_data[month_features], daily_data[TARGET])

    future = pd.DataFrame({"Order_Date": pd.date_range("2026-01-01", "2026-12-31")})
    future["Month"] = future["Order_Date"].dt.month
    future = future.join(create_month_columns(future))

    future["Predicted_Revenue"] = model.predict(future[month_features])
    monthly_forecast = future.groupby("Month")["Predicted_Revenue"].sum()

    print(monthly_forecast.round(0))
    print("Total 2026 forecast:", round(monthly_forecast.sum(), 0))

    return model, monthly_forecast


def plot_forecast(monthly_forecast):
    plt.figure(figsize=(10, 5))
    monthly_forecast.plot(marker="o", color=eda.TEAL)
    plt.title("2026 Monthly Revenue Forecast")
    plt.xlabel("Month")
    plt.ylabel("Predicted revenue")
    plt.xticks(range(1, 13), ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    plt.grid(True)
    eda.save_chart(CHART_FOLDER, "Forecast_2026.png")


# ---------------- MONTH IMPACT ----------------

def show_month_impact(model, month_features):
    # each coefficient = extra daily revenue of that month compared to January
    month_names = ["February", "March", "April", "May", "June", "July",
                   "August", "September", "October", "November", "December"]

    for name, coefficient in zip(month_names, model.coef_):
        print(name, "vs January:", round(coefficient, 0), "per day")
