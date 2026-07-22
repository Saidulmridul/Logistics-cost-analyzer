"""Vehicle Analysis page — utilization, cost, and maintenance by vehicle type/driver."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import database as db
from filters import apply_sidebar_filters
from utils import inject_css, kpi_card, fmt_currency

st.set_page_config(page_title="Vehicle Analysis | Logistics Cost Analyzer", page_icon="🚛", layout="wide")
inject_css()

st.markdown('<div class="app-title">🚛 Vehicle Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Utilization, maintenance, and driver performance across the fleet</div>',
            unsafe_allow_html=True)

full_df = db.load_data()
if full_df.empty:
    st.error("No data found. Please visit the main Dashboard page first to generate data.")
    st.stop()

df = apply_sidebar_filters(full_df, key_prefix="vehicle")
if df.empty:
    st.warning("No shipments match the selected filters.")
    st.stop()

vehicle_summary = df.groupby("vehicle_type", as_index=False).agg(
    shipments=("shipment_id", "count"),
    total_distance=("distance_km", "sum"),
    total_cost=("total_cost", "sum"),
    avg_maintenance=("maintenance_cost", "mean"),
    total_maintenance=("maintenance_cost", "sum"),
    avg_delivery_time=("delivery_time_hours", "mean"),
).sort_values("shipments", ascending=False)

cols = st.columns(4)
kpi_card(cols[0], "Vehicle Types", f"{df['vehicle_type'].nunique():,}")
kpi_card(cols[1], "Most Used Vehicle", vehicle_summary.iloc[0]["vehicle_type"] if not vehicle_summary.empty else "-")
highest_maint = vehicle_summary.sort_values("avg_maintenance", ascending=False).iloc[0] if not vehicle_summary.empty else None
kpi_card(cols[2], "Highest Avg Maintenance", highest_maint["vehicle_type"] if highest_maint is not None else "-")
kpi_card(cols[3], "Total Maintenance Cost", fmt_currency(df["maintenance_cost"].sum()))

st.markdown('<div class="section-header">🚚 Vehicle Utilization</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    fig1 = px.bar(
        vehicle_summary, x="vehicle_type", y="shipments", title="Shipments by Vehicle Type",
        template="plotly_white", color="vehicle_type", color_discrete_sequence=px.colors.qualitative.Prism,
        text="shipments",
    )
    fig1.update_layout(xaxis_title="", yaxis_title="Shipments", height=400, showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    fig2 = px.bar(
        vehicle_summary, x="vehicle_type", y="total_distance", title="Total Distance Covered by Vehicle Type",
        template="plotly_white", color="vehicle_type", color_discrete_sequence=px.colors.qualitative.Prism,
    )
    fig2.update_layout(xaxis_title="", yaxis_title="Distance (km)", height=400, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown('<div class="section-header">🔧 Maintenance & Efficiency</div>', unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    fig3 = px.bar(
        vehicle_summary.sort_values("avg_maintenance", ascending=False),
        x="vehicle_type", y="avg_maintenance", title="Average Maintenance Cost by Vehicle Type",
        template="plotly_white", color="avg_maintenance", color_continuous_scale="Reds",
    )
    fig3.update_layout(xaxis_title="", yaxis_title="Avg Maintenance ($)", height=400)
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    fig4 = px.box(
        df, x="vehicle_type", y="cost_per_km", title="Cost per Km Distribution by Vehicle Type",
        template="plotly_white", color="vehicle_type", color_discrete_sequence=px.colors.qualitative.Prism,
    )
    fig4.update_layout(xaxis_title="", yaxis_title="Cost per Km ($)", height=400, showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown('<div class="section-header">👤 Driver Performance</div>', unsafe_allow_html=True)
driver_summary = df.groupby("driver", as_index=False).agg(
    shipments=("shipment_id", "count"),
    avg_delivery_time=("delivery_time_hours", "mean"),
    on_time_pct=("delivery_status", lambda s: (s == "On Time").mean() * 100),
    total_distance=("distance_km", "sum"),
).sort_values("shipments", ascending=False)

c5, c6 = st.columns(2)
with c5:
    fig5 = px.bar(
        driver_summary.head(10), x="driver", y="shipments", title="Top 10 Drivers by Shipment Count",
        template="plotly_white", color="shipments", color_continuous_scale="Blues",
    )
    fig5.update_layout(xaxis_title="", yaxis_title="Shipments", height=420, xaxis_tickangle=-30)
    st.plotly_chart(fig5, use_container_width=True)

with c6:
    fig6 = px.scatter(
        driver_summary, x="avg_delivery_time", y="on_time_pct", size="shipments", color="on_time_pct",
        hover_name="driver", template="plotly_white", title="Driver On-Time Rate vs Avg Delivery Time",
        color_continuous_scale="RdYlGn",
    )
    fig6.update_layout(height=420, xaxis_title="Avg Delivery Time (hrs)", yaxis_title="On-Time Rate (%)")
    st.plotly_chart(fig6, use_container_width=True)

with st.expander("🔎 View Full Vehicle & Driver Data"):
    tab1, tab2 = st.tabs(["Vehicle Summary", "Driver Summary"])
    with tab1:
        st.dataframe(
            vehicle_summary.style.format({
                "total_distance": "{:.0f}", "total_cost": "${:,.2f}",
                "avg_maintenance": "${:.2f}", "total_maintenance": "${:,.2f}",
                "avg_delivery_time": "{:.1f}",
            }), use_container_width=True, height=250,
        )
    with tab2:
        st.dataframe(
            driver_summary.style.format({
                "avg_delivery_time": "{:.1f}", "on_time_pct": "{:.1f}%", "total_distance": "{:.0f}",
            }), use_container_width=True, height=250,
        )
