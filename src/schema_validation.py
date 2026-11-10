from dataclasses import dataclass
from typing import Iterable
import pandas as pd

ALIASES = {
    "tpep_pickup_datetime": "pickup_datetime",
    "lpep_pickup_datetime": "pickup_datetime",
    "tpep_dropoff_datetime": "dropoff_datetime",
    "lpep_dropoff_datetime": "dropoff_datetime",
    "pulocationid": "pickup_location_id",
    "dolocationid": "dropoff_location_id",
    "trip_distance": "trip_distance",
    "passenger_count": "passenger_count",
    "fare_amount": "fare_amount",
    "tip_amount": "tip_amount",
    "tolls_amount": "tolls_amount",
    "total_amount": "total_amount",
    "payment_type": "payment_type",
    "vendorid": "vendor_id",
}

@dataclass(frozen=True)
class SchemaResult:
    columns: tuple[str, ...]
    missing_required: tuple[str, ...]
    mapped_columns: dict[str, str]

    @property
    def valid(self) -> bool:
        return not self.missing_required

def normalize_columns(columns: Iterable[str]) -> dict[str, str]:
    return {
        str(column): ALIASES.get(
            str(column).lower().replace(" ", "_"),
            str(column).lower().replace(" ", "_"),
        )
        for column in columns
    }

def validate_schema(columns: Iterable[str], required: set[str] | None = None) -> SchemaResult:
    normalized = normalize_columns(columns)
    needed = required or {"pickup_datetime", "dropoff_datetime"}
    missing = tuple(sorted(needed - set(normalized.values())))
    return SchemaResult(tuple(normalized.values()), missing, normalized)

def normalize_frame(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.rename(columns=normalize_columns(frame.columns))
    result = result.loc[:, ~result.columns.duplicated()].copy()
    return result
