import pandas as pd
import pytest

from app.metrics import actuals_hourly, compute_metrics


def test_actuals_hourly_averages_half_hours_and_drops_incomplete():
    actuals = pd.DataFrame({
        "startTime": pd.to_datetime(
            ["2026-01-01T12:00Z", "2026-01-01T12:30Z", "2026-01-01T13:00Z"], utc=True),
        "actual_mw": [100, 200, 999],  # 13:00 has no partner -> dropped
    })
    result = actuals_hourly(actuals)
    assert len(result) == 1
    assert result.loc[0, "actual_mw"] == 150


def test_symmetric_errors_have_zero_bias():
    df = pd.DataFrame({"actual_mw": [100, 100], "error_mw": [10, -10], "abs_error_mw": [10, 10]})
    m = compute_metrics(df)
    assert m["mae_mw"] == pytest.approx(10)
    assert m["rmse_mw"] == pytest.approx(10)
    assert m["bias_mw"] == pytest.approx(0)
    assert m["mape_pct"] == pytest.approx(10)


def test_over_forecast_gives_positive_bias():
    df = pd.DataFrame({"actual_mw": [100, 200], "error_mw": [20, 20], "abs_error_mw": [20, 20]})
    assert compute_metrics(df)["bias_mw"] == pytest.approx(20)