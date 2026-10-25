"""Forecast selection: what did the trader know at decision time?"""
from datetime import date, datetime, time
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
UK_TZ = "Europe/London"


def load_actuals(path: Path = DATA_DIR / "actuals.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df["startTime"] = pd.to_datetime(df["startTime"], utc=True)
    return df[["startTime", "generation"]].rename(columns={"generation": "actual_mw"})


def load_forecasts(path: Path = DATA_DIR / "forecasts.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ("startTime", "publishTime"):
        df[col] = pd.to_datetime(df[col], utc=True)
    return df[["startTime", "publishTime", "generation"]].rename(
        columns={"generation": "forecast_mw"}
    )


def decision_cutoff(delivery_date: date, cutoff_time: time = time(9, 0)) -> pd.Timestamp:
    """Decision moment: cutoff_time (UK local) on the day BEFORE delivery, in UTC."""
    local = pd.Timestamp(datetime.combine(delivery_date, cutoff_time)) - pd.Timedelta(days=1)
    return local.tz_localize(UK_TZ).tz_convert("UTC")


def select_forecast_for_day(
    forecasts: pd.DataFrame, delivery_date: date, cutoff_time: time = time(9, 0)
) -> pd.DataFrame:
    """For each target time on delivery_date, the latest forecast published <= cutoff."""
    cutoff = decision_cutoff(delivery_date, cutoff_time)
    day_start = pd.Timestamp(delivery_date).tz_localize(UK_TZ).tz_convert("UTC")
    day_end = (pd.Timestamp(delivery_date) + pd.Timedelta(days=1)).tz_localize(UK_TZ).tz_convert("UTC")

    known = forecasts[
        (forecasts["startTime"] >= day_start)
        & (forecasts["startTime"] < day_end)
        & (forecasts["publishTime"] <= cutoff)
    ]
    if known.empty:
        return known.assign(cutoff=pd.Series(dtype="datetime64[ns, UTC]"),
                            horizon_h=pd.Series(dtype="float"))

    latest = known.loc[known.groupby("startTime")["publishTime"].idxmax()]
    latest = latest.sort_values("startTime").reset_index(drop=True)
    latest["cutoff"] = cutoff
    latest["horizon_h"] = (latest["startTime"] - latest["publishTime"]).dt.total_seconds() / 3600
    return latest


def select_forecasts_for_period(
    forecasts: pd.DataFrame, start: date, end: date, cutoff_time: time = time(9, 0)
) -> pd.DataFrame:
    days = pd.date_range(start, end, freq="D")
    frames = [select_forecast_for_day(forecasts, d.date(), cutoff_time) for d in days]
    return pd.concat(frames, ignore_index=True)