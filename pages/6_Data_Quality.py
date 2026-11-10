import json
import streamlit as st
from pathlib import Path
from src.config import METADATA_DIR, REPORT_DIR
from src.ui import apply_theme, page_header
st.set_page_config(page_title="Data Quality", layout="wide")
apply_theme()
page_header("Data Quality and Processing", "Transparent ingestion, validation, and processing details for the current dataset.")
manifest = METADATA_DIR / "manifest.json"
reports = sorted(REPORT_DIR.glob("*.json"))
if manifest.exists():
    st.subheader("Imported files")
    st.dataframe(json.loads(manifest.read_text(encoding="utf-8")), use_container_width=True)
else:
    st.info("No ingestion manifest found.")
if reports:
    st.subheader("Latest processing report")
    report = json.loads(reports[-1].read_text(encoding="utf-8"))
    st.json(report)
    st.download_button("Download quality report", json.dumps(report, indent=2), reports[-1].name, "application/json")
else:
    st.info("No processing report found.")
