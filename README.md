# 🚚 Logistics Cost Analyzer

A portfolio-quality, end-to-end **logistics cost & profitability analytics dashboard** built with
Streamlit, Pandas, NumPy, Plotly, SQLite, OpenPyXL, and ReportLab.

All data is **100% fictional and synthetically generated** — no external datasets or APIs required.

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

## 📁 Project Structure

```
logistics_cost_analyzer/
├── app.py                     # Main entry point / Dashboard page
├── data_generator.py          # Synthetic data generation (1,500+ shipments)
├── database.py                # SQLite persistence layer
├── filters.py                 # Shared sidebar filter widgets
├── insights.py                # Automatic business insight generation
├── reports.py                 # CSV / Excel / PDF export helpers
├── utils.py                   # KPI calculations + shared CSS/styling
├── requirements.txt
├── README.md
├── data/
│   └── logistics.db           # SQLite database (created on first run)
└── pages/
    ├── 1_💰_Cost_Analysis.py
    ├── 2_🛣️_Route_Analysis.py
    ├── 3_🚛_Vehicle_Analysis.py
    ├── 4_📈_Profitability_Analysis.py
    ├── 5_💡_Business_Insights.py
    ├── 6_🧾_Reports.py
    └── 7_🔎_Data_Explorer.py
```

## 🚀 Getting Started

1. **Install dependencies** (Python 3.9+ recommended):

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app**:

   ```bash
   streamlit run app.py
   ```

3. On first launch, the app automatically generates **1,500 fictional shipment records** and stores
   them in a local SQLite database at `data/logistics.db`. Subsequent runs reuse the same data unless
   you click **🔄 Regenerate Data** on the Dashboard.

## 🧮 Data Model

Each shipment record includes:

| Field | Description |
|---|---|
| `shipment_id` | Unique identifier (e.g. `SHP-000123`) |
| `date` | Shipment date |
| `supplier` | Logistics supplier/carrier |
| `warehouse` | Origin warehouse |
| `destination` | Delivery destination |
| `route` | Warehouse → destination |
| `vehicle_type` | Light Van, Medium Truck, Heavy Truck, Refrigerated Truck, Trailer |
| `driver` | Assigned driver |
| `distance_km` | Distance traveled |
| `fuel_cost`, `labor_cost`, `maintenance_cost`, `toll_cost`, `other_charges` | Cost components |
| `total_cost` | Sum of all cost components |
| `revenue` | Revenue billed to customer |
| `profit` | Revenue − Total Cost |
| `delivery_time_hours` | Total delivery duration |
| `delivery_status` | On Time / Delayed / Early / Cancelled |

Derived fields: `month`, `cost_per_km`, `profit_margin_pct`.

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
