from pathlib import Path
import shutil
import tempfile
from zipfile import ZipFile

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .config import METADATA_DIR, PROCESSED_DIR, RAW_DIR, REPORT_DIR
from .data_cleaning import clean_trips, write_report
from .data_loader import (
    download_month,
    download_processed_bundle,
    download_zone_lookup,
    update_manifest,
)

SAMPLE_YEAR = 2025
SAMPLE_MONTH = 1
SAMPLE_BATCH_SIZE = 25_000


def bootstrap_data(year: int = SAMPLE_YEAR, month: int = SAMPLE_MONTH) -> Path:
    output = PROCESSED_DIR / f"yellow_tripdata_{year}-{month:02d}.parquet"
    bundle_path = RAW_DIR / "urban-mobility-data.zip"
    if download_processed_bundle(year, month, bundle_path):
        try:
            with tempfile.TemporaryDirectory(dir=PROCESSED_DIR) as temporary_dir:
                temporary_root = Path(temporary_dir)
                expected_files = {
                    f"processed/{output.name}": output,
                    "metadata/manifest.json": METADATA_DIR / "manifest.json",
                    f"reports/{output.stem}.json": REPORT_DIR / f"{output.stem}.json",
                }
                with ZipFile(bundle_path) as bundle:
                    members = set(bundle.namelist())
                    dataset_member = f"processed/{output.name}"
                    if dataset_member not in members:
                        raise ValueError(
                            f"Prepared data bundle is missing {dataset_member}."
                        )

                    staged_files = []
                    for member, target in expected_files.items():
                        if member not in members:
                            continue
                        staged = temporary_root / member
                        staged.parent.mkdir(parents=True, exist_ok=True)
                        with bundle.open(member) as source, staged.open("wb") as destination:
                            shutil.copyfileobj(source, destination)
                        staged_files.append((staged, target))

                staged_dataset = next(
                    staged
                    for staged, target in staged_files
                    if target == output
                )
                metadata = pq.read_metadata(staged_dataset)
                if metadata.num_rows == 0:
                    raise ValueError("Prepared data bundle contains no trips.")

                for staged, target in staged_files:
                    if target == output:
                        continue
                    target.parent.mkdir(parents=True, exist_ok=True)
                    staged.replace(target)
                output.parent.mkdir(parents=True, exist_ok=True)
                staged_dataset.replace(output)
            return output
        finally:
            bundle_path.unlink(missing_ok=True)

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
    reports = []
    input_rows = 0
    writer = None

    try:
        for batch in pq.ParquetFile(source).iter_batches(batch_size=SAMPLE_BATCH_SIZE):
            frame = batch.to_pandas()
            input_rows += len(frame)
            cleaned, report = clean_trips(frame)
            for location_column, name_column in (
                ("pickup_location_id", "pickup_zone_name"),
                ("dropoff_location_id", "dropoff_zone_name"),
            ):
                if location_column in cleaned:
                    cleaned[name_column] = cleaned[location_column].map(zone_names).astype("string")
            reports.append(report)
            if cleaned.empty:
                continue

            table = pa.Table.from_pandas(cleaned, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(
                    temporary_output,
                    table.schema,
                    compression="zstd",
                    compression_level=6,
                )
            else:
                table = table.cast(writer.schema)
            writer.write_table(table)

        if writer is None:
            raise ValueError(f"No valid trips found in the {input_rows:,} source rows.")
        writer.close()
        writer = None
        if record.get("rows") is not None and input_rows != record["rows"]:
            raise ValueError(
                f"Processed {input_rows:,} rows, but the source manifest reports "
                f"{record['rows']:,} rows."
            )
        temporary_output.replace(output)
    except Exception:
        if writer is not None:
            writer.close()
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
    summary["sample"] = False
    summary["source_rows_processed"] = input_rows
    write_report(summary, REPORT_DIR / f"{Path(record['filename']).stem}.json")

    record["dashboard_processed_rows"] = input_rows
    update_manifest([record])
    return output
