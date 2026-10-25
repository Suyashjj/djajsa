from datetime import date

import pandas as pd

from app.processing import select_forecast_for_day


def test_picks_latest_forecast_before_cutoff():
    # Delivery 2026-01-10, cutoff = 2026-01-09 09:00 UTC
    forecasts = pd.DataFrame({
        "startTime": pd.to_datetime(["2026-01-10T12:00Z"] * 4, utc=True),
        "publishTime": pd.to_datetime(
            ["2026-01-09T08:00Z", "2026-01-09T08:30Z",   # known at cutoff
             "2026-01-09T09:30Z", "2026-01-10T06:00Z"],  # after cutoff: must be ignored
            utc=True),
        "forecast_mw": [100, 110, 200, 300],
    })
    result = select_forecast_for_day(forecasts, date(2026, 1, 10))
    assert len(result) == 1
    assert result.loc[0, "forecast_mw"] == 110