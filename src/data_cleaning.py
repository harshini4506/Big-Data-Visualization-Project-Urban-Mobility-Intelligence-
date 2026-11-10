from datetime import datetime, timezone
from pathlib import Path
import json
import logging
import pandas as pd
from .schema_validation import normalize_frame, validate_schema

logger = logging.getLogger(__name__)

def clean_trips(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    original_rows = len(frame)
    data = normalize_frame(frame)
    schema = validate_schema(data.columns)
    if not schema.valid:
        raise ValueError(f"Missing required columns: {', '.join(schema.missing_required)}")
    for column in ("pickup_datetime", "dropoff_datetime"):
        data[column] = pd.to_datetime(data[column], errors="coerce")
    for column in ("trip_distance", "fare_amount", "tip_amount", "tolls_amount", "total_amount", "passenger_count"):
        if column in data:
            data[column] = pd.to_numeric(data[column], errors="coerce")
    duplicate_count = int(data.duplicated().sum())
    rules = {
        "missing_timestamp": int(data[["pickup_datetime", "dropoff_datetime"]].isna().any(axis=1).sum()),
        "non_positive_duration": 0,
        "negative_distance": int((data["trip_distance"] < 0).fillna(False).sum()) if "trip_distance" in data else 0,
        "negative_fare": int((data["fare_amount"] < 0).fillna(False).sum()) if "fare_amount" in data else 0,
        "invalid_passenger_count": int(((data["passenger_count"] < 0) | (data["passenger_count"] > 20)).fillna(False).sum()) if "passenger_count" in data else 0,
    }
    duration = data["dropoff_datetime"] - data["pickup_datetime"]
    rules["non_positive_duration"] = int((duration <= pd.Timedelta(0)).fillna(False).sum())
    invalid = data["pickup_datetime"].isna() | data["dropoff_datetime"].isna() | (duration <= pd.Timedelta(0))
    for column in ("trip_distance", "fare_amount", "passenger_count"):
        if column in data:
            invalid |= data[column].lt(0).fillna(False)
    cleaned = data.loc[~invalid].drop_duplicates().copy()
    cleaned["trip_duration_minutes"] = (cleaned["dropoff_datetime"] - cleaned["pickup_datetime"]).dt.total_seconds() / 60
    report = {
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "original_rows": original_rows,
        "processed_rows": len(cleaned),
        "accepted_rows": len(cleaned),
        "rejected_rows": original_rows - len(cleaned),
        "duplicate_rows": duplicate_count,
        "invalid_by_rule": rules,
        "missing_values": {str(k): int(v) for k, v in data.isna().sum().items()},
    }
    return cleaned, report

def write_report(report: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")

