"""
app.py  -  Food Delivery Operations Dashboard

Run with:   streamlit run app.py

How Streamlit works: this file runs from top to bottom every time the user changes
a filter. The calculations are in the src/ folder, this file only decides what to show.
"""
import pandas as pd
import streamlit as st

import config
from src import charts, data_loader, kpis

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
partners_f = data_loader.filter_partners(partners, regions, vehicles)
restaurants_f = restaurants[restaurants["City"].isin(regions)]

if df.empty or partners_f.empty:
    st.warning("No data for this combination of filters.")
    st.stop()

st.title("Streamlit Dashboard")
st.caption(f"{len(df):,} orders selected")

# ---------------------------------------------------------------- tabs
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Delivery partners", "Restaurants", "Daily KPI lookup"])

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

# ================================================================ TAB 4: DAILY KPI LOOKUP
# Same idea as the "Daily KPI lookup" page of the Power BI report.
# Source: daily_kpi_summary (SQL). It is one row per day, so the sidebar filters do not apply here.
with tab4:
    daily = data_loader.build_daily_kpi(tables)

    st.caption("Pick a date to see the KPIs of that day. Sidebar filters do not apply to this tab.")
    picked = st.date_input("Date", value=daily["KPI_Date"].max().date(),
                           min_value=daily["KPI_Date"].min().date(),
                           max_value=daily["KPI_Date"].max().date())

    d = kpis.daily_kpis(daily, picked)
    if d is None:
        st.warning("No orders on this date.")
    else:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Orders", f"{d['orders']:,}")
        c2.metric("Delivered", f"{d['delivered']:,}")
        c3.metric("Cancelled", f"{d['cancelled']:,}")
        c4.metric("Returned", f"{d['returned']:,}")
        c5.metric("Revenue", kpis.format_money(d["revenue"]))

        c1, c2, c3 = st.columns(3)
        c1.metric("Delivered rate", f"{d['delivered_rate']:.1f}%")
        c2.metric("Cancel rate", f"{d['cancel_rate']:.1f}%")
        c3.metric("Orders vs average day", f"{d['vs_avg_day']:+.1f}%")
        c3.caption(f"Overall average day = {d['avg_overall']:.0f} orders")

        left, right = st.columns(2)
        left.pyplot(charts.daily_monthly_orders(kpis.daily_monthly_trend(daily), pd.Timestamp(picked)))
        right.pyplot(charts.daily_orders(kpis.daily_month_table(daily, picked), pd.Timestamp(picked), d["avg_day"]))
