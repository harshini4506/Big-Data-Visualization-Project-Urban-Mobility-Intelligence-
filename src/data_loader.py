from pathlib import Path
import json
import logging
import requests
import pyarrow.parquet as pq
from .config import RAW_DIR, METADATA_DIR

logger = logging.getLogger(__name__)

def tlc_url(year: int, month: int, vehicle_type: str = "yellow") -> str:
    if not 1 <= month <= 12:
        raise ValueError("month must be between 1 and 12")
    if vehicle_type not in {"yellow", "green"}:
        raise ValueError("vehicle_type must be yellow or green")
    prefix = "yellow" if vehicle_type == "yellow" else "green"
    return f"https://d37ci6vzurychx.cloudfront.net/trip-data/{prefix}_tripdata_{year}-{month:02d}.parquet"

def download_month(year: int, month: int, vehicle_type: str = "yellow", output_dir: Path = RAW_DIR) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    url = tlc_url(year, month, vehicle_type)
    destination = output_dir / Path(url).name
    if destination.exists():
        try:
            metadata = pq.read_metadata(destination)
            return {"filename": destination.name, "url": url, "status": "existing", "size": destination.stat().st_size, "rows": metadata.num_rows}
        except Exception as exc:
            logger.warning("Existing file is unreadable; redownloading %s: %s", destination, exc)
    temporary = destination.with_suffix(".part")
    try:
        with requests.get(url, stream=True, timeout=(15, 120)) as response:
            response.raise_for_status()
            with temporary.open("wb") as target:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        target.write(chunk)
        metadata = pq.read_metadata(temporary)
        temporary.replace(destination)
        return {"filename": destination.name, "url": url, "status": "downloaded", "size": destination.stat().st_size, "rows": metadata.num_rows}
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise

def update_manifest(records: list[dict], path: Path = METADATA_DIR / "manifest.json") -> None:
    existing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    by_name = {record["filename"]: record for record in existing}
    for record in records:
        by_name[record["filename"]] = record
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(list(by_name.values()), indent=2), encoding="utf-8")

def download_zone_lookup(path: Path = METADATA_DIR / "taxi_zone_lookup.csv") -> Path:
    url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=(15, 60))
    response.raise_for_status()
    temporary = path.with_suffix(".part")
    temporary.write_bytes(response.content)
    temporary.replace(path)
    return path
