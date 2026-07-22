"""Reports page — export filtered data as Excel, PDF, or CSV."""

import streamlit as st
from datetime import datetime

import database as db
from filters import apply_sidebar_filters
from utils import compute_kpis, inject_css, kpi_card, fmt_currency
from insights import generate_insights
from reports import to_csv_bytes, to_excel_bytes, to_pdf_bytes

st.set_page_config(page_title="Reports | Logistics Cost Analyzer", page_icon="🧾", layout="wide")
inject_css()

st.markdown('<div class="app-title">🧾 Reports & Export</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Export filtered shipment data and KPI summaries</div>',
            unsafe_allow_html=True)

full_df = db.load_data()
if full_df.empty:
    st.error("No data found. Please visit the main Dashboard page first to generate data.")
    st.stop()

df = apply_sidebar_filters(full_df, key_prefix="report")
if df.empty:
    st.warning("No shipments match the selected filters.")
    st.stop()

kpis = compute_kpis(df)

cols = st.columns(4)
kpi_card(cols[0], "Records to Export", f"{len(df):,}")
kpi_card(cols[1], "Total Cost", fmt_currency(kpis["Total Logistics Cost"]))
kpi_card(cols[2], "Total Revenue", fmt_currency(kpis["Total Revenue"]))
kpi_card(cols[3], "Total Profit", fmt_currency(kpis["Total Profit"]))

st.markdown('<div class="section-header">📥 Download Options</div>', unsafe_allow_html=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M")

readable_kpis = {
    "Total Shipments": f"{kpis['Total Shipments']:,}",
    "Total Logistics Cost": fmt_currency(kpis["Total Logistics Cost"]),
    "Total Revenue": fmt_currency(kpis["Total Revenue"]),
    "Total Profit": fmt_currency(kpis["Total Profit"]),
    "Profit Margin (%)": f"{kpis['Profit Margin (%)']:.2f}%",
    "Avg Cost per Shipment": fmt_currency(kpis["Avg Cost per Shipment"]),
    "Avg Cost per Km": fmt_currency(kpis["Avg Cost per Km"]),
    "Total Distance (km)": f"{kpis['Total Distance (km)']:,.1f}",
    "Avg Delivery Time (hrs)": f"{kpis['Avg Delivery Time (hrs)']:.2f}",
}

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("#### 📄 CSV Export")
    st.write("Raw filtered shipment data in CSV format — ideal for further analysis in other tools.")
    csv_bytes = to_csv_bytes(df)
    st.download_button(
        "⬇️ Download CSV", data=csv_bytes, file_name=f"logistics_shipments_{timestamp}.csv",
        mime="text/csv", use_container_width=True,
    )

with c2:
    st.markdown("#### 📊 Excel Export")
    st.write("Formatted workbook with a KPI summary sheet, full data sheet, and a monthly profit chart.")
    with st.spinner("Building Excel workbook..."):
        excel_bytes = to_excel_bytes(df, readable_kpis)
    st.download_button(
        "⬇️ Download Excel", data=excel_bytes, file_name=f"logistics_report_{timestamp}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True,
    )

with c3:
    st.markdown("#### 🧾 PDF Report")
    st.write("Executive-style PDF with KPIs, business insights, and a sample of the shipment data.")
    with st.spinner("Building PDF report..."):
        insights = generate_insights(df)
        pdf_bytes = to_pdf_bytes(df, readable_kpis, insights)
    st.download_button(
        "⬇️ Download PDF", data=pdf_bytes, file_name=f"logistics_report_{timestamp}.pdf",
        mime="application/pdf", use_container_width=True,
    )

st.markdown('<div class="section-header">👀 Preview: Filtered Data</div>', unsafe_allow_html=True)
st.dataframe(df, use_container_width=True, height=420)
