"""
app.py
-------
Logistics Cost Analyzer — main entry point / Dashboard page.

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from data_generator import generate_shipment_data
import database as db
from filters import apply_sidebar_filters
from utils import compute_kpis, inject_css, kpi_card, fmt_currency, fmt_number

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Logistics Cost Analyzer",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)



inject_css()


# ---------------------------------------------------------------------------
# Data loading (generate once, persist in SQLite, cache in-session)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_dataset():
    if db.record_count() == 0:
        df = generate_shipment_data(n=1500, seed=42)
        db.init_db_with_data(df)
    df = db.load_data()
    return df


with st.spinner("Loading shipment data..."):
    full_df = load_dataset()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
col_title, col_refresh = st.columns([5, 1])
with col_title:
    st.markdown(
        '<div class="app-title">🚚 Logistics Cost Analyzer</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="app-subtitle">Fictional demo data · shipment cost, revenue & profitability intelligence</div>',
        unsafe_allow_html=True,
    )
with col_refresh:
    st.write("")
    if st.button("🔄 Regenerate Data"):
        new_df = generate_shipment_data(n=1500, seed=np.random.randint(0, 99999))
        db.reset_database(new_df)
        st.cache_data.clear()
        st.rerun()

st.sidebar.markdown("##  Navigation")
st.sidebar.info(
    "Use the pages above to explore **Cost**, **Route**, **Vehicle**, and "
    "**Profitability** analysis, plus **Business Insights** and **Reports**."
)

# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------
filtered_df = apply_sidebar_filters(full_df, key_prefix="dash")

if filtered_df.empty:
    st.warning("No shipments match the selected filters. Please adjust your filter criteria.")
    st.stop()

kpis = compute_kpis(filtered_df)

# ---------------------------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------------------------
st.markdown('<div class="section-header">📊 Key Performance Indicators</div>', unsafe_allow_html=True)

row1 = st.columns(4)
kpi_card(row1[0], "Total Shipments", fmt_number(kpis["Total Shipments"]))
kpi_card(row1[1], "Total Logistics Cost", fmt_currency(kpis["Total Logistics Cost"]))
kpi_card(row1[2], "Total Revenue", fmt_currency(kpis["Total Revenue"]))
kpi_card(row1[3], "Total Profit", fmt_currency(kpis["Total Profit"]))

row2 = st.columns(4)
kpi_card(row2[0], "Profit Margin", f"{kpis['Profit Margin (%)']:.1f}%")
kpi_card(row2[1], "Avg Cost / Shipment", fmt_currency(kpis["Avg Cost per Shipment"]))
kpi_card(row2[2], "Avg Cost / Km", fmt_currency(kpis["Avg Cost per Km"]))
kpi_card(row2[3], "Total Distance", f"{kpis['Total Distance (km)']:,.0f} km")

row3 = st.columns(4)
kpi_card(row3[0], "Avg Delivery Time", f"{kpis['Avg Delivery Time (hrs)']:.1f} hrs")
on_time_rate = (filtered_df["delivery_status"] == "On Time").mean() * 100
kpi_card(row3[1], "On-Time Rate", f"{on_time_rate:.1f}%")
active_suppliers = filtered_df["supplier"].nunique()
kpi_card(row3[2], "Active Suppliers", fmt_number(active_suppliers))
active_vehicles = filtered_df["vehicle_type"].nunique()
kpi_card(row3[3], "Vehicle Types in Use", fmt_number(active_vehicles))

PLOTLY_TEMPLATE = "plotly_white"
COLOR_SEQ = px.colors.qualitative.Prism

# ---------------------------------------------------------------------------
# Monthly Cost & Profit
# ---------------------------------------------------------------------------
st.markdown('<div class="section-header">📈 Monthly Trends</div>', unsafe_allow_html=True)

monthly = (
    filtered_df.groupby("month", as_index=False)
    .agg(total_cost=("total_cost", "sum"), revenue=("revenue", "sum"), profit=("profit", "sum"))
    .sort_values("month")
)

c1, c2 = st.columns(2)
with c1:
    fig_cost = px.bar(
        monthly, x="month", y="total_cost", title="Monthly Logistics Cost",
        template=PLOTLY_TEMPLATE, color_discrete_sequence=["#1F4E78"],
    )
    fig_cost.update_layout(xaxis_title="Month", yaxis_title="Total Cost ($)", height=380)
    st.plotly_chart(fig_cost, use_container_width=True)

with c2:
    fig_profit = go.Figure()
    fig_profit.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["profit"], mode="lines+markers",
        name="Profit", line=dict(color="#2E86AB", width=3), fill="tozeroy",
    ))
    fig_profit.update_layout(
        title="Monthly Profit", xaxis_title="Month", yaxis_title="Profit ($)",
        template=PLOTLY_TEMPLATE, height=380,
    )
    st.plotly_chart(fig_profit, use_container_width=True)

# ---------------------------------------------------------------------------
# Cost Breakdown & Fuel Trend
# ---------------------------------------------------------------------------
c3, c4 = st.columns(2)
with c3:
    cost_components = {
        "Fuel": filtered_df["fuel_cost"].sum(),
        "Labor": filtered_df["labor_cost"].sum(),
        "Maintenance": filtered_df["maintenance_cost"].sum(),
        "Toll": filtered_df["toll_cost"].sum(),
        "Other": filtered_df["other_charges"].sum(),
    }
    fig_breakdown = px.pie(
        names=list(cost_components.keys()), values=list(cost_components.values()),
        title="Cost Breakdown", hole=0.45, template=PLOTLY_TEMPLATE,
        color_discrete_sequence=COLOR_SEQ,
    )
    fig_breakdown.update_layout(height=380)
    st.plotly_chart(fig_breakdown, use_container_width=True)

with c4:
    fuel_monthly = filtered_df.groupby("month", as_index=False)["fuel_cost"].sum().sort_values("month")
    fig_fuel = px.line(
        fuel_monthly, x="month", y="fuel_cost", title="Fuel Cost Trend", markers=True,
        template=PLOTLY_TEMPLATE, color_discrete_sequence=["#D62246"],
    )
    fig_fuel.update_layout(xaxis_title="Month", yaxis_title="Fuel Cost ($)", height=380)
    st.plotly_chart(fig_fuel, use_container_width=True)

# ---------------------------------------------------------------------------
# Top Expensive Routes & Vehicle Utilization
# ---------------------------------------------------------------------------
st.markdown('<div class="section-header">🛣️ Routes & Vehicles</div>', unsafe_allow_html=True)

c5, c6 = st.columns(2)
with c5:
    route_cost = (
        filtered_df.groupby("route", as_index=False)["total_cost"].sum()
        .sort_values("total_cost", ascending=False).head(10)
    )
    fig_routes = px.bar(
        route_cost, x="total_cost", y="route", orientation="h",
        title="Top 10 Most Expensive Routes", template=PLOTLY_TEMPLATE,
        color="total_cost", color_continuous_scale="Blues",
    )
    fig_routes.update_layout(yaxis_title="", xaxis_title="Total Cost ($)", height=420,
                              yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig_routes, use_container_width=True)

with c6:
    vehicle_util = filtered_df.groupby("vehicle_type", as_index=False).agg(
        shipments=("shipment_id", "count"), avg_distance=("distance_km", "mean")
    )
    fig_vehicle = px.bar(
        vehicle_util, x="vehicle_type", y="shipments", title="Vehicle Utilization (Shipment Count)",
        template=PLOTLY_TEMPLATE, color="vehicle_type", color_discrete_sequence=COLOR_SEQ,
        text="shipments",
    )
    fig_vehicle.update_layout(xaxis_title="", yaxis_title="Shipments", height=420, showlegend=False)
    st.plotly_chart(fig_vehicle, use_container_width=True)

# ---------------------------------------------------------------------------
# Supplier & Warehouse Comparison
# ---------------------------------------------------------------------------
c7, c8 = st.columns(2)
with c7:
    supplier_cmp = filtered_df.groupby("supplier", as_index=False).agg(
        total_cost=("total_cost", "sum"), profit=("profit", "sum")
    ).sort_values("total_cost", ascending=False)
    fig_supplier = go.Figure()
    fig_supplier.add_trace(go.Bar(x=supplier_cmp["supplier"], y=supplier_cmp["total_cost"],
                                   name="Total Cost", marker_color="#1F4E78"))
    fig_supplier.add_trace(go.Bar(x=supplier_cmp["supplier"], y=supplier_cmp["profit"],
                                   name="Profit", marker_color="#2E86AB"))
    fig_supplier.update_layout(
        title="Supplier Comparison: Cost vs Profit", barmode="group",
        template=PLOTLY_TEMPLATE, height=420, xaxis_tickangle=-30,
    )
    st.plotly_chart(fig_supplier, use_container_width=True)

with c8:
    wh_cmp = filtered_df.groupby("warehouse", as_index=False).agg(
        total_cost=("total_cost", "sum"), profit=("profit", "sum"),
        shipments=("shipment_id", "count"),
    ).sort_values("profit", ascending=False)
    fig_wh = px.bar(
        wh_cmp, x="warehouse", y="profit", title="Warehouse Comparison (Profit)",
        template=PLOTLY_TEMPLATE, color="profit", color_continuous_scale="Tealgrn",
        text="shipments",
    )
    fig_wh.update_traces(texttemplate="%{text} shipments", textposition="outside")
    fig_wh.update_layout(xaxis_title="", yaxis_title="Profit ($)", height=420, xaxis_tickangle=-15)
    st.plotly_chart(fig_wh, use_container_width=True)

# ---------------------------------------------------------------------------
# Delivery Status
# ---------------------------------------------------------------------------
st.markdown('<div class="section-header">📦 Delivery Performance</div>', unsafe_allow_html=True)

status_counts = filtered_df["delivery_status"].value_counts().reset_index()
status_counts.columns = ["delivery_status", "count"]
status_colors = {"On Time": "#2E9E5B", "Delayed": "#E8A33D", "Early": "#2E86AB", "Cancelled": "#D62246"}

fig_status = px.pie(
    status_counts, names="delivery_status", values="count", title="Delivery Status Distribution",
    color="delivery_status", color_discrete_map=status_colors, hole=0.45,
)
fig_status.update_layout(height=400)
st.plotly_chart(fig_status, use_container_width=True)

st.caption(
    "💡 Tip: use the sidebar filters to drill into specific suppliers, warehouses, routes, "
    "vehicles, or drivers — every chart and KPI updates instantly."
)
