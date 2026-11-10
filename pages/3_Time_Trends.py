import streamlit as st
from src.database import connect
from src.queries import aggregate, grouped_metrics
from src.visualizations import line, bar, heatmap
from src.filters import sidebar_filters
from src.ui import apply_theme, page_header
st.set_page_config(page_title="Time Trends", layout="wide")
apply_theme()
page_header("Time and Demand Trends", "Understand when demand rises across days, weekdays, and hours.")
try:
    con = connect()
    filters = sidebar_filters(con)
    hourly = aggregate(con, filters, "EXTRACT(hour FROM pickup_datetime)", "")
    weekday = aggregate(con, filters, "DAYOFWEEK(pickup_datetime)", "")
    daily = aggregate(con, filters, "CAST(pickup_datetime AS DATE)", "")
    heat = grouped_metrics(con, filters, "EXTRACT(hour FROM pickup_datetime) AS hour, DAYOFWEEK(pickup_datetime) AS dayofweek", "count(*) AS trips")
except FileNotFoundError:
    st.warning("Process TLC data before opening time trends."); st.stop()
st.plotly_chart(line(daily, "period", "trips", "Daily demand"), use_container_width=True)
left, right = st.columns(2)
with left: st.plotly_chart(bar(hourly, "period", "trips", "Hourly demand"), use_container_width=True)
with right: st.plotly_chart(bar(weekday, "period", "trips", "Demand by weekday"), use_container_width=True)
st.plotly_chart(heatmap(heat, "hour", "dayofweek", "trips", "Average demand by hour and weekday"), use_container_width=True)
