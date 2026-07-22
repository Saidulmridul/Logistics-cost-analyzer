"""Profitability Analysis page — margins, profit drivers, and trends."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import database as db
from filters import apply_sidebar_filters
from utils import compute_kpis, inject_css, kpi_card, fmt_currency

st.set_page_config(page_title="Profitability Analysis | Logistics Cost Analyzer", page_icon="📈", layout="wide")
inject_css()

st.markdown('<div class="app-title">📈 Profitability Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Margins, profit drivers, and trends across the business</div>',
            unsafe_allow_html=True)

full_df = db.load_data()
if full_df.empty:
    st.error("No data found. Please visit the main Dashboard page first to generate data.")
    st.stop()

df = apply_sidebar_filters(full_df, key_prefix="profit")
if df.empty:
    st.warning("No shipments match the selected filters.")
    st.stop()

kpis = compute_kpis(df)

cols = st.columns(4)
kpi_card(cols[0], "Total Profit", fmt_currency(kpis["Total Profit"]))
kpi_card(cols[1], "Profit Margin", f"{kpis['Profit Margin (%)']:.1f}%")
profitable_pct = (df["profit"] > 0).mean() * 100
kpi_card(cols[2], "Profitable Shipments", f"{profitable_pct:.1f}%")
loss_making = (df["profit"] < 0).sum()
kpi_card(cols[3], "Loss-Making Shipments", f"{loss_making:,}")

st.markdown('<div class="section-header">📊 Profitability Trends</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    monthly = df.groupby("month", as_index=False).agg(
        revenue=("revenue", "sum"), cost=("total_cost", "sum"), profit=("profit", "sum")
    ).sort_values("month")
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=monthly["month"], y=monthly["revenue"], name="Revenue", marker_color="#2E86AB"))
    fig1.add_trace(go.Bar(x=monthly["month"], y=monthly["cost"], name="Cost", marker_color="#D62246"))
    fig1.add_trace(go.Scatter(x=monthly["month"], y=monthly["profit"], name="Profit",
                               mode="lines+markers", line=dict(color="#1F4E78", width=3), yaxis="y2"))
    fig1.update_layout(
        title="Revenue vs Cost vs Profit (Monthly)", template="plotly_white", barmode="group", height=440,
        yaxis=dict(title="Revenue / Cost ($)"),
        yaxis2=dict(title="Profit ($)", overlaying="y", side="right"),
    )
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    margin_monthly = df.groupby("month", as_index=False)["profit_margin_pct"].mean().sort_values("month")
    fig2 = px.area(
        margin_monthly, x="month", y="profit_margin_pct", title="Average Profit Margin Trend",
        template="plotly_white", color_discrete_sequence=["#2E9E5B"],
    )
    fig2.update_layout(xaxis_title="Month", yaxis_title="Profit Margin (%)", height=440)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown('<div class="section-header">🏆 Profit Drivers</div>', unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    supplier_profit = df.groupby("supplier", as_index=False)["profit"].sum().sort_values("profit", ascending=False)
    fig3 = px.bar(
        supplier_profit, x="profit", y="supplier", orientation="h", title="Profit by Supplier",
        template="plotly_white", color="profit", color_continuous_scale="RdYlGn",
    )
    fig3.update_layout(yaxis=dict(categoryorder="total ascending"), height=420, yaxis_title="", xaxis_title="Profit ($)")
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    wh_profit = df.groupby("warehouse", as_index=False).agg(
        profit=("profit", "sum"), margin=("profit_margin_pct", "mean")
    ).sort_values("margin", ascending=False)
    fig4 = px.bar(
        wh_profit, x="warehouse", y="margin", title="Average Profit Margin by Warehouse",
        template="plotly_white", color="margin", color_continuous_scale="RdYlGn",
    )
    fig4.update_layout(xaxis_title="", yaxis_title="Avg Margin (%)", height=420, xaxis_tickangle=-15)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown('<div class="section-header">🚛 Profit by Vehicle & Delivery Status</div>', unsafe_allow_html=True)
c5, c6 = st.columns(2)

with c5:
    vehicle_profit = df.groupby("vehicle_type", as_index=False)["profit"].sum().sort_values("profit", ascending=False)
    fig5 = px.bar(
        vehicle_profit, x="vehicle_type", y="profit", title="Profit by Vehicle Type",
        template="plotly_white", color="profit", color_continuous_scale="Blues",
    )
    fig5.update_layout(xaxis_title="", yaxis_title="Profit ($)", height=420)
    st.plotly_chart(fig5, use_container_width=True)

with c6:
    status_profit = df.groupby("delivery_status", as_index=False)["profit"].sum()
    fig6 = px.bar(
        status_profit, x="delivery_status", y="profit", title="Profit by Delivery Status",
        template="plotly_white", color="delivery_status",
        color_discrete_map={"On Time": "#2E9E5B", "Delayed": "#E8A33D", "Early": "#2E86AB", "Cancelled": "#D62246"},
    )
    fig6.update_layout(xaxis_title="", yaxis_title="Profit ($)", height=420, showlegend=False)
    st.plotly_chart(fig6, use_container_width=True)

with st.expander("🔎 View Shipments Ranked by Profit"):
    st.dataframe(
        df[["shipment_id", "date", "supplier", "route", "vehicle_type", "revenue",
            "total_cost", "profit", "profit_margin_pct", "delivery_status"]]
        .sort_values("profit", ascending=False),
        use_container_width=True, height=350,
    )
