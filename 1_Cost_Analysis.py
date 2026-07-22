"""Cost Analysis page — deep dive into cost drivers and composition."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import database as db
from filters import apply_sidebar_filters
from utils import compute_kpis, inject_css, kpi_card, fmt_currency

st.set_page_config(page_title="Cost Analysis | Logistics Cost Analyzer", page_icon="💰", layout="wide")
inject_css()

st.markdown('<div class="app-title"> Cost Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Understand what drives logistics cost across your network</div>',
            unsafe_allow_html=True)

full_df = db.load_data()
if full_df.empty:
    st.error("No data found. Please visit the main Dashboard page first to generate data.")
    st.stop()

df = apply_sidebar_filters(full_df, key_prefix="cost")
if df.empty:
    st.warning("No shipments match the selected filters.")
    st.stop()

kpis = compute_kpis(df)

cols = st.columns(4)
kpi_card(cols[0], "Total Logistics Cost", fmt_currency(kpis["Total Logistics Cost"]))
kpi_card(cols[1], "Avg Cost / Shipment", fmt_currency(kpis["Avg Cost per Shipment"]))
kpi_card(cols[2], "Avg Cost / Km", fmt_currency(kpis["Avg Cost per Km"]))
fuel_share = df["fuel_cost"].sum() / df["total_cost"].sum() * 100 if df["total_cost"].sum() else 0
kpi_card(cols[3], "Fuel Share of Cost", f"{fuel_share:.1f}%")

st.markdown('<div class="section-header">🧾 Cost Component Breakdown</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    components = {
        "Fuel": df["fuel_cost"].sum(), "Labor": df["labor_cost"].sum(),
        "Maintenance": df["maintenance_cost"].sum(), "Toll": df["toll_cost"].sum(),
        "Other": df["other_charges"].sum(),
    }
    fig = px.bar(
        x=list(components.keys()), y=list(components.values()),
        title="Total Cost by Component", template="plotly_white",
        color=list(components.keys()), color_discrete_sequence=px.colors.qualitative.Prism,
    )
    fig.update_layout(xaxis_title="", yaxis_title="Cost ($)", height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    monthly_components = df.groupby("month", as_index=False).agg(
        fuel=("fuel_cost", "sum"), labor=("labor_cost", "sum"),
        maintenance=("maintenance_cost", "sum"), toll=("toll_cost", "sum"),
        other=("other_charges", "sum"),
    ).sort_values("month")
    fig2 = go.Figure()
    for col, name, color in [
        ("fuel", "Fuel", "#1F4E78"), ("labor", "Labor", "#2E86AB"),
        ("maintenance", "Maintenance", "#D62246"), ("toll", "Toll", "#E8A33D"),
        ("other", "Other", "#7A9E7E"),
    ]:
        fig2.add_trace(go.Bar(x=monthly_components["month"], y=monthly_components[col], name=name, marker_color=color))
    fig2.update_layout(title="Monthly Cost Composition", barmode="stack", template="plotly_white",
                        xaxis_title="Month", yaxis_title="Cost ($)", height=400)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown('<div class="section-header">📊 Cost by Dimension</div>', unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    by_supplier = df.groupby("supplier", as_index=False)["total_cost"].mean().sort_values("total_cost", ascending=False)
    fig3 = px.bar(by_supplier, x="total_cost", y="supplier", orientation="h",
                  title="Average Cost per Shipment by Supplier", template="plotly_white",
                  color="total_cost", color_continuous_scale="Blues")
    fig3.update_layout(yaxis=dict(categoryorder="total ascending"), height=420, yaxis_title="", xaxis_title="Avg Cost ($)")
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    by_warehouse = df.groupby("warehouse", as_index=False)["total_cost"].mean().sort_values("total_cost", ascending=False)
    fig4 = px.bar(by_warehouse, x="warehouse", y="total_cost",
                  title="Average Cost per Shipment by Warehouse", template="plotly_white",
                  color="total_cost", color_continuous_scale="Purp")
    fig4.update_layout(height=420, xaxis_title="", yaxis_title="Avg Cost ($)", xaxis_tickangle=-15)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown('<div class="section-header">📐 Cost vs Distance</div>', unsafe_allow_html=True)
fig5 = px.scatter(
    df, x="distance_km", y="total_cost", color="vehicle_type", size="total_cost",
    hover_data=["shipment_id", "supplier", "route"], template="plotly_white",
    title="Cost vs Distance by Vehicle Type", color_discrete_sequence=px.colors.qualitative.Prism,
)
fig5.update_layout(height=460, xaxis_title="Distance (km)", yaxis_title="Total Cost ($)")
st.plotly_chart(fig5, use_container_width=True)

with st.expander("🔎 View Detailed Cost Data Table"):
    st.dataframe(
        df[["shipment_id", "date", "supplier", "warehouse", "route", "vehicle_type",
            "distance_km", "fuel_cost", "labor_cost", "maintenance_cost", "toll_cost",
            "other_charges", "total_cost", "cost_per_km"]].sort_values("total_cost", ascending=False),
        use_container_width=True, height=350,
    )
