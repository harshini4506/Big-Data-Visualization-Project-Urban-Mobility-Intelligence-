from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from .config import METADATA_DIR, PROCESSED_DIR, RAW_DIR, REPORT_DIR
from .data_cleaning import clean_trips, write_report
from .data_loader import download_month, download_zone_lookup, update_manifest

SAMPLE_YEAR = 2025
SAMPLE_MONTH = 1
SAMPLE_ROW_LIMIT = 100_000
SAMPLE_BATCH_SIZE = 25_000


def bootstrap_sample_data(
    max_rows: int = SAMPLE_ROW_LIMIT,
    year: int = SAMPLE_YEAR,
    month: int = SAMPLE_MONTH,
) -> Path:
    record = download_month(year, month)
    source = RAW_DIR / record["filename"]
    lookup_path = download_zone_lookup(METADATA_DIR / "taxi_zone_lookup.csv")
    lookup = pd.read_csv(lookup_path)
    zone_names = lookup.assign(
        zone_name=lambda frame: frame["Zone"].astype(str)
        + " ("
        + frame["Borough"].astype(str)
        + ")"
    ).set_index("LocationID")["zone_name"]

    output = PROCESSED_DIR / record["filename"]
    temporary_output = output.with_suffix(".parquet.part")
    chunks = []
    reports = []
    input_rows = 0

    for batch in pq.ParquetFile(source).iter_batches(batch_size=SAMPLE_BATCH_SIZE):
        remaining = max_rows - input_rows
        if remaining <= 0:
            break
        frame = batch.slice(0, remaining).to_pandas()
        input_rows += len(frame)
        cleaned, report = clean_trips(frame)
        for location_column, name_column in (
            ("pickup_location_id", "pickup_zone_name"),
            ("dropoff_location_id", "dropoff_zone_name"),
        ):
            if location_column in cleaned:
                cleaned[name_column] = cleaned[location_column].map(zone_names)
        if not cleaned.empty:
            chunks.append(cleaned)
        reports.append(report)

    if not chunks:
        raise ValueError(f"No valid trips found in the first {input_rows:,} source rows.")

    try:
        pd.concat(chunks, ignore_index=True).to_parquet(temporary_output, index=False)
        temporary_output.replace(output)
    except Exception:
        temporary_output.unlink(missing_ok=True)
        raise

    summary = reports[0]
    summary["original_rows"] = sum(report["original_rows"] for report in reports)
    summary["processed_rows"] = sum(report["processed_rows"] for report in reports)
    summary["accepted_rows"] = summary["processed_rows"]
    summary["rejected_rows"] = sum(report["rejected_rows"] for report in reports)
    summary["duplicate_rows"] = sum(report["duplicate_rows"] for report in reports)
    for rule in summary["invalid_by_rule"]:
        summary["invalid_by_rule"][rule] = sum(
            report["invalid_by_rule"][rule] for report in reports
        )
    for column in summary["missing_values"]:
        summary["missing_values"][column] = sum(
            report["missing_values"][column] for report in reports
        )
    summary["sample"] = True
    summary["source_rows_limited_to"] = max_rows
    write_report(summary, REPORT_DIR / f"{Path(record['filename']).stem}.json")

    record["dashboard_sample_rows"] = input_rows
    update_manifest([record])
    return output
