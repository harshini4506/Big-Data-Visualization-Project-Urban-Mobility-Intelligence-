import argparse
from pathlib import Path
import pandas as pd
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import REPORT_DIR
from src.data_cleaning import clean_trips, write_report
parser = argparse.ArgumentParser()
parser.add_argument("--input", type=Path, default=Path("data/raw"))
parser.add_argument("--output", type=Path, default=Path("data/processed"))
parser.add_argument("--max-files", type=int)
args = parser.parse_args()
files = sorted(args.input.glob("*.parquet"))
if args.max_files: files = files[:args.max_files]
if not files: raise SystemExit(f"No Parquet files found in {args.input}")
lookup_path = Path("data/metadata/taxi_zone_lookup.csv")
lookup = pd.read_csv(lookup_path) if lookup_path.exists() else None
for source in files:
    cleaned, report = clean_trips(pd.read_parquet(source))
    if lookup is not None:
        labels = lookup.assign(
            zone_name=lambda frame: frame["Zone"].astype(str) + " (" + frame["Borough"].astype(str) + ")"
        )[["LocationID", "zone_name"]]
        for location_column, name_column in (
            ("pickup_location_id", "pickup_zone_name"),
            ("dropoff_location_id", "dropoff_zone_name"),
        ):
            if location_column in cleaned:
                cleaned = cleaned.merge(
                    labels.rename(columns={"LocationID": location_column, "zone_name": name_column}),
                    on=location_column,
                    how="left",
                )
    target = args.output / source.name
    args.output.mkdir(parents=True, exist_ok=True)
    cleaned.to_parquet(target, index=False, compression="zstd", compression_level=6)
    write_report(report, REPORT_DIR / f"{source.stem}.json")
    print(f"processed {source.name}: {report['processed_rows']:,} accepted / {report['original_rows']:,} input")
