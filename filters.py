"""
filters.py
-----------
Reusable sidebar filter widgets shared across all pages.
"""

import streamlit as st
import pandas as pd


def apply_sidebar_filters(df: pd.DataFrame, key_prefix: str = "f") -> pd.DataFrame:
    """Render sidebar filter widgets and return the filtered DataFrame."""

    st.sidebar.markdown("### 🔍 Filters")

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key=f"{key_prefix}_date",
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    suppliers = st.sidebar.multiselect(
        "Supplier",
        options=sorted(df["supplier"].unique()),
        default=[],
        key=f"{key_prefix}_supplier",
    )
    warehouses = st.sidebar.multiselect(
        "Warehouse",
        options=sorted(df["warehouse"].unique()),
        default=[],
        key=f"{key_prefix}_warehouse",
    )
    routes = st.sidebar.multiselect(
        "Route",
        options=sorted(df["route"].unique()),
        default=[],
        key=f"{key_prefix}_route",
    )
    vehicles = st.sidebar.multiselect(
        "Vehicle Type",
        options=sorted(df["vehicle_type"].unique()),
        default=[],
        key=f"{key_prefix}_vehicle",
    )
    drivers = st.sidebar.multiselect(
        "Driver",
        options=sorted(df["driver"].unique()),
        default=[],
        key=f"{key_prefix}_driver",
    )
    statuses = st.sidebar.multiselect(
        "Delivery Status",
        options=sorted(df["delivery_status"].unique()),
        default=[],
        key=f"{key_prefix}_status",
    )

    filtered = df[
        (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
    ]
    if suppliers:
        filtered = filtered[filtered["supplier"].isin(suppliers)]
    if warehouses:
        filtered = filtered[filtered["warehouse"].isin(warehouses)]
    if routes:
        filtered = filtered[filtered["route"].isin(routes)]
    if vehicles:
        filtered = filtered[filtered["vehicle_type"].isin(vehicles)]
    if drivers:
        filtered = filtered[filtered["driver"].isin(drivers)]
    if statuses:
        filtered = filtered[filtered["delivery_status"].isin(statuses)]

    st.sidebar.markdown(f"**{len(filtered):,}** of **{len(df):,}** records match")

    if st.sidebar.button("↺ Reset Filters", key=f"{key_prefix}_reset"):
        for k in list(st.session_state.keys()):
            if k.startswith(key_prefix):
                del st.session_state[k]
        st.rerun()

    return filtered
