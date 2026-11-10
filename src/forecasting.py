import numpy as np
import pandas as pd

FEATURES = ["lag_1", "lag_24", "hour", "weekday"]

def prepare_hourly(frame: pd.DataFrame) -> pd.DataFrame:
    series = frame.set_index("pickup_datetime").resample("h").size().rename("trips").asfreq("h", fill_value=0).to_frame()
    series["lag_1"] = series["trips"].shift(1)
    series["lag_24"] = series["trips"].shift(24)
    series["hour"] = series.index.hour
    series["weekday"] = series.index.dayofweek
    return series.dropna()

def train_forecast(frame: pd.DataFrame, test_fraction: float = .2) -> dict:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    data = prepare_hourly(frame)
    if len(data) < 48:
        raise ValueError("At least 48 hourly observations are required for forecasting.")
    split = max(1, int(len(data) * (1 - test_fraction)))
    train, test = data.iloc[:split], data.iloc[split:]
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(train[FEATURES], train["trips"])
    prediction = model.predict(test[FEATURES])
    baseline = test["lag_24"].to_numpy()
    return {
        "model": model, "timestamps": test.index, "actual": test["trips"].to_numpy(),
        "predicted": prediction, "mae": mean_absolute_error(test["trips"], prediction),
        "rmse": mean_squared_error(test["trips"], prediction) ** .5,
        "baseline_mae": mean_absolute_error(test["trips"], baseline),
    }
