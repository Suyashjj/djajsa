"""Loads the CSV data once and keeps it in memory."""
from functools import lru_cache

import pandas as pd

from app.metrics import actuals_hourly
from app.processing import load_actuals, load_forecasts


@lru_cache(maxsize=1)
def get_forecasts() -> pd.DataFrame:
    return load_forecasts()


@lru_cache(maxsize=1)
def get_actuals_hourly() -> pd.DataFrame:
    return actuals_hourly(load_actuals())