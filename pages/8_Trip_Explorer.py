import streamlit as st

from src.database import connect
from src.exports import csv_bytes
from src.filters import sidebar_filters
from src.queries import query_frame
from src.ui import apply_theme, page_header

st.set_page_config(page_title="Trip Explorer", layout="wide")
apply_theme()
page_header("Trip Explorer", "Inspect a bounded sample of trips matching the shared dashboard filters.")

try:
    connection = connect()
    filters = sidebar_filters(connection)
    rows = query_frame(
        connection,
        filters,
        "ORDER BY pickup_datetime DESC",
        5000,
    )
except FileNotFoundError:
    st.warning("No processed Parquet files found. Run the ingestion and processing commands in the README.")
    st.stop()

st.caption("The explorer is limited to the latest 5,000 matching trips to keep the interface responsive.")
if rows.empty:
    st.info("No trips match the current filters.")
else:
    columns = [
        column
        for column in (
            "pickup_datetime",
            "dropoff_datetime",
            "pickup_zone_name",
            "dropoff_zone_name",
            "passenger_count",
            "trip_distance",
            "trip_duration_minutes",
            "fare_amount",
            "tip_amount",
            "total_amount",
            "payment_type",
        )
        if column in rows.columns
    ]
    visible = rows[columns]
    st.dataframe(visible, use_container_width=True, hide_index=True)
    st.download_button(
        "Download matching trip sample",
        csv_bytes(visible),
        "filtered_trip_sample.csv",
        "text/csv",
    )
