"""
Project settings in one place: paths, colours, month names.
Every other module imports from here, so a change is made only once.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

FILES = {
    "orders": "orders_clean.csv",
    "customers": "customers_clean.csv",
    "restaurants": "restaurants_clean.csv",
    "partners": "delivery_partners_clean.csv",
    "daily_kpi": "daily_kpi_summary.csv",      # exported from MySQL (table daily_kpi_summary)
}

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# festive months as defined in the EDA report (March, July, Aug, Oct, Nov, Dec)
FESTIVE_MONTHS = [3, 7, 8, 10, 11, 12]

# light dashboard theme (same colours as the Excel / Power BI / EDA charts)
BG = "#FFFFFF"
PANEL = "#FFFFFF"
GRID = "#E1E5EA"
TEXT = "#333333"
MUTED = "#9AA3AF"

NAVY = "#1F3A5F"
TEAL = "#2A9D8F"
ORANGE = "#E76F51"
GOLD = "#E9C46A"
PURPLE = "#8E7DBE"

PALETTE = [NAVY, TEAL, ORANGE, GOLD, PURPLE]   # colours used for grouped bars

REGION_COLORS = {"Metropolitan": NAVY, "Semi-Urban": ORANGE, "Urban": TEAL}
VEHICLE_ORDER = ["Bicycle", "Scooter", "Bike", "Car"]
REGION_ORDER = ["Metropolitan", "Semi-Urban", "Urban"]
