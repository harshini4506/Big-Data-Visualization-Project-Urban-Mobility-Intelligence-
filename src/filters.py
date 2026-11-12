from dataclasses import dataclass
from datetime import date
import pandas as pd
import streamlit as st
from .database import relation_sql

@dataclass(frozen=True)
class FilterState:
    start_date: date | None = None
    end_date: date | None = None
    pickup_zone: str | None = None
    dropoff_zone: str | None = None
    payment_type: str | None = None
    min_fare: float | None = None
    max_fare: float | None = None
    min_distance: float | None = None
    max_distance: float | None = None

def apply_frame_filters(frame: pd.DataFrame, state: FilterState) -> pd.DataFrame:
    result = frame
    if state.start_date and "pickup_datetime" in result:
        result = result[result["pickup_datetime"].dt.date >= state.start_date]
    if state.end_date and "pickup_datetime" in result:
        result = result[result["pickup_datetime"].dt.date <= state.end_date]
    for field, value in (("pickup_zone", state.pickup_zone), ("dropoff_zone", state.dropoff_zone), ("payment_type", state.payment_type)):
        if value and field in result:
            result = result[result[field].astype(str) == str(value)]
    for field, low, high in (("fare_amount", state.min_fare, state.max_fare), ("trip_distance", state.min_distance, state.max_distance)):
        if field in result:
            if low is not None: result = result[result[field] >= low]
            if high is not None: result = result[result[field] <= high]
    return result

def _safe_date_bounds(connection):
    bounds = connection.execute(
        "SELECT min(CAST(pickup_datetime AS DATE)), max(CAST(pickup_datetime AS DATE)) "
        f"FROM {relation_sql()}"
    ).fetchone()
    start, end = bounds or (None, None)
    if start is None or end is None:
        fallback = date.today()
        return fallback, fallback

    start = pd.to_datetime(start).date()
    end = pd.to_datetime(end).date()
    if start > end:
        start, end = end, start
    return start, end


def sidebar_filters(connection) -> dict:
    """Render filters from the currently available Parquet data."""
    start, end = _safe_date_bounds(connection)
    selected = st.sidebar.date_input("Date range", value=(start, end))

    if not isinstance(selected, tuple):
        dates = (selected, selected)
    else:
        dates = selected if len(selected) == 2 else (selected[0], selected[0])

    start_value = pd.to_datetime(dates[0]).date() if dates[0] is not None else start
    end_value = pd.to_datetime(dates[-1]).date() if dates[-1] is not None else end
    if start_value > end_value:
        start_value, end_value = end_value, start_value

    result = {"start": str(start_value), "end": str(pd.Timestamp(end_value) + pd.Timedelta(days=1))}
    for label, column, name_column, key in (
        ("Pickup zone", "pickup_location_id", "pickup_zone_name", "pickup_zone"),
        ("Drop-off zone", "dropoff_location_id", "dropoff_zone_name", "dropoff_zone"),
        ("Payment type", "payment_type", None, "payment_type"),
    ):
        if name_column:
            values = connection.execute(
                f"SELECT DISTINCT {column}, {name_column} FROM {relation_sql()} "
                f"WHERE {column} IS NOT NULL ORDER BY {name_column} LIMIT 500"
            ).fetchall()
            options = [None] + values
            result[key] = st.sidebar.selectbox(
                label,
                options,
                format_func=lambda value: "All" if value is None else str(value[1]),
            )
            result[key] = None if result[key] is None else result[key][0]
            continue
        values = connection.execute(
            f"SELECT DISTINCT {column} FROM {relation_sql()} "
            f"WHERE {column} IS NOT NULL ORDER BY 1 LIMIT 500"
        ).fetchall()
        options = [None] + [row[0] for row in values]
        result[key] = st.sidebar.selectbox(label, options, format_func=lambda value: "All" if value is None else str(value))
    result["min_fare"], result["max_fare"] = st.sidebar.slider("Fare range", 0.0, 500.0, (0.0, 500.0))
    result["min_distance"], result["max_distance"] = st.sidebar.slider("Distance range", 0.0, 100.0, (0.0, 100.0))
    return result
