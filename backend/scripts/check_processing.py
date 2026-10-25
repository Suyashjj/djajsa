import sys
sys.path.append(".")
from datetime import date

from app.processing import load_forecasts, select_forecast_for_day, select_forecasts_for_period

f = load_forecasts()

print("Publish times per day:\n", f.groupby(f["publishTime"].dt.date).size().head(3))
print("Distinct publish times on 2026-01-10:",
      f[f["publishTime"].dt.date == date(2026, 1, 10)]["publishTime"].nunique())
print("Horizon (h) of ALL forecasts:\n",
      ((f["startTime"] - f["publishTime"]).dt.total_seconds() / 3600).describe())

day = select_forecast_for_day(f, date(2026, 1, 10))
print("\n--- Delivery day 2026-01-10 ---")
print(day.head())
print("rows:", len(day), "| cutoff:", day["cutoff"].iloc[0])
assert (day["publishTime"] <= day["cutoff"]).all(), "leak: used a forecast after cutoff!"

jan = select_forecasts_for_period(f, date(2026, 1, 1), date(2026, 1, 31))
per_day = jan.groupby(jan["startTime"].dt.date).size()
print("\n--- Whole January ---")
print("total rows:", len(jan), "| rows/day min-max:", per_day.min(), "-", per_day.max())
print("Selected horizon (h):\n", jan["horizon_h"].describe())