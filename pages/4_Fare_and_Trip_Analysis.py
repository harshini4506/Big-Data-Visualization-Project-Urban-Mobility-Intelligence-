import streamlit as st
from src.database import connect
from src.queries import query_frame, aggregate
from src.visualizations import histogram, bar, scatter, box, donut
from src.exports import csv_bytes
from src.filters import sidebar_filters
from src.ui import apply_theme, page_header
st.set_page_config(page_title="Fare and Trip Analysis", layout="wide")
apply_theme()
page_header("Fare and Trip Analysis", "Explore fare, distance, and payment behavior from the selected trips.")
try:
    con = connect()
    filters = sidebar_filters(con)
    frame = query_frame(con, filters, "ORDER BY pickup_datetime", 100000)
    payment = aggregate(con, filters, "payment_type", "")
except FileNotFoundError:
    st.warning("Process TLC data before opening fare analysis."); st.stop()
left, right = st.columns(2)
with left:
    st.plotly_chart(histogram(frame, "fare_amount", "Fare distribution (bounded query sample)"), use_container_width=True)
with right:
    st.plotly_chart(histogram(frame, "trip_distance", "Trip-distance distribution (bounded query sample)"), use_container_width=True)
st.plotly_chart(bar(payment, "period", "trips", "Payment type"), use_container_width=True)
metric_cols = st.columns(2)
with metric_cols[0]:
    st.plotly_chart(scatter(frame, "trip_distance", "fare_amount", "Fare versus trip distance"), use_container_width=True)
with metric_cols[1]:
    st.plotly_chart(box(frame, "payment_type", "total_amount", "Total amount by payment type"), use_container_width=True)
st.caption("Detailed distributions are capped at 100,000 rows to protect memory; the label identifies the bounded result.")
st.download_button("Download filtered trip sample", csv_bytes(frame), "trip_sample.csv", "text/csv")
