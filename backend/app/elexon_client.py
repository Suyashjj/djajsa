import requests
import pandas as pd

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"


def _get(endpoint: str, params: dict) -> pd.DataFrame:
    url = f"{BASE_URL}{endpoint}"
    resp = requests.get(url, params=params, timeout=60)
    print(f"GET {resp.url}\n -> status {resp.status_code}")
    resp.raise_for_status()
    payload = resp.json()
    # stream endpoints usually return a plain list; others wrap it in {"data": [...]}
    rows = payload["data"] if isinstance(payload, dict) and "data" in payload else payload
    return pd.DataFrame(rows)


def fetch_actual_wind(start: str, end: str) -> pd.DataFrame:
    """FUELHH: actual generation, WIND only. Dates as YYYY-MM-DD."""
    return _get(
        "/datasets/FUELHH/stream",
        {"settlementDateFrom": start, "settlementDateTo": end, "fuelType": "WIND"},
    )


def fetch_wind_forecast(start: str, end: str) -> pd.DataFrame:
    """WINDFOR: forecasts, filtered by when they were published."""
    return _get(
        "/datasets/WINDFOR/stream",
        {"publishDateTimeFrom": f"{start}T00:00:00Z", "publishDateTimeTo": f"{end}T23:59:59Z"},
    )