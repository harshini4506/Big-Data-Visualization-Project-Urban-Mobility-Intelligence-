import streamlit as st

from src.config import PROCESSED_DIR
from src.database import connect
from src.exports import csv_bytes
from src.filters import sidebar_filters
from src.queries import aggregate, kpis, query_frame
from src.ui import apply_theme, page_header
from src.visualizations import bar, donut, line, scatter

st.set_page_config(page_title="Urban Mobility Intelligence", layout="wide")
apply_theme()
page_header(
    "Urban Mobility Intelligence",
    "Explore NYC taxi demand, fares, distances, and routes with interactive charts.",
)

try:
    connection = connect()
    filters = sidebar_filters(connection)
    metrics = kpis(connection, filters)
except FileNotFoundError:
    st.warning(
        f"No processed Parquet files found in {PROCESSED_DIR}. "
        "Run the ingestion and processing commands in the README."
    )
    st.stop()

metric_labels = (
    ("Total trips", "total_trips", "{:,.0f}"),
    ("Total fare", "total_fare", "${:,.0f}"),
    ("Average fare", "average_fare", "${:,.2f}"),
    ("Average distance", "average_distance", "{:,.2f} mi"),
    ("Average duration", "average_duration", "{:,.2f} min"),
    ("Trips per day", "trips_per_day", "{:,.0f}"),
)
for row in (metric_labels[:3], metric_labels[3:]):
    columns = st.columns(3)
    for column, (label, key, format_string) in zip(columns, row):
        value = metrics[key]
        column.metric(
            label,
            "Unavailable" if value is None else format_string.format(value),
        )

daily = aggregate(connection, filters, "CAST(pickup_datetime AS DATE)", "")
hourly = aggregate(connection, filters, "EXTRACT(hour FROM pickup_datetime)", "")
zones = aggregate(connection, filters, "pickup_zone_name", "")
payments = aggregate(connection, filters, "payment_type", "")

if not daily.empty and not hourly.empty:
    busiest_day = daily.loc[daily["trips"].idxmax()]
    peak_hour = hourly.loc[hourly["trips"].idxmax()]
    st.subheader("At a glance")
    insight_columns = st.columns(3)
    insight_columns[0].info(
        f"**Busiest day**\n\n{busiest_day['period']:%b %d, %Y} · "
        f"{busiest_day['trips']:,.0f} trips"
    )
    insight_columns[1].info(
        f"**Peak pickup hour**\n\n{int(peak_hour['period']):02d}:00 · "
        f"{peak_hour['trips']:,.0f} trips"
    )
    insight_columns[2].info(
        f"**Active pickup zones**\n\n{zones['period'].nunique():,} zones"
    )

st.subheader("Demand overview")
left, right = st.columns(2)
with left:
    if daily.empty:
        st.info("No daily trip data matches the selected filters.")
    else:
        st.plotly_chart(
            line(daily, "period", "trips", "Daily trip volume"),
            use_container_width=True,
            theme=None,
        )
with right:
    if hourly.empty:
        st.info("No hourly trip data matches the selected filters.")
    else:
        st.plotly_chart(
            bar(hourly, "period", "trips", "Trips by pickup hour"),
            use_container_width=True,
            theme=None,
        )

st.subheader("Zones and payment")
left, right = st.columns(2)
with left:
    if zones.empty:
        st.info("No pickup-zone data matches the selected filters.")
    else:
        st.plotly_chart(
            bar(
                zones.nlargest(12, "trips").sort_values("trips"),
                "trips",
                "period",
                "Top pickup zones",
            ),
            use_container_width=True,
            theme=None,
        )
with right:
    if payments.empty:
        st.info("No payment data matches the selected filters.")
    else:
        st.plotly_chart(
            donut(payments, "period", "trips", "Payment mix"),
            use_container_width=True,
            theme=None,
        )

with st.expander("Explore fare and distance relationship"):
    trips = query_frame(
        connection,
        filters,
        "ORDER BY pickup_datetime DESC",
        10000,
    )
    if {"trip_distance", "fare_amount"}.issubset(trips.columns):
        fare_distance = trips.dropna(subset=["trip_distance", "fare_amount"])
        if fare_distance.empty:
            st.info("No fare and distance data matches the selected filters.")
        else:
            st.plotly_chart(
                scatter(
                    fare_distance,
                    "trip_distance",
                    "fare_amount",
                    "Fare versus trip distance (latest 10,000 trips)",
                ),
                use_container_width=True,
                theme=None,
            )
    else:
        st.info("Fare and distance fields are not available in the selected data.")

st.download_button(
    "Download daily summary",
    csv_bytes(daily),
    "daily_trips.csv",
    "text/csv",
)
