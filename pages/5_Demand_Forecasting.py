import streamlit as st
import pandas as pd
from src.database import connect
from src.queries import query_frame
from src.forecasting import train_forecast
from src.filters import sidebar_filters
from src.ui import apply_theme, page_header
import plotly.graph_objects as go
st.set_page_config(page_title="Demand Forecasting", layout="wide")
apply_theme()
page_header("Demand Forecasting", "Evaluate a chronological hourly demand model against a previous-day baseline.")
try:
    connection = connect()
    filters = sidebar_filters(connection)
    frame = query_frame(connection, filters, "ORDER BY pickup_datetime", 500000)
except FileNotFoundError:
    st.warning("Process TLC data before forecasting."); st.stop()
if st.button("Train chronological baseline model"):
    try:
        result = train_forecast(frame[["pickup_datetime"]].dropna())
        st.metric("Model MAE", f"{result['mae']:.2f}")
        st.metric("Model RMSE", f"{result['rmse']:.2f}")
        st.metric("Previous-day baseline MAE", f"{result['baseline_mae']:.2f}")
        chart = go.Figure()
        chart.add_scatter(x=result["timestamps"], y=result["actual"], name="Actual")
        chart.add_scatter(x=result["timestamps"], y=result["predicted"], name="Predicted")
        st.plotly_chart(chart, use_container_width=True)
        st.caption("Evaluation uses a chronological holdout. Forecasts are estimates, not guaranteed future traffic.")
    except ValueError as exc:
        st.error(str(exc))
else:
    st.info("Click the button to train using the currently available processed records.")
