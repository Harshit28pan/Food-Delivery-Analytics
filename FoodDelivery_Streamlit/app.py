"""
app.py  -  Food Delivery Operations & Forecast Dashboard

Run with:   streamlit run app.py

How Streamlit works: this file runs from top to bottom every time the user changes
a filter. The calculations are in the src/ folder, this file only decides what to show.
"""
import pandas as pd
import streamlit as st

import config
from src import charts, data_loader, forecasting, kpis, stats_tests

# ---------------------------------------------------------------- page setup
st.set_page_config(page_title="Food Delivery Dashboard", layout="wide")

# ---------------------------------------------------------------- load data
tables = data_loader.load_tables()
merged = data_loader.build_merged(tables)       # orders + customer + restaurant + partner columns
partners = tables["partners"]
restaurants = tables["restaurants"]

# ---------------------------------------------------------------- sidebar filters
st.sidebar.title("Filters")
all_years = sorted(merged["Order_Year"].unique())
years = st.sidebar.multiselect("Year", all_years, default=all_years)
regions = st.sidebar.multiselect("Region", config.REGION_ORDER, default=config.REGION_ORDER)
vehicles = st.sidebar.multiselect("Vehicle type", config.VEHICLE_ORDER, default=config.VEHICLE_ORDER)


# stop the page if a filter is empty, otherwise the calculations would fail
if not years or not regions or not vehicles:
    st.warning("Please select at least one year, region and vehicle type.")
    st.stop()

# apply the filters: df = selected orders, partners_f / restaurants_f = selected partners / restaurants
df = data_loader.apply_filters(merged, years, regions, vehicles)
df_all_years = data_loader.apply_filters(merged, all_years, regions, vehicles)
partners_f = data_loader.filter_partners(partners, regions, vehicles)
restaurants_f = restaurants[restaurants["City"].isin(regions)]

if df.empty or partners_f.empty:
    st.warning("No data for this combination of filters.")
    st.stop()

st.title("Food Delivery: Operations & Forecast")
st.caption(f"{len(df):,} orders selected")

# ---------------------------------------------------------------- tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Overview", "Delivery partners", "Restaurants", "2026 Forecast", "Statistics"])

# ================================================================ TAB 1: OVERVIEW
with tab1:
    k = kpis.headline_kpis(df, partners_f)

    # five KPI cards in one row
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Delivered revenue", kpis.format_money(k["revenue"]))
    c1.caption(f"{k['delivered_orders']:,} delivered orders")
    c2.metric("Orders lost", f"{k['lost_rate']:.1f}%")
    c2.caption("Cancelled + returned")
    c3.metric("Avg delivery time", f"{k['avg_delivery_time']:.1f} min")
    c3.caption(f"Average rating {k['avg_rating']:.2f}")
    c4.metric("Active partners", f"{k['active_partners']:,}")
    c4.caption(f"Average speed {k['avg_speed']:.1f} KMPH")
    c5.metric("Orders per partner", f"{k['orders_per_partner']:,.0f}")
    c5.caption(f"Efficiency score {k['avg_efficiency']:.2f}")

    region_df = kpis.region_load(df, partners_f)

    # automatic insight: show a message only when one region is much busier than the others
    busiest = region_df.loc[region_df["Orders_per_Partner"].idxmax()]
    lightest_load = region_df["Orders_per_Partner"].min()
    if busiest["Orders_per_Partner"] > 2 * lightest_load:
        st.info(f"{busiest['Region']} partners handle {busiest['Orders_per_Partner']:,.0f} orders each, "
                f"about {busiest['Orders_per_Partner'] / lightest_load:.1f} times the lightest region, "
                f"and they are slower ({busiest['Avg_Speed']:.1f} KMPH). Supply is the problem, not demand.")

    left, right = st.columns([3, 2])
    left.pyplot(charts.monthly_orders(kpis.monthly_orders(df)))
    right.pyplot(charts.status_mix(kpis.status_mix_by_region(df)))

    st.subheader("Region scorecard")
    st.dataframe(region_df.round(2), hide_index=True)

