# Urban Mobility Intelligence Dashboard

An interactive, multi-page Streamlit dashboard for analyzing official [NYC TLC trip-record data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page). DuckDB queries Parquet files directly, so the application can work with millions of rows without loading the complete dataset into Pandas.

## Features

- Incremental yellow-taxi Parquet downloads with a manifest and schema inspection.
- Configurable cleaning and validation reports while preserving raw files.
- Interactive line, bar, donut, histogram, scatter, box, and heatmap visualizations across overview, geographic, time, fare, route, and forecast pages.
- Shared sidebar filters and bounded CSV exports across the Streamlit dashboard.
- Chronological random-forest demand forecasting with a previous-day baseline.
- Live New York weather context, refreshed every 10 minutes while the dashboard is open.
- GitHub Actions weather snapshots every 10 minutes, committed only when the observation changes.

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

On a fresh deployment without processed data, select **Load January 2025 data** on the overview page. The app first downloads the preprocessed January dataset from the latest GitHub Release, avoiding the slow download-and-clean path after Streamlit Cloud restarts. The release is built automatically by the `Publish prepared dashboard data` GitHub Actions workflow and contains Zstandard-compressed Parquet data plus its manifest and quality report. Ensure GitHub Actions is enabled; after pushing the workflow, wait for its first run to finish. You can also start it from **Actions → Publish prepared dashboard data → Run workflow**. If no release asset exists yet, the app falls back to downloading and processing the official TLC file; this initial fallback may take several minutes. Use **Retry loading data** if loading fails. The raw and processed datasets are not committed to Git history.

The overview also displays current New York weather from Open-Meteo, including temperature, conditions, relative humidity, and wind speed, and refreshes it every 10 minutes while a viewer has the page open. A separate GitHub Actions workflow polls every 10 minutes and commits `data/live_weather.json` only when the observed weather changes; the Streamlit app uses that saved snapshot if the API is unavailable. The API observation itself may update less often than 10 minutes. GitHub scheduled jobs can be delayed, and repository updates may trigger a Streamlit redeploy, but neither guarantees that Streamlit Cloud stays awake when nobody is viewing the app. This live weather context does not turn the historical TLC trips into a live feed.

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
