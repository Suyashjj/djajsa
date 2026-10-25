"""Forecast accuracy metrics. Error = forecast - actual (positive = over-forecast)."""
import numpy as np
import pandas as pd


def actuals_hourly(actuals: pd.DataFrame) -> pd.DataFrame:
    """Average the two half-hours into one hourly value (drops incomplete hours)."""
    df = actuals.copy()
    df["hour"] = df["startTime"].dt.floor("h")
    g = df.groupby("hour")["actual_mw"].agg(["mean", "count"]).reset_index()
    g = g[g["count"] == 2]
    return g.rename(columns={"hour": "startTime", "mean": "actual_mw"})[["startTime", "actual_mw"]]


def build_comparison(forecasts: pd.DataFrame, actuals_h: pd.DataFrame) -> pd.DataFrame:
    df = forecasts.merge(actuals_h, on="startTime", how="inner")
    df["error_mw"] = df["forecast_mw"] - df["actual_mw"]
    df["abs_error_mw"] = df["error_mw"].abs()
    return df


def compute_metrics(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"n": 0, "mae_mw": None, "rmse_mw": None, "bias_mw": None,
                "mape_pct": None, "p90_abs_error_mw": None}
    nonzero = df[df["actual_mw"] > 0]  # avoid dividing by zero in MAPE
    mape = (nonzero["abs_error_mw"] / nonzero["actual_mw"]).mean() * 100 if len(nonzero) else None
    return {
        "n": int(len(df)),
        "mae_mw": float(df["abs_error_mw"].mean()),
        "rmse_mw": float(np.sqrt((df["error_mw"] ** 2).mean())),
        "bias_mw": float(df["error_mw"].mean()),
        "mape_pct": None if mape is None else float(mape),
        "p90_abs_error_mw": float(df["abs_error_mw"].quantile(0.9)),
    }


def metrics_by_day(df: pd.DataFrame) -> pd.DataFrame:
    rows = [{"date": d, **compute_metrics(g)} for d, g in df.groupby(df["startTime"].dt.date)]
    return pd.DataFrame(rows)


def metrics_by_horizon(
    forecasts_all: pd.DataFrame, actuals_h: pd.DataFrame, bin_hours: int = 6, max_hours: int = 72
) -> pd.DataFrame:
    """Accuracy vs how far ahead the forecast was made (uses ALL forecast versions)."""
    df = build_comparison(forecasts_all, actuals_h)
    df["horizon_h"] = (df["startTime"] - df["publishTime"]).dt.total_seconds() / 3600
    df = df[(df["horizon_h"] >= 0) & (df["horizon_h"] < max_hours)]
    df["bin"] = (df["horizon_h"] // bin_hours * bin_hours).astype(int)
    rows = [{"horizon_from_h": b, "horizon_to_h": b + bin_hours, **compute_metrics(g)}
            for b, g in df.groupby("bin")]
    return pd.DataFrame(rows)