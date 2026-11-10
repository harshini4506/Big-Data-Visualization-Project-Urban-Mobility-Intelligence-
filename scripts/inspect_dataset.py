import argparse
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pyarrow.parquet as pq
from src.schema_validation import validate_schema
parser = argparse.ArgumentParser()
parser.add_argument("--path", type=Path, default=Path("data/raw"))
args = parser.parse_args()
results = []
for file in sorted(args.path.glob("*.parquet")):
    metadata = pq.read_metadata(file)
    result = validate_schema(metadata.schema.names)
    results.append({"filename": file.name, "rows": metadata.num_rows, "columns": list(metadata.schema.names), "valid": result.valid, "missing_required": result.missing_required})
print(json.dumps(results, indent=2))

