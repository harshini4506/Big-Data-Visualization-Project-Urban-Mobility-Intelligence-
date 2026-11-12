import requests
import streamlit as st

from src.config import PROCESSED_DIR
from src.bootstrap import bootstrap_data
from src.database import connect
from src.exports import csv_bytes
from src.filters import sidebar_filters
from src.live_weather import (
    fetch_current_weather,
    load_weather_snapshot,
    weather_description,
)
from src.queries import aggregate, grouped_metrics, kpis, query_frame
from src.ui import apply_theme, page_header
from src.visualizations import bar, box, donut, heatmap, histogram, line, scatter

st.set_page_config(page_title="Urban Mobility Intelligence", layout="wide")
apply_theme()
page_header(
    "Urban Mobility Intelligence",
    "Explore NYC taxi demand, fares, distances, and routes with interactive charts.",
)

@st.cache_data(ttl=600, show_spinner=False)
def _cached_current_weather() -> dict[str, object]:
    try:
        weather = fetch_current_weather()
    except (requests.RequestException, ValueError):
        weather = load_weather_snapshot()
        weather["is_saved_snapshot"] = True
        return weather
    weather["is_saved_snapshot"] = False
    return weather


@st.fragment(run_every="10m")
def live_weather() -> None:
    st.subheader("Live New York weather")
    try:
        weather = _cached_current_weather()
    except (requests.RequestException, ValueError) as exc:
        st.warning(f"Current weather is temporarily unavailable: {exc}")
        return

    columns = st.columns(4)
    columns[0].metric("Temperature", f"{weather['temperature_c']:.1f} °C")
    columns[1].metric(
        "Conditions",
        weather_description(weather["weather_code"]),
    )
    columns[2].metric("Precipitation", f"{weather['precipitation_mm']:.1f} mm")
    columns[3].metric("Wind", f"{weather['wind_speed_kmh']:.1f} km/h")
    observed_at = weather["observed_at"]
    source = "saved GitHub snapshot" if weather["is_saved_snapshot"] else "Open-Meteo"
    st.caption(
        f"{source} · observed {observed_at:%b %d, %Y %I:%M %p} New York time · "
        "refreshes every 10 minutes while this page is open; GitHub polls every 10 minutes"
    )


if not any(PROCESSED_DIR.glob("*.parquet")):
    st.info(
        "Trip data is not available yet. Load January 2025 TLC data to enable "
        "the dashboard. The initial download and processing may take several minutes."
    )
    if "data_load_error" in st.session_state:
        st.error(f"Could not load NYC TLC trip data: {st.session_state.data_load_error}")

    button_label = (
        "Retry loading data"
        if "data_load_error" in st.session_state
        else "Load January 2025 data"
    )
    if st.button(button_label, type="primary"):
        try:
            with st.spinner(
                "Loading all January 2025 NYC TLC trip data. "
                "This may take several minutes..."
            ):
                bootstrap_data()
        except Exception as exc:
            st.session_state.data_load_error = str(exc)
            st.rerun()
        else:
            st.session_state.pop("data_load_error", None)
            st.rerun()

    st.stop()

live_weather()

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
hourly_weekday = grouped_metrics(
    connection,
    filters,
    "EXTRACT(hour FROM pickup_datetime) AS hour, "
    "DAYOFWEEK(pickup_datetime) AS dayofweek",
    "count(*) AS trips",
)
trips = query_frame(
    connection,
    filters,
    "ORDER BY pickup_datetime DESC",
    10000,
)

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

st.subheader("Patterns across time and trip characteristics")
st.caption(
    "The heatmap uses all trips matching the filters. Distribution and box plots "
    "use the latest 10,000 matching trips to keep the overview responsive."
)
if hourly_weekday.empty:
    st.info("No weekday and hour data matches the selected filters.")
else:
    weekday_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    hourly_weekday["dayofweek"] = hourly_weekday["dayofweek"].astype(int)
    figure = heatmap(
        hourly_weekday,
        "hour",
        "dayofweek",
        "trips",
        "Trip volume by pickup hour and weekday",
    )
    figure.update_yaxes(
        tickmode="array",
        tickvals=list(range(7)),
        ticktext=weekday_names,
        autorange="reversed",
    )
    st.plotly_chart(figure, use_container_width=True, theme=None)

fare_trips = (
    trips.dropna(subset=["fare_amount"])
    if "fare_amount" in trips.columns
    else trips.iloc[0:0]
)
distance_trips = (
    trips.dropna(subset=["trip_distance"])
    if "trip_distance" in trips.columns
    else trips.iloc[0:0]
)
left, right = st.columns(2)
with left:
    if fare_trips.empty:
        st.info("No fare data matches the selected filters.")
    else:
        st.plotly_chart(
            histogram(fare_trips, "fare_amount", "Fare distribution"),
            use_container_width=True,
            theme=None,
        )
with right:
    if distance_trips.empty:
        st.info("No trip-distance data matches the selected filters.")
    else:
        st.plotly_chart(
            histogram(distance_trips, "trip_distance", "Trip-distance distribution"),
            use_container_width=True,
            theme=None,
        )

if {"payment_type", "total_amount"}.issubset(trips.columns):
    payment_amounts = trips.dropna(subset=["payment_type", "total_amount"])
    if payment_amounts.empty:
        st.info("No payment and total-amount data matches the selected filters.")
    else:
        st.plotly_chart(
            box(
                payment_amounts,
                "payment_type",
                "total_amount",
                "Trip total by payment type",
            ),
            use_container_width=True,
            theme=None,
        )

with st.expander("Explore fare and distance relationship"):
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
