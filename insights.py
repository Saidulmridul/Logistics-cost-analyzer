"""
insights.py
------------
Generates automatic business insights and cost-saving recommendations
from the shipment DataFrame.
"""

import pandas as pd


def generate_insights(df: pd.DataFrame) -> list:
    """Return a list of dicts: {'icon', 'title', 'detail'} summarizing insights."""
    insights = []

    if df.empty:
        return [{
            "icon": "⚠️",
            "title": "No data available",
            "detail": "Adjust your filters to see insights.",
        }]

    active = df[df["delivery_status"] != "Cancelled"]

    # Most expensive supplier (by average total cost)
    if not active.empty:
        supplier_cost = active.groupby("supplier")["total_cost"].mean().sort_values(ascending=False)
        top_supplier = supplier_cost.index[0]
        insights.append({
            "icon": "💰",
            "title": f"Most Expensive Supplier: {top_supplier}",
            "detail": f"Averages ${supplier_cost.iloc[0]:,.2f} per shipment, "
                      f"{(supplier_cost.iloc[0] / supplier_cost.mean() - 1) * 100:.1f}% above the supplier average.",
        })

    # Most profitable route
    route_profit = active.groupby("route")["profit"].sum().sort_values(ascending=False)
    if not route_profit.empty:
        top_route = route_profit.index[0]
        insights.append({
            "icon": "🏆",
            "title": f"Most Profitable Route: {top_route}",
            "detail": f"Generated ${route_profit.iloc[0]:,.2f} in total profit across all shipments.",
        })

    # Highest maintenance cost (supplier or vehicle)
    maint_vehicle = active.groupby("vehicle_type")["maintenance_cost"].mean().sort_values(ascending=False)
    if not maint_vehicle.empty:
        top_vehicle = maint_vehicle.index[0]
        insights.append({
            "icon": "🔧",
            "title": f"Highest Maintenance Cost: {top_vehicle}",
            "detail": f"Averages ${maint_vehicle.iloc[0]:,.2f} in maintenance cost per shipment. "
                      f"Consider a preventive maintenance schedule for this vehicle class.",
        })

    # Best warehouse (by profit margin)
    wh_perf = active.groupby("warehouse").agg(
        total_profit=("profit", "sum"),
        avg_margin=("profit_margin_pct", "mean"),
    ).sort_values("avg_margin", ascending=False)
    if not wh_perf.empty:
        best_wh = wh_perf.index[0]
        insights.append({
            "icon": "🏭",
            "title": f"Best Performing Warehouse: {best_wh}",
            "detail": f"Achieves the highest average profit margin at {wh_perf.iloc[0]['avg_margin']:.1f}%, "
                      f"contributing ${wh_perf.iloc[0]['total_profit']:,.2f} in total profit.",
        })

    # Delayed shipment rate
    delay_rate = (df["delivery_status"] == "Delayed").mean() * 100
    insights.append({
        "icon": "⏱️",
        "title": f"Delivery Delay Rate: {delay_rate:.1f}%",
        "detail": "Consider reviewing routes and vehicle scheduling if this exceeds 15-20%."
                  if delay_rate > 15 else "Delivery performance is within a healthy range.",
    })

    # Cost-saving recommendation: highest cost-per-km routes
    route_cpk = active.groupby("route")["cost_per_km"].mean().sort_values(ascending=False)
    if not route_cpk.empty:
        worst_route = route_cpk.index[0]
        insights.append({
            "icon": "📉",
            "title": "Cost-Saving Opportunity",
            "detail": f"Route '{worst_route}' has the highest cost per km "
                      f"(${route_cpk.iloc[0]:.2f}/km). Renegotiating carrier rates or "
                      f"consolidating shipments here could reduce overall logistics spend.",
        })

    # Fuel cost share of total cost
    fuel_share = active["fuel_cost"].sum() / active["total_cost"].sum() * 100 if active["total_cost"].sum() else 0
    insights.append({
        "icon": "⛽",
        "title": f"Fuel Represents {fuel_share:.1f}% of Total Cost",
        "detail": "Fuel is the dominant cost driver. Route optimization and fuel-efficient "
                  "vehicle allocation could yield meaningful savings."
                  if fuel_share > 35 else "Fuel costs are reasonably balanced against other cost centers.",
    })

    return insights
