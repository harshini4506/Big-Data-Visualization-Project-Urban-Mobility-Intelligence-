import pandas as pd
from src.data_cleaning import clean_trips
def test_cleaning_rejects_invalid_duration_and_negative_distance():
    frame = pd.DataFrame({"tpep_pickup_datetime": ["2025-01-01 10:00", "2025-01-01 10:00"], "tpep_dropoff_datetime": ["2025-01-01 10:10", "2025-01-01 09:59"], "trip_distance": [1.0, -2.0], "fare_amount": [10.0, 3.0]})
    cleaned, report = clean_trips(frame)
    assert len(cleaned) == 1
    assert report["rejected_rows"] == 1

