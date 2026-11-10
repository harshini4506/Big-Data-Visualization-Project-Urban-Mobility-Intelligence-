import pandas as pd
from src.schema_validation import validate_schema, normalize_frame
def test_tlc_schema_maps_columns():
    result = validate_schema(["tpep_pickup_datetime", "tpep_dropoff_datetime", "fare_amount"])
    assert result.valid
    assert result.mapped_columns["tpep_pickup_datetime"] == "pickup_datetime"
def test_normalize_frame():
    assert "pickup_datetime" in normalize_frame(pd.DataFrame({"tpep_pickup_datetime": []})).columns

