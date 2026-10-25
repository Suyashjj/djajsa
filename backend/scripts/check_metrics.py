import sys
sys.path.append(".")
from datetime import date

import pandas as pd

from app.metrics import actuals_hourly, build_comparison, compute_metrics, metrics_by_day, metrics_by_horizon
from app.processing import load_actuals, load_forecasts, select_forecasts_for_period

pd.set_option("display.width", 200)

actuals_h = actuals_hourly(load_actuals())
actuals_h = actuals_h[actuals_h["startTime"] < pd.Timestamp("2026-02-01", tz="UTC")]
forecasts = load_forecasts()

selected = select_forecasts_for_period(forecasts, date(2026, 1, 1), date(2026, 1, 31))
cmp = build_comparison(selected, actuals_h)
print("hourly actuals:", len(actuals_h), "| compared rows:", len(cmp))

print("\nOVERALL (09:00 D-1 cutoff):")
for k, v in compute_metrics(cmp).items():
    print(f"  {k}: {v}")

print("\nBY DAY (first 5):")
print(metrics_by_day(cmp)[["date", "n", "mae_mw", "rmse_mw", "bias_mw"]].head().round(1))

print("\nBY HORIZON (all forecast versions):")
print(metrics_by_horizon(forecasts, actuals_h)[
    ["horizon_from_h", "horizon_to_h", "n", "mae_mw", "rmse_mw", "bias_mw"]].round(1))