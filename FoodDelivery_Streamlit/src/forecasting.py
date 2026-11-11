"""
forecasting.py
Step 3: predict the 2026 revenue. This is the same method as Regression.py:
daily delivered revenue + month columns (dummy variables) + Linear Regression.
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

import config


def daily_revenue(df):
    """Delivered revenue for every day."""
    delivered = df[df["Order_Status"] == "Delivered"]
    daily = delivered.groupby("Order_Date")["Final_Amount"].sum().reset_index()
    daily = daily.rename(columns={"Final_Amount": "Daily_Revenue"})
    daily["Month"] = daily["Order_Date"].dt.month
    daily["Order_Year"] = daily["Order_Date"].dt.year
    return daily


def month_columns(months):
    """
    Turn the month number into dummy (0/1) columns: Month_2 ... Month_12.
    January is left out on purpose, it is the base month the others are compared with.
    """
    dummies = pd.get_dummies(months, prefix="Month", drop_first=True, dtype=int)
    # make sure all 11 columns always exist, in the same order
    wanted = ["Month_" + str(m) for m in range(2, 13)]
    return dummies.reindex(columns=wanted, fill_value=0)


def check_model(daily):
    """
    Same check as Regression.py (Model 2): train on 2023 and 2024, test on 2025 (a year the model has not seen).
    These numbers are the ones printed by main.py (regression step).
    """
    train = daily[daily["Order_Year"] < 2025]
    test = daily[daily["Order_Year"] == 2025]
    X_train = month_columns(train["Month"])
    X_test = month_columns(test["Month"])

    model = LinearRegression()
    model.fit(X_train, train["Daily_Revenue"])
    test_predicted = model.predict(X_test)

    train_r2 = r2_score(train["Daily_Revenue"], model.predict(X_train))
    test_r2 = r2_score(test["Daily_Revenue"], test_predicted)
    test_mae = mean_absolute_error(test["Daily_Revenue"], test_predicted)
    test_rmse = np.sqrt(mean_squared_error(test["Daily_Revenue"], test_predicted))

    return {"train_r2": train_r2, "test_r2": test_r2, "test_mae": test_mae, "test_rmse": test_rmse,
            "n_train": len(train), "n_test": len(test)}


def forecast_year(daily, year=2026):
    """Train the model on all past days (same as Regression.py), then predict every day of `year`."""
    # 1. train on all years
    X = month_columns(daily["Month"])
    y = daily["Daily_Revenue"]
    model = LinearRegression()
    model.fit(X, y)

    # 2. model quality exactly as in Regression.py (train 2023-2024, test 2025)
    quality = check_model(daily)

    # 3. predict every day of the future year, then add the days up month by month
    dates = pd.date_range(str(year) + "-01-01", str(year) + "-12-31")
    future = pd.DataFrame({"Order_Date": dates, "Month": dates.month})
    future["Predicted_Revenue"] = model.predict(month_columns(future["Month"]))
    monthly = future.groupby("Month")["Predicted_Revenue"].sum().reset_index()
    monthly["Month_Name"] = monthly["Month"].apply(lambda m: config.MONTH_NAMES[m - 1])
    return monthly, model, quality


def actual_monthly_by_year(df):
    """Real delivered revenue: one row per month, one column per year."""
    delivered = df[df["Order_Status"] == "Delivered"]
    return delivered.pivot_table(index="Order_Month", columns="Order_Year",
                                 values="Final_Amount", aggfunc="sum")


def month_impact(model):
    """Extra daily revenue of each month compared with January (the model coefficients)."""
    return pd.DataFrame({"Month": config.MONTH_NAMES[1:], "Extra_Daily_Revenue": model.coef_})
