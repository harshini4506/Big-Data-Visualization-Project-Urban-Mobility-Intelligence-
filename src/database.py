from pathlib import Path
from .config import PROCESSED_DIR, RAW_DIR

def parquet_glob(directory: Path = PROCESSED_DIR) -> str:
    files = sorted(directory.glob("*.parquet"))
    if not files:
        raise FileNotFoundError(f"No processed Parquet files found in {directory}")
    return str(directory / "*.parquet").replace("\\", "/")

def connect():
    import duckdb
    return duckdb.connect(":memory:")

def relation_sql(directory: Path = PROCESSED_DIR) -> str:
    return f"read_parquet('{parquet_glob(directory)}', union_by_name=true)"
