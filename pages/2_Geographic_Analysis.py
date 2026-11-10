import streamlit as st
from src.database import connect
from src.queries import aggregate
from src.visualizations import bar
from src.filters import sidebar_filters
from src.ui import apply_theme, page_header
st.set_page_config(page_title="Geographic Analysis", layout="wide")
apply_theme()
page_header("Geographic Demand Analysis", "Compare pickup and drop-off activity by validated TLC zone IDs.")
try:
    con = connect()
    filters = sidebar_filters(con)
    pickup = aggregate(con, filters, "pickup_zone_name", "")
    dropoff = aggregate(con, filters, "dropoff_zone_name", "")
except FileNotFoundError:
    st.warning("Process TLC data before opening geographic analysis."); st.stop()
left, right = st.columns(2)
with left: st.plotly_chart(bar(pickup.nlargest(20, "trips"), "period", "trips", "Top pickup zones"), use_container_width=True)
with right: st.plotly_chart(bar(dropoff.nlargest(20, "trips"), "period", "trips", "Top drop-off zones"), use_container_width=True)
st.caption("Zone names come from the official TLC taxi-zone lookup. A boundary GeoJSON is required before rendering a geographic map; zone IDs are never treated as coordinates.")
