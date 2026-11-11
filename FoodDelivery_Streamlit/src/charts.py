"""
charts.py
Step 6: every chart of the dashboard. Each function receives a table and returns a
matplotlib figure. The app then shows it with st.pyplot(figure).
"""
import matplotlib
matplotlib.use("Agg")            # draw without opening a window
import matplotlib.pyplot as plt

import config

# light colours so the charts match the light Streamlit theme
plt.rcParams["figure.facecolor"] = config.BG
plt.rcParams["axes.facecolor"] = config.PANEL
plt.rcParams["axes.edgecolor"] = config.GRID
plt.rcParams["grid.color"] = config.GRID
plt.rcParams["text.color"] = config.TEXT
plt.rcParams["axes.labelcolor"] = config.TEXT
plt.rcParams["axes.titlecolor"] = config.TEXT
plt.rcParams["xtick.color"] = config.TEXT
plt.rcParams["ytick.color"] = config.TEXT


def new_chart(title, width=7, height=3.8):
    """Create an empty chart with a title and a light horizontal grid."""
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_title(title, fontsize=13, fontweight="bold", loc="left")
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    return fig, ax


def region_colors(region_list):
    """One fixed colour for each region, so a region looks the same on every chart."""
    return [config.REGION_COLORS[region] for region in region_list]


def orders_per_partner(region_df):
    """Bar chart: how many orders each partner handles, per region."""
    fig, ax = new_chart("Orders handled per partner", 6)
    bars = ax.bar(region_df["Region"], region_df["Orders_per_Partner"],
                  color=region_colors(region_df["Region"]), width=0.55)
    ax.bar_label(bars, fmt="%.0f")                      # write the value on top of each bar
    ax.set_ylabel("Orders per partner")
    fig.tight_layout()
    return fig


def region_bar(region_df, column, title, ylabel):
    """Bar chart of any one column for each region (used for efficiency score)."""
    fig, ax = new_chart(title, 6)
    bars = ax.bar(region_df["Region"], region_df[column],
                  color=region_colors(region_df["Region"]), width=0.55)
    ax.bar_label(bars, fmt="%.2f")
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    return fig


def speed_by_region_vehicle(speed_df):
    """Grouped bars: average speed of each vehicle type inside each region."""
    # pivot: rows = region, columns = vehicle type, values = speed
    table = speed_df.pivot(index="Region", columns="Vehicle_Type", values="Avg_Delivery_Speed_KMPH")
    fig, ax = new_chart("Delivery speed by region and vehicle")
    table.plot(kind="bar", ax=ax, rot=0, color=config.PALETTE, width=0.8)
    ax.set_xlabel("")
    ax.set_ylabel("Average speed (KMPH)")
    ax.set_ylim(0, 32)                              # extra space on top for the legend
    ax.legend(title="Vehicle", fontsize=8, ncol=4, loc="upper center")
    fig.tight_layout()
    return fig


def partner_scatter(partner_df):
    """Scatter plot: each dot is one partner (orders handled vs rating)."""
    fig, ax = new_chart("Partner workload vs rating")
    for region in config.REGION_ORDER:
        part = partner_df[(partner_df["Region"] == region) & (partner_df["Orders"] > 0)]
        ax.scatter(part["Orders"], part["Avg_Order_Rating"], s=14, alpha=0.7,
                   color=config.REGION_COLORS[region], label=region)
    ax.set_xlabel("Orders handled by the partner")
    ax.set_ylabel("Average order rating")
    ax.legend(fontsize=8)
    fig.tight_layout()
    return fig


def efficiency_hist(partner_df):
    """Histogram: how the partner efficiency scores are spread in each region."""
    fig, ax = new_chart("Partner efficiency score")
    for region in config.REGION_ORDER:
        scores = partner_df[partner_df["Region"] == region]["Delivery_Efficiency_Score"]
        ax.hist(scores, bins=25, alpha=0.7, color=config.REGION_COLORS[region], label=region)
    ax.set_xlabel("Delivery efficiency score")
    ax.set_ylabel("Number of partners")
    ax.legend(fontsize=8)
    fig.tight_layout()
    return fig


def monthly_orders(monthly_df):
    """Bar chart: orders in each month. Festive months are orange, others teal."""
    fig, ax = new_chart("Orders by month (festive months in orange)", 8)
    colors = []
    for is_festive in monthly_df["Festive"]:
        colors.append(config.ORANGE if is_festive else config.TEAL)
    bars = ax.bar(monthly_df["Month_Name"], monthly_df["Orders"], color=colors, width=0.65)
    ax.bar_label(bars, fmt="%.0f", fontsize=8)
    ax.set_ylabel("Orders")
    fig.tight_layout()
    return fig


def status_mix(share_df):
    """Stacked horizontal bars: % of delivered, cancelled and returned orders per region."""
    colors = {"Delivered": config.TEAL, "Cancelled": config.ORANGE, "Returned": config.NAVY}
    fig, ax = new_chart("Order status share by region", 6, 3.2)
    share_df.plot(kind="barh", stacked=True, ax=ax,
                  color=[colors[status] for status in share_df.columns])
    ax.set_xlabel("% of orders")
    ax.set_ylabel("")
    ax.grid(axis="y", visible=False)
    ax.legend(fontsize=8, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.25))
    fig.tight_layout()
    return fig


def prep_time(prep_df):
    """Grouped bars: kitchen preparation time of each cuisine inside each region."""
    table = prep_df.pivot(index="Region", columns="Cuisine_Type", values="Avg_Preparation_Time_Minutes")
    fig, ax = new_chart("Kitchen preparation time")
    table.plot(kind="bar", ax=ax, rot=0, color=config.PALETTE, width=0.8)
    ax.set_xlabel("")
    ax.set_ylabel("Minutes")
    ax.set_ylim(0, 52)
    ax.legend(title="Cuisine", fontsize=8, ncol=4, loc="upper center")
    fig.tight_layout()
    return fig


def capacity_hist(restaurants_f):
    """Histogram: daily order capacity of the restaurants."""
    fig, ax = new_chart("Restaurant daily order capacity")
    ax.hist(restaurants_f["Order_Capacity_Per_Day"], bins=30, color=config.NAVY)
    ax.set_xlabel("Order capacity per day")
    ax.set_ylabel("Number of restaurants")
    fig.tight_layout()
    return fig


def forecast(monthly_fc, actual_by_year):
    """Line chart: real revenue of past years (grey) and the 2026 forecast (orange)."""
    fig, ax = new_chart("Monthly delivered revenue: actual vs 2026 forecast", 9, 4.2)
    month_names = monthly_fc["Month_Name"]
    for year in actual_by_year.columns:
        ax.plot(month_names, actual_by_year[year] / 1_000_000, color=config.MUTED,
                linewidth=1, marker="o", markersize=3, label="Actual " + str(year))
    ax.plot(month_names, monthly_fc["Predicted_Revenue"] / 1_000_000, color=config.ORANGE,
            linewidth=2.5, marker="o", label="Forecast 2026")
    ax.set_ylabel("Revenue (₹ million)")
    ax.legend(fontsize=8, ncol=4)
    fig.tight_layout()
    return fig


def month_impact(impact_df):
    """Bar chart: extra daily revenue of each month compared with January."""
    fig, ax = new_chart("Extra daily revenue compared with January", 7, 3.6)
    ax.bar(impact_df["Month"].str[:3], impact_df["Extra_Daily_Revenue"] / 1000,
           color=config.TEAL, width=0.65)
    ax.set_ylabel("₹ thousand per day")
    fig.tight_layout()
    return fig
