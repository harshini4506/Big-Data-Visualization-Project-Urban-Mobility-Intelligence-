"""Download the official TLC taxi-zone lookup used for readable zone labels."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data_loader import download_zone_lookup

path = download_zone_lookup()
print(f"Downloaded official zone lookup to {path}")
