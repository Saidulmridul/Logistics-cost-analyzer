"""Route Analysis page — performance, cost, and profitability by route."""

import streamlit as st
import pandas as pd
import plotly.express as px

import database as db
from filters import apply_sidebar_filters
from utils import compute_kpis, inject_css, kpi_card, fmt_currency

st.set_page_config(page_title="Route Analysis | Logistics Cost Analyzer", page_icon="🛣️", layout="wide")
inject_css()

st.markdown('<div class="app-title">🛣️ Route Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Compare cost, distance, and profitability across shipping routes</div>',
            unsafe_allow_html=True)

full_df = db.load_data()
if full_df.empty:
    st.error("No data found. Please visit the main Dashboard page first to generate data.")
    st.stop()

df = apply_sidebar_filters(full_df, key_prefix="route")
if df.empty:
    st.warning("No shipments match the selected filters.")
    st.stop()

route_summary = df.groupby("route", as_index=False).agg(
    shipments=("shipment_id", "count"),
    total_cost=("total_cost", "sum"),
    total_revenue=("revenue", "sum"),
    total_profit=("profit", "sum"),
    avg_distance=("distance_km", "mean"),
    avg_cost_per_km=("cost_per_km", "mean"),
    avg_delivery_time=("delivery_time_hours", "mean"),
).sort_values("total_cost", ascending=False)

cols = st.columns(4)
kpi_card(cols[0], "Total Routes", f"{df['route'].nunique():,}")
kpi_card(cols[1], "Most Expensive Route", route_summary.iloc[0]["route"] if not route_summary.empty else "-")
best_route = route_summary.sort_values("total_profit", ascending=False).iloc[0] if not route_summary.empty else None
kpi_card(cols[2], "Most Profitable Route", best_route["route"] if best_route is not None else "-")
kpi_card(cols[3], "Avg Distance / Route", f"{route_summary['avg_distance'].mean():.0f} km" if not route_summary.empty else "-")

st.markdown('<div class="section-header">💵 Top Routes by Cost & Profit</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    top_cost = route_summary.head(12)
    fig1 = px.bar(top_cost, x="total_cost", y="route", orientation="h",
                  title="Top 12 Routes by Total Cost", template="plotly_white",
                  color="total_cost", color_continuous_scale="Blues")
    fig1.update_layout(yaxis=dict(categoryorder="total ascending"), height=460, yaxis_title="", xaxis_title="Total Cost ($)")
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    top_profit = route_summary.sort_values("total_profit", ascending=False).head(12)
    fig2 = px.bar(top_profit, x="total_profit", y="route", orientation="h",
                  title="Top 12 Routes by Total Profit", template="plotly_white",
                  color="total_profit", color_continuous_scale="Tealgrn")
    fig2.update_layout(yaxis=dict(categoryorder="total ascending"), height=460, yaxis_title="", xaxis_title="Total Profit ($)")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown('<div class="section-header">⏱️ Efficiency by Route</div>', unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    fig3 = px.scatter(
        route_summary, x="avg_distance", y="avg_cost_per_km", size="shipments", color="total_profit",
        hover_name="route", template="plotly_white", title="Cost Efficiency: Distance vs Cost/Km",
        color_continuous_scale="RdYlGn",
    )
    fig3.update_layout(height=440, xaxis_title="Avg Distance (km)", yaxis_title="Avg Cost per Km ($)")
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    fig4 = px.bar(
        route_summary.sort_values("avg_delivery_time", ascending=False).head(12),
        x="avg_delivery_time", y="route", orientation="h", template="plotly_white",
        title="Slowest 12 Routes by Avg Delivery Time", color="avg_delivery_time",
        color_continuous_scale="Oranges",
    )
    fig4.update_layout(yaxis=dict(categoryorder="total ascending"), height=440, yaxis_title="", xaxis_title="Avg Delivery Time (hrs)")
    st.plotly_chart(fig4, use_container_width=True)

st.markdown('<div class="section-header">🌍 Destination Volume</div>', unsafe_allow_html=True)
dest_summary = df.groupby("destination", as_index=False).agg(
    shipments=("shipment_id", "count"), total_revenue=("revenue", "sum")
).sort_values("shipments", ascending=False)
fig5 = px.treemap(
    dest_summary, path=["destination"], values="shipments", color="total_revenue",
    color_continuous_scale="Blues", title="Shipment Volume by Destination",
)
fig5.update_layout(height=460)
st.plotly_chart(fig5, use_container_width=True)

with st.expander("🔎 View Full Route Summary Table"):
    st.dataframe(
        route_summary.style.format({
            "total_cost": "${:,.2f}", "total_revenue": "${:,.2f}", "total_profit": "${:,.2f}",
            "avg_distance": "{:.1f}", "avg_cost_per_km": "${:.2f}", "avg_delivery_time": "{:.1f}",
        }),
        use_container_width=True, height=350,
    )
