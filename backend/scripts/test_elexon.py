import sys
sys.path.append(".")  # so "app" is importable when run from /backend

from app.elexon_client import fetch_actual_wind, fetch_wind_forecast

actual = fetch_actual_wind("2026-01-10", "2026-01-10")
print("\nACTUALS:", actual.shape)
print(actual.head())
print(actual.dtypes)

forecast = fetch_wind_forecast("2026-01-09", "2026-01-10")
print("\nFORECASTS:", forecast.shape)
print(forecast.head())
print(forecast.dtypes)