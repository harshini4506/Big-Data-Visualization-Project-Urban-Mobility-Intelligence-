import streamlit as st

from src.database import connect
from src.filters import sidebar_filters
from src.ui import apply_theme, page_header
from src.visualizations import bar
from src.queries import aggregate

st.set_page_config(page_title="Route Analysis", layout="wide")
apply_theme()
page_header("Route Analysis", "Discover the most common origin-to-destination journeys in the selected data.")

try:
    connection = connect()
    filters = sidebar_filters(connection)
    routes = aggregate(
        connection,
        filters,
        "pickup_zone_name || ' -> ' || dropoff_zone_name",
        "",
    )
except FileNotFoundError:
    st.warning("No processed Parquet files found. Run the ingestion and processing commands in the README.")
    st.stop()

routes = routes[routes["period"].notna()].nlargest(20, "trips").sort_values("trips")
if routes.empty:
    st.info("No routes match the current filters.")
else:
    st.plotly_chart(
        bar(routes, "trips", "period", "Top origin-to-destination routes"),
        use_container_width=True,
        theme=None,
    )
    st.dataframe(
        routes.rename(columns={"period": "Route", "trips": "Trips"}),
        use_container_width=True,
        hide_index=True,
    )
