"""
utils.py
---------
Shared KPI calculations and CSS styling used across all pages.
"""

import pandas as pd
import streamlit as st


def compute_kpis(df: pd.DataFrame) -> dict:
    """Compute the core headline KPIs for a given (filtered) DataFrame."""
    if df.empty:
        return {
            "Total Shipments": 0,
            "Total Logistics Cost": 0.0,
            "Total Revenue": 0.0,
            "Total Profit": 0.0,
            "Profit Margin (%)": 0.0,
            "Avg Cost per Shipment": 0.0,
            "Avg Cost per Km": 0.0,
            "Total Distance (km)": 0.0,
            "Avg Delivery Time (hrs)": 0.0,
        }

    total_shipments = len(df)
    total_cost = df["total_cost"].sum()
    total_revenue = df["revenue"].sum()
    total_profit = df["profit"].sum()
    profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0.0
    avg_cost_per_shipment = total_cost / total_shipments if total_shipments else 0.0
    total_distance = df["distance_km"].sum()
    avg_cost_per_km = total_cost / total_distance if total_distance else 0.0
    avg_delivery_time = df["delivery_time_hours"].mean()

    return {
        "Total Shipments": total_shipments,
        "Total Logistics Cost": round(total_cost, 2),
        "Total Revenue": round(total_revenue, 2),
        "Total Profit": round(total_profit, 2),
        "Profit Margin (%)": round(profit_margin, 2),
        "Avg Cost per Shipment": round(avg_cost_per_shipment, 2),
        "Avg Cost per Km": round(avg_cost_per_km, 2),
        "Total Distance (km)": round(total_distance, 1),
        "Avg Delivery Time (hrs)": round(avg_delivery_time, 2),
    }


def fmt_currency(x):
    return f"${x:,.2f}"


def fmt_number(x):
    return f"{x:,.0f}"


CUSTOM_CSS = """
<style>
    /* Overall app background */
    .stApp {
        background-color: #F5F7FA;
    }

    /* KPI Card */
    .kpi-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        border-left: 5px solid #1F4E78;
        margin-bottom: 12px;
        height: 100%;
    }
    .kpi-label {
        font-size: 0.80rem;
        color: #6B7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.55rem;
        font-weight: 700;
        color: #111827;
    }
    .kpi-sub {
        font-size: 0.75rem;
        color: #9CA3AF;
        margin-top: 2px;
    }

    /* Section headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1F4E78;
        margin: 18px 0 8px 0;
        padding-bottom: 6px;
        border-bottom: 2px solid #E5E7EB;
    }

    /* Insight card */
    .insight-card {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border-left: 4px solid #2E86AB;
    }
    .insight-title {
        font-weight: 700;
        color: #1F4E78;
        font-size: 0.95rem;
    }
    .insight-detail {
        color: #4B5563;
        font-size: 0.85rem;
        margin-top: 3px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #10243E;
    }
    section[data-testid="stSidebar"] * {
        color: #E5E7EB !important;
    }
    section[data-testid="stSidebar"] .stButton button {
        background-color: #1F4E78;
        color: white !important;
        border-radius: 8px;
        border: none;
    }

    /* Headings */
    h1, h2, h3 {
        color: #10243E;
    }

    /* Dataframe container */
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }

    .app-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #10243E;
    }
    .app-subtitle {
        color: #6B7280;
        font-size: 0.95rem;
        margin-bottom: 14px;
    }
</style>
"""


def inject_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def kpi_card(col, label, value, sub=None):
    with col:
        sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                {sub_html}
            </div>
            """,
            unsafe_allow_html=True,
        )
