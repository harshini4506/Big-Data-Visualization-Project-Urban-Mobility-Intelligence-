import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data_loader import download_month, update_manifest

parser = argparse.ArgumentParser(description="Download official NYC TLC monthly Parquet files.")
parser.add_argument("--year", type=int, required=True)
parser.add_argument("--months", type=int, nargs="+", required=True)
parser.add_argument("--vehicle-type", choices=["yellow", "green"], default="yellow")
args = parser.parse_args()
records = []
for month in args.months:
    try:
        record = download_month(args.year, month, args.vehicle_type)
        print(f"{record['status']}: {record['filename']} ({record['rows']:,} rows)")
        records.append(record)
    except Exception as exc:
        print(f"FAILED {args.year}-{month:02d}: {exc}", file=sys.stderr)
update_manifest(records)