# ================================================================ TAB 2: DELIVERY PARTNERS
with tab2:
    region_df = kpis.region_load(df, partners_f)
    partner_df = kpis.partner_table(df, partners_f)

    left, right = st.columns(2)
    left.pyplot(charts.orders_per_partner(region_df))
    right.pyplot(charts.region_bar(region_df, "Avg_Efficiency", "Average efficiency score", "Score (0 to 1)"))

    left, right = st.columns(2)
    left.pyplot(charts.speed_by_region_vehicle(kpis.speed_by_region_vehicle(partners_f)))
    right.pyplot(charts.partner_scatter(partner_df))

    st.pyplot(charts.efficiency_hist(partners_f))

    # leaderboard with two small controls
    st.subheader("Partner leaderboard")
    show_which = st.radio("Show", ["Top 10", "Bottom 10"], horizontal=True)
    min_orders = st.slider("Minimum orders handled", 0, int(partner_df["Orders"].max()), 0)

    eligible = partner_df[partner_df["Orders"] >= min_orders]
    is_bottom = (show_which == "Bottom 10")         # True: lowest score first, False: highest first
    ranked = eligible.sort_values("Delivery_Efficiency_Score", ascending=is_bottom)
    columns = ["Delivery_Partner_ID", "Partner_Name", "Region", "Vehicle_Type", "Orders",
               "Avg_Customer_Rating", "Avg_Delivery_Speed_KMPH", "Delivery_Efficiency_Score"]
    st.dataframe(ranked[columns].head(10).round(2), hide_index=True)

# ================================================================ TAB 3: RESTAURANTS
with tab3:
    rest_df = kpis.restaurant_table(df, restaurants_f)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Restaurants", f"{len(rest_df):,}")
    c2.metric("Avg preparation time", f"{rest_df['Avg_Preparation_Time_Minutes'].mean():.1f} min")
    c3.metric("Avg restaurant rating", f"{rest_df['Avg_Rating'].mean():.2f}")
    low_capacity = (rest_df["Order_Capacity_Per_Day"] <= 1).mean() * 100
    c4.metric("Capacity of 1 order/day", f"{low_capacity:.1f}%")
    c4.caption("Source data issue, kept as it is")

    left, right = st.columns(2)
    left.pyplot(charts.prep_time(kpis.prep_time_by_cuisine_region(restaurants_f)))
    right.pyplot(charts.capacity_hist(restaurants_f))

    st.info("Preparation time depends on the region, not on the cuisine. "
            "Semi-Urban kitchens are the slowest.")

    st.subheader("Restaurants to review")
    sort_by = st.selectbox("Sort by", ["Slowest preparation", "Lowest rating", "Most orders"])
    if sort_by == "Slowest preparation":
        rest_df = rest_df.sort_values("Avg_Preparation_Time_Minutes", ascending=False)
    elif sort_by == "Lowest rating":
        rest_df = rest_df.sort_values("Avg_Rating")
    else:
        rest_df = rest_df.sort_values("Orders", ascending=False)
    columns = ["Restaurant_ID", "Restaurant_Name", "City", "Cuisine_Type",
               "Avg_Preparation_Time_Minutes", "Avg_Rating", "Orders"]
    st.dataframe(rest_df[columns].head(15), hide_index=True)

