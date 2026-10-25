from datetime import date, time

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from app.data_store import get_actuals_hourly, get_forecasts
from app.metrics import build_comparison, compute_metrics, metrics_by_day, metrics_by_horizon
from app.processing import select_forecast_for_day, select_forecasts_for_period

router = APIRouter(prefix="/api")

MIN_DATE = date(2026, 1, 1)
MAX_DATE = date(2026, 1, 31)
DEFAULT_CUTOFF = time(9, 0)


def _validate_dates(*dates: date) -> None:
    for d in dates:
        if not MIN_DATE <= d <= MAX_DATE:
            raise HTTPException(422, f"Date {d} outside supported range {MIN_DATE} to {MAX_DATE}")


def _records(df: pd.DataFrame) -> list[dict]:
    """DataFrame -> JSON-safe list of dicts (NaN -> None, timestamps -> ISO strings)."""
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out.astype(object).where(pd.notna(out), None).to_dict("records")


@router.get("/forecast")
def forecast_for_day(
    date: date = Query(..., description="Delivery date, e.g. 2026-01-10"),
    cutoff: time = Query(DEFAULT_CUTOFF, description="Decision time on D-1 (UK time), HH:MM"),
):
    _validate_dates(date)
    selected = select_forecast_for_day(get_forecasts(), date, cutoff)
    merged = selected.merge(get_actuals_hourly(), on="startTime", how="left")
    merged["error_mw"] = merged["forecast_mw"] - merged["actual_mw"]
    cols = ["startTime", "forecast_mw", "actual_mw", "error_mw", "publishTime", "horizon_h"]
    return {
        "delivery_date": str(date),
        "cutoff_time": str(cutoff),
        "cutoff_utc": merged["cutoff"].iloc[0].strftime("%Y-%m-%dT%H:%M:%SZ") if len(merged) else None,
        "data": _records(merged[cols]),
    }


@router.get("/metrics")
def metrics(
    start: date = Query(MIN_DATE),
    end: date = Query(MAX_DATE),
    cutoff: time = Query(DEFAULT_CUTOFF),
):
    _validate_dates(start, end)
    if start > end:
        raise HTTPException(422, "start must be <= end")
    selected = select_forecasts_for_period(get_forecasts(), start, end, cutoff)
    cmp = build_comparison(selected, get_actuals_hourly())
    by_day = metrics_by_day(cmp)
    by_day["date"] = by_day["date"].astype(str)
    return {
        "start": str(start),
        "end": str(end),
        "cutoff_time": str(cutoff),
        "overall": compute_metrics(cmp),
        "by_day": _records(by_day),
    }


@router.get("/metrics/horizon")
def horizon_metrics():
    df = metrics_by_horizon(get_forecasts(), get_actuals_hourly())
    return {"data": _records(df)}