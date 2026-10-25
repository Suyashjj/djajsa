import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

sys.path.append(".")  # run from /backend
from app.elexon_client import fetch_actual_wind, fetch_wind_forecast

DATA_DIR = Path("data")
CHUNK_DAYS = 7

ACTUALS_RANGE = (date(2026, 1, 1), date(2026, 2, 1))
FORECAST_PUBLISH_RANGE = (date(2025, 12, 30), date(2026, 1, 31))


def date_chunks(start: date, end: date, days: int):
    """Yield inclusive (start, end) ISO date strings in chunks."""
    cur = start
    while cur <= end:
        chunk_end = min(cur + timedelta(days=days - 1), end)
        yield cur.isoformat(), chunk_end.isoformat()
        cur = chunk_end + timedelta(days=1)


def fetch_all(fetch_fn, date_range) -> pd.DataFrame:
    frames = [fetch_fn(s, e) for s, e in date_chunks(*date_range, CHUNK_DAYS)]
    return pd.concat(frames, ignore_index=True).drop_duplicates()


def main():
    DATA_DIR.mkdir(exist_ok=True)

    actuals = fetch_all(fetch_actual_wind, ACTUALS_RANGE)
    forecasts = fetch_all(fetch_wind_forecast, FORECAST_PUBLISH_RANGE)

    actuals.to_csv(DATA_DIR / "actuals.csv", index=False)
    forecasts.to_csv(DATA_DIR / "forecasts.csv", index=False)

    print("\n===== SUMMARY =====")
    print("ACTUALS columns:", list(actuals.columns))
    print("ACTUALS rows:", len(actuals), "(expected 32 days x 48 = 1536)")
    print("ACTUALS startTime range:", actuals["startTime"].min(), "->", actuals["startTime"].max())
    print("ACTUALS nulls:\n", actuals.isna().sum())

    print("\nFORECASTS columns:", list(forecasts.columns))
    print("FORECASTS rows:", len(forecasts))
    print("FORECASTS publishTime range:", forecasts["publishTime"].min(), "->", forecasts["publishTime"].max())
    print("FORECASTS startTime range:", forecasts["startTime"].min(), "->", forecasts["startTime"].max())
    print("FORECASTS nulls:\n", forecasts.isna().sum())
    print("Duplicate (startTime, publishTime):",
          forecasts.duplicated(subset=["startTime", "publishTime"]).sum())


if __name__ == "__main__":
    main()