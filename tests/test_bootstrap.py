import json
from io import BytesIO
from zipfile import ZipFile

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from src import bootstrap


def test_bootstrap_processes_all_batches_with_zone_names(tmp_path, monkeypatch):
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
    monkeypatch.setattr(bootstrap, "download_processed_bundle", lambda *args: False)
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

    output = bootstrap.bootstrap_data()

    result = pd.read_parquet(output)
    assert len(result) == 2
    assert result["pickup_zone_name"].tolist() == [
        "Zone One (Manhattan)",
        "Zone Two (Queens)",
    ]
    assert result["trip_duration_minutes"].tolist() == [10.0, 10.0]
    assert pq.read_metadata(output).row_group(0).column(0).compression == "ZSTD"
    report = json.loads((report_dir / f"{source.stem}.json").read_text(encoding="utf-8"))
    assert report["source_rows_processed"] == 3
    assert report["processed_rows"] == 2


def test_bootstrap_installs_prepared_bundle_without_processing(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    metadata_dir = tmp_path / "metadata"
    report_dir = tmp_path / "reports"
    for directory in (raw_dir, processed_dir, metadata_dir, report_dir):
        directory.mkdir()

    output = processed_dir / "yellow_tripdata_2025-01.parquet"
    dataset = pa.table(
        {
            "pickup_datetime": [pd.Timestamp("2025-01-01 10:00:00")],
            "dropoff_datetime": [pd.Timestamp("2025-01-01 10:10:00")],
        }
    )
    bundle_path = raw_dir / "urban-mobility-data.zip"

    def write_bundle(year, month, destination):
        parquet_bytes = BytesIO()
        pq.write_table(dataset, parquet_bytes)
        with ZipFile(destination, "w") as bundle:
            bundle.writestr(
                "processed/yellow_tripdata_2025-01.parquet",
                parquet_bytes.getvalue(),
            )
            bundle.writestr("metadata/manifest.json", "[]")
            bundle.writestr("reports/yellow_tripdata_2025-01.json", "{}")
        return True

    monkeypatch.setattr(bootstrap, "RAW_DIR", raw_dir)
    monkeypatch.setattr(bootstrap, "PROCESSED_DIR", processed_dir)
    monkeypatch.setattr(bootstrap, "METADATA_DIR", metadata_dir)
    monkeypatch.setattr(bootstrap, "REPORT_DIR", report_dir)
    monkeypatch.setattr(bootstrap, "download_processed_bundle", write_bundle)

    def fail_raw_download(*args):
        raise AssertionError("raw data should not be processed")

    monkeypatch.setattr(bootstrap, "download_month", fail_raw_download)

    installed = bootstrap.bootstrap_data()

    assert installed == output
    assert pq.read_table(output).num_rows == 1
    assert (metadata_dir / "manifest.json").read_text(encoding="utf-8") == "[]"
    assert (report_dir / f"{output.stem}.json").read_text(encoding="utf-8") == "{}"
    assert not bundle_path.exists()
