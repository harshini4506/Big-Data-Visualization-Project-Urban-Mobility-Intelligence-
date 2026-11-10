import pandas as pd
from src.forecasting import prepare_hourly
def test_hourly_series_has_lags_and_fills_gaps():
    frame = pd.DataFrame({"pickup_datetime": pd.date_range("2025-01-01", periods=30, freq="h")})
    result = prepare_hourly(frame)
    assert {"lag_1", "lag_24", "hour", "weekday"}.issubset(result.columns)

