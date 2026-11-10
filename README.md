# Urban Mobility Intelligence Dashboard

An interactive, multi-page Streamlit dashboard for analyzing official [NYC TLC trip-record data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page). DuckDB queries Parquet files directly, so the application can work with millions of rows without loading the complete dataset into Pandas.

## Features

- Incremental yellow-taxi Parquet downloads with a manifest and schema inspection.
- Configurable cleaning and validation reports while preserving raw files.
- Interactive line, bar, donut, histogram, scatter, box, and heatmap visualizations across overview, geographic, time, fare, route, and forecast pages.
- Shared sidebar filters and bounded CSV exports across the Streamlit dashboard.
- Chronological random-forest demand forecasting with a previous-day baseline.

## Windows setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts\download_data.py --year 2025 --months 1
python scripts\inspect_dataset.py
python scripts\process_data.py
streamlit run app.py
pytest -q
```

The download command is incremental and skips readable files already present. TLC file availability can lag publication, so an HTTP 404 is reported and is not treated as an empty dataset. Raw data is intentionally ignored by Git.

The dependency constraints support Streamlit Community Cloud's current Python runtime, including binary PyArrow wheels for Python 3.14. Streamlit 1.52 or newer is required for compatibility with the PyArrow versions providing those wheels.

On a fresh deployment without processed data, choose **Load sample data** on the overview page. The app downloads the official January 2025 yellow-taxi file and prepares a bounded 100,000-row sample locally; the full raw file is not committed to the repository.

## Architecture

`app.py` is the Streamlit overview and `pages/` contains the rest of the Streamlit dashboard. `scripts/download_data.py` downloads documented monthly TLC files. `src/data_cleaning.py` normalizes column names and applies explicit validity rules. `src/database.py` discovers processed Parquet files and queries them with DuckDB. All dashboard pages use `src/filters.py`, `src/queries.py`, and `src/visualizations.py`; there is no separate Flask application.

The canonical TLC yellow-taxi fields are mapped to a stable internal schema where available: pickup/drop-off timestamps, location IDs, passenger count, distance, fare, tip, tolls, total, and payment type. Missing optional fields disable only the affected metric.

## Data processing

```powershell
python scripts/inspect_dataset.py --path data/raw
python scripts/process_data.py --input data/raw --output data/processed
```

Processing writes normalized Parquet files and JSON reports under ignored directories. Use `--max-files` for a small verification run. Do not commit TLC data.

## Forecasting

The forecasting page trains on the currently filtered hourly series when enough observations exist. It uses a chronological 80/20 split, lag/calendar features, and reports MAE/RMSE against both the model and a previous-day baseline. It never displays forecasts when training data is insufficient.

## Limitations

Taxi-zone boundary GeoJSON is optional; without it the geographic page provides honest zone rankings rather than inventing coordinates. TLC schemas vary by vehicle type and year, so each file is validated independently. Forecasts are estimates and are not guarantees of future traffic.
