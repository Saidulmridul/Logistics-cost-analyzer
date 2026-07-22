"""Business Insights page — auto-generated observations and recommendations."""

import streamlit as st
import plotly.express as px

import database as db
from filters import apply_sidebar_filters
from utils import compute_kpis, inject_css, fmt_currency
from insights import generate_insights

st.set_page_config(page_title="Business Insights | Logistics Cost Analyzer", page_icon="💡", layout="wide")
inject_css()

st.markdown('<div class="app-title">💡 Business Insights</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Automatically generated observations and cost-saving recommendations</div>',
            unsafe_allow_html=True)

full_df = db.load_data()
if full_df.empty:
    st.error("No data found. Please visit the main Dashboard page first to generate data.")
    st.stop()

df = apply_sidebar_filters(full_df, key_prefix="insights")
if df.empty:
    st.warning("No shipments match the selected filters.")
    st.stop()

insights = generate_insights(df)

st.markdown('<div class="section-header">🔍 Key Findings</div>', unsafe_allow_html=True)

for ins in insights:
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">{ins['icon']} {ins['title']}</div>
            <div class="insight-detail">{ins['detail']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="section-header">📌 Supporting Visuals</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    supplier_cost = df.groupby("supplier", as_index=False)["total_cost"].mean().sort_values("total_cost", ascending=False)
    fig1 = px.bar(
        supplier_cost, x="total_cost", y="supplier", orientation="h",
        title="Average Cost per Shipment by Supplier", template="plotly_white",
        color="total_cost", color_continuous_scale="Reds",
    )
    fig1.update_layout(yaxis=dict(categoryorder="total ascending"), height=400, yaxis_title="", xaxis_title="Avg Cost ($)")
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    wh_margin = df.groupby("warehouse", as_index=False)["profit_margin_pct"].mean().sort_values("profit_margin_pct", ascending=False)
    fig2 = px.bar(
        wh_margin, x="warehouse", y="profit_margin_pct", title="Average Profit Margin by Warehouse",
        template="plotly_white", color="profit_margin_pct", color_continuous_scale="RdYlGn",
    )
    fig2.update_layout(xaxis_title="", yaxis_title="Avg Margin (%)", height=400, xaxis_tickangle=-15)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown('<div class="section-header">💡 Recommendations Summary</div>', unsafe_allow_html=True)
st.info(
    "Based on the current filter selection, focus improvement efforts on the highest-cost supplier "
    "and route identified above, evaluate preventive maintenance for high-maintenance vehicle classes, "
    "and replicate best practices from the top-performing warehouse across the network."
)
