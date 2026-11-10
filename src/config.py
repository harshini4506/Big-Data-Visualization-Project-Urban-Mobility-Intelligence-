from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
METADATA_DIR = ROOT / "data" / "metadata"
REPORT_DIR = ROOT / "reports"
MODEL_DIR = ROOT / "models"
LOG_DIR = ROOT / "logs"
TLC_PAGE = "https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page"
DEFAULT_MAX_EXPORT_ROWS = 100_000
REQUIRED_COLUMNS = {"pickup_datetime", "dropoff_datetime"}
for directory in (RAW_DIR, PROCESSED_DIR, METADATA_DIR, REPORT_DIR, MODEL_DIR, LOG_DIR):
    directory.mkdir(parents=True, exist_ok=True)