# ================================================================ TAB 4: FORECAST
with tab4:
    daily = forecasting.daily_revenue(df_all_years)
    monthly_fc, model, quality = forecasting.forecast_year(daily)
    actual = forecasting.actual_monthly_by_year(df_all_years)

    total_forecast = monthly_fc["Predicted_Revenue"].sum()
    last_year = actual.columns.max()
    last_year_total = actual[last_year].sum()
    peak = monthly_fc.loc[monthly_fc["Predicted_Revenue"].idxmax()]
    slowest = monthly_fc.loc[monthly_fc["Predicted_Revenue"].idxmin()]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("2026 forecast revenue", kpis.format_money(total_forecast))
    c1.caption(f"{(total_forecast / last_year_total - 1) * 100:+.1f}% compared with {last_year}")
    c2.metric("Peak month", peak["Month_Name"])
    c2.caption(kpis.format_money(peak["Predicted_Revenue"]))
    c3.metric("Slowest month", slowest["Month_Name"])
    c3.caption(kpis.format_money(slowest["Predicted_Revenue"]))
    c4.metric("Model R² on 2025 (test)", f"{quality['test_r2']:.3f}")
    c4.caption(f"Average daily error ₹{quality['test_mae']:,.0f}")

    st.pyplot(charts.forecast(monthly_fc, actual))
    st.info("The model uses only the month of the year (same method as the regression step). It repeats the seasonal pattern "
            "and does not assume any growth. Prepare stock and partners before October.")

    # model check: same numbers as the regression step (Model 2). Train = 2023-2024, test = 2025
    with st.expander("Model check (same as the regression step, Model 2)"):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("R² (train 2023-24)", f"{quality['train_r2']:.3f}")
        m2.metric("R² (test 2025)", f"{quality['test_r2']:.3f}")
        m3.metric("MAE (test 2025)", f"₹{quality['test_mae']:,.2f}")
        m4.metric("RMSE (test 2025)", f"₹{quality['test_rmse']:,.2f}")
        st.caption("These numbers match the regression output when all years, regions and vehicles are selected.")

    left, right = st.columns([3, 2])
    left.pyplot(charts.month_impact(forecasting.month_impact(model)))
    table = monthly_fc[["Month_Name", "Predicted_Revenue"]].round(0)
    right.dataframe(table, hide_index=True)
    right.download_button("Download forecast as CSV", table.to_csv(index=False), "forecast_2026.csv")

# ================================================================ TAB 5: STATISTICS
with tab5:
    st.caption("Same 5 tests, samples and random_state (42) as the statistics step, so the numbers match its output. "
               "They always use all orders (the sidebar filters do not change them). "
               "Significance level = 0.05: if the p-value is below 0.05 we reject the null hypothesis (H0).")

    # benchmark for tests 1 and 3 (the statistics step used 35 minutes)
    benchmark = st.number_input("Benchmark delivery time for the one-sample tests (minutes)", value=35)

    results = [
        ("1. One-sample Z-test", "Delivery time vs benchmark", stats_tests.one_sample_z_test(merged, benchmark)),
        ("2. Two-sample Z-test", "Delivery time: Metropolitan vs Semi-Urban", stats_tests.two_sample_z_test(merged)),
        ("3. One-sample T-test", "Delivery time vs benchmark (small sample)", stats_tests.one_sample_t_test(merged, benchmark)),
        ("4. Two-sample T-test", "Final amount: festive vs normal", stats_tests.two_sample_t_test(merged)),
        ("5. Paired T-test", "Monthly delivered revenue: 2024 vs 2025", stats_tests.paired_t_test(merged)),
    ]

    # summary table of all five tests
    summary = pd.DataFrame({
        "Test": [r[0] for r in results],
        "Question": [r[1] for r in results],
        "Test statistic": [round(r[2]["statistic"], 4) for r in results],
        "P-value": [f"{r[2]['p_value']:.4g}" for r in results],
        "Decision": [r[2]["decision"] for r in results],
    })
    st.dataframe(summary, hide_index=True)

    # one block per test: hypotheses, numbers, observation
    for title, question, r in results:
        st.subheader(title)
        st.write("**H0 (null):** " + r["h0"])
        st.write("**H1 (alternative):** " + r["h1"])
        c1, c2, c3 = st.columns(3)
        c1.metric("Test statistic", f"{r['statistic']:.4f}")
        c2.metric("P-value", f"{r['p_value']:.4g}")
        c3.metric("Decision", r["decision"])
        if r["rejected"]:
            st.success("Observation: " + r["observation"])
        else:
            st.info("Observation: " + r["observation"])
        st.caption(r["note"])
