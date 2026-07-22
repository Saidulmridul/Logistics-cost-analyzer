"""Data Explorer page — search, sort, and browse raw shipment records."""

import streamlit as st

import database as db
from filters import apply_sidebar_filters
from utils import inject_css
from reports import to_csv_bytes

st.set_page_config(page_title="Data Explorer | Logistics Cost Analyzer", page_icon="🔎", layout="wide")
inject_css()

st.markdown('<div class="app-title"> Data Explorer</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Search, sort, and export raw shipment records</div>',
            unsafe_allow_html=True)

full_df = db.load_data()
if full_df.empty:
    st.error("No data found. Please visit the main Dashboard page first to generate data.")
    st.stop()

df = apply_sidebar_filters(full_df, key_prefix="explorer")
if df.empty:
    st.warning("No shipments match the selected filters.")
    st.stop()

st.markdown('<div class="section-header">🔍 Search & Sort</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    search_term = st.text_input(
        "Search (shipment ID, supplier, warehouse, destination, route, or driver)",
        placeholder="e.g. SHP-000123, Orion, Dhaka...",
    )
with c2:
    sort_col = st.selectbox(
        "Sort by",
        options=["date", "total_cost", "revenue", "profit", "distance_km",
                 "delivery_time_hours", "cost_per_km", "profit_margin_pct"],
        index=0,
    )
with c3:
    sort_dir = st.selectbox("Order", options=["Descending", "Ascending"], index=0)

result_df = df.copy()
if search_term:
    term = search_term.strip().lower()
    mask = (
        result_df["shipment_id"].str.lower().str.contains(term, na=False)
        | result_df["supplier"].str.lower().str.contains(term, na=False)
        | result_df["warehouse"].str.lower().str.contains(term, na=False)
        | result_df["destination"].str.lower().str.contains(term, na=False)
        | result_df["route"].str.lower().str.contains(term, na=False)
        | result_df["driver"].str.lower().str.contains(term, na=False)
    )
    result_df = result_df[mask]

result_df = result_df.sort_values(sort_col, ascending=(sort_dir == "Ascending"))

st.markdown(f"**{len(result_df):,}** records found")

st.dataframe(
    result_df[[
        "shipment_id", "date", "supplier", "warehouse", "destination", "route",
        "vehicle_type", "driver", "distance_km", "total_cost", "revenue", "profit",
        "delivery_time_hours", "delivery_status",
    ]],
    use_container_width=True, height=500,
)

st.download_button(
    "⬇️ Download Search Results (CSV)",
    data=to_csv_bytes(result_df),
    file_name="logistics_search_results.csv",
    mime="text/csv",
)
