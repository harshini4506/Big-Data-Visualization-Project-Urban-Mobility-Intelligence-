import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from src import bootstrap


def test_bootstrap_writes_bounded_cleaned_sample_with_zone_names(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    metadata_dir = tmp_path / "metadata"
    report_dir = tmp_path / "reports"
    for directory in (raw_dir, processed_dir, metadata_dir, report_dir):
        directory.mkdir()

    source = raw_dir / "yellow_tripdata_2025-01.parquet"
    pq.write_table(
        pa.table(
            {
                "tpep_pickup_datetime": [
                    "2025-01-01 10:00:00",
                    "2025-01-01 10:01:00",
                    "2025-01-01 10:02:00",
                ],
                "tpep_dropoff_datetime": [
                    "2025-01-01 10:10:00",
                    "2025-01-01 10:11:00",
                    "2025-01-01 09:59:00",
                ],
                "PULocationID": [1, 2, 1],
                "DOLocationID": [2, 1, 2],
                "fare_amount": [10.0, 12.0, 3.0],
                "trip_distance": [1.0, 2.0, 1.0],
            }
        ),
        source,
    )
    lookup_path = metadata_dir / "taxi_zone_lookup.csv"
    pd.DataFrame(
        {
            "LocationID": [1, 2],
            "Zone": ["Zone One", "Zone Two"],
            "Borough": ["Manhattan", "Queens"],
        }
    ).to_csv(lookup_path, index=False)

    monkeypatch.setattr(bootstrap, "RAW_DIR", raw_dir)
    monkeypatch.setattr(bootstrap, "PROCESSED_DIR", processed_dir)
    monkeypatch.setattr(bootstrap, "METADATA_DIR", metadata_dir)
    monkeypatch.setattr(bootstrap, "REPORT_DIR", report_dir)
    monkeypatch.setattr(
        bootstrap,
        "download_month",
        lambda year, month: {
            "filename": source.name,
            "status": "existing",
            "rows": 3,
        },
    )
    monkeypatch.setattr(
        bootstrap,
        "download_zone_lookup",
        lambda path: lookup_path,
    )
    monkeypatch.setattr(bootstrap, "SAMPLE_BATCH_SIZE", 2)

    output = bootstrap.bootstrap_sample_data(max_rows=2)

    result = pd.read_parquet(output)
    assert len(result) == 2
    assert result["pickup_zone_name"].tolist() == [
        "Zone One (Manhattan)",
        "Zone Two (Queens)",
    ]
    assert result["trip_duration_minutes"].tolist() == [10.0, 10.0]
