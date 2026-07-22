# 🚚 Logistics Cost Analyzer

A end-to-end **logistics cost & profitability analytics dashboard** built with
Streamlit, Pandas, NumPy, Plotly, SQLite, OpenPyXL, and ReportLab.

All data is **100% fictional and synthetically generated**  no external datasets or APIs required.

## 🌐 Live Demo

🔗 **Streamlit App:** : https://logistics-cost-analyzer-by-mridul.streamlit.app/


## ✨ Features

- **Dashboard** — KPI cards (shipments, cost, revenue, profit, margin, cost/km, distance, delivery time)
  plus 9+ interactive Plotly charts (monthly cost/profit, cost breakdown, fuel trend, top routes,
  vehicle utilization, supplier/warehouse comparison, delivery status).
- **Cost Analysis** — cost component breakdown, monthly composition, cost by supplier/warehouse, cost vs distance.
- **Route Analysis** — top expensive/profitable routes, efficiency scatter plots, destination volume treemap.
- **Vehicle Analysis** — utilization, maintenance costs, cost-per-km distribution, driver performance.
- **Profitability Analysis** — revenue vs cost vs profit trends, margin trend, profit drivers by supplier/warehouse/vehicle.
- **Business Insights** — auto-generated findings (most expensive supplier, most profitable route,
  highest maintenance cost, best warehouse, cost-saving recommendations).
- **Reports** — export filtered data as **CSV**, **Excel** (with KPI summary + chart), and **PDF** (executive report).
- **Data Explorer** — full-text search, sortable table, CSV download.
- **Filtering** — date range, supplier, warehouse, route, vehicle type, driver, delivery status — available on every page.
- **SQLite persistence** — data is generated once and stored in `data/logistics.db`; use the
  "Regenerate Data" button on the Dashboard to create a fresh synthetic dataset.





## 🛠️ Tech Stack

- **Streamlit** — multipage web app framework
- **Pandas / NumPy** — data generation & analysis
- **Plotly** — interactive charts
- **SQLite** — lightweight embedded database
- **OpenPyXL** — Excel report generation
- **ReportLab** — PDF report generation

## 📌 Notes

- All company names, suppliers, routes, and figures are entirely fictional and for demonstration purposes only.
- The dashboard is fully responsive and designed for both desktop and wide-screen use.
